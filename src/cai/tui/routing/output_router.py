"""
Маршрутизатор вывода для направления контента в правильный терминал.
Следует паттерну Strategy для различных стратегий маршрутизации.
"""

import threading
import sys
from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Any, Dict, Optional, Tuple

# Контекстные переменные для маршрутизации терминала
current_terminal_id: ContextVar[Optional[str]] = ContextVar('current_terminal_id', default=None)
current_terminal_number: ContextVar[Optional[int]] = ContextVar('current_terminal_number', default=None)


class IRoutingStrategy(ABC):
    """Интерфейс для стратегий маршрутизации"""

    @abstractmethod
    def get_terminal_id(self, context: Dict[str, Any]) -> Optional[str]:
        """Получить ID терминала на основе контекста"""
        pass

    @abstractmethod
    def set_terminal_context(self, terminal_id: str, terminal_number: int) -> Any:
        """Установить контекст терминала и вернуть токен для очистки"""
        pass


class ContextVarRoutingStrategy(IRoutingStrategy):
    """Маршрутизация на основе контекстных переменных (лучший вариант для async)"""

    def get_terminal_id(self, context: Dict[str, Any]) -> Optional[str]:
        """Получить ID терминала из контекстных переменных"""
        # Сначала проверяем контекстные переменные
        terminal_id = current_terminal_id.get()
        if terminal_id:
            return terminal_id

        # Резервный вариант — словарь контекста
        return context.get('terminal_id')

    def set_terminal_context(self, terminal_id: str, terminal_number: int) -> Any:
        """Установить контекстные переменные"""
        tokens = []
        tokens.append(current_terminal_id.set(terminal_id))
        tokens.append(current_terminal_number.set(terminal_number))
        return tokens


class ThreadLocalRoutingStrategy(IRoutingStrategy):
    """Маршрутизация на основе локальных данных потока (для синхронного кода)"""

    def __init__(self):
        self._thread_local = threading.local()

    def get_terminal_id(self, context: Dict[str, Any]) -> Optional[str]:
        """Получить ID терминала из локальных данных потока"""
        # Проверяем локальные данные потока
        if hasattr(self._thread_local, 'terminal_id'):
            return self._thread_local.terminal_id

        # Резервный вариант — контекст
        return context.get('terminal_id')

    def set_terminal_context(self, terminal_id: str, terminal_number: int) -> Any:
        """Установить контекст в локальных данных потока"""
        self._thread_local.terminal_id = terminal_id
        self._thread_local.terminal_number = terminal_number
        return None  # Очистка для локальных данных потока не нужна


class HybridRoutingStrategy(IRoutingStrategy):
    """Гибридная стратегия, работающая как с async, так и с sync кодом"""

    def __init__(self):
        self._context_strategy = ContextVarRoutingStrategy()
        self._thread_strategy = ThreadLocalRoutingStrategy()

    def get_terminal_id(self, context: Dict[str, Any]) -> Optional[str]:
        """Попробовать обе стратегии"""
        # Сначала пробуем контекстные переменные (async)
        terminal_id = self._context_strategy.get_terminal_id(context)
        if terminal_id:
            return terminal_id

        # Пробуем локальные данные потока (sync)
        terminal_id = self._thread_strategy.get_terminal_id(context)
        if terminal_id:
            return terminal_id

        # Финальный резервный вариант
        return context.get('terminal_id')

    def set_terminal_context(self, terminal_id: str, terminal_number: int) -> Any:
        """Установить оба контекста"""
        tokens = []

        # Устанавливаем контекстные переменные
        ctx_tokens = self._context_strategy.set_terminal_context(terminal_id, terminal_number)
        if ctx_tokens:
            tokens.extend(ctx_tokens)

        # Устанавливаем локальные данные потока
        self._thread_strategy.set_terminal_context(terminal_id, terminal_number)

        return tokens


class OutputRouter:
    """Центральный маршрутизатор вывода терминала"""

    _instance = None
    _strategy: IRoutingStrategy = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._strategy = HybridRoutingStrategy()
        return cls._instance

    def set_strategy(self, strategy: IRoutingStrategy) -> None:
        """Установить стратегию маршрутизации"""
        self._strategy = strategy

    def get_terminal_id(self, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Получить текущий ID терминала"""
        context = context or {}
        return self._strategy.get_terminal_id(context)

    def set_terminal_context(self, terminal_id: str, terminal_number: int = 1) -> Any:
        """Установить контекст терминала для текущего выполнения"""
        return self._strategy.set_terminal_context(terminal_id, terminal_number)

    def route_to_terminal(self, terminal_id: str, terminal_number: int = 1):
        """Контекстный менеджер для маршрутизации в конкретный терминал"""
        return TerminalRoutingContext(terminal_id, terminal_number, self._strategy)

    # Вспомогательные методы
    def get_current_context(self) -> Tuple[Optional[str], Optional[int]]:
        """Вернуть текущие (terminal_id, terminal_number) из контекстных переменных."""
        return current_terminal_id.get(), current_terminal_number.get()

    def clear_current_context(self) -> None:
        """Очистить контекстные переменные для id/номера терминала."""
        try:
            current_terminal_id.set(None)
            current_terminal_number.set(None)
        except Exception:
            pass

    def set_terminal_id_only(self, terminal_id: str) -> Any:
        """Установить только id терминала в контекстных переменных (номер не меняется)."""
        return current_terminal_id.set(terminal_id)


class TerminalRoutingContext:
    """Контекстный менеджер для маршрутизации терминала"""

    def __init__(self, terminal_id: str, terminal_number: int, strategy: IRoutingStrategy):
        self.terminal_id = terminal_id
        self.terminal_number = terminal_number
        self.strategy = strategy
        self.tokens = None

    def __enter__(self):
        """Установить контекст терминала"""
        self.tokens = self.strategy.set_terminal_context(self.terminal_id, self.terminal_number)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Очистить контекст"""
        # Контекстные переменные очищаются автоматически при выходе токенов из области видимости
        pass


# Глобальный экземпляр маршрутизатора
output_router = OutputRouter()

# Глобальный реестр выводов терминалов
_terminal_outputs = {}
_registry_lock = threading.RLock()


def register_terminal_output(terminal_id: str, output_widget: Any) -> None:
    """Зарегистрировать виджет вывода терминала"""
    with _registry_lock:
        _terminal_outputs[terminal_id] = output_widget


def get_terminal_output(terminal_id: str) -> Any:
    """Получить виджет вывода терминала"""
    with _registry_lock:
        return _terminal_outputs.get(terminal_id)


class EnhancedTerminalRoutingContext:
    """Расширенный контекст маршрутизации с перенаправлением stdout/stderr"""
    
    def __init__(self, terminal_id: str, output_widget: Any, terminal_number: int = 1):
        self.terminal_id = terminal_id
        self.output_widget = output_widget
        self.terminal_number = terminal_number
        self.old_stdout = None
        self.old_stderr = None
        self.old_print = None
        
    def __enter__(self):
        """Настроить маршрутизацию"""
        import sys
        
        # Сохраняем оригиналы
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        self.old_print = __builtins__.get('print', print)
        
        # Создаём обёртку для stdout/stderr
        class TerminalWriter:
            def __init__(self, widget, is_stderr=False):
                self.widget = widget
                self.is_stderr = is_stderr
                
            def write(self, text):
                if text and self.widget:
                    try:
                        if self.is_stderr:
                            self.widget.write(f"[red]{text}[/red]")
                        else:
                            self.widget.write(text)
                    except Exception:
                        # Резервный вариант
                        pass
                return len(text) if text else 0
                
            def flush(self):
                pass
                
            def isatty(self):
                return False
                
        # Заменяем stdout/stderr
        sys.stdout = TerminalWriter(self.output_widget)
        sys.stderr = TerminalWriter(self.output_widget, is_stderr=True)
        
        # Заменяем print
        def terminal_print(*args, **kwargs):
            text = ' '.join(str(arg) for arg in args)
            if text and self.output_widget:
                self.output_widget.write(text)
                
        __builtins__['print'] = terminal_print
        
        # Также устанавливаем контекст для другой маршрутизации
        output_router.set_terminal_context(self.terminal_id, self.terminal_number)
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Восстановить маршрутизацию"""
        import sys
        
        # Восстанавливаем оригиналы
        if self.old_stdout:
            sys.stdout = self.old_stdout
        if self.old_stderr:
            sys.stderr = self.old_stderr
        if self.old_print:
            __builtins__['print'] = self.old_print


# Вспомогательные функции
def get_current_terminal_id() -> Optional[str]:
    """Получить текущий ID терминала"""
    return output_router.get_terminal_id()

def get_current_terminal_context() -> Tuple[Optional[str], Optional[int]]:
    """Получить текущие (terminal_id, terminal_number) из контекста."""
    return output_router.get_current_context()


def set_terminal_context(terminal_id: str, terminal_number: int = 1) -> Any:
    """Установить контекст терминала"""
    return output_router.set_terminal_context(terminal_id, terminal_number)

def clear_current_terminal_context() -> None:
    """Очистить контекст терминала из контекстных переменных."""
    output_router.clear_current_context()

def set_terminal_id_only(terminal_id: str) -> Any:
    """Установить только id терминала в контекстных переменных (номер сохраняется)."""
    return output_router.set_terminal_id_only(terminal_id)


def route_to_terminal(terminal_id: str, terminal_output=None, terminal_number: int = 1):
    """Контекстный менеджер для маршрутизации вывода в конкретный терминал
    
    Args:
        terminal_id: ID терминала для маршрутизации
        terminal_output: Необязательный виджет вывода (для прямой маршрутизации)
        terminal_number: Номер терминала (по умолчанию 1)
    """
    if terminal_output:
        # Используем расширенную маршрутизацию с виджетом вывода
        return EnhancedTerminalRoutingContext(terminal_id, terminal_output, terminal_number)
    else:
        # Используем стандартную маршрутизацию
        return output_router.route_to_terminal(terminal_id, terminal_number)
