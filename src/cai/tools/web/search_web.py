import os
import re
from openai import OpenAI
from dotenv import load_dotenv

from cai.tools.web.google_search import google_dork_search, google_search
from cai.sdk.agents import function_tool
from cai.agents.guardrails import sanitize_external_content


@function_tool
def query_perplexity(query: str = "", context: str = "") -> str:
    """
    Запрос к API Perplexity AI с пользовательским запросом.

    Args:
        query (str): Вопрос для поиска.
        context (str): Полный контекст текущего задания CTF.

    Returns:
        str: Ответ от Perplexity AI.
    """
    load_dotenv()
    api_key = os.getenv("PERPLEXITY_API_KEY")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert cybersecurity researcher specializing in CTF "
                "competitions. Your role is to search for and provide precise, "
                "actionable intelligence to your pentesting team. Focus on "
                "delivering technical details, exploitation techniques, and "
                "vulnerability information relevant to the search query. Include "
                "specific commands, payloads, or tools that would help the team "
                "progress in their CTF challenge. Prioritize accuracy and depth "
                "over general explanations. Your team relies on your research to "
                "identify attack vectors, bypass security controls, and capture "
                "flags. Always suggest concrete next steps based on your findings."
                "Put the neccesary code in each iteration"
            ),
        },
        {
            "role": "user",
            "content": (
                f"You should search the following terms: {query} and the full "
                f"context of current CTF challenge: {context}"
            ),
        },
    ]

    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    
    # Sanitize the response as it comes from external source
    content = response.choices[0].message.content
    return sanitize_external_content(content)



@function_tool
def make_web_search_with_explanation(context: str = "", query: str = "") -> str:
    """
    Выполняет интеллектуальный веб-поиск через AI-сервис для поиска
    релевантной информации по кибербезопасности и CTF. Эта функция отправляет
    указанный запрос в поисковую систему и возвращает ответ.
    Она также использует полный контекст текущего задания CTF.

    КОНТЕКСТ ВСЕГДА НЕОБХОДИМ
    Args:
      context (str): Полный контекст текущего задания CTF.
        query (str): Вопрос или ключевые слова для поиска.


    Returns:
        str: Результат поиска.
    """
    return query_perplexity(query, context)


@function_tool
def make_google_search(query: str, dorks=False) -> str:
    """
    Поиск информации в Google.

    Args:
        query: Поисковый запрос для Google.
        dorks: Использовать ли Google dorks для расширенного поиска.
            По умолчанию False.

    Returns:
        Список результатов поиска. Каждый результат содержит URL, заголовок и фрагмент.
    """
    if dorks:
        result = google_dork_search(query)
    else:
        result = google_search(query)
    
    # Sanitize search results as they come from external sources
    if isinstance(result, str):
        return sanitize_external_content(result)
    return result


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("query_perplexity", query_perplexity, categories=["recon", "web"])
TOOL_REGISTRY.register("make_web_search_with_explanation", make_web_search_with_explanation, categories=["recon", "web"])
TOOL_REGISTRY.register("make_google_search", make_google_search, categories=["recon", "web"])
