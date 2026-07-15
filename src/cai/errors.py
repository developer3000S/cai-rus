"""Иерархия ошибок CAI.

Типизированные ошибки, заменяющие голые блоки except: и строковые возвраты ошибок.
Вдохновлено перечислением CodexErr из Codex с 150+ вариантами.

Создано в Day 0 как общий контракт между 3 потоками рефакторинга.
- Поток 1 (Core Engine): заполняет ошибки LLM и инструментов
- Поток 2 (Foundation): заполняет ошибки конфигурации
- Поток 3 (Interface): потребляет все типы ошибок для отображения
"""


class CAIError(Exception):
    """Базовый класс для всех ошибок CAI."""

    def __init__(self, message: str = "", details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


# --- Ошибки LLM (Поток 1) ---


class LLMError(CAIError):
    """Ошибки при общении с провайдерами LLM."""
    pass


class LLMTimeout(LLMError):
    """Вызов LLM превысил время ожидания."""
    pass


class LLMAuthError(LLMError):
    """Ошибка аутентификации/авторизации."""
    pass


class LLMRateLimited(LLMError):
    """Достигнут лимит частоты запросов, включает время повтора, если доступно."""

    def __init__(self, message: str = "", retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class LLMContextOverflow(LLMError):
    """Окно контекста превышено."""
    pass


class LLMProviderUnavailable(LLMError):
    """Конечная точка провайдера недоступна."""
    pass


class LLMEmptyAssistantError(LLMProviderUnavailable):
    """Шлюз вернул последовательные пустые ответы ассистента (без текста, без инструментов)."""

    pass


# --- Ошибки инструментов (Поток 1) ---


class ToolError(CAIError):
    """Ошибки во время выполнения инструмента."""
    pass


class ToolTimeout(ToolError):
    """Выполнение инструмента превысило время ожидания."""

    def __init__(self, message: str = "", timeout_seconds: int = 0):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class ToolNotFound(ToolError):
    """Запрошенный инструмент не найден в реестре."""
    pass


class ToolExecutionFailed(ToolError):
    """Процесс инструмента завершился с ошибкой."""

    def __init__(self, message: str = "", exit_code: int = -1):
        super().__init__(message)
        self.exit_code = exit_code


# --- Ошибки конфигурации (Поток 2) ---


class ConfigError(CAIError):
    """Ошибки загрузки/валидации конфигурации."""
    pass


class ConfigValidationError(ConfigError):
    """Значения конфигурации выходят за ожидаемый диапазон."""
    pass


class ConfigMissingError(ConfigError):
    """Не предоставлена обязательная конфигурация."""
    pass


# --- Ошибки сессии (Поток 3) ---


class SessionError(CAIError):
    """Ошибки сохранения сессии."""
    pass


class SessionCorrupted(SessionError):
    """Файл сессии нечитаем или поврежден."""
    pass
