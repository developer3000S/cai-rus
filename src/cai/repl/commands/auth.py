"""
Команда авторизации для CAI REPL.

Эта команда позволяет добавлять пользователей и устройства в постоянную
базу данных аутентификации, используемую API CAI (`AuthManager`).

Типичное использование:

    /auth add-user <username> <password>
        Создать нового пользователя в общей БД аутентификации.

    /auth add-ip <device_ip[:port]>
        Создать случайного пользователя и токен сессии для указанного IP-адреса устройства
        и передать учётные данные на TCP-слушатель на устройстве
        (например, iOS-приложение) через простое JSON-рукопожатие.
"""

from __future__ import annotations

import json
import os
import socket
from typing import List, Optional

from rich.console import Console  # type: ignore[import]
from rich.panel import Panel  # type: ignore[import]

from cai.api.auth import AuthManager
from cai.repl.commands.base import Command, register_command

console = Console()


class AuthCommand(Command):
    """Команда для управления пользователями API и сопряжения устройств."""

    def __init__(self) -> None:
        super().__init__(
            name="/auth",
            description="Управление пользователями API-аутентификации и сопряжение устройств с сервером CAI",
            aliases=[],
        )
        self.add_subcommand(
            "add-user",
            "Добавить пользователя в БД аутентификации: /auth add-user <username> <password>",
            self.handle_add_user,
        )
        self.add_subcommand(
            "add-ip",
            "Сопрячь устройство по IP и передать учётные данные по TCP: /auth add-ip <ip[:port]>",
            self.handle_add_ip,
        )

    # /auth add-user <username> <password>
    def handle_add_user(self, args: Optional[List[str]] = None) -> bool:
        if not args or len(args) < 2:
            console.print(
                "[red]Использование:[/red] /auth add-user <username> <password>",
            )
            return False

        username, password = args[0], args[1]
        manager = AuthManager()
        try:
            user = manager.create_user(username, password)
        except Exception as exc:  # pragma: no cover - defensive
            console.print(f"[red]Не удалось создать пользователя:[/red] {exc}")
            return False

        console.print(
            Panel(
                f"Пользователь [bold]{user.username}[/bold] добавлен в базу данных аутентификации.",
                title="Аутентификация",
                border_style="green",
            )
        )
        return True

    # /auth add-ip <ip[:port]>
    def handle_add_ip(self, args: Optional[List[str]] = None) -> bool:
        if not args or not args[0]:
            console.print("[red]Использование:[/red] /auth add-ip <ip[:port]>")
            console.print("Пример: /auth add-ip 192.168.1.50 или /auth add-ip 192.168.1.50:10101")
            return False

        target = args[0]
        if ":" in target:
            host, port_str = target.rsplit(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                console.print(f"[red]Неверный порт в {target}[/red]")
                return False
        else:
            host = target
            port = int(os.getenv("CAI_AUTH_DEVICE_PORT", "10101"))

        # Determine API base URL to send to the device.
        # Priority:
        #   1. Explicit CAI_AUTH_BASE_URL
        #   2. CAI_AUTH_PUBLIC_HOST (if set)
        #   3. IP of the local interface used to reach the device
        #   4. CAI_API_HOST / 127.0.0.1 (last-resort fallback)
        base_url_env = os.getenv("CAI_AUTH_BASE_URL")
        api_host_env = os.getenv("CAI_AUTH_PUBLIC_HOST")
        api_port = int(os.getenv("CAI_AUTH_PUBLIC_PORT") or os.getenv("CAI_API_PORT", "8000"))
        if base_url_env:
            base_url = base_url_env
        else:
            if api_host_env:
                api_host = api_host_env
            else:
                # Try to infer the local IP address used to talk to the device.
                try:
                    tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    tmp_sock.connect((host, 1))
                    api_host = tmp_sock.getsockname()[0]
                    tmp_sock.close()
                except Exception:
                    api_host = os.getenv("CAI_API_HOST", "127.0.0.1")
            base_url = f"http://{api_host}:{api_port}/api/v1"

        manager = AuthManager()
        try:
            user, plain_password, session = manager.create_random_user_and_session_for_ip(host)
        except Exception as exc:  # pragma: no cover - defensive
            console.print(f"[red]Failed to create user/session:[/red] {exc}")
            return False

        payload = {
            "base_url": base_url,
            "username": user.username,
            "password": plain_password,
            "session_token": session.token,
        }

        console.print(
            f"[cyan]Connecting to device at[/cyan] [bold]{host}:{port}[/bold] "
            f"to deliver credentials...",
        )

        try:
            with socket.create_connection((host, port), timeout=10) as sock:
                data = json.dumps(payload).encode("utf-8")
                sock.sendall(data)
        except OSError as exc:
            console.print(
                Panel(
                    f"Failed to connect to device at {host}:{port}\n\n{exc}",
                    title="Ошибка сопряжения",
                    border_style="red",
                )
            )
            console.print(
                "[yellow]Убедитесь, что устройство слушает (например, iOS-приложение в "
                'режиме "Подключить сервер") и доступно в сети.[/yellow]'
            )
            return False

        console.print(
            Panel(
                "[green]Запрос на сопряжение устройства отправлен успешно.[/green]\n\n"
                f"Назначенный логин: [bold]{user.username}[/bold]\n"
                f"Случайный пароль: [bold]{plain_password}[/bold]\n"
                f"Токен сессии: [dim](скрыт, хранится в БД аутентификации сервера)[/dim]\n\n"
                f"Базовый URL API для устройства: [bold]{base_url}[/bold]",
                title="Сопряжение устройства",
                border_style="green",
            )
        )
        return True


# Register command on import
register_command(AuthCommand())
