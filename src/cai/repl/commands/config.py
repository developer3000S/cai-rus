"""Устаревшие команды REPL ``/config``, ``/cfg`` — только уведомление об устаревании."""

from __future__ import annotations

from typing import Optional

from rich.console import Console  # pylint: disable=import-error
from rich.panel import Panel  # pylint: disable=import-error

from cai.repl.commands.base import Command, register_command
from cai.repl.ui.banner import _CAI_GREEN, _quick_guide_subpanel_title

console = Console()


def print_config_deprecated_message(out: Optional[Console] = None) -> None:
    """Single panel redirecting users to ``/env`` (also used by ``/help config``).

    ``out`` defaults to this module's console so ``/config`` and tests that patch
    ``help.console`` can route output consistently.
    """
    target = out if out is not None else console
    body = (
        "[bold]/config[/bold] устарел. Используйте [bold #00ff9d]/env[/bold #00ff9d] вместо него:\n\n"
        "• [bold #00ff9d]/env[/bold #00ff9d] — ключи [dim]CAI_[/dim] / [dim]CTF_[/dim] в текущем процессе\n"
        "• [bold #00ff9d]/env list[/bold #00ff9d] — полный каталог\n"
        "• [bold #00ff9d]/env get <n|NAME>[/bold #00ff9d] / "
        "[bold #00ff9d]/env set <n|NAME> <value...>[/bold #00ff9d]\n"
        "• [bold #00ff9d]/env default[/bold #00ff9d] — восстановить все значения по умолчанию"
    )
    target.print(
        Panel(
            body,
            title=_quick_guide_subpanel_title("Deprecated command"),
            title_align="left",
            padding=(1, 1),
            border_style=_CAI_GREEN,
        )
    )


class ConfigCommand(Command):
    """Stub: print deprecation only."""

    def __init__(self):
        super().__init__(
            name="/config",
            description="Устарело: используйте /env для переменных окружения",
            aliases=["/cfg"],
        )

    def handle(self, args=None):  # pylint: disable=unused-argument
        print_config_deprecated_message()
        return True


register_command(ConfigCommand())
