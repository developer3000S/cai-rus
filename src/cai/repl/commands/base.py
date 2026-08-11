"""
Базовый модуль команд CAI REPL.
Этот модуль предоставляет базовую структуру для всех команд в CAI REPL.
"""

from typing import List, Optional, Dict, Any, Callable, Tuple
from rich.console import Console  # pylint: disable=import-error
from difflib import get_close_matches

console = Console()


class Command:
    """Базовый класс для всех команд."""

    def __init__(self, name: str, description: str, aliases: List[str] = None):
        """Инициализировать команду.

        Args:
            name: Имя команды (например, "/memory")
            description: Краткое описание команды
            aliases: Необязательный список псевдонимов команды
        """
        self.name = name
        self.description = description
        self.aliases = aliases or []
        self.subcommands: Dict[str, Dict[str, Any]] = {}

    def add_subcommand(self, name: str, description: str, handler: Callable):
        """Добавить подкоманду к данной команде.

        Args:
            name: Имя подкоманды (например, "list")
            description: Краткое описание подкоманды
            handler: Функция, вызываемая при выполнении подкоманды
        """
        self.subcommands[name] = {"description": description, "handler": handler}

    def get_subcommands(self) -> List[str]:
        """Получить список всех имён подкоманд.

        Returns:
            Список имён подкоманд
        """
        return list(self.subcommands.keys())

    def get_subcommand_description(self, subcommand: str) -> str:
        """Получить описание подкоманды.

        Args:
            subcommand: Имя подкоманды

        Returns:
            Описание подкоманды
        """
        return self.subcommands.get(subcommand, {}).get("description", "")

    def handle(self, args: Optional[List[str]] = None) -> bool:
        """Обработать команду.

        Args:
            args: Необязательный список аргументов команды

        Returns:
            True, если команда успешно обработана, False в противном случае
        """
        if not args:
            return self.handle_no_args()

        subcommand = args[0]
        if subcommand in self.subcommands:
            handler = self.subcommands[subcommand]["handler"]
            return handler(args[1:] if len(args) > 1 else None)

        return self.handle_unknown_subcommand(subcommand)

    def handle_no_args(self) -> bool:
        """Обработать команду, когда аргументы не переданы.

        Returns:
            True, если команда успешно обработана, False в противном случае
        """
        subcommands = ", ".join(self.get_subcommands())
        console.print(f"[yellow]{self.name} command requires a subcommand: {subcommands}[/yellow]")
        return False

    def handle_unknown_subcommand(self, subcommand: str) -> bool:
        """Обработать неизвестную подкоманду.

        Args:
            subcommand: Неизвестная подкоманда

        Returns:
            True, если команда успешно обработана, False в противном случае
        """
        console.print(f"[red]Unknown {self.name} subcommand: {subcommand}[/red]")
        return False


# Реестр всех команд
COMMANDS: Dict[str, Command] = {}
COMMAND_ALIASES: Dict[str, str] = {}


def register_command(command: Command) -> None:
    """Зарегистрировать команду в глобальном реестре.

    Args:
        command: Команда для регистрации
    """
    COMMANDS[command.name] = command

    # Регистрируем псевдонимы
    for alias in command.aliases:
        COMMAND_ALIASES[alias] = command.name


def get_command(name: str) -> Optional[Command]:
    """Получить команду по имени или псевдониму.

    Args:
        name: Имя или псевдоним команды

    Returns:
        Команда, если найдена, иначе None
    """
    # Проверяем, является ли это псевдонимом
    name = COMMAND_ALIASES.get(name, name)

    return COMMANDS.get(name)


def find_closest_command(command: str) -> Optional[str]:
    """Найти ближайшую совпадающую команду для ошибочно введённой команды.
    
    Args:
        command: Ошибочно введённая команда
        
    Returns:
        Ближайшая совпадающая команда или None
    """
    # Убираем ведущий слэш, если есть
    command_without_slash = command.lstrip("/")
    
    # Получаем все команды и псевдонимы
    all_commands = [cmd.lstrip("/") for cmd in COMMANDS.keys()]
    all_commands.extend(list(COMMAND_ALIASES.keys()))
    
    # Находим ближайшее совпадение
    matches = get_close_matches(command_without_slash, all_commands, n=1, cutoff=0.6)
    
    if matches:
        match = matches[0]
        # Проверяем, является ли это псевдонимом
        if match in COMMAND_ALIASES:
            # Получаем реальную команду и обеспечиваем одиночный слэш
            actual_cmd = COMMAND_ALIASES[match]
            return "/" + actual_cmd.lstrip("/")
        else:
            # Обеспечиваем одиночный слэш
            return "/" + match.lstrip("/")

    return None


def handle_command(command: str, args: Optional[List[str]] = None) -> bool:
    """Обработать команду.

    Args:
        command: Имя команды или псевдоним
        args: Необязательный список аргументов команды

    Returns:
        True, если команда успешно обработана, False в противном случае
    """
    cmd = get_command(command)
    if cmd:
        return cmd.handle(args)

    return False


def handle_command_with_autocorrect(command: str, args: Optional[List[str]] = None, auto_correct: bool = True) -> Tuple[bool, Optional[str]]:
    """Обработать команду с поддержкой автокоррекции.

    Args:
        command: Имя команды или псевдоним
        args: Необязательный список аргументов команды
        auto_correct: Выполнять ли автокоррекцию и исполнение ошибочно введённых команд

    Returns:
        Кортеж (команда_обработана, предложенная_команда)
    """
    cmd = get_command(command)
    if cmd:
        return (cmd.handle(args), None)
    
    # Команда не найдена, пытаемся найти ближайшее совпадение
    suggested = find_closest_command(command)
    
    if suggested and auto_correct:
        cmd = get_command(suggested)
        if cmd:
            return (cmd.handle(args), suggested)
    
    return (False, suggested)
