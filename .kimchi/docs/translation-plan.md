# План перевода проекта CAI на русский язык
> **Цель:** перевести все пользовательские markdown-файлы и user-facing строки интерфейса на русский язык, сохранив код, команды, пути и форматирование.
> **Подход:** разделить файлы на 10 групп по ~12 файлов; каждую группу переводит отдельный Builder-агент с помощью локальной модели `gemma4:31b-cloud` (Ollama) через вспомогательный скрипт. Затем отдельный агент переводит строки CLI/REPL/TUI и запускает валидацию.
## Ограничения и правила перевода
1. Переводится только естественный язык (заголовки, абзацы, списки, описания).
2. НЕ переводятся: имена файлов/путей, команды shell, код в блоках и inline, имена переменных/функций, URL, названия инструментов/библиотек, маркдаун-разметка, Mako/Jinja-шаблоны (`<% ... %>`, `${...}`), значения в конфигах.
3. Ссылки и навигация в `mkdocs.yml` не меняются (пути файлов остаются прежними).
4. Если файл уже содержит качественный русский перевод (>20% кириллицы и понятный текст), агент пропускает его.
5. После перевода запускаются `pytest` (или минимальный набор тестов) и `mkdocs build` (если доступно).

## Группы markdown-файлов для перевода
### Chunk 1: markdown-группа 1 (6 файлов, ~84166 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `README.md` (77558 символов)
- `docs/providers/ollama_cloud.md` (1824 символов)
- `src/cai/prompts/micro/blueteam.md` (1547 символов)
- `examples/research_bot/README.md` (1283 символов)
- `src/cai/prompts/system_dns_smtp_agent.md` (1031 символов)
- `src/cai/prompts/micro/android.md` (923 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 2: markdown-группа 2 (10 файлов, ~84111 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `benchmarks/README.md` (64247 символов)
- `src/cai/prompts/system_triage_agent.md` (4371 символов)
- `docs/results.md` (3765 символов)
- `src/cai/prompts/system_reporting_agent.md` (3185 символов)
- `src/cai/prompts/system_ctf_agent.md` (2208 символов)
- `src/cai/prompts/core/system_codeact_template.md` (1812 символов)
- `src/cai/prompts/system_continuous_ops_agent.md` (1454 символов)
- `src/cai/prompts/micro/continuous_ops.md` (1166 символов)
- `examples/mcp/git_example/README.md` (1041 символов)
- `src/cai/prompts/system_flag_discriminator.md` (862 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 3: markdown-группа 3 (13 файлов, ~84131 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `src/cai/caibench/atkdef/README.md` (38044 символов)
- `docs/mui/mui_index.md` (8993 символов)
- `docs/benchmarking/cyber_ranges.md` (7553 символов)
- `tests/integration/README_STREAMING_TESTS.md` (6582 символов)
- `src/cai/prompts/reverse_engineering_agent.md` (5721 символов)
- `docs/cai/index.md` (4360 символов)
- `src/cai/prompts/system_reasoner_supporter.md` (3601 символов)
- `src/cai/caibench/cyber_ranges/README.md` (2904 символов)
- `src/cai/prompts/system_exploit_expert.md` (1814 символов)
- `src/cai/prompts/micro/web.md` (1472 символов)
- `src/cai/prompts/micro/sdr.md` (1136 символов)
- `src/cai/prompts/micro/memory_forensics.md` (1063 символов)
- `src/cai/prompts/micro/usecase.md` (888 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 4: markdown-группа 4 (16 файлов, ~84143 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `src/cai/prompts/system_apt_agent.md` (33829 символов)
- `docs/tui/getting_started.md` (9328 символов)
- `docs/mui/user_interface.md` (7802 символов)
- `src/cai/prompts/system_android_app_logic_mapper.md` (6697 символов)
- `src/cai/tui/README.md` (5991 символов)
- `src/cai/prompts/wifi_security_agent.md` (4523 символов)
- `examples/agent_patterns/README.md` (3816 символов)
- `src/cai/prompts/system_thought_router.md` (3251 символов)
- `docs/cai_development.md` (2228 символов)
- `docs/cai/getting-started/packet_capture_wsl.md` (1882 символов)
- `src/cai/prompts/micro/network.md` (1607 символов)
- `docs/cai/development/contributing.md` (1206 символов)
- `src/cai/prompts/micro/dfir.md` (1096 символов)
- `src/cai/prompts/micro/flag.md` (732 символов)
- `docs/ref/run.md` (111 символов)
- `docs/ref/tracing/setup.md` (44 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 5: markdown-группа 5 (14 файлов, ~84201 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `docs/cli/advanced_usage.md` (25272 символов)
- `docs/tui/commands_reference.md` (12805 символов)
- `docs/benchmarking/running_benchmarks.md` (8824 символов)
- `docs/benchmarking/knowledge_benchmarks.md` (7573 символов)
- `docs/mui/getting_started.md` (6629 символов)
- `docs/tui/teams_and_parallel_execution.md` (5799 символов)
- `src/cai/prompts/system_blue_team_agent.md` (4314 символов)
- `docs/cai/troubleshooting/operator_feedback_reproduction.md` (3652 символов)
- `src/cai/prompts/system_compliance_agent.md` (2536 символов)
- `src/cai/ctr/system_prompts/qwen.md` (1949 символов)
- `src/cai/prompts/micro/reporting.md` (1579 символов)
- `docs/providers/ollama.md` (1236 символов)
- `src/cai/prompts/micro/replay.md` (1066 символов)
- `src/cai/prompts/micro/triage.md` (967 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 6: markdown-группа 6 (16 файлов, ~84259 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `docs/cai/getting-started/commands.md` (18812 символов)
- `src/cai/caibench/cyber_ranges/easy_techcorp2/README.md` (12820 символов)
- `tests/refusals/README.md` (9346 символов)
- `docs/tui/tui_index.md` (8108 символов)
- `docs/benchmarking/attack_defense.md` (7064 символов)
- `src/cai/prompts/subghz_agent.md` (6316 символов)
- `docs/cai/getting-started/installation.md` (5276 символов)
- `src/cai/prompts/system_web_bounty_agent.md` (3855 символов)
- `docs/tui/troubleshooting.md` (3601 символов)
- `src/cai/prompts/micro/ctf.md` (2236 символов)
- `examples/financial_research_agent/README.md` (1922 символов)
- `src/cai/prompts/micro/reverse.md` (1571 символов)
- `docs/voice/tracing.md` (1443 символов)
- `examples/mcp/filesystem_example/README.md` (994 символов)
- `tests/README.md` (526 символов)
- `examples/mcp/sse_example/README.md` (369 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 7: markdown-группа 7 (16 файлов, ~84142 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `docs/tui/terminals_management.md` (16828 символов)
- `src/cai/caibench/cyber_ranges/poo-range/README.md` (13971 символов)
- `src/cai/prompts/core/system_master_template.md` (9611 символов)
- `docs/cai/getting-started/configuration.md` (8111 символов)
- `src/cai/prompts/system_android_sast.md` (7426 символов)
- `src/cai/prompts/memory_analysis_agent.md` (6409 символов)
- `docs/quickstart.md` (5366 символов)
- `src/cai/prompts/system_dfir_agent.md` (3883 символов)
- `docs/other_cli/claude_code.md` (3309 символов)
- `docs/other_cli/opencode.md` (2483 символов)
- `docs/cai/troubleshooting/platform_limitations.md` (2145 символов)
- `src/cai/prompts/micro/bugbounty.md` (1475 символов)
- `src/cai/prompts/micro/wifi.md` (1172 символов)
- `src/cai/prompts/micro/codeagent.md` (1063 символов)
- `src/cai/prompts/micro/guardrail.md` (842 символов)
- `docs/ref/run_context.md` (48 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 8: markdown-группа 8 (16 файлов, ~84209 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `docs/research.md` (16353 символов)
- `docs/tui/sidebar_features.md` (13988 символов)
- `src/cai/prompts/system_replay_attack_agent.md` (10985 символов)
- `docs/tui/keyboard_shortcuts.md` (7912 символов)
- `src/cai/prompts/system_network_analyzer.md` (7046 символов)
- `src/cai/caibench/cyber_ranges/promptfoo/README.md` (6075 символов)
- `docs/voice/quickstart.md` (5313 символов)
- `src/cai/prompts/system_selection_agent.md` (3980 символов)
- `docs/cai/case-studies/operator-artifact-evidence.md` (3296 символов)
- `src/cai/caibench/cyber_ranges/CobaltGroupRansomware/README.md` (2458 символов)
- `docs/cai/getting-started/MCP.md` (1927 символов)
- `examples/model_providers/README.md` (1800 символов)
- `src/cai/prompts/micro/apt.md` (1122 символов)
- `examples/voice/static/README.md` (1005 символов)
- `src/cai/prompts/micro/reasoner.md` (657 символов)
- `src/cai/caibench/artifacts/chals/forensics/Br3akTh3Vau1t/README.md` (292 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 9: markdown-группа 9 (15 файлов, ~84204 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `src/cai/prompts/system_orchestration_agent.md` (15283 символов)
- `docs/cai_architecture.md` (14066 символов)
- `tests/refusals/REFUSAL_ANALYSIS_REPORT.md` (10995 символов)
- `docs/benchmarking/privacy_benchmarks.md` (8232 символов)
- `src/cai/prompts/system_web_pentester.md` (7279 символов)
- `docs/tui/advanced_features.md` (6420 символов)
- `docs/mui/gestures_shortcuts.md` (5391 символов)
- `docs/voice/pipeline.md` (4211 символов)
- `src/cai/prompts/system_use_cases.md` (3274 символов)
- `docs/other_cli/codex.md` (2351 символов)
- `src/cai/prompts/micro/compliance.md` (1837 символов)
- `src/cai/prompts/micro/redteam.md` (1660 символов)
- `src/cai/prompts/micro/selection.md` (1190 символов)
- `src/cai/prompts/core/user_master_template.md` (1053 символов)
- `examples/voice/streamed/README.md` (962 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

### Chunk 10: markdown-группа 10 (15 файлов, ~84214 символов)
**Сложность:** simple (механический перевод с сохранением форматирования)
**Файлы:**
- `examples/research_bot/sample_outputs/product_recs.md` (14628 символов)
- `examples/research_bot/sample_outputs/vacation.md` (14158 символов)
- `docs/tui/user_interface.md` (12641 символов)
- `docs/benchmarking/overview.md` (7829 символов)
- `docs/mui/chat_features.md` (6852 символов)
- `docs/benchmarking/jeopardy_ctfs.md` (6391 символов)
- `docs/cai_quickstart.md` (4858 символов)
- `src/cai/prompts/system_red_team_agent.md` (4292 символов)
- `src/cai/prompts/system_bug_bounter.md` (3304 символов)
- `src/cai/caibench/cyber_ranges/poo-range/attacker/tools/attack_guide.md` (2351 символов)
- `docs/cai/api-reference/core.md` (2190 символов)
- `src/cai/prompts/micro/activedirectory.md` (1511 символов)
- `docs/cai_citation_and_acknowledgments.md` (1185 символов)
- `src/cai/prompts/micro/mail.md` (1043 символов)
- `src/cai/prompts/micro/thought_router.md` (981 символов)
**Критерии приёмки:**
- Все файлы группы содержат русский текст в прозе.
- Маркдаун-разметка, код, ссылки и пути не повреждены.
- Агент возвращает список изменённых/пропущенных файлов.

## Chunk 11: user-facing строки в Python-исходниках
**Сложность:** simple
**Файлы (основные):**
- `src/cai/cli.py`
- `src/cai/repl/commands/*.py`
- `src/cai/continuous_ops/loop_runner.py`
- `src/cai/parallel_worker.py`
- `src/cai/ctr/experiment.py`
- компоненты TUI с пользовательскими подписями/подсказками
**Критерии приёмки:**
- Все help/description для argparse/click переведены на русский.
- Имена аргументов, команды и синтаксис CLI не изменены.
- Тесты, ожидающие английские строки, обновлены.

## Chunk 12: валидация и финальная проверка
**Сложность:** simple
**Действия:**
1. Запустить `pytest -x` (или выборочные тесты, если полный набор долгий).
2. Запустить `mkdocs build` (если команда доступна).
3. Проверить отсутствие непереведённых заголовков/абзацев в переведённых файлах (выборочная проверка).
4. Обновить `TODO.md` и `md_english_files.txt`, удалив переведённые файлы из списка.
**Критерии приёмки:**
- `pytest` проходит без ошибок, связанных с переводом.
- `mkdocs build` завершается успешно.
- Список непереведённых файлов пуст (или задокументированы исключения).

