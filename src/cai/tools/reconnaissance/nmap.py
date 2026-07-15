"""
Инструменты nmap.
"""

from cai.tools.common import run_command  # pylint: disable=E0401
from cai.sdk.agents import function_tool


@function_tool
def nmap(args: str, target: str, ctf=None) -> str:
    """
    Простой инструмент nmap для сканирования указанной цели.

    Args:
        args: Дополнительные аргументы для команды nmap
        target: Целевой хост или IP-адрес для сканирования

    Returns:
        str: Вывод выполнения команды nmap
    """
    command = f"nmap {args} {target}"
    return run_command(command, ctf=ctf, stream=True)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("nmap", nmap, categories=['recon', 'network'])
