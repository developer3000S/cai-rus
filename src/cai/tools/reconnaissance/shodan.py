"""
Утилита поиска Shodan для разведки.

Этот модуль предоставляет функции для поиска информации о хостах,
сервисах и уязвимостях в Shodan с помощью API Shodan.
"""

import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from cai.sdk.agents import function_tool


@function_tool
def shodan_search(query: str, limit: int = 10) -> str:
    """
    Поиск информации в Shodan по указанному запросу.

    Args:
        query (str): Поисковый запрос Shodan.
        limit (int): Максимальное количество результатов. По умолчанию 10.

    Returns:
        str: Отформатированная строка с результатами поиска.
    """
    results = _perform_shodan_search(query, limit)

    if not results:
        return "Результаты не найден или произошла ошибка API."

    formatted_results = ""
    for result in results:
        formatted_results += f"IP: {result.get('ip_str', 'N/A')}\n"
        formatted_results += f"Порт: {result.get('port', 'N/A')}\n"
        formatted_results += f"Организация: {result.get('org', 'N/A')}\n"
        formatted_results += f"Имена хостов: {', '.join(result.get('hostnames', ['N/A']))}\n"
        formatted_results += f"Страна: {result.get('location', {}).get('country_name', 'N/A')}\n"

        if "data" in result:
            formatted_results += (
                f"Баннер: {result['data'][:200]}...\n"
                if len(result["data"]) > 200
                else f"Баннер: {result['data']}\n"
            )

        formatted_results += "\n"

    return formatted_results


@function_tool
def shodan_host_info(ip: str) -> str:
    """
    Получить подробную информацию о конкретном хосте из Shodan.

    Args:
        ip (str): IP-адрес хоста.

    Returns:
        str: Отформатированная строка с информацией о хосте.
    """
    result = _get_shodan_host_info(ip)

    if not result:
        return f"Информация для IP {ip} не найдена или произошла ошибка API."

    formatted_result = f"IP: {result.get('ip_str', 'N/A')}\n"
    formatted_result += f"Организация: {result.get('org', 'N/A')}\n"
    formatted_result += f"Операционная система: {result.get('os', 'N/A')}\n"
    formatted_result += f"Страна: {result.get('country_name', 'N/A')}\n"
    formatted_result += f"Город: {result.get('city', 'N/A')}\n"
    formatted_result += f"Провайдер: {result.get('isp', 'N/A')}\n"
    formatted_result += f"Последнее обновление: {result.get('last_update', 'N/A')}\n"
    formatted_result += f"Имена хостов: {', '.join(result.get('hostnames', ['N/A']))}\n"
    formatted_result += f"Домены: {', '.join(result.get('domains', ['N/A']))}\n\n"

    if "ports" in result:
        formatted_result += f"Открытые порты: {', '.join(map(str, result['ports']))}\n\n"

    if "vulns" in result:
        formatted_result += "Уязвимости:\n"
        for vuln in result["vulns"]:
            formatted_result += f"- {vuln}\n"

    return formatted_result


def _perform_shodan_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Вспомогательная функция для выполнения поиска в Shodan.

    Args:
        query (str): Поисковый запрос Shodan.
        limit (int): Максимальное количество результатов.

    Returns:
        List[Dict[str, Any]]: Список словарей с результатами поиска.
    """
    load_dotenv()
    api_key = os.getenv("SHODAN_API_KEY")

    if not api_key:
        raise ValueError("Ключ API Shodan (SHODAN_API_KEY) должен быть установлен в переменных окружения.")

    base_url = "https://api.shodan.io/shodan/host/search"

    params = {
        "key": api_key,
        "query": query,
        "limit": min(limit, 100),  # Shodan API has limits
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            return []

        data = response.json()

        if "matches" not in data:
            return []

        return data["matches"][:limit]

    except Exception:
        return []


def _get_shodan_host_info(ip: str) -> Optional[Dict[str, Any]]:
    """
    Вспомогательная функция для получения информации о хосте из Shodan.

    Args:
        ip (str): IP-адрес хоста.

    Returns:
        Optional[Dict[str, Any]]: Словарь с информацией о хосте или None в случае ошибки.
    """
    load_dotenv()
    api_key = os.getenv("SHODAN_API_KEY")

    if not api_key:
        raise ValueError("Ключ API Shodan (SHODAN_API_KEY) должен быть установлен в переменных окружения.")

    base_url = f"https://api.shodan.io/shodan/host/{ip}"

    params = {"key": api_key}

    try:
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            return None

        return response.json()

    except Exception:
        return None


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("shodan_search", shodan_search, categories=["recon", "network"])
TOOL_REGISTRY.register("shodan_host_info", shodan_host_info, categories=["recon", "network"])
