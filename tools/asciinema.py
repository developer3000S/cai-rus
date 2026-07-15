#!/usr/bin/env python3
"""
Инструмент для записи сессий asciinema JSONL файлов воспроизведения.

Использование:
    cai-asciinema path/to/file.jsonl 0.5

Этот инструмент оборачивает запись asciinema для захвата сессий воспроизведения.
"""

import argparse
import os
import subprocess
import sys


def parse_arguments():
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Запись сессий asciinema JSONL файлов воспроизведения.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  cai-asciinema path/to/file.jsonl 0.5
  cai-asciinema conversation.jsonl 1.0
""",
    )

    parser.add_argument("jsonl_file", help="Путь к JSONL файлу, содержащему историю разговоров")

    parser.add_argument("replay_delay", type=float, help="Время в секундах ожидания между действиями")

    parser.add_argument(
        "--output", "-o", type=str, help="Путь к выходному файлу для записи (необязательно)"
    )

    return parser.parse_args()


def main():
    """Основная функция для записи сессии asciinema."""
    args = parse_arguments()

    # Проверка существования JSONL файла
    if not os.path.exists(args.jsonl_file):
        print(f"Ошибка: Файл {args.jsonl_file} не найден", file=sys.stderr)
        sys.exit(1)

    # Построение команды для записи с использованием того же интерпретатора Python
    replay_command = f"{sys.executable} tools/replay.py {args.jsonl_file} {args.replay_delay}"

    # Построение команды asciinema
    asciinema_cmd = ["asciinema", "rec", f"--command={replay_command}", "--overwrite"]

    # Добавление выходного файла при указании
    if args.output:
        asciinema_cmd.append(args.output)

    print(f"Запись сессии asciinema для {args.jsonl_file} с задержкой {args.replay_delay}s...")
    print(f"Running: {' '.join(asciinema_cmd)}")

    try:
        # Выполнение команды asciinema
        result = subprocess.run(asciinema_cmd, check=True)
        # result = subprocess.run(replay_command, check=True)
        print("Запись успешно завершена!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Ошибка: Запись asciinema не удалась с кодом выхода {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Ошибка: asciinema не найден. Пожалуйста, сначала установите asciinema.", file=sys.stderr)
        print("Установите с помощью: pip install asciinema", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
