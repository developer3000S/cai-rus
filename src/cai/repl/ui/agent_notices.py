"""REPL notices for agent selection (orchestration BETA badge, etc.)."""

from __future__ import annotations

from rich.text import Text

from cai.config import ORCHESTRATION_AGENT_TYPE


def is_orchestration_agent(agent_key: str) -> bool:
    """Return True when *agent_key* is the orchestration entry agent."""
    return (agent_key or "").strip() == ORCHESTRATION_AGENT_TYPE


def orchestration_beta_badge_markup() -> str:
    """Compact Rich markup for the BETA badge (matches unrestricted mode style)."""
    return "[bold white on bright_red] BETA [/]"


def orchestration_beta_text() -> Text:
    """Multi-line Rich text for session banner when orchestration is active."""
    return Text.from_markup(
        "[bold yellow]Агент оркестрации[/bold yellow] "
        f"{orchestration_beta_badge_markup()} "
        "[dim]— экспериментальный breadth-first делегирование "
        "(run_specialist, contest, parallel scouts). "
        "Для стабильной маршрутизации передач используйте selection_agent.[/dim]"
    )


def orchestration_beta_panel_line() -> str:
    """Single plain line for /agent current panel content."""
    return (
        "Агент оркестрации [BETA] — экспериментальный breadth-first делегирование "
        "(run_specialist, contest, parallel scouts). "
        "Для стабильной маршрутизации передач используйте selection_agent."
    )


def orchestration_beta_name_suffix() -> Text:
    """Suffix for /agent list Name column."""
    return Text.from_markup(f" {orchestration_beta_badge_markup()}")
