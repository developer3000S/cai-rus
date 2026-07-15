"""
Инструмент управления планами для обновления планов (списка задач) отдельных агентов.

Каждый агент поддерживает собственный план в памяти, хранимый на экземпляре модели
(`agent.model._current_plan`). Это предотвращает смешивание планов между агентами
и избегает записи в общие JSON-файлы в ~/.cai.

Использование:
  - Вызовите этот инструмент со списком словарей задач для установки/обновления плана.
  - Не смешивайте обновления плана с инструментами выполнения команд.

Инструмент не действует, если в окружении не установлена переменная `CAI_PLAN=true`.
"""

import os
from cai.sdk.agents.tool import function_tool  # pylint: disable=import-error

# Prefer the per-execution-context active model first
try:
    from cai.sdk.agents.models.openai_chatcompletions import (
        get_current_active_model,
        ACTIVE_MODEL_INSTANCES,
    )
except Exception:  # pragma: no cover - defensive import fallback
    get_current_active_model = lambda: None  # type: ignore
    ACTIVE_MODEL_INSTANCES = {}

# As a secondary fallback, use the SimpleAgentManager active agent
try:
    from cai.sdk.agents.simple_agent_manager import AGENT_MANAGER
except Exception:  # pragma: no cover
    AGENT_MANAGER = None  # type: ignore


@function_tool
async def Todo_list(todos: list | None = None) -> str:
    """
    Обновление плана текущего агента (списка задач).

    Args:
        todos: Список словарей задач с полями, такими как:
               {'content': str, 'status': 'pending'|'in_progress'|'completed', 'activeForm': str}

    Поведение:
        - Сохраняет план в памяти на экземпляре модели текущего агента
          (отдельно для каждого агента, не общий).
        - Требует переменную окружения CAI_PLAN=true для активации.

    Returns:
        Подтверждение с отформатированным блоком <todo_list> или сообщение об ошибке.
    """
    from cai.config import get_config
    cfg = get_config()
    if not cfg.plan_enabled:
        return "Функция плана отключена. Установите CAI_PLAN=true для включения отслеживания планов."

    if todos is None:
        return "Ошибка: 'todos' обязателен (список словарей задач)"

    if not isinstance(todos, list) or len(todos) == 0:
        return "Ошибка: 'todos' должен быть непустым списком"

    if not all(isinstance(item, dict) for item in todos):
        return "Ошибка: каждый элемент в 'todos' должен быть словарём"

    # Resolve the current model instance, prioritizing the execution context
    model_instance = None

    # 1) ContextVar during model generation/tool execution
    try:
        model_instance = get_current_active_model()
    except Exception:
        model_instance = None

    # 2) Active agent from SimpleAgentManager
    if model_instance is None and AGENT_MANAGER is not None:
        try:
            agent = AGENT_MANAGER.get_active_agent()
            if agent and hasattr(agent, "model") and hasattr(agent.model, "_current_plan"):
                model_instance = agent.model
        except Exception:
            pass

    # 3) Most recent model from ACTIVE_MODEL_INSTANCES registry
    if model_instance is None and ACTIVE_MODEL_INSTANCES:
        try:
            latest_key = max(ACTIVE_MODEL_INSTANCES.keys(), key=lambda x: x[1])
            model_ref = ACTIVE_MODEL_INSTANCES.get(latest_key)
            model_instance = model_ref() if model_ref else None
        except Exception:
            model_instance = None

    if model_instance is None or not hasattr(model_instance, "_current_plan"):
        return "Ошибка: не удалось найти модель текущего агента для сохранения плана"

    # Store plan on the model instance (per-agent)
    try:
        model_instance._current_plan = todos  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover - defensive
        return f"Ошибка обновления плана: {e}"

    # Produce a compact confirmation with the todo list for visibility
    lines = [
        "План успешно обновлён. Продолжайте использовать список задач для отслеживания прогресса.",
        "",
        "<todo_list>",
    ]
    for idx, task in enumerate(todos, 1):
        status = task.get("status", "pending")
        content = task.get("content", "N/A")
        lines.append(f"{idx}. [{status}] {content}")
    lines.append("</todo_list>")
    return "\n".join(lines)


# Auto-register in ToolRegistry [E]
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("Todo_list", Todo_list, categories=["misc"])
