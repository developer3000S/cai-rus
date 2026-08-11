"""
Реестр виджетов терминала — хранит ссылки на виджеты UniversalTerminal для обновления панели действий
"""

import threading
from typing import Optional, Dict, Any

import os
_CAI_DEBUG_DIR = os.path.join(os.path.expanduser("~"), ".cai", "debug")


class TerminalWidgetRegistry:
    """Реестр виджетов UniversalTerminal"""
    
    def __init__(self):
        self._widgets: Dict[str, Any] = {}  # terminal_id -> виджет UniversalTerminal
        self._lock = threading.Lock()
    
    def register(self, terminal_id: str, widget: Any) -> None:
        """Зарегистрировать виджет UniversalTerminal"""
        with self._lock:
            # Отладочное логирование
            try:
                with open(f"{_CAI_DEBUG_DIR}/cai_widget_registry.log", "a") as f:
                    import datetime
                    f.write(f"\n[{datetime.datetime.now().isoformat()}] Registering widget:\n")
                    f.write(f"  terminal_id: {terminal_id}\n")
                    f.write(f"  widget type: {type(widget).__name__}\n")
                    if hasattr(widget, 'terminal_number'):
                        f.write(f"  terminal_number: {widget.terminal_number}\n")
                    if hasattr(widget, 'state') and hasattr(widget.state, 'agent_id'):
                        f.write(f"  agent_id: {widget.state.agent_id}\n")
            except:
                pass
            
            self._widgets[terminal_id] = widget
            # Также регистрировать предсказуемые ID для параллельного режима
            if hasattr(widget, 'terminal_number'):
                predictable_id = f"terminal-{widget.terminal_number}"
                self._widgets[predictable_id] = widget
    
    def get(self, terminal_id: str) -> Optional[Any]:
        """Получить виджет UniversalTerminal по идентификатору"""
        with self._lock:
            widget = self._widgets.get(terminal_id)
            # Отладочное логирование
            try:
                with open(f"{_CAI_DEBUG_DIR}/cai_widget_registry.log", "a") as f:
                    import datetime
                    f.write(f"\n[{datetime.datetime.now().isoformat()}] Looking up widget by terminal_id:\n")
                    f.write(f"  terminal_id: {terminal_id}\n")
                    f.write(f"  found: {widget is not None}\n")
                    f.write(f"  registered IDs: {list(self._widgets.keys())}\n")
            except:
                pass
            return widget
    
    def get_by_agent_id(self, agent_id: str) -> Optional[Any]:
        """Получить виджет UniversalTerminal по идентификатору агента"""
        with self._lock:
            # Попытка найти по agent_id в состоянии виджета
            for widget in self._widgets.values():
                if hasattr(widget, 'state') and hasattr(widget.state, 'agent_id'):
                    if widget.state.agent_id == agent_id:
                        return widget
            
            # Запасной вариант: попытка извлечь номер терминала из agent_id
            if agent_id and agent_id.startswith("P") and agent_id[1:].isdigit():
                terminal_number = int(agent_id[1:])
                predictable_id = f"terminal-{terminal_number}"
                return self._widgets.get(predictable_id)
        
        return None
    
    def unregister(self, terminal_id: str) -> None:
        """Удалить регистрацию виджета терминала"""
        with self._lock:
            widget = self._widgets.pop(terminal_id, None)
            # Также удалить предсказуемый ID
            if widget and hasattr(widget, 'terminal_number'):
                predictable_id = f"terminal-{widget.terminal_number}"
                self._widgets.pop(predictable_id, None)
    
    def clear(self) -> None:
        """Очистить все регистрации"""
        with self._lock:
            self._widgets.clear()


# Глобальный экземпляр реестра
TERMINAL_WIDGET_REGISTRY = TerminalWidgetRegistry()


def register_terminal_widget(terminal_id: str, widget: Any) -> None:
    """Зарегистрировать виджет UniversalTerminal"""
    TERMINAL_WIDGET_REGISTRY.register(terminal_id, widget)


def get_terminal_widget(terminal_id: str) -> Optional[Any]:
    """Получить виджет UniversalTerminal по идентификатору"""
    return TERMINAL_WIDGET_REGISTRY.get(terminal_id)


def get_terminal_widget_by_agent_id(agent_id: str) -> Optional[Any]:
    """Получить виджет UniversalTerminal по идентификатору агента"""
    return TERMINAL_WIDGET_REGISTRY.get_by_agent_id(agent_id)