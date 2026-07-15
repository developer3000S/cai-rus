"""
Help command for CAI REPL.
This module provides commands for displaying help information.
"""

from typing import List, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError as exc:
    raise ImportError(
        "The 'rich' package is required. Please install it with: pip install rich"
    ) from exc

from cai.repl.commands.base import COMMAND_ALIASES, COMMANDS, Command, register_command
from cai.repl.commands.command_reference_index import categorized_command_tables
from cai.repl.commands.config import print_config_deprecated_message
from cai.repl.commands.settings_cli_catalog import settings_help_panel_subcommand_bullets
from cai.repl.ui.banner import _CAI_GREEN, _quick_guide_subpanel_title

console = Console()


def _h_panel_desc(text: str) -> str:
    """One-line intro for ``/h <topic>`` panels (below the green title bar; body, not dim)."""
    return f"[white]{text}[/white]\n\n"


def create_styled_table(
    title: Optional[str],
    headers: List[tuple[str, str]],
    header_style: str = "bold white",
) -> Table:
    """Create a styled table with consistent formatting.

    Args:
        title: The table title
        headers: List of (header_name, style) tuples
        header_style: Style for the header row

    Returns:
        A configured Table instance
    """
    table = Table(title=title, show_header=True, header_style=header_style)
    for header, style in headers:
        table.add_column(header, style=style)
    return table


def create_notes_panel(
    notes: List[str], title: str = "Примечания", border_style: str | None = None
) -> Panel:
    """Create a notes panel with consistent formatting.

    Args:
        notes: List of note strings
        title: Panel title
        border_style: Style for the panel border (defaults to CAI green)

    Returns:
        A configured Panel instance
    """
    notes_text = Text.from_markup("\n".join(f"• {note}" for note in notes))
    return Panel(
        notes_text,
        title=_quick_guide_subpanel_title(title),
        title_align="left",
        border_style=border_style or _CAI_GREEN,
        padding=(1, 1),
    )


def model_help_panel_markup() -> str:
    """Rich markup for ``/h model`` (authoritative model CLI syntax)."""
    z = _CAI_GREEN
    return (
        _h_panel_desc(
            "Выбор модели: просмотр и установка CAI_MODEL из краткой таблицы или полного каталога."
        )
        + f"[bold {z}]Синтаксис[/bold {z}]\n"
        f"• [bold {z}]/model[/bold {z}] — текущая модель и краткая таблица\n"
        f"• [bold {z}]/model show[/bold {z}] — полный каталог LiteLLM\n"
        f"• [bold {z}]/model show supported[/bold {z}] — только модели с function calling\n"
        f"• [bold {z}]/model show <term>[/bold {z}] — фильтр по имени\n"
        f"• [bold {z}]/model show supported <term>[/bold {z}] — фильтр по поддерживаемым\n"
        f"• [bold {z}]/model <name>[/bold {z}] или [bold {z}]/model <n>[/bold {z}] — установка "
        f"[bold]CAI_MODEL[/bold], если идентификатор есть в загруженном каталоге (вступает в силу на следующем ходу)\n\n"
        f"[bold {z}]Примечания[/bold {z}]\n"
        f"• Ключи API: [bold {z}]/env list[/bold {z}]\n"
        f"• Номера строк соответствуют [bold {z}]/model show[/bold {z}]; краткая таблица пропускает "
        "слоты только LiteLLM\n\n"
        f"[dim]Алиас: /mod[/dim]"
    )


def graph_help_panel_markup() -> str:
    """Rich markup for ``/h graph`` (aligned with ``GraphCommand`` subcommands)."""
    z = _CAI_GREEN
    return (
        _h_panel_desc(
            "Представления графа показывают сообщения пользователя, ассистента и инструментов; экспорт в json, dot или mermaid."
        )
        + f"[bold {z}]Доступные команды:[/bold {z}]\n"
        f"• [bold {z}]/graph[/bold {z}] или [bold {z}]/g[/bold {z}] — "
        "многоагентная раскладка, когда [bold]CAI_PARALLEL[/bold]>1 или существуют несколько параллельных слотов; "
        "в противном случае — активный агент\n"
        f"• [bold {z}]/graph show[/bold {z}] — то же, что и [bold {z}]/graph[/bold {z}]\n"
        f"• [bold {z}]/graph P1[/bold {z}] — граф для параллельного агента по id (напр. P2, P3)\n"
        f"• [bold {z}]/graph <agent_name>[/bold {z}] — граф для конкретного агента (имя может содержать пробелы)\n"
        f"• [bold {z}]/graph all[/bold {z}] — графы для каждого агента с историей\n"
        f"• [bold {z}]/graph timeline[/bold {z}] — таблица сообщений по агентам (по индексу сообщения)\n"
        f"• [bold {z}]/graph stats[/bold {z}] — подсчёт сообщений и вызовов инструментов по агентам\n"
        f"• [bold {z}]/graph export <format>[/bold {z}] — экспорт данных (необязательное имя файла)\n\n"
        f"[bold {z}]Примеры:[/bold {z}]\n"
        f"• [bold {z}]/graph[/bold {z}] — граф текущего контекста\n"
        f"• [bold {z}]/graph P2[/bold {z}] — граф для агента P2\n"
        f"• [bold {z}]/graph red_teamer[/bold {z}] — граф для этого агента\n"
        f"• [bold {z}]/graph timeline[/bold {z}] — таблица сообщений\n"
        f"• [bold {z}]/graph stats[/bold {z}] — статистика\n"
        f"• [bold {z}]/graph export mermaid graph.md[/bold {z}] — записать файл Mermaid\n"
        f"• [bold {z}]/g timeline[/bold {z}] — то же через алиас\n\n"
        f"[bold {z}]Возможности:[/bold {z}]\n"
        "• Панели нескольких агентов в параллельном режиме\n"
        "• Поток сообщений пользователя, ассистента и вызовов инструментов в графе\n"
        "• Таблица временной шкалы для кросс-агентного просмотра (порядок индексов, а не реальное время)\n"
        "• Статистика по агентам\n"
        "• Экспорт отслеживаемых историй в файл\n\n"
        "[dim]Экспорт: json (полные сообщения), dot (Graphviz), mermaid (текст диаграммы). "
        "Необязательный путь по умолчанию получает имя с временной меткой в текущей директории.[/dim]\n\n"
        f"[dim]Алиас: /g[/dim]"
    )


def cost_help_panel_markup() -> str:
    """Rich markup for ``/h cost`` (aligned with ``CostCommand`` subcommands)."""
    z = _CAI_GREEN
    return (
        _h_panel_desc(
            "Расходы текущей сессии и токены, а также глобальные итоги из ~/.cai/usage.json, "
            "когда включено отслеживание использования."
        )
        + f"[bold {z}]Синтаксис[/bold {z}]\n"
        f"• [bold {z}]/cost[/bold {z}] или [bold {z}]/cost summary[/bold {z}]: "
        "панели сессии + глобальная, фрагмент топ-моделей, подсказки для других представлений\n"
        f"• [bold {z}]/cost models[/bold {z}] — расходы и доля по моделям\n"
        f"• [bold {z}]/cost daily[/bold {z}] — последние 30 дней и недельная сводка\n"
        f"• [bold {z}]/cost sessions[/bold {z}] — недавние сессии (по умолчанию 10 строк); "
        f"необязательный числовой аргумент ограничивает строки (напр. [bold {z}]/cost sessions 5[/bold {z}])\n"
        f"• [bold {z}]/cost reset[/bold {z}] — очистить сохранённую статистику (введите RESET для подтверждения; сделайте резервную копию)\n\n"
        f"[bold {z}]Связанные[/bold {z}]\n"
        f"• [bold {z}]/context[/bold {z}] — куда уходят токены контекста (оценки по ролям + тяжёлые сообщения)\n\n"
        f"[bold {z}]Примечания[/bold {z}]\n"
        "• Токены кэша (чтение/запись) отображаются, когда бэкенд их сообщает (зависит от провайдера)\n"
        "• Некоторые представления используют локальную оценку; токенизация провайдера может отличаться в зависимости от модели\n\n"
        f"[dim]Алиасы: /costs, /usage. Глобальное отслеживание отключено: CAI_DISABLE_USAGE_TRACKING=true[/dim]"
    )


def auth_help_panel_markup() -> str:
    """Rich markup for ``/h auth`` (aligned with ``AuthCommand`` subcommands)."""
    z = _CAI_GREEN
    return (
        _h_panel_desc(
            "Сохранённые пользователи API (`AuthManager`): добавление именованной учётной записи или привязка устройства по IP."
        )
        + f"[bold {z}]Синтаксис[/bold {z}]\n"
        f"• [bold {z}]/auth add-user <username> <password>[/bold {z}] — регистрация пользователя\n"
        f"• [bold {z}]/auth add-ip <ip[:port]>[/bold {z}] — случайный пользователь + сессия, JSON через TCP к "
        "слушателю устройства (порт устройства из [bold]CAI_AUTH_DEVICE_PORT[/bold])\n\n"
        f"[dim][bold]base_url[/bold] устройства: [bold]CAI_AUTH_BASE_URL[/bold], если задан, иначе публичные переменные "
        f"хоста/порта и [bold]CAI_API_*[/bold]. [bold {z}]/auth[/bold {z}] без аргументов показывает "
        "список подкоманд.[/dim]"
    )


def commands_reference_panel_markup() -> str:
    """Full Rich markup for ``/h commands`` (single bordered panel, like ``/h agent``)."""
    z = _CAI_GREEN
    parts: list[str] = [
        _h_panel_desc(
            "Все доступные команды"
        )
    ]
    for category, commands in categorized_command_tables():
        parts.append(f"[bold {z}]{category}[/bold {z}]\n")
        for cmd, aliases, desc in commands:
            alias_suffix = (
                f" [dim]({aliases})[/dim]" if aliases and aliases.strip() else ""
            )
            parts.append(
                f"• [bold {z}]{cmd}[/bold {z}]{alias_suffix} — [white]{desc}[/white]\n"
            )
        parts.append("\n")
    parts.append(
        "[dim]• /h <topic> — например agent, env, model (индекс команд: /help topics)[/dim]"
    )
    return "".join(parts)


class HelpCommand(Command):
    """Command for displaying help information."""

    def __init__(self):
        """Initialize the help command."""
        super().__init__(
            name="/help",
            description=("Отображение справки о командах и возможностях"),
            aliases=["/h", "/?"],
        )

        # Add subcommands organized by category
        # Agent Management
        self.add_subcommand("agent", "Справка по командам агентов", self.handle_agent)
        self.add_subcommand("parallel", "Справка по параллельному выполнению", self.handle_parallel)
        self.add_subcommand("queue", "Справка по команде очереди", self.handle_queue)

        # Memory & History
        self.add_subcommand("memory", "Справка по сохранению памяти", self.handle_memory)
        self.add_subcommand("history", "Справка по истории разговоров", self.handle_history)
        self.add_subcommand(
            "compact", "Справка по сжатию разговоров", self.handle_compact
        )
        self.add_subcommand("flush", "Справка по очистке историй", self.handle_flush)
        self.add_subcommand("load", "Справка по загрузке файлов JSONL", self.handle_load)
        self.add_subcommand("save", "Справка по сохранению разговоров в JSONL", self.handle_save)
        self.add_subcommand(
            "merge", "Справка по слиянию историй агентов", self.handle_merge_help
        )

        self.add_subcommand("config", "Устарело — то же, что /config; используйте /env", self.handle_config)
        self.add_subcommand("env", "Справка по переменным окружения", self.handle_env)
        self.add_subcommand(
            "var",
            "Подробная справка по переменным окружения (/help var NAME)",
            self.handle_var,
        )
        self.add_subcommand(
            "workspace", "Справка по управлению рабочим пространством", self.handle_workspace
        )
        self.add_subcommand(
            "virtualization", "Справка по контейнерам Docker", self.handle_virtualization
        )

        # Tools & Integration
        self.add_subcommand("mcp", "Справка по Model Context Protocol", self.handle_mcp)
        self.add_subcommand("shell", "Справка по командам оболочки", self.handle_shell)

        # Utilities
        self.add_subcommand("model", "Справка по выбору модели", self.handle_model)
        self.add_subcommand("graph", "Справка по визуализации", self.handle_graph)
        self.add_subcommand(
            "aliases",
            "Список зарегистрированных алиасов команд",
            self.handle_aliases,
        )

        # Session & Cost
        self.add_subcommand("cost", "Справка по отслеживанию расходов", self.handle_cost)
        self.add_subcommand("context", "Справка по использованию контекста", self.handle_context)
        self.add_subcommand("exit", "Справка по выходу из CAI", self.handle_exit)
        self.add_subcommand("resume", "Справка по возобновлению сессии", self.handle_resume)
        self.add_subcommand("sessions", "Справка по списку сессий", self.handle_sessions)
        self.add_subcommand("replay", "Справка по воспроизведению сессий", self.handle_replay)
        self.add_subcommand(
            "continue", "Справка по режиму продолжения", self.handle_continue
        )

        # Model Tuning
        self.add_subcommand(
            "temperature", "Справка по настройке температуры", self.handle_temperature
        )
        self.add_subcommand("topp", "Справка по настройке top-p", self.handle_topp)

        # Advanced
        self.add_subcommand(
            "settings", "Справка по /settings (алиас /set)", self.handle_settings
        )
        self.add_subcommand("auth", "Справка по аутентификации API", self.handle_auth)
        self.add_subcommand("ctr", "Справка по анализу безопасности CTR", self.handle_ctr)
        self.add_subcommand("api", "Справка по /api: ALIAS_API_KEY в .env (Alias / CAI PRO)", self.handle_api)
        self.add_subcommand(
            "metadebug", "Справка по отладке мета-агента", self.handle_metadebug
        )

        # General
        self.add_subcommand("commands", "Список всех доступных команд", self.handle_commands)
        self.add_subcommand(
            "topics",
            "Команды по категориям + подсказки /help <topic>; /help добавляет таблицы окружения",
            self.handle_help_topics,
        )

    def handle_unknown_subcommand(self, subcommand: str) -> bool:
        """Legacy help tokens ``quick`` / ``quickstart`` → point to ``/quickstart``."""
        if subcommand in ("quick", "quickstart"):
            console.print(
                "[dim]Команды /help quick или /help quickstart не существует; используйте [bold]/quickstart[/bold] "
                "(алиасы: /qs, /quick).[/dim]"
            )
            return False
        return super().handle_unknown_subcommand(subcommand)

    def handle_memory(self, _: Optional[List[str]] = None) -> bool:
        """Show help for memory commands."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc("Память: сохранение, восстановление и управление снимками разговоров агентов.")
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/memory list[/bold #00ff9d] - Список сохранённых снимков памяти\n"
                "• [bold #00ff9d]/memory save [name] [agent][/bold #00ff9d] - Сохранить текущую историю агента\n"
                "• [bold #00ff9d]/memory apply <ID|name> [agent|all][/bold #00ff9d] - Применить память к агенту\n"
                "• [bold #00ff9d]/memory show <ID|name>[/bold #00ff9d] - Показать содержимое памяти\n"
                "• [bold #00ff9d]/memory delete <ID|name>[/bold #00ff9d] - Удалить сохранённую память\n"
                "• [bold #00ff9d]/memory merge <ID1> <ID2> [name][/bold #00ff9d] - Объединить памяти в одну\n"
                "• [bold #00ff9d]/memory status[/bold #00ff9d] - Показать текущие применённые памяти\n"
                "• [bold #00ff9d]/memory compact <agent|all>[/bold #00ff9d] - Сжать и сохранить историю агента\n"
                "• [bold #00ff9d]/memory remove <memory_id> <agent>[/bold #00ff9d] - Удалить конкретную память из агента\n"
                "• [bold #00ff9d]/memory clear <agent>[/bold #00ff9d] - Очистить все памяти агента\n"
                "• [bold #00ff9d]/memory list-applied [agent][/bold #00ff9d] - Показать применённые памяти\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/memory save pentest_login_flow[/bold #00ff9d] - Сохранить с пользовательским именем\n"
                "• [bold #00ff9d]/memory save[/bold #00ff9d] - Сохранить с автогенерированным именем\n"
                "• [bold #00ff9d]/memory show M001[/bold #00ff9d] - Просмотреть память по ID\n"
                "• [bold #00ff9d]/memory apply M001 P1[/bold #00ff9d] - Применить память к агенту P1\n"
                "• [bold #00ff9d]/memory delete M001[/bold #00ff9d] - Удалить память по ID\n"
                "• [bold #00ff9d]/memory compact red_teamer[/bold #00ff9d] - Сжать память одного агента\n"
                "• [bold #00ff9d]/memory remove M001 red_teamer[/bold #00ff9d] - Удалить одну память из агента\n"
                "• [bold #00ff9d]/memory clear red_teamer[/bold #00ff9d] - Очистить все памяти агента\n"
                "• [bold #00ff9d]/memory list-applied[/bold #00ff9d] - Показать все применённые памяти\n\n"
                f"[bold {z}]Рекомендуемый порядок:[/bold {z}]\n"
                "• 1. Выберите/используйте агента (напр. /agent red_teamer)\n"
                "• 2. Отправьте хотя бы один обычный запрос (не команду)\n"
                "• 3. Выполните /memory save <name>\n"
                "• 4. Используйте /memory list и /memory show для проверки\n"
                "• 5. Применяйте через /memory apply при необходимости\n\n"
                f"[bold {z}]Примечания:[/bold {z}]\n"
                "• Если '/memory save' сообщает об отсутствии истории, сначала отправьте запрос\n"
                "• ID памяти (напр., M001) — самый безопасный способ ссылаться на памяти\n"
                "• Используйте '/memory status' для просмотра текущих применённых памятей\n\n"
                "[dim]Алиас: /mem[/dim]",
                title=_quick_guide_subpanel_title("Команды памяти"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_agent(self, _: Optional[List[str]] = None) -> bool:
        """Show help for agent management."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Агенты — автономные ИИ-ассистенты. Точка входа по умолчанию: "
                    "[bold]selection_agent[/bold] (роутер только для передачи); "
                    "[bold]orchestration_agent[/bold] [bold white on bright_red] BETA [/] добавляет "
                    "поисковую маршрутизацию с инструментами специалистов. "
                    "См. [bold]/help var CAI_AGENT_TYPE[/bold] и [bold]/help var CAI_ORCHESTRATION_*[/bold]."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/agent list[/bold #00ff9d] - Список всех доступных агентов\n"
                "• [bold #00ff9d]/agent select <name>[/bold #00ff9d] - Переключиться на конкретного агента\n"
                "• [bold #00ff9d]/agent info <name>[/bold #00ff9d] - Показать детали и инструменты агента\n"
                "• [bold #00ff9d]/agent current[/bold #00ff9d] - Показать текущую конфигурацию агента\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/agent list[/bold #00ff9d] - Просмотреть всех доступных агентов\n"
                "• [bold #00ff9d]/agent select [/bold #00ff9d][red]red_teamer[/red]"
                " [dim]- Переключиться на агента атакующей безопасности[/dim]\n"
                "• [bold #00ff9d]/agent info [/bold #00ff9d][red]bug_bounter[/red]"
                " [dim]- Просмотреть детали агента поиска уязвимостей[/dim]\n"
                "• [bold #00ff9d]/a select [/bold #00ff9d][red]2[/red] [dim]- Выбрать агента по номеру (алиас)[/dim]\n\n"
                f"[bold {z}]Доступные агенты:[/bold {z}]\n"
                "• [bold #00ff9d]selection_agent[/bold #00ff9d] - Точка входа по умолчанию: роутер только для передачи "
                "(без инструментов специалиста оркестрации)\n"
                "• [bold #00ff9d]orchestration_agent[/bold #00ff9d] [bold white on bright_red] BETA [/] - "
                "Маршрутизация плюс [bold]run_specialist[/bold], двойной контест и "
                "[bold]run_parallel_specialists[/bold] "
                "(настройка воркеров через [bold]CAI_ORCHESTRATION_WORKER_MAX_TURNS[/bold]; опциональная подсказка "
                "многофронтового режима: [bold]CAI_ORCHESTRATION_MAS_HINT[/bold])\n"
                "• [bold #00ff9d]one_tool_agent[/bold #00ff9d] - Базовый решатель CTF\n"
                "• [bold #00ff9d]red_teamer[/bold #00ff9d] - Специалист атакующей безопасности\n"
                "• [bold #00ff9d]blue_teamer[/bold #00ff9d] - Специалист防御ной безопасности\n"
                "• [bold #00ff9d]bug_bounter[/bold #00ff9d] - Охотник за уязвимостями\n"
                "• [bold #00ff9d]dfir[/bold #00ff9d] - Цифровая forensicика и реагирование на инциденты\n"
                "• [bold #00ff9d]network_traffic_analyzer[/bold #00ff9d] - Анализ сети\n"
                "• [bold #00ff9d]flag_discriminator[/bold #00ff9d] - Извлечение флагов CTF\n"
                "• [bold #00ff9d]codeagent[/bold #00ff9d] - Генерация и анализ кода\n"
                "• [bold #00ff9d]thought[/bold #00ff9d] - Стратегическое планирование\n\n"
                "[dim]Алиас: /a[/dim]",
                title=_quick_guide_subpanel_title("Команды агентов"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_context(self, _: Optional[List[str]] = None) -> bool:
        """Show help for context usage breakdown."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Использование контекста: проверка распределения токенов (оценки по ролям и тяжёлые сообщения). "
                    "Полезно для диагностики быстрого роста токенов и решения о необходимости сжатия."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/context[/bold #00ff9d] - Оценка контекста по ролям (system/user/assistant/tool)\n"
                "• [bold #00ff9d]/context top[/bold #00ff9d] - Самые большие сообщения по оценке токенов (по умолчанию 8)\n"
                "• [bold #00ff9d]/context top 20[/bold #00ff9d] - Топ-20 тяжёлых сообщений\n\n"
                f"[bold {z}]Примечания:[/bold {z}]\n"
                "• Оценки учитывают только роль+содержимое сообщения; системные промпты и схемы инструментов добавляют дополнительную нагрузку\n"
                "• Токенизация провайдера может отличаться от локальных оценок в зависимости от модели\n\n"
                "[dim]Алиас: /ctx[/dim]",
                title=_quick_guide_subpanel_title("Использование контекста"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_graph(self, _: Optional[List[str]] = None) -> bool:
        """Show help for graph visualization."""
        console.print(
            Panel(
                graph_help_panel_markup(),
                title=_quick_guide_subpanel_title("Graph Commands"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_shell(self, _: Optional[List[str]] = None) -> bool:
        """Show help for shell command execution."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Оболочка: выполнение команд в текущей директории рабочего пространства или в контейнере, "
                    "когда задан CAI_ACTIVE_CONTAINER."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/shell <command>[/bold #00ff9d] - Выполнить команду оболочки\n\n"
                f"[bold {z}]Алиасы:[/bold {z}]\n"
                "• [bold #00ff9d]/s[/bold #00ff9d], [bold #00ff9d]$[/bold #00ff9d] - Сокращение для /shell\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/shell ls -la[/bold #00ff9d] [dim]- Список файлов[/dim]\n"
                "• [bold #00ff9d]/s pwd[/bold #00ff9d] [dim]- Текущая директория[/dim]\n"
                "• [bold #00ff9d]$ git status[/bold #00ff9d] [dim]- Статус git[/dim]",
                title=_quick_guide_subpanel_title("Команды оболочки"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_env(self, _: Optional[List[str]] = None) -> bool:
        """Show help for environment variables."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Окружение: ключи сессии и полный каталог используют те же таблицы, что и /help."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/env[/bold #00ff9d] — "
                "только ключи [dim]CAI_[/dim] / [dim]CTF_[/dim], установленные в процессе "
                "(как и раньше)\n"
                "• [bold #00ff9d]/env list[/bold #00ff9d] — "
                "все переменные каталога (#, текущее, по умолчанию, значения, когда, описание)\n"
                "• [bold #00ff9d]/env get <n|NAME>[/bold #00ff9d] — показать одну запись каталога\n"
                "• [bold #00ff9d]/env set <n|NAME> <value>[/bold #00ff9d] — установить по номеру или "
                "имени (значение может содержать пробелы; без кавычек)\n"
                "• [bold #00ff9d]/env default[/bold #00ff9d] — восстановить все переменные каталога "
                "до зарегистрированных значений по умолчанию\n\n"
                f"[bold {z}]Примечания:[/bold {z}]\n"
                "• Пример записи каталога: [bold]CAI_MODEL[/bold] ([bold]/env list[/bold], "
                "[bold]/help var CAI_MODEL[/bold]).\n"
                "• [bold]/help[/bold] по-прежнему включает полные таблицы справки по окружению.\n\n"
                "[dim]Алиас: /e[/dim]",
                title=_quick_guide_subpanel_title("Команды окружения"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_var(self, args: Optional[List[str]] = None) -> bool:
        """Long-form help for one or more environment variables."""
        from cai.repl.commands.env_var_help import example_cyan_line, usage_markup_bold, render_variable_help
        from cai.repl.ui.banner import environment_reference_outer_title

        if not args or not any(a.strip() for a in args):
            console.print(
                Panel(
                    Text.from_markup(
                        _h_panel_desc(
                            "Подробные строки для одной переменной каталога (полные таблицы — в /help)."
                        )
                        + f"{usage_markup_bold()}  [dim](одно или несколько имён)[/dim]\n\n"
                        "Подробная справка по одной переменной из таблиц под "
                        "[bold]/help[/bold]: "
                        "тип, когда применяется, значение по умолчанию и примеры для копирования.\n\n"
                        "[bold]Примеры[/bold]\n"
                        f"{example_cyan_line('CAI_MODEL')}\n"
                        f"{example_cyan_line('CAI_DEBUG')}\n\n"
                        "[dim]Все задокументированные переменные (включая бывшие «Дополнительные») находятся в каталоге /env.[/dim]"
                    ),
                    title=environment_reference_outer_title(),
                    title_align="left",
                    border_style=_CAI_GREEN,
                    padding=(1, 1),
                )
            )
            return True

        all_ok = True
        for token in args:
            raw = token.strip()
            if not raw:
                continue
            ok, canonical, body = render_variable_help(raw)
            if not ok:
                all_ok = False
            title_text = _quick_guide_subpanel_title(
                f"Переменная — {canonical}" if ok else f"Неизвестно — {canonical}"
            )
            style = _CAI_GREEN if ok else "red"
            console.print(
                Panel(
                    Text.from_markup(body),
                    title=title_text,
                    title_align="left",
                    border_style=style,
                    padding=(1, 1),
                )
            )
        return all_ok

    def handle_aliases(self, _: Optional[List[str]] = None) -> bool:
        """Show all command aliases."""
        return self.handle_help_aliases()

    def handle_model(self, _: Optional[List[str]] = None) -> bool:
        """Show help for model selection."""
        console.print(
            Panel(
                Text.from_markup(model_help_panel_markup(), overflow="fold"),
                title=_quick_guide_subpanel_title("Model Commands"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_config(self, _: Optional[List[str]] = None) -> bool:
        """Legacy ``/help config`` — deprecation notice only (use ``/env``)."""
        print_config_deprecated_message(console)
        return True

    def handle_no_args(self) -> bool:
        """Show the full quick guide (startup scaffolding panel; on demand only)."""
        from cai.repl.commands.environment_reference import print_environment_reference
        from cai.repl.ui.banner import display_quick_guide

        display_quick_guide(console)
        console.print()
        print_environment_reference(console)
        return True

    def _print_command_table(
        self,
        title: str,
        commands: List[tuple[str, str, str]],
        header_style: str | None = None,
        command_style: str | None = None,
        alias_column: str = "Алиас",
    ) -> None:
        """Print a table of commands with consistent formatting."""
        z = _CAI_GREEN
        hs = header_style if header_style is not None else f"bold {z}"
        cs = command_style if command_style is not None else f"bold {z}"
        table = create_styled_table(
            title,
            [
                ("Команда", cs),
                (alias_column, "#9aa0a6"),
                ("Описание", "white"),
            ],
            hs,
        )

        for cmd, alias, desc in commands:
            table.add_row(cmd, alias, desc)

        console.print(table)

    def handle_help_topics(self, _: Optional[List[str]] = None) -> bool:
        """Topic index: intro, categorized commands, tips (no environment-variable tables)."""
        from cai.repl.ui.banner import display_help_topics_index

        display_help_topics_index(console)
        return True

    def handle_help(self) -> bool:
        """Same output as bare ``/help``: two-column quick guide + env reference."""
        return self.handle_no_args()

    def handle_help_aliases(self) -> bool:
        """Show all command aliases in a well-formatted table."""
        z = _CAI_GREEN
        accent = f"bold {z}"
        intro = (
            f"[bold]Алиасы команд[/bold]"
        )
        console.print(
            Panel(
                Text.from_markup(intro, overflow="fold"),
                title=_quick_guide_subpanel_title("Алиасы"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )

        alias_table = create_styled_table(
            None,
            [
                ("Алиас", accent),
                ("Команда", accent),
                ("Описание", "white"),
            ],
            accent,
        )

        for alias, command in sorted(COMMAND_ALIASES.items()):
            cmd = COMMANDS.get(command)
            description = cmd.description if cmd else ""
            alias_table.add_row(alias, command, description)

        console.print(alias_table)

        tips = [
            "Используйте алиас как первый токен строки, так же, как и полное имя команды.",
            (
                f"Пример: [bold {z}]/a list[/bold {z}] вместо [bold {z}]/agent list[/bold {z}], или "
                f"[bold {z}]/mem list[/bold {z}] вместо [bold {z}]/memory list[/bold {z}]."
            ),
            "[dim]Оболочка: `$` работает только в начале строки (те же правила маршрутизации, что и `/`).[/dim]",
        ]
        console.print("\n")
        console.print(create_notes_panel(tips, "Советы"))

        return True

    def handle_parallel(self, _: Optional[List[str]] = None) -> bool:
        """Show help for parallel execution."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Параллельное выполнение: запуск нескольких агентов одновременно с изолированными историями, затем слияние."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/parallel[/bold #00ff9d] - Показать текущую конфигурацию\n"
                "• [bold #00ff9d]/parallel add <agent>[/bold #00ff9d] - Добавить агента в параллельную конфигурацию\n"
                "• [bold #00ff9d]/parallel run[/bold #00ff9d] - Выполнить настроенных параллельных агентов\n"
                "• [bold #00ff9d]/parallel list[/bold #00ff9d] - Список настроенных агентов\n"
                "• [bold #00ff9d]/parallel clear[/bold #00ff9d] - Очистить все конфигурации\n"
                "• [bold #00ff9d]/parallel remove <index>[/bold #00ff9d] - Удалить конкретного агента\n"
                "• [bold #00ff9d]/parallel override-models[/bold #00ff9d] - Использовать глобальную модель для всех\n"
                "• [bold #00ff9d]/parallel merge <indices>[/bold #00ff9d] - Объединить истории агентов\n"
                "• [bold #00ff9d]/parallel prompt <index> <text>[/bold #00ff9d] - Установить пользовательский промпт\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/parallel add red_teamer[/bold #00ff9d] - Добавить агента red team\n"
                "• [bold #00ff9d]/parallel prompt P1 Analyze service exposure[/bold #00ff9d]\n"
                "• [bold #00ff9d]/parallel run[/bold #00ff9d] - Выполнить настроенных параллельных агентов\n"
                "• [bold #00ff9d]/merge[/bold #00ff9d] - Объединить и автоматически выйти из параллельного режима\n"
                "• [bold #00ff9d]/p list[/bold #00ff9d] - Показать всех настроенных агентов\n\n"
                f"[bold {z}]Примечания:[/bold {z}]\n"
                "• Агенты работают независимо с изолированными контекстами\n"
                "• Каждый агент получает уникальный ID (P1, P2 и т.д.)\n"
                "• Результаты отображаются бок о бок\n"
                "• /merge объединяет контексты всех параллельных агентов и выходит из параллельного режима\n"
                "• /parallel clear выходит из параллельного режима без объединения контекстов\n"
                "• /parallel add <agent> --model alias1 устанавливает пользовательскую модель\n"
                "• Используйте переменную окружения CAI_PARALLEL для установки количества по умолчанию\n\n"
                "[dim]Алиасы: /par, /p[/dim]",
                title=_quick_guide_subpanel_title("Параллельные команды"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_queue(self, _: Optional[List[str]] = None) -> bool:
        """Show help for queue commands."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc("Очередь: постановка запросов в очередь для последовательного выполнения на активном или выбранном агенте.")
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/queue или /queue show[/bold #00ff9d] - Показать состояние очереди\n"
                "• [bold #00ff9d]/queue add <prompt>[/bold #00ff9d] - Добавить запрос в очередь (активный агент)\n"
                "• [bold #00ff9d]/queue add --agent <name> <prompt>[/bold #00ff9d] - Добавить с конкретным агентом\n"
                "• [bold #00ff9d]/queue list[/bold #00ff9d] - Список запросов в очереди\n"
                "• [bold #00ff9d]/queue clear[/bold #00ff9d] - Очистить очередь запросов\n"
                "• [bold #00ff9d]/queue remove <index>[/bold #00ff9d] - Удалить один запрос из очереди\n"
                "• [bold #00ff9d]/queue move <from> <to>[/bold #00ff9d] - Переместить запрос на новую позицию\n"
                "• [bold #00ff9d]/queue next[/bold #00ff9d] - Показать следующий запрос в очереди\n"
                "• [bold #00ff9d]/queue load <file>[/bold #00ff9d] - Загрузить запросы из файла\n"
                "• [bold #00ff9d]/queue run[/bold #00ff9d] - Выполнить все запросы в очереди\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                '• [bold #00ff9d]/queue add Analyze this target service[/bold #00ff9d]\n'
                "• [bold #00ff9d]/queue add --agent red_teamer scan target[/bold #00ff9d]\n"
                "• [bold #00ff9d]/queue move 3 1[/bold #00ff9d] - Переместить элемент #3 на позицию #1\n"
                "• [bold #00ff9d]/queue clear[/bold #00ff9d] - Очистить очередь\n"
                "• [bold #00ff9d]/queue load prompts.txt[/bold #00ff9d] - Загрузить запросы из файла\n\n"
                "[dim]Алиас: /que[/dim]",
                title=_quick_guide_subpanel_title("Команды очереди"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_history(self, _: Optional[List[str]] = None) -> bool:
        """Show help for conversation history."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "История: просмотр, поиск и детальный анализ транскриптов по агентам и параллельным слотам."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/history[/bold #00ff9d] - Панель управления (дерево агентов)\n"
                "• [bold #00ff9d]/history all[/bold #00ff9d] - Отобразить все истории агентов хронологически\n"
                "• [bold #00ff9d]/history <agent>[/bold #00ff9d] или [bold #00ff9d]/history <ID>[/bold #00ff9d]"
                " - Показать историю конкретного агента\n"
                "• [bold #00ff9d]/history agent <name>[/bold #00ff9d] - Показать историю по имени агента\n"
                "• [bold #00ff9d]/history search <term>[/bold #00ff9d] - Поиск сообщений среди всех агентов\n"
                "• [bold #00ff9d]/history index <agent> <index> [role][/bold #00ff9d]"
                " - Показать конкретное сообщение по индексу\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/history[/bold #00ff9d] - Открыть панель управления агентами\n"
                "• [bold #00ff9d]/history P1[/bold #00ff9d] - Показать разговор P1\n"
                "• [bold #00ff9d]/history agent red_teamer[/bold #00ff9d] - Показать историю red_teamer\n"
                '• [bold #00ff9d]/history search "password"[/bold #00ff9d] - Поиск по запросу\n'
                "• [bold #00ff9d]/history index red_teamer 5[/bold #00ff9d] - Показать сообщение #5\n"
                "• [bold #00ff9d]/history index P1 3 user[/bold #00ff9d] - Показать 3-е сообщение пользователя от P1\n\n"
                f"[bold {z}]Возможности:[/bold {z}]\n"
                "• Подсчёт сообщений и разбивка по ролям для каждого агента\n"
                "• Визуализация ролей сообщений (цветовая кодировка)\n"
                "• Детали вызовов инструментов\n"
                "• Используйте [bold #00ff9d]/save <file>.jsonl[/bold #00ff9d] для снимков ([bold #00ff9d]/load[/bold #00ff9d]); "
                "[bold #00ff9d].md[/bold #00ff9d] для читаемого экспорта\n"
                "• Индикатор состояния памяти\n"
                "• Поддержка параллельных агентов (изолированные истории)\n\n"
                "[dim]Алиас: /his[/dim]",
                title=_quick_guide_subpanel_title("Команды истории"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_compact(self, _: Optional[List[str]] = None) -> bool:
        """Show help for conversation compaction."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Сжатие: использование модели резюмирования для уменьшения длинных тредов и освобождения контекста."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/compact[/bold #00ff9d] - Сжать текущий разговор\n"
                "• [bold #00ff9d]/compact model <name>[/bold #00ff9d] - Установить модель сжатия по имени\n"
                "• [bold #00ff9d]/compact model <number>[/bold #00ff9d] - Установить модель сжатия по номеру из таблицы\n"
                "• [bold #00ff9d]/compact model default[/bold #00ff9d] - Сбросить на модель текущего агента\n"
                "• [bold #00ff9d]/compact prompt <text>[/bold #00ff9d] - Установить пользовательский промпт резюмирования\n"
                "• [bold #00ff9d]/compact prompt reset[/bold #00ff9d] - Сбросить на промпт по умолчанию\n"
                "• [bold #00ff9d]/compact status[/bold #00ff9d] - Показать текущие настройки\n\n"
                f"[bold {z}]Флаги (разовое переопределение):[/bold {z}]\n"
                "• [bold #00ff9d]/compact --model <model>[/bold #00ff9d] - Сжать с конкретной моделью\n"
                "• [bold #00ff9d]/compact --prompt <text>[/bold #00ff9d] - Сжать с пользовательским промптом\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/compact model o3-mini[/bold #00ff9d] - Установить O3 Mini как модель сжатия\n"
                "• [bold #00ff9d]/compact model 3[/bold #00ff9d] - Установить модель по номеру из таблицы\n"
                "• [bold #00ff9d]/compact model default[/bold #00ff9d] - Использовать модель текущего агента\n"
                '• [bold #00ff9d]/compact prompt "Focus on vulnerabilities"[/bold #00ff9d] - Установить пользовательский промпт\n'
                "• [bold #00ff9d]/compact prompt reset[/bold #00ff9d] - Сбросить на промпт по умолчанию\n"
                "• [bold #00ff9d]/cmp status[/bold #00ff9d] - Проверить конфигурацию\n"
                "• [bold #00ff9d]/compact --model o3-mini[/bold #00ff9d] - Разовое сжатие с конкретной моделью\n"
                '• [bold #00ff9d]/compact --prompt "Focus on credentials"[/bold #00ff9d] - Разовый пользовательский промпт\n\n'
                f"[bold {z}]Возможности:[/bold {z}]\n"
                "• Сохранение важного контекста\n"
                "• Сокращение использования токенов\n"
                "• Сохранение в память (с префиксом M)\n"
                "• Очистка истории после сжатия\n\n"
                "[dim]Алиас: /cmp[/dim]",
                title=_quick_guide_subpanel_title("Команды сжатия"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_flush(self, _: Optional[List[str]] = None) -> bool:
        """Show help for clearing histories."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Очистка: удаление сохранённых сообщений с сохранением агентов, инструментов и MCP в настроенной конфигурации."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/flush[/bold #00ff9d] - Очистить историю текущего агента\n"
                "• [bold #00ff9d]/flush all[/bold #00ff9d] - Очистить все истории агентов\n"
                "• [bold #00ff9d]/flush <agent>[/bold #00ff9d] - Очистить конкретного агента\n"
                "• [bold #00ff9d]/flush P1[/bold #00ff9d] - Очистить параллельного агента P1\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/flush[/bold #00ff9d] - Очистить активного агента\n"
                "• [bold #00ff9d]/flush all[/bold #00ff9d] - Сбросить всех агентов\n"
                "• [bold #00ff9d]/flush red_teamer[/bold #00ff9d] - Очистить агента red team\n"
                "• [bold #00ff9d]/clear P2[/bold #00ff9d] - Очистить параллельного агента P2\n\n"
                f"[bold {z}]Действия:[/bold {z}]\n"
                "• Удаляет все сообщения\n"
                "• Сбрасывает счётчики токенов\n"
                "• Сохраняет конфигурацию агента\n"
                "• Сохраняет подключения MCP\n\n"
                "[dim]Алиас: /clear[/dim]",
                title=_quick_guide_subpanel_title("Команды очистки"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_load(self, _: Optional[List[str]] = None) -> bool:
        """Show help for loading JSONL files."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc("Загрузка JSONL-транскриптов из /save (или другого места) обратно в агентов.")
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/load <file>[/bold #00ff9d] - Загрузить для текущего агента\n"
                "• [bold #00ff9d]/load <file> agent <name>[/bold #00ff9d] - Загрузить для конкретного агента\n"
                "• [bold #00ff9d]/load <file> all[/bold #00ff9d] - Распределить среди всех агентов\n"
                "• [bold #00ff9d]/load <file> parallel[/bold #00ff9d] - Умное параллельное распределение\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/load session.jsonl[/bold #00ff9d] - Загрузить для текущего агента ([dim]используйте .jsonl из /save, а не .md[/dim])\n"
                "• [bold #00ff9d]/load ctf.jsonl agent red_teamer[/bold #00ff9d] - Загрузить для red team\n"
                "• [bold #00ff9d]/load scan.jsonl all[/bold #00ff9d] - Разделить между агентами\n"
                "• [bold #00ff9d]/l pentest.jsonl parallel[/bold #00ff9d] - Загрузка по шаблонам\n\n"
                "Используйте [bold #00ff9d]/save file.jsonl[/bold #00ff9d] для повторной загрузки через [bold #00ff9d]/load[/bold #00ff9d]; "
                "[bold #00ff9d].md[/bold #00ff9d] экспорты только для чтения (не для /load).\n"
                "[dim]/history export[/dim] устарело; используйте [bold #00ff9d]/save[/bold #00ff9d].\n\n"
                f"[bold {z}]Режимы распределения:[/bold {z}]\n"
                "• [bold #00ff9d]agent[/bold #00ff9d] - Загрузить всё одному агенту\n"
                "• [bold #00ff9d]all[/bold #00ff9d] - Распределение по кругу\n"
                "• [bold #00ff9d]parallel[/bold #00ff9d] - Сопоставление по шаблонам агентов\n\n"
                "[dim]Алиас: /l[/dim]",
                title=_quick_guide_subpanel_title("Команды загрузки"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_save(self, _: Optional[List[str]] = None) -> bool:
        """Show help for saving conversation JSONL or Markdown."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Сохранение: экспорт JSONL для /load или Markdown для людей; используйте после /flush для безопасного архивирования."
                )
                + f"[bold {z}]Форматы:[/bold {z}]\n"
                "• [bold #00ff9d].jsonl[/bold #00ff9d] — машинный формат, один JSON-объект на строку "
                "([dim]agent, role, content[/dim], поля инструментов). Используйте с [bold]/load[/bold].\n"
                "• [bold #00ff9d].md[/bold #00ff9d] или [bold #00ff9d].markdown[/bold #00ff9d] — читаемый "
                "отчёт (заголовки по агентам и ролям). Не загружается через [bold]/load[/bold].\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/save session.jsonl[/bold #00ff9d]\n"
                "• [bold #00ff9d]/save findings.md[/bold #00ff9d]\n"
                "• [bold #00ff9d]/save ~/notes/cai_thread.jsonl[/bold #00ff9d]\n\n"
                "Пути с тильдой ([bold]~/...[/bold]) раскрываются; родительские директории создаются при необходимости.\n"
                "Не то же самое, что [bold]/memory save[/bold] (резюмированная память в [dim].cai/memory[/dim]).\n\n"
                "[dim]Устарело: /history export — используйте /save.[/dim]",
                title=_quick_guide_subpanel_title("Команды сохранения"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_workspace(self, _: Optional[List[str]] = None) -> bool:
        """Show help for workspace management."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Метки и пути рабочего пространства для CAI_WORKSPACE; /workspace или /workspace get показывает состояние."
                )
                + f"[bold {z}]Подкоманды[/bold {z}] ([dim]алиас[/dim] [bold #00ff9d]/ws[/bold #00ff9d])\n"
                "• [bold #00ff9d]/workspace set <name>[/bold #00ff9d] — установить метку рабочего пространства\n"
                "• [bold #00ff9d]/workspace get[/bold #00ff9d] — то же, что и [bold]/ws[/bold]\n"
                "• [bold #00ff9d]/workspace ls[/bold #00ff9d] [dim](необязательный путь в рабочем пространстве)[/dim] — список файлов\n"
                "• [bold #00ff9d]/workspace exec <cmd>[/bold #00ff9d] — выполнить команду оболочки в текущей директории рабочего пространства\n"
                "• [bold #00ff9d]/workspace copy <src> <dst>[/bold #00ff9d] — хост ↔ контейнер через [bold]docker cp[/bold]; "
                "[bold]container:[/bold] ровно на одном пути; требуется [dim]CAI_ACTIVE_CONTAINER[/dim] "
                "([dim]/h virtualization[/dim])\n\n"
                "[dim]Базовый путь хоста:[/dim] [dim]CAI_WORKSPACE_DIR[/dim]\n\n"
                "[dim]Алиас: /ws[/dim]",
                title=_quick_guide_subpanel_title("Команды рабочего пространства"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_virtualization(self, _: Optional[List[str]] = None) -> bool:
        """Show help for Docker container management."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Виртуализация: привязка CAI к контейнерам Docker для изолированного запуска инструментов безопасности."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/virtualization[/bold #00ff9d] или [bold #00ff9d]/virtualization info[/bold #00ff9d] — полное состояние (алиас [bold #00ff9d]/virt[/bold #00ff9d])\n"
                "• [bold #00ff9d]/virtualization list[/bold #00ff9d] - Список контейнеров Docker\n"
                "• [bold #00ff9d]/virtualization set <container_id>[/bold #00ff9d] - Установить активный контейнер (префикс, если уникален)\n"
                "• [bold #00ff9d]/virtualization clear[/bold #00ff9d] - Вернуться на хост\n"
                "• [bold #00ff9d]/virtualization pull <image>[/bold #00ff9d] - Загрузить образ Docker\n"
                "• [bold #00ff9d]/virtualization run <image|id>[/bold #00ff9d] - Новый контейнер из образа или активировать, если <id> совпадает с префиксом контейнера\n"
                "• [bold #00ff9d]/virtualization <image_or_pen_id>[/bold #00ff9d] - Переключение (то же, что и короткая команда)\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/virt pull kalilinux/kali-rolling[/bold #00ff9d] - Загрузить Kali\n"
                "• [bold #00ff9d]/virt run parrotsec/security[/bold #00ff9d] - Запустить Parrot OS\n"
                "• [bold #00ff9d]/virt set abc123def456[/bold #00ff9d] - Активировать контейнер по ID\n"
                "• [bold #00ff9d]/virt abc123def456[/bold #00ff9d] - То же (короткая команда)\n\n"
                f"[bold {z}]Поддерживаемые образы:[/bold {z}]\n"
                "• [bold #00ff9d]kalilinux/kali-rolling[/bold #00ff9d] - Kali Linux\n"
                "• [bold #00ff9d]parrotsec/security[/bold #00ff9d] - Parrot Security\n"
                "• [bold #00ff9d]Любой образ для безопасности[/bold #00ff9d]\n\n"
                f"[bold {z}]Возможности:[/bold {z}]\n"
                "• Сетевая связность хоста включена\n"
                "• Монтирование рабочего пространства\n"
                "• Интерактивный TTY\n"
                "• Устанавливает CAI_ACTIVE_CONTAINER\n\n",
                title=_quick_guide_subpanel_title("Команды виртуализации"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_mcp(self, _: Optional[List[str]] = None) -> bool:
        """Show help for Model Context Protocol."""
        from cai.repl.commands.mcp import mcp_help_panel_markup

        console.print(
            Panel(
                mcp_help_panel_markup(),
                title=_quick_guide_subpanel_title("MCP Commands"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_cost(self, _: Optional[List[str]] = None) -> bool:
        """Show help for cost tracking."""
        console.print(
            Panel(
                cost_help_panel_markup(),
                title=_quick_guide_subpanel_title("Cost Commands"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_exit(self, _: Optional[List[str]] = None) -> bool:
        """Show help for exiting CAI."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Выход из REPL: сессия завершается и отображается краткое резюме "
                    "(то же, что и Ctrl+C)."
                )
                + f"[bold {z}]Команда:[/bold {z}]\n"
                f"• [bold {z}]/exit[/bold {z}] — выйти из CAI\n\n"
                f"[bold {z}]Алиасы:[/bold {z}] [dim]/q, /quit[/dim]\n\n"
                f"[bold {z}]Также:[/bold {z}] [dim]Ctrl+C в приглашении[/dim]\n",
                title=_quick_guide_subpanel_title("Команды выхода"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_resume(self, _: Optional[List[str]] = None) -> bool:
        """Show help for session resume."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Возобновление заменяет старые флаги ``cai --resume`` / ``--logpath``: выберите журнал, "
                    "воспроизведите его, затем загрузите историю в активного агента."
                )
                + f"[bold {z}]Команды:[/bold {z}]\n"
                "• [bold #00ff9d]/resume[/bold #00ff9d] — те же [bold #00ff9d]10[/bold #00ff9d] последних сессий, что и "
                "[bold #00ff9d]/sessions[/bold #00ff9d]; введите номер для загрузки\n"
                "• [bold #00ff9d]/resume last[/bold #00ff9d] — самый свежий журнал в [dim]logs/[/dim] с сообщениями\n"
                "• [bold #00ff9d]/resume <file.jsonl>[/bold #00ff9d] — загрузить эту запись\n"
                "• [bold #00ff9d]/resume <dir>[/bold #00ff9d] — выбрать из до 10 самых свежих [dim].jsonl[/dim] в "
                "[dim]dir[/dim] (рекурсивно)\n"
                "• [bold #00ff9d]/resume <dir> <token>[/bold #00ff9d] — самый свежий [dim].jsonl[/dim] в "
                "[dim]dir[/dim], имя которого содержит [dim]token[/dim]\n"
                "• [bold #00ff9d]/resume <token>[/bold #00ff9d] — поиск в именах файлов [dim]logs/cai_*.jsonl[/dim] "
                "(не путь)\n\n"
                f"[bold {z}]Связанные:[/bold {z}]\n"
                "• [bold #00ff9d]/sessions[/bold #00ff9d], [bold #00ff9d]/sessions <n>[/bold #00ff9d]\n\n"
                "[dim]Алиас: /r[/dim]",
                title=_quick_guide_subpanel_title("Команды возобновления"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_sessions(self, _: Optional[List[str]] = None) -> bool:
        """Show help for session listing."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Сессии: просмотр JSONL-журналов на диске. Список по умолчанию соответствует первому шагу "
                    "[bold #00ff9d]/resume[/bold #00ff9d] (10 самых свежих с сообщениями)."
                )
                + f"[bold {z}]Команды:[/bold {z}]\n"
                "• [bold #00ff9d]/sessions[/bold #00ff9d] — последние [bold #00ff9d]10[/bold #00ff9d] сессий "
                "([dim]logs/cai_*.jsonl[/dim])\n"
                "• [bold #00ff9d]/sessions <n>[/bold #00ff9d] — последние [dim]n[/dim] сессий\n"
                "• [bold #00ff9d]/sessions <id|path>[/bold #00ff9d] — метаданные одного журнала\n\n"
                f"[bold {z}]Связанные:[/bold {z}]\n"
                "• [bold #00ff9d]/resume[/bold #00ff9d] — выбрать и воспроизвести для агента\n\n"
                "[dim]Алиас: /sess[/dim]",
                title=_quick_guide_subpanel_title("Команды сессий"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_replay(self, _: Optional[List[str]] = None) -> bool:
        """Show help for session replay."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc("Воспроизведение JSONL-записи с необязательной задержкой; остановка из TUI при необходимости.")
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/replay <file.jsonl>[/bold #00ff9d] - Воспроизвести разговор\n"
                "• [bold #00ff9d]/replay <file.jsonl> <delay>[/bold #00ff9d] - Воспроизвести с пользовательской задержкой\n"
                "• [bold #00ff9d]/replay stop[/bold #00ff9d] - Отменить активное воспроизведение (TUI)\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/replay session.jsonl[/bold #00ff9d] - Воспроизвести на стандартной скорости\n"
                "• [bold #00ff9d]/replay session.jsonl 2[/bold #00ff9d] - Задержка 2 сек между шагами\n"
                "• [bold #00ff9d]/replay stop[/bold #00ff9d] - Остановить текущее воспроизведение\n\n"
                f"[bold {z}]Возможности:[/bold {z}]\n"
                "• Показывает промпты пользователя, панели ассистента и выводы инструментов\n"
                "• Пошаговое воспроизведение в реальном времени\n"
                "• Запись сессии отключена во время воспроизведения",
                title=_quick_guide_subpanel_title("Команды воспроизведения"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_continue(self, _: Optional[List[str]] = None) -> bool:
        """Show help for continuation mode."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Режим продолжения: позволяет агенту продолжать работу пошагово, пока вы не отключите его."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/continue[/bold #00ff9d] - Включить и продолжить текущую задачу\n"
                "• [bold #00ff9d]/continue on[/bold #00ff9d] - Включить режим продолжения\n"
                "• [bold #00ff9d]/continue off[/bold #00ff9d] - Отключить режим продолжения\n"
                "• [bold #00ff9d]/continue status[/bold #00ff9d] - Проверить текущий статус режима\n\n"
                f"[bold {z}]Как это работает:[/bold {z}]\n"
                "• При включении агент автоматически продолжает\n"
                "  работу над текущей задачей после каждого ответа\n"
                "• Полезно для длительных многоэтапных задач\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/continue[/bold #00ff9d] - Начать продолжение\n"
                "• [bold #00ff9d]/continue off[/bold #00ff9d] - Остановить автопродолжение",
                title=_quick_guide_subpanel_title("Команды продолжения"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_temperature(self, _: Optional[List[str]] = None) -> bool:
        """Show help for ``/temperature`` (matches command: no subcommands, optional value)."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Температура сэмплирования (0.0–2.0). Команда без аргументов показывает текущее значение; "
                    "с числом устанавливает [bold]CAI_TEMPERATURE[/bold] и model_settings "
                    "активного агента REPL для следующего хода."
                )
                + f"[bold {z}]Синтаксис[/bold {z}]\n"
                f"• [bold {z}]/temperature[/bold {z}] [dim]— показать текущее[/dim]\n"
                f"• [bold {z}]/temperature <value>[/bold {z}] [dim]— установить дробное число от 0.0 до 2.0[/dim]\n\n"
                f"[dim]Переменная: CAI_TEMPERATURE. Некоторые модели могут игнорировать или ограничивать параметр.[/dim]\n\n"
                "[dim]Алиас: /temp[/dim]",
                title=_quick_guide_subpanel_title("Температура"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_topp(self, _: Optional[List[str]] = None) -> bool:
        """Show help for ``/topp`` (matches command: no subcommands, optional value)."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Nucleus-сэмплирование top_p (0.0–1.0). Команда без аргументов показывает текущее значение; "
                    "с числом устанавливает [bold]CAI_TOP_P[/bold] и model_settings "
                    "активного агента REPL для следующего хода."
                )
                + f"[bold {z}]Синтаксис[/bold {z}]\n"
                f"• [bold {z}]/topp[/bold {z}] [dim]— показать текущее[/dim]\n"
                f"• [bold {z}]/topp <value>[/bold {z}] [dim]— установить дробное число от 0.0 до 1.0[/dim]\n\n"
                f"[bold {z}]Справка по значениям:[/bold {z}]\n"
                "• [bold #00ff9d]0.1[/bold #00ff9d] - Очень узкий (топ 10% вероятностной массы)\n"
                "• [bold #00ff9d]0.5[/bold #00ff9d] - Умеренный (топ 50%)\n"
                "• [bold #00ff9d]1.0[/bold #00ff9d] - По умолчанию (учитывать все токены)\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/topp 0.5[/bold #00ff9d] - Более сфокусированное сэмплирование\n"
                "• [bold #00ff9d]/topp 1.0[/bold #00ff9d] - Поведение по умолчанию\n\n"
                f"[dim]Переменная: CAI_TOP_P. Некоторые модели могут игнорировать или ограничивать параметр.[/dim]",
                title=_quick_guide_subpanel_title("Top-P"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_settings(self, _: Optional[List[str]] = None) -> bool:
        """Show help for interactive settings."""
        z = _CAI_GREEN
        subs = settings_help_panel_subcommand_bullets()
        console.print(
            Panel(
                _h_panel_desc(
                    "Настройки: редактирование переменных .env, FAQ, проверки API, язык и Ollama."
                )
                + f"[bold {z}]Команды:[/bold {z}]\n"
                "• [bold #00ff9d]/settings[/bold #00ff9d] - Интерактивное меню\n"
                f"{subs}\n\n"
                "[dim]Алиас: /set[/dim]",
                title=_quick_guide_subpanel_title("Настройки"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_auth(self, _: Optional[List[str]] = None) -> bool:
        """Show help for API authentication."""
        console.print(
            Panel(
                auth_help_panel_markup(),
                title=_quick_guide_subpanel_title("Auth Commands"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_ctr(self, _: Optional[List[str]] = None) -> bool:
        """Show help for CTR security analysis."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "CTR: теоретико-игровой анализ сессии; артефакты в папках run_* "
                    "(базовая директория или один уровень вложенности, одинаковое обнаружение для list/show/graph/use)."
                )
                + f"[bold {z}]Команды:[/bold {z}]\n"
                f"• [bold {z}]/ctr[/bold {z}] — запустить полный анализ\n"
                f"• [bold {z}]/ctr show[/bold {z}] — вывести равновесие и стратегии\n"
                f"• [bold {z}]/ctr graph[/bold {z}] — открыть изображение графа; сводка узлов/рёбер при наличии данных\n"
                f"• [bold {z}]/ctr list[/bold {z}] — список запусков (сначала новые; # соответствует [bold {z}]/ctr use <n>[/bold {z}])\n"
                f"• [bold {z}]/ctr use[/bold {z}] — [dim]индекс из списка[/dim], [dim]имя папки запуска в базе[/dim] "
                f"или [dim]абсолютный путь[/dim]\n"
                f"• [bold {z}]/ctr open[/bold {z}] — открыть папку запусков в файловом менеджере\n\n"
                f"[dim]Пример: [bold {z}]/ctr[/bold {z}] затем [bold {z}]/ctr list[/bold {z}] и [bold {z}]/ctr use 1[/bold {z}][/dim]",
                title=_quick_guide_subpanel_title("Команды CTR"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_api(self, _: Optional[List[str]] = None) -> bool:
        """Show help for /api (ALIAS_API_KEY in .env)."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "ALIAS_API_KEY для моделей Alias (CAI PRO). "
                    "Показ сначала читает .env, затем переменные окружения процесса, если не задано в файле; "
                    "маскированный вывод соответствует подсказке при запуске CLI (первые 4 … последние 4, если ключ длиннее 10 символов)."
                )
                + f"[bold {z}]Команды:[/bold {z}]\n"
                f"• [bold {z}]/api[/bold {z}] — показать маскированный ALIAS_API_KEY\n"
                f"• [bold {z}]/api show[/bold {z}] — то же, что и [bold {z}]/api[/bold {z}]\n"
                f"• [bold {z}]/api set <key>[/bold {z}] — записать [bold {z}].env[/bold {z}] и обновить "
                f"[bold {z}]os.environ[/bold {z}] для этого процесса\n"
                f"• [bold {z}]/api <key>[/bold {z}] — сокращение для [bold {z}]set[/bold {z}], если "
                f"первый токен не [bold {z}]show[/bold {z}] и не [bold {z}]set[/bold {z}]\n\n"
                f"[bold {z}]Примечания:[/bold {z}]\n"
                f"• Алиас: [bold {z}]/apikey[/bold {z}] (те же обработчики, что и [bold {z}]/api[/bold {z}])\n"
                f"• Ключи других провайдеров: [bold {z}]/env[/bold {z}], [bold {z}]/settings[/bold {z}]\n"
                f"• HTTP API-сервер (FastAPI) может использовать [bold {z}]CAI_API_KEY[/bold {z}] как запасной "
                f"корневой ключ; см. [bold {z}]docs/api.md[/bold {z}]\n\n"
                f"[dim]Пример: [bold {z}]/api show[/bold {z}] затем [bold {z}]/api set[/bold {z}] "
                f"(вставьте ключ следующим токеном)[/dim]",
                title=_quick_guide_subpanel_title("Команды API"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_metadebug(self, _: Optional[List[str]] = None) -> bool:
        """Show help for meta-agent debugging."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc("Мета-отладка: вывод состояния мета-рассуждений, маршрутизации и диагностики выбора агента.")
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/metadebug[/bold #00ff9d] - Показать отладочную информацию\n\n"
                f"[bold {z}]Что показывает:[/bold {z}]\n"
                "• Состояние рассуждений мета-агента\n"
                "• Решения о выборе агента\n"
                "• Внутренняя информация о маршрутизации\n\n"
                "[dim]Алиас: /md[/dim]",
                title=_quick_guide_subpanel_title("Команды мета-отладки"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True

    def handle_commands(self, _: Optional[List[str]] = None) -> bool:
        """List all available commands in one panel (same layout style as other /h topics)."""
        z = _CAI_GREEN
        console.print(
            Panel(
                Text.from_markup(commands_reference_panel_markup(), overflow="fold"),
                title=_quick_guide_subpanel_title("Справочник команд"),
                title_align="left",
                padding=(1, 1),
                border_style=z,
            )
        )
        return True

    def handle_merge_help(self, _: Optional[List[str]] = None) -> bool:
        """Show help for merge command."""
        z = _CAI_GREEN
        console.print(
            Panel(
                _h_panel_desc(
                    "Слияние: объединение параллельных воркеров в общие истории и выход из параллельного режима."
                )
                + f"[bold {z}]Доступные команды:[/bold {z}]\n"
                "• [bold #00ff9d]/merge <agents...> [options][/bold #00ff9d] - Объединить указанных агентов\n"
                "• [bold #00ff9d]/merge all [options][/bold #00ff9d] - Объединить все истории агентов\n\n"
                f"[bold {z}]Поведение по умолчанию:[/bold {z}]\n"
                "Без --target все исходные агенты получают полную\n"
                "объединённую историю (с автоматическим контролем дубликатов).\n"
                "После успешного слияния CAI автоматически выходит из параллельного режима,\n"
                "чтобы вы могли продолжать использовать объединённый контекст в следующих запросах.\n\n"
                f"[bold {z}]Параметры:[/bold {z}]\n"
                "• [bold #00ff9d]--strategy <type>[/bold #00ff9d] - Стратегия слияния\n"
                "  • chronological (по умолчанию) - По временной метке\n"
                "  • by-agent - По агентам\n"
                "  • interleaved - Сохранение потока разговора\n"
                "• [bold #00ff9d]--target <name>[/bold #00ff9d] - Создать нового агента с объединённой историей\n"
                "• [bold #00ff9d]--remove-sources[/bold #00ff9d] - Удалить исходных агентов после слияния\n"
                "• [bold #00ff9d]--no-worker-summary[/bold #00ff9d] - Сохранить полные транскрипты по воркерам (без ИИ-резюме)\n"
                "• [bold #00ff9d]--summarize-workers[/bold #00ff9d] - Резюмировать каждый воркер, даже короткие истории\n\n"
                "[dim]Переменная: CAI_MERGE_SUMMARIZE_PER_WORKER=1 (по умолчанию) включает резюмирование по воркерам, "
                "когда у воркера ≥ CAI_MERGE_SUMMARIZE_MIN_MESSAGES (по умолчанию 20).[/dim]\n\n"
                f"[bold {z}]Примеры:[/bold {z}]\n"
                "• [bold #00ff9d]/merge P1 P2[/bold #00ff9d]\n"
                "  → P1 получает сообщения P2, P2 получает сообщения P1\n"
                "• [bold #00ff9d]/merge P1 P2 --target combined[/bold #00ff9d]\n"
                "  → Создаёт нового агента 'combined', P1 и P2 без изменений\n"
                "• [bold #00ff9d]/merge all[/bold #00ff9d]\n"
                "  → Все агенты получают полную объединённую историю\n"
                "• [bold #00ff9d]/merge all --target unified --remove-sources[/bold #00ff9d]\n"
                "  → Создаёт агента 'unified' и удаляет всех остальных\n\n"
                f"[bold {z}]Примечания:[/bold {z}]\n"
                "• /merge = слияние контекстов + автоматический выход из параллельного режима\n"
                "• /parallel clear = выход из параллельного режима без слияния контекстов\n"
                "• Используйте ID агентов (P1, P2) или полные имена\n"
                "• Имена агентов с пробелами определяются автоматически\n"
                "• Дубликаты автоматически фильтруются\n"
                "• Это алиас для /parallel merge\n\n"
                "[dim]Алиас: /mrg[/dim]",
                title=_quick_guide_subpanel_title("Команды слияния"),
                title_align="left",
                padding=(1, 1),
                border_style=_CAI_GREEN,
            )
        )
        return True


# Register the command
register_command(HelpCommand())
