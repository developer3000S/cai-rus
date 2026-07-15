#!/usr/bin/env python3
"""
Инструмент для создания GIF записей JSONL файлов воспроизведения.

Использование:
    cai-gif path/to/file.jsonl 0.5 output.gif

Этот инструмент оборачивает запись asciinema и agg для создания GIF анимаций.
"""

import argparse
import os
import subprocess
import sys
import tempfile


def parse_arguments():
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Создание GIF записей JSONL файлов воспроизведения.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  cai-gif path/to/file.jsonl 0.5 output.gif
  cai-gif conversation.jsonl 1.0 demo.gif
""",
    )

    parser.add_argument("jsonl_file", help="Путь к JSONL файлу, содержащему историю разговоров")

    parser.add_argument("replay_delay", type=float, help="Время в секундах ожидания между действиями")

    parser.add_argument("output_gif", help="Путь к выходному GIF файлу")

    return parser.parse_args()


def check_dependencies():
    """Проверка установки необходимых инструментов."""
    missing_deps = []

    # Проверка asciinema
    try:
        subprocess.run(["asciinema", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("asciinema")

    # Проверка agg
    try:
        subprocess.run(["agg", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("agg")

    if missing_deps:
        print("Ошибка: Отсутствуют необходимые зависимости:", file=sys.stderr)
        if "asciinema" in missing_deps:
            print("  - asciinema: Установите с помощью 'pip install asciinema'", file=sys.stderr)
        if "agg" in missing_deps:
            print("  - agg: Установите с помощью 'npm install -g @asciinema/agg'", file=sys.stderr)
        sys.exit(1)


def main():
    """Основная функция для создания GIF записи."""
    args = parse_arguments()
    check_dependencies()

    # Проверка существования JSONL файла
    if not os.path.exists(args.jsonl_file):
        print(f"Ошибка: Файл {args.jsonl_file} не найден", file=sys.stderr)
        sys.exit(1)

    # Создание временного файла для asciinema cast
    with tempfile.NamedTemporaryFile(suffix=".cast", delete=False) as temp_cast:
        temp_cast_path = temp_cast.name

    try:
        # Построение команды для записи с использованием того же интерпретатора Python
        replay_command = f"{sys.executable} tools/replay.py {args.jsonl_file} {args.replay_delay}"

        # Построение команды asciinema
        asciinema_cmd = [
            "asciinema",
            "rec",
            f"--command={replay_command}",
            "--overwrite",
            temp_cast_path,
        ]

        print(
            f"Запись сессии asciinema для {args.jsonl_file} с задержкой {args.replay_delay}s..."
        )
        print(f"Running: {' '.join(asciinema_cmd)}")

        # Выполнение команды asciinema
        subprocess.run(asciinema_cmd, check=True)

        # Конвертация cast файла в GIF с помощью agg
        print(f"Конвертация записи в GIF: {args.output_gif}")
        agg_cmd = ["agg", temp_cast_path, args.output_gif]
        subprocess.run(agg_cmd, check=True)

        print("Создание GIF успешно завершено!")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"Ошибка: Команда не удалась с кодом выхода {e.returncode}", file=sys.stderr)
        return e.returncode
    except Exception as e:  # pylint: disable=broad-except
        print(f"Ошибка: {str(e)}", file=sys.stderr)
        return 1
    finally:
        # Очистка временного cast файла
        try:
            os.unlink(temp_cast_path)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
