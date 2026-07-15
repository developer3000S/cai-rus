"""REPL `/workspace` (`/ws`): именованная метка рабочего пространства, пути хоста и файловые операции с учётом контейнера."""

import json
import os
import subprocess
from subprocess import CompletedProcess
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel

from cai.repl.commands.base import Command, register_command
from cai.repl.commands.env_catalog import set_env_var
from cai.repl.ui.banner import _CAI_GREEN, _quick_guide_subpanel_title
from cai.tools.common import _get_container_workspace_path, _get_workspace_dir

console = Console()


def _ws_accent_open() -> str:
    return f"bold {_CAI_GREEN}"


def _ws_panel(body: str, title: str) -> Panel:
    return Panel(
        body,
        title=_quick_guide_subpanel_title(title),
        title_align="left",
        padding=(1, 1),
        border_style=_CAI_GREEN,
    )


def _docker_mkdir_p(container_id: str, remote_path: str) -> CompletedProcess[str]:
    return subprocess.run(
        ["docker", "exec", container_id, "mkdir", "-p", remote_path],
        capture_output=True,
        text=True,
        check=False,
    )


def _resolve_workspace_display(
    workspace_name: Optional[str], active_container: str
) -> Tuple[str, str]:
    """Return (environment label, workspace directory path shown to the user)."""
    if not active_container:
        return "Host System", _get_workspace_dir()
    try:
        result = subprocess.run(
            ["docker", "inspect", active_container],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return "Host System (container not running)", _get_workspace_dir()
        container_info = json.loads(result.stdout)
        if not container_info:
            return "Host System (container not running)", _get_workspace_dir()
        image = container_info[0].get("Config", {}).get("Image", "unknown")
        env_name = f"Container ({image})"
        if workspace_name:
            workspace_dir = f"/workspace/workspaces/{workspace_name}"
            _docker_mkdir_p(active_container, workspace_dir)
        else:
            workspace_dir = "/"
        return env_name, workspace_dir
    except Exception:
        return "Host System (error inspecting container)", _get_workspace_dir()


def _print_no_active_container_for_copy() -> None:
    """Explain how to activate a container when /workspace copy cannot run."""
    g = _ws_accent_open()
    body = (
        f"[yellow]No active Docker container.[/yellow] "
        f"[bold {_CAI_GREEN}]/workspace copy[/bold {_CAI_GREEN}] requires "
        f"[dim]CAI_ACTIVE_CONTAINER[/dim] set to a running container ID.\n\n"
        "[bold]How to set it up:[/bold]\n"
        f"[dim]• From the REPL:[/dim] [{g}]/virtualization pull kalilinux/kali-rolling[/{g}] "
        f"[dim]then[/dim] [{g}]/virtualization run kalilinux/kali-rolling[/{g}] "
        f"[dim](short:[/dim] [{g}]/virt …[/{g}][dim]).[/dim]\n"
        f"[dim]• Re-attach:[/dim] [{g}]/virt set <container_id>[/{g}] [dim]or[/dim] "
        f"[{g}]/virt <container_id>[/{g}] [dim](sets CAI_ACTIVE_CONTAINER).[/dim]\n"
        "[dim]• From your shell before launching cai:[/dim] "
        "[dim]export CAI_ACTIVE_CONTAINER=<id>[/dim]\n"
        f"[dim]• More help:[/dim] [{g}]/h virtualization[/{g}] [dim]and[/dim] [{g}]/h workspace[/{g}]"
    )
    console.print(_ws_panel(body, "Copy"))


class WorkspaceCommand(Command):
    """Команда для управления рабочим пространством в Docker-контейнерах или локально."""

    def __init__(self):
        """Initialize the workspace command."""
        super().__init__(
            name="/workspace",
            description=(
                "Установить или отобразить имя текущего рабочего пространства и управлять файлами. "
                "Влияет на именование файлов журналов и место хранения файлов."
            ),
            aliases=["/ws"],
        )

        self.add_subcommand("set", "Установить имя текущего рабочего пространства", self.handle_set)
        self.add_subcommand(
            "get",
            "Показать имя, окружение и пути рабочего пространства (используйте ls для списка файлов)",
            self.handle_get,
        )
        self.add_subcommand("ls", "Показать файлы в рабочем пространстве", self.handle_ls_subcommand)
        self.add_subcommand(
            "exec", "Выполнить команду в рабочем пространстве", self.handle_exec_subcommand
        )
        self.add_subcommand(
            "copy", "Копировать файлы между хостом и контейнером", self.handle_copy_subcommand
        )

    def handle(self, args: Optional[List[str]] = None) -> bool:
        """Handle the workspace command."""
        if not args:
            return self.handle_get()
        if args[0] in self.subcommands:
            return super().handle(args)
        return self.handle_unknown_subcommand(args[0])

    def handle_no_args(self) -> bool:
        """Handle the command when no arguments are provided."""
        return self.handle_get()

    def handle_get(self, _: Optional[List[str]] = None) -> bool:
        """Display the current workspace name and directory information."""
        workspace_name = os.getenv("CAI_WORKSPACE", None)
        active_container = os.getenv("CAI_ACTIVE_CONTAINER", "")
        env_name, workspace_dir = _resolve_workspace_display(workspace_name, active_container)

        g = _ws_accent_open()
        lines = [
            f"Текущее рабочее пространство: [bold {_CAI_GREEN}]{workspace_name or 'Нет'}[/bold {_CAI_GREEN}]",
            f"Рабочее окружение: [bold]{env_name}[/bold]",
            f"Каталог рабочего пространства: [bold]{workspace_dir}[/bold]",
            "",
            f"[{g}]Доступные команды:[/{g}]",
            f"• [{g}]/workspace set <name>[/{g}] [dim]—[/dim] Установить имя рабочего пространства",
            f"• [{g}]/workspace ls[/{g}] [dim]—[/dim] Показать файлы в рабочем пространстве",
            f"• [{g}]/workspace exec <cmd>[/{g}] [dim]—[/dim] Выполнить команду в рабочем пространстве",
            f"• [{g}]/workspace copy <src> <dst>[/{g}] [dim]—[/dim] "
            "Копировать между хостом и контейнером; [bold]container:[/bold] на ровно одном пути",
        ]
        if not active_container:
            lines.append(
                f"  [dim]copy требует CAI_ACTIVE_CONTAINER — см. [/dim][{g}]/h virtualization[/{g}]"
            )
        lines.append("")
        lines.append(
            f"[dim]List files with [{g}]/workspace ls[/{g}] or [{g}]/ws ls[/{g}] "
            "(optional path relative to workspace).[/dim]"
        )
        console.print(_ws_panel("\n".join(lines), "Workspace"))

        return True

    def handle_set(self, args: Optional[List[str]] = None) -> bool:
        """Set the current workspace name"""
        if not args or len(args) != 1:
            g = _ws_accent_open()
            body = (
                f"[{g}]Использование:[/{g}] [{g}]/workspace set <workspace_name>[/{g}]\n\n"
                "[dim]Имена рабочих пространств должны быть простыми метками (буквы/цифры/_/-), "
                "а не путями файловой системы.[/dim]\n"
                f"[dim]Пример:[/dim] [{g}]/workspace set pentest_lab[/{g}]"
            )
            console.print(_ws_panel(body, "Set workspace"))
            return False

        workspace_name = args[0]
        if not all(c.isalnum() or c in ["_", "-"] for c in workspace_name):
            body = (
                "[red]Неверное имя рабочего пространства. "
                "Используйте только буквы, цифры, подчёркивания или дефисы.[/red]\n\n"
                "[dim]Не включайте разделители путей, такие как '/' или '\\'.[/dim]\n"
                "[dim]Допустимые примеры: mylab, red_team_01, client-a[/dim]"
            )
            console.print(_ws_panel(body, "Set workspace"))
            return False

        if not set_env_var("CAI_WORKSPACE", workspace_name):
            console.print("[red]Не удалось установить переменную окружения рабочего пространства.[/red]")
            return False

        new_workspace_dir = _get_workspace_dir()

        try:
            os.makedirs(new_workspace_dir, exist_ok=True)
        except OSError as e:
            console.print(f"[red]Ошибка создания каталога хоста {new_workspace_dir}: {e}[/red]")

        active_container = os.getenv("CAI_ACTIVE_CONTAINER", "")
        if active_container:
            check_process = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Running}}", active_container],
                capture_output=True,
                text=True,
                check=False,
            )

            if check_process.returncode == 0 and "true" in check_process.stdout.lower():
                container_workspace_path = _get_container_workspace_path()
                try:
                    mkdir_result = _docker_mkdir_p(active_container, container_workspace_path)
                    if mkdir_result.returncode == 0:
                        console.print(
                            f"[dim]Создан каталог рабочего пространства в контейнере: {container_workspace_path}[/dim]"
                        )
                    else:
                        console.print(
                            "[yellow]Предупреждение: Не удалось создать каталог рабочего пространства в контейнере: "
                            f"{mkdir_result.stderr}[/yellow]"
                        )
                except Exception as e:
                    console.print(
                        f"[yellow]Предупреждение: Не удалось настроить рабочее пространство в контейнере: {str(e)}[/yellow]"
                    )

        body = (
            f"Рабочее пространство изменено на: [bold {_CAI_GREEN}]{workspace_name}[/bold {_CAI_GREEN}]\n"
            f"Новый каталог рабочего пространства: [bold]{new_workspace_dir}[/bold]"
        )
        console.print(_ws_panel(body, "Рабочее пространство обновлено"))

        return True

    def handle_ls_subcommand(self, args: Optional[List[str]] = None) -> bool:
        """Handle the ls subcommand."""
        host_workspace_dir = _get_workspace_dir()
        active_container = os.getenv("CAI_ACTIVE_CONTAINER", "")

        if active_container:
            container_workspace_path = _get_container_workspace_path()

            target_path_in_container = container_workspace_path
            if args:
                target_path_in_container = os.path.join(container_workspace_path, args[0])

            _docker_mkdir_p(active_container, container_workspace_path)

            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    active_container,
                    "ls",
                    "-la",
                    target_path_in_container,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                console.print(result.stdout)
                return True

            fb = (
                f"[yellow]Failed to list files in container:[/yellow] [dim]{result.stderr}[/dim]\n"
                "[yellow]Falling back to host system…[/yellow]"
            )
            console.print(_ws_panel(fb, "List"))

        target_path_on_host = host_workspace_dir
        if args:
            target_path_on_host = os.path.join(host_workspace_dir, args[0])

        dir_to_ensure = (
            os.path.dirname(target_path_on_host)
            if "." in os.path.basename(target_path_on_host)
            else target_path_on_host
        )
        try:
            os.makedirs(dir_to_ensure, exist_ok=True)
        except OSError as e:
            console.print(f"[red]Error creating directory {dir_to_ensure} on host: {e}[/red]")

        try:
            result = subprocess.run(
                ["ls", "-la", target_path_on_host],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                console.print(result.stdout)
                return True
            console.print(f"[red]Error listing files: {result.stderr}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False

    def handle_exec_subcommand(self, args: Optional[List[str]] = None) -> bool:
        """Handle the exec subcommand."""
        if not args:
            g = _ws_accent_open()
            body = (
                f"[{g}]Usage:[/{g}] [{g}]/workspace exec <command>[/{g}] "
                f"[dim]or[/dim] [{g}]/ws exec <command>[/{g}]"
            )
            console.print(_ws_panel(body, "Exec"))
            return False

        command = " ".join(args)
        host_workspace_dir = _get_workspace_dir()
        active_container = os.getenv("CAI_ACTIVE_CONTAINER", "")

        if active_container:
            try:
                container_workspace_path = _get_container_workspace_path()
                _docker_mkdir_p(active_container, container_workspace_path)

                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        "-w",
                        container_workspace_path,
                        active_container,
                        "sh",
                        "-c",
                        command,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                console.print(f"[dim]$ {command}[/dim]")
                if result.stdout:
                    console.print(result.stdout)

                if result.stderr:
                    console.print(f"[yellow]{result.stderr}[/yellow]")

                if result.returncode != 0:
                    console.print(
                        _ws_panel(
                            "[yellow]Command failed in container. Trying on host…[/yellow]",
                            "Exec",
                        )
                    )
                    return self._exec_on_host(command, host_workspace_dir)

                return True
            except Exception as e:
                console.print(
                    _ws_panel(
                        f"[yellow]Error executing in container:[/yellow] [dim]{str(e)}[/dim]\n"
                        "[yellow]Falling back to host execution…[/yellow]",
                        "Exec",
                    )
                )

        return self._exec_on_host(command, host_workspace_dir)

    def _exec_on_host(self, command: str, workspace_dir: str) -> bool:
        """Execute a command on the host."""
        os.makedirs(workspace_dir, exist_ok=True)

        try:
            result = subprocess.run(
                command,
                shell=True,  # nosec B602
                capture_output=True,
                text=True,
                check=False,
                cwd=workspace_dir,
            )

            console.print(f"[dim]$ {command}[/dim]")
            if result.stdout:
                console.print(result.stdout)

            if result.stderr:
                console.print(f"[yellow]{result.stderr}[/yellow]")

            return result.returncode == 0
        except Exception as e:
            console.print(f"[red]Error executing command: {str(e)}[/red]")
            return False

    def handle_copy_subcommand(self, args: Optional[List[str]] = None) -> bool:
        """Handle the copy subcommand."""
        if not args or len(args) < 2:
            g = _ws_accent_open()
            body = (
                f"[{g}]Usage:[/{g}] [{g}]/workspace copy <source> <destination>[/{g}] "
                f"[dim]or[/dim] [{g}]/ws copy <source> <destination>[/{g}]\n\n"
                f"[dim]Exactly one path must use the[/dim] [bold {_CAI_GREEN}]container:[/bold {_CAI_GREEN}] "
                f"[dim]prefix; requires[/dim] [dim]CAI_ACTIVE_CONTAINER[/dim][dim].[/dim]"
            )
            console.print(_ws_panel(body, "Copy"))
            return False

        active_container = os.getenv("CAI_ACTIVE_CONTAINER", "")
        if not active_container:
            _print_no_active_container_for_copy()
            return False

        source = args[0]
        destination = args[1]

        if source.startswith("container:"):
            container_path = source[10:]
            host_path = destination

            if not container_path.startswith("/"):
                container_path = f"/workspace/{container_path}"

            try:
                result = subprocess.run(
                    ["docker", "cp", f"{active_container}:{container_path}", host_path],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0:
                    console.print(
                        _ws_panel(
                            f"[bold {_CAI_GREEN}]Copied[/bold {_CAI_GREEN}] "
                            f"[dim]from[/dim] [bold]container:{container_path}[/bold] "
                            f"[dim]to[/dim] [bold]{host_path}[/bold]",
                            "Copy",
                        )
                    )
                    return True
                console.print(f"[red]Error copying from container: {result.stderr}[/red]")
                return False
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                return False
        if destination.startswith("container:"):
            host_path = source
            container_path = destination[10:]

            if not container_path.startswith("/"):
                container_path = f"/workspace/{container_path}"

            try:
                result = subprocess.run(
                    ["docker", "cp", host_path, f"{active_container}:{container_path}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0:
                    console.print(
                        _ws_panel(
                            f"[bold {_CAI_GREEN}]Copied[/bold {_CAI_GREEN}] "
                            f"[dim]from[/dim] [bold]{host_path}[/bold] "
                            f"[dim]to[/dim] [bold]container:{container_path}[/bold]",
                            "Copy",
                        )
                    )
                    return True
                console.print(f"[red]Error copying to container: {result.stderr}[/red]")
                return False
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                return False

        g = _ws_accent_open()
        body = (
            "[yellow]Ambiguous copy direction.[/yellow] "
            f"[dim]Use the[/dim] [bold {_CAI_GREEN}]container:[/bold {_CAI_GREEN}] "
            f"[dim]prefix on source or destination.[/dim]\n\n"
            f"[{g}]Examples:[/{g}]\n"
            f"• [{g}]/workspace copy file.txt container:file.txt[/{g}] "
            "[dim]# host → container[/dim]\n"
            f"• [{g}]/workspace copy container:file.txt file.txt[/{g}] "
            "[dim]# container → host[/dim]"
        )
        console.print(_ws_panel(body, "Copy"))
        return False


register_command(WorkspaceCommand())
