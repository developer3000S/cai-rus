"""
Отслеживание идентификатора терминала для TUI (обёртки совместимости).

Этот модуль предоставляет стабильный интерфейс для получения/установки текущего
контекста маршрутизации терминала. Исторически некоторые точки вызова обращались
напрямую к объекту ``_thread_local`` уровня модуля. Слой маршрутизации с тех пор
перешёл на ContextVars с гибридной стратегией, поэтому здесь предоставляется
обратно-совместимый прокси, зеркалирующий старые атрибуты и делегирующий к
единственному источнику истины в ``routing.output_router``.
"""

from typing import Optional

from cai.tui.routing.output_router import (
    set_terminal_context as _set_ctx,
    get_current_terminal_id as _get_tid,
    clear_current_terminal_context as _clear_ctx,
    current_terminal_id as _ctx_tid,
    current_terminal_number as _ctx_tnum,
)


def set_current_terminal_id(terminal_id: str) -> None:
    """Установить идентификатор текущего терминала, оставив номер без изменений при его наличии."""
    _set_ctx(terminal_id)


def get_current_terminal_id() -> Optional[str]:
    """Вернуть идентификатор текущего терминала, если установлен, иначе None."""
    return _get_tid()


def get_current_terminal_number() -> Optional[int]:
    """Вернуть номер текущего терминала, если установлен, иначе None."""
    try:
        return _ctx_tnum.get()
    except Exception:
        return None


def clear_current_terminal_id() -> None:
    """Очистить текущий контекст терминала из контекстных переменных."""
    _clear_ctx()


class _CompatThreadLocalProxy:
    """Прокси совместимости, предоставляющий ``terminal_id`` и ``terminal_number``.

    Старый код обращался к ``terminal_tracking._thread_local.terminal_number`` для
    определения активного терминала. Теперь это хранится в ContextVars; данный
    прокси перенаправляет чтение атрибутов к этим ContextVars, чтобы устаревший
    код продолжал работать без изменений.
    """

    def __getattr__(self, name):
        if name == "terminal_id":
            value = _ctx_tid.get()
            if value is None:
                raise AttributeError("terminal_id is not set")
            return value
        if name == "terminal_number":
            value = _ctx_tnum.get()
            if value is None:
                raise AttributeError("terminal_number is not set")
            return value
        raise AttributeError(f"Unknown attribute '{name}' on _CompatThreadLocalProxy")


# Атрибуты обратной совместимости: со знаком подчёркивания и без
_thread_local = _CompatThreadLocalProxy()
thread_local = _thread_local
