"""Пакет chatcompletions — рефакторинг из openai_chatcompletions.py.

Реэкспортирует все публичные имена, чтобы существующие импорты вида
``from cai.sdk.agents.models.openai_chatcompletions import OpenAIChatCompletionsModel``
продолжали работать через шим совместимости по старому пути.
"""

# Основной класс модели (пока остаётся в исходном файле на этом этапе)
# Реэкспортируем утилиты подмодулей для прямого использования.
from .token_counter import count_tokens_with_tiktoken, _check_reasoning_compatibility
from .usage_tracker import InputTokensDetails, CustomResponseUsage
from .cache_manager import (
    normalize_and_apply_cache,
    normalize_messages_for_cache,
    apply_cache_control,
    has_cache_control,
    debug_cache_messages,
)
from .stream_handler import StreamingState
from .message_builder import Converter, ToolConverter
from .auto_compactor import auto_compact_if_needed, get_model_max_tokens
from .httpx_client import direct_httpx_completion
from .litellm_adapter import fetch_response_litellm_openai, fetch_response_litellm_ollama

# model.py реэкспортирует вспомогательные функции модульного уровня; основной класс
# будет импортироваться из исходного файла до завершения полной миграции.
from .model import (
    ACTIVE_MODEL_INSTANCES,
    PERSISTENT_MESSAGE_HISTORIES,
    set_current_active_model,
    get_current_active_model,
    get_agent_message_history,
    get_all_agent_histories,
    clear_agent_history,
    clear_all_histories,
    _StreamingState,
)

__all__ = [
    # Подсчёт токенов
    "count_tokens_with_tiktoken",
    "_check_reasoning_compatibility",
    # Отслеживание использования
    "InputTokensDetails",
    "CustomResponseUsage",
    # Управление кэшем
    "normalize_and_apply_cache",
    "normalize_messages_for_cache",
    "apply_cache_control",
    "has_cache_control",
    "debug_cache_messages",
    # Потоковая передача
    "StreamingState",
    "_StreamingState",
    # Построение сообщений
    "Converter",
    "ToolConverter",
    # Вспомогательные функции модульного уровня
    "ACTIVE_MODEL_INSTANCES",
    "PERSISTENT_MESSAGE_HISTORIES",
    "set_current_active_model",
    "get_current_active_model",
    "get_agent_message_history",
    "get_all_agent_histories",
    "clear_agent_history",
    "clear_all_histories",
    # Авто-компактификация
    "auto_compact_if_needed",
    "get_model_max_tokens",
    # Прямой httpx-клиент (обход LiteLLM)
    "direct_httpx_completion",
    # Адаптеры LiteLLM
    "fetch_response_litellm_openai",
    "fetch_response_litellm_ollama",
]
