#!/usr/bin/env python3
"""
Пример:

CAI_MODEL="claude-sonnet-4-20250514" CAI_STREAM=True python3 case_study_generator.py --jsonl_file logs/cai_b97af8fc-3d51-45d3-8393-6c3341d33807_20250602_201144_luijait_darwin_24.5.0_81_38_189_27.jsonl --output_php_file alias_web/case_study_test.php

Генератор кейсов CAI - Генерация PHP кейсов из JSONL файлов.

Этот скрипт загружает контекст из JSONL файлов с помощью того же механизма, что и команда /load CAI,
запускает агент UseCase с потоковым выводом и генерирует PHP кейсы.

Использование:
    python case_study_generator.py --jsonl_file logs/session.jsonl --output_php_file output.php
    python case_study_generator.py --jsonl_file logs/last --output_php_file case_studies/latest.php
"""

import os
from dotenv import load_dotenv

# Загрузка .env только из текущей директории, не из родительских директорий
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path=dotenv_path, verbose=False)

# Установка значения по умолчанию для OPENAI_API_KEY, если он еще не установлен
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = ""

import sys
import asyncio
import argparse
from pathlib import Path
import json
import re
from typing import List, Dict, Any, Optional

# Импорт компонентов CAI SDK
from cai.sdk.agents import Runner
from cai.sdk.agents.models.openai_chatcompletions import message_history, add_to_message_history
from cai.sdk.agents.run_to_jsonl import load_history_from_jsonl
from cai.sdk.agents.stream_events import RunItemStreamEvent
from cai.sdk.agents.items import ToolCallOutputItem

# Импорт агента UseCase
from src.cai.agents.usecase import use_case_agent

# Rich консоль для лучшего вывода
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def extract_php_code(text: str) -> Optional[str]:
    """Извлечение PHP кода из блоков кода markdown."""
    if not text:
        return None

    # Попытка извлечения PHP кода между ```php и ```
    php_matches = re.findall(r"```php\n(.*?)```", text, re.DOTALL)
    if php_matches:
        return php_matches[0].strip()

    # Если блоков кода нет, проверяем, не выглядит ли весь текст как PHP
    if text.strip().startswith("<?php") or text.strip().startswith("<!doctype"):
        return text.strip()

    return None


async def generate_case_study(jsonl_file: str, output_php_file: str) -> Optional[str]:
    """
    Генерация PHP кейса из JSONL файла с использованием потокового вывода.

    Аргументы:
        jsonl_file: Путь к JSONL файлу для загрузки контекста
        output_php_file: Путь для сохранения PHP вывода

    Возвращает:
        Путь к сохраненному PHP файлу или None в случае неудачи
    """
    # Очистка любых существующих сообщений в message_history для начала с чистого листа
    message_history.clear()

    # Загрузка контекста из JSONL файла (имитация команды /load)
    try:
        console.print(f"[yellow]Загрузка JSONL файла: {jsonl_file}[/yellow]")
        messages = load_history_from_jsonl(jsonl_file)

        if not messages:
            console.print("[red]Ошибка: Сообщения не найдены в JSONL файле[/red]")
            return None

        console.print(f"[green]✓ Загружено {len(messages)} сообщений из JSONL[/green]")

        # Добавление сообщений в message_history (точно как делает команда /load)
        for message in messages:
            message_history.append(message)

        # Отображение сводки загруженного контекста
        user_messages = sum(1 for msg in messages if msg.get("role") == "user")
        assistant_messages = sum(1 for msg in messages if msg.get("role") == "assistant")
        tool_messages = sum(1 for msg in messages if msg.get("role") == "tool")

        console.print(
            Panel(
                f"Контекст загружен:\n"
                f"• Сообщений пользователей: {user_messages}\n"
                f"• Сообщений ассистента: {assistant_messages}\n"
                f"• Сообщений инструментов: {tool_messages}",
                title="[bold]Сводка контекста JSONL[/bold]",
                border_style="blue",
            )
        )

    except Exception as e:
        console.print(f"[red]Ошибка загрузки JSONL файла: {str(e)}[/red]")
        return None

    # Анализ загруженного контекста для предоставления лучших рекомендаций
    context_summary = []
    if messages:
        # Find the main topic/challenge from user messages
        for msg in messages:
            if msg.get("role") == "user" and msg.get("content"):
                content = msg.get("content", "")[:300]  # First 300 chars
                if content and len(content) > 20:  # Skip very short messages
                    context_summary.append(content.strip())
                    if len(context_summary) >= 5:  # Get first few meaningful messages
                        break

    # Генерация промпта для кейса с контекстом
    prompt = "Сгенерируйте PHP код для кейса по кибербезопасности на основе шаблона. "
    prompt += "Проанализируйте загруженный контекст разговора и создайте подробный кейс. "
    prompt += "Заполните все разделы TEMPLATE-TODO соответствующей информацией из сессии. "
    prompt += "Подробно объясните проблему и решение в этом сценарии"
    prompt += "Вывод должен быть полным PHP кодом, готовым к сохранению в файл."

    # Добавление сводки разговора JSONL к промпту
    if messages:
        prompt += "\n\n## Контекст разговора из JSONL:\n"

        # Получение ключевой информации из разговора
        user_msgs = [msg for msg in messages if msg.get("role") == "user"]
        assistant_msgs = [msg for msg in messages if msg.get("role") == "assistant"]
        tool_msgs = [msg for msg in messages if msg.get("role") == "tool"]

        # Добавление сообщений пользователей
        if user_msgs:
            prompt += "\n### Сообщения пользователей:\n"
            for i, msg in enumerate(user_msgs[:5], 1):
                content = msg.get("content", "")[:500]
                if content:
                    prompt += f"{i}. {content}\n"

        # Добавление ключевых ответов ассистента
        if assistant_msgs:
            prompt += "\n### Ключевые ответы ассистента:\n"
            for i, msg in enumerate(assistant_msgs[:3], 1):
                content = msg.get("content", "")[:500]
                if content and "I'll help" not in content:  # Пропуск универсальных ответов
                    prompt += f"{i}. {content}\n"

        # Добавление выводов инструментов, которые могут содержать важные данные
        if tool_msgs:
            prompt += "\n### Выводы инструментов (ключевые находки):\n"
            important_tools = []
            for msg in tool_msgs:
                content = msg.get("content", "")
                # Look for important patterns in tool output
                if any(
                    keyword in content.lower()
                    for keyword in [
                        "map",
                        "credential",
                        "password",
                        "auth",
                        "endpoint",
                        "192.168",
                        "http",
                    ]
                ):
                    important_tools.append(content[:500])

            for i, content in enumerate(important_tools[:5], 1):
                prompt += f"{i}. {content}\n"

    console.print(f"\n[cyan]Генерация кейса с агентом UseCase...[/cyan]")

    # Настройка потокового режима на основе переменной окружения
    stream_mode = os.getenv("CAI_STREAM", "true").lower() != "false"

    try:
        if stream_mode:
            # Потоковый режим - аналогично реализации CLI
            console.print("[dim]Использование потокового режима...[/dim]")

            # Отслеживание наличия вывода
            has_output = False
            accumulated_text = []
            php_code = None

            # Запуск потокового процесса как в CLI
            async def process_streamed_response():
                try:
                    result_stream = Runner.run_streamed(use_case_agent, prompt)

                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                        transient=True,
                    ) as progress:
                        task = progress.add_task(
                            "[cyan]Processing with UseCase agent...", total=None
                        )

                        # Потребление событий для выполнения асинхронного генератора
                        async for event in result_stream.stream_events():
                            if isinstance(event, RunItemStreamEvent):
                                # Handle tool outputs
                                if event.name == "tool_output" and isinstance(
                                    event.item, ToolCallOutputItem
                                ):
                                    progress.update(
                                        task,
                                        description=f"[cyan]Tool: {event.item.raw_item.get('name', 'unknown')}...",
                                    )

                                    # Добавление сообщения инструмента в историю (как в CLI)
                                    tool_msg = {
                                        "role": "tool",
                                        "tool_call_id": event.item.raw_item["call_id"],
                                        "content": event.item.output,
                                    }
                                    add_to_message_history(tool_msg)

                        progress.update(task, description="[green]Завершение вывода...")

                    # Результат доступен после завершения потоковой передачи
                    # Но нам нужно извлечь вывод из message_history
                    # поскольку потоковая передача не обеспечивает прямой доступ к финальному выводу

                    # Получение последнего сообщения ассистента из message_history
                    for msg in reversed(message_history):
                        if msg.get("role") == "assistant" and msg.get("content"):
                            return msg.get("content")

                    return None

                except Exception as e:
                    console.print(f"[red]Ошибка в потоковой передаче: {str(e)}[/red]")
                    import traceback

                    console.print(f"[red]{traceback.format_exc()}[/red]")
                    return None

            # Запуск потокового процесса
            final_output = await process_streamed_response()

            if final_output:
                php_code = extract_php_code(final_output)
                if not php_code:
                    php_code = final_output

            if php_code:
                console.print(f"[green]✓ Сгенерировано {len(php_code)} символов вывода[/green]")
            else:
                console.print("[red]Ошибка: Нет вывода от агента UseCase[/red]")
                return None

        else:
            # Непотоковый режим (проще, как в примерах)
            console.print("[dim]Использование непотокового режима...[/dim]")

            # Показ прогресса
            with console.status("[bold green]Генерация кейса...") as status:
                # Вместо передачи истории разговоров напрямую,
                # просто используем промпт со всем встроенным контекстом
                # Это избегает проблем с неполными парами вызов/ответ инструмента

                # Запуск только с промптом
                result = await Runner.run(use_case_agent, prompt)

            # Извлечение PHP кода из результата
            if hasattr(result, "final_output") and result.final_output:
                output_text = result.final_output

                # Обработка вывода для обработки выводов инструментов
                for item in result.new_items:
                    if isinstance(item, ToolCallOutputItem):
                        # Добавление сообщений инструментов в историю
                        tool_msg = {
                            "role": "tool",
                            "tool_call_id": item.raw_item["call_id"],
                            "content": item.output,
                        }
                        add_to_message_history(tool_msg)

                php_code = extract_php_code(output_text)
                if not php_code:
                    # Если извлечение не удалось, используем необработанный вывод
                    php_code = output_text

                console.print(f"[green]✓ Сгенерировано {len(php_code)} символов вывода[/green]")
            else:
                console.print("[red]Ошибка: Нет вывода от агента UseCase[/red]")
                return None

    except Exception as e:
        console.print(f"[red]Ошибка генерации кейса: {str(e)}[/red]")
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/red]")
        return None

    # Валидация PHP кода
    if not php_code or len(php_code) < 100:
        console.print("[red]Ошибка: Сгенерированный вывод слишком короткий или недопустимый[/red]")
        return None

    # Save PHP code to file
    try:
        output_path = Path(output_php_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(php_code)

        console.print(f"\n[green]✓ PHP кейс сохранен в: {output_php_file}[/green]")

        # Отображение размера файла и предварительного просмотра
        file_size = output_path.stat().st_size
        console.print(f"[dim]File size: {file_size:,} bytes[/dim]")

        # Показ первых строк как предварительный просмотр
        lines = php_code.split("\n")[:15]
        preview = "\n".join(lines)
        if len(php_code.split("\n")) > 15:
            preview += "\n..."

        console.print(Panel(preview, title="[bold]Предварительный просмотр PHP файла[/bold]", border_style="blue"))

        return str(output_path)

    except Exception as e:
        console.print(f"[red]Ошибка сохранения PHP файла: {str(e)}[/red]")
        return None


def parse_args():
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Генерация PHP кейсов из JSONL файлов с помощью агента CAI UseCase.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Генерация кейса из конкретного JSONL файла
  python case_study_generator.py --jsonl_file logs/session_20240102_123456.jsonl --output_php_file case_studies/ctf_writeup.php
  
  # Использование последнего журнала сессии (поведение по умолчанию, как команда /load)
  python case_study_generator.py --jsonl_file logs/last --output_php_file case_studies/latest.php
  
  # Генерация с пользовательской директорией вывода
  python case_study_generator.py --jsonl_file logs/last --output_php_file ~/Documents/case_studies/analysis.php
  
  # Переопределение модели
  python case_study_generator.py --jsonl_file logs/last --output_php_file output.php --model gpt-4o
  
  # Отключение потоковой передачи
  CAI_STREAM=false python case_study_generator.py --jsonl_file logs/last --output_php_file output.php
        """,
    )
    parser.add_argument(
        "--jsonl_file",
        type=str,
        default="logs/last",
        help="Путь к JSONL файлу, содержащему контекст разговора (по умолчанию: logs/last)",
    )
    parser.add_argument(
        "--output_php_file",
        type=str,
        required=True,
        help="Путь, по которому будет сохранен сгенерированный PHP файл",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Переопределение используемой модели (например, claude-sonnet-4-20250514, gpt-4o)",
    )
    return parser.parse_args()


async def main():
    """Основная точка входа для скрипта."""
    args = parse_args()

    # Отображение баннера
    console.print(
        Panel(
            "[bold cyan]Генератор кейсов CAI[/bold cyan]\n"
            "Генерация профессиональных кейсов по кибербезопасности из журналов сессий JSONL\n\n"
            "[dim]Этот инструмент использует агент CAI UseCase для анализа контекста сессии и генерации\n"
            "подробных PHP кейсов на основе истории разговоров.[/dim]",
            border_style="cyan",
        )
    )

    # Переопределение модели при указании
    if args.model:
        os.environ["CAI_MODEL"] = args.model
        console.print(f"[yellow]Использование переопределения модели: {args.model}[/yellow]")

    current_model = os.getenv("CAI_MODEL", "alias1")
    console.print(f"[yellow]Модель: {current_model}[/yellow]")

    # Проверка существования JSONL файла
    jsonl_path = Path(args.jsonl_file)
    if not jsonl_path.exists() and args.jsonl_file != "logs/last":
        console.print(f"[red]Ошибка: JSONL файл не найден: {args.jsonl_file}[/red]")
        return 1

    # Генерация кейса
    result = await generate_case_study(args.jsonl_file, args.output_php_file)

    if result:
        console.print("\n[bold green]✨ Генерация кейса успешно завершена![/bold green]")
        console.print(f"[dim]Теперь вы можете открыть {result} в браузере или редакторе[/dim]")
        return 0
    else:
        console.print("\n[bold red]❌ Генерация кейса не удалась[/bold red]")
        console.print("[dim]Пожалуйста, проверьте сообщения об ошибках выше и убедитесь:[/dim]")
        console.print("[dim]1. JSONL файл содержит допустимые данные сессии[/dim]")
        console.print("[dim]2. Агент UseCase имеет доступ к файлу шаблона[/dim]")
        console.print("[dim]3. Ваши API ключи правильно настроены[/dim]")
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
