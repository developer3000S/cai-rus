"""
Команда использования контекста для CAI REPL (CLI).

Предоставляет вид, аналогичный Claude-Code, показывающий, куда расходуются токены контекста.
Это приблизительная оценка: использование у провайдера может отличаться в зависимости от токенизатора/модели.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cai.repl.commands.base import Command, register_command
from cai.repl.ui.banner import _CAI_GREEN
from cai.sdk.agents.models.openai_chatcompletions import get_current_active_model
from cai.sdk.agents.models.chatcompletions.token_counter import count_tokens_with_tiktoken
from cai.util.tokens import get_model_input_tokens


console = Console(highlight=False)
_Z = _CAI_GREEN
_M = "#9aa0a6"


def _extract_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif "text" in item:
                    parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join([p for p in parts if p])
    return str(content)


def _msg_token_estimate(msg: dict) -> int:
    # Approximate per-message token usage by counting role + content only.
    # The full request includes additional overhead (format/tool schemas/system prompt).
    role = str(msg.get("role", ""))
    content = _extract_text(msg.get("content"))
    role_tok, _ = count_tokens_with_tiktoken(role)
    content_tok, _ = count_tokens_with_tiktoken(content)
    return int(role_tok + content_tok)


@dataclass(frozen=True)
class _RoleStats:
    messages: int
    tokens: int


class ContextCommand(Command):
    def __init__(self) -> None:
        super().__init__(
            name="/context",
            description="Показать, куда расходуются токены контекста",
            aliases=["/ctx"],
        )
        self.add_subcommand("top", "Показать самые тяжёлые сообщения контекста", self.handle_top)
        self.add_subcommand(
            "trim",
            "Детерминированно обрезать старые выводы инструментов (без суммаризации)",
            self.handle_trim,
        )

    def handle(self, args: Optional[List[str]] = None) -> bool:
        if not args:
            return self.handle_summary()
        sub = (args[0] or "").strip().lower()
        if sub in self.subcommands:
            handler = self.subcommands[sub]["handler"]
            return handler(args[1:] if len(args) > 1 else [])
        return self.handle_summary()

    def handle_summary(self, args: Optional[List[str]] = None) -> bool:
        model_inst = get_current_active_model()
        if model_inst is None:
            console.print(f"[yellow]Активный экземпляр модели не найден.[/yellow]")
            console.print(f"[dim {_M}]Сначала отправьте запрос, затем попробуйте /context снова.[/dim {_M}]")
            return True

        model_name = str(getattr(model_inst, "model", "") or "")
        history = list(getattr(model_inst, "message_history", []) or [])

        # Per-role breakdown
        by_role: dict[str, Tuple[int, int]] = {}  # role -> (msgs, toks)
        total_est = 0
        for msg in history:
            if not isinstance(msg, dict):
                continue
            role = str(msg.get("role", "unknown") or "unknown")
            tok = _msg_token_estimate(msg)
            total_est += tok
            m, t = by_role.get(role, (0, 0))
            by_role[role] = (m + 1, t + tok)

        max_tokens = int(get_model_input_tokens(model_name) or 0)
        pct = (total_est / max_tokens * 100.0) if max_tokens > 0 else 0.0

        table = Table(
            title=f"[bold {_Z}]Разбивка контекста[/bold {_Z}]",
            box=box.ROUNDED,
            header_style=f"bold {_M}",
            show_header=True,
        )
        table.add_column("Роль", style=f"bold {_Z}", no_wrap=True)
        table.add_column("Сообщения", justify="right")
        table.add_column("Примерно токенов", justify="right")
        table.add_column("Доля", justify="right")

        def _share(tok: int) -> str:
            if total_est <= 0:
                return "—"
            return f"{(tok / total_est) * 100:5.1f}%"

        for role in ("system", "user", "assistant", "tool", "developer", "unknown"):
            if role not in by_role:
                continue
            msgs, tok = by_role[role]
            table.add_row(role, str(msgs), f"{tok:,}", _share(tok))

        # Any other roles
        for role in sorted(set(by_role.keys()) - {"system", "user", "assistant", "tool", "developer", "unknown"}):
            msgs, tok = by_role[role]
            table.add_row(role, str(msgs), f"{tok:,}", _share(tok))

        summary = Text()
        summary.append("Модель: ", style=f"dim {_M}")
        summary.append(model_name or "(unknown)", style="bold white")
        summary.append("\nПримерный контекст: ", style=f"dim {_M}")
        summary.append(f"{total_est:,} tokens", style="bold white")
        summary.append(" / ", style=f"dim {_M}")
        summary.append(f"{max_tokens:,}" if max_tokens else "unknown", style="bold white")
        summary.append("  (", style=f"dim {_M}")
        summary.append(f"{pct:.1f}%", style="bold white")
        summary.append(")\n", style=f"dim {_M}")
        summary.append(
            "Примечание: этот вид учитывает только роль+содержимое сообщения. Системные подсказки, схемы инструментов и "
            "специфичная для провайдера токенизация могут добавить значительные накладные расходы.",
            style=f"dim {_M}",
        )

        # Actionable hints (best-effort)
        hints: list[str] = []
        tool_tok = by_role.get("tool", (0, 0))[1] if "tool" in by_role else 0
        if total_est > 0 and (tool_tok / total_est) >= 0.4:
            hints.append("Выводы инструментов доминируют. Попробуйте: /context top, затем /context trim.")
        if pct >= 80:
            hints.append("Вы приближаетесь к лимиту контекста. Попробуйте: /compact (суммаризация) или /context trim (только инструменты).")
        if not hints and pct >= 50:
            hints.append("Если использование токенов растёт быстро, используйте: /context top для поиска тяжёлых сообщений.")

        console.print()
        if hints:
            hint_text = Text()
            hint_text.append("Рекомендации:\n", style=f"bold {_Z}")
            for h in hints:
                hint_text.append(f"• {h}\n", style=f"dim {_M}")
            console.print(
                Panel(
                    Text.assemble(summary, "\n\n", hint_text),
                    border_style=_Z,
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )
        else:
            console.print(Panel(summary, border_style=_Z, box=box.ROUNDED, padding=(1, 2)))
        console.print(table)
        console.print(
            f"\n[dim {_M}]Попробуйте '/context top', чтобы увидеть самые большие сообщения (обычно выводы инструментов).[/dim {_M}]"
        )
        return True

    def handle_top(self, args: Optional[List[str]] = None) -> bool:
        model_inst = get_current_active_model()
        if model_inst is None:
            console.print(f"[yellow]No active model instance found.[/yellow]")
            return True

        n = 8
        if args:
            try:
                n = max(1, min(50, int(args[0])))
            except Exception:
                n = 8

        history = list(getattr(model_inst, "message_history", []) or [])
        scored: list[tuple[int, dict]] = []
        for msg in history:
            if isinstance(msg, dict):
                scored.append((_msg_token_estimate(msg), msg))
        scored.sort(key=lambda x: x[0], reverse=True)

        table = Table(
            title=f"[bold {_Z}]Топ {min(n, len(scored))} сообщений по оценке токенов[/bold {_Z}]",
            box=box.ROUNDED,
            header_style=f"bold {_M}",
            show_header=True,
        )
        table.add_column("#", justify="right", style=f"dim {_M}")
        table.add_column("Роль", style=f"bold {_Z}", no_wrap=True)
        table.add_column("Примерно токенов", justify="right")
        table.add_column("Предпросмотр", overflow="fold")

        for i, (tok, msg) in enumerate(scored[:n], start=1):
            role = str(msg.get("role", "unknown") or "unknown")
            text = _extract_text(msg.get("content", ""))
            preview = " ".join(text.strip().split())
            if len(preview) > 240:
                preview = preview[:237] + "…"
            table.add_row(str(i), role, f"{tok:,}", preview or "[dim](empty)[/dim]")

        console.print()
        console.print(table)
        return True

    def handle_trim(self, args: Optional[List[str]] = None) -> bool:
        """Trim old tool outputs deterministically (no LLM call)."""
        model_inst = get_current_active_model()
        if model_inst is None:
            console.print(f"[yellow]Активный экземпляр модели не найден.[/yellow]")
            return True

        max_chars = 800
        keep_recent = 12
        if args:
            # Simple parsing: /context trim [max_chars] [keep_recent]
            if len(args) >= 1:
                try:
                    max_chars = int(args[0])
                except Exception:
                    max_chars = 800
            if len(args) >= 2:
                try:
                    keep_recent = int(args[1])
                except Exception:
                    keep_recent = 12

        history = getattr(model_inst, "message_history", None)
        if not isinstance(history, list) or not history:
            console.print(f"[yellow]Нет истории сообщений для обрезки.[/yellow]")
            return True

        # Import the same phase-1 truncator used by auto-compactor for consistent behaviour.
        from cai.sdk.agents.models.chatcompletions.auto_compactor import (
            _phase1_truncate_message_history as _truncate_phase1,
        )

        keep_start = max(0, len(history) - max(1, keep_recent))
        before = sum(_msg_token_estimate(m) for m in history if isinstance(m, dict))
        truncated_count, tokens_saved = _truncate_phase1(history, keep_start=keep_start, max_chars=max_chars)
        after = sum(_msg_token_estimate(m) for m in history if isinstance(m, dict))

        # Persist ratio for footer/toolbar.
        try:
            model_name = str(getattr(model_inst, "model", "") or "")
            max_tokens = int(get_model_input_tokens(model_name) or 0)
            if max_tokens > 0:
                import os

                os.environ["CAI_CONTEXT_USAGE"] = str(min(1.0, max(0.0, after / max_tokens)))
        except Exception:
            pass

        console.print()
        console.print(
            Panel(
                f"[bold {_Z}]Обрезка выводов инструментов завершена[/bold {_Z}]\n\n"
                f"[{_M}]Обрезано выводов:[/] [white]{truncated_count}[/white]\n"
                f"[{_M}]Примерно токенов до:[/] [white]{before:,}[/white]\n"
                f"[{_M}]Примерно токенов после:[/]  [white]{after:,}[/white]\n"
                f"[{_M}]Примерно токенов освобождено:[/]  [white]{max(0, before - after):,}[/white]\n"
                f"[dim {_M}]Примечание: tokens_saved — быстрая оценка, используемая компоновщиком; до/после — оценки по роли+содержимому.[/dim {_M}]",
                border_style=_Z,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        return True


register_command(ContextCommand())

