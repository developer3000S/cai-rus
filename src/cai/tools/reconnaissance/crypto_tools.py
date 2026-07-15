"""
Криптоинструменты
"""

from cai.tools.common import run_command
from cai.sdk.agents import function_tool


# # URLDecodeTool
# # HexDumpTool
# # Base64DecodeTool
# # ROT13DecodeTool
# # BinaryAnalysisTool


@function_tool
def strings_command(file_path: str, ctf=None) -> str:
    """
        Извлечение печатаемых строк из бинарного файла.

    #     Args:
    #         args: Additional arguments to pass to the strings command
    #         file_path: Path to the binary file to extract strings from

    #     Returns:
            str: Вывод выполнения команды strings
    """
    command = f"strings {file_path}"
    return run_command(command, ctf=ctf)


@function_tool
def decode64(input_data: str, ctf=None) -> str:
    """
    Декодирование строки, закодированной в base64.

    Args:
        input_data: Строка в формате base64 для декодирования
        args: Дополнительные аргументы (не используются в этой функции)

    Returns:
        str: Декодированная строка
    """
    command = f"base64 --decode {input_data}"
    return run_command(command, ctf=ctf)


@function_tool
def decode_hex_bytes(input_data: str) -> str:
    """
    Декодирование строки шестнадцатеричных байтов в текст ASCII.

    Формат ввода:
    "0xFF 0x00 0x63..."
    Args:
        input_data: Строка, содержащая шестнадцатеричные байты

    Returns:
        str: Декодированный текст ASCII
    """
    try:
        # Split the input string and convert hex strings to bytes
        hex_bytes = [int(x, 16) for x in input_data.split() if x.startswith("0x")]
        # Convert bytes to ASCII string
        decoded = bytes(hex_bytes).decode("ascii")
        return decoded
    except (ValueError, UnicodeDecodeError) as e:
        return f"Ошибка декодирования шестнадцатеричных байтов: {str(e)}"


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("strings_command", strings_command, categories=["recon", "misc"])
TOOL_REGISTRY.register("decode64", decode64, categories=["recon", "misc"])
TOOL_REGISTRY.register("decode_hex_bytes", decode_hex_bytes, categories=["recon", "misc"])
