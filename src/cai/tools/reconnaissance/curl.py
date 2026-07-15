"""
Инструменты curl.
"""

from cai.tools.common import run_command  # pylint: disable=import-error
from cai.sdk.agents import function_tool


@function_tool
def curl(args: str = "", target: str = "", ctf=None) -> str:
    """
    Простой инструмент curl для выполнения HTTP-запросов к указанной цели.

    Args:
        args: Дополнительные аргументы для команды curl
        target: Целевой URL для запроса

    Returns:
        str: Вывод выполнения команды curl
    """
    command = f"curl {args} {target}"
    return run_command(command, ctf=ctf)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("curl", curl, categories=['recon', 'web'])
