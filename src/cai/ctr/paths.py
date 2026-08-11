"""
Утилиты путей CTR.

Предоставляет единый источник истины для того, куда записываются и откуда читаются
артефакты запусков CTR. Использует переопределение через переменную окружения,
если она задана, или системную временную директорию для переносимости между платформами.
"""

from __future__ import annotations

import os
import tempfile
from typing import Optional


def get_ctr_output_base_dir(override: Optional[str] = None) -> str:
    """Определить базовую директорию для выходных данных CTR.

    Порядок приоритета:
    - Явное переопределение, переданное в функцию
    - Переменная окружения `CAI_CTR_OUTPUT_DIR`
    - Системная временная директория по пути `<tempdir>/cai/ctr`
    """
    base = (
        override
        or os.getenv("CAI_CTR_OUTPUT_DIR")
        or os.path.join(tempfile.gettempdir(), "cai", "ctr")
    )
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        # В крайнем случае возвращаемся к tempdir без вложенных папок
        base = os.path.join(tempfile.gettempdir(), "ctr")
        os.makedirs(base, exist_ok=True)
    return base
