# NetworkConnectionstool in exploitFlow
"""
Инструмент Netstat
"""

from cai.tools.common import run_command  # pylint: disable=import-error
from cai.sdk.agents import function_tool


@function_tool
def netstat(args: str = "", ctf=None) -> str:
    """
    Инструмент netstat для вывода всех слушающих портов и связанных с ними программ.
    Args:
        args: Дополнительные аргументы для команды netstat
    Returns:
        str: Вывод выполнения команды netstat
    """
    command = f"netstat -tuln {args}"
    return run_command(command, ctf=ctf)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("netstat", netstat, categories=["recon", "network"])
