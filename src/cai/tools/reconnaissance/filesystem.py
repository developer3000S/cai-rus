"""
Инструменты CLI для выполнения команд.
"""

from cai.tools.common import run_command  # pylint: disable=E0401
from cai.sdk.agents import function_tool


@function_tool
def list_dir(path: str, args: str = "", ctf=None) -> str:
    """
    Вывод содержимого директории.
    по умолчанию .
    Args:
        path: Путь к директории для вывода содержимого
        args: Дополнительные аргументы для команды ls

    Returns:
        str: Вывод выполнения команды ls
    """
    command = f"ls {path} {args}"
    return run_command(command, ctf=ctf)


@function_tool
def cat_file(file_path: str, args: str = "", ctf=None) -> str:
    """
    Вывод содержимого файла.

    Args:
        args: Дополнительные аргументы для команды cat
        file_path: Путь к файлу для вывода содержимого

    Returns:
        str: Вывод выполнения команды cat
    """
    command = f"cat {args} {file_path} "
    return run_command(command, ctf=ctf)


# FileSearchTool
# ListDirTool
# TextSearchTool
# FileAnalysisTool
# StringExtractionTool
# ReadFileTool
# FilePermissionsTool
# FileCompressionTool


@function_tool
def pwd_command(ctf=None) -> str:
    """
    Получение текущей рабочей директории.

    Returns:
        str: Абсолютный путь текущей рабочей директории
    """
    command = "pwd"
    return run_command(command, ctf=ctf)


@function_tool
def find_file(file_path: str, args: str = "", ctf=None) -> str:
    """
    Поиск файла в файловой системе.
    """
    command = f"find {file_path} {args}"
    return run_command(command, ctf=ctf)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("list_dir", list_dir, categories=["recon", "misc"])
TOOL_REGISTRY.register("cat_file", cat_file, categories=["recon", "misc"])
TOOL_REGISTRY.register("pwd_command", pwd_command, categories=["recon", "misc"])
TOOL_REGISTRY.register("find_file", find_file, categories=["recon", "misc"])
