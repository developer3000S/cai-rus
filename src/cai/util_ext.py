"""Расширенные утилиты для CAI"""
import base64
import hashlib
import json
import os
import platform
import random
import string
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

# Встроенный публичный ключ сервера
_K = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA98imbEha/70cxkfXIbyJ
dbpM6y7X+MWMVcdSTwAeb+jzLRfKzMZVXeEaYzkzH+STlDiqmb+XufX+guhmpyKz
RbV3rcJeM2s4QJ3OcsbOnxVG9Eyo6LrHu/aU71LOW8pPD5eIh0/BRCDojG56pZ8N
CFF0Rsfve6SH6waOibUoovMYu2ZfzzGb/oeyPsL8yb4fIqnOOH85FbAm8aCrpGNZ
6A8U67s6TQAnqLFn6x2h901K2GhNxweRQqJ5n2qwMCPLmEHyKZiLo8GbK3lrcnbj
j6qNKkgoL+b9rcYJ1toLP8btTHIyQX2N+gWVgxzMNPtDfCKIJm4Jag0fIEiVsNF2
QZ7NaMjRqtRs8WIzmUWBMVoyWqWCty6sNrum/uYZNCcNma855IeFEOrmYNzNEWxP
5xgJT/Hvs9/bTOUWqrB3L/8EGeV3hrhUZ1km25mogAnSOcFWviqObREc/1yTfsB4
Ln0Hv4tvILd74aBqG1zRF0Wjd25O7vl8oY3RBp7iCtrq+CdOI1jrTx4yo9JM/DKu
MfTbFI1YPjuJahQjbbKHvCKPKq6pxCQBZ91SsBHdM2tHLRXZ1olO0y0trety+fjx
T9W1tmmRU9QyFvS9LsKdjfBOzyprC5MCz740pctKkSspYn88R19N8Cu3MihaTUw6
/JHvKMwL2+DgFmF7Dqjc+jsCAwEAAQ==
-----END PUBLIC KEY-----"""

_V_URL = "https://api.aliasrobotics.com:665/v1/validate"
_I_URL = "https://api.aliasrobotics.com:666/key/info"

try:
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
    _crypto_available = True
except ImportError:
    try:
        from Cryptodome.Hash import SHA256
        from Cryptodome.PublicKey import RSA
        from Cryptodome.Signature import pkcs1_15
        _crypto_available = True
    except ImportError:
        _crypto_available = False


def _h() -> str:
    """Сгенерировать отпечаток системы"""
    p: list[str] = []
    try:
        n = uuid.getnode()
        if n:
            p.append(f"mac:{n:012x}")
    except Exception:
        pass
    for path in (Path("/etc/machine-id"), Path("/var/lib/dbus/machine-id")):
        try:
            if path.exists():
                v = path.read_text().strip()
                if v:
                    p.append(f"machine:{v}")
                    break
        except Exception:
            pass
    for g, l in ((platform.node, "node"), (platform.system, "system"), (platform.machine, "arch")):
        try:
            v = g()
            if v:
                p.append(f"{l}:{v}")
        except Exception:
            pass
    if not p:
        r = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        p.append("fallback:" + r)
    d = hashlib.sha256('|'.join(sorted(p)).encode()).hexdigest()
    return d[:32]


def _n(l: int = 32) -> str:
    """Сгенерировать одноразовый ключ"""
    a = string.ascii_letters + string.digits
    return ''.join(random.choice(a) for _ in range(l))


def _s(sig_b64: str, msg: str) -> bool:
    """Проверить подпись"""
    if not _crypto_available:
        return False
    try:
        k = RSA.import_key(_K)
        sig = base64.b64decode(sig_b64)
        h = SHA256.new(msg.encode('utf-8'))
        pkcs1_15.new(k).verify(h, sig)
        return True
    except Exception:
        return False


def _c(k: str) -> bool:
    """Проверить ключ через конечную точку info (httpx; та же семантика статусов что и legacy curl)."""
    try:
        import httpx

        timeout = httpx.Timeout(3.0, connect=3.0)
        with httpx.Client(timeout=timeout) as client:
            r = client.get(
                _I_URL,
                headers={"Authorization": f"Bearer {k}"},
            )
        code = r.status_code
        # 403 = виртуальный ключ (действителен для маршрутов LLM), 500/502/429 = прокси/лимит частоты
        return code in (200, 403, 500, 502, 429)
    except Exception:
        return False


def _v(k: str) -> bool:
    """Проверить ключ"""
    if not k or not k.strip():
        return False
    # Проверяем только действительность ключа через конечную точку /key/info (HTTP 200 = действителен)
    # Без машинно-специфичной проверки
    return _c(k)


def _license_off() -> bool:
    """Вернуть True если ``CAI_LICENSE_OFF`` установлен в истинное значение.

    При включении CAI работает в режиме открытого кода: проверка лицензии при запуске
    пропускается, а операции обновления направлены на публичный пакет PyPI ``cai-framework``
    вместо приватного индекса пакетов Alias.
    """
    return os.getenv("CAI_LICENSE_OFF", "").strip().lower() in ("1", "true", "yes")


def _chk() -> bool:
    """Проверить действительность лицензии.

    Установите ``CAI_LICENSE_OFF=1`` в окружении для полного пропуска проверки лицензии
    (например, для сборок с открытым кодом или локальной разработки).
    """
    if _license_off():
        return True
    k = os.getenv("ALIAS_API_KEY", "").strip()
    if not k:
        return False  # Ключ не установлен, отказ в операции
    return _v(k)


def check_system_dependencies() -> tuple[bool, list[str]]:
    """Проверить наличие необходимых системных зависимостей.
    
    Возвращает:
        Кортеж (всё_ок, отсутствующие_зависимости)
    """
    import shutil
    required = ["curl"]
    missing = [cmd for cmd in required if shutil.which(cmd) is None]
    return (len(missing) == 0, missing)


def display_missing_dependencies_error(missing: list[str]) -> None:
    """Отобразить понятное сообщение об ошибке для отсутствующих зависимостей."""
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console(stderr=True)
    deps_list = "\n".join(f"  • {dep}" for dep in missing)
    
    install_hint = ""
    if "curl" in missing:
        install_hint = (
            "\n[yellow]Подсказки по установке:[/yellow]\n"
            "  • Debian/Ubuntu: [cyan]sudo apt-get install curl[/cyan]\n"
            "  • macOS:         [cyan]brew install curl[/cyan]"
        )
    
    console.print(
        Panel(
            f"[bold red]Отсутствуют необходимые системные зависимости[/bold red]\n\n"
            f"Требуются следующие системные команды:\n\n"
            f"{deps_list}\n"
            f"{install_hint}",
            title="[red]Ошибка зависимости[/red]",
            border_style="red"
        )
    )


def pip_index_timeout_seconds() -> int:
    """Тайм-аут для ``pip index`` в :func:`check_for_updates` (``CAI_UPDATE_PIP_TIMEOUT``, по умолчанию 10)."""
    try:
        v = int(os.getenv("CAI_UPDATE_PIP_TIMEOUT", "10"))
    except ValueError:
        return 10
    return max(3, min(v, 120))


def user_env_requests_auto_framework_update() -> bool:
    """Вернуть True только если пользователь явно включил автоустановку через окружение.

    ``CAI_AUTO_UPDATE`` должен быть **наличествовать** в :data:`os.environ` (например, из ``export`` или
    ``.env`` перед запуском процесса). Если ключ отсутствует, при запуске всегда будет запрос.
    При наличии значение должно быть истинным (``1``, ``true``, ``yes``, ``on``); любое другое
    значение (включая пустое) считается выключенным, чтобы случайный ``CAI_AUTO_UPDATE=``
    не приводил к автообновлению.
    """
    if "CAI_AUTO_UPDATE" not in os.environ:
        return False
    return os.getenv("CAI_AUTO_UPDATE", "").strip().lower() in ("1", "true", "yes", "on")


def check_for_updates() -> Optional[Dict[str, Any]]:
    """Проверить, доступно ли обновление для cai-framework.
    
    Возвращает:
        Словарь с информацией об обновлении если доступно, None если обновления нет или при ошибке
        {
            "current_version": "x.x.x",
            "latest_version": "y.y.y",
            "update_available": True
        }
    """
    try:
        import importlib.metadata
        import re
        
        # Получить текущую установленную версию
        try:
            current_version = importlib.metadata.version("cai-framework")
        except importlib.metadata.PackageNotFoundError:
            # Установка для разработки
            return None
            
        # В режиме OSS проверяем относительно публичного PyPI (ALIAS_API_KEY не требуется).
        # В противном случае используем приватный индекс Alias с проверкой API-ключа.
        oss_mode = _license_off()
        if oss_mode:
            pip_args = [
                sys.executable, "-m", "pip", "index", "versions",
                "--no-color",
                "cai-framework",
            ]
        else:
            k = os.getenv("ALIAS_API_KEY", "").strip()
            if not k:
                return None
            index_url = f"https://packages.aliasrobotics.com:664/{k}/"
            pip_args = [
                sys.executable, "-m", "pip", "index", "versions",
                "--index-url", index_url,
                "--no-color",
                "cai-framework",
            ]

        # Использовать pip index для проверки последней версии без скачивания
        result = subprocess.run(
            pip_args,
            capture_output=True,
            text=True,
            timeout=pip_index_timeout_seconds(),
        )
        
        if result.returncode != 0:
            return None
            
        # Разобрать вывод для поиска доступных версий
        output = result.stdout
        # Искать номера версий в выводе
        version_pattern = r'(\d+\.\d+\.\d+(?:\.\w+)?)'
        versions = re.findall(version_pattern, output)
        
        if not versions:
            return None
            
        # Отсортировать версии и получить последнюю
        from packaging import version as pkg_version
        sorted_versions = sorted(versions, key=pkg_version.parse, reverse=True)
        latest_version = sorted_versions[0] if sorted_versions else None
        
        if not latest_version:
            return None
            
        # Сравнить версии
        update_available = pkg_version.parse(latest_version) > pkg_version.parse(current_version)
        return {
            "current_version": current_version,
            "latest_version": latest_version,
            "update_available": update_available,
        }

    except Exception:
        # Молча завершать — не прерывать нормальную работу
        pass

    return None


def prompt_for_update(update_info: Dict[str, Any]) -> bool:
    """Предложить пользователю обновить CAI (стиль Rich совпадает с баннером сессии: CAI green / #004433 / серый)."""
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.table import Table
    from rich.text import Text

    from cai.repl.ui.banner import CAI_GREEN

    _grey_mid = "#888888"
    _grey = "dim white"

    console = Console()

    title = Text()
    title.append(" CAI ", style="bold #0d1117 on #00ff9d")
    title.append(" Доступна новая версия ", style="bold white on #004433")
    title.append(" ", style="on #004433")

    table = Table(
        show_header=False,
        box=box.SIMPLE_HEAD,
        border_style=_grey_mid,
        padding=(0, 1),
        collapse_padding=True,
    )
    table.add_column(style=_grey, no_wrap=True)
    table.add_column()
    table.add_row(
        "Установлена",
        Text(update_info["current_version"], style="italic white"),
    )
    table.add_row(
        "Последняя",
        Text(update_info["latest_version"], style=f"bold {CAI_GREEN}"),
    )

    panel = Panel(
        table,
        title=title,
        title_align="left",
        border_style=CAI_GREEN,
        expand=False,
        padding=(0, 1),
        subtitle="[dim white]Из вашего индекса пакетов Alias[/dim white]",
        subtitle_align="left",
    )

    console.print()
    console.print(panel)
    console.print()

    from rich.theme import Theme
    styled_console = Console(theme=Theme({
        "prompt.choices": f"bold {CAI_GREEN}",
        "prompt.default": CAI_GREEN,
    }))
    return Confirm.ask(
        f"[bold {CAI_GREEN}]Обновить сейчас?[/bold {CAI_GREEN}] [dim white](по умолчанию: нет — требуется явное подтверждение)[/dim white]",
        default=False,
        console=styled_console,
    )


def perform_update(api_key: str) -> bool:
    """Выполнить обновление через pip для cai-framework.

    Аргументы:
        api_key: ALIAS_API_KEY для аутентификации в приватном индексе пакетов Alias.
            Игнорируется при установленном ``CAI_LICENSE_OFF=1``, в котором
            случае обновление загружается из публичного PyPI.

    Возвращает:
        True если обновление успешно, False в противном случае
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text

    from cai.repl.ui.banner import CAI_GREEN

    console = Console()

    oss_mode = _license_off()
    if oss_mode:
        pip_args = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "cai-framework",
        ]
    else:
        index_url = f"https://packages.aliasrobotics.com:664/{api_key}/"
        pip_args = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--index-url",
            index_url,
            "--upgrade",
            "cai-framework",
        ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"[bold {CAI_GREEN}]Обновление cai-framework…[/bold {CAI_GREEN}]",
            total=None,
        )

        result = subprocess.run(
            pip_args,
            capture_output=True,
            text=True,
        )

        progress.update(task, completed=True)

    if result.returncode == 0:
        ok_line = Text()
        ok_line.append("✓ ", style=f"bold {CAI_GREEN}")
        ok_line.append("Обновление завершено", style="bold white")
        sub = Text()
        try:
            import importlib.metadata

            installed = importlib.metadata.version("cai-framework")
            sub.append(
                f"Установлен cai-framework {installed} (то же что и cai --version). ",
                style="dim white",
            )
        except Exception:
            pass
        sub.append("Перезапустите CAI для загрузки новой версии.", style="italic dim white")
        console.print(
            Panel(
                Text.assemble(ok_line, "\n", sub),
                border_style=CAI_GREEN,
                padding=(0, 1),
                title=Text.assemble(
                    (" CAI ", "bold #0d1117 on #00ff9d"),
                    (" Готово ", "bold white on #004433"),
                    (" ", "on #004433"),
                ),
                title_align="left",
            )
        )
        return True

    err = Text()
    err.append("Обновление не удалось", style="bold white")
    err.append("\n", "")
    err.append(result.stderr or "(нет деталей)", style="dim white")
    console.print(
        Panel(
            err,
            border_style="red",
            title="[bold white]CAI[/bold white]",
            title_align="left",
        )
    )
    return False
