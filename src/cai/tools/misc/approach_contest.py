"""Инструменты конкурса двух подходов, параллельных специалистов и одного специалиста.

Этот модуль предоставляет точки входа ``@function_tool``, используемые
агентом оркестрации (``cai.agents.orchestration_agent``):

* :func:`run_dual_approach_contest` — два параллельных исследовательских
  воркера для одной задачи пользователя (конкурирующие гипотезы или
  ортогональные рамки).
* :func:`run_parallel_specialists` — от двух до четырёх специалистов
  параллельно для независимых подзадач.
* :func:`run_specialist` — один специалист, при этом оркестратор остаётся
  под контролем.

Все используют один общий внутренний конвейер (поиск агента → клонирование
с не более чем одним допустимым инструментом → запуск с отключённым
отображением → оборачивание вывода как черновых данных только для
оркестратора). Общая инфраструктура использует :class:`WorkerSpec`,
:class:`WorkerResult` и :func:`_compose_contest_brief`, чтобы каждый
инструмент возвращал одинаковый каркас разметки.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass
from typing import Any, Final, Literal

from cai.sdk.agents import RunConfig, Runner
from cai.sdk.agents.items import ItemHelpers
from cai.sdk.agents.model_settings import ModelSettings
from cai.sdk.agents.tool import function_tool
from cai.config import get_config
from cai.util._worker_silence import silence_worker_display

# === Constants ============================================================

def _configured_worker_max_turns() -> int:
    """Runner max_turns for each specialist worker (env ``CAI_ORCHESTRATION_WORKER_MAX_TURNS``)."""
    try:
        n = int(get_config().orchestration_worker_max_turns)
    except (TypeError, ValueError, AttributeError):
        n = 6
    return max(1, min(n, 32))


def _worker_constraints_prefix(max_turns: int) -> str:
    """Worker-facing budget text; ``max_turns`` matches ``Runner.run(..., max_turns=...)``."""
    n = max(1, int(max_turns))
    return (
        "## Ограничения конкурса (обязательно)\n"
        f"- У вас не более **{n} ходов** всего за этот запуск (каждый ход = один шаг модели, "
        "включая вызовы инструментов).\n"
        "- Используйте **не более одного вызова инструмента за ход** "
        "(предпочтительно ноль, если можете ответить на основе рассуждений).\n"
        "- Оставайтесь в рамках ниже; не начинайте вложенный конкурс двух подходов.\n\n"
        "## Дисциплина исследования (обязательно)\n"
        "- Если в рамках не указано **узкое последующее действие** или точная команда пользователя: "
        "первый действенный шаг = кратчайшая безопасная **разведка территории**; уточняйте цели "
        "в последующих ходах, когда у вас есть сигнал.\n"
        "- Дословная команда пользователя в рамках имеет приоритет.\n\n"
        "## Ограничения вывода\n"
        "- Возвращайте компактную сводку конкурса, а не окончательный отчёт для пользователя.\n"
        "- Используйте только эту структуру: Статус, Ключевые доказательства, Риски/неизвестности, Рекомендуемое следующее действие.\n"
        "- Делайте это кратко; агент оркестрации синтезирует окончательный вывод.\n\n"
    )



_NO_TOOL_NAMES: Final[frozenset[str]] = frozenset(
    {"", "none", "no_tool", "no-tool", "reasoning_only"}
)

# Wrapper that frames worker output as orchestrator-only scratch data. The
# orchestration system prompt instructs the LLM to never quote/paraphrase
# anything inside ``<orchestrator_internal>`` to the user, so the markdown
# headings produced by the workers do not leak into the user-facing reply.
_INTERNAL_OPEN: Final[str] = (
    "<orchestrator_internal>\n"
    "# ВНУТРЕННИЕ ДАННЫЕ — только черновик оркестратора.\n"
    "# НЕ цитируйте, не копируйте, не перефразируйте и не форматируйте ничего из нижеследующего для пользователя.\n"
    "# Прочитайте, решите, затем напишите краткий ответ от своего имени.\n"
)
_INTERNAL_CLOSE: Final[str] = "</orchestrator_internal>"

# Per-worker output cap for single-branch tools (``run_specialist``).
# Multi-branch tools divide a shared budget so combined brief + wrappers stay
# under the ~10 k tool-output truncation in ``_run_impl.truncate_output``.
_MAX_WORKER_OUTPUT_CHARS: Final[int] = 4000
_ORCH_COMBINED_OUTPUT_BUDGET: Final[int] = 8500


def _per_worker_output_cap(branch_count: int) -> int:
    """Chars per worker when several branches are composed into one tool return."""
    n = max(1, int(branch_count))
    if n <= 1:
        return _MAX_WORKER_OUTPUT_CHARS
    return max(1200, min(_MAX_WORKER_OUTPUT_CHARS, _ORCH_COMBINED_OUTPUT_BUDGET // n))

# === Pre-baked decision paragraphs ========================================
# Hoisted out of ``run_dual_approach_contest`` so the long English prose stays
# visible at module level, easy to diff and to lint without scrolling through
# control flow.

_DECISION_BOTH_FAILED: Final[str] = (
    "Обе ветки провалились. Агент оркестрации должен кратко объяснить причину блокировки "
    "и выбрать следующий конкретный шаг восстановления."
)
_DECISION_READY: Final[str] = (
    "Агент оркестрации сравнивает доказательства, покрытие и риски, затем продолжает с "
    "`run_specialist` для конкретного выполнения, если следующее решение снова достаточно "
    "нестабильно для оправдания нового конкурса. Окончательный вывод для пользователя "
    "поступает от агента оркестрации."
)
_DECISION_SPECIALIST: Final[str] = (
    "Агент оркестрации использует вышеприведённую сводку воркера как черновик, принимает "
    "решение о следующем конкретном действии и либо вызывает другой инструмент, либо "
    "пишет окончательный синтез."
)
_DECISION_PARALLEL: Final[str] = (
    "Агент оркестрации объединяет сводки воркеров, затем продолжает в том же ходу "
    "пользователя с дополнительными вызовами инструментов до достижения цели пользователя "
    "или пишет один окончательный синтез."
)
_DECISION_PARALLEL_ALL_FAILED: Final[str] = (
    "Все параллельные воркеры провалились. Агент оркестрации должен кратко объяснить "
    "причину блокировки и выбрать следующий конкретный шаг восстановления."
)

_RATIONALE_SPECIALIST: Final[str] = "выполнение одним специалистом, выбранное оркестратором"

_DEFAULT_MAX_TURNS: Final[int] = 2


# === Data classes =========================================================


@dataclass(frozen=True, slots=True)
class WorkerSpec:
    """Inputs for one worker run.

    Each worker invocation (contest branch A/B or single specialist) becomes a
    ``WorkerSpec`` instance. Keeps :func:`_run_worker` declarative — no eight
    keyword arguments per call site, no positional vs keyword foot-guns.
    """

    label: str
    agent_type: str
    framing: str
    user_task: str
    rationale: str
    allowed_tool_name: str
    max_turns: int = _DEFAULT_MAX_TURNS
    # If set, caps this worker's brief before merging (multi-branch tools).
    max_output_chars: int | None = None
    group_id: str = ""
    workflow_prefix: str = "Contest"


@dataclass(frozen=True, slots=True)
class WorkerResult:
    """Typed outcome of one worker run.

    Replaces the previous "stringly-typed" convention where errors were carried
    in the worker output prefixed with ``[error] …``. Callers now check
    :attr:`failed` directly and the concrete error message is preserved
    separately from the worker brief that gets shown in the contest summary.
    """

    label: str
    agent_name: str
    allowed_tool_name: str
    output: str
    error: str | None = None

    @property
    def failed(self) -> bool:
        return self.error is not None

    @property
    def status(self) -> Literal["completed", "failed"]:
        return "failed" if self.failed else "completed"


# === Helpers ==============================================================


def _wrap_internal(body: str) -> str:
    """Frame ``body`` so the orchestrator reads it as private scratch data."""
    return f"{_INTERNAL_OPEN}\n{body}\n{_INTERNAL_CLOSE}"


def _truncate_worker_output(text: str, max_chars: int | None = None) -> str:
    """Cap a single worker brief; keep head + tail with a clear marker."""
    cap = _MAX_WORKER_OUTPUT_CHARS if max_chars is None else max(256, int(max_chars))
    if len(text) <= cap:
        return text
    half = cap // 2
    head = text[:half]
    tail = text[-half:]
    return (
        f"{head}\n\n"
        f"... [обрезано оркестратором: {len(text) - cap} символов] ...\n\n"
        f"{tail}"
    )


def _display_tool_name(tool_name: str) -> str:
    requested = (tool_name or "").strip()
    if requested.lower() in _NO_TOOL_NAMES:
        return "none"
    return requested


def _new_group_id(kind: str) -> str:
    """Stable, collision-resistant trace group id.

    The previous implementation used ``id(asyncio.current_task())`` which is a
    process-local memory address that can be reused once the originating task
    is collected — fine for a single run but unreliable as a tracing key when
    the orchestrator fires many contests back-to-back. ``uuid4`` removes that
    coupling entirely.
    """
    return f"{kind}:{uuid.uuid4().hex[:12]}"


def _resolve_worker_tool(agent: Any, allowed_tool_name: str) -> tuple[list[Any], str | None]:
    """Определяет инструменты, которые воркер может использовать.

    Принимает одно имя инструмента или разделённый запятыми список (например,
    ``"fetch_url,generic_linux_command"``), чтобы оркестратор мог предоставить
    воркеру небольшой набор инструментов за одну делегацию, избегая амплификации
    1-инструмент/1-делегация (см. отладочную сессию ab1027).

    Возвращает список разрешённых инструментов — пустой, когда вызывающий передал
    ``none`` / ``""`` для воркеров только с рассуждениями. Возвращает ``(tools, None)``
    при успехе или ``([], сообщение_об_ошибке)``, когда ANY запрошенное имя
    неизвестно для ``agent``.
    """
    requested = (allowed_tool_name or "").strip()
    if requested.lower() in _NO_TOOL_NAMES:
        return [], None

    available = list(agent.tools or [])
    by_name = {getattr(t, "name", ""): t for t in available}

    requested_names = [n.strip() for n in requested.split(",") if n.strip()]
    if not requested_names:
        return [], None

    resolved: list[Any] = []
    missing: list[str] = []
    for name in requested_names:
        tool = by_name.get(name)
        if tool is None:
            missing.append(name)
        elif tool not in resolved:
            resolved.append(tool)

    if missing:
        avail = ", ".join(sorted(by_name.keys()))
        joined_missing = ", ".join(f"`{m}`" for m in missing)
        return (
            [],
            f"Инструмент(ы) {joined_missing} недоступны для `{agent.name}`. Доступные: {avail}",
        )
    return resolved, None


def _contest_worker(agent: Any, allowed_tool_name: str) -> tuple[Any | None, str | None]:
    """Возвращает клон воркера, который не может передавать и предоставляет выбранные инструменты.

    ``allowed_tool_name`` может быть одним инструментом или разделённым запятыми списком,
    в этом случае воркер получает весь небольшой набор инструментов сразу.
    """
    tools, error = _resolve_worker_tool(agent, allowed_tool_name)
    if error:
        return None, error

    base_settings = agent.model_settings or ModelSettings()
    # Allow parallel tool calls only when the worker actually has >1 tool;
    # otherwise keep the original sequential behaviour.
    parallel = len(tools) > 1
    model_settings = base_settings.resolve(ModelSettings(parallel_tool_calls=parallel))
    return (
        agent.clone(
            tools=tools,
            handoffs=[],
            model_settings=model_settings,
        ),
        None,
    )


def _resolve_agent(agent_type: str, label: str) -> tuple[Any | None, str | None]:
    """Ищет фабрику специализированного агента; возвращает ``(агент, сообщение_об_ошибке)``.

    При ошибке (опечатка, удалённый агент, регистр) строка ошибки содержит
    список доступных ключей фабрик, чтобы агент оркестрации мог исправиться
    без дополнительного раунда — аналогично тому, как :func:`_resolve_worker_tool`
    уже предоставляет список доступных имён инструментов.
    """
    from cai.agents import get_agent_by_name

    key = agent_type.strip()
    try:
        return get_agent_by_name(key, agent_id=f"O{label}"), None
    except ValueError as exc:
        try:
            from cai.agents import get_available_agents

            available = ", ".join(sorted(get_available_agents().keys()))
        except Exception:  # pragma: no cover — defensive: discovery rarely fails
            available = ""
        suggestion = f" Доступные: {available}." if available else ""
        return None, f"Неверный agent_type `{key}`: {exc}.{suggestion}"


def _build_worker_input(spec: WorkerSpec) -> str:
    """Формирует пользовательский промпт для одного воркера.

    Сохраняется как чистая функция, чтобы тесты могли проверять
    детерминированные заголовки (``## Approach framing (A)``, ``## Allowed worker tool`` и т.д.)
    без запуска всего конвейера оркестрации.
    """
    return (
        f"{_worker_constraints_prefix(spec.max_turns)}"
        f"## Рамки подхода ({spec.label})\n{spec.framing}\n\n"
        f"## Общая задача пользователя\n{spec.user_task}\n\n"
        f"## Допустимый инструмент воркера\n{spec.allowed_tool_name or 'нет'}\n\n"
        f"## Обоснование конкурса (от оркестратора)\n{spec.rationale}\n"
    )


# === Worker runner ========================================================


async def _run_worker(spec: WorkerSpec) -> WorkerResult:
    """Запускает одного воркера согласно ``spec`` и возвращает типизированный ``WorkerResult``."""
    base_agent, agent_error = _resolve_agent(spec.agent_type, spec.label)
    if agent_error or base_agent is None:
        msg = agent_error or "Неизвестная ошибка разрешения агента"
        return WorkerResult(
            label=spec.label,
            agent_name=spec.agent_type,
            allowed_tool_name=spec.allowed_tool_name,
            output=msg,
            error=msg,
        )

    agent, setup_error = _contest_worker(base_agent, spec.allowed_tool_name)
    display_name = getattr(agent or base_agent, "name", None) or spec.agent_type
    if setup_error:
        return WorkerResult(
            label=spec.label,
            agent_name=display_name,
            allowed_tool_name=spec.allowed_tool_name,
            output=setup_error,
            error=setup_error,
        )

    user_input = _build_worker_input(spec)
    trace_meta: dict[str, str] = {"contest_group": spec.group_id}
    if spec.workflow_prefix == "Parallel":
        trace_meta["parallel_branch"] = str(spec.label)
    else:
        trace_meta["contest_branch"] = f"approach_{spec.label.lower()}"
    rc = RunConfig(
        workflow_name=f"{spec.workflow_prefix} branch {spec.label}",
        group_id=spec.group_id,
        trace_metadata=trace_meta,
    )

    try:
        # ``silence_worker_display`` suppresses the worker's user-facing markdown
        # panels and Rich streaming panels (the "● Red Team Agent ─ <conclusion>"
        # boxes); only the orchestration agent's final synthesis is meant to
        # reach the user. Live-block tool rows still render so the user sees
        # progress for the worker's individual tool calls.
        with silence_worker_display():
            result = await Runner.run(
                agent,
                user_input,
                max_turns=spec.max_turns,
                run_config=rc,
            )
    except Exception as exc:  # pylint: disable=broad-except
        msg = f"{type(exc).__name__}: {exc}"
        return WorkerResult(
            label=spec.label,
            agent_name=display_name,
            allowed_tool_name=spec.allowed_tool_name,
            output=msg,
            error=msg,
        )

    out = ItemHelpers.text_message_outputs(result.new_items)
    if not out.strip():
        out = "(текстовый вывод не захвачен)"
    out_cap = spec.max_output_chars
    return WorkerResult(
        label=spec.label,
        agent_name=display_name,
        allowed_tool_name=spec.allowed_tool_name,
        output=_truncate_worker_output(out, out_cap),
    )


# === Brief composition ====================================================


def _format_branch_section(result: WorkerResult) -> list[str]:
    return [
        f"### Подход {result.label}",
        f"- Агент: `{result.agent_name}`",
        f"- Инструмент: `{_display_tool_name(result.allowed_tool_name)}`",
        f"- Статус: `{result.status}`",
        "",
        "#### Сводка воркера",
        result.output,
        "",
    ]


def _compose_contest_brief(
    *,
    title: str,
    overall_status: str,
    rationale: str,
    results: tuple[WorkerResult, ...],
    decision_text: str,
    extra_header_lines: tuple[str, ...] = (),
) -> str:
    """Рендерит каноническую сводку, общую для конкурсов и инструментов одного специалиста.

    Ранее оба инструмента рендерили разную структуру разметки, что заставляло LLM
    (и любой downstream-парсер) изучать два формата. С одним каркасом здесь
    ``run_specialist`` и ``run_dual_approach_contest`` различаются только
    заголовком, количеством веток и заключительным абзацем решения.
    """
    lines: list[str] = [
        f"## {title}",
        "",
        f"- Общий статус: `{overall_status}`",
        f"- Обоснование: {rationale}",
    ]
    lines.extend(extra_header_lines)
    lines.append("")
    for result in results:
        lines.extend(_format_branch_section(result))
    lines.extend(["### Следующее решение", decision_text])
    return "\n".join(lines)


# === Public tools =========================================================


@function_tool
async def run_dual_approach_contest(
    agent_type_for_approach_a: str,
    agent_type_for_approach_b: str,
    allowed_tool_for_approach_a: str,
    allowed_tool_for_approach_b: str,
    approach_a_framing: str,
    approach_b_framing: str,
    shared_user_task: str,
    contest_rationale: str,
) -> str:
    """Запускает два параллельных исследовательских подхода к одной задаче пользователя (макс. 2 агента; бюджет ходов воркеров из ``CAI_ORCHESTRATION_WORKER_MAX_TURNS``).

    Используйте только для сравнения ортогональных методологий, конкурирующих гипотез,
    нестабильных доказательств или высокорискового ветвления перед тем, как направить CAI
    по одному пути. Тактические последующие действия обычно следует выполнять с помощью
    ``run_specialist``.

    ``agent_type_*`` должны быть ключами фабрик (например, ``redteam_agent``, ``blueteam_agent``).
    Воркеры работают без передачи и с не более чем одним допустимым именем инструмента
    (``none`` = только рассуждения).

    После возврата этого инструмента вы (Агент оркестрации) остаётесь под контролем:
    сравнивайте выводы, выбирайте победителя, планируйте **следующий** шаг и либо снова
    вызывайте этот инструмент для нового по-настоящему нестабильного решения, вызывайте
    ``run_specialist`` для конкретной последующей работы, или продолжайте рассуждать до
    достижения цели пользователя.

    Args:
        agent_type_for_approach_a: Ключ фабрики для воркера A.
        agent_type_for_approach_b: Ключ фабрики для воркера B (может совпадать с A).
        allowed_tool_for_approach_a: Точное имя инструмента A или ``none`` для только рассуждений.
        allowed_tool_for_approach_b: Точное имя инструмента B или ``none`` для только рассуждений.
        approach_a_framing: Как A должен решать задачу (инструменты/стратегия указываются здесь).
        approach_b_framing: Как B должен решать задачу (**ортогонально** A по возможности).
        shared_user_task: Конкретный запрос пользователя, который должны решить оба воркера.
        contest_rationale: Краткое обоснование проведения конкурса.
    """
    group_id = _new_group_id("contest")
    per_cap = _per_worker_output_cap(2)
    specs = (
        WorkerSpec(
            label="A",
            agent_type=agent_type_for_approach_a,
            framing=approach_a_framing,
            user_task=shared_user_task,
            rationale=contest_rationale,
            allowed_tool_name=allowed_tool_for_approach_a,
            group_id=group_id,
            workflow_prefix="Contest",
            max_turns=_configured_worker_max_turns(),
            max_output_chars=per_cap,
        ),
        WorkerSpec(
            label="B",
            agent_type=agent_type_for_approach_b,
            framing=approach_b_framing,
            user_task=shared_user_task,
            rationale=contest_rationale,
            allowed_tool_name=allowed_tool_for_approach_b,
            group_id=group_id,
            workflow_prefix="Contest",
            max_turns=_configured_worker_max_turns(),
            max_output_chars=per_cap,
        ),
    )
    results: tuple[WorkerResult, ...] = tuple(
        await asyncio.gather(*(_run_worker(spec) for spec in specs))
    )

    if all(r.failed for r in results):
        return _wrap_internal(
            _compose_contest_brief(
                title="Конкурс двух подходов",
                overall_status="обе ветки провалились",
                rationale=contest_rationale,
                results=results,
                decision_text=_DECISION_BOTH_FAILED,
            )
        )
    return _wrap_internal(
        _compose_contest_brief(
            title="Конкурс двух подходов",
            overall_status="готово к решению оркестратора",
            rationale=contest_rationale,
            extra_header_lines=(
                "- Структура: сводки воркеров показаны для прозрачности; окончательный вывод "
                "после оркестрации.",
            ),
            results=results,
            decision_text=_DECISION_READY,
        )
    )


@function_tool
async def run_specialist(
    agent_type: str,
    allowed_tool_name: str,
    task: str,
    framing: str,
) -> str:
    """Запускает одного специалиста, сохраняя контроль агента оркестрации.

    Используйте это для победившего пути после конкурса, для **узкого последующего** углубления,
    или когда подходит только один канал. Используйте ``run_parallel_specialists`` для
    параллельной широкой разведки первого волны по ортогональным направлениям. Воркер не может
    передавать и предоставляет не более одного имени инструмента.

    Args:
        agent_type: Ключ фабрики для специалиста (например, ``redteam_agent``).
        allowed_tool_name: Имя инструмента, которое может использовать воркер, ИЛИ разделённый
            запятыми список имён (например, ``"fetch_url,generic_linux_command"``) для предоставления
            небольшого набора инструментов за одну делегацию и избежания 1-инструмент/1-делегация,
            ИЛИ ``none`` для только рассуждений.
        task: Краткая конкретная рабочая просьба (не копируйте дословно весь пользовательский запрос).
        framing: Стратегия и ограничения; укажите **широкую разведку** или **узкое последующее**
            действие, чтобы воркер применял дисциплину поиска в ширину или пропускал её, когда
            вам нужно точное выполнение.
    """
    spec = WorkerSpec(
        label="S",
        agent_type=agent_type,
        framing=framing,
        user_task=task,
        rationale=_RATIONALE_SPECIALIST,
        allowed_tool_name=allowed_tool_name,
        group_id=_new_group_id("specialist"),
        workflow_prefix="Specialist",
        max_turns=_configured_worker_max_turns(),
    )
    result = await _run_worker(spec)
    overall_status = "провалено" if result.failed else "выполнено"
    return _wrap_internal(
        _compose_contest_brief(
            title="Сводка специалиста",
            overall_status=overall_status,
            rationale=_RATIONALE_SPECIALIST,
            results=(result,),
            decision_text=_DECISION_SPECIALIST,
        )
    )

@function_tool
async def run_parallel_specialists(workers_json: str, parallel_rationale: str) -> str:
    """Запускает 2–4 специалиста параллельно для независимых подзадач, сохраняя ваш контроль.

    Основной инструмент для **параллельных разведчиков первого волны MAS**: параллельная
    **широкая** разведка по ортогональным направлениям (короткие строки ``task``, разведывательные
    ``framing``). Также используйте, когда пользователь называет несколько рабочих направлений.

    Используйте ``run_dual_approach_contest`` при сравнении двух гипотез для **одного**
    ветвления; используйте ``run_specialist`` для одного **узкого** последующего действия,
    когда у вас есть сигнал.

    ``workers_json`` должен быть JSON-массивом из 2–4 объектов. Каждый объект требует ключей:
    ``agent_type``, ``allowed_tool_name``, ``task``, ``framing`` (тот же контракт, что
    и ``run_specialist``).

    Args:
        workers_json: JSON-массив спецификаций воркеров (2–4 элемента).
        parallel_rationale: Почему параллельное выполнение уместно сейчас (например, карта
            территории первого волны).
    """
    raw = (workers_json or "").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return f"Неверный workers_json (недопустимый JSON): {exc}"

    if not isinstance(data, list):
        return "workers_json должен быть JSON-массивом."

    if len(data) < 2:
        return "Укажите не менее 2 воркеров для параллельного выполнения или используйте run_specialist для одного."

    if len(data) > 4:
        return "Допускается не более 4 параллельных воркеров; разделите дополнительную работу на последующие вызовы инструментов."

    required = ("agent_type", "allowed_tool_name", "task", "framing")
    for i, w in enumerate(data, start=1):
        if not isinstance(w, dict):
            return f"Воркер {i} должен быть JSON-объектом."
        for key in required:
            if key not in w:
                return f"У воркера {i} отсутствует обязательный ключ `{key}`."

    max_t = _configured_worker_max_turns()
    per_cap = _per_worker_output_cap(len(data))
    group_id = _new_group_id("parallel")
    specs: list[WorkerSpec] = []
    for i, w in enumerate(data, start=1):
        specs.append(
            WorkerSpec(
                label=f"P{i}",
                agent_type=str(w["agent_type"]),
                framing=str(w["framing"]),
                user_task=str(w["task"]),
                rationale=parallel_rationale,
                allowed_tool_name=str(w["allowed_tool_name"]),
                max_turns=max_t,
                max_output_chars=per_cap,
                group_id=group_id,
                workflow_prefix="Parallel",
            )
        )

    results: tuple[WorkerResult, ...] = tuple(
        await asyncio.gather(*(_run_worker(spec) for spec in specs))
    )

    if all(r.failed for r in results):
        return _wrap_internal(
            _compose_contest_brief(
                title="Параллельные специалисты",
                overall_status="все ветки провалились",
                rationale=parallel_rationale,
                results=results,
                decision_text=_DECISION_PARALLEL_ALL_FAILED,
            )
        )

    overall = "частичное выполнение" if any(r.failed for r in results) else "выполнено"
    return _wrap_internal(
        _compose_contest_brief(
            title="Параллельные специалисты",
            overall_status=overall,
            rationale=parallel_rationale,
            results=results,
            decision_text=_DECISION_PARALLEL,
        )
    )

