"""Менеджер вывода CAI.

Система вывода на основе событий, заменяющая 13+ изменяемых глобальных переменных в util.py.
Вдохновлено паттерном каналов событий Codex (tx_event + типизированные дельты).

Создано в Day 0 как общий контракт между 3 потоками рефакторинга.
- Поток 1 (Core Engine): генерирует события из выполнения инструментов и вызовов LLM
- Поток 3 (Interface): реализует обработчики для TUI, CLI, API
- Поток 2 (Foundation): удаляет старые глобальные переменные из util.py после завершения миграции

Компактное расширение REPL (готовое к оркестрации):
- События ``Task*`` представляют активность агента на гранулярности *задачи*. Задача — это
  один вызов инструмента агентом (или логическая единица, генерируемая будущим планировщиком).
  Они находятся на более высоком уровне, чем события ``Tool*``, и управляют однострочным
  рендерером Live и всплывающим окном раскрытия Ctrl+O.
- События ``Turn*`` обрамляют ход пользователя, чтобы рендерер мог корректно
  сворачивать область Live между ходами.
- ``TaskRegistry`` хранит состояние задач в ОЗУ (FIFO с ограничением), потребляемое
  всплывающим окном раскрытия Ctrl+O.
"""

from __future__ import annotations

import json
import sys
import threading
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, TextIO


# --- Типы событий ---


@dataclass
class OutputEvent:
    """Базовое событие вывода."""

    timestamp: float = field(default_factory=time.time)
    agent_id: str | None = None


@dataclass
class ToolStartEvent(OutputEvent):
    """Выполнение инструмента началось."""

    tool_name: str = ""
    call_id: str = ""


@dataclass
class ToolStreamEvent(OutputEvent):
    """Пошаговый вывод инструмента (стриминг)."""

    tool_name: str = ""
    call_id: str = ""
    chunk: str = ""


@dataclass
class ToolCompleteEvent(OutputEvent):
    """Выполнение инструмента завершено."""

    tool_name: str = ""
    call_id: str = ""
    output: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0


@dataclass
class ToolErrorEvent(OutputEvent):
    """Выполнение инструмента завершилось ошибкой."""

    tool_name: str = ""
    call_id: str = ""
    error: str = ""
    error_type: str = ""


@dataclass
class LLMStreamEvent(OutputEvent):
    """Пошаговый фрагмент ответа LLM."""

    content: str = ""
    is_reasoning: bool = False


@dataclass
class LLMCompleteEvent(OutputEvent):
    """Ответ LLM завершён."""

    content: str = ""
    usage: dict = field(default_factory=dict)
    model: str = ""
    cost: float = 0.0


@dataclass
class StatusEvent(OutputEvent):
    """Общее обновление статуса."""

    message: str = ""
    level: str = "info"


@dataclass
class AgentHandoffEvent(OutputEvent):
    """Произошла передача агента."""

    from_agent: str = ""
    to_agent: str = ""


# --- События компактного/оркестрационного режима ---


@dataclass
class TurnStartEvent(OutputEvent):
    """Ход пользователя только что начался."""

    turn_id: str = ""
    user_input: str = ""


@dataclass
class TurnSummaryEvent(OutputEvent):
    """Ход пользователя только что завершился. Используется компактным обработчиком для сворачивания
    переходного блока Live между ходами. ``tasks`` сохраняется, чтобы будущие
    потребители (телеметрия, JSON-стоки, оркестратор) могли прикрепить снимок
    без повторного вычисления из :data:`TASK_REGISTRY`."""

    turn_id: str = ""
    tasks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TaskStartEvent(OutputEvent):
    """Задача агента началась.

    ``task_id`` уникален в рамках хода. ``label`` — описание для человека,
    отображаемое на строке live (сегодня определяется детерминированно; в будущем
    будет генерироваться агентом-планировщиком).
    """

    task_id: str = ""
    agent_name: str = ""
    agent_id: str = ""
    tool_name: str = ""
    label: str = ""
    call_id: str = ""
    parent_task_id: str = ""
    depth: int = 0


@dataclass
class TaskUpdateEvent(OutputEvent):
    """Пошаговый прогресс задачи (фрагмент вывода и/или переопределение метки)."""

    task_id: str = ""
    chunk: str = ""
    label: str = ""


@dataclass
class TaskCompleteEvent(OutputEvent):
    """Задача успешно завершена."""

    task_id: str = ""
    output: str = ""
    duration_seconds: float = 0.0
    cost: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0


@dataclass
class TaskErrorEvent(OutputEvent):
    """Задача завершилась ошибкой; содержит информацию об ошибке для JSONL-стока и всплывающего окна."""

    task_id: str = ""
    output: str = ""
    error: str = ""
    error_type: str = ""
    duration_seconds: float = 0.0


# --- Протокол обработчика вывода ---


class OutputHandler(Protocol):
    """Интерфейс для потребителей вывода (TUI, CLI, API, файл)."""

    def handle(self, event: OutputEvent) -> None: ...


# --- Менеджер вывода ---


class OutputManager:
    """Центральная шина вывода, заменяющая глобальное изменяемое состояние.

    Использование:
        # При запуске (Поток 3 подключает обработчики)
        output = OutputManager()
        output.subscribe(TUIOutputHandler(...))

        # Во время выполнения (Поток 1 генерирует)
        output.emit(ToolStartEvent(tool_name="nmap", call_id="abc"))
        output.emit(ToolStreamEvent(tool_name="nmap", call_id="abc", chunk="..."))
        output.emit(ToolCompleteEvent(tool_name="nmap", call_id="abc", output="..."))
    """

    def __init__(self) -> None:
        self._handlers: list[OutputHandler] = []

    def subscribe(self, handler: OutputHandler) -> None:
        self._handlers.append(handler)

    def unsubscribe(self, handler: OutputHandler) -> None:
        self._handlers.remove(handler)

    def emit(self, event: OutputEvent) -> None:
        for handler in self._handlers:
            try:
                handler.handle(event)
            except Exception:
                pass  # Обработчики не должны ломать конвейер

    def flush(self) -> None:
        for handler in self._handlers:
            if hasattr(handler, "flush"):
                handler.flush()


# --- Конкретные обработчики ---


class CLIOutputHandler:
    """Отрисовывает события вывода в консоль Rich (headless/CLI режим).

    Разработан для не-TUI сессий, где вывод идёт напрямую в терминал.
    Использует форматирование Rich если доступно, иначе — простой текст.
    """

    def __init__(self, file: TextIO | None = None) -> None:
        self._file = file or sys.stderr
        try:
            from rich.console import Console

            self._console = Console(file=self._file, highlight=False)
            self._rich = True
        except ImportError:
            self._console = None
            self._rich = False

    def _print(self, text: str) -> None:
        if self._rich and self._console:
            self._console.print(text, highlight=False)
        else:
            print(text, file=self._file, flush=True)

    def handle(self, event: OutputEvent) -> None:  # noqa: C901
        if isinstance(event, ToolStartEvent):
            # Подавлено: запуск/вывод/завершение инструмента отрисовывается
            # плоским стилем в cli_print_tool_output / _create_tool_panel_content.
            pass
        elif isinstance(event, ToolStreamEvent):
            # Подавлено: фрагменты стриминга обрабатываются дисплеем Rich Live
            pass
        elif isinstance(event, ToolCompleteEvent):
            # Подавлено: завершение отрисовывается плоским стилем в streaming.py
            pass
        elif isinstance(event, ToolErrorEvent):
            # Ошибки всё ещё показываются, чтобы избежать молчаливых сбоев
            self._print(
                f"[bold red]!! {event.tool_name}: {event.error}[/bold red]"
                if self._rich
                else f"!! {event.tool_name}: {event.error}"
            )
        elif isinstance(event, LLMStreamEvent):
            if self._rich and self._console:
                self._console.print(event.content, end="", highlight=False)
            else:
                print(event.content, end="", file=self._file, flush=True)
        elif isinstance(event, LLMCompleteEvent):
            if event.content:
                self._print(event.content)
        elif isinstance(event, StatusEvent):
            level_style = {
                "info": "cyan",
                "warning": "yellow",
                "error": "bold red",
            }.get(event.level, "dim")
            self._print(
                f"[{level_style}]{event.message}[/{level_style}]"
                if self._rich
                else f"[{event.level.upper()}] {event.message}"
            )
        elif isinstance(event, AgentHandoffEvent):
            self._print(
                f"[bold magenta]>> Передача: {event.from_agent} -> {event.to_agent}[/bold magenta]"
                if self._rich
                else f">> Передача: {event.from_agent} -> {event.to_agent}"
            )

    def flush(self) -> None:
        self._file.flush()


class FileOutputHandler:
    """Логирует события вывода в JSONL-файл для воспроизведения/аудита.

    Каждая строка — JSON-объект с ``type``, полями события и временной меткой.
    Несериализуемые значения преобразуются через ``str()``.
    """

    def __init__(self, filepath: str | Path) -> None:
        self._path = Path(filepath)
        self._file: TextIO = open(self._path, "a", encoding="utf-8")

    def _serialize(self, obj: Any) -> Any:
        """Сделать поля dataclass безопасными для JSON."""
        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._serialize(v) for v in obj]
        # Примитивы проходят как есть; всё остальное становится str
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        return str(obj)

    def handle(self, event: OutputEvent) -> None:
        data: dict[str, Any] = {"type": type(event).__name__}
        data.update(self._serialize(event.__dict__))
        self._file.write(json.dumps(data, default=str) + "\n")

    def flush(self) -> None:
        self._file.flush()

    def close(self) -> None:
        self._file.flush()
        self._file.close()


# --- Реестр задач ---


@dataclass
class TaskRecord:
    """Снимок жизненного цикла одной задачи. Потребляется всплывающим окном раскрытия Ctrl+O
    и любыми будущими подписчиками телеметрии/оркестратора."""

    task_id: str
    turn_id: str
    agent_name: str
    agent_id: str
    tool_name: str
    label: str
    started_at: float
    status: str = "running"  # "running" | "completed" | "error"
    completed_at: float | None = None
    duration_seconds: float = 0.0
    output: str = ""
    error: str = ""
    error_type: str = ""
    cost: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    call_id: str = ""
    parent_task_id: str = ""
    depth: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "turn_id": self.turn_id,
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "tool_name": self.tool_name,
            "label": self.label,
            "started_at": self.started_at,
            "status": self.status,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "output": self.output,
            "error": self.error,
            "error_type": self.error_type,
            "cost": self.cost,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "call_id": self.call_id,
            "parent_task_id": self.parent_task_id,
            "depth": self.depth,
        }


class TaskRegistry:
    """Реестр записей задач в памяти, FIFO с ограничением.

    Потокобезопасный; потребляется всплывающим окном раскрытия Ctrl+O и live-рендерером.
    Полный ``output`` хранится здесь, чтобы контекст LLM (обрабатывается отдельно)
    и UI никогда не разделяли буферы.

    Записи сохраняются между ходами до вытеснения FIFO; ``begin_turn`` только
    вращает ``current_turn_id``, чтобы окно могло ограничиться «этим ходом» без
    потери предыдущих данных при необходимости.
    """

    def __init__(self, max_size: int = 200) -> None:
        self._tasks: "OrderedDict[str, TaskRecord]" = OrderedDict()
        self._max = max_size
        self._lock = threading.RLock()
        self._current_turn_id: str | None = None

    @property
    def current_turn_id(self) -> str | None:
        return self._current_turn_id

    def begin_turn(self, turn_id: str | None = None) -> str:
        with self._lock:
            self._current_turn_id = turn_id or uuid.uuid4().hex[:12]
            return self._current_turn_id

    def add(self, record: TaskRecord) -> None:
        with self._lock:
            self._tasks[record.task_id] = record
            while len(self._tasks) > self._max:
                self._tasks.popitem(last=False)

    def update(self, task_id: str, *, chunk: str | None = None, label: str | None = None) -> None:
        with self._lock:
            rec = self._tasks.get(task_id)
            if rec is None:
                return
            if chunk:
                rec.output += chunk
            if label:
                rec.label = label

    def complete(
        self,
        task_id: str,
        *,
        output: str | None = None,
        duration_seconds: float | None = None,
        cost: float = 0.0,
        tokens_input: int = 0,
        tokens_output: int = 0,
    ) -> None:
        with self._lock:
            rec = self._tasks.get(task_id)
            if rec is None:
                return
            rec.status = "completed"
            rec.completed_at = time.time()
            if output is not None:
                rec.output = output
            if duration_seconds is not None:
                rec.duration_seconds = duration_seconds
            else:
                rec.duration_seconds = max(0.0, rec.completed_at - rec.started_at)
            rec.cost = cost
            rec.tokens_input = tokens_input
            rec.tokens_output = tokens_output

    def fail(
        self,
        task_id: str,
        *,
        output: str | None = None,
        error: str = "",
        error_type: str = "",
        duration_seconds: float | None = None,
    ) -> None:
        with self._lock:
            rec = self._tasks.get(task_id)
            if rec is None:
                return
            rec.status = "error"
            rec.completed_at = time.time()
            if output is not None:
                rec.output = output
            rec.error = error
            rec.error_type = error_type
            if duration_seconds is not None:
                rec.duration_seconds = duration_seconds
            else:
                rec.duration_seconds = max(0.0, rec.completed_at - rec.started_at)

    def get(self, task_id: str) -> TaskRecord | None:
        with self._lock:
            return self._tasks.get(task_id)

    def active(self) -> list[TaskRecord]:
        with self._lock:
            return [r for r in self._tasks.values() if r.status == "running"]

    def for_turn(self, turn_id: str | None = None) -> list[TaskRecord]:
        """Вернуть задачи, принадлежащие ``turn_id`` (по умолчанию текущий)."""
        target = turn_id or self._current_turn_id
        if target is None:
            return []
        with self._lock:
            return [r for r in self._tasks.values() if r.turn_id == target]

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._current_turn_id = None


# Синглтон для текущей сессии
OUTPUT = OutputManager()
TASK_REGISTRY = TaskRegistry()
