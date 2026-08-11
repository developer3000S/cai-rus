"""
Слой представления TUI — компоновка макета и CSS, извлечённые из cai_terminal.py.

Часть рефакторинга MVC из оригинального монолита на 4500+ строк кода.
"""

from cai.tui.view.main_view import (
    CAI_TERMINAL_CSS,
    compose_main_layout,
    register_cai_themes,
    get_help_basic_content,
    get_help_advanced_content,
    get_help_protips_content,
    update_tab_appearance,
)

__all__ = [
    "CAI_TERMINAL_CSS",
    "compose_main_layout",
    "register_cai_themes",
    "get_help_basic_content",
    "get_help_advanced_content",
    "get_help_protips_content",
    "update_tab_appearance",
]
