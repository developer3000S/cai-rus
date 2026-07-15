"""
Инструмент SSH Pass для выполнения удаленных команд через SSH с аутентификацией по паролю.

Пример обобщения: для выполнения локальной команды мы используем обертку bash
в `generic_linux_command` и в `execute_cli_command` -> `cai.tools.misc.cli_utils`
Используя эти обертки, команды типа `ssh` или `netcat` обычно блокируются
LLM, поэтому используется инженерия промптов для выполнения команды локально
и возврата результата. Другое решение — реализовать интерактивные CLI, на данный момент эта команда
покрывает все варианты использования SSH. Более логичная и простая реализация по сравнению с
`hackingbuddyGPT` `https://github.com/ipa-lab/hackingBuddyGPT`
Отлично обрабатывает повышение привилегий и автономно вводит пароли SSH,
что пока не встречалось в других фреймворках кибербезопасности (февраль 2025)
"""  # noqa: E501

from cai.tools.common import run_command  # pylint: disable=E0401 # noqa: E501
from cai.sdk.agents import function_tool

import shlex

@function_tool
def run_ssh_command_with_credentials(
    host: str, username: str, password: str, command: str, port: int = 22
) -> str:
    """
    Выполнение команды на удаленном хосте через SSH с аутентификацией по паролю.

    Args:
        host: Адрес удаленного хоста
        username: Имя пользователя SSH
        password: Пароль SSH
        command: Команда для выполнения на удаленном хосте
        port: Порт SSH (по умолчанию: 22)

    Returns:
        str: Вывод выполнения удаленной команды
    """

    # # Escape special characters in password and command to prevent shell injection
    # #
    # # NOTE: evolved into using shlex for better shell escaping
    # escaped_password = password.replace("'", "'\\''")
    # escaped_command = command.replace("'", "'\\''")

    try:
        port = int(port)
        if port <= 0 or port > 65535:
            return "Порт не является допустимым целым числом"
    except Exception:
        return "Порт не является допустимым целым числом"

    # Escape special characters to prevent shell injection
    quoted_password = shlex.quote(password)
    quoted_username = shlex.quote(username)
    quoted_host = shlex.quote(host)
    quoted_command = shlex.quote(command)
    port = str(port)

    ssh_command = (
        f"sshpass -p {quoted_password} "
        f"ssh -o StrictHostKeyChecking=no "
        f"{quoted_username}@{quoted_host} -p {port} "
        f"{quoted_command}"
    )
    return run_command(ssh_command)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("run_ssh_command_with_credentials", run_ssh_command_with_credentials, categories=['c2', 'lateral_movement'])
