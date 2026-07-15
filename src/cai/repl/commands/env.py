"""
Команда окружения для CAI REPL.
Этот модуль предоставляет команды для отображения и настройки переменных окружения.
"""

from typing import List, Optional

from cai.repl.commands.base import Command, register_command
from cai.repl.commands.env_catalog import (
    handle_env_catalog_default,
    handle_env_catalog_get,
    handle_env_catalog_list,
    handle_env_catalog_set,
    print_bare_env_session_view,
)


class EnvCommand(Command):
    """Команда для отображения и настройки переменных окружения (сессия REPL)."""

    def __init__(self):
        """Initialize the env command."""
        super().__init__(
            name="/env",
            description="Отображение и настройка переменных окружения",
            aliases=["/e"],
        )
        self.add_subcommand(
            "list",
            "Показать все переменные каталога и их значения",
            handle_env_catalog_list,
        )
        self.add_subcommand(
            "get",
            "Получить переменную каталога по номеру или имени",
            handle_env_catalog_get,
        )
        self.add_subcommand(
            "set",
            "Установить переменную каталога: /env set <#|NAME> <value...>",
            handle_env_catalog_set,
        )
        self.add_subcommand(
            "default",
            "Восстановить все переменные каталога до значений по умолчанию",
            handle_env_catalog_default,
        )

    def handle(self, args: Optional[List[str]] = None) -> bool:
        """Route: no args -> session CAI_/CTF_ in os.environ; else subcommands only."""
        if not args:
            return print_bare_env_session_view()

        first_arg = args[0]
        if first_arg in self.subcommands:
            handler = self.subcommands[first_arg]["handler"]
            return handler(args[1:] if len(args) > 1 else None)

        return self.handle_unknown_subcommand(first_arg)

    def handle_no_args(self) -> bool:
        """Satisfy base contract if invoked without args via default handler."""
        return print_bare_env_session_view()


register_command(EnvCommand())
