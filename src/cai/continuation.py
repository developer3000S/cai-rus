"""
Модуль для обработки непрерывного выполнения агента с автоматическими подсказками продолжения.

Использует синглтон CAIConfig для конфигурации модели/ключа вместо вызовов os.getenv() [S].
"""

import logging
import os
import asyncio
from typing import List, Dict, Any, Optional
from rich.console import Console

from cai.config import get_config

logger = logging.getLogger(__name__)


async def generate_continuation_advice(
    agent_name: str,
    message_history: List[Dict[str, Any]],
    console: Optional[Console] = None
) -> str:
    """
    Сгенерировать умную подсказку продолжения на основе текущего контекста беседы,
    используя модель для анализа ситуации и предоставления контекстных рекомендаций.
    
    Аргументы:
        agent_name: Имя текущего агента
        message_history: Список предыдущих сообщений в беседе
        console: Опциональная консоль Rich для вывода
    
    Возвращает:
        Строка подсказки продолжения для поддержания работы агента
    """
    # Получить модель из синглтона CAIConfig [S]
    cfg = get_config()
    model_name = cfg.model
    
    # Проверить, следует ли использовать модель-запасной вариант для локального тестирования [S]
    # Это позволяет функции продолжения работать даже без учётных данных alias1
    fallback = cfg.continuation_fallback_model
    if model_name == "alias1" and fallback:
        model_name = fallback
    
    # Найти исходный запрос пользователя (первое сообщение пользователя)
    original_request = None
    for msg in message_history:
        if msg.get("role") == "user" and msg.get("content"):
            original_request = msg.get("content")
            break
    
    # Получить недавний контекст для анализа (последние 10 сообщений)
    recent_messages = message_history[-10:] if len(message_history) > 10 else message_history
    
    # Анализ недавней активности
    last_assistant_message = None
    last_tool_output = None
    recent_tool_calls = []
    errors_found = []
    
    for msg in reversed(recent_messages):
        role = msg.get("role", "")
        
        if role == "assistant" and last_assistant_message is None:
            last_assistant_message = msg.get("content", "")
            if msg.get("tool_calls"):
                for tc in msg.get("tool_calls", []):
                    if "function" in tc:
                        recent_tool_calls.append(tc["function"].get("name", "unknown"))
                
        elif role == "tool" and last_tool_output is None:
            last_tool_output = msg.get("content", "")
            # Проверка ошибок в выводе инструмента
            if "error" in str(last_tool_output).lower():
                errors_found.append(last_tool_output)
    
    # Построить более подробный контекст для лучших подсказок продолжения
    # Включить больше истории сообщений для контекста
    conversation_summary = []
    for msg in recent_messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user" and content:
            conversation_summary.append(f"Пользователь: {content[:100]}..." if len(content) > 100 else f"Пользователь: {content}")
        elif role == "assistant" and content:
            conversation_summary.append(f"Агент: {content[:100]}..." if len(content) > 100 else f"Агент: {content}")
        elif role == "tool":
            conversation_summary.append(f"Вывод инструмента: {content[:50]}..." if len(content) > 50 else f"Вывод инструмента: {content}")
    
    context_summary = f"""Вы — ИИ-ассистент, помогающий агенту по кибербезопасности продолжить свою работу. На основе истории беседы сгенерируйте конкретную подсказку продолжения.

ИСХОДНАЯ ЗАДАЧА: {original_request or "Не указана"}

ХОД БЕСЕДЫ:
{chr(10).join(conversation_summary[-5:])}

ТЕКУЩИЙ СТАТУС:
- Последнее действие: {last_assistant_message[:150] + "..." if last_assistant_message and len(last_assistant_message) > 150 else last_assistant_message or "Нет недавних действий"}
- Использованные инструменты: {', '.join(recent_tool_calls) if recent_tool_calls else "Нет"}
- Ошибки: {'Да - ' + str(errors_found[0])[:50] if errors_found else 'Нет'}

Сгенерируйте конкретную, применимую подсказку продолжения, которая:
1. Напрямую указывает, что должно произойти далее
2. Релевантна текущему контексту
3. Помогает достичь исходной задачи
4. Лаконична (одно предложение)

ВАЖНО: Отвечайте ТОЛЬКО подсказкой продолжения. Без объяснений, без «Вот подсказка:», только прямая инструкция."""

    try:
        # Использовать litellm напрямую, как это делает остальная кодовая база для вызовов API
        import litellm
        
        # Включить отладочное логирование для litellm если в режиме отладки
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Генерация подсказки продолжения с моделью: {model_name}")
            logger.debug(f"Длина контекста: {len(context_summary)} символов")
        
        # Подготовить kwargs для litellm в зависимости от типа модели
        kwargs = {
            "model": model_name,
            "messages": [{"role": "user", "content": context_summary}],
            "temperature": 0.3,  # Переопределение по умолчанию (0.7) — более низкая температура для сфокусированного продолжения
            "max_tokens": 150,  # Чуть больше токенов для полных мыслей
            "stream": False
        }
        
        # Настройка для alias2-mini (компактная модель Alias; тот же API-шлюз что и у других моделей alias)
        if model_name.lower() == "alias2-mini":
            kwargs["api_base"] = "https://api.aliasrobotics.com:666/"
            kwargs["custom_llm_provider"] = "openai"
            kwargs["api_key"] = (cfg.alias_api_key or "sk-alias-1234567890").strip()
        # Настройка для моделей alias (следуя паттерну в openai_chatcompletions.py) [S]
        elif "alias" in model_name.lower() and "alias0.5" not in model_name.lower():
            kwargs["api_base"] = "https://api.aliasrobotics.com:666/"
            kwargs["custom_llm_provider"] = "openai"
            kwargs["api_key"] = (cfg.alias_api_key or "sk-alias-1234567890").strip()
        
        # Вызов API
        logger.debug(f"Вызов API с kwargs: {kwargs.get('model')}, провайдер: {kwargs.get('custom_llm_provider', 'по умолчанию')}")
        response = await litellm.acompletion(**kwargs)
        
        # Безопасное извлечение содержимого
        continuation_prompt = None
        if response:
            logger.debug(f"Получен ответ: {response}")
            if hasattr(response, 'choices') and response.choices:
                if hasattr(response.choices[0], 'message') and response.choices[0].message:
                    content = response.choices[0].message.content
                    reasoning_content = getattr(response.choices[0].message, 'reasoning_content', None)
                    if reasoning_content and content:
                        content = reasoning_content + "\n\n" + content
                    elif reasoning_content:
                        content = reasoning_content
                    continuation_prompt = content.strip() if content else None
                    logger.debug(f"Извлечённая подсказка: {continuation_prompt}")
        
        # Проверка на_genericные ответы, для которых стоит использовать лучший запасной вариант
        generic_responses = [
            "продолжить работу над задачей",
            "перейти к следующему шагу",
            "продолжать",
            "continue working on the task",
            "proceed with the next step",
            "keep going",
            "continue"
        ]
        
        is_generic = continuation_prompt and any(
            generic in continuation_prompt.lower() 
            for generic in generic_responses
        ) and len(continuation_prompt) < 50
        
        # Запасной вариант если ответ пустой, слишком короткий или слишком genericный
        if not continuation_prompt or len(continuation_prompt) < 10 or is_generic:
            logger.debug(f"Ответ слишком genericный или короткий, используется контекстный запасной вариант")
            raise ValueError("Generic response - using fallback")
        
    except Exception as e:
        # Логировать ошибку, но не раскрывать пользователю данные аутентификации
        if "AuthenticationError" in str(type(e)):
            logger.debug(f"Ошибка аутентификации модели: {str(e)}")
        else:
            logger.error(f"Ошибка генерации подсказки продолжения: {str(e)}")
        
        # Предоставить более конкретный запасной вариант на основе подробного анализа контекста
        logger.debug(f"Использование запасной логики. Ошибки: {bool(errors_found)}, Инструменты: {recent_tool_calls}, Посл. сообщение: {last_assistant_message[:50] if last_assistant_message else 'Нет'}")
        
        if errors_found:
            error_text = str(errors_found[0]).lower()
            if "not found" in error_text or "does not exist" in error_text:
                continuation_prompt = "Поищите правильный путь к файлу или создайте отсутствующий ресурс."
            elif "permission" in error_text or "denied" in error_text:
                continuation_prompt = "Проверьте права доступа и попробуйте обратиться к ресурсу с соответствующими учётными данными."
            elif "syntax" in error_text or "parse" in error_text:
                continuation_prompt = "Исправьте синтаксическую ошибку и повторите операцию."
            else:
                continuation_prompt = "Проанализируйте конкретное сообщение об ошибке и реализуйте решение."
                
        elif recent_tool_calls:
            # Гораздо более конкретные на основе комбинаций инструментов и контекста
            tool_str = ' '.join(recent_tool_calls).lower()
            
            if "grep" in tool_str or "search" in tool_str:
                if last_tool_output and "found" in str(last_tool_output).lower():
                    continuation_prompt = "Подробно изучите результаты поиска и исследуйте наиболее релевантные находки."
                else:
                    continuation_prompt = "Расширьте параметры поиска или попробуйте другие поисковые запросы."
                    
            elif "read" in tool_str or "file" in tool_str:
                if last_assistant_message and "security" in original_request.lower():
                    continuation_prompt = "Проанализируйте код на уязвимости безопасности, такие как проблемы инъекций или аутентификации."
                else:
                    continuation_prompt = "Обработайте содержимое файла и извлеките соответствующую информацию."
                    
            elif "write" in tool_str or "edit" in tool_str:
                continuation_prompt = "Проверьте корректность внесённых изменений и протестируйте изменённый код."
                
            elif "bash" in tool_str or "shell" in tool_str:
                continuation_prompt = "Проверьте вывод команды и действуйте на основе результатов."
                
            else:
                continuation_prompt = "Используйте результаты инструментов для продвижения к цели."
                
        elif last_assistant_message:
            # Анализ последнего сообщения для лучшего контекста
            last_msg_lower = last_assistant_message.lower()
            
            if "joke" in original_request.lower() or "joke" in last_msg_lower:
                continuation_prompt = "Расскажите ещё одну шутку или каламбур о кибербезопасности."
            elif "found" in last_msg_lower or "discovered" in last_msg_lower:
                continuation_prompt = "Исследуйте эти находки более подробно."
            elif "analyzing" in last_msg_lower or "checking" in last_msg_lower:
                continuation_prompt = "Завершите анализ и подведите итоги."
            elif "error" in last_msg_lower or "issue" in last_msg_lower:
                continuation_prompt = "Устраните выявленную проблему и продолжайте."
            else:
                # Запасной вариант на основе исходного запроса
                if "security" in original_request.lower() or "vulnerabilit" in original_request.lower():
                    continuation_prompt = "Продолжите оценку безопасности, проверив наличие дополнительных уязвимостей."
                elif "analyze" in original_request.lower() or "review" in original_request.lower():
                    continuation_prompt = "Углубите анализ, изучив больше файлов или аспектов."
                elif "test" in original_request.lower():
                    continuation_prompt = "Запустите дополнительные тесты для обеспечения полного покрытия."
                else:
                    continuation_prompt = "Сделайте следующий логический шаг для выполнения исходной задачи."
        else:
            continuation_prompt = "Начните работу над задачей, выполнив первое конкретное действие."
    
    if console:
        console.print(f"\n[cyan]🤖 Автопродолжение с:[/cyan] {continuation_prompt}")
    
    return continuation_prompt


def should_continue_automatically(
    message_history: List[Dict[str, Any]],
    force_continue: bool = False
) -> bool:
    """
    Определить, должен ли агент автоматически продолжать на основе состояния беседы.
    
    Аргументы:
        message_history: Список предыдущих сообщений
        force_continue: Принудительное продолжение независимо от состояния
        
    Возвращает:
        Логическое значение, указывающее, следует ли продолжать автоматически
    """
    if force_continue:
        return True
    
    if not message_history:
        return False
    
    # Получить последние несколько сообщений
    recent_messages = message_history[-5:]
    
    # Проверить, активно ли работает агент (недавнее использование инструментов)
    has_recent_tools = any(
        msg.get("role") == "assistant" and msg.get("tool_calls")
        for msg in recent_messages
    )
    
    # Проверить, заявил ли агент явно о завершении
    last_assistant_msg = None
    for msg in reversed(recent_messages):
        if msg.get("role") == "assistant" and msg.get("content"):
            last_assistant_msg = msg.get("content", "").lower()
            break
    
    if last_assistant_msg:
        completion_indicators = [
            "completed", "finished", "done", "accomplished",
            "achieved", "succeeded", "concluded", "no further",
            "that's all", "nothing more",
            "завершено", "выполнено", "готово", "сделано",
        ]
        
        if any(indicator in last_assistant_msg for indicator in completion_indicators):
            return False
    
    # Продолжать если агент активно использует инструменты или проводит расследование
    return has_recent_tools
