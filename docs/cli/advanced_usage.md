# Продвинутое использование

Это руководство охватывает продвинутые функции, автоматизацию, скриптинг и техники для продвинутых пользователей интерфейса командной строки CAI.

---

## Содержание

1. [Флаги запуска CLI](#флаги-запуска-cli)
2. [Параллельное выполнение](#параллельное-выполнение)
3. [Система очередей](#система-очередей)
4. [Автоматизация и скриптинг](#автоматизация-и-скриптинг)
5. [Управление памятью](#управление-памятью)
6. [Рабочее пространство и виртуализация](#рабочее-пространство-и-виртуализация)
7. [Рабочие процессы CTF](#рабочие-процессы-ctf)
8. [Управление стоимостью](#управление-стоимостью)
9. [Управление конфигурацией](#управление-конфигурацией)
10. [Паттерны интеграции](#паттерны-интеграции)
11. [Решение проблем](#решение-проблем)

---

## Флаги запуска CLI

CAI предоставляет мощные флаги командной строки для управления сессиями и автономной работы.

### Флаги возобновления сессий

Возобновление предыдущих сессий для продолжения с того места, где вы остановились:

```bash
# Возобновить последнюю сессию
cai --resume

# Возобновить с интерактивным выбором сессии
cai --resume list

# Возобновить конкретную сессию по ID
cai --resume abc12345

# Возобновить из конкретного файла журнала
cai --resume /path/to/session.jsonl

# Возобновить из пользовательского каталога журналов
cai --resume list --logpath ~/custom_logs/
```

### Флаг режима продолжения

Включение автономной работы, где агент продолжает работать без ожидания ввода от пользователя:

```bash
# Запуск в режиме продолжения
cai --continue --prompt "выполни аудит безопасности"

# Сокращенная форма
cai -c --prompt "проанализируй уязвимости"
```

### Комбинирование возобновления и продолжения

Самая мощная комбинация — возобновление сессии И автономное продолжение:

```bash
# Возобновить последнюю сессию и продолжить работу
cai --resume --continue

# Возобновить конкретную сессию и продолжить
cai --resume abc12345 --continue

# Сокращенная форма
cai --resume -c
```

Это идеально подходит для:
- Возобновления прерванных долгосрочных задач
- Продолжения аудитов безопасности после перерыва
- Продолжения пентестов с того места, где вы остановились

### Другие полезные флаги

```bash
# Запуск с начальным промптом
cai --prompt "ваша задача здесь"
cai -p "ваша задача здесь"

# Использование конкретного типа агента
cai --agent redteam_agent
cai -a bug_bounter_agent

# Использование конкретной модели
cai --model alias1
cai -m gpt-4o

# Загрузка YAML конфигурации
cai --yaml config.yaml

# Проверка версии
cai --version

# Обновление CAI
cai --update
```

Для подробной документации по возобновлению сессий смотрите [Возобновление сессий](../session_resume.md).
Для подробностей о режиме продолжения смотрите [Режим продолжения](../continue_mode.md).

---

## Параллельное выполнение

Запуск нескольких агентов одновременно для получения различных перспектив или распределения нагрузки.

### Базовая настройка параллельного выполнения

#### Способ 1: Использование команд

```bash
# Запуск CAI
cai

# Добавление агентов в параллельную конфигурацию
CAI> /parallel add redteam_agent alias1
CAI> /parallel add blueteam_agent alias1
CAI> /parallel add bug_bounter_agent gpt-4o

# Список настроенных агентов
CAI> /parallel list

# Выполнение на всех агентах
CAI> /parallel run "проанализируй безопасность target.com"

# Объединение результатов
CAI> /parallel merge
```

#### Способ 2: Использование YAML конфигурации

Создайте `agents.yaml`:

```yaml
metadata:
  description: "Многопроспектный анализ безопасности"
  auto_run: true

agents:
  - name: offensive
    agent_type: redteam_agent
    model: alias1
    
  - name: defensive
    agent_type: blueteam_agent
    model: alias1
    
  - name: bug_hunter
    agent_type: bug_bounter_agent
    model: gpt-4o
    
  - name: forensics
    agent_type: dfir_agent
    model: alias1
```

Запуск с YAML:

```bash
cai --yaml agents.yaml --prompt "выполни комплексную оценку безопасности target.com"
```

#### Способ 3: Использование переменной окружения

```bash
# Установка количества параллельных задач
export CAI_PARALLEL=3
export CAI_AGENT_TYPE=redteam_agent
export CAI_MODEL=alias1

cai --prompt "просканируй сеть 192.168.1.0/24"
```

### Продвинутые паттерны параллельного выполнения

#### Паттерн 1: Распределенная разведка

Разделение разведки между несколькими агентами:

```yaml
# recon_team.yaml
agents:
  - name: subdomain_enum
    agent_type: redteam_agent
    model: alias1
    initial_prompt: "Перечисли поддомены для диапазона A-M"
    
  - name: subdomain_enum2
    agent_type: redteam_agent
    model: alias1
    initial_prompt: "Перечисли поддомены для диапазона N-Z"
    
  - name: port_scanner
    agent_type: network_security_analyzer_agent
    model: alias1
    initial_prompt: "Просканируй все обнаруженные хосты"
    
  - name: web_analyzer
    agent_type: bug_bounter_agent
    model: alias1
    initial_prompt: "Проанализируй все найденные веб-сервисы"
```

```bash
cai --yaml recon_team.yaml
```

#### Паттерн 2: Анализ Красная vs Синяя команда

Сравнение наступательной и защитной перспектив:

```bash
# Настройка команд
CAI> /parallel add redteam_agent alias1
CAI> /parallel add blueteam_agent alias1

# Выполнение одного анализа с различных перспектив
CAI> /parallel run "проанализируй защитную позицию этого веб-приложения"

# Сравнение результатов
CAI> /parallel merge
```

#### Паттерн 3: Сравнение нескольких моделей

Тестирование различных моделей на одной задаче:

```yaml
# model_comparison.yaml
agents:
  - name: alias_test
    agent_type: bug_bounter_agent
    model: alias1
    
  - name: gpt4o_test
    agent_type: bug_bounter_agent
    model: gpt-4o
    
  - name: claude_test
    agent_type: bug_bounter_agent
    model: claude-3-5-sonnet-20241022
```

### Управление результатами параллельного выполнения

```bash
# Просмотр выводов отдельных агентов
CAI> /history 10 offensive
CAI> /history 10 defensive

# Объединение всех бесед
CAI> /parallel merge

# Сохранение объединенных результатов
CAI> /save parallel_assessment_results.json

# Очистка параллельной конфигурации
CAI> /parallel clear
```

---

## Система очередей

Пакетная обработка нескольких промптов для автоматизированных рабочих процессов.

### Создание файлов очереди

Создайте `security_checklist.txt`:

```text
# Чек-лист оценки безопасности
# Комментарии начинаются с # и игнорируются

# Этап 1: Разведка
/agent redteam_agent
Выполни пассивную разведку target.com
Перечисли поддомены и сервисы

# Этап 2: Сканирование уязвимостей
/agent bug_bounter_agent
Протестируй на уязвимости OWASP Top 10
Проверь на известные CVE в обнаруженных сервисах

# Этап 3: Анализ сети
/agent network_security_analyzer_agent
$ nmap -sV -p- target.com
Проанализируй сетевую топологию

# Этап 4: Генерация отчета
/agent reporting_agent
Сгенерируй комплексный отчет безопасности
/save security_assessment_report.md

# Этап 5: Очистка
/cost
/history 50
```

### Загрузка и выполнение очередей

#### Способ 1: Автозагрузка при запуске

```bash
# Установка переменной окружения
export CAI_QUEUE_FILE="security_checklist.txt"
cai

# Очередь выполняется автоматически
```

#### Способ 2: Очередь командной строки

```bash
# Используйте точки с запятой для цепочки команд
cai --prompt "/agent redteam_agent ; просканируй target.com ; /save results.json"
```

### Продвинутые паттерны очередей

#### Паттерн 1: Очередь задач CTF

```text
# ctf_workflow.txt
/config CTF_NAME=hackableii
/config CTF_CHALLENGE=web_app
/agent redteam_agent
Проанализируй среду задачи CTF
Найди и эксплуатируй уязвимости
Извлеки флаг
/save ctf_solution.md
```

#### Паттерн 2: Рабочий процесс Bug Bounty

```text
# bugbounty_recon.txt
/agent bug_bounter_agent
/config CAI_PRICE_LIMIT=20.0

# Разведка
Выполни перечисление поддоменов target.com
Определи веб-технологии и фреймворки
Составь карту поверхности атаки

# Тестирование
Протестируй механизмы аутентификации на обходы
Проверь на уязвимости инъекций
Проанализируй API эндпоинты на проблемы безопасности

# Отчетность
Составь находки в отчет bug bounty
/save bugbounty_findings.md
/cost
```

#### Паттерн 3: Непрерывный мониторинг безопасности

```text
# daily_security_check.txt
/agent network_security_analyzer_agent

# Ежедневные проверки
$ nmap -sV 192.168.1.0/24
Проанализируй изменения с предыдущего сканирования
Определи новые сервисы или хосты
Сообщи об аномалиях

/save daily_scan_$(date +%Y%m%d).json
```

---

## Автоматизация и скриптинг

Интеграция CAI в скрипты и конвейеры CI/CD.

### Интеграция с Bash-скриптами

#### Скрипт 1: Автоматизированное сканирование безопасности

```bash
#!/bin/bash
# security_scan.sh

TARGET="$1"
OUTPUT_DIR="./scan_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Конфигурация
export CAI_MODEL=alias1
export CAI_AGENT_TYPE=redteam_agent
export CAI_PRICE_LIMIT=10.0
export CAI_MAX_TURNS=50
export CAI_TRACING=false
export CAI_DEBUG=0

# Создание каталога вывода
mkdir -p "$OUTPUT_DIR"

# Запуск CAI с автоматизированным промптом
cai --prompt "
/agent redteam_agent
Выполни комплексное сканирование безопасности $TARGET
Протестируй на распространенные уязвимости
/save $OUTPUT_DIR/scan_${TIMESTAMP}.json
/cost
/exit
"

echo "Сканирование завершено. Результаты сохранены в $OUTPUT_DIR/scan_${TIMESTAMP}.json"
```

Использование:

```bash
chmod +x security_scan.sh
./security_scan.sh target.com
```

#### Скрипт 2: Пакетное сканирование нескольких целей

```bash
#!/bin/bash
# batch_scan.sh

TARGETS_FILE="$1"
OUTPUT_DIR="./batch_results"

mkdir -p "$OUTPUT_DIR"

while IFS= read -r target; do
    echo "Сканирование $target..."
    
    CAI_PRICE_LIMIT=5.0 cai --prompt "
    /agent bug_bounter_agent
    Просканируй $target на веб-уязвимости
    /save $OUTPUT_DIR/${target//\//_}_scan.json
    /exit
    "
    
    echo "Завершено: $target"
    sleep 2
done < "$TARGETS_FILE"

echo "Все сканирования завершены!"
```

Использование:

```bash
# targets.txt содержит по одному домену в строке
./batch_scan.sh targets.txt
```

#### Скрипт 3: Автоматизация CTF

```bash
#!/bin/bash
# ctf_solver.sh

CTF_NAME="$1"
CHALLENGE="$2"

export CTF_NAME="$CTF_NAME"
export CTF_CHALLENGE="$CHALLENGE"
export CTF_INSIDE=true
export CAI_AGENT_TYPE=redteam_agent
export CAI_MODEL=alias1
export CAI_MAX_TURNS=100

# Создание файла очереди
cat > /tmp/ctf_queue.txt << 'EOF'
Проанализируй задачу CTF
Определи уязвимости
Эксплуатируй и найди флаг
/save ctf_solution.json
/exit
EOF

# Запуск с очередью
CAI_QUEUE_FILE=/tmp/ctf_queue.txt cai

# Очистка
rm /tmp/ctf_queue.txt
```

Использование:

```bash
./ctf_solver.sh hackableii web_challenge
```

### Интеграция с CI/CD

#### Пример GitHub Actions

```yaml
# .github/workflows/security-scan.yml
name: Сканирование безопасности

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Ежедневно в 2 часа ночи

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Клонирование кода
      uses: actions/checkout@v3
      
    - name: Настройка Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Установка CAI
      run: |
        pip install cai
        
    - name: Запуск сканирования безопасности
      env:
        ALIAS_API_KEY: ${{ secrets.ALIAS_API_KEY }}
        CAI_MODEL: alias1
        CAI_PRICE_LIMIT: 10.0
        CAI_TRACING: false
      run: |
        cai --prompt "
        /agent bug_bounter_agent
        Проанализируй этот репозиторий на проблемы безопасности
        Сфокусируйся на уязвимостях OWASP Top 10
        /save security_report.json
        /exit
        "
        
    - name: Загрузка результатов
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: security_report.json
```

#### Пример GitLab CI

```yaml
# .gitlab-ci.yml
security_scan:
  stage: test
  image: python:3.11
  
  before_script:
    - pip install cai
    
  script:
    - |
      cai --prompt "
      /agent redteam_agent
      Просканируй $CI_PROJECT_URL на уязвимости
      /save scan_results.json
      /exit
      "
      
  artifacts:
    paths:
      - scan_results.json
    expire_in: 1 week
    
  only:
    - main
    - merge_requests
```

### Неинтерактивный режим

```bash
# Выполнение одной команды
cai --prompt "просканируй 192.168.1.1" > output.txt

# Подавление интерактивных элементов
CAI_DEBUG=0 CAI_BRIEF=true cai --prompt "быстрое сканирование"

# Перенаправление вывода
cai --prompt "проанализируй" | grep -i "уязвимость"

# Вывод JSON для парсинга
cai --prompt "просканируй цель ; /save results.json ; /exit"
```

---

## Управление памятью

Продвинутая постоянная память для долгосрочного контекста.

### Эпизодическая память

Хранение и вызов конкретных эпизодов или сессий.

```bash
# Включение эпизодической памяти
export CAI_MEMORY=episodic
cai

# Во время сессии
CAI> /memory save "SQLi уязвимость найдена в форме входа"
CAI> /memory save "XSS в разделе комментариев"

# Список воспоминаний
CAI> /memory list

# Применение воспоминания к новой сессии
CAI> /memory apply mem_12345
```

### Семантическая память

Хранение знаний и фактов.

```bash
# Включение семантической памяти
export CAI_MEMORY=semantic
cai

# Сохранение семантических знаний
CAI> /memory save "Цель использует Apache 2.4.41 с ModSecurity"
```

### Комбинированная память

Использование эпизодической и семантической памяти:

```bash
# Включение всех типов памяти
export CAI_MEMORY=all
export CAI_MEMORY_ONLINE=true
export CAI_MEMORY_ONLINE_INTERVAL=5

cai
```

### Режим онлайн-памяти

Автоматическое сохранение памяти через определенные интервалы:

```bash
# Настройка онлайн-памяти
export CAI_MEMORY=episodic
export CAI_MEMORY_ONLINE=true
export CAI_MEMORY_ONLINE_INTERVAL=3  # Сохранение каждые 3 хода

cai --prompt "длинная сессия разведки"
```

### Рабочие процессы с памятью

#### Рабочий процесс 1: Многодневная оценка

**День 1:**
```bash
CAI> /agent bug_bounter_agent
CAI> Выполни разведку target.com
CAI> /memory save "day1_reconnaissance"
CAI> /save day1_session.json
```

**День 2:**
```bash
CAI> /agent bug_bounter_agent
CAI> /memory apply day1_reconnaissance
CAI> Продолжи тестирование на основе вчерашних находок
CAI> /memory save "day2_exploitation"
```

#### Рабочий процесс 2: База знаний

```bash
# Построение базы знаний безопасности
CAI> /memory save "CVE-2024-1234 влияет на Apache < 2.4.59"
CAI> /memory save "Обходы SQL-инъекций для ModSecurity"
CAI> /memory save "Варианты полезных нагрузок XSS для обхода WAF"

# Позже, в новой сессии
CAI> /memory list
CAI> /memory apply mem_useful_techniques
```

### Сжатие памяти

Уменьшение размера памяти с сохранением важной информации:

```bash
# Сжатие текущей беседы
CAI> /memory compact

# Статус и статистика
CAI> /memory status
```

### Управление памятью

```bash
# Просмотр конкретного воспоминания
CAI> /memory show mem_12345

# Объединение воспоминаний
CAI> /memory merge mem_12345 mem_67890 "combined_findings"

# Удаление воспоминания
CAI> /memory delete mem_12345
```

---

## Рабочее пространство и виртуализация

Управление средами выполнения и Docker контейнерами.

### Управление рабочим пространством

```bash
# Показать текущее рабочее пространство
CAI> /workspace show

# Изменить рабочее пространство
CAI> /workspace set /home/user/pentests/target_corp

# Список содержимого рабочего пространства
CAI> /workspace list

# Выполнение команд в рабочем пространстве
CAI> $ ls -la
CAI> $ cat target_info.txt
```

### Выполнение в Docker контейнерах

#### Автоматическая настройка контейнера (CTF)

```bash
# CTF автоматически настраивает контейнер
export CTF_NAME=hackableii
export CTF_INSIDE=true
cai

# Команды автоматически выполняются внутри контейнера
CAI> $ whoami
CAI> $ ip addr
```

#### Ручное управление контейнерами

```bash
# Список доступных контейнеров
CAI> /virtualization list

# Установка активного контейнера
CAI> /virtualization set ubuntu_pentest

# Все команды теперь выполняются в контейнере
CAI> $ nmap -sV localhost

# Возврат к хосту
CAI> /virtualization clear
```

### Переменные окружения для виртуализации

```bash
# Конфигурация CTF
export CTF_NAME=hackableii
export CTF_CHALLENGE=web_app
export CTF_SUBNET=192.168.3.0/24
export CTF_IP=192.168.3.100
export CTF_INSIDE=true  # Выполнение внутри контейнера

# Активный контейнер
export CAI_ACTIVE_CONTAINER=abc123def456

cai
```

### Продвинутые паттерны виртуализации

#### Паттерн 1: Изолированное тестирование

```bash
#!/bin/bash
# isolated_test.sh

# Создание изолированного контейнера
CONTAINER_ID=$(docker run -d ubuntu:latest sleep infinity)

# Установка контейнера для CAI
export CAI_ACTIVE_CONTAINER=$CONTAINER_ID

# Запуск тестов
cai --prompt "
/virtualization set $CONTAINER_ID
Установи и протестируй образец вредоносного ПО
Проанализируй поведение
/save malware_analysis.json
/exit
"

# Очистка
docker stop $CONTAINER_ID
docker rm $CONTAINER_ID
```

#### Паттерн 2: Тестирование с несколькими контейнерами

```bash
# Тестирование на нескольких контейнерах
CAI> /virtualization set web_server_container
CAI> $ curl http://localhost

CAI> /virtualization set db_container
CAI> $ psql -l

CAI> /virtualization set app_container
CAI> $ python test_exploit.py
```

---

## Рабочие процессы CTF

Специализированные рабочие процессы для задач Capture The Flag.

### Базовая настройка CTF

```bash
# Настройка среды CTF
export CTF_NAME=hackableii
export CTF_CHALLENGE=binary_exploit
export CAI_AGENT_TYPE=redteam_agent
export CAI_MODEL=alias1
export CAI_MAX_TURNS=inf

cai
```

### Типы задач CTF

#### Тип 1: Веб-задачи

```bash
export CTF_NAME=webchallenge
export CTF_INSIDE=true

cai --prompt "
/agent bug_bounter_agent
Проанализируй это веб-приложение
Найди и эксплуатируй уязвимости
Извлеки флаг
/save web_ctf_solution.md
"
```

#### Тип 2: Эксплуатация бинарных файлов

```bash
export CTF_NAME=pwn_challenge

cai --prompt "
/agent reverse_engineering_agent
Проанализируй бинарный файл
Найди уязвимость переполнения буфера
Разработай эксплойт
/save exploit.py
"
```

#### Тип 3: Криминалистика

```bash
export CTF_NAME=forensics_challenge

cai --prompt "
/agent dfir_agent
Проанализируй дамп памяти
Извлеки скрытые данные
Найди флаг
/save forensics_analysis.md
"
```

### Автоматический решатель CTF

```bash
#!/bin/bash
# auto_ctf.sh

CHALLENGES=(
    "web_app:bug_bounter_agent"
    "binary_exploit:reverse_engineering_agent"
    "network_forensics:dfir_agent"
    "crypto:redteam_agent"
)

for challenge in "${CHALLENGES[@]}"; do
    IFS=':' read -r name agent <<< "$challenge"
    
    echo "Решение $name..."
    
    CTF_NAME="ctf_event" \
    CTF_CHALLENGE="$name" \
    CAI_AGENT_TYPE="$agent" \
    cai --prompt "
    Проанализируй и реши задачу
    Найди флаг
    /save ${name}_solution.json
    /exit
    "
done
```

### CTF с временными ограничениями

```bash
# Установка строгих ограничений для CTF
export CAI_MAX_TURNS=50
export CAI_MAX_INTERACTIONS=200
export CAI_PRICE_LIMIT=5.0

# Принудительный выход, если флаг не найден
# (требуется режим force_until_flag)
cai --prompt "реши задачу CTF"
```

---

## Управление стоимостью

Контроль и оптимизация затрат на использование API.

### Установка лимитов стоимости

```bash
# Установка лимита стоимости
export CAI_PRICE_LIMIT=10.0

# Установка лимита взаимодействий
export CAI_MAX_INTERACTIONS=100

# Установка лимита ходов
export CAI_MAX_TURNS=50

cai
```

### Настройка стоимости во время выполнения

```bash
# Проверка текущих затрат
CAI> /cost

# Увеличение лимита при необходимости
CAI> /config CAI_PRICE_LIMIT=20.0

# Проверка обновленного лимита
CAI> /config | grep PRICE_LIMIT
```

### Стратегии оптимизации затрат

#### Стратегия 1: Выбор модели

```bash
# Использование более дешевых моделей для разведки
CAI> /agent redteam_agent
CAI> /model alias1  # Сбалансированная стоимость/производительность

# Использование мощных моделей для сложного анализа
CAI> /model gpt-4o
CAI> Проанализируй сложную цепочку уязвимостей
```

#### Стратегия 2: Сжатие беседы

```bash
# При приближении к лимитам токенов
CAI> /compact

# Или настройка автоматического сжатия
export CAI_AUTO_COMPACT=true
```

#### Стратегия 3: Целенаправленные промпты

```bash
# Будьте конкретны для снижения переключений
CAI> Просканируй 192.168.1.1 порты 80,443,8080 с помощью nmap -sV

# Вместо:
CAI> Просканируй 192.168.1.1
# (агент спрашивает какие порты)
# (несколько ходов = более высокая стоимость)
```

### Мониторинг затрат

```bash
# Просмотр подробной разбивки затрат
CAI> /cost

# Стоимость по агентам
CAI> /cost redteam_agent
CAI> /cost bug_bounter_agent

# Статистика сессии
CAI> /history
CAI> /cost all
```

### Рабочие процессы с ограниченным бюджетом

```bash
#!/bin/bash
# budget_scan.sh

# Установка строгого бюджета
export CAI_PRICE_LIMIT=2.0
export CAI_MODEL=alias1  # Экономичная модель

cai --prompt "
/agent redteam_agent
Быстрое сканирование уязвимостей $TARGET
Сфокусируйся только на критических проблемах
/cost
/save budget_scan.json
/exit
"

# Проверка, не достигнут ли лимит
if grep -q "price limit" budget_scan.json; then
    echo "Внимание: Достигнут лимит стоимости"
fi
```

---

## Управление конфигурацией

Продвинутые паттерны конфигурации.

### Профили конфигурации

#### Профиль 1: Разработка

```bash
# dev_profile.env
export CAI_MODEL=alias1
export CAI_DEBUG=2
export CAI_PRICE_LIMIT=5.0
export CAI_TRACING=true
export CAI_MAX_TURNS=20
```

Использование:
```bash
source dev_profile.env
cai
```

#### Профиль 2: Продакшен

```bash
# prod_profile.env
export CAI_MODEL=alias1
export CAI_DEBUG=0
export CAI_BRIEF=true
export CAI_PRICE_LIMIT=50.0
export CAI_TRACING=false
export CAI_GUARDRAILS=true
```

#### Профиль 3: CTF

```bash
# ctf_profile.env
export CAI_MODEL=alias1
export CAI_AGENT_TYPE=redteam_agent
export CAI_MAX_TURNS=inf
export CAI_PRICE_LIMIT=20.0
export CAI_DEBUG=1
```

### Переопределение моделей для агентов

```bash
# Установка различных моделей для различных агентов
export CAI_REDTEAM_AGENT_MODEL=gpt-4o
export CAI_BUG_BOUNTER_AGENT_MODEL=alias1
export CAI_DFIR_AGENT_MODEL=claude-3-5-sonnet-20241022

# Модель по умолчанию для других
export CAI_MODEL=alias1

cai
```

### Динамическая конфигурация

```bash
# Запуск с базовой конфигурацией
CAI> /config

# Настройка во время сессии
CAI> /config CAI_DEBUG=2
CAI> /config CAI_PRICE_LIMIT=15.0

# Проверка изменений
CAI> /env | grep CAI
```

---

## Паттерны интеграции

Интеграция CAI с другими инструментами и сервисами.

### Интеграция с MCP

#### Паттерн 1: Интеграция с Burp Suite

```bash
# Запуск MCP сервера Burp Suite
# (в отдельном терминале)
burp-mcp-server --port 9876

# В CAI
CAI> /mcp load http://localhost:9876/sse burp
CAI> /mcp tools burp
CAI> /mcp add redteam_agent burp

# Использование инструментов Burp
CAI> Используй Burp для сканирования https://target.com
```

#### Паттерн 2: Интеграция пользовательских инструментов

```bash
# Загрузка пользовательского MCP сервера
CAI> /mcp load stdio "python my_custom_tools.py" custom

# Добавление к агенту
CAI> /mcp add bug_bounter_agent custom

# Использование пользовательских инструментов
CAI> Используй пользовательский сканер на цели
```

### Интеграция с API

```bash
#!/bin/bash
# api_integration.sh

# Получение результатов CAI
RESULT=$(cai --prompt "просканируй $TARGET ; /save -" 2>/dev/null)

# Отправка во внешний API
curl -X POST https://api.security-platform.com/scans \
  -H "Content-Type: application/json" \
  -d "$RESULT"
```

### Интеграция с вебхуками

```bash
#!/bin/bash
# webhook_notify.sh

# Запуск сканирования
cai --prompt "сканирование безопасности $TARGET ; /save results.json"

# Отправка уведомления через вебхук
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "target": "'$TARGET'",
    "status": "complete",
    "results": "'$(cat results.json)'"
  }'
```

---

## Решение проблем

Типичные проблемы и решения.

### Проблема: Достигнут лимит стоимости

```bash
# Проверка текущей стоимости
CAI> /cost

# Увеличение лимита
CAI> /config CAI_PRICE_LIMIT=20.0

# Или перезапуск с более высоким лимитом
exit
CAI_PRICE_LIMIT=20.0 cai
```

### Проблема: Превышен максимальный лимит взаимодействий

```bash
# Проверка текущего количества
CAI> /env | grep MAX_INTERACTIONS

# Увеличение лимита
CAI> /config CAI_MAX_INTERACTIONS=500

# Или используйте /flush для начала заново
CAI> /flush
```

### Проблема: Агент не отвечает

```bash
# Прерывание текущей операции
Ctrl+C

# Проверка статуса агента
CAI> /agent

# Переключение на другого агента
CAI> /agent redteam_agent

# Проверка конфигурации
CAI> /config
```

### Проблема: Окно контекста заполнено

```bash
# Проверка использования контекста (CAI PRO)
CAI> /context

# Сжатие беседы
CAI> /compact

# Или очистка и начало заново
CAI> /flush
```

### Проблема: Проблемы с выполнением контейнера

```bash
# Проверка статуса виртуализации
CAI> /virtualization info

# Список контейнеров
CAI> /virtualization list

# Очистка настройки контейнера
CAI> /virtualization clear

# Проверка рабочего пространства
CAI> /workspace show
```

### Проблема: Ошибка загрузки памяти

```bash
# Проверка статуса памяти
CAI> /memory status

# Список доступных воспоминаний
CAI> /memory list

# Удаление поврежденной памяти
CAI> /memory delete mem_problematic

# Проверка каталога хранения
$ ls -la ~/.cai/memory/
```

### Режим отладки

```bash
# Включение максимальной отладки
export CAI_DEBUG=2
cai

# Или включение во время сессии
CAI> /config CAI_DEBUG=2
```

---

## Лучшие практики

### 1. Управление сессиями

```bash
# Всегда сохраняйте важные сессии
CAI> /save project_name_$(date +%Y%m%d).json

# Используйте описательные имена файлов
CAI> /save pentest_target_corp_phase1.json
```

### 2. Контроль стоимости

```bash
# Установите разумные лимиты
export CAI_PRICE_LIMIT=10.0
export CAI_MAX_TURNS=50

# Регулярно монорьте
CAI> /cost
```

### 3. Выбор агентов

```bash
# Используйте специализированных агентов
# ✅ Хорошо: /agent bug_bounter_agent для веб-приложений
# ❌ Плохо: /agent one_tool_agent для сложных задач

# Пусть selection_agent поможет
CAI> /agent selection_agent
CAI> Мне нужно протестировать мобильное приложение
```

### 4. Параллельное выполнение

```bash
# Используйте YAML для сложных настроек
# ✅ Хорошо: cai --yaml team_config.yaml
# ❌ Плохо: Ручное /parallel add для многих агентов
```

### 5. Использование памяти

```bash
# Сохраняйте важные находки
CAI> /memory save "критическая уязвимость в системе аутентификации"

# Используйте описательные имена
# ✅ Хорошо: "SQLi в админке - обходы WAF"
# ❌ Плохо: "bug1"
```

---

## Краткий справочник

### Переменные окружения

| Переменная | Назначение | Пример |
|----------|---------|---------|
| `CAI_MODEL` | Модель по умолчанию | `alias1` |
| `CAI_AGENT_TYPE` | Агент по умолчанию | `redteam_agent` |
| `CAI_PARALLEL` | Количество параллельных задач | `3` |
| `CAI_QUEUE_FILE` | Автозагрузка очереди | `prompts.txt` |
| `CAI_MEMORY` | Режим памяти | `episodic` |
| `CAI_MEMORY_ONLINE` | Автосохранение памяти | `true` |
| `CAI_PRICE_LIMIT` | Лимит стоимости | `10.0` |
| `CAI_MAX_TURNS` | Лимит ходов | `50` |
| `CAI_ACTIVE_CONTAINER` | Docker контейнер | `abc123` |

### Паттерны команд

```bash
# Автоматизация
cai --prompt "команда ; команда ; команда"
CAI_QUEUE_FILE=file.txt cai

# Параллельное выполнение
cai --yaml agents.yaml --prompt "задача"
CAI_PARALLEL=3 cai

# CTF
CTF_NAME=challenge cai
```

---

## Следующие шаги

- 📖 [Начало работы](getting_started.md) - Базовое использование
- 📚 [Справочник команд](commands_reference.md) - Все команды
- 🏠 [Обзор CLI](cli_index.md) - Основная документация

---

*Последнее обновление: Ноябрь 2025 | CAI CLI v0.6+*
