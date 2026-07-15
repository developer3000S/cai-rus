"""
Универсальная утилита OSINT от C99.nl для разведки.

Этот модуль предоставляет инструмент `c99`, который объединяет множество API C99.nl,
обеспечивая единый интерфейс для типичных задач разведки / OSINT.

Примеры действий (полное описание см. в документации C99.nl):
    - \"subdomain\"      → Поиск поддоменов / CloudFlare Resolver
    - \"firewall\"       → Определение технологии файрвола (WAF)
    - \"phone_lookup\"   → Поиск информации о номере телефона
    - \"ping\"           → Пинг хоста
    - \"geoip\"          → GeoIP запрос
    - \"whois\"          → Whois проверка
    - \"gif\"            → Поиск GIF

Окружение:
    - Требуется переменная C99_API_KEY (или её наличие в .env).
"""

import json
import os
from typing import Any, Dict, List, Optional, Union, Literal

import requests
from dotenv import load_dotenv

from cai.sdk.agents import function_tool

JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


def _get_c99_api_key() -> str:
    """Загрузить и вернуть API-ключ C99 из переменных окружения."""
    load_dotenv()
    api_key = os.getenv("C99_API_KEY")
    if not api_key:
        raise ValueError("API-ключ C99.nl (C99_API_KEY) должен быть задан в переменных окружения.")
    return api_key


def _call_c99_api(endpoint: str, params: Dict[str, Any]) -> Optional[JSONType]:
    """
    Generic helper to call a C99.nl API endpoint and return parsed JSON.

    Note: Endpoint paths and parameter names are based on publicly
    available examples and may need adjustment to match your C99.nl
    documentation exactly.
    """
    api_key = _get_c99_api_key()

    base_url = f"https://api.c99.nl/{endpoint}"

    query_params: Dict[str, Any] = {"key": api_key}
    # Remove None-valued parameters to avoid sending them.
    for k, v in params.items():
        if v is not None:
            query_params[k] = v

    # Request JSON output where supported.
    query_params["json"] = ""

    try:
        response = requests.get(base_url, params=query_params, timeout=60)
    except Exception:  # pylint: disable=broad-except
        return None

    if response.status_code != 200:
        return None

    try:
        return response.json()
    except Exception:  # pylint: disable=broad-except
        # If JSON parsing fails, fall back to raw text.
        return response.text


def _format_subdomain_results(
    data: JSONType,
    only_cloudflare: bool = False,
) -> str:
    """Форматировать результаты поиска поддоменов / Cloudflare resolver."""
    if data is None:
        return "Поддомены не найдены или произошла ошибка API."

    # C99.nl / wrappers commonly return a dict with a `subdomains` key.
    if isinstance(data, dict) and "subdomains" in data:
        entries = data.get("subdomains") or []
    elif isinstance(data, list):
        entries = data
    else:
        # Fallback to JSON dump for unexpected shapes.
        return json.dumps(data, indent=2, default=str)

    formatted_results = ""
    count = 0

    for entry in entries:
        # Strings: treat each as a subdomain.
        if isinstance(entry, str):
            subdomain = entry
            cloudflare_flag = None
            ip = None
        elif isinstance(entry, dict):
            subdomain = (
                entry.get("subdomain")
                or entry.get("host")
                or entry.get("domain")
                or entry.get("hostname")
                or "N/A"
            )
            ip = entry.get("ip") or entry.get("ip_address") or entry.get("address")
            cloudflare_flag = entry.get("cloudflare")
            if cloudflare_flag is None:
                cloudflare_flag = entry.get("is_cloudflare")
        else:
            continue

        if only_cloudflare and not cloudflare_flag:
            continue

        count += 1
        formatted_results += f"Subdomain: {subdomain}\n"
        if ip:
            formatted_results += f"IP: {ip}\n"
        if cloudflare_flag is not None:
            formatted_results += f"Cloudflare: {cloudflare_flag}\n"
        formatted_results += "\n"

    if count == 0:
        if only_cloudflare:
            return "Поддомены за Cloudflare не найдены."
        return "Поддомены не найдены."

    return formatted_results


def _format_firewall_results(data: JSONType, target: str) -> str:
    """Форматировать результаты определения файрвола / WAF."""
    if data is None:
        return f"Информация о файрволе для {target} не найдена или произошла ошибка API."

    if isinstance(data, dict):
        # Many wrappers return {success: bool, result: "..."} or similar.
        if not data.get("success", True):
            reason = data.get("message") or data.get("error") or "Неизвестная ошибка"
            return f"Обнаружение файрвола не удалось для {target}: {reason}"

        result = data.get("result") or data.get("firewall") or data.get("waf")
        if result:
            return f"Файрвол / WAF для {target}: {result}"

        # Fallback to JSON dump when shape is unexpected but dict-like.
        return json.dumps(data, indent=2, default=str)

    # Fallback for non-dict payloads.
    return str(data)


def _format_phone_lookup_results(data: JSONType, number: str) -> str:
    """Форматировать результаты поиска информации о номере телефона."""
    if data is None:
        return f"Информация о номере {number} не найдена или произошла ошибка API."

    if isinstance(data, dict):
        if not data.get("success", True):
            reason = data.get("message") or data.get("error") or "Неизвестная ошибка"
            return f"Поиск телефона не удался для {number}: {reason}"

        formatted = f"Информация о номере {number}:\n"
        # Highlight commonly useful fields when present.
        common_keys = [
            "international",
            "local_format",
            "country",
            "country_code",
            "location",
            "carrier",
            "line_type",
            "type",
            "valid",
        ]
        for key in common_keys:
            if key in data:
                formatted += f"{key.replace('_', ' ').title()}: {data[key]}\n"

        # Include any remaining keys for completeness.
        extra_keys = {
            k: v
            for k, v in data.items()
            if k not in common_keys and k not in {"success"}
        }
        if extra_keys:
            formatted += f"Extra: {extra_keys}\n"

        return formatted

    # Fallback for non-dict payloads.
    return str(data)


def _format_generic_results(data: Optional[JSONType]) -> str:
    """Универсальный форматировщик для JSON/текстовых ответов C99.nl."""
    if data is None:
        return "Данные не возвращены или произошла ошибка API."

    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2, default=str)

    return str(data)


@function_tool
def c99(
    action: Literal[
        "subdomain",
        "cloudflare",
        "firewall",
        "phone_lookup",
        "ping",
        "ip_to_host",
        "dns_checker",
        "host_to_ip",
        "ip2domains",
        "whois",
        "screenshot",
        "geoip",
        "up_or_down",
        "reputation",
        "headers",
        "link_backup",
        "random_string",
        "dictionary",
        "synonym",
        "email_validator",
        "disposable_email",
        "ip_validator",
        "tor_checker",
        "translate",
        "random_person",
        "youtube_details",
        "ip_logger",
        "bitcoin_balance",
        "currency",
        "currency_rates",
        "weather",
        "qr_generator",
        "proxy_detector",
        "password_generator",
        "random_number",
        "license_key",
        "either_or",
        "gif",
    ],
    target: str = "",
    param1: Optional[str] = None,
    param2: Optional[str] = None,
    param3: Optional[str] = None,
    realtime: bool = False,
) -> str:
    """
    Выполнить действие OSINT от C99.nl над целью.

    Args:
        action (str): Действие для выполнения. Поддерживаемые:
            - \"subdomain\": перечисление поддоменов для домена.
            - \"cloudflare\": перечисление поддоменов; показывать только за Cloudflare.
            - \"firewall\": определение технологии WAF / файрвола для URL.
            - \"phone_lookup\": поиск информации о номере телефона.
            - \"ping\": пинг хоста.
            - \"ip_to_host\": разрешение IP в имя хоста.
            - \"dns_checker\": расширенная DNS-проверка для домена (param1=тип, param2=сервер).
            - \"host_to_ip\": разрешение имени хоста в IP (param2=сервер).
            - \"ip2domains\": поиск доменов, размещённых на IP.
            - \"whois\": whois-запрос для домена.
            - \"screenshot\": создание скриншота для URL.
            - \"geoip\": GeoIP-запрос для хоста/IP.
            - \"up_or_down\": проверка доступности сайта.
            - \"reputation\": проверка репутации сайта/URL.
            - \"headers\": получение HTTP-заголовков для хоста.
            - \"link_backup\": создание онлайн-резервной копии URL.
            - \"random_string\": выбор случайной строки из удалённого текстового файла.
            - \"dictionary\": поиск слова в словаре.
            - \"synonym\": поиск синонимов для слова.
            - \"email_validator\": проверка существования электронной почты.
            - \"disposable_email\": проверка, является ли почта одноразовой.
            - \"ip_validator\": проверка формата IP-адреса.
            - \"tor_checker\": проверка, является ли IP выходом TOR.
            - \"translate\": перевод текста (target=текст, param1=код языка).
            - \"random_person\": генерация случайного человека (target=пол).
            - \"youtube_details\": получение деталей видео YouTube (target=ID видео).
            - \"ip_logger\": управление IP-логгером (target=действие, param1=доп. параметр).
            - \"bitcoin_balance\": проверка баланса адреса Bitcoin.
            - \"currency\": конвертация валюты (target=сумма, param1=из, param2=в).
            - \"currency_rates\": получение курсов валют (target=исходная валюта).
            - \"weather\": запрос погоды (target=местоположение).
            - \"qr_generator\": генерация QR-кода (target=строка, param1=размер).
            - \"proxy_detector\": определение, является ли IP прокси/VPN.
            - \"password_generator\": генерация пароля
                (param1=длина, param2=включить, param3=пользовательский список).
            - \"random_number\": случайное число
                (param1=длина или param2=\"min,max\" для диапазона).
            - \"license_key\": генерация лицензионного ключа
                (target=шаблон, param1=количество).
            - \"either_or\": получение случайной дилеммы.
            - \"gif\": поиск GIF (target=ключевое слово).
        target (str): Основная целевая строка. Интерпретация зависит от действия,
            см. выше.
        param1 (str, optional): Вспомогательный параметр для некоторых действий.
        param2 (str, optional): Вспомогательный параметр для некоторых действий.
        param3 (str, optional): Вспомогательный параметр для некоторых действий.
        realtime (bool): Для действий, связанных с поддоменами, запрашивать
                         результаты в реальном времени, где это поддерживается.
                         Игнорируется для других действий.

    Returns:
        str: Форматированная строка с результатами или сообщение об ошибке.
    """
    normalized = action.lower().strip()

    if normalized in {"subdomain", "subdomains"}:
        data = _call_c99_api(
            "subdomainfinder",
            {
                "domain": target,
                "realtime": "true" if realtime else None,
            },
        )
        return _format_subdomain_results(data, only_cloudflare=False)

    if normalized in {"cloudflare", "cf"}:
        data = _call_c99_api(
            "subdomainfinder",
            {
                "domain": target,
                "realtime": "true" if realtime else None,
            },
        )
        return _format_subdomain_results(data, only_cloudflare=True)

    if normalized in {"firewall", "waf"}:
        # NOTE: Endpoint / parameter names are inferred from public examples
        # and may need to be adjusted to match your C99.nl documentation.
        data = _call_c99_api(
            "firewalldetector",
            {
                "url": target,
            },
        )
        return _format_firewall_results(data, target)

    if normalized in {"phone_lookup", "phonelookup", "phone"}:
        data = _call_c99_api(
            "phonelookup",
            {
                "number": target,
            },
        )
        return _format_phone_lookup_results(data, target)

    if normalized == "ping":
        data = _call_c99_api(
            "ping",
            {
                "host": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"ip_to_host", "iptohost"}:
        data = _call_c99_api(
            "gethostname",
            {
                "host": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"dns_checker", "dnschecker"}:
        data = _call_c99_api(
            "dnschecker",
            {
                "url": target,
                "type": param1,  # e.g., a, aaaa, cname, mx, ns, soa, txt
                "server": param2,  # country code or empty for all
            },
        )
        return _format_generic_results(data)

    if normalized in {"host_to_ip", "hosttoip"}:
        data = _call_c99_api(
            "dnsresolver",
            {
                "host": target,
                "server": param2,  # optional server code
            },
        )
        return _format_generic_results(data)

    if normalized == "ip2domains":
        data = _call_c99_api(
            "ip2domains",
            {
                "ip": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "whois":
        data = _call_c99_api(
            "whois",
            {
                "domain": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "screenshot":
        data = _call_c99_api(
            "createscreenshot",
            {
                "url": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "geoip":
        data = _call_c99_api(
            "geoip",
            {
                "host": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"up_or_down", "upordown"}:
        data = _call_c99_api(
            "upordown",
            {
                "host": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"reputation", "reputationchecker"}:
        data = _call_c99_api(
            "reputationchecker",
            {
                "url": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"headers", "getheaders"}:
        data = _call_c99_api(
            "getheaders",
            {
                "host": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"link_backup", "linkbackup"}:
        data = _call_c99_api(
            "linkbackup",
            {
                "url": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"random_string", "randomstringpicker"}:
        data = _call_c99_api(
            "randomstringpicker",
            {
                "textfile": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "dictionary":
        data = _call_c99_api(
            "dictionary",
            {
                "word": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "synonym":
        data = _call_c99_api(
            "synonym",
            {
                "word": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"email_validator", "emailvalidator"}:
        data = _call_c99_api(
            "emailvalidator",
            {
                "email": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"disposable_email", "disposablemailchecker"}:
        data = _call_c99_api(
            "disposablemailchecker",
            {
                "email": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"ip_validator", "ipvalidator"}:
        data = _call_c99_api(
            "ipvalidator",
            {
                "ip": target,
            },
        )
        return _format_generic_results(data)

    if normalized in {"tor_checker", "torchecker"}:
        data = _call_c99_api(
            "torchecker",
            {
                "ip": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "translate":
        data = _call_c99_api(
            "translate",
            {
                "text": target,
                "tolanguage": param1,
            },
        )
        return _format_generic_results(data)

    if normalized == "random_person":
        data = _call_c99_api(
            "randomperson",
            {
                "gender": target or "all",
            },
        )
        return _format_generic_results(data)

    if normalized == "youtube_details":
        data = _call_c99_api(
            "youtubedetails",
            {
                "videoid": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "ip_logger":
        data = _call_c99_api(
            "iplogger",
            {
                "action": target or "viewloggers",
                "id": param1,
            },
        )
        return _format_generic_results(data)

    if normalized == "bitcoin_balance":
        data = _call_c99_api(
            "bitcoinbalance",
            {
                "address": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "currency":
        data = _call_c99_api(
            "currency",
            {
                "amount": target,
                "from": param1,
                "to": param2,
            },
        )
        return _format_generic_results(data)

    if normalized == "currency_rates":
        data = _call_c99_api(
            "currencyrates",
            {
                "source": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "weather":
        data = _call_c99_api(
            "weather",
            {
                "location": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "qr_generator":
        data = _call_c99_api(
            "qrgenerator",
            {
                "string": target,
                "size": param1,
            },
        )
        return _format_generic_results(data)

    if normalized == "proxy_detector":
        data = _call_c99_api(
            "proxydetector",
            {
                "ip": target,
            },
        )
        return _format_generic_results(data)

    if normalized == "password_generator":
        data = _call_c99_api(
            "passwordgenerator",
            {
                "length": param1,
                "include": param2,
                "customlist": param3,
            },
        )
        return _format_generic_results(data)

    if normalized == "random_number":
        data = _call_c99_api(
            "randomnumber",
            {
                "length": param1,
                "between": param2,
            },
        )
        return _format_generic_results(data)

    if normalized == "license_key":
        data = _call_c99_api(
            "licensekeygenerator",
            {
                "template": target,
                "amount": param1,
            },
        )
        return _format_generic_results(data)

    if normalized in {"either_or", "eitheror"}:
        data = _call_c99_api("eitheror", {})
        return _format_generic_results(data)

    if normalized == "gif":
        data = _call_c99_api(
            "gif",
            {
                "keyword": target,
            },
        )
        return _format_generic_results(data)

    return (
        "Неподдерживаемое действие C99. Поддерживаемые действия: subdomain, cloudflare, "
        "firewall, phone_lookup, ping, ip_to_host, dns_checker, host_to_ip, "
        "ip2domains, whois, screenshot, geoip, up_or_down, reputation, headers, "
        "link_backup, random_string, dictionary, synonym, email_validator, "
        "disposable_email, ip_validator, tor_checker, translate, random_person, "
        "youtube_details, ip_logger, bitcoin_balance, currency, currency_rates, "
        "weather, qr_generator, proxy_detector, password_generator, random_number, "
        "license_key, either_or, gif."
    )


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("c99", c99, categories=["recon", "web"])
