"""
Отслеживание идентификатора терминала для TUI с поддержкой асинхронного контекста
"""

import contextvars
from typing import Optional

# Контекстная переменная для идентификатора терминала, распространяемая через асинхронные вызовы
_terminal_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'terminal_id',
    default=None
)


def set_current_terminal_id_async(terminal_id: str) -> contextvars.Token:
    """Установить идентификатор текущего терминала для данного асинхронного контекста"""
    return _terminal_id_context.set(terminal_id)


def get_current_terminal_id_async() -> Optional[str]:
    """Получить идентификатор текущего терминала для данного асинхронного контекста"""
    return _terminal_id_context.get()


def reset_current_terminal_id_async(token: contextvars.Token) -> None:
    """Сбросить контекст идентификатора терминала к предыдущему значению"""
    _terminal_id_context.reset(token)


def clear_current_terminal_id_async() -> None:
    """Очистить идентификатор текущего терминала для данного асинхронного контекста"""
    _terminal_id_context.set(None)