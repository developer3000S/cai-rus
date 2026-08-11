"""Утилиты выполнения Docker-контейнеров и управления путями рабочих пространств.

Вынесены из tools/common.py (3 343 строки) в рамках рефакторинга движка.
Содержат вспомогательные функции разрешения рабочих пространств и асинхронный
механизм выполнения Docker-команд.
"""

import os

_CAI_DEBUG_DIR = os.path.join(os.path.expanduser("~"), ".cai", "debug")
import subprocess  # nosec B404
import time
import uuid

from wasabi import color  # pylint: disable=import-error

from cai.util import (
    start_active_timer,
    stop_active_timer,
    start_idle_timer,
    stop_idle_timer,
)
from cai.tools.streaming import (
    _get_idle_timeout,
    is_tool_streaming_enabled,
    _get_agent_token_info,
)


# ---------------------------------------------------------------------------
# Вспомогательные функции путей рабочих пространств (используются модулями container и executor)
# ---------------------------------------------------------------------------

def _default_workspace_base() -> str:
    """Возвращает базовый путь рабочего пространства по умолчанию: ~/.cai/workspace"""
    return os.path.join(os.path.expanduser("~"), ".cai", "workspace")


def _get_workspace_dir() -> str:
    """Определяет целевую директорию рабочего пространства на основе переменных окружения хоста.

    Порядок разрешения:
      1. Переменная окружения CAI_WORKSPACE_DIR   (явное переопределение)
      2. ~/.cai/workspace/{CAI_WORKSPACE}          (именованное рабочее пространство)
      3. ~/.cai/workspace/                         (по умолчанию)
    """
    base_dir_env = os.getenv("CAI_WORKSPACE_DIR")
    workspace_name = os.getenv("CAI_WORKSPACE")

    if base_dir_env:
        base_dir = os.path.abspath(base_dir_env)
    else:
        base_dir = _default_workspace_base()

    if workspace_name:
        if not all(c.isalnum() or c in ["_", "-"] for c in workspace_name):
            print(color(
                f"Недопустимое имя CAI_WORKSPACE '{workspace_name}'. "
                f"Используется директория '{base_dir}'.", fg="yellow",
            ))
            target_dir = base_dir
        else:
            target_dir = os.path.join(base_dir, workspace_name)
    else:
        target_dir = base_dir

    try:
        abs_target_dir = os.path.abspath(target_dir)
        os.makedirs(abs_target_dir, exist_ok=True)
        return abs_target_dir
    except OSError as e:
        print(color(
            f"Ошибка создания/доступа к директории рабочего пространства на хосте '{abs_target_dir}': {e}",
            fg="red",
        ))
        fallback = _default_workspace_base()
        os.makedirs(fallback, exist_ok=True)
        print(color(f"Используется резервный вариант: {fallback}", fg="yellow"))
        return fallback


def _get_container_workspace_path() -> str:
    """Определяет целевой путь рабочего пространства внутри контейнера."""
    workspace_name = os.getenv("CAI_WORKSPACE")
    if workspace_name:
        if not all(c.isalnum() or c in ["_", "-"] for c in workspace_name):
            print(color(
                f"Недопустимое имя CAI_WORKSPACE '{workspace_name}' для контейнера. "
                f"Используется '/workspace'.", fg="yellow",
            ))
            return "/workspace"
        return f"/workspace/workspaces/{workspace_name}"
    else:
        return "/workspace"



async def _run_docker_async(
    command,
    container_id,
    stdout=False,
    timeout=100,
    stream=False,
    call_id=None,
    tool_name=None,
    args=None,
):
    """Асинхронная версия выполнения Docker-команд через asyncio subprocess."""
    import asyncio

    # Убедиться, что мы в режиме активного времени для выполнения инструмента
    stop_idle_timer()
    start_active_timer()

    try:
        container_workspace = _get_container_workspace_path()

        # Разбор команды для отображения
        parts = command.strip().split(" ", 1)
        cmd_name = parts[0] if parts else ""
        cmd_args = parts[1] if len(parts) > 1 else ""

        if not tool_name:
            tool_name = f"{cmd_name}_command" if cmd_name else "command"

        # Формирование команды docker exec
        docker_cmd_list = [
            "docker",
            "exec",
            "-w",
            container_workspace,
            container_id,
            "sh",
            "-c",
            command,
        ]

        if stream:
            from cai.util import start_tool_streaming, update_tool_streaming, finish_tool_streaming

            # Если были предоставлены аргументы (например, из execute_code), использовать их как основу
            # В противном случае создать аргументы инструмента для отображения
            if args and isinstance(args, dict):
                tool_args = args.copy()
                # Добавление информации о контейнере
                tool_args["container"] = container_id[:12]
                tool_args["environment"] = "Container"
                tool_args["workspace"] = container_workspace
                tool_args["full_command"] = command
            else:
                tool_args = {
                    "command": cmd_name,
                    "args": cmd_args if cmd_args.strip() else "",
                    "full_command": command,
                    "container": container_id[:12],
                    "environment": "Container",
                    "workspace": container_workspace,
                }

            if not call_id:
                call_id = f"cmd_{cmd_name}_{str(uuid.uuid4())[:8]}"

            token_info = _get_agent_token_info()
            call_id = start_tool_streaming(tool_name, tool_args, call_id, token_info)

            process = None
            try:
                # Создание асинхронного подпроцесса
                process = await asyncio.create_subprocess_exec(
                    *docker_cmd_list, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )

                # Потоковая передача вывода
                output_buffer = []
                start_time = time.time()

                # Помощник для форматирования времени для отображения
                def _format_countdown(elapsed, total_timeout):
                    remaining = max(0, total_timeout - elapsed)
                    return f"{total_timeout}s|{remaining:.1f}s"

                try:
                    # Применить таймаут ко всему процессу потоковой передачи и выполнения
                    async def read_and_stream():
                        nonlocal output_buffer
                        buffer_size = 0
                        # Lower-latency streaming for docker
                        update_interval = 1 if tool_name == "generic_linux_command" else 1

                        # Чтение stdout с определением простоя
                        last_output = time.time()
                        while True:
                            if process.returncode is not None:
                                break
                            try:
                                line = await asyncio.wait_for(process.stdout.readline(), timeout=0.5)
                                if line:
                                    output_buffer.append(line.decode('utf-8', errors='replace'))
                                    buffer_size += 1
                                    last_output = time.time()
                                    if buffer_size >= update_interval:
                                        elapsed = time.time() - start_time
                                        streaming_args = dict(tool_args)
                                        streaming_args["timeout_countdown"] = _format_countdown(elapsed, timeout)
                                        update_tool_streaming(tool_name, streaming_args, ''.join(output_buffer), call_id, token_info)
                                        buffer_size = 0
                                else:
                                    break
                            except asyncio.TimeoutError:
                                idle_timeout = _get_idle_timeout()
                                if time.time() - last_output > idle_timeout:
                                    process.terminate()
                                    try:
                                        await asyncio.wait_for(process.wait(), timeout=1.0)
                                    except asyncio.TimeoutError:
                                        process.kill()
                                        await process.wait()
                                    output_buffer.append(f"\n[Остановлено: простоя {idle_timeout}с]")
                                    break

                        # Ожидание завершения процесса
                        if process.returncode is None:
                            return_code = await process.wait()
                        else:
                            return_code = process.returncode
                        return return_code

                    return_code = await asyncio.wait_for(read_and_stream(), timeout=timeout)

                except asyncio.TimeoutError:
                    if os.getenv("CAI_TUI_MODE") == "true":
                        with open(f"{_CAI_DEBUG_DIR}/cai_timeout_debug.log", "a") as f:
                            f.write(f"  DOCKER TIMEOUT TRIGGERED after {timeout}s! Killing process...\n")

                    process.kill()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        process.terminate()

                    partial_output = "".join(output_buffer) if 'output_buffer' in locals() else ""
                    timeout_msg = f"\n[Команда превысила время выполнения в контейнере ({timeout} сек)]"

                    execution_info = {
                        "status": "timeout",
                        "environment": "Container",
                        "host": container_id[:12],
                        "tool_time": timeout,
                    }

                    finish_tool_streaming(
                        tool_name, tool_args, partial_output + timeout_msg, call_id, execution_info, token_info
                    )
                    return partial_output + timeout_msg

                execution_time = time.time() - start_time

                # Получение stderr, если есть
                stderr_data = await process.stderr.read()
                if stderr_data:
                    stderr_str = stderr_data.decode("utf-8", errors="replace")
                    output_buffer.append("\nВЫВОД ОШИБКИ:\n" + stderr_str)

                final_output = "".join(output_buffer)
                if return_code != 0:
                    final_output += f"\nКоманда завершилась с кодом {return_code}"

                execution_info = {
                    "status": "completed" if return_code == 0 else "error",
                    "return_code": return_code,
                    "environment": "Container",
                    "host": container_id[:12],
                    "tool_time": execution_time,
                }

                tool_args["elapsed"] = f"{execution_time:.1f}s"

                finish_tool_streaming(
                    tool_name, tool_args, final_output, call_id, execution_info, token_info
                )
                return final_output

            except asyncio.CancelledError:
                if process and process.returncode is None:
                    process.kill()
                    try:
                        await process.wait()
                    except Exception:
                        pass

                execution_info = {
                    "status": "cancelled",
                    "environment": "Container",
                    "host": container_id[:12],
                    "tool_time": time.time() - start_time if 'start_time' in locals() else 0,
                }

                cancelled_output = "".join(output_buffer) if 'output_buffer' in locals() else ""
                cancelled_output += "\n[Выполнение отменено]"

                finish_tool_streaming(
                    tool_name, tool_args, cancelled_output, call_id, execution_info, token_info
                )
                raise

        else:
            # Асинхронное выполнение без потоковой передачи
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                *docker_cmd_list, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise subprocess.TimeoutExpired(command, timeout)
            except asyncio.CancelledError:
                process.kill()
                try:
                    await process.wait()
                except Exception:
                    pass
                raise

            output = stdout_data.decode("utf-8", errors="replace") if stdout_data else ""
            if not output and stderr_data:
                output = stderr_data.decode("utf-8", errors="replace")

            if stdout:
                context_msg = f"(docker:{container_id[:12]}:{container_workspace})"
                print(f"\033[32m{context_msg} $ {command}\n{output}\033[0m")

            token_info = _get_agent_token_info()

            from cai.util.session import is_parallel_session

            is_parallel = False
            if token_info and token_info.get("agent_id"):
                agent_id = token_info.get("agent_id")
                if agent_id and agent_id.startswith("P") and agent_id[1:].isdigit():
                    if is_parallel_session():
                        is_parallel = True

            in_tui_mode = os.getenv("CAI_TUI_MODE") == "true"
            streaming_enabled = is_tool_streaming_enabled()

            if in_tui_mode or (streaming_enabled and is_parallel):
                from cai.util import cli_print_tool_output

                execution_time = time.time() - start_time
                parts = command.strip().split(" ", 1)

                if not call_id:
                    cmd_name = parts[0] if parts else "cmd"
                    call_id = f"container_{cmd_name}_{str(uuid.uuid4())[:8]}"

                execution_info = {
                    "status": "completed" if process.returncode == 0 else "error",
                    "return_code": process.returncode,
                    "environment": "Container",
                    "host": container_id[:12],
                    "tool_time": execution_time,
                }

                display_args = (
                    args
                    if args is not None
                    else {
                        "command": parts[0] if parts else command,
                        "args": parts[1] if len(parts) > 1 else "",
                        "full_command": command,
                        "container": container_id[:12],
                        "workspace": container_workspace,
                    }
                )

                cli_print_tool_output(
                    tool_name=tool_name or "generic_linux_command",
                    args=display_args,
                    output=output.strip(),
                    call_id=call_id,
                    execution_info=execution_info,
                    token_info=token_info,
                    streaming=False,
                )

            return output.strip()

    except Exception as e:
        error_msg = f"Ошибка выполнения команды в контейнере: {str(e)}"
        print(color(error_msg, fg="red"))
        return error_msg
    finally:
        stop_active_timer()
        start_idle_timer()
