"""Контекст подавления отображения воркера при запуске субагентов.

Находится в :mod:`cai.util` (а не в :mod:`cai.sdk.agents`), чтобы пользовательские
процедуры отображения, такие как :mod:`cai.util.streaming`, могли выполнять ``import``
при загрузке модуля без запуска тяжёлого инициализатора пакета ``cai.sdk.agents`` —
этот пакет сам активно подтягивает :mod:`cai.util` для трекера стоимости и
потоковых хелперов Rich, поэтому импорт из ``streaming`` создал бы
циклический импорт с частично инициализированным модулем.

Контекст
--------
Агент оркестрации (``cai.agents.orchestration_agent``) вызывает специализированных
агентов как *инструменты* через :func:`cai.tools.misc.approach_contest.run_specialist`
(и ``run_dual_approach_contest`` для параллельных A/B соревнований). Каждый вызов
инструмента порождает новый :class:`cai.sdk.agents.Runner.run` для воркер-агента,
жизненный цикл которого естественным образом производит:

* Финальные markdown-панели, отрисованные :func:`cai.util.streaming.cli_print_agent_messages`
  (боксы «● Red Team Agent (alias1) ── <conclusion>»).
* Потоковые Rich-панели, создаваемые на стороне модели
  (:mod:`cai.sdk.agents.models.openai_chatcompletions`).

Эти выводы являются *внутренними черновиками* оркестратора — пользователь должен
видеть только финальный синтез оркестратора. Если панели воркера просачиваются,
создаётся впечатление, что два агента отвечают на один вопрос, причём воркер
опережает формулировку оркестратора.

Механизм
---------
Одна :class:`contextvars.ContextVar` плюс ``contextmanager``
:func:`silence_worker_display`. Процедуры отображения, которые должны
пропускаться при работе воркера, обращаются к :func:`worker_display_silenced`
и завершаются досрочно. Флаг устанавливается ``_run_worker`` в
:mod:`cai.tools.misc.approach_contest` и автоматически восстанавливается при
выходе (безопасно для реентрантности — вложенные воркеры остаются тихими).

Что **не** подавляется
-----------------------
Компактный живой блок REPL (:mod:`cai.repl.ui.compact_renderer`) продолжает
показывать строки инструментов воркера (``↳ ● Red Team Agent ─ nmap …``),
потому что это прогресс-обратная связь, которую пользователь хочет видеть.
Только маршруты финальных панелей / потоковых панелей управляются этим флагом.
"""

from __future__ import annotations

import contextvars
from collections.abc import Iterator
from contextlib import contextmanager

_WORKER_DISPLAY_SILENT: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "cai_worker_display_silent",
    default=False,
)


@contextmanager
def silence_worker_display() -> Iterator[None]:
    """Подавить отображение сообщений, пока субагент работает как инструмент-воркер.

    Контекст **наследуется** задачами, порождёнными через :mod:`asyncio`, потому что
    значения ``ContextVar`` копируются в контекст каждой новой задачи. Вложенные
    контексты безопасны: повторный вход в :func:`silence_worker_display`, когда флаг
    уже установлен, является холостой операцией для потребителя (остаётся ``True``),
    а внутренний ``__exit__`` восстанавливает предыдущее ``True`` вместо сброса
    в ``False``.
    """
    token = _WORKER_DISPLAY_SILENT.set(True)
    try:
        yield
    finally:
        _WORKER_DISPLAY_SILENT.reset(token)


def worker_display_silenced() -> bool:
    """Вернуть ``True``, пока запуск субагента подавляет пользовательский вывод."""
    return _WORKER_DISPLAY_SILENT.get()


__all__ = ["silence_worker_display", "worker_display_silenced"]
