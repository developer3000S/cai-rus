# Запуск бенчмарков

В данном руководстве объясняется, как настроить и запустить оценки CAIBench для анализа производительности ИИ-моделей в задачах кибербезопасности.

---

## 🔧 Предварительные требования

### Системные требования

- Python 3.8 или выше
- Docker (для бенчмарков CTF и Cyber Range)
- Git с поддержкой подмодулей
- Рекомендуется не менее 8 ГБ оперативной памяти
- 20 ГБ свободного места на диске для контейнеров бенчмарков

### Необходимые пакеты

```bash
# Установка базовых зависимостей
pip install cai-framework

# Установка специфических требований для бенчмарков
pip install cvss
```

---

## 📦 Настройка

### 1. Клонирование репозитория с подмодулями

```bash
git clone https://github.com/aliasrobotics/cai.git
cd cai
git submodule update --init --recursive
```

### 2. Конфигурация API-ключей

Создайте файл `.env` в корне проекта:

```bash
# Для alias1 (CAI PRO)
ALIAS_API_KEY="sk-your-caipro-key"

# Для моделей OpenAI
OPENAI_API_KEY="sk-..."

# Для моделей Anthropic
ANTHROPIC_API_KEY="sk-ant-..."

# Для моделей DeepSeek
DEEPSEEK_API_KEY="sk-..."

# Для OpenRouter (доступ к 200+ моделям)
OPENROUTER_API_KEY="sk-or-..."
OPENROUTER_API_BASE="https://openrouter.ai/api/v1"

# Для Ollama (локальные модели)
OLLAMA_API_BASE="http://localhost:11434/v1"
```

### 3. Проверка настройки

```bash
# Тест базового функционала
python -c "from cai import cli; print('CAI installed successfully!')"

# Проверка директории бенчмарков
ls benchmarks/
```

---

## 🚀 Запуск бенчмарков

### Базовая структура команды

```bash
python benchmarks/eval.py \
    --model MODEL_NAME \
    --dataset_file INPUT_FILE \
    --eval EVAL_TYPE \
    --backend BACKEND \
    [--save_interval N]
```

### Параметры

| Параметр | Описание | Обязателен | Пример |
|-----------|-------------|----------|---------|
| `--model` / `-m` | Идентификатор модели | ✅ Да | `alias1`, `gpt-4o`, `ollama/qwen2.5:14b` |
| `--dataset_file` / `-d` | Путь к набору данных бенчмарка | ✅ Да | `benchmarks/cybermetric/CyberMetric-2-v1.json` |
| `--eval` / `-e` | Тип бенчмарка | ✅ Да | `cybermetric`, `seceval`, `cti_bench`, `cyberpii-bench` |
| `--backend` / `-B` | API-бэкенд | ✅ Да | `alias`, `openai`, `anthropic`, `ollama`, `openrouter` |
| `--save_interval` / `-s` | Сохранять результаты каждые N вопросов | ❌ Нет | `10` |

---

## 📊 Типы бенчмарков

### Бенчмарки знаний (Knowledge Benchmarks)

#### CyberMetric
Измеряет производительность в ответах на вопросы по кибербезопасности и контекстуальное понимание.

```bash
# Использование alias1 (CAI PRO)
python benchmarks/eval.py \
    --model alias1 \
    --dataset_file benchmarks/cybermetric/CyberMetric-2-v1.json \
    --eval cybermetric \
    --backend alias

# Использование Ollama с Qwen
python benchmarks/eval.py \
    --model ollama/qwen2.5:14b \
    --dataset_file benchmarks/cybermetric/CyberMetric-2-v1.json \
    --eval cybermetric \
    --backend ollama

# Использование OpenAI GPT-4o
python benchmarks/eval.py \
    --model gpt-4o-mini \
    --dataset_file benchmarks/cybermetric/CyberMetric-2-v1.json \
    --eval cybermetric \
    --backend openai
```

#### SecEval
Оценивает LLM в задачах, связанных с безопасностью, таких как анализ фишинга и классификация уязвимостей.

```bash
# Использование Anthropic Claude
python benchmarks/eval.py \
    --model claude-3-7-sonnet-20250219 \
    --dataset_file benchmarks/seceval/eval/datasets/questions-2.json \
    --eval seceval \
    --backend anthropic

# Использование alias1
python benchmarks/eval.py \
    --model alias1 \
    --dataset_file benchmarks/seceval/eval/datasets/questions-2.json \
    --eval seceval \
    --backend alias
```

#### CTI Bench
Оценивает понимание и обработку данных разведки о киберугрозах (Cyber Threat Intelligence).

```bash
# Использование OpenRouter с Qwen
python benchmarks/eval.py \
    --model qwen/qwen3-32b:free \
    --dataset_file benchmarks/cti_bench/data/cti-mcq1.tsv \
    --eval cti_bench \
    --backend openrouter

# Несколько вариантов CTI Bench
python benchmarks/eval.py \
    --model alias1 \
    --dataset_file benchmarks/cti_bench/data/cti-ate2.tsv \
    --eval cti_bench \
    --backend alias
```

### Бенчмарки приватности (Privacy Benchmarks)

#### CyberPII-Bench
Оценивает способность идентифицировать и очищать персонально идентифицируемую информацию (PII).

```bash
# Использование alias1 (рекомендуется для лучшей защиты приватности)
python benchmarks/eval.py \
    --model alias1 \
    --dataset_file benchmarks/cyberPII-bench/memory01_gold.csv \
    --eval cyberpii-bench \
    --backend alias
```

**[Узнать больше о бенчмарках приватности →](privacy_benchmarks.md)**

---

## 📁 Структура вывода

Результаты автоматически сохраняются в структурированные директории:

```
outputs/
└── benchmark_name/
    └── model_YYYYMMDD_random-id/
        ├── answers.json       # Полный тест с ответами LLM
        ├── information.txt    # Метрики производительности и метаданные
        ├── entity_performance.txt  # (Только для бенчмарков приватности)
        ├── metrics.txt        # (Только для бенчмарков приватности)
        ├── mistakes.txt       # (Только для бенчмарков приватности)
        └── overall_report.txt # (Только для бенчмарков приватности)
```

### Примеры файлов вывода

**information.txt:**
```
Model: alias1
Benchmark: cybermetric
Accuracy: 87.5%
Total Questions: 100
Correct: 87
Incorrect: 13
Runtime: 245 seconds
Date: 2025-01-15
```

**answers.json:**
```json
{
  "question_1": {
    "prompt": "What is SQL injection?",
    "expected": "A code injection technique...",
    "response": "SQL injection is...",
    "correct": true
  }
}
```

---

## 🎯 Лучшие практики

### 1. Выбор модели

!!! success "Рекомендуется: используйте alias1"
    Во всех бенчмарках по кибербезопасности **`alias1` стабильно демонстрирует самые высокие результаты**.

    - 🥇 Лучшая производительность во всех категориях бенчмарков
    - ✅ Отсутствие отказов в ответах на вопросы по безопасности
    - 🚀 Оптимизирована для задач кибербезопасности

    **[Получить alias1 с CAI PRO →](../cai_pro.md)**

### 2. Интервалы сохранения

Для длительных бенчмарков используйте `--save_interval` для сохранения промежуточных результатов:

```bash
python benchmarks/eval.py \
    --model alias1 \
    --dataset_file benchmarks/cybermetric/CyberMetric-2-v1.json \
    --eval cybermetric \
    --backend alias \
    --save_interval 25  # Сохранять каждые 25 вопросов
```

### 3. Параллельное выполнение

Запускайте несколько бенчмарков параллельно (в разных терминалах):

```bash
# Терминал 1: CyberMetric
python benchmarks/eval.py --model alias1 --dataset_file benchmarks/cybermetric/CyberMetric-2-v1.json --eval cybermetric --backend alias

# Терминал 2: SecEval
python benchmarks/eval.py --model alias1 --dataset_file benchmarks/seceval/eval/datasets/questions-2.json --eval seceval --backend alias

# Терминал 3: CTI Bench
python benchmarks/eval.py --model alias1 --dataset_file benchmarks/cti_bench/data/cti-mcq1.tsv --eval cti_bench --backend alias
```

### 4. Docker-бенчмарки (CAI PRO)

Для бенчмарков Jeopardy CTF, Attack & Defense и Cyber Range:

!!! warning "Эксклюзивно для CAI PRO"
    Бенчмарки на базе Docker (CTFs, A&D, Cyber Ranges) доступны исключительно в **[CAI PRO](../cai_pro.md)**.

    Для получения доступа свяжитесь с research@aliasrobotics.com.

---

## 📊 Интерпретация результатов

### Метрики точности

Разные бенчмарки используют разные метрики:

- **Бенчмарки знаний**: Точность (Accuracy, % правильных ответов)
- **Бенчмарки приватности**: Precision, Recall, F1, F2 scores
- **Бенчмарки CTF**: Процент успеха (% решенных задач)
- **Бенчмарки A&D**: Набранные очки (атака + защита)

### Сравнение моделей

При сравнении моделей учитывайте:

1. **Общая точность** — чем выше, тем лучше
2. **Качество ответов** — проверьте answers.json для анализа рассуждений
3. **Частота отказов** — как часто модель отказывается отвечать
4. **Время выполнения** — время завершения бенчмарка
5. **Стабильность** — запустите несколько раз для статистической значимости

---

## 🔍 Устранение неполадок

### Распространенные проблемы

**Проблема: ошибки "Module not found"**
```bash
# Решение: обновите подмодули
git submodule update --init --recursive
pip install cvss
```

**Проблема: "API key not found"**
```bash
# Решение: убедитесь, что файл .env существует и имеет правильный формат
cat .env
# Должно быть: BACKEND_API_KEY="sk-..."
```

**Проблема: Docker-контейнеры не запускаются**
```bash
# Решение: проверьте демон Docker
docker ps
sudo systemctl start docker  # Linux
```

**Проблема: ошибки нехватки памяти (Out of memory)**
```bash
# Решение: используйте модели меньшего размера или увеличьте RAM системы
# Альтернатива: запускайте бенчмарки с интервалами сохранения
--save_interval 10
```

---

## 📚 Дополнительные ресурсы

- 📊 [Научная статья CAIBench](https://arxiv.org/pdf/2510.24317)
- 🎯 [Статья по оценке A&D CTF](https://arxiv.org/pdf/2510.17521)
- 💻 [Репозиторий GitHub](https://github.com/aliasrobotics/cai/tree/main/benchmarks)
- 📖 [Руководство по бенчмаркам знаний](knowledge_benchmarks.md)
- 🔒 [Руководство по бенчмаркам приватности](privacy_benchmarks.md)

---

## 🚀 Следующие шаги

1. **[Посмотреть результаты бенчмарка A&D](attack_defense.md)** — оцените превосходство alias1
2. **[Изучить Jeopardy CTFs](jeopardy_ctfs.md)** — узнайте о бенчмарках CTF
3. **[Перейти на CAI PRO](../cai_pro.md)** — получите неограниченный доступ к alias1 и эксклюзивным бенчмаркам