# План перевода проекта CAI на русский язык

## Цель
Перевести все пользовательские строки интерфейса (CLI, REPL, TUI), сообщения об ошибках, подсказки, описания инструментов, документацию и примеры на русский язык.

## Ограничение области
- **Переводятся**: строки, которые видит конечный пользователь (help-тексты, сообщения `print`/`console.print`, prompt-инструкции для LLM, описания инструментов, `README.md`, примеры).
- **Не переводятся**: внутренние комментарии разработчика, docstrings (кроме пользовательских docstrings в CLI), имена переменных, ключи конфигурации, технические термины без устоявшегося перевода.

## Чанки

### Чанк 1: Точка входа CLI (`src/cai/cli.py`)
- **Файлы**: `src/cai/cli.py`
- **Сложность**: simple
- **Что переводить**: help-тексты `argparse`, сообщения запуска (`Starting CAI framework...`, `Verifying license...`, `Checking for framework updates...`, `Update available`, `is up to date`, `Authentication Error`, `Continuing startup`, `Loading parallel agent configuration...`), `--version` вывод.
- **Критерии приёмки**: `python -m cai --help` показывает русские тексты; `--version` выводит русскую строку; сообщения при старте на русском.

### Чанк 2: Headless REPL — основной цикл (`src/cai/cli_headless.py`, часть 1)
- **Файлы**: `src/cai/cli_headless.py` (строки 1–900 примерно)
- **Сложность**: complex (много строк, форматирование Rich)
- **Что переводить**: сообщения о лимитах (`Maximum turn limit`, `Maximum interaction limit`, `Price limit reached`), авто-продолжение, переключение агента, начальный prompt, ошибки потоковой передачи, CTF-статусы (`Correct flag submitted`, `Incorrect flag`).
- **Критерии приёмки**: интерактивный headless-режим отображает статусы на русском; тесты `pytest tests/` проходят (или не ломаются из-за изменений строк).

### Чанк 3: Headless REPL — параллельное выполнение и финал (`src/cai/cli_headless.py`, часть 2)
- **Файлы**: `src/cai/cli_headless.py` (строки 900–конец)
- **Сложность**: complex
- **Что переводить**: таблицы сводки параллельных агентов (`Agent`, `Status`, `Result`, `Tokens`, `Cost`), сообщения о завершении сессии, логирование, сообщения об ошибках выполнения.
- **Критерии приёмки**: режим `--yaml` с несколькими агентами выводит русские заголовки таблиц и сообщения.

### Чанк 4: UI запуска и баннеры (`src/cai/repl/ui/`)
- **Файлы**: `src/cai/repl/ui/startup_hints.py`, `src/cai/repl/ui/banner.py`, `src/cai/repl/ui/agent_notices.py`
- **Сложность**: simple
- **Что переводить**: startup-хинты (`Starting CAI framework...`, `Loading agents...`, `Connecting to model...`), баннер/справка, BETA-значки агентов.
- **Критерии приёмки**: при старте TUI/headless все подсказки на русском; `python -m cai --tui` (если запускается) показывает русский баннер.

### Чанк 5: Инструменты — исполнитель и сетевая часть (`src/cai/tools/executor.py`, `src/cai/tools/container.py`, `src/cai/tools/network/capture_traffic.py`)
- **Файлы**: `src/cai/tools/executor.py`, `src/cai/tools/container.py`, `src/cai/tools/network/capture_traffic.py`
- **Сложность**: simple
- **Что переводить**: сообщения о выполнении команд (`Failed to start session`, `Container execution timed out`, `Attempting execution on host instead`, `Capture stopped`, `Error executing command`).
- **Критерии приёмки**: сообщения инструментов при ошибках/таймаутах на русском.

### Чанк 6: Инструменты — описания и prompt-инструкции
- **Файлы**: `src/cai/tools/*.py` (описания `__doc__` функций-инструментов), `src/cai/prompts/` (шаблоны)
- **Сложность**: complex (нужно сохранить семантику для LLM)
- **Что переводить**: docstrings функций инструментов, которые передаются LLM как `description`; системные промпты в `src/cai/prompts/`.
- **Критерии приёмки**: `python -c "from cai.tools... import ...; print(...__doc__)"` возвращает русский текст; тесты инструментов проходят.

### Чанк 7: README.md — доведение до полного русского
- **Файлы**: `README.md`
- **Сложность**: simple
- **Что переводить**: оставшиеся английские разделы (бейджи/ссылки оставить, перевести текст): Key Features, Note, Warning, Impact, Competitions, Research Impact, Installation, Setup, Architecture, Quickstart, Environment Variables, OpenRouter, Azure, MCP, Development, Contributions, FAQ и т.д.
- **Критерии приёмки**: весь текст README.md на русском (кроме имён продуктов, бейджей, ссылок).

### Чанк 8: Примеры и документация (`examples/`, `docs/`)
- **Файлы**: `examples/**/*.py`, `docs/**/*.md` (если есть пользовательские строки)
- **Сложность**: simple
- **Что переводить**: комментарии-пояснения в примерах, выводимые строки, пользовательские docstrings.
- **Критерии приёмки**: примеры читаемы на русском; не ломаются при запуске.

## Порядок выполнения
1. Чанк 1 → Чанк 4 (независимые, можно параллельно)
2. Чанк 2 → Чанк 3 (последовательно, один большой файл)
3. Чанк 5 → Чанк 6 (инструменты)
4. Чанк 7 (README)
5. Чанк 8 (примеры)
6. Проверка: `ruff check src/cai tests`, `pytest tests/ -x --timeout 30`

## Примечания
- Не переводить технические термины, для которых нет устоявшегося русского эквивалента, без пояснений (например, CTF, API, LLM, YAML, HTTP).
- Сохранить форматирование Rich (`[bold red]...[/bold red]`).
- После перевода прогнать тесты, чтобы изменение строк не сломало asserts.
