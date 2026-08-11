"""
Управление конфигурацией TUI для CAI
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class TUIConfig:
    """Управляет конфигурацией TUI, включая настройки темы"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".cai"
        self.config_file = self.config_dir / "tui_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфигурацию из файла"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_config(self) -> None:
        """Сохранить конфигурацию в файл"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def get_theme(self) -> Optional[str]:
        """Получить сохранённые настройки темы"""
        # Переменная окружения имеет приоритет
        env_theme = os.getenv("CAI_THEME")
        if env_theme:
            return env_theme
        # Иначе использовать сохранённую конфигурацию
        return self.config.get("theme")
    
    def set_theme(self, theme: str) -> None:
        """Сохранить настройки темы"""
        self.config["theme"] = theme
        self._save_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Установить значение конфигурации"""
        self.config[key] = value
        self._save_config()