"""CLI точка входа для CAI (Cybersecurity AI Framework).

Этот модуль — тонкий оркестратор:
  1. Инициализирует окружение через ``cli_setup``
  2. Разбирает CLI аргументы (argparse)
  3. Переключает в режим TUI или headless REPL (``cli_headless.run_cai_cli``)

Тяжёлая логика находится в:
  - ``cai.cli_setup``    -- загрузка .env, настройка предупреждений/логирования, инициализация CTF
  - ``cai.cli_headless`` -- интерактивный цикл REPL, выполнение агентов, параллельный режим
"""

# --- Инициализация ДО любых других импортов cai ---
from cai.cli_setup import bootstrap as _bootstrap
_bootstrap()

# --- Подавление шума "Event loop is closed" при выходе (Python 3.12+) ----------
# BaseSubprocessTransport.__del__ пытается закрыть каналы через закрытый цикл.
# Это безвредно, но выводит некрасивые трассировки. Патчим заранее.
import asyncio.base_subprocess as _abs
_original_bst_del = _abs.BaseSubprocessTransport.__del__

def _quiet_bst_del(self):
    try:
        _original_bst_del(self)
    except RuntimeError:
        pass  # "Event loop is closed" во время завершения интерпретатора — игнорируем

_abs.BaseSubprocessTransport.__del__ = _quiet_bst_del
# ---------------------------------------------------------------------------

import argparse
import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from cai.config import get_config
from cai.cli_setup import create_last_log_symlink
import cai.cli_setup as _cli_setup  # для обратной совместимости ctf_global
from cai.repl.commands.parallel import (
    PARALLEL_CONFIGS,
    load_parallel_config_from_yaml,
)
from cai.sdk.agents import set_tracing_disabled
from wasabi import color
from cai.util import ensure_litellm_transcription_support
from cai.repl.ui.banner import display_banner
from cai.repl.ui.startup_hints import StartupHints, mask_key_for_hint

# Повторный экспорт для обратной совместимости (другие модули импортируют из cai.cli)
__all__ = [
    "main",
    "run_cai_cli",
    "update_agent_models_recursively",
    "create_last_log_symlink",
    "START_TIME",
    "ctf_global",
]


def _resolve_alias_model_name(model_name: str | None) -> str:
    """Вернуть модель семейства alias, с fallback на CAI_MODEL затем alias1."""
    env_model = (os.getenv("CAI_MODEL", "alias1") or "alias1").strip()
    candidate = (model_name or env_model).strip()
    if candidate.lower().startswith("alias"):
        return candidate
    if env_model.lower().startswith("alias"):
        return env_model
    return "alias1"


def _print_deferred_update_notice(console: Console, update_info: dict) -> None:
    """Показать отложенное уведомление об обновлении после запуска."""
    if not update_info or not update_info.get("update_available"):
        return
    current_version = update_info.get("current_version", "unknown")
    latest_version = update_info.get("latest_version", "unknown")
    console.print(
        f"[#9aa0a6][CAI] Доступно обновление:[/] "
        f"[bold white]{current_version}[/bold white][#9aa0a6] -> [/]"
        f"[bold #00ff9d]{latest_version}[/bold #00ff9d]"
    )
    console.print(
        "[#9aa0a6][CAI] Выполните [/][bold #00ff9d]cai --update[/bold #00ff9d]"
        "[#9aa0a6] для просмотра и применения.[/]"
    )


def __getattr__(name):
    """Ленивый реэкспорт: headless CLI (тяжёлый импорт) и глобальные переменные cli_setup."""
    if name in ("run_cai_cli", "update_agent_models_recursively", "START_TIME"):
        import cai.cli_headless as _headless

        globals()["run_cai_cli"] = _headless.run_cai_cli
        globals()["update_agent_models_recursively"] = _headless.update_agent_models_recursively
        globals()["START_TIME"] = _headless.START_TIME
        return globals()[name]
    if name in ("ctf_global", "messages_ctf", "ctf_init", "first_ctf_time", "previous_ctf_name"):
        return getattr(_cli_setup, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _ensure_headless_bound() -> None:
    """Импортировать cli_headless в глобальные переменные этого модуля.

    ``__getattr__`` срабатывает только при доступе в стиле ``import cai.cli; cai.cli.run_cai_cli``;
    ``LOAD_GLOBAL`` внутри этого файла не вызывает его, поэтому внутренние
    вызывающие должны явно привязать перед использованием ``run_cai_cli`` /
    ``update_agent_models_recursively``.
    """
    g = globals()
    if "run_cai_cli" in g:
        return
    import cai.cli_headless as _headless

    g["run_cai_cli"] = _headless.run_cai_cli
    g["update_agent_models_recursively"] = _headless.update_agent_models_recursively
    g["START_TIME"] = _headless.START_TIME


def main():
    """Разобрать CLI аргументы и переключить в соответствующий режим."""
    deferred_update_info: dict | None = None
    update_holder: dict = {}
    update_thread: threading.Thread | None = None

    # Первый обратный вызов как можно скорее (только Rich — чтобы не импортировать cli_headless до headless REPL).
    boot_console = Console()
    boot = StartupHints(boot_console)
    boot.start("Запуск фреймворка CAI...")

    # --- Проверка системных зависимостей ---
    try:
        from cai.util_ext import check_system_dependencies, display_missing_dependencies_error
        all_ok, missing = check_system_dependencies()
        if not all_ok:
            boot.stop()
            display_missing_dependencies_error(missing)
            sys.exit(1)
    except Exception:
        pass

    # --- Проверка лицензии + запрос обновления ---
    # check_for_updates() может занять до ~10с (pip index). _chk() обращается к API через curl (~3–5с).
    # Запускаем параллельно, чтобы холодный старт был ~max(a,b) вместо a+b. Отключение: CAI_SKIP_UPDATE_CHECK=1
    try:
        from cai.util_ext import (
            _chk,
            check_for_updates,
            perform_update,
            prompt_for_update,
            user_env_requests_auto_framework_update,
        )
        boot.update(
            f"Проверка лицензии и API-ключа ({mask_key_for_hint(os.getenv('ALIAS_API_KEY', ''))})..."
        )
        skip_updates = os.getenv("CAI_SKIP_UPDATE_CHECK", "").lower() in ("1", "true", "yes")
        def _run_check_for_updates() -> None:
            try:
                update_holder["info"] = check_for_updates()
            except Exception:
                update_holder["info"] = None

        if not skip_updates:
            update_thread = threading.Thread(target=_run_check_for_updates, daemon=True)
            update_thread.start()

        if not _chk():
            boot.stop()
            # Вместо жесткого выхода, переключаемся в режим Community Edition
            Console(stderr=True).print(
                Panel(
                    "[bold yellow]LICENSE_KEY недействителен или не установлен[/bold yellow]\n\n"
                    "CAI запускается в режиме [bold]Community Edition (Research & Learning)[/bold].\n"
                    "Некоторые профессиональные функции (например, модель alias1) будут ограничены.\n\n"
                    "Для перехода на [bold]Professional Edition[/bold] установите действительный ALIAS_API_KEY.",
                    title="[yellow]Режим Community Edition[/yellow]",
                    border_style="yellow",
                )
            )
            # Мы не вызываем sys.exit(1), позволяя приложению продолжить работу.

        update_info = None
        if not skip_updates and update_thread is not None:
            # Сохраняем неблокирующий запуск: не ждём pip index на критическом пути.
            # Если фоновая проверка завершится быстро, мы всё ещё можем показать запрос.
            boot.update("Проверка обновлений фреймворка...")
            if not update_thread.is_alive():
                update_info = update_holder.get("info")

        if update_info and update_info.get("update_available"):
            boot.stop()
            api_key = os.getenv("ALIAS_API_KEY", "").strip()
            if user_env_requests_auto_framework_update() or prompt_for_update(update_info):
                if perform_update(api_key):
                    sys.exit(0)
            boot.start("Продолжение запуска...", leading_blank=False)
        elif update_info is not None and update_info.get("update_available") is False:
            from cai.repl.ui.banner import CAI_GREEN
            boot.stop()
            Console().print(
                f"[bold {CAI_GREEN}]✓[/bold {CAI_GREEN}] "
                f"[bold white]cai-framework {update_info.get('current_version', '')} "
                f"уже обновлён.[/bold white]"
            )
            boot.start("Продолжение запуска...", leading_blank=False)
    except Exception:
        pass

    # --- Argparse ---
    parser = argparse.ArgumentParser(
        prog="cai",
        description="Фреймворк искусственного интеллекта для кибербезопасности CAI",
        add_help=True,
        allow_abbrev=False,
    )
    parser.add_argument("--tui", action="store_true", help="Запустить CAI в режиме Textual UI")
    parser.add_argument("--yaml", dest="yaml_path", metavar="FILE", help="Загрузить определения агентов из YAML")
    parser.add_argument("--prompt", dest="prompt_override", metavar="TEXT", help="Начальная подсказка для немедленного выполнения")
    parser.add_argument("--version", action="store_true", help="Показать версию CAI и выйти")
    parser.add_argument("--update", action="store_true", help="Проверить обновления и установить если доступны")
    parser.add_argument("--continue", "-c", action="store_true", dest="continue_mode", help="Включить непрерывный режим")
    parser.add_argument("--unrestricted", action="store_true",
                        help="Включить управление abliteration (steering_enabled=true, thinking отключён)")
    parser.add_argument(
        "--yolo",
        action="store_true",
        help="Режим YOLo: пропустить подтверждение чувствительных команд (авто-одобрение запусков инструментов; небезопасно)",
    )
    parser.add_argument("--api", action="store_true", help="Запустить как HTTP API бэкенд")
    cfg = get_config()
    parser.add_argument("--api-host", default=cfg.api_host)
    parser.add_argument("--api-port", type=int, default=cfg.api_port)
    parser.add_argument("--api-reload", action="store_true", default=cfg.api_reload)
    parser.add_argument("--api-workers", type=int, default=cfg.api_workers)
    try:
        parsed_args, remaining_args = parser.parse_known_args()
    except SystemExit:
        boot.stop()
        raise

    _exit_if_removed_resume_cli_flags(sys.argv[1:])

    # --- --yolo (должен выполняться до агента/инструментов: отключает запросы чувствительных команд) ---
    if parsed_args.yolo:
        os.environ["CAI_YOLO"] = "true"

    # --- --unrestricted ---
    if parsed_args.unrestricted:
        os.environ["CAI_UNRESTRICTED"] = "true"
        # Та же точка входа совместимая с OpenAI что и CAI по умолчанию; LiteLLM маршрутизует по API-ключу + имени модели.
        _UNRESTRICTED_API_BASE = "https://api.aliasrobotics.com:666/"
        _UNRESTRICTED_MODEL = _resolve_alias_model_name(None)
        os.environ.setdefault("OPENAI_API_BASE", _UNRESTRICTED_API_BASE)
        os.environ.setdefault("CAI_MODEL", _UNRESTRICTED_MODEL)
        # Аутентификация: используйте ALIAS_API_KEY из .env (httpx_client предпочитает его).

    # --- --version ---
    if parsed_args.version:
        boot.stop()
        try:
            import importlib.metadata
            print(f"Фреймворк CAI v{importlib.metadata.version('cai-framework')}")
        except Exception:
            print("Фреймворк CAI (версия разработки)")
        sys.exit(0)

    # --- --update ---
    if parsed_args.update:
        boot.stop()
        _handle_update_command()
        return

    # --- Загрузка YAML ---
    resolved_yaml_path: Optional[Path] = None
    if parsed_args.yaml_path:
        boot.update("Загрузка конфигурации параллельных агентов...")
        candidate_path = Path(parsed_args.yaml_path).expanduser()
        quiet_load = parsed_args.tui
        if not load_parallel_config_from_yaml(candidate_path, quiet=quiet_load):
            boot.stop()
            if quiet_load:
                print(f"Ошибка: не удалось загрузить конфигурацию агентов '{parsed_args.yaml_path}'", file=sys.stderr)
            sys.exit(2)
        resolved_yaml_path = candidate_path.resolve()

        if not parsed_args.tui:
            boot.stop()
            print(f"Загружено {len(PARALLEL_CONFIGS)} параллельных агентов из {resolved_yaml_path}", file=sys.stderr)
            _maybe_enable_auto_run(resolved_yaml_path)
            boot.start("Продолжение запуска...", leading_blank=False)

    # --- Режим API-сервера ---
    if parsed_args.api:
        boot.stop()
        from cai.api.server import run_api_server
        try:
            run_api_server(
                host=parsed_args.api_host,
                port=parsed_args.api_port,
                reload=parsed_args.api_reload,
                workers=parsed_args.api_workers,
            )
        except KeyboardInterrupt:
            sys.exit(0)
        return

    # --- Режим TUI ---
    if parsed_args.tui:
        boot.stop()
        if resolved_yaml_path:
            os.environ["CAI_TUI_STARTUP_YAML"] = str(resolved_yaml_path)
        shared_prompt = parsed_args.prompt_override
        if not shared_prompt and remaining_args:
            shared_prompt = " ".join(remaining_args).strip()
        if shared_prompt:
            os.environ["CAI_TUI_SHARED_PROMPT"] = shared_prompt
        os.environ["CAI_TUI_MODE"] = "true"

        from cai.tui.display.context_preservation import enable_task_context_propagation
        enable_task_context_propagation()
        from cai.tui.cai_terminal import run_cai_tui
        run_cai_tui()
        return

    # --- Проверка конфигурации при запуске [B] ---
    config_warnings = cfg.validate()
    if config_warnings:
        boot.stop()
        console = Console(stderr=True)
        for w in config_warnings:
            console.print(f"[yellow]⚠ Предупреждение конфигурации: {w}[/yellow]")

    # --- Режим Headless CLI ---
    boot.set_message("Инициализация вывода CLI...")
    # Подключить OutputManager для событий вывода CLI [P+T].
    # Компактный режим (q3=b) по умолчанию; отключение через CAI_COMPACT_REPL=0
    # возвращает устаревший CLIOutputHandler.
    from cai.repl.ui.compact_wiring import install_compact_ui, is_compact_enabled
    if is_compact_enabled():
        install_compact_ui()
    else:
        from cai.output import OUTPUT, CLIOutputHandler
        OUTPUT.subscribe(CLIOutputHandler())

    from cai.util import ensure_litellm_logging_worker_loop_safety
    patch_applied = ensure_litellm_transcription_support()
    ensure_litellm_logging_worker_loop_safety()
    if not patch_applied:
        boot.stop()
        print(color("Не удалось включить поддержку транскрипции LiteLLM", color="red"))
        boot.start("Продолжение запуска...", leading_blank=False)

    boot.stop()
    try:
        from cai.repl.ui.terminal_title import set_terminal_window_title

        set_terminal_window_title()
    except Exception:
        pass
    display_banner(boot_console, model=cfg.model, agent_type=cfg.agent_type)
    boot_console.print()
    boot.start("Загрузка агента и среды выполнения сессии...", leading_blank=False)

    initial_prompt = _resolve_initial_prompt(parsed_args, remaining_args)
    boot.update("Определение агента из конфигурации...")
    _ensure_headless_bound()
    agent = _resolve_agent()
    _agent_type_resolved = os.getenv("CAI_AGENT_TYPE", cfg.agent_type)
    os.environ.setdefault(
        "CAI_AGENT_ROUTE_MODE",
        "auto"
        if _agent_type_resolved in ("selection_agent", "orchestration_agent")
        else "pinned",
    )
    boot.stop()
    if update_thread is not None and not update_thread.is_alive():
        deferred_update_info = update_holder.get("info")
    if deferred_update_info:
        _print_deferred_update_notice(boot_console, deferred_update_info)

    run_cai_cli(
        agent,
        initial_prompt=initial_prompt,
        continue_mode=getattr(parsed_args, "continue_mode", False),
        console=boot_console,
        skip_startup_banner=True,
    )


# ---------------------------------------------------------------------------
# Приватные вспомогательные функции для main()
# ---------------------------------------------------------------------------

def _handle_update_command():
    from cai.repl.ui.banner import CAI_GREEN
    from cai.util_ext import (
        _license_off,
        check_for_updates,
        perform_update,
        prompt_for_update,
        user_env_requests_auto_framework_update,
    )

    console = Console()
    oss_mode = _license_off()
    api_key = os.getenv("ALIAS_API_KEY", "").strip()
    if not oss_mode and not api_key:
        console.print(Panel(
            "[bold red]ALIAS_API_KEY не установлен[/bold red]\n\n"
            "Пожалуйста, установите действительный ALIAS_API_KEY в файле .env или переменной окружения, "
            "или установите [bold]CAI_LICENSE_OFF=1[/bold] для обновления из публичного PyPI.",
            title="[red]Ошибка аутентификации[/red]",
            border_style="red",
        ))
        sys.exit(1)

    console.print("[dim white]Проверка обновлений…[/dim white]")
    update_info = check_for_updates()
    if update_info and update_info.get("update_available"):
        if user_env_requests_auto_framework_update() or prompt_for_update(update_info):
            sys.exit(0 if perform_update(api_key) else 1)
        else:
            console.print("[italic dim white]Обновление отменено.[/italic dim white]")
    elif update_info is not None:
        console.print(
            f"[bold {CAI_GREEN}]✓[/bold {CAI_GREEN}] "
            f"[bold white]cai-framework {update_info.get('current_version', '')} "
            f"уже обновлён.[/bold white]"
        )
    else:
        console.print(
            "[yellow]Не удалось проверить обновления[/yellow] "
            "[dim white](ошибка сети или индекс недоступен).[/dim white]"
        )
        sys.exit(1)
    sys.exit(0)


def _maybe_enable_auto_run(resolved_yaml_path):
    from cai.config_loader import load_agents_config, extract_agent_definitions
    try:
        data, _ = load_agents_config(resolved_yaml_path)
        agents, metadata, _ = extract_agent_definitions(data)
        has_auto_run = any(a.get('auto_run', metadata.get('auto_run', False)) for a in agents)
        if has_auto_run and PARALLEL_CONFIGS:
            os.environ["CAI_AUTO_RUN_PARALLEL"] = "1"
            print("Авто-запуск включён для параллельных агентов. Они будут выполняться автоматически.", file=sys.stderr)
    except Exception:
        pass


def _resolve_initial_prompt(parsed_args, remaining_args):
    source = parsed_args.prompt_override or (" ".join(remaining_args) if remaining_args else None)
    if not source:
        return None

    initial_prompt = source
    if ';' in initial_prompt:
        commands = [cmd.strip() for cmd in initial_prompt.split(';')]
        if len(commands) > 1:
            initial_prompt = commands[0]
            from cai.repl.commands.queue import add_to_queue
            for cmd in commands[1:]:
                if cmd:
                    add_to_queue(cmd)
            os.environ["CAI_AUTO_RUN_QUEUE"] = "1"
    return initial_prompt


def _resolve_agent():
    cfg = get_config()
    agent_type = cfg.agent_type

    from cai.agents.patterns import get_pattern
    pattern = get_pattern(agent_type)

    if pattern and hasattr(pattern, "configs"):
        console = Console()
        console.print(f"[cyan]Загрузка паттерна из CAI_AGENT_TYPE: {agent_type}[/cyan]")
        PARALLEL_CONFIGS.clear()
        for idx, config in enumerate(pattern.configs, 1):
            config.id = f"P{idx}"
            PARALLEL_CONFIGS.append(config)
        if len(PARALLEL_CONFIGS) >= 2:
            os.environ["CAI_PARALLEL"] = str(len(PARALLEL_CONFIGS))
            os.environ["CAI_PARALLEL_AGENTS"] = ",".join(c.agent_name for c in PARALLEL_CONFIGS)
        console.print(f"[green]Загружен параллельный паттерн: {pattern.description}[/green]")
        for idx, config in enumerate(PARALLEL_CONFIGS, 1):
            resolved_model = _resolve_alias_model_name(config.model)
            model_info = f" [{resolved_model}]"
            console.print(f"  [P{idx}] {config.agent_name}{model_info}")
        from cai.agents import get_agent_by_name
        agent = get_agent_by_name(PARALLEL_CONFIGS[0].agent_name, agent_id="P1")
    else:
        from cai.agents import get_agent_by_name
        from cai.sdk.agents.simple_agent_manager import DEFAULT_SESSION_AGENT_ID

        agent = get_agent_by_name(agent_type, agent_id=DEFAULT_SESSION_AGENT_ID)

    from cai.sdk.agents.simple_agent_manager import AGENT_MANAGER
    AGENT_MANAGER.switch_to_single_agent(agent, getattr(agent, "name", agent_type))

    if hasattr(agent, "model"):
        if hasattr(agent.model, "disable_rich_streaming"):
            agent.model.disable_rich_streaming = True
        if hasattr(agent.model, "suppress_final_output"):
            agent.model.suppress_final_output = False

    update_agent_models_recursively(agent, cfg.model)
    return agent


def _exit_if_removed_resume_cli_flags(argv: list[str]) -> None:
    """Уведомить пользователей что --resume / --logpath были удалены (используйте /resume в REPL)."""
    removed: set[str] = set()
    for arg in argv:
        if arg == "--resume" or arg.startswith("--resume="):
            removed.add("--resume")
        elif arg == "--logpath" or arg.startswith("--logpath="):
            removed.add("--logpath")
    if not removed:
        return
    console = Console(stderr=True)
    flags = ", ".join(sorted(removed))
    console.print(
        f"[bold #00ff9d]Удалённые CLI флаги:[/bold #00ff9d] {flags}.\n"
        "[dim]Запустите CAI, затем используйте [/dim][bold #00ff9d]/resume[/bold #00ff9d][dim] "
        "(выберите из того же недавнего списка что и [/dim][bold #00ff9d]/sessions[/bold #00ff9d][dim]), "
        "[/dim][bold #00ff9d]/resume last[/bold #00ff9d][dim], путь `.jsonl`, каталог, "
        "или [/dim][bold #00ff9d]/sessions <n>[/bold #00ff9d][dim] для расширенного списка.[/dim]"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
