"""Централизованная конфигурация CAI.

Единый источник правды для всей конфигурации.
Заменяет 936 рассеянных вызовов os.getenv() в 137 файлах.

Создано в Day 0 как общий контракт между 3 потоками рефакторинга.
- Поток 2 (Foundation): реализует from_env() и validate()
- Поток 1 (Core Engine): потребляет для настроек LLM/инструментов
- Поток 3 (Interface): потребляет для настроек TUI/REPL
"""

from enum import Enum
from dataclasses import dataclass
from typing import Final, Optional, List
import os
import warnings

from .auth_types import Edition, Role

_LEGACY_COMPACTED_MEMORY_WARNED = False

# Автоматическое сжатие никогда не ждёт дольше этой доли окна контекста модели,
# даже если CAI_AUTO_COMPACT_THRESHOLD установлен выше (пользователи всё ещё
# могут установить меньшее значение).
AUTO_COMPACT_THRESHOLD_MAX: Final[float] = 0.8

DEFAULT_AGENT_TYPE: Final[str] = "selection_agent"
ORCHESTRATION_AGENT_TYPE: Final[str] = "orchestration_agent"


def _parse_inf(value: str) -> int | float:
    if value.lower() in ("inf", "infinite", "infinity", "unlimited"):
        return float("inf")
    return int(value)


def _parse_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")


def compacted_memory_env_enabled() -> bool:
    """Включены ли сводки /compact из REPL для внедрения в системные подсказки агента.

    Читает ``CAI_COMPACTED_MEMORY`` если установлено; в противном случае использует
    устаревшее ``CAI_MEMORY`` (deprecated) на один выпуск.
    """
    global _LEGACY_COMPACTED_MEMORY_WARNED  # pylint: disable=global-statement
    if "CAI_COMPACTED_MEMORY" in os.environ:
        return _parse_bool(os.getenv("CAI_COMPACTED_MEMORY", "false"))
    legacy = os.getenv("CAI_MEMORY", "").strip().lower()
    if legacy in ("true", "1", "yes", "episodic", "semantic", "all"):
        if not _LEGACY_COMPACTED_MEMORY_WARNED:
            warnings.warn(
                "CAI_MEMORY устарел для компактной памяти сессий; установите "
                "CAI_COMPACTED_MEMORY=true. Поддержка устаревшего CAI_MEMORY будет "
                "удалена в будущем выпуске.",
                DeprecationWarning,
                stacklevel=2,
            )
            _LEGACY_COMPACTED_MEMORY_WARNED = True
        return True
    return False


@dataclass
class CAIConfig:
    """Полная конфигурация CAI, загружаемая один раз при запуске."""

    # --- Модель и агент ---
    model: str = "alias1"
    agent_type: str = DEFAULT_AGENT_TYPE
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int | None = None
    reasoning_effort: str | None = None

    # --- Лимиты ---
    max_turns: int | float = float("inf")
    max_interactions: int | float = float("inf")
    price_limit: float = 1.0

    # --- Стриминг ---
    stream: bool = False
    tool_stream: bool = True

    # --- Параллелизм ---
    parallel: int = 1

    # --- Компактная память сессий (/compact) ---
    compacted_memory: bool = False

    # --- Отладка и логирование ---
    debug: int = 1
    debug_pricing: bool = False
    tracing: bool = True
    telemetry: bool = True

    # --- Автоматическое сжатие ---
    auto_compact: bool = True
    # Сжимать когда контекст превышает эту долю окна модели.
    auto_compact_threshold: float = 0.8

    # --- Безопасность ---
    guardrails: bool = False
    tool_timeout: int = 120

    # --- TUI ---
    tui_enabled: bool = True
    tui_mode: str = "default"
    tui_theme: str = "tokyo-night"
    tui_startup_yaml: str | None = None
    tui_shared_prompt: str | None = None

    # --- CTF ---
    ctf_name: str | None = None
    ctf_challenge: str | None = None

    # --- Планирование ---
    plan_enabled: bool = False

    # --- Оркестрация (воркеры, создаваемые инструментами orchestration_agent) ---
    orchestration_worker_max_turns: int = 6
    orchestration_mas_hint: bool = True

    # --- Реестр инструментов ---
    # Если True, ToolRegistry автоматически дополняет инструменты агента на основе
    # отображения категорий по типу агента. По умолчанию отключено для минимизации
    # использования токенов (каждая дополнительная схема инструмента стоит ~120-150
    # токенов подсказки за ход).
    tool_registry_auto: bool = False

    # --- Продолжение ---
    continuation_fallback_model: str | None = None

    # --- Поиск ---
    google_search_api_key: str | None = None
    google_search_cx: str | None = None

    # --- Веб-загрузка (инструмент fetch_url) ---
    # Политика SSRF: по умолчанию инструмент fetch_url блокирует loopback, RFC1918,
    # link-local и cloud-metadata хосты для предотвращения подделки запросов
    # на стороне сервера через инъекцию подсказок. Установите CAI_FETCH_ALLOW_INTERNAL=true
    # для разрешения внутренних целей (например, при пентесте внутренней сети).
    fetch_allow_internal: bool = False
    fetch_user_agent: str | None = None  # CAI_FETCH_USER_AGENT (переопределение OPSEC)
    fetch_max_bytes: int = 5_242_880  # CAI_FETCH_MAX_BYTES (лимит ответа 5 МБ)
    fetch_timeout: int = 20  # CAI_FETCH_TIMEOUT (секунды)

    # --- Рабочее пространство ---
    workspace_dir: str | None = None  # Переопределение CAI_WORKSPACE_DIR
    workspace_name: str | None = None  # Именованное рабочее пространство CAI_WORKSPACE

    # --- Ключи API (не логируются) ---
    alias_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    perplexity_api_key: str | None = None
    c99_api_key: str | None = None
    shodan_api_key: str | None = None
    admin_password: str | None = None

    # --- Виртуализация ---
    active_container: str | None = None
    default_docker_image: str = "kalilinux/kali-rolling"

    # --- SSH ---
    ssh_user: str | None = None
    ssh_host: str | None = None

    # --- CTF runtime ---
    ctf_inside: bool = True  # CTF_INSIDE: выполнять ли инструменты внутри контейнера CTF

    # --- Сессия ---
    session_input_wait: float = 5.0  # CAI_SESSION_INPUT_WAIT: секунды ожидания ввода

    # --- Обход LiteLLM ---
    force_httpx: bool = False  # Если True, ВСЕ модели совместимые с OpenAI используют httpx напрямую

    # --- Ollama ---
    ollama_url: str | None = None

    # --- API-сервер ---
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = False
    api_workers: int = 1

    # --- Широковещание (параллельный TUI) ---
    broadcast_mode: bool = False

    # --- Автоматизация ---
    auto_run_queue: bool = False
    auto_run_parallel: bool = False
    queue_file: str | None = None
    pattern_description: str = ""

    @classmethod
    def from_env(cls) -> CAIConfig:
        """Загрузить всю конфигурацию из переменных окружения. Вызывается ОДИН раз."""
        # Determine edition first to apply constraints
        from .auth_types import Edition
        
        def _get_edition() -> Edition:
            if os.getenv("CAI_LICENSE_OFF", "").strip().lower() in ("1", "true", "yes"):
                return Edition.COMMUNITY
            if os.getenv("ALIAS_API_KEY"):
                return Edition.PROFESSIONAL
            return Edition.COMMUNITY

        edition = _get_edition()
        
        parallel = int(os.getenv("CAI_PARALLEL", "1"))
        if edition == Edition.COMMUNITY:
            parallel = 1

        return cls(
            model=os.getenv("CAI_MODEL", "alias1"),
            agent_type=os.getenv("CAI_AGENT_TYPE", DEFAULT_AGENT_TYPE),
            temperature=float(os.getenv("CAI_TEMPERATURE", "0.7")),
            top_p=float(os.getenv("CAI_TOP_P", "1.0")),
            max_tokens=(
                int(os.getenv("CAI_MAX_TOKENS"))
                if os.getenv("CAI_MAX_TOKENS")
                else None
            ),
            reasoning_effort=os.getenv("CAI_REASONING_EFFORT"),
            max_turns=_parse_inf(os.getenv("CAI_MAX_TURNS", "inf")),
            max_interactions=_parse_inf(os.getenv("CAI_MAX_INTERACTIONS", "inf")),
            price_limit=float(os.getenv("CAI_PRICE_LIMIT", "1")),
            auto_compact=_parse_bool(os.getenv("CAI_AUTO_COMPACT", "true")),
            auto_compact_threshold=min(
                float(os.getenv("CAI_AUTO_COMPACT_THRESHOLD", "0.8")),
                AUTO_COMPACT_THRESHOLD_MAX,
            ),
            stream=_parse_bool(os.getenv("CAI_STREAM", "false")),
            tool_stream=_parse_bool(os.getenv("CAI_TOOL_STREAM", "true")),
            parallel=parallel,
            compacted_memory=compacted_memory_env_enabled(),
            debug=int(os.getenv("CAI_DEBUG", "1")),
            debug_pricing=os.getenv("CAI_DEBUG_PRICING", "0") == "1",
            tracing=_parse_bool(os.getenv("CAI_TRACING", "true")),
            telemetry=os.getenv("CAI_TELEMETRY", "true").lower() != "false",
            guardrails=_parse_bool(os.getenv("CAI_GUARDRAILS", "false")),
            tool_timeout=int(os.getenv("CAI_TOOL_TIMEOUT", "120")),
            tui_enabled=_parse_bool(os.getenv("CAI_TUI", "true")),
            tui_mode=os.getenv("CAI_TUI_MODE", "default"),
            tui_theme=os.getenv("CAI_THEME", "tokyo-night"),
            tui_startup_yaml=os.getenv("CAI_TUI_STARTUP_YAML"),
            tui_shared_prompt=os.getenv("CAI_TUI_SHARED_PROMPT"),
            ctf_name=os.getenv("CTF_NAME"),
            ctf_challenge=os.getenv("CTF_CHALLENGE"),
            plan_enabled=_parse_bool(os.getenv("CAI_PLAN", "false")),
            orchestration_worker_max_turns=int(
                os.getenv("CAI_ORCHESTRATION_WORKER_MAX_TURNS", "6")
            ),
            orchestration_mas_hint=_parse_bool(os.getenv("CAI_ORCHESTRATION_MAS_HINT", "true")),
            tool_registry_auto=_parse_bool(os.getenv("CAI_TOOL_REGISTRY_AUTO", "false")),
            continuation_fallback_model=os.getenv("CAI_CONTINUATION_FALLBACK_MODEL"),
            google_search_api_key=os.getenv("GOOGLE_SEARCH_API_KEY"),
            google_search_cx=os.getenv("GOOGLE_SEARCH_CX"),
            fetch_allow_internal=_parse_bool(
                os.getenv("CAI_FETCH_ALLOW_INTERNAL", "false")
            ),
            fetch_user_agent=os.getenv("CAI_FETCH_USER_AGENT"),
            fetch_max_bytes=int(os.getenv("CAI_FETCH_MAX_BYTES", "5242880")),
            fetch_timeout=int(os.getenv("CAI_FETCH_TIMEOUT", "20")),
            workspace_dir=os.getenv("CAI_WORKSPACE_DIR"),
            workspace_name=os.getenv("CAI_WORKSPACE"),
            alias_api_key=os.getenv("ALIAS_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
            c99_api_key=os.getenv("C99_API_KEY"),
            shodan_api_key=os.getenv("SHODAN_API_KEY"),
            admin_password=os.getenv("CAI_ADMIN_PASSWORD"),
            active_container=os.getenv("CAI_ACTIVE_CONTAINER"),
            default_docker_image=os.getenv(
                "CAI_DOCKER_IMAGE", "kalilinux/kali-rolling"
            ),
            ssh_user=os.getenv("SSH_USER"),
            ssh_host=os.getenv("SSH_HOST"),
            ctf_inside=_parse_bool(os.getenv("CTF_INSIDE", "true")),
            session_input_wait=float(os.getenv("CAI_SESSION_INPUT_WAIT", "5.0")),
            force_httpx=_parse_bool(os.getenv("CAI_FORCE_HTTPX", "false")),
            ollama_url=os.getenv("CAI_OLLAMA_URL"),
            api_host=os.getenv("CAI_API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("CAI_API_PORT", "8000")),
            api_reload=os.getenv("CAI_API_RELOAD", "false").lower() == "true",
            api_workers=int(os.getenv("CAI_API_WORKERS", "1")),
            broadcast_mode=_parse_bool(os.getenv("CAI_BROADCAST_MODE", "false")),
            auto_run_queue=os.getenv("CAI_AUTO_RUN_QUEUE") == "1",
            auto_run_parallel=os.getenv("CAI_AUTO_RUN_PARALLEL") == "1",
            queue_file=os.getenv("CAI_QUEUE_FILE"),
            pattern_description=os.getenv("CAI_PATTERN_DESCRIPTION", ""),
        )

    def validate(self) -> list[str]:
        """Вернуть список предупреждений валидации. Пустой = всё в порядке."""
        warnings = []
        if self.price_limit <= 0:
            warnings.append("CAI_PRICE_LIMIT должен быть > 0")
        if not (0 <= self.temperature <= 2):
            warnings.append("CAI_TEMPERATURE должен быть от 0 до 2")
        if not (0 <= self.top_p <= 1):
            warnings.append("CAI_TOP_P должен быть от 0 до 1")
        if self.parallel < 1:
            warnings.append("CAI_PARALLEL должен быть >= 1")
        if not (1 <= self.orchestration_worker_max_turns <= 32):
            warnings.append("CAI_ORCHESTRATION_WORKER_MAX_TURNS должен быть от 1 до 32")
        if self.tool_timeout < 1:
            warnings.append("CAI_TOOL_TIMEOUT должен быть >= 1")
        if self.debug not in (0, 1, 2):
            warnings.append("CAI_DEBUG должен быть 0, 1 или 2")
        _ac_env = os.getenv("CAI_AUTO_COMPACT_THRESHOLD")
        if _ac_env is not None:
            try:
                if float(_ac_env) > AUTO_COMPACT_THRESHOLD_MAX + 1e-9:
                    cap = f"{AUTO_COMPACT_THRESHOLD_MAX:.0%}"
                    warnings.append(
                        f"CAI_AUTO_COMPACT_THRESHOLD выше {cap} ограничен до {cap}; "
                        "автоматическое сжатие не будет отложено за эту отметку."
                    )
            except ValueError:
                pass
        return warnings


# ---------------------------------------------------------------------------
# Синглтон модуля — загружается один раз, доступен везде через:
#   from cai.config import get_config
# ---------------------------------------------------------------------------
_CONFIG: CAIConfig | None = None


def get_config() -> CAIConfig:
    """Вернуть глобальный синглтон CAIConfig (ленивая загрузка из окружения при первом вызове)."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = CAIConfig.from_env()
    return _CONFIG


def get_active_edition() -> Edition:
    """
    Determine the active edition of the framework.
    
    - If CAI_LICENSE_OFF is true, it's Community Edition.
    - If ALIAS_API_KEY is present and valid, it's Professional Edition.
    - Otherwise, default to Community Edition.
    """
    if os.getenv("CAI_LICENSE_OFF", "").strip().lower() in ("1", "true", "yes"):
        return Edition.COMMUNITY
    
    # Check if a valid ALIAS_API_KEY is set
    if os.getenv("ALIAS_API_KEY"):
        return Edition.PROFESSIONAL
        
    return Edition.COMMUNITY
