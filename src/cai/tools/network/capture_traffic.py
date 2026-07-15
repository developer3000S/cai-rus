#!/usr/bin/env python3
import paramiko
import tempfile
import os
import subprocess
import time
import socket
import sys
from contextlib import contextmanager
from cai.sdk.agents import function_tool


@function_tool
def capture_remote_traffic(
    ip, username, password, interface, capture_filter="", port=22, timeout=10
):
    """
    Захватывает сетевой трафик с удалённой виртуальной машины и возвращает канал, который может быть прочитан tshark.

    Args:
        ip (str): IP-адрес удалённой виртуальной машины
        username (str): SSH имя пользователя для удалённой виртуальной машины
        password (str): SSH пароль для удалённой виртуальной машины
        interface (str): Сетевой интерфейс для захвата (например, eth0)
        capture_filter (str, optional): Фильтр tcpdump
        port (int, optional): SSH порт (по умолчанию: 22)
        timeout (int, optional): Тайм-аут подключения в секундах (по умолчанию: 10)

    Returns:
        subprocess.Popen: Процесс с stdout, который может быть прочитан tshark

    Raises:
        ConnectionError: Если подключение к удалённой виртуальной машине не удалось
        RuntimeError: Если запуск захвата трафика не удался
    """
    try:
        # Create SSH client and connect to remote VM
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Подключение к {ip}:{port} как {username}...")
        client.connect(ip, port=port, username=username, password=password, timeout=timeout)

        # Verify interface exists
        _, stdout, stderr = client.exec_command(f"ip link show {interface}")
        if stdout.channel.recv_exit_status() != 0:
            error = stderr.read().decode().strip()
            raise RuntimeError(f"Интерфейс {interface} не найден: {error}")

        # Check if we have necessary permissions
        _, stdout, stderr = client.exec_command("which tcpdump")
        if stdout.channel.recv_exit_status() != 0:
            raise RuntimeError("tcpdump не найден в удалённой системе")

        # Build tcpdump command with filter if provided
        tcpdump_cmd = f"tcpdump -U -i {interface} -w - "
        if capture_filter:
            tcpdump_cmd += f"'{capture_filter}'"

        print(f"Запуск захвата на {ip}:{interface}...")

        # Start tcpdump process on remote machine and get its output
        stdin, stdout, stderr = client.exec_command(tcpdump_cmd)

        # Check if tcpdump started successfully (non-blocking check)
        time.sleep(1)
        if stdout.channel.exit_status_ready():
            error = stderr.read().decode().strip()
            raise RuntimeError(f"Не удалось запустить tcpdump: {error}")

        # Create a named pipe (FIFO) for tshark to read from
        fifo_path = tempfile.mktemp()
        os.mkfifo(fifo_path)

        # Start a process to read from SSH and write to the FIFO
        def pipe_ssh_to_fifo():
            try:
                with open(fifo_path, "wb") as fifo:
                    while True:
                        data = stdout.read(4096)
                        if not data:
                            break
                        fifo.write(data)
                        fifo.flush()
            except (BrokenPipeError, OSError) as e:
                print(f"Ошибка в pipe_ssh_to_fifo: {str(e)}")
            finally:
                print("Закрытие FIFO из-за ошибки или завершения.")

        import threading

        thread = threading.Thread(target=pipe_ssh_to_fifo, daemon=True)
        thread.start()

        print(f"Захват запущен. Данные доступны по адресу: {fifo_path}")
        print(f"Теперь вы можете использовать: tshark -r {fifo_path} -c 100 [опции]")

        # Example usage in the context manager
        subprocess.run(["tshark", "-r", fifo_path, "-c", "100"])

        return fifo_path

    except paramiko.AuthenticationException:
        raise ConnectionError("Аутентификация не удалась. Проверьте имя пользователя и пароль.")
    except paramiko.SSHException as e:
        raise ConnectionError(f"Ошибка SSH подключения: {str(e)}")
    except socket.timeout:
        raise ConnectionError(f"Подключение превысило тайм-аут после {timeout} секунд")
    except Exception as e:
        raise RuntimeError(f"Непредвиденная ошибка: {str(e)}")


@function_tool  # TODO: not ideal to decorete this context manager.
@contextmanager
def remote_capture_session(ip, username, password, interface, capture_filter="", port=22):
    """
    Менеджер контекста для удалённого захвата трафика с автоматической очисткой ресурсов.

    Использование:
        with remote_capture_session("192.168.1.100", "admin", "password", "eth0") as fifo_path:
            # Запуск tshark для чтения из FIFO
            subprocess.run(["tshark", "-r", fifo_path, "-T", "fields", "-e", "ip.src"])
    """
    fifo_path = None
    client = None

    try:
        fifo_path = capture_remote_traffic(
            ip, username, password, interface, capture_filter=capture_filter, port=port
        )
        yield fifo_path
    finally:
        if fifo_path and os.path.exists(fifo_path):
            try:
                os.unlink(fifo_path)
            except:
                pass


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 5:
        print("Использование: capture_traffic.py <ip> <username> <password> <interface> [фильтр]")
        sys.exit(1)

    ip = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    interface = sys.argv[4]
    capture_filter = sys.argv[5] if len(sys.argv) > 5 else ""

    try:
        with remote_capture_session(ip, username, password, interface, capture_filter) as fifo_path:
            # Keep the script running until interrupted
            print("Нажмите Ctrl+C для остановки захвата")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗахват остановлен")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("capture_remote_traffic", capture_remote_traffic, categories=['network', 'recon'])
TOOL_REGISTRY.register("remote_capture_session", remote_capture_session, categories=['network', 'recon'])
