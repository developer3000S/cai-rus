"""
Управление контекстом выполнения для TUI-терминалов

Тонкие обёртки, делегирующие вызовы в routing.output_router для обеспечения
единственного источника истины о контексте терминала.
"""

from typing import Optional
from cai.tui.routing.output_router import (
    set_terminal_context as _set_ctx,
    get_current_terminal_id as _get_tid,
    clear_current_terminal_context as _clear_ctx,
)


def set_terminal_id_context(terminal_id: str):
    """Устанавливает идентификатор терминала через контекст маршрутизации. Возвращает None (совместимость)."""
    _set_ctx(terminal_id)
    return None


def get_terminal_id_context() -> Optional[str]:
    """Получает идентификатор терминала из контекста маршрутизации."""
    return _get_tid()


def reset_terminal_id_context(token) -> None:  # token ignored for compat
    """Сбрасывает контекст терминала (совместимая сигнатура)."""
    _clear_ctx()
