"""
Категоризированный индекс slash-команд для справки REPL (соответствует публичному справочнику команд).

Строки разрешаются относительно ``COMMANDS`` после ленивой загрузки, чтобы UI оставался
синхронизированным с ``register_command`` без ручного поддержания каждой команды в нескольких файлах.
"""

from __future__ import annotations

# (заголовок раздела, первичные ключи, хранящиеся в ``COMMANDS``)
CLI_COMMAND_CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Agent Management", ("/agent", "/queue")),
    ("Model Management", ("/model", "/temperature", "/topp")),
    (
        "Memory & History",
        ("/memory", "/history", "/compact", "/flush", "/load", "/save", "/merge"),
    ),
    ("Environment & Configuration", ("/env", "/workspace", "/virtualization", "/config")),
    ("Tools & Integration", ("/mcp", "/shell")),
    ("Parallel Execution", ("/parallel",)),
    (
        "Session, cost & utilities",
        (
            "/resume",
            "/sessions",
            "continue",
            "/cost",
            "/context",
            "/replay",
            "/quickstart",
            "/graph",
            "/help",
            "/settings",
            "/metadebug",
            "/ctr",
            "/api",
            "/auth",
            "/exit",
        ),
    ),
)


def _display_cmd_name(primary: str) -> str:
    # Голый ``?`` — это команда быстрых подсказок; ``/?`` является псевдонимом ``/help``, а не тем же токеном.
    if primary == "?":
        return "?"
    return primary if primary.startswith("/") else f"/{primary}"


def _aliases_for_primary(primary: str, alias_map: dict[str, str]) -> str:
    als = sorted(a for a, p in alias_map.items() if p == primary and a != primary)
    return ", ".join(als)


def _collect_rows() -> tuple[
    list[tuple[str, list[tuple[str, str, str]]]], list[tuple[str, str, str]]
]:
    from cai.repl.commands import _ensure_all_commands_loaded
    from cai.repl.commands.base import COMMAND_ALIASES, COMMANDS

    _ensure_all_commands_loaded()

    assigned: set[str] = set()
    blocks: list[tuple[str, list[tuple[str, str, str]]]] = []

    for title, keys in CLI_COMMAND_CATEGORIES:
        rows: list[tuple[str, str, str]] = []
        seen_primary: set[str] = set()
        for key in keys:
            cmd = COMMANDS.get(key)
            if cmd is None:
                continue
            primary = cmd.name
            if primary in seen_primary:
                continue
            seen_primary.add(primary)
            if primary in assigned:
                continue
            rows.append(
                (
                    _display_cmd_name(primary),
                    _aliases_for_primary(primary, COMMAND_ALIASES),
                    cmd.description,
                )
            )
            assigned.add(primary)
        if rows:
            blocks.append((title, rows))

    other: list[tuple[str, str, str]] = []
    for primary in sorted(COMMANDS.keys(), key=lambda x: _display_cmd_name(x).lower()):
        if primary in assigned:
            continue
        cmd = COMMANDS[primary]
        other.append(
            (
                _display_cmd_name(primary),
                _aliases_for_primary(primary, COMMAND_ALIASES),
                cmd.description,
            )
        )
    if other:
        blocks.append(("Other", other))

    flat: list[tuple[str, str, str]] = []
    for _, rs in blocks:
        flat.extend(rs)
    return blocks, flat


def categorized_command_tables() -> list[tuple[str, list[tuple[str, str, str]]]]:
    """Для ``/help commands`` — (категория, [(команда, псевдонимы, описание), ...])."""
    blocks, _ = _collect_rows()
    return blocks


def help_topic_rows_by_category() -> list[tuple[str, list[tuple[str, str]]]]:
    """Для ``/help topics`` — slash-команды по категориям ``[(категория, [(команда, описание), ...]), ...]``."""
    blocks, _ = _collect_rows()
    return [(title, [(a, c) for a, _, c in rows]) for title, rows in blocks]
