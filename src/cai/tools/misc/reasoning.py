"""
Модуль инструментов рассуждений для отслеживания мыслей, находок и анализа
Предоставляет утилиты для записи и получения ключевой информации, обнаруженной
в ходе прохождения CTF.
"""

from cai.sdk.agents import function_tool


@function_tool
def thought(
    breakdowns: str = "",
    reflection: str = "",  # pylint: disable=too-many-arguments  # noqa: E501
    action: str = "",
    next_step: str = "",
    key_clues: str = "",
    ctf=None,
) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Инструмент для выражения детальных мыслей и анализа во время boot2root CTF.

    Args:
        breakdowns: Детальный разбор текущей ситуации/находок
        reflection: Размышления о прогрессе и полученных выводах
        action: Текущие или запланированные действия
        next_step: Следующие шаги
        key_clues: Важные улики или подсказки
        ctf: Объект CTF для использования в контексте
    Returns:
        str: Форматированная строка, содержащая указанные мысли и анализ
    """
    output = []
    if breakdowns:
        output.append(f"Thought: {breakdowns}")
    if reflection:
        output.append(f"Reflection: {reflection}")
    if action:
        output.append(f"Action: {action}")
    if next_step:
        output.append(f"Next Step: {next_step}")
    if key_clues:
        output.append(f"Key Clues: {key_clues}")
    return "\n".join(output)


@function_tool
def write_key_findings(findings: str) -> str:
    """
    Запись ключевых находок в файл state.txt для отслеживания важных деталей CTF.
    Записывает только критическую информацию, такую как:
    - Обнаруженные учетные данные
    - Найденные уязвимости
    - Векторы повышения привилегий
    - Важные детали доступа к системе
    - Другие ключевые находки, необходимые для прогресса

    Args:
        findings: Строка, содержащая ключевые находки для добавления в state.txt

    Returns:
        Строка, подтверждающая запись находок
    """
    try:
        with open("state.txt", "a", encoding="utf-8") as f:
            f.write("\n" + findings + "\n")
        return f"Успешная запись находок в state.txt:\n{findings}"
    except OSError as e:
        return f"Ошибка записи в state.txt: {str(e)}"


@function_tool
def read_key_findings() -> str:
    """
    Чтение ключевых находок из файла state.txt для получения важных данных
    Получает критическую информацию, такую как:
    - Обнаруженные учетные данные
    - Найденные уязвимости
    - Векторы повышения привилегий
    - Важные детали доступа к системе
    - Другие ключевые находки, необходимые для прогресса

    Returns:
        Строка, содержащая все находки из state.txt, или сообщение об ошибке,
        если файл не найден
    """
    try:
        with open("state.txt", encoding="utf-8") as f:
            findings = f.read()
        return findings or "Нет находок"
    except FileNotFoundError:
        return "Файл state.txt не найден. Никакие находки не были записаны."
    except OSError as e:
        return f"Ошибка чтения state.txt: {str(e)}"


@function_tool
def think(thought: str) -> str:  # pylint: disable=unused-argument
    """
    Используйте инструмент для размышления о чем-либо.

    Он не получит новую информацию и не изменит базу данных, а лишь добавит
    мысль в журнал. Используйте, когда необходимы сложные рассуждения или
    кэширование памяти.

    Args:
        thought: Мысль для размышления.
    Returns:
        str: Обработанная мысль
    """
    return f"{thought}"


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("thought", thought, categories=["misc"])
TOOL_REGISTRY.register("write_key_findings", write_key_findings, categories=["misc"])
TOOL_REGISTRY.register("read_key_findings", read_key_findings, categories=["misc"])
TOOL_REGISTRY.register("think", think, categories=["misc"])
