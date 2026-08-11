"""Консервативные интервалы тиков на основе уровней TPM/RPM в стиле Alias (без анализа ключей)."""

from __future__ import annotations

import os


def resolve_rate_tier() -> str:
    """Возвращает ``pro`` или ``edu`` из ``CAI_ALIAS_RATE_TIER`` (по умолчанию: ``pro``)."""
    raw = (os.getenv("CAI_ALIAS_RATE_TIER") or "pro").strip().lower()
    if raw in ("edu", "education", "educational", "student"):
        return "edu"
    return "pro"


def get_rate_limits(tier: str | None = None) -> tuple[int, int]:
    """Возвращает ``(tokens_per_minute, requests_per_minute)`` для данного уровня."""
    t = (tier or resolve_rate_tier()).lower()
    if t == "edu":
        return 150_000, 20
    return 500_000, 60


def compute_base_tick_seconds(
    estimated_tokens_per_iteration: int,
    tier: str | None = None,
) -> float:
    """Нижняя граница секунд между итерациями для снижения риска ошибки 429 (эвристика).

    Использует более строгое из двух значений:
    - интервал, вычисленный из RPM (с запасом),
    - интервал, вычисленный из TPM по отношению к оценочным токенам на итерацию (с запасом).
    """
    tpm, rpm = get_rate_limits(tier)
    est = max(int(estimated_tokens_per_iteration), 256)
    from_rpm = (60.0 / float(max(rpm, 1))) * 1.25
    from_tpm = (float(est) / float(max(tpm, 1))) * 60.0 * 1.25
    return max(1.0, from_rpm, from_tpm)


def min_allowed_tick_seconds(
    estimated_tokens_per_iteration: int,
    tier: str | None = None,
) -> float:
    """Минимальный пользовательский тик согласно правилу продукта ``1.75 * base_time``."""
    return 1.75 * compute_base_tick_seconds(estimated_tokens_per_iteration, tier=tier)
