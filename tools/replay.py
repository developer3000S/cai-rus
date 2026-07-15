#!/usr/bin/env python3
"""
Инструмент для преобразования JSONL файлов в формат воспроизведения, имитирующий вывод CLI.
Это позволяет просматривать разговоры в более читаемом формате.

Использование:
    JSONL_FILE_PATH="path/to/file.jsonl" REPLAY_DELAY="0.5" python3 tools/replay.py

    # Или с использованием позиционных аргументов:
    python3 tools/replay.py path/to/file.jsonl 0.5
    cai-replay path/to/file.jsonl 0.5

    # Или с использованием аргументов командной строки:
    python3 tools/replay.py --jsonl-file-path path/to/file.jsonl --replay-delay 0.5

Использование с asciinema rec, генерация .cast файла и его преобразование в gif:
    asciinema rec --command="python3 tools/replay.py path/to/file.jsonl 0.5" --overwrite

Или альтернативно:
    asciinema rec --command="JSONL_FILE_PATH='caiextensions-memory/caiextensions/memory/it/pentestperf/hackableii/hackableII_autonomo.jsonl' REPLAY_DELAY='0.05' cai-replay"

Затем преобразуйте .cast файл в gif:
    agg /tmp/tmp6c4dxoac-ascii.cast demo.gif

Переменные окружения:
    JSONL_FILE_PATH: Путь к JSONL файлу, содержащему историю разговоров (обязательно)
    REPLAY_DELAY: Время в секундах ожидания между действиями (по умолчанию: 0.5)
"""

import re
import json
import os
import sys
import time
import argparse
from typing import Dict, List, Tuple

# Отключение записи сессии для инструмента воспроизведения
os.environ["CAI_DISABLE_SESSION_RECORDING"] = "true"

# Добавляем родительскую директорию в путь для импорта модулей cai
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.text import Text
from rich.console import Group
from rich.columns import Columns
from rich.rule import Rule

from cai.util import cli_print_agent_messages, cli_print_tool_output, color, COST_TRACKER
from cai.sdk.agents.run_to_jsonl import get_token_stats, load_history_from_jsonl
from cai.repl.ui.banner import display_banner
from collections import defaultdict

# Инициализация объекта консоли для вывода rich
console = Console()


# Создаем собственную функцию display_execution_time, использующую нашу локальную консоль
def display_execution_time(metrics=None):
    """Отображение общего времени выполнения с нашей локальной консолью."""
    if metrics is None:
        return

    # Создаем панель для времени выполнения
    content = []
    content.append(f"Время сессии: {metrics['session_time']}")
    content.append(f"Активное время: {metrics['active_time']}")
    content.append(f"Время простоя: {metrics['idle_time']}")

    if metrics.get("llm_time") and metrics["llm_time"] != "0.0s":
        content.append(
            f"Время обработки LLM: [bold yellow]{metrics['llm_time']}[/bold yellow] "
            f"[dim]({metrics['llm_percentage']:.1f}% от сессии)[/dim]"
        )

    time_panel = Panel(
        Group(*[Text(line) for line in content]),
        border_style="blue",
        box=ROUNDED,
        padding=(0, 1),
        title="[bold]Статистика сессии[/bold]",
        title_align="left",
    )
    console.print(time_panel)


def load_jsonl(file_path: str) -> List[Dict]:
    """Загрузка JSONL файла и возврат его содержимого в виде списка словарей."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Предупреждение: Пропуск недопустимой строки JSON: {line[:50]}...")
    return data


def normalize_content(content) -> str:
    """
    Нормализация содержимого сообщения из различных форматов в простую строку.

    Обрабатывает:
    - Простые строки: возврат как есть
    - Список блоков содержимого: извлечение текста из каждого блока
    - None: возврат пустой строки
    """
    if content is None:
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                # Обработка различных типов блоков содержимого
                if "text" in item:
                    text_parts.append(item["text"])
                elif "content" in item:
                    text_parts.append(str(item["content"]))
        return "\n".join(text_parts).strip() if text_parts else str(content)

    return str(content).strip()


def detect_parallel_agents(messages: List[Dict]) -> Dict[str, str]:
    """
    Обнаружение параллельных агентов из сообщений путем анализа паттернов поля отправителя.
    Возвращает отображение agent_id на agent_name.
    """
    agents = {}

    # Ищем сообщения с полем отправителя, следующим параллельному паттерну
    for msg in messages:
        sender = msg.get("sender", "")
        # Совпадение паттернов типа "Bug Bounter [P1]", "Red Team Agent [P2]" и т.д.
        match = re.match(r"(.+?)\s*\[(P\d+)\]$", sender)
        if match:
            agent_name = match.group(1).strip()
            agent_id = match.group(2)
            agents[agent_id] = agent_name

    return agents


def replay_conversation(
    messages: List[Dict],
    replay_delay: float = 0.5,
    usage: Tuple = None,
    jsonl_file_path: str = None,
    full_data: List[Dict] = None,
) -> None:
    """
    Воспроизведение разговора из списка сообщений с выводом в реальном времени.

    Аргументы:
        messages: Список словарей сообщений
        replay_delay: Время в секундах ожидания между действиями
        usage: Кортеж, содержащий (model_name, total_input_tokens, total_output_tokens,
               total_cost, active_time, idle_time)
        jsonl_file_path: Путь к исходному JSONL файлу для отображения графа
        full_data: Полные данные JSONL для дополнительного поиска метаданных
    """
    turn_counter = 0
    interaction_counter = 0
    debug = 0  # Always set debug to 2

    # Обнаружение параллельных агентов
    parallel_agents = detect_parallel_agents(messages)
    is_parallel = len(parallel_agents) > 0

    # Сохранение сообщений для отображения графа
    agent_messages = defaultdict(list)

    # Создание отображения временных меток на имена агентов из full_data
    timestamp_to_agent = {}
    if full_data:
        for entry in full_data:
            if entry.get("agent_name") and entry.get("timestamp_iso"):
                timestamp_to_agent[entry["timestamp_iso"]] = entry["agent_name"]

    if not messages:
        print(color("Не найдено допустимых сообщений в JSONL файле", fg="yellow"))
        return

    print(color(f"Воспроизведение разговора с {len(messages)} сообщениями...", fg="green"))

    if is_parallel:
        print(color(f"Обнаружено {len(parallel_agents)} параллельных агентов:", fg="cyan"))
        for agent_id, agent_name in sorted(parallel_agents.items()):
            print(color(f"  • {agent_name} [{agent_id}]", fg="cyan"))

    # Извлечение статистики использования из кортежа usage
    # Обработка как старого формата (4 элемента), так и нового (6 элементов с временем)
    file_model = usage[0]
    total_input_tokens = usage[1]
    total_output_tokens = usage[2]
    total_cost = usage[3]

    # Проверка наличия информации о времени
    active_time = usage[4] if len(usage) > 4 else 0
    idle_time = usage[5] if len(usage) > 5 else 0

    # Отображение информации о времени при наличии
    if active_time > 0 or idle_time > 0:
        print(color(f"Активное время: {active_time:.2f}s", fg="cyan"))
        print(color(f"Время простоя: {idle_time:.2f}s", fg="cyan"))

    print(color(f"Общая стоимость: ${total_cost:.6f}", fg="cyan"))

    # Инициализация COST_TRACKER общей стоимостью из JSONL файла
    COST_TRACKER.session_total_cost = total_cost

    # Первый проход: Обработка всех выводов инструментов
    tool_outputs = {}
    for idx, message in enumerate(messages):
        if message.get("role") == "tool" and message.get("tool_call_id"):
            tool_id = message.get("tool_call_id")
            content = message.get("content", "")
            tool_outputs[tool_id] = content

    # Обработка сообщений ассистента для сопоставления вызовов инструментов с выводами
    for message in messages:
        if message.get("role") == "assistant" and message.get("tool_calls"):
            for tool_call in message.get("tool_calls", []):
                call_id = tool_call.get("id", "")
                if call_id in tool_outputs:
                    # Добавляем этот вывод к tool_outputs сообщения ассистента
                    if "tool_outputs" not in message:
                        message["tool_outputs"] = {}
                    message["tool_outputs"][call_id] = tool_outputs[call_id]

    # Обработка всех сообщений, включая последнее
    total_messages = len(messages)
    cumulative_cost = 0.0  # Отслеживание кумулятивной стоимости для прогрессивных обновлений

    for i, message in enumerate(messages):
        try:
            # Добавление задержки между действиями
            if i > 0:
                time.sleep(replay_delay)

            role = message.get("role", "")
            content = normalize_content(message.get("content"))
            sender = message.get("sender", role)
            model = message.get("model", file_model)

            # Обновление COST_TRACKER кумулятивной стоимостью до этого сообщения
            # Вычисление стоимости из токенов, если interaction_cost недоступен
            message_cost = message.get("interaction_cost", 0.0)
            if message_cost == 0 and role == "assistant":
                # Оценка стоимости из токенов (грубая оценка: $5/M входные, $15/M выходные)
                input_tokens = message.get("input_tokens", 0)
                output_tokens = message.get("output_tokens", 0)
                if input_tokens > 0 or output_tokens > 0:
                    message_cost = (input_tokens * 0.000005) + (output_tokens * 0.000015)
            if message_cost > 0:
                cumulative_cost += message_cost
                COST_TRACKER.current_agent_total_cost = cumulative_cost
                COST_TRACKER.session_total_cost = cumulative_cost

            # Пропуск системных сообщений
            if role == "system":
                continue

            # Сохранение сообщения для графа при обнаружении параллельных агентов
            if is_parallel:
                # Определение агента для этого сообщения
                if role == "assistant":
                    # Извлечение ID агента из отправителя при наличии
                    agent_match = re.match(r"(.+?)\s*\[(P\d+)\]$", sender)
                    if agent_match:
                        agent_id = agent_match.group(2)
                        agent_messages[agent_id].append(message)
                elif role == "user":
                    # Сообщения пользователей отправляются всем агентам
                    for agent_id in parallel_agents:
                        agent_messages[agent_id].append(message)
                elif role == "tool":
                    # Сообщения инструментов отправляются агенту, который их вызвал
                    # Ищем предыдущее сообщение ассистента, которое выполнило этот вызов инструмента
                    tool_call_id = message.get("tool_call_id")
                    for j in range(i - 1, -1, -1):
                        prev_msg = messages[j]
                        if prev_msg.get("role") == "assistant":
                            prev_sender = prev_msg.get("sender", "")
                            agent_match = re.match(r"(.+?)\s*\[(P\d+)\]$", prev_sender)
                            if agent_match:
                                agent_id = agent_match.group(2)
                                agent_messages[agent_id].append(message)
                                break

            # Обработка сообщений пользователей
            if role == "user":
                print(color(f"CAI> ", fg="cyan") + f"{content}")
                turn_counter += 1
                # Не сбрасываем interaction_counter для сохранения нумерации между запросами пользователей

            # Обработка сообщений ассистента
            elif role == "assistant":
                # Проверка наличия вызовов инструментов
                tool_calls = message.get("tool_calls", [])
                tool_outputs = message.get("tool_outputs", {})

                # Извлечение фактического имени агента
                display_sender = sender

                # Сначала проверяем наличие agent_name в метаданных сообщения
                agent_name = message.get("agent_name")
                if agent_name:
                    display_sender = agent_name
                else:
                    # Если все еще не найдено, пытаемся извлечь из паттернов содержимого
                    if display_sender in ["assistant", role] and content:
                        # Ищем паттерны типа "Agent: Bug Bounter >>" или "[0] Agent: Bug Bounter"
                        agent_match = re.search(
                            r"(?:\[\d+\]\s*)?Agent:\s*([^>]+?)(?:\s*>>|\s*\[|$)", content
                        )
                        if agent_match:
                            display_sender = agent_match.group(1).strip()

                    # Если все еще "assistant", используем имя по умолчанию
                    if display_sender == "assistant" or display_sender == role:
                        display_sender = "Assistant"

                if tool_calls:
                    # Only print the assistant message if there's actual content
                    # Skip empty panels when only tool_calls are present
                    if content and content.strip():
                        cli_print_agent_messages(
                            display_sender,
                            content,
                            interaction_counter,
                            model,
                            debug,
                            interaction_input_tokens=message.get("input_tokens", 0),
                            interaction_output_tokens=message.get("output_tokens", 0),
                            interaction_reasoning_tokens=message.get("reasoning_tokens", 0),
                            total_input_tokens=total_input_tokens,
                            total_output_tokens=total_output_tokens,
                            total_reasoning_tokens=message.get("total_reasoning_tokens", 0),
                            interaction_cost=message.get("interaction_cost", 0.0),
                            total_cost=total_cost,
                            cache_read_tokens=message.get("cache_read_tokens", 0),
                            cache_creation_tokens=message.get("cache_creation_tokens", 0),
                        )

                    # Печатаем каждый вызов инструмента с его выводом
                    for tool_call in tool_calls:
                        function = tool_call.get("function", {})
                        name = function.get("name", "")
                        arguments = function.get("arguments", "{}")
                        call_id = tool_call.get("id", "")

                        # Получаем вывод инструмента при наличии
                        tool_output = ""
                        if call_id and call_id in tool_outputs:
                            tool_output = tool_outputs[call_id]
                            # Обнаружение заглушек для пустых выводов
                            if tool_output.startswith("Tool response for call_"):
                                tool_output = "(Инструмент не вернул вывод)"

                        # Пропуск пустых вызовов инструментов
                        if not name:
                            continue

                        try:
                            # Пытаемся разобрать аргументы как JSON
                            if (
                                arguments
                                and isinstance(arguments, str)
                                and arguments.strip().startswith("{")
                            ):
                                args_obj = json.loads(arguments)
                            else:
                                args_obj = arguments

                            # Специальная обработка для execute_code для отображения полного кода
                            # Не изменяем args_obj для execute_code, мы обработаем отображение отдельно
                        except json.JSONDecodeError:
                            args_obj = arguments

                        # Специальная обработка для execute_code для отображения кода
                        if (
                            name == "execute_code"
                            and isinstance(args_obj, dict)
                            and args_obj.get("code")
                        ):
                            # Показываем execute_code с полным содержимым кода
                            from rich.panel import Panel
                            from rich.syntax import Syntax

                            code = args_obj.get("code", "")
                            language = args_obj.get("language", "python")
                            filename = args_obj.get("filename", "exploit")

                            # Создаем подсвеченный код
                            syntax = Syntax(code, language, theme="monokai", line_numbers=True)

                            # Создаем панель с кодом
                            code_panel = Panel(
                                syntax,
                                title=f"[bold yellow]execute_code({filename}.{language})[/bold yellow]",
                                border_style="yellow",
                                padding=(0, 1),
                            )
                            console.print(code_panel)

                            # Если есть вывод, показываем его тоже
                            if tool_output:
                                output_panel = Panel(
                                    tool_output,
                                    title="[bold green]Output[/bold green]",
                                    border_style="green",
                                    padding=(0, 1),
                                )
                                console.print(output_panel)

                            console.print()  # Добавляем отступ
                        else:
                            # Печатаем другие вызовы инструментов нормально
                            cli_print_tool_output(
                                tool_name=name,
                                args=args_obj,
                                output=tool_output,  # Use the matched tool output
                                call_id=call_id,
                                token_info={
                                    "interaction_input_tokens": message.get("input_tokens", 0),
                                    "interaction_output_tokens": message.get("output_tokens", 0),
                                    "interaction_reasoning_tokens": message.get(
                                        "reasoning_tokens", 0
                                    ),
                                    "total_input_tokens": total_input_tokens,
                                    "total_output_tokens": total_output_tokens,
                                    "total_reasoning_tokens": message.get(
                                        "total_reasoning_tokens", 0
                                    ),
                                    "model": model,
                                    "interaction_cost": message.get("interaction_cost", 0.0),
                                    "total_cost": total_cost,
                                    "agent_name": f"{display_sender} [P1]",
                                    "cache_read_tokens": message.get("cache_read_tokens", 0),
                                    "cache_creation_tokens": message.get("cache_creation_tokens", 0),
                                },
                            )
                else:
                    # Печатаем обычное сообщение ассистента
                    cli_print_agent_messages(
                        display_sender,
                        content or "",
                        interaction_counter,
                        model,
                        debug,
                        interaction_input_tokens=message.get("input_tokens", 0),
                        interaction_output_tokens=message.get("output_tokens", 0),
                        interaction_reasoning_tokens=message.get("reasoning_tokens", 0),
                        total_input_tokens=total_input_tokens,
                        total_output_tokens=total_output_tokens,
                        total_reasoning_tokens=message.get("total_reasoning_tokens", 0),
                        interaction_cost=message.get("interaction_cost", 0.0),
                        total_cost=total_cost,
                        cache_read_tokens=message.get("cache_read_tokens", 0),
                        cache_creation_tokens=message.get("cache_creation_tokens", 0),
                    )
                interaction_counter += 1  # инкремент счетчика взаимодействий

            # Обработка сообщений инструментов - только тех, которые не были уже отображены с сообщениями ассистента
            elif role == "tool":
                # Проверка, отображали ли мы уже этот вывод инструмента с сообщением ассистента
                tool_call_id = message.get("tool_call_id", "")

                # Пропуск сообщений инструментов, которые уже были отображены с сообщением ассистента
                is_already_displayed = False
                for prev_msg in messages[:i]:
                    if prev_msg.get("role") == "assistant" and tool_call_id in prev_msg.get(
                        "tool_outputs", {}
                    ):
                        is_already_displayed = True
                        break

                if not is_already_displayed and content:  # Показываем только если есть фактическое содержимое
                    tool_name = message.get("name", message.get("tool_call_id", "unknown"))
                    cli_print_tool_output(
                        tool_name=tool_name,
                        args="",
                        output=content,
                        token_info={
                            "interaction_input_tokens": message.get("input_tokens", 0),
                            "interaction_output_tokens": message.get("output_tokens", 0),
                            "interaction_reasoning_tokens": message.get("reasoning_tokens", 0),
                            "total_input_tokens": total_input_tokens,
                            "total_output_tokens": total_output_tokens,
                            "total_reasoning_tokens": message.get("total_reasoning_tokens", 0),
                            "model": model,
                            "interaction_cost": message.get("interaction_cost", 0.0),
                            "total_cost": total_cost,
                            "cache_read_tokens": message.get("cache_read_tokens", 0),
                            "cache_creation_tokens": message.get("cache_creation_tokens", 0),
                        },
                    )

            # Обработка любых других типов сообщений (включая финальные сообщения)
            else:
                # Всегда показываем последнее сообщение, даже если оно кажется пустым
                if content or (i == total_messages - 1 and role not in ["system", "tool"]):
                    cli_print_agent_messages(
                        sender or role,
                        content or "[Сессия завершена]",
                        interaction_counter,
                        model,
                        debug,
                        interaction_input_tokens=message.get("input_tokens", 0),
                        interaction_output_tokens=message.get("output_tokens", 0),
                        interaction_reasoning_tokens=message.get("reasoning_tokens", 0),
                        total_input_tokens=total_input_tokens,
                        total_output_tokens=total_output_tokens,
                        total_reasoning_tokens=message.get("total_reasoning_tokens", 0),
                        interaction_cost=message.get("interaction_cost", 0.0),
                        total_cost=total_cost,
                    )

            # Принудительный сброс stdout для немедленного вывода
            sys.stdout.flush()

        except Exception as e:
            # Обработка любых ошибок при обработке сообщений
            print(color(f"Предупреждение: Ошибка обработки сообщения {i+1}: {str(e)}", fg="yellow"))
            print(color("Продолжаем со следующим сообщением...", fg="yellow"))
            continue

    # Отображение графа в конце при обнаружении параллельных агентов
    if is_parallel and agent_messages:
        display_parallel_graph(agent_messages, parallel_agents)


def display_parallel_graph(
    agent_messages: Dict[str, List[Dict]], parallel_agents: Dict[str, str]
) -> None:
    """Отображение графа, показывающего взаимодействия параллельных агентов."""
    print("\n" + "=" * 80)
    print(color("\n🎯 Граф взаимодействий параллельных агентов", fg="cyan", style="bold"))
    print("=" * 80 + "\n")

    graphs = []

    for agent_id in sorted(parallel_agents.keys()):
        agent_name = parallel_agents[agent_id]
        messages = agent_messages.get(agent_id, [])

        if not messages:
            continue

        # Построение графа для этого агента
        graph_lines = []
        turn_counter = 0

        for i, msg in enumerate(messages):
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "user":
                # Сообщения пользователей не получают номера ходов
                if len(content) > 50:
                    content = content[:47] + "..."
                graph_lines.append(f"[cyan]● User[/cyan]")
                graph_lines.append(f"  {content}")
            elif role == "assistant":
                turn_counter += 1
                tool_calls = msg.get("tool_calls", [])
                if tool_calls:
                    tools_str = ", ".join(
                        [tc.get("function", {}).get("name", "?") for tc in tool_calls[:3]]
                    )
                    if len(tool_calls) > 3:
                        tools_str += f" (+{len(tool_calls)-3})"
                    graph_lines.append(
                        f"[bold red][{turn_counter}][/bold red] [yellow]▶ Агент[/yellow]"
                    )
                    graph_lines.append(f"  [dim]Инструменты: {tools_str}[/dim]")
                else:
                    graph_lines.append(
                        f"[bold red][{turn_counter}][/bold red] [yellow]▶ Агент[/yellow]"
                    )
                    if content and len(content.strip()) > 0:
                        preview = content[:50] + "..." if len(content) > 50 else content
                        graph_lines.append(f"  [dim]{preview}[/dim]")
            elif role == "tool":
                # Ответы инструментов получают тот же номер хода, что и их ассистент
                graph_lines.append(
                    f"[bold red][{turn_counter}][/bold red] [magenta]◆ Инструмент[/magenta]"
                )
                if content:
                    preview = content[:50] + "..." if len(content) > 50 else content
                    graph_lines.append(f"  [dim]{preview}[/dim]")

            if i < len(messages) - 1:
                graph_lines.append("    ↓")

        # Создание панели для этого агента
        agent_panel = Panel(
            "\n".join(graph_lines),
            title=f"[bold cyan]{agent_name} [{agent_id}][/bold cyan]",
            border_style="blue",
            padding=(0, 1),
            expand=False,
        )
        graphs.append(agent_panel)

    # Отображение графов в колонках
    if len(graphs) > 1:
        console.print(Columns(graphs, equal=False, expand=False, padding=(1, 2)))
    elif graphs:
        console.print(graphs[0])

    # Печать сводки
    console.print("\n[bold]Сводка:[/bold]")
    total_messages = sum(len(msgs) for msgs in agent_messages.values())
    unique_user_messages = len(
        set(
            msg.get("content", "")
            for msgs in agent_messages.values()
            for msg in msgs
            if msg.get("role") == "user"
        )
    )

    console.print(f"• Всего агентов: {len(parallel_agents)}")
    console.print(f"• Всего сообщений: {total_messages}")
    console.print(f"• Сообщений пользователей: {unique_user_messages}")
    console.print(
        f"• Среднее количество сообщений на агента: {total_messages / len(parallel_agents) if parallel_agents else 0:.1f}"
    )
    print("\n" + "=" * 80)


def parse_arguments():
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Инструмент для преобразования JSONL файлов в формат воспроизведения, имитирующий вывод CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # С использованием переменных окружения:
  JSONL_FILE_PATH="path/to/file.jsonl" REPLAY_DELAY="0.5" python3 tools/replay.py

  # С использованием позиционных аргументов:
  python3 tools/replay.py path/to/file.jsonl 0.5
  cai-replay path/to/file.jsonl 0.5

  # С использованием аргументов командной строки:
  python3 tools/replay.py --jsonl-file-path path/to/file.jsonl --replay-delay 0.5

  # С использованием позиционного аргумента только для файла:
  python3 tools/replay.py path/to/file.jsonl --replay-delay 0.5

  # С asciinema:
  asciinema rec --command="python3 tools/replay.py path/to/file.jsonl 0.5" --overwrite
""",
    )

    parser.add_argument(
        "jsonl_file",
        nargs="?",
        default=None,
        help="Путь к JSONL файлу, содержащему историю разговоров",
    )

    parser.add_argument(
        "replay_delay_pos",
        nargs="?",
        type=float,
        default=None,
        help="Время в секундах ожидания между действиями (позиционный аргумент)",
    )

    parser.add_argument(
        "--jsonl-file-path", type=str, help="Путь к JSONL файлу, содержащему историю разговоров"
    )

    parser.add_argument(
        "--replay-delay",
        type=float,
        default=0.5,
        help="Время в секундах ожидания между действиями (по умолчанию: 0.5)",
    )

    return parser.parse_args()


def main():
    """Основная функция для обработки JSONL файлов и генерации вывода воспроизведения."""
    # Отображение баннера
    display_banner(console)
    print("\n")

    # Разбор аргументов командной строки
    args = parse_arguments()

    # Получение переменных окружения или аргументов командной строки
    # Сначала проверяем --jsonl-file-path, затем позиционный аргумент, затем переменную окружения
    jsonl_file_path = args.jsonl_file_path or args.jsonl_file or os.environ.get("JSONL_FILE_PATH")

    # Для задержки воспроизведения приоритет: позиционный аргумент > --replay-delay > переменная окружения > значение по умолчанию
    if args.replay_delay_pos is not None:
        replay_delay = args.replay_delay_pos
    elif args.replay_delay != 0.5:      # Проверка --replay-delay был ли явно установлен
        replay_delay = args.replay_delay
    else:
        replay_delay = float(os.environ.get("REPLAY_DELAY", "0.5"))

    # Валидация обязательных параметров
    if not jsonl_file_path:
        print(
            color(
                "Ошибка: Требуется путь к JSONL файлу. Используйте позиционный аргумент, опцию --jsonl-file-path или установите переменную окружения JSONL_FILE_PATH.",
                fg="red",
            )
        )
        sys.exit(1)

    print(color(f"Загрузка JSONL файла: {jsonl_file_path}", fg="blue"))

    try:
        # Загрузка полного JSONL файла для извлечения выводов инструментов и имен агентов
        full_data = load_jsonl(jsonl_file_path)

        # Извлечение выводов инструментов из событий и поиск последнего сообщения ассистента
        tool_outputs = {}
        agent_names = {}  # Сохранение имен агентов по временной метке или другому идентификатору

        # Извлечение имен агентов из полных данных
        current_agent_name = None
        for entry in full_data:
            # Отслеживание текущего имени агента из различных событий
            if entry.get("agent_name"):
                current_agent_name = entry.get("agent_name")
                # Сохранение имени агента с временной меткой или другим идентификатором
                timestamp = entry.get("timestamp")
                if timestamp:
                    agent_names[timestamp] = entry.get("agent_name")

            # Также ищем события agent_run_start, которые содержат имена агентов
            if entry.get("event") == "agent_run_start" and entry.get("agent_name"):
                current_agent_name = entry.get("agent_name")

        # Загрузка JSONL файла для сообщений
        messages = load_history_from_jsonl(jsonl_file_path)

        # Присоединение выводов инструментов и имен агентов к сообщениям
        # Также отслеживание текущего агента для сообщений без временных меток
        last_known_agent = current_agent_name

        for i, message in enumerate(messages):
            # Попытка сопоставить имена агентов по временной метке
            msg_timestamp = message.get("timestamp")
            if msg_timestamp and msg_timestamp in agent_names:
                message["agent_name"] = agent_names[msg_timestamp]
                last_known_agent = agent_names[msg_timestamp]
            elif (
                message.get("role") == "assistant"
                and not message.get("agent_name")
                and last_known_agent
            ):
                # Если совпадения временной метки нет, но у нас есть последний известный агент, используем его
                message["agent_name"] = last_known_agent

            if message.get("role") == "assistant" and message.get("tool_calls"):
                if "tool_outputs" not in message:
                    message["tool_outputs"] = {}

                for tool_call in message.get("tool_calls", []):
                    call_id = tool_call.get("id", "")
                    if call_id in tool_outputs:
                        message["tool_outputs"][call_id] = tool_outputs[call_id]

        print(color(f"Загружено {len(messages)} сообщений из JSONL файла", fg="blue"))

        # Получение статистики токенов и стоимости из JSONL файла
        usage = get_token_stats(jsonl_file_path)

        # Отображение информации о времени при наличии (новый формат)
        if len(usage) > 4:
            print(color(f"Active time: {usage[4]:.2f}s", fg="blue"))
            print(color(f"Idle time: {usage[5]:.2f}s", fg="blue"))

        # Передача full_data в replay_conversation для поиска имени агента
        replay_conversation(messages, replay_delay, usage, jsonl_file_path, full_data)
        print(color("Воспроизведение успешно завершено", fg="green"))

        # Отображение общей стоимости
        active_time = usage[4] if len(usage) > 4 else 0
        idle_time = usage[5] if len(usage) > 5 else 0
        total_time = active_time + idle_time

        # Форматирование значений времени как строк с единицами измерения
        def format_time(seconds):
            """Форматирование времени в секундах в читаемую строку."""
            if seconds < 60:
                return f"{seconds:.1f}s"
            else:
                # Преобразование секунд в часы, минуты, секунды
                hours, remainder = divmod(seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                if hours > 0:
                    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
                else:
                    return f"{int(minutes)}m {int(seconds)}s"

        metrics = {
            "session_time": format_time(total_time),
            "llm_time": "0.0s",
            "llm_percentage": 0,
            "active_time": format_time(active_time),
            "idle_time": format_time(idle_time),
        }
        display_execution_time(metrics)

    except FileNotFoundError:
        print(color(f"Ошибка: Файл {jsonl_file_path} не найден", fg="red"))
        sys.exit(1)
    except json.JSONDecodeError:
        print(color(f"Ошибка: Недопустимый JSON в {jsonl_file_path}", fg="red"))
        sys.exit(1)
    except Exception as e:
        print(color(f"Ошибка: {str(e)}", fg="red"))
        sys.exit(1)
    finally:
        # Очистка переменной окружения для избежания загрязнения других процессов
        if "CAI_DISABLE_SESSION_RECORDING" in os.environ:
            del os.environ["CAI_DISABLE_SESSION_RECORDING"]


if __name__ == "__main__":
    main()
