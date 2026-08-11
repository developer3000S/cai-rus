"""Адаптер LiteLLM для вызовов моделей OpenAI и Ollama/Qwen.

Оборачивает ``litellm.acompletion`` с фильтрацией параметров для конкретных
провайдеров, повторной попыткой при слишком длинном tool_call_id и построением
объекта Response для потоковой передачи.

Извлечено из openai_chatcompletions.py [F] для уменьшения размера монолита.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Literal, cast

import litellm
from openai import NOT_GIVEN, NotGiven
from openai.types.responses import Response

from cai.util import get_ollama_api_base
from ..fake_id import FAKE_RESPONSES_ID

if TYPE_CHECKING:
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletionToolChoiceOptionParam,
    )
    from openai import AsyncStream
    from ...model_settings import ModelSettings


def _build_response_obj(
    model: str,
    model_settings: "ModelSettings",
    tool_choice: "ChatCompletionToolChoiceOptionParam | NotGiven",
    parallel_tool_calls: bool,
) -> Response:
    """Создать заглушку объекта Response для обёрток потоковой передачи."""
    return Response(
        id=FAKE_RESPONSES_ID,
        created_at=time.time(),
        model=model,
        object="response",
        output=[],
        tool_choice="auto"
        if tool_choice is None or tool_choice == NOT_GIVEN
        else cast(Literal["auto", "required", "none"], tool_choice),
        top_p=model_settings.top_p,
        temperature=model_settings.temperature,
        tools=[],
        parallel_tool_calls=parallel_tool_calls or False,
    )


async def fetch_response_litellm_openai(
    *,
    kwargs: dict,
    model_name: str,
    model_settings: "ModelSettings",
    tool_choice: "ChatCompletionToolChoiceOptionParam | NotGiven",
    stream: bool,
    parallel_tool_calls: bool,
) -> "ChatCompletion | tuple[Response, AsyncStream[ChatCompletionChunk]]":
    """Обработать стандартные вызовы LiteLLM API для OpenAI и совместимых моделей.

    Если возникает ContextWindowExceededError из-за слишком длинного tool_call_id,
    усекает все tool_call_id в сообщениях до 40 символов и повторяет запрос
    один раз без уведомления.
    """
    try:
        if stream:
            ret = await litellm.acompletion(**kwargs)
            stream_obj = await litellm.acompletion(**kwargs)
            return _build_response_obj(model_name, model_settings, tool_choice, parallel_tool_calls), stream_obj
        else:
            return await litellm.acompletion(**kwargs)
    except Exception as e:
        error_msg = str(e)
        if (
            "string too long" in error_msg
            or "Invalid 'messages" in error_msg
            and "tool_call_id" in error_msg
            and "maximum length" in error_msg
        ):
            # Усечь все tool_call_id до 40 символов и повторить попытку один раз
            messages = kwargs.get("messages", [])
            for msg in messages:
                if (
                    "tool_call_id" in msg
                    and isinstance(msg["tool_call_id"], str)
                    and len(msg["tool_call_id"]) > 40
                ):
                    msg["tool_call_id"] = msg["tool_call_id"][:40]
                if "tool_calls" in msg and isinstance(msg["tool_calls"], list):
                    for tool_call in msg["tool_calls"]:
                        if (
                            isinstance(tool_call, dict)
                            and "id" in tool_call
                            and isinstance(tool_call["id"], str)
                            and len(tool_call["id"]) > 40
                        ):
                            tool_call["id"] = tool_call["id"][:40]
            kwargs["messages"] = messages

            if stream:
                ret = await litellm.acompletion(**kwargs)
                stream_obj = await litellm.acompletion(**kwargs)
                return _build_response_obj(model_name, model_settings, tool_choice, parallel_tool_calls), stream_obj
            else:
                return await litellm.acompletion(**kwargs)
        else:
            raise


async def fetch_response_litellm_ollama(
    *,
    kwargs: dict,
    model_name: str,
    model_settings: "ModelSettings",
    tool_choice: "ChatCompletionToolChoiceOptionParam | NotGiven",
    stream: bool,
    parallel_tool_calls: bool,
) -> "ChatCompletion | tuple[Response, AsyncStream[ChatCompletionChunk]]":
    """Получить ответ от модели Ollama или Qwen через LiteLLM.

    Гарантирует, что параметр 'format' не установлен как JSON-строка (это может
    вызвать проблемы с Ollama API), и фильтрует только поддерживаемые параметры.
    """
    # Извлечь только поддерживаемые параметры для Ollama
    ollama_supported_params = {
        "model": kwargs.get("model", ""),
        "messages": kwargs.get("messages", []),
        "stream": kwargs.get("stream", False),
    }

    for param in ["temperature", "top_p", "max_tokens"]:
        if param in kwargs and kwargs[param] is not NOT_GIVEN:
            ollama_supported_params[param] = kwargs[param]

    if "extra_headers" in kwargs:
        ollama_supported_params["extra_headers"] = kwargs["extra_headers"]

    if "tools" in kwargs and kwargs.get("tools") and kwargs.get("tools") is not NOT_GIVEN:
        ollama_supported_params["tools"] = kwargs.get("tools")

    ollama_kwargs = {
        k: v
        for k, v in ollama_supported_params.items()
        if v is not None and k not in ["response_format", "store"]
    }

    api_base = get_ollama_api_base()

    if stream:
        response = _build_response_obj(model_name, model_settings, tool_choice, parallel_tool_calls)
        stream_obj = await litellm.acompletion(
            **ollama_kwargs, api_base=api_base, custom_llm_provider="openai"
        )
        return response, stream_obj
    else:
        return await litellm.acompletion(
            **ollama_kwargs,
            api_base=api_base,
            custom_llm_provider="openai",
        )
