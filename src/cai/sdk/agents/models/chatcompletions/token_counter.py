"""Утилиты подсчёта токенов с использованием tiktoken.

Обеспечивает согласованный подсчёт токенов для сообщений и текста,
а также проверку совместимости с режимом рассуждений для моделей Claude.
"""

from __future__ import annotations

import tiktoken


def _check_reasoning_compatibility(messages):
    """
    Проверить совместимость истории сообщений с режимом рассуждений Claude.

    Согласно документации Claude 4, при включённом режиме рассуждений последнее
    сообщение ассистента должно начинаться с блока «thinking». Если в истории
    есть сообщения ассистента с обычным текстом, режим рассуждений следует отключить.

    Args:
        messages: Список словарей-сообщений

    Returns:
        bool: True, если совместимо с режимом рассуждений, иначе False
    """
    if not messages:
        return True  # Пустой список сообщений совместим

    # Найти последнее сообщение ассистента
    last_assistant_msg = None
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            last_assistant_msg = msg
            break

    if not last_assistant_msg:
        return True  # Нет сообщений ассистента — совместимо

    # Проверить, содержит ли последнее сообщение ассистента обычный текст
    content = last_assistant_msg.get("content")
    if content:
        # Строка с текстом — не совместимо
        if isinstance(content, str) and content.strip():
            return False
        # Список блоков — проверить наличие текстовых блоков
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        return False

    # Проверить наличие tool_calls (они совместимы с режимом рассуждений)
    if last_assistant_msg.get("tool_calls"):
        return True

    # Нет контента или только блоки «thinking» — совместимо
    return True


def count_tokens_with_tiktoken(text_or_messages):
    """
    Подсчитать токены с помощью библиотеки tiktoken.
    Работает как со строками, так и со списками сообщений.
    Возвращает кортеж (input_tokens, reasoning_tokens).
    """
    if not text_or_messages:
        return 0, 0

    try:
        # Попытка использовать кодировку cl100k_base (используется GPT-4 и GPT-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Резервный вариант — кодировка GPT-2, если cl100k недоступна
        try:
            encoding = tiktoken.get_encoding("gpt2")
        except Exception:
            # Если tiktoken недоступен — оценка по числу символов
            if isinstance(text_or_messages, str):
                return len(text_or_messages) // 4, 0
            elif isinstance(text_or_messages, list):
                total_len = 0
                for msg in text_or_messages:
                    if isinstance(msg, dict) and "content" in msg:
                        if isinstance(msg["content"], str):
                            total_len += len(msg["content"])
                return total_len // 4, 0
            else:
                return 0, 0

    # Обработка различных типов входных данных
    if isinstance(text_or_messages, str):
        token_count = len(encoding.encode(text_or_messages))
        return token_count, 0
    elif isinstance(text_or_messages, list):
        total_tokens = 0
        reasoning_tokens = 0

        # Добавить токены на накладные расходы формата сообщений (ChatML)
        # Каждое сообщение имеет базовые накладные расходы (~4 токена)
        total_tokens += len(text_or_messages) * 4

        for msg in text_or_messages:
            if isinstance(msg, dict):
                # Добавить токены для поля role
                if "role" in msg:
                    total_tokens += len(encoding.encode(msg["role"]))

                # Подсчитать токены контента
                if "content" in msg and msg["content"]:
                    if isinstance(msg["content"], str):
                        content_tokens = len(encoding.encode(msg["content"]))
                        total_tokens += content_tokens

                        # Токены сообщений ассистента учитываются как токены рассуждений
                        if msg.get("role") == "assistant":
                            reasoning_tokens += content_tokens
                    elif isinstance(msg["content"], list):
                        for content_part in msg["content"]:
                            if isinstance(content_part, dict) and "text" in content_part:
                                part_tokens = len(encoding.encode(content_part["text"]))
                                total_tokens += part_tokens
                                if msg.get("role") == "assistant":
                                    reasoning_tokens += part_tokens

        return total_tokens, reasoning_tokens
    else:
        return 0, 0
