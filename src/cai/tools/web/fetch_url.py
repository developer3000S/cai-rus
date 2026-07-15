"""LLM-friendly URL fetcher.

Downloads a single URL and returns its main content as Markdown (HTML),
extracted text (PDF), pretty-printed JSON, or plain text. Designed for use
by CAI agents as a "read the web" tool after running a search.

Design notes:

* Static HTTP only. No JavaScript rendering. SPAs that ship an empty
  ``<html><script>...</script></html>`` shell will not work — this is
  intentional to keep the tool fast, lightweight and OPSEC-friendly.
* httpx is the primary client. If httpx hits a Cloudflare "Just a moment"
  challenge or returns 403/503 with an anti-bot HTML body, the call is
  retried with ``curl-cffi`` (Chrome TLS fingerprint).
* SSRF guard blocks loopback / RFC1918 / link-local / cloud-metadata hosts
  and non-http(s) schemes by default. Bypass via ``CAI_FETCH_ALLOW_INTERNAL``.
* DNS-rebinding mitigation: hostnames are resolved exactly once before the
  request and the resulting IP is *pinned*. httpx is told to dial the IP
  literal while keeping the original FQDN in the ``Host`` header and
  ``sni_hostname`` TLS extension. Redirects are followed manually so each
  hop is re-validated by the SSRF guard.
* All output is wrapped by ``sanitize_external_content`` to defang
  prompt-injection payloads embedded in remote content.
* Errors never raise; they are returned as sanitized strings so the LLM can
  reason about them.

This module is intentionally a single ~600 LOC file (cohesive: SSRF guard
+ fetch + extract + JS-required detector + tool wrapper); splitting it
would create three trivial sub-modules sharing one tool. Cortocircuito
del PRP §8 aceptado.
"""

from __future__ import annotations

import asyncio
import io
import ipaddress
import json
import os
import re
import socket
from urllib.parse import urlsplit, urlunsplit

import httpx

from cai.agents.guardrails import sanitize_external_content
from cai.sdk.agents import function_tool

# Cloud-metadata hostnames that must never be reachable through the tool.
_METADATA_HOSTS: frozenset[str] = frozenset(
    {
        "metadata.google.internal",
        "metadata",
        "metadata.azure.com",
        "instance-data",
    }
)

# Numeric metadata endpoints (IMDS).
_METADATA_IPS: frozenset[str] = frozenset(
    {
        "169.254.169.254",  # AWS / GCP / Azure / DigitalOcean / Alibaba
        "100.100.100.200",  # Alibaba Cloud secondary
        "fd00:ec2::254",  # AWS IPv6 IMDS
    }
)

_ALLOWED_SCHEMES: frozenset[str] = frozenset({"http", "https"})

# Heuristic markers for anti-bot interstitials.
_ANTIBOT_MARKERS: tuple[bytes, ...] = (
    b"Just a moment",
    b"cf-browser-verification",
    b"challenge-platform",
    b"__cf_chl",
    b"Attention Required! | Cloudflare",
)

# Clamp range for the user-controlled ``max_chars`` parameter.
_MAX_CHARS_MIN = 1024
_MAX_CHARS_MAX = 1_000_000
_MAX_CHARS_DEFAULT = 80_000

# Cap for redirect chains followed manually.
_MAX_REDIRECTS = 5


class _SSRFBlocked(Exception):
    """Генерируется, когда исходящий запрос блокируется SSRF-защитой."""


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _is_unsafe_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _check_ssrf(url: str, *, allow_internal: bool) -> str:
    """Проверяет *url* и возвращает литерал IP для подключения.

    Разрешение DNS здесь (и только здесь) делает инструмент устойчивым к
    DNS rebinding: вызывающий код должен подключиться к возвращённому IP, а не
    повторно разрешать FQDN.

    Returns:
        Литерал IP (строка IPv4 или IPv6) для подключения.

    Raises:
        _SSRFBlocked: если схема, хост или любой разрешённый IP запрещены.
    """
    parts = urlsplit(url)
    scheme = parts.scheme.lower()

    if scheme not in _ALLOWED_SCHEMES:
        raise _SSRFBlocked(
            f"схема '{scheme}' не разрешена (только http/https)"
        )

    host = (parts.hostname or "").lower()
    if not host:
        raise _SSRFBlocked("URL не содержит компонент хоста")

    # Cloud metadata is ALWAYS blocked, regardless of CAI_FETCH_ALLOW_INTERNAL.
    if host in _METADATA_HOSTS or host in _METADATA_IPS:
        raise _SSRFBlocked(f"хост '{host}' является эндпоинтом облачных метаданных")

    # Literal IP path.
    try:
        ip_obj = ipaddress.ip_address(host)
        if not allow_internal and _is_unsafe_ip(ip_obj):
            raise _SSRFBlocked(f"хост '{host}' является приватным/зарезервированным адресом")
        return host

    except ValueError:
        pass  # fall through to FQDN resolution

    # FQDN: resolve, validate every record, return the first safe IP.
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise _SSRFBlocked(f"не удалось разрешить хост '{host}': {exc}") from exc

    safe_ips: list[str] = []
    for info in infos:
        raw_addr = info[4][0]
        ip_str = str(raw_addr)  # getaddrinfo returns int for AF_UNIX edge cases
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if ip_str in _METADATA_IPS:
            raise _SSRFBlocked(
                f"хост '{host}' разрешается в облачный метаданный IP '{ip_str}'"
            )
        if not allow_internal and _is_unsafe_ip(ip):
            raise _SSRFBlocked(
                f"хост '{host}' разрешается в приватный/loopback/link-local '{ip_str}'"
            )
        safe_ips.append(ip_str)

    if not safe_ips:
        raise _SSRFBlocked(f"нет пригодных IP для хоста '{host}'")
    # Only the first safe A/AAAA record is returned; happy-eyeballs over the
    # remaining records is not implemented (the connection just fails if the
    # first IP is down). Adequate for read-the-web fetches; revisit if we
    # start using fetch_url against multi-homed hosts with flaky primaries.
    return safe_ips[0]


def _build_pinned_url(url: str, resolved_ip: str) -> tuple[str, str]:
    """Возвращает ``(pinned_url, original_host_header)``.

    Закреплённый URL заменяет FQDN на проверенный IP, чтобы httpx
    подключался к этому точному адресу. Заголовок Host по-прежнему содержит
    исходный FQDN, чтобы виртуальный хостинг работал и сертификат TLS
    проверялся по правильному имени. Если URL уже использовал литерал IP,
    URL возвращается без изменений.
    """
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if host == resolved_ip.lower():
        return url, parts.netloc

    ip_for_netloc = (
        f"[{resolved_ip}]" if ":" in resolved_ip else resolved_ip
    )
    netloc = (
        f"{ip_for_netloc}:{parts.port}" if parts.port else ip_for_netloc
    )
    pinned = urlunsplit(
        (parts.scheme, netloc, parts.path or "/", parts.query, parts.fragment)
    )
    return pinned, parts.netloc


def _looks_like_antibot(body: bytes, status: int) -> bool:
    if status in (403, 503):
        return True
    sample = body[:4096]
    return any(marker in sample for marker in _ANTIBOT_MARKERS)


def _default_headers(user_agent: str | None) -> dict[str, str]:
    return {
        "User-Agent": user_agent
        or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "application/pdf,application/json;q=0.9,*/*;q=0.5"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }


async def _fetch_httpx_pinned(
    url: str,
    resolved_ip: str,
    *,
    timeout: int,
    max_bytes: int,
    user_agent: str | None,
) -> tuple[bytes, str, int, str | None]:
    """Получает *url* по подключению к *resolved_ip* (безопасно от DNS rebinding).

    Возвращает ``(body, content_type, status, location)``. ``location`` — это
    заголовок ``Location`` при ответе 3xx; ``None`` в остальных случаях.
    """
    pinned_url, host_header = _build_pinned_url(url, resolved_ip)
    parts = urlsplit(url)

    headers = _default_headers(user_agent)
    headers["Host"] = host_header

    async with httpx.AsyncClient(
        follow_redirects=False,
        timeout=timeout,
        http2=False,
    ) as client:
        request = client.build_request("GET", pinned_url, headers=headers)
        if parts.scheme == "https" and parts.hostname:
            # Tell the TLS layer to use the original FQDN for SNI and cert
            # verification, even though we are dialing the IP literal.
            request.extensions["sni_hostname"] = parts.hostname

        resp = await client.send(request, stream=True)
        try:
            chunks: list[bytes] = []
            received = 0
            async for chunk in resp.aiter_bytes():
                chunks.append(chunk)
                received += len(chunk)
                if received >= max_bytes:
                    break
            body = b"".join(chunks)[:max_bytes]
            ctype = resp.headers.get("content-type", "").split(";", 1)[0].strip()
            status = resp.status_code
            location = (
                resp.headers.get("location")
                if 300 <= status < 400
                else None
            )
        finally:
            await resp.aclose()
    return body, ctype, status, location


def _fetch_curl_cffi_sync(
    url: str,
    resolved_ip: str,  # kept for API symmetry with the httpx path (see docstring)
    *,
    timeout: int,
    max_bytes: int,
    user_agent: str | None,
) -> tuple[bytes, str, int]:
    """Синхронный fallback с curl-cffi (TLS-отпечаток Chrome).

    Известное ограничение: высокоуровневый API curl-cffi не предоставляет ``--resolve``,
    поэтому этот путь fallback позволяет curl повторно разрешить FQDN. Мы принимаем
    более узкое окно DNS rebinding, потому что этот код выполняется только когда
    httpx столкнулся с антибот-проверкой И его собственная проверка SSRF (с закреплением IP)
    уже прошла для того же URL миллисекунды ранее.
    """
    from curl_cffi import requests as curl_requests  # local import (heavy)

    resp = curl_requests.get(
        url,
        impersonate="chrome124",
        timeout=timeout,
        allow_redirects=False,
        headers=_default_headers(user_agent),
    )
    body = resp.content[:max_bytes] if resp.content else b""
    ctype = resp.headers.get("content-type", "").split(";", 1)[0].strip()
    return body, ctype, resp.status_code


def _detect_kind(body: bytes, content_type: str) -> str:
    """Возвращает одно из: 'pdf', 'html', 'json', 'text', 'unknown'."""
    if body[:5] == b"%PDF-" or content_type == "application/pdf":
        return "pdf"
    if content_type.startswith("application/json"):
        return "json"
    if content_type.startswith("text/html") or content_type in {
        "application/xhtml+xml",
        "application/xml",
    }:
        return "html"
    if not content_type:
        stripped = body[:64].lstrip()
        if stripped[:1] in (b"{", b"["):
            try:
                json.loads(body.decode("utf-8", errors="replace"))
                return "json"
            except (ValueError, UnicodeDecodeError):
                pass
        if b"<html" in body[:1024].lower() or b"<!doctype html" in body[:1024].lower():
            return "html"
    if content_type.startswith("text/"):
        return "text"
    return "unknown"


def _decode_body(body: bytes, content_type: str) -> str:
    match = re.search(r"charset=([\w\-]+)", content_type, re.IGNORECASE)
    if match:
        try:
            return body.decode(match.group(1), errors="replace")
        except LookupError:
            pass
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return body.decode("latin-1", errors="replace")


# Phrases that strongly indicate the page is a JavaScript-required SPA
# or a frame-busting redirect, where the static HTML body contains no
# useful content for the LLM. Evidence from debug session ab1027:
# - NVD vuln/search returns 200 with body "You are viewing this page in
#   an unauthorized frame window. This is a potential security issue,
#   you are being redirected to ..."
# - cve.org SPA returns 200 with body "We're sorry but the CVE Website
#   doesn't work properly without JavaScript ..."
_JS_REQUIRED_PATTERNS: tuple[str, ...] = (
    "doesn't work properly without javascript",
    "please enable javascript",
    "javascript is required",
    "you need to enable javascript",
    "you are viewing this page in an unauthorized frame window",
    "this is a potential security issue, you are being redirected",
)

# URL → suggested alternative endpoint when fetch_url hits a JS-required
# wall. Keys are substrings matched against the original URL host/path.
_JS_FALLBACK_HINTS: tuple[tuple[str, str], ...] = (
    (
        "nvd.nist.gov/vuln",
        "Use the JSON API instead: "
        "https://services.nvd.nist.gov/rest/json/cves/2.0"
        "?keywordSearch=YOUR_TERM&resultsPerPage=20",
    ),
    (
        "cve.org",
        "Use the legacy MITRE search instead: "
        "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=YOUR_TERM",
    ),
)


def _detect_js_required(html_lower: str) -> str | None:
    """Возвращает обнаруженный индикатор, если страница зависит от JS, иначе None."""
    for needle in _JS_REQUIRED_PATTERNS:
        if needle in html_lower:
            return needle
    return None


def _build_js_required_message(url: str, indicator: str, body_size: int) -> str:
    suggestion = ""
    for key, hint in _JS_FALLBACK_HINTS:
        if key in url.lower():
            suggestion = f"\nРекомендация для этого хоста: {hint}\n"
            break
    if not suggestion:
        suggestion = (
            "\nРекомендация: найдите JSON/REST API эндпоинт, RSS/Atom "
            "ленту или статическую зеркальную копию документации этого ресурса.\n"
        )
    return (
        f"[fetch_url] {url}\n"
        f"# Статус: 200, но страница требует JavaScript для отображения полезного содержимого\n"
        f'# Обнаруженный паттерн: "{indicator}"\n'
        f"# Получено байт: {body_size}\n\n"
        "Этот URL предоставляет одностраничное приложение JavaScript или "
        "страницу с frame-busting перенаправлением. fetch_url не выполняет JavaScript, "
        "поэтому из этого URL не может быть извлечено полезное содержимое."
        f"{suggestion}"
    )


def _extract_html(body: bytes, content_type: str) -> str:
    import trafilatura  # local import to keep startup cost low

    html = _decode_body(body, content_type)
    md = trafilatura.extract(
        html,
        output_format="markdown",
        include_links=True,
        include_tables=True,
        include_formatting=True,
        favor_recall=True,
    )
    if md:
        return md
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "[пустой документ]"


def _extract_pdf(body: bytes) -> str:
    from pypdf import PdfReader  # local import

    reader = PdfReader(io.BytesIO(body))
    pages: list[str] = []
    for idx, page in enumerate(reader.pages, start=1):
        try:
            txt = page.extract_text() or ""
        except Exception:  # pylint: disable=broad-except
            txt = ""
        pages.append(f"## Page {idx}\n\n{txt.strip()}")
    return "\n\n".join(pages) if pages else "[пустой PDF]"


def _extract_json(body: bytes, content_type: str) -> str:
    text = _decode_body(body, content_type)
    try:
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except ValueError:
        return text


def _extract(body: bytes, content_type: str) -> str:
    kind = _detect_kind(body, content_type)
    if kind == "pdf":
        return _extract_pdf(body)
    if kind == "html":
        return _extract_html(body, content_type)
    if kind == "json":
        return _extract_json(body, content_type)
    if kind == "text":
        return _decode_body(body, content_type)
    return f"[Неподдерживаемый тип содержимого: {content_type or 'неизвестный'}]"


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    dropped = len(text) - max_chars
    return text[:max_chars] + f"\n\n[...обрезано {dropped} символов]"


def _clamp_max_chars(value: int) -> int:
    """Ограничивает ``max_chars`` безопасным диапазоном."""
    if value <= 0:
        return _MAX_CHARS_DEFAULT
    return max(_MAX_CHARS_MIN, min(value, _MAX_CHARS_MAX))


async def _fetch_with_redirects(
    url: str,
    *,
    allow_internal: bool,
    timeout: int,
    max_bytes: int,
    user_agent: str | None,
) -> tuple[bytes, str, int, str]:
    """Получает *url*, отслеживая до ``_MAX_REDIRECTS`` переходов вручную.

    Каждый переход повторно проверяется SSRF-защитой перед подключением. Возвращает
    ``(body, content_type, status, final_url)``.
    """
    current = url
    for _ in range(_MAX_REDIRECTS + 1):
        ip = _check_ssrf(current, allow_internal=allow_internal)
        body, ctype, status, location = await _fetch_httpx_pinned(
            current,
            ip,
            timeout=timeout,
            max_bytes=max_bytes,
            user_agent=user_agent,
        )
        if location and 300 <= status < 400:
            current = str(httpx.URL(current).join(location))
            continue
        return body, ctype, status, current
    raise _SSRFBlocked(f"слишком много перенаправлений с {url}")


@function_tool
async def fetch_url(
    url: str,
    max_chars: int = _MAX_CHARS_DEFAULT,
    timeout: int = 0,
) -> str:
    """Получает один URL и возвращает его основное содержимое, готовое для LLM.

    Используйте ПОСЛЕ веб-поиска (``make_google_search``,
    ``query_perplexity``) для чтения фактического содержимого результата.

    Поведение:

    * HTML-страницы преобразуются в Markdown с удалением навигации/рекламы.
    * PDF извлекаются как текст, по одной секции на страницу.
    * JSON-эндпоинты возвращаются форматированными.
    * Обычный текст передаётся как есть.
    * Если страница защищена базовой антибот-проверкой, вызов
      повторяется с использованием клиента с TLS-отпечатком Chrome.
    * Запросы к приватным / loopback / link-local / облачным метаданным хостам
      блокируются по умолчанию. Установите ``CAI_FETCH_ALLOW_INTERNAL=true`` для
      разрешения внутренних целей при авторизованном внутреннем тестировании.
    * Имена хостов разрешаются DNS ровно один раз, и полученный IP
      закрепляется для запроса, предотвращая DNS rebinding. Перенаправления
      отслеживаются вручную, чтобы каждый переход повторно проверялся.
    * JavaScript НЕ выполняется; одностраничные приложения, требующие
      клиентского рендеринга, вернут пустую оболочку.

    Args:
        url: HTTP или HTTPS URL для получения.
        max_chars: Жёсткий лимит возвращаемых символов (ограничено
            [1024, 1_000_000]; по умолчанию 80_000).
        timeout: Тайм-аут запроса в секундах. ``0`` использует ``CAI_FETCH_TIMEOUT``
            (по умолчанию 20с).

    Returns:
        Извлечённое содержимое, обёрнутое в разделители внешнего содержимого CAI
        для нейтрализации встроенных полезных нагрузок инъекции подсказок.
        Ошибки возвращаются как очищенные строки; эта функция никогда не
        генерирует исключения.
    """
    allow_internal = _bool_env("CAI_FETCH_ALLOW_INTERNAL", False)
    max_bytes = _int_env("CAI_FETCH_MAX_BYTES", 5_242_880)
    effective_timeout = timeout if timeout > 0 else _int_env("CAI_FETCH_TIMEOUT", 20)
    user_agent = os.getenv("CAI_FETCH_USER_AGENT") or None
    clamped_chars = _clamp_max_chars(max_chars)

    try:
        body, ctype, status, final_url = await _fetch_with_redirects(
            url,
            allow_internal=allow_internal,
            timeout=effective_timeout,
            max_bytes=max_bytes,
            user_agent=user_agent,
        )
    except _SSRFBlocked as exc:
        return sanitize_external_content(
            f"[fetch_url заблокирован] {exc}. "
            "Установите CAI_FETCH_ALLOW_INTERNAL=true для разрешения внутренних целей."
        )
    except Exception as exc:  # pylint: disable=broad-except
        return sanitize_external_content(
            f"[fetch_url ошибка] httpx не удался: {type(exc).__name__}: {exc}"
        )

    # Anti-bot fallback. We re-validate SSRF on the final URL just in case
    # the redirect chain changed the host.
    if _looks_like_antibot(body, status):
        try:
            ip = _check_ssrf(final_url, allow_internal=allow_internal)
            body2, ctype2, status2 = await asyncio.to_thread(
                _fetch_curl_cffi_sync,
                final_url,
                ip,
                timeout=effective_timeout,
                max_bytes=max_bytes,
                user_agent=user_agent,
            )
            if not _looks_like_antibot(body2, status2):
                body, ctype, status = body2, ctype2, status2
        except Exception:  # pylint: disable=broad-except
            pass  # keep original 4xx/5xx response

    if status >= 400:
        return sanitize_external_content(
            f"[fetch_url] HTTP {status} для {url}. "
            f"Предварительный просмотр тела:\n\n{_extract(body, ctype)[:2000]}"
        )

    # Detect JS-required pages / frame-busting redirects on text/html responses.
    # These return HTTP 200 with a body that contains no useful content,
    # so we short-circuit with a clear error pointing the LLM to alternatives.
    if (ctype or "").lower().startswith("text/html"):
        html_lower = _decode_body(body, ctype).lower()
        js_indicator = _detect_js_required(html_lower)
        if js_indicator:
            return sanitize_external_content(
                _build_js_required_message(final_url, js_indicator, len(body))
            )

    extracted = _truncate(_extract(body, ctype), clamped_chars)

    header = (
        f"# Получено: {final_url}\n"
        f"# Статус: {status}\n"
        f"# Content-Type: {ctype or 'неизвестный'}\n"
        f"# Байты: {len(body)}\n\n"
    )
    return sanitize_external_content(header + extracted)


# --- Auto-register with ToolRegistry ---
# Registered under "misc" so every agent type (red, blue, bugbounty, purple,
# dfir, plus the default fallback) gets access. Also under "recon" and "web"
# for category-targeted lookups.
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402

TOOL_REGISTRY.register("fetch_url", fetch_url, categories=["recon", "web", "misc"])
