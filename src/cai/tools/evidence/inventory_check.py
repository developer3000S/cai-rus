"""Проверка полноты покрытия инвентаризаций в стиле CSV/YAML в выводе агента."""

from __future__ import annotations

import csv
import os
import re
from pathlib import Path

from cai.sdk.agents import function_tool


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_ids_from_csv(path: Path, id_pattern: re.Pattern[str], id_column: str | None) -> set[str]:
    text = _read_text(path)
    if not text.strip():
        return set()

    # Try structured CSV first when a column is named.
    try:
        reader = csv.DictReader(text.splitlines())
        if reader.fieldnames:
            target_col = id_column
            if not target_col:
                for name in reader.fieldnames:
                    if name and id_pattern.search(name):
                        target_col = name
                        break
                if not target_col:
                    for name in reader.fieldnames:
                        sample = name or ""
                        if id_pattern.search(sample):
                            target_col = name
                            break
            if target_col and target_col in (reader.fieldnames or []):
                found: set[str] = set()
                for row in reader:
                    val = (row.get(target_col) or "").strip()
                    for match in id_pattern.finditer(val):
                        found.add(match.group(0))
                if found:
                    return found
    except csv.Error:
        pass

    return set(id_pattern.findall(text))


def _extract_ids_from_response(response_text: str, id_pattern: re.Pattern[str]) -> set[str]:
    if not response_text.strip():
        return set()
    return set(id_pattern.findall(response_text))


@function_tool
def verify_csv_inventory(
    file_path: str,
    id_pattern: str = r"PAsset-\d+",
    id_column: str = "",
    response_text: str = "",
) -> str:
    """
    Подсчет ID инвентаризации в CSV/текстовом файле и сравнение с ID, упомянутыми в выводе агента.

    Используйте, когда пользователь просит проверить каждый PAsset-XX (или аналогичный) в таблице:
    1) Запустите этот инструмент с путем к CSV перед завершением задачи.
    2) Передайте ваш последний текст оценки в response_text.
    3) Сообщите пользователю о пропущенных ID и продолжайте, пока пропущенных не останется.

    Args:
        file_path: Путь к CSV или текстовой инвентаризации (абсолютный или относительно рабочей области).
        id_pattern: Регулярное выражение для одного токена ID (по умолчанию PAsset-NN).
        id_column: Необязательное имя столбца CSV, содержащего ID; определяется автоматически, если пусто.
        response_text: Необязательный текст ответа агента для проверки покрытия файла.

    Returns:
        Сводка с общим количеством ID в файле, найденными ID в response_text и пропущенными ID.
    """
    path = Path(os.path.expanduser(file_path.strip()))
    if not path.is_file():
        return f"Ошибка: файл инвентаризации не найден: {path}"

    try:
        pattern = re.compile(id_pattern)
    except re.error as exc:
        return f"Ошибка: недопустимое регулярное выражение id_pattern: {exc}"

    col = id_column.strip() or None
    file_ids = sorted(_extract_ids_from_csv(path, pattern, col), key=str)
    total = len(file_ids)

    if not file_ids:
        return (
            f"Нет ID, соответствующих шаблону {id_pattern!r} в {path}.\n"
            "Проверьте id_pattern/id_column или кодировку файла."
        )

    lines = [
        f"Файл инвентаризации: {path}",
        f"Шаблон ID: {id_pattern}",
        f"Всего уникальных ID в файле: {total}",
    ]

    if response_text.strip():
        response_ids = _extract_ids_from_response(response_text, pattern)
        missing = [i for i in file_ids if i not in response_ids]
        extra = sorted(response_ids - set(file_ids))
        covered = total - len(missing)
        lines.extend(
            [
                f"ID упомянуто в response_text: {len(response_ids)}",
                f"Покрыто (в файле ∩ ответе): {covered}/{total}",
            ]
        )
        if missing:
            preview = ", ".join(missing[:30])
            suffix = f" ... (+{len(missing) - 30} more)" if len(missing) > 30 else ""
            lines.append(f"ОТСУТСТВУЕТ в ответе ({len(missing)}): {preview}{suffix}")
        else:
            lines.append("ОТСУТСТВУЕТ в ответе: нет — полное покрытие.")
        if extra:
            lines.append(f"Лишние ID в ответе (нет в файле): {', '.join(extra[:20])}")
    else:
        preview = ", ".join(file_ids[:40])
        suffix = f" ... (+{total - 40} more)" if total > 40 else ""
        lines.append(f"Список ID (первые 40): {preview}{suffix}")
        lines.append(
            "Совет: запустите снова с response_text, установленным на вашу оценку, чтобы получить пропущенные ID."
        )

    return "\n".join(lines)


from cai.tool_registry import TOOL_REGISTRY  # noqa: E402

TOOL_REGISTRY.register(
    "verify_csv_inventory",
    verify_csv_inventory,
    categories=["compliance", "misc"],
)
