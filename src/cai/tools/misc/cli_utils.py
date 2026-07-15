"""
Модуль утилит CLI для выполнения команд оболочки и обработки их вывода.
"""

from cai.tools.common import run_command  # pylint: disable=E0401
from cai.sdk.agents import function_tool


@function_tool
def execute_cli_command(command: str) -> str:
    """
    Выполнение команды CLI и возврат вывода.

    Args:
        command (str): Команда для выполнения.
        Должна быть краткой иocused.

        Избегайте излишне длинных команд
        с ненужными флагами/опциями.

    Returns:
        str: Вывод команды, отформатированный для ясности и читаемости.
            Длинные выводы будут обрезаны или отфильтрованы
    """
    return run_command(command)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("execute_cli_command", execute_cli_command, categories=['misc'])
