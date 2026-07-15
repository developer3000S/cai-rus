# FileDownloadTool in exploitFlow

"""
Инструмент Wget
"""

from cai.tools.common import run_command  # pylint: disable=import-error
from cai.sdk.agents import function_tool


@function_tool
def wget(url: str, args: str = "", ctf=None) -> str:
    """
    Инструмент Wget для загрузки файлов из интернета.
    Args:
        url: URL файла для загрузки
        args: Дополнительные аргументы для команды wget

    Returns:
        str: Вывод выполнения команды wget
    """
    command = f"wget {args} {url}"
    return run_command(command, ctf=ctf)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("wget", wget, categories=['recon', 'web'])
