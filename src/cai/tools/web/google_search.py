"""
Утилита поиска Google для обычных поисковых запросов и Google Dorking.

Этот модуль предоставляет функции для выполнения поисковых запросов Google в двух режимах:
1. Обычный поиск - возвращает URL из стандартных результатов поиска Google
2. Google Dorking - возвращает URL из поисков с использованием продвинутых операторов Google
"""

import os
import requests
from typing import List, Optional, Dict, Tuple
from dotenv import load_dotenv
from cai.sdk.agents import function_tool


def google_search(query: str, num_results: int = 10) -> str:
    """
    Выполняет обычный поиск Google и возвращает форматированную строку с результатами.

    Args:
        query (str): Поисковый запрос.
        num_results (int): Максимальное количество результатов. По умолчанию 10.

    Returns:
        str: Форматированная строка, содержащая URL, заголовки и фрагменты
        результатов поиска.
    """
    results = _perform_search(query, num_results, is_dork=False)
    formatted_results = ""

    for result in results:
        formatted_results += f"Title: {result['title']}\n"
        formatted_results += f"URL: {result['url']}\n"
        formatted_results += f"Snippet: {result['snippet']}\n\n"

    return formatted_results


def google_dork_search(dork_query: str, num_results: int = 100) -> str:
    """
    Выполняет поиск Google Dork и возвращает форматированную строку с URL.

    Google Dorking использует продвинутые операторы поиска для поиска конкретной информации.
    Примеры операторов: site:, filetype:, inurl:, intitle: и т.д.

    Args:
        dork_query (str): Запрос Google Dork с операторами.
        num_results (int): Максимальное количество результатов. По умолчанию 10.

    Returns:
        str: Форматированная строка, содержащая URL из результатов поиска Dork.
    """
    results = _perform_search(dork_query, num_results, is_dork=True)
    formatted_results = ""

    for result in results:
        formatted_results += f"{result['url']}\n"

    return formatted_results


def _perform_search(
    query: str, num_results: int = 10, is_dork: bool = False
) -> List[Dict[str, str]]:
    """
    Вспомогательная функция для выполнения поисковых запросов Google.

    Args:
        query (str): Поисковый запрос.
        num_results (int): Максимальное количество результатов.
        is_dork (bool): Является ли это поиском Dork.

    Returns:
        List[Dict[str, str]]: Для обычных поисков возвращает список словарей
        с URL, заголовками и фрагментами. Для поисков Dork возвращает список
        словарей только с URL.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")

    if not api_key or not cx:
        raise ValueError(
            "Ключ API Google Search (GOOGLE_SEARCH_API_KEY) и ID пользовательского "
            "поискового движка (GOOGLE_SEARCH_CX) должны быть установлены в переменных окружения."
        )

    base_url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": min(num_results, 10),  # API limits to 10 results per request
    }

    results = []

    # Google API returns max 10 results per request, so we need to make multiple
    # requests with different start indices to get more results
    for start_index in range(
        1, min(num_results + 1, 101), 10
    ):  # Google API limits to 100 results total
        if start_index > 1:
            params["start"] = start_index

        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            break

        data = response.json()

        if "items" not in data:
            break

        for item in data["items"]:
            if len(results) >= num_results:
                break

            if is_dork:
                results.append({"url": item["link"]})
            else:
                results.append(
                    {
                        "url": item["link"],
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                    }
                )

    return results


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("google_search", function_tool(google_search), categories=['web', 'recon'])
TOOL_REGISTRY.register("google_dork_search", function_tool(google_dork_search), categories=['web', 'recon'])
