#!/usr/bin/env python3
"""
Запуск эксперимента CTR - Интерфейс командной строки для интеграции CAI-CTR.

Эта оболочка делегирует `cai.ctr.experiment.main()`, который предоставляет
интерфейс на базе argparse. Он поддерживает обработку одного JSONL журнала
или директории JSONL журналов, а также необязательные флаги для режима CTF и
сеток скоростей атаки/защиты.

Примеры
=======
Запуск CTR над одним файлом журнала:
    cai-ctr --input_log ~/.cai/logs/session_2025-09-04.jsonl

Запуск CTR над всеми журналами в папке:
    cai-ctr --input_log ~/.cai/logs/

Указание скоростей и директории вывода:
    cai-ctr --input_log ./logs --attack_rate 1,2,3 --defense_rate 0,1 \
            --output_dir /tmp/cai/ctr

Показ справки:
    cai-ctr -h
"""

import sys
import os
import asyncio

# Добавление директории src в путь Python для редактируемых установок и прямых запусков
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from cai.ctr.experiment import main as experiment_main


def main() -> None:
    """Синхронная точка входа для консольного скрипта `cai-ctr`."""
    asyncio.run(experiment_main())


if __name__ == "__main__":
    main()
