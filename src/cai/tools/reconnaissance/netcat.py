"""
Инструменты для команды netcat
"""

from cai.tools.common import run_command  # pylint: disable=import-error
from cai.sdk.agents import function_tool


@function_tool
def netcat(host: str, port: int, data: str = "", args: str = "", ctf=None) -> str:
    """
    Простой инструмент netcat для подключения к указанному хосту и порту.
    Args:
        args: Дополнительные аргументы для команды netcat
        host: Целевой хост для подключения
        port: Целевой порт для подключения
        data: Данные для отправки на хост (необязательно)

    Returns:
        str: Вывод выполнения команды netcat
         или сообщение об ошибке при сбое подключения
    """
    try:
        if not isinstance(port, int):
            return "Ошибка: Порт должен быть целым числом"
        if port < 1 or port > 65535:
            return "Ошибка: Порт должен быть от 1 до 65535"

        if data:
            command = f'echo "{data}" | nc -w 3 {host} {port} {args}; exit'
        else:
            command = f'echo "" | nc -w 3 {host} {port} {args}; exit'

        result = run_command(command, ctf=ctf)

        return result
    except Exception as e:  # pylint: disable=broad-except
        return f"Ошибка выполнения команды netcat: {str(e)}"


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("netcat", netcat, categories=['recon', 'network'])
