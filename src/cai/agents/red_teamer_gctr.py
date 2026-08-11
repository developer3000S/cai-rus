"""Агент Red Team с интеграцией игро-теоретического CTR (Cut The Rope).

Тонкая обёртка: клонирует базовый агент red_teamer и подключает CTRHooks.
"""

from typing import Optional

from cai.agents.gctr_mixin import make_gctr_agent
from cai.agents.red_teamer import redteam_agent as _base_agent

_GCTR_KWARGS = dict(
    name="Red Team GCTR",
    description=(
        "Red team agent with integrated game-theoretic security analysis. "
        "Automatically runs CTR (Cut The Rope) analysis every few interactions "
        "to assess defender/attacker strategies and equilibrium."
    ),
    team_label="Red Team",
)

# Экземпляр по умолчанию
redteam_gctr_agent = make_gctr_agent(_base_agent, **_GCTR_KWARGS)


def create_redteam_gctr_agent(n_interactions: Optional[int] = None):
    """Создаёт агент Red Team GCTR (фабрика с обратной совместимостью)."""
    return make_gctr_agent(_base_agent, n_interactions=n_interactions, **_GCTR_KWARGS)


def transfer_to_redteam_gctr_agent(**kwargs):
    """Передача управления агенту red team GCTR."""
    return redteam_gctr_agent
