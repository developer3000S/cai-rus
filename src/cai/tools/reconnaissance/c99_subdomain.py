"""
Утилита поиска поддоменов C99.nl для разведки.

Этот модуль предоставляет функцию для перечисления поддоменов заданного домена
с помощью API C99.nl Subdomain Finder и CloudFlare Resolver.
"""

import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from cai.sdk.agents import function_tool


@function_tool
def c99_subdomain_enum(domain: str, realtime: bool = False) -> str:
    """
    Перечисление поддоменов для заданного домена с помощью API C99.nl.

    Args:
        domain (str): Целевой домен (например, example.com).
        realtime (bool): Запрашивать ли результаты в реальном времени / свежие результаты от C99.nl.
                         Может потребовать больше кредитов. По умолчанию False.

    Returns:
        str: Отформатированная строка с обнаруженными поддоменами и, при наличии,
             связанной метаданными.
    """
    results = _perform_c99_subdomain_lookup(domain, realtime=realtime)

    if not results:
        return "Поддомены не найдены или произошла ошибка API."

    formatted_results = ""

    # If the API returned a list of strings, treat each as a subdomain.
    if isinstance(results, list) and all(isinstance(item, str) for item in results):
        for subdomain in results:
            formatted_results += f"Поддомен: {subdomain}\n"
        return formatted_results

    # If the API returned a list of dicts, try to extract common fields.
    if isinstance(results, list) and all(isinstance(item, dict) for item in results):
        for entry in results:
            subdomain = (
                entry.get("subdomain")
                or entry.get("host")
                or entry.get("domain")
                or entry.get("hostname")
                or "N/A"
            )
            ip = entry.get("ip") or entry.get("ip_address") or entry.get("address")
            cloudflare = entry.get("cloudflare") or entry.get("is_cloudflare")

            formatted_results += f"Поддомен: {subdomain}\n"
            if ip:
                formatted_results += f"IP: {ip}\n"
            if cloudflare is not None:
                formatted_results += f"Cloudflare: {cloudflare}\n"

            # Include any other keys that might be useful but are not standardised.
            extra_keys = {
                k: v
                for k, v in entry.items()
                if k
                not in {
                    "subdomain",
                    "host",
                    "domain",
                    "hostname",
                    "ip",
                    "ip_address",
                    "address",
                    "cloudflare",
                    "is_cloudflare",
                }
            }
            if extra_keys:
                formatted_results += f"Дополнительно: {extra_keys}\n"

            formatted_results += "\n"

        return formatted_results

    # Fallback: return a pretty-printed representation of the JSON-like structure.
    try:
        import json

        return json.dumps(results, indent=2, default=str)
    except Exception:  # pylint: disable=broad-except
        return str(results)


def _perform_c99_subdomain_lookup(
    domain: str, realtime: bool = False
) -> Optional[List[Any] | Dict[str, Any]]:
    """
    Вспомогательная функция для выполнения поиска поддоменов C99.nl.

    API C99.nl Subdomain Finder обычно используется через:
        https://api.c99.nl/subdomainfinder?key=API_KEY&domain=example.com&json

    Args:
        domain (str): Целевой домен.
        realtime (bool): Запрашивать ли результаты в реальном времени.

    Returns:
        Optional[List[Any] | Dict[str, Any]]: Разобранный ответ JSON или None
        в случае ошибки.
    """
    load_dotenv()
    api_key = os.getenv("C99_API_KEY")

    if not api_key:
        raise ValueError("Ключ API C99.nl (C99_API_KEY) должен быть установлен в переменных окружения.")

    base_url = "https://api.c99.nl/subdomainfinder"

    params = {
        "key": api_key,
        "domain": domain,
    }

    # Request JSON output as recommended by C99.nl.
    # Their API supports appending `&json` to the query string. Using an empty
    # value here results in `json=` which is accepted by the API.
    params["json"] = ""

    if realtime:
        params["realtime"] = "true"

    try:
        response = requests.get(base_url, params=params, timeout=60)
        if response.status_code != 200:
            return None

        # Many C99 APIs return either a list or a dict when `&json` is used.
        # We return the parsed JSON and let the caller format it.
        return response.json()
    except Exception:  # pylint: disable=broad-except
        return None


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("c99_subdomain_enum", c99_subdomain_enum, categories=["recon", "web"])

