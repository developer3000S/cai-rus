"""
Утилита простого парсера терминала
"""

import re
from typing import Tuple, List, Optional


def parse_terminal_target(args: List[str]) -> Tuple[List[str], Optional[int]]:
    """
    Разобрать целевой терминал из аргументов команды.
    
    Ищет спецификаторы терминала вида 't1', 'T2' и т.д. в конце аргументов.
    Также сохраняет 'all' для широковещательной рассылки на все терминалы.
    
    Args:
        args: Список аргументов команды
        
    Returns:
        Кортеж из (cleaned_args, terminal_number)
        - cleaned_args: Аргументы с удалённым спецификатором терминала (но 'all' сохраняется)
        - terminal_number: Номер терминала, если найден, иначе None
        
    Examples:
        ['gpt-4o', 't1'] -> (['gpt-4o'], 1)
        ['select', 'agent_name', 'T2'] -> (['select', 'agent_name'], 2)
        ['ping', '192.168.1.1', 'all'] -> (['ping', '192.168.1.1', 'all'], None)
        ['list'] -> (['list'], None)
    """
    if not args:
        return args, None
        
    last_arg = args[-1]
    
    # Проверяем, является ли аргумент "all" — сохраняем его в аргументах
    if last_arg.lower() == 'all':
        return args, None
    
    # Сопоставляем спецификаторы терминала: t1, T1, t2, T2 и т.д.
    match = re.match(r'^[tT](\d+)$', last_arg)
    if match:
        terminal_number = int(match.group(1))
        return args[:-1], terminal_number
    
    return args, None