#!/usr/bin/env python3
"""
Скрипт для насыщения лимита токенов в минуту (TPM) конечной точки LLM.
Цель: 490,000 TPM (чуть ниже лимита 500,000 TPM)
"""

# Подавление предупреждений перед любыми импортами
import warnings
warnings.filterwarnings("ignore", message=".*UnsupportedFieldAttributeWarning.*")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

import asyncio
import os
import time
from typing import List, Dict, Any
import litellm
import logging
from datetime import datetime
import tiktoken
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.live import Live
from rich import print as rprint

# Загрузка переменных окружения из файла .env
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path=dotenv_path, verbose=False)

# Настройка логирования - установка WARNING для уменьшения шума
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Подавление логов HTTP запросов от httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Rich консоль
console = Console()

# Подавление отладочной информации от litellm
litellm.suppress_debug_info = True
litellm.set_verbose = False

# Отключение логирования litellm
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("litellm").setLevel(logging.WARNING)

# Конфигурация
TARGET_TPM = 490000  # Целевые токены в минуту
TARGET_TOKENS_PER_REQUEST = 8000  # Большой запрос для максимизации использования токенов
REQUESTS_PER_MINUTE = TARGET_TPM // TARGET_TOKENS_PER_REQUEST  # Около 61 запроса
REQUEST_INTERVAL = 60.0 / REQUESTS_PER_MINUTE if REQUESTS_PER_MINUTE > 0 else 1.0

# Конфигурация API
API_BASE = "https://api.aliasrobotics.com:666/"
API_KEY = os.getenv("ALIAS_API_KEY", "").strip()

if not API_KEY:
    raise ValueError("Необходимо установить переменную окружения ALIAS_API_KEY")

# Конфигурация модели - используйте CAI_MODEL, если установлена, иначе по умолчанию alias1
# поскольку она оптимизирована и может обрабатывать большие контексты
MODEL = os.getenv("CAI_MODEL", "alias1")

# Конфигурация температуры
TEMPERATURE = float(os.getenv("CAI_TEMPERATURE", "0.7"))

def count_tokens(text: str) -> int:
    """Подсчет токенов в тексте с помощью tiktoken."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except:
        encoding = tiktoken.get_encoding("gpt2")
    return len(encoding.encode(text))

def generate_large_prompt(target_tokens: int) -> str:
    """Генерация промпта с приблизительно целевым количеством токенов."""
    # Базовый контекст о сложной технической системе
    base_prompt = """Вы анализируете сложную распределенную систему со следующими характеристиками:

Система состоит из нескольких микросервисов, развернутых в различных регионах:
- Сервис фронтенда: обрабатывает запросы пользователей и рендеринг UI
- API Gateway: маршрутизирует запросы к соответствующим бэкенд-сервисам
- Сервис аутентификации: управляет аутентификацией и авторизацией пользователей
- Кластер базы данных: распределенный PostgreSQL с репликами для чтения
- Уровень кэширования: кластер Redis для управления сессиями и кэширования
- Очередь сообщений: RabbitMQ для асинхронной обработки
- Движок аналитики: обработка данных в реальном времени с Apache Spark
- Стек мониторинга: Prometheus, Grafana и пользовательские оповещения

Каждый сервис имеет конкретные требования к производительности и SLA:
1. Фронтенд должен отвечать в течение 200мс для 95% запросов
2. API Gateway должен обрабатывать 10,000 запросов в секунду
3. Запросы к базе данных должны завершаться в течение 100мс
4. Соотношение попаданий в кэш должно быть выше 85%
5. Задержка обработки очереди сообщений должна быть менее 500мс

Система испытывает следующие паттерны нагрузки:
- Пиковые часы: 8:00-10:00 и 18:00-21:00 местного времени
- Трафик в выходные составляет 60% от трафика в будние дни
- Месячные всплески 1-го и 15-го числа (обработка заработной платы)
- Сезонные колебания во время праздников и распродаж

Последние инциденты и их корневые причины:
"""
    
    # Добавляем подробные описания инцидентов для достижения целевого количества токенов
    incident_template = """
Инцидент #{num}: Исчерпание пула подключений к базе данных
Дата: 2024-{month:02d}-{day:02d}
Длительность: {duration} минут
Влияние: Затронуто {impact}% пользователей
Корневая причина: Деплой ввел утечку подключений к базе данных в платежном сервисе. Каждый запрос создавал новое подключение без его корректного закрытия. Лимит пула подключений в 100 был достигнут в течение 45 минут после деплоя.
Решение: Откат деплоя и внедрение корректного управления подключениями с использованием блоков try-with-resources. Добавление мониторинга метрик пула подключений.
Извлеченные уроки: Необходимо лучше тестировать управление ресурсами в staging окружении. Внедрение автоматических предохранителей для подключений к базе данных.

"""
    
    current_tokens = count_tokens(base_prompt)
    incidents = []
    incident_num = 1
    
    # Генерируем инциденты до тех пор, пока не достигнем приблизительно целевого количества токенов
    while current_tokens < target_tokens - 500:  # Оставляем некоторый запас
        incident = incident_template.format(
            num=incident_num,
            month=(incident_num % 12) + 1,
            day=(incident_num % 28) + 1,
            duration=30 + (incident_num % 90),
            impact=5 + (incident_num % 40)
        )
        incidents.append(incident)
        current_tokens = count_tokens(base_prompt + "".join(incidents))
        incident_num += 1
    
    full_prompt = base_prompt + "".join(incidents)
    full_prompt += "\n\nНа основе этих инцидентов и характеристик системы предоставьте краткую сводку о наиболее критической проблеме."
    
    return full_prompt

async def make_large_token_request(request_id: int, prompt: str) -> Dict[str, Any]:
    """Выполнение одного API запроса с большим количеством токенов."""
    start_time = time.time()
    prompt_tokens = count_tokens(prompt)
    
    try:
        response = await litellm.acompletion(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_base=API_BASE,
            api_key=API_KEY,
            custom_llm_provider="openai",
            max_tokens=1000,  # Разумный ответ
            temperature=TEMPERATURE,
            timeout=120.0  # Увеличенный тайм-аут для больших запросов
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Извлечение использования токенов
        usage = response.usage if hasattr(response, 'usage') else {}
        actual_prompt_tokens = getattr(usage, 'prompt_tokens', prompt_tokens)
        output_tokens = getattr(usage, 'completion_tokens', 0)
        total_tokens = getattr(usage, 'total_tokens', actual_prompt_tokens + output_tokens)
        
        return {
            "request_id": request_id,
            "status": "success",
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "prompt_tokens_estimated": prompt_tokens,
            "input_tokens": actual_prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }
        
    except litellm.exceptions.Timeout as e:
        console.print(f"[bold red]⏱️  ОБНАРУЖЕН ТАЙМАУТ![/bold red] Запрос {request_id} превысил лимит времени после {duration:.2f}s")
        console.print(f"[red]Ошибка: {str(e)}[/red]")
        return {
            "request_id": request_id,
            "status": "timeout",
            "duration": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "prompt_tokens_estimated": prompt_tokens,
            "error": str(e)
        }
    except Exception as e:
        if "rate limit" in str(e).lower():
            console.print(f"[bold yellow]⚠️  ДОСТИГНУТ ЛИМИТ СКОРОСТИ![/bold yellow] Запрос {request_id}")
            console.print(f"[yellow]Ошибка: {str(e)}[/yellow]")
        else:
            console.print(f"[red]❌ Запрос {request_id} не удался: {str(e)[:100]}...[/red]", highlight=False)
        return {
            "request_id": request_id,
            "status": "error",
            "duration": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "prompt_tokens_estimated": prompt_tokens,
            "error": str(e)
        }

async def token_saturation_test(num_minutes: float = 2):
    """Выполнение теста насыщения токенов на указанное количество минут."""
    # Отображение конфигурации теста
    config_table = Table(title="Конфигурация теста насыщения TPM", show_header=True, header_style="bold magenta")
    config_table.add_column("Параметр", style="cyan")
    config_table.add_column("Значение", style="green")
    config_table.add_row("Целевой TPM", f"{TARGET_TPM:,}")
    config_table.add_row("Целевые токены/Запрос", f"{TARGET_TOKENS_PER_REQUEST:,}")
    config_table.add_row("Запросов в минуту", str(REQUESTS_PER_MINUTE))
    config_table.add_row("Длительность", f"{num_minutes} минут")
    config_table.add_row("Модель", MODEL)
    
    console.print(config_table)
    
    # Генерируем большой промпт один раз
    console.print("\n[yellow]Генерация большого промпта...[/yellow]")
    large_prompt = generate_large_prompt(TARGET_TOKENS_PER_REQUEST)
    actual_prompt_tokens = count_tokens(large_prompt)
    console.print(f"[green]✓ Сгенерирован промпт с {actual_prompt_tokens:,} токенами[/green]")
    
    results = []
    start_time = time.time()
    
    # Отслеживание окна токенов в минуту
    minute_windows = {}
    
    # Подсчет общего количества необходимых запросов
    total_requests = int(REQUESTS_PER_MINUTE * num_minutes)
    
    # Переменная для отслеживания необходимости остановки из-за тайм-аута
    should_stop = False
    
    # Создание задач для параллельного выполнения (пакетами по минутам)
    for minute in range(int(num_minutes)):
        if should_stop:
            break
            
        minute_start = time.time()
        minute_tasks = []
        
        # Ограничение параллельных запросов для перегрузки API
        requests_this_minute = min(50, REQUESTS_PER_MINUTE, total_requests - (minute * REQUESTS_PER_MINUTE))
        
        for i in range(requests_this_minute):
            request_id = minute * REQUESTS_PER_MINUTE + i + 1
            task = make_large_token_request(request_id, large_prompt)
            minute_tasks.append(task)
        
        # Выполнение запросов пакетами
        console.print(f"\n[cyan]Минута {minute + 1}: Отправка {len(minute_tasks)} запросов...[/cyan]")
        batch_size = 10
        minute_results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            task_id = progress.add_task("[green]Обработка запросов...", total=len(minute_tasks))
            
            for batch_start in range(0, len(minute_tasks), batch_size):
                batch_end = min(batch_start + batch_size, len(minute_tasks))
                batch = minute_tasks[batch_start:batch_end]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                minute_results.extend(batch_results)
                
                progress.update(task_id, advance=len(batch))
                
                # Проверка тайм-аутов
                for result in batch_results:
                    if isinstance(result, dict) and result.get("status") == "timeout":
                        should_stop = True
                        console.print("\n[bold red]🛑 Обнаружен тайм-аут! Остановка теста...[/bold red]")
                        break
                
                if should_stop:
                    break
                    
                # Небольшая задержка между пакетами
                if batch_end < len(minute_tasks):
                    await asyncio.sleep(0.5)
        
        # Обработка результатов
        for result in minute_results:
            if isinstance(result, Exception):
                logger.error(f"Task exception: {result}")
                results.append({
                    "status": "error",
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                results.append(result)
                
                # Отслеживание токенов в этом окне минуты
                if minute not in minute_windows:
                    minute_windows[minute] = {"requests": 0, "tokens": 0}
                minute_windows[minute]["requests"] += 1
                minute_windows[minute]["tokens"] += result.get("total_tokens", 0)
        
        # Ожидание остатка минуты при необходимости
        minute_elapsed = time.time() - minute_start
        if minute_elapsed < 60 and minute < num_minutes - 1:
            wait_time = 60 - minute_elapsed
            logger.info(f"Ожидание {wait_time:.1f}s до следующей минуты...")
            await asyncio.sleep(wait_time)
    
    # Финальная статистика
    total_time = time.time() - start_time
    successful_requests = sum(1 for r in results if r.get("status") == "success")
    timeout_requests = sum(1 for r in results if r.get("status") == "timeout")
    error_requests = sum(1 for r in results if r.get("status") == "error")
    
    # Подсчет общего количества использованных токенов
    total_tokens = sum(r.get("total_tokens", 0) for r in results if r.get("status") == "success")
    total_estimated_tokens = sum(r.get("prompt_tokens_estimated", 0) for r in results)
    
    # Создание таблицы результатов
    results_table = Table(title="\n🏁 Результаты теста насыщения TPM", show_header=True, header_style="bold cyan")
    results_table.add_column("Метрика", style="yellow")
    results_table.add_column("Значение", style="white")
    
    results_table.add_row("Общее время", f"{total_time:.2f} секунд")
    results_table.add_row("Всего запросов", str(len(results)))
    results_table.add_row("Успешные запросы", f"[green]{successful_requests}[/green]")
    results_table.add_row("Запросы с тайм-аутом", f"[red]{timeout_requests}[/red]" if timeout_requests > 0 else str(timeout_requests))
    results_table.add_row("Запросы с ошибками", f"[yellow]{error_requests}[/yellow]" if error_requests > 0 else str(error_requests))
    results_table.add_row("Всего использовано токенов", f"[bold]{total_tokens:,}[/bold]")
    results_table.add_row("Отправлено токенов (оценка)", f"{total_estimated_tokens:,}")
    results_table.add_row("Фактический TPM", f"[bold green]{(total_tokens / (total_time / 60)):,.0f}[/bold green]")
    if successful_requests > 0:
        results_table.add_row("Среднее токенов/Запрос", f"{(total_tokens / successful_requests):,.0f}")
    
    console.print(results_table)
    
    # Показать окно токенов в минуту
    if minute_windows:
        window_table = Table(title="\nОкно токенов в минуту", show_header=True)
        window_table.add_column("Минута", style="cyan")
        window_table.add_column("Запросы", style="green")
        window_table.add_column("Токены", style="magenta")
        for window, stats in sorted(minute_windows.items()):
            window_table.add_row(str(window + 1), str(stats['requests']), f"{stats['tokens']:,}")
        console.print(window_table)
    
    # Проверка, достигли ли мы ограничений скорости
    rate_limit_errors = [r for r in results if "rate" in str(r.get("error", "")).lower()]
    if rate_limit_errors:
        console.print(Panel(
            f"[bold yellow]⚠️  Достигнут лимит скорости {len(rate_limit_errors)} раз![/bold yellow]\n\n"
            f"Ошибки лимита скорости:\n",
            title="Обнаружен лимит скорости",
            border_style="yellow"
        ))
        for err in rate_limit_errors[:3]:  # Показываем первые 3
            console.print(f"[yellow]  - {err.get('error', 'Неизвестная ошибка')}[/yellow]")
    
    # Проверка, достигли ли мы тайм-аутов
    if timeout_requests > 0:
        timeout_errors = [r for r in results if r.get("status") == "timeout"]
        achieved_tpm = (total_tokens / (total_time / 60)) if total_time > 0 else 0
        console.print(Panel(
            f"[bold red]⏱️  Достигнут тайм-аут {timeout_requests} раз![/bold red]\n\n"
            f"Это указывает на то, что конечная точка API насыщена и не может отвечать вовремя.\n"
            f"Достигнуто приблизительно [bold]{achieved_tpm:,.0f} TPM[/bold] до тайм-аута.\n"
            f"Конечная точка успешно насыщена!",
            title="Анализ тайм-аута",
            border_style="red"
        ))

async def main():
    """Основная функция для запуска теста насыщения TPM."""
    console.print(Panel(
        f"[bold cyan]Тест насыщения лимита TPM[/bold cyan]\n\n"
        f"[yellow]Модель:[/yellow] {MODEL}\n"
        f"[yellow]Цель:[/yellow] {TARGET_TPM:,} токенов в минуту\n"
        f"[yellow]API:[/yellow] {API_BASE}",
        title="🚀 Запуск теста",
        border_style="blue"
    ))
    
    # Проверка доступности tiktoken
    try:
        import tiktoken
    except ImportError:
        console.print("[red]⚠️  tiktoken не установлен. Установите с помощью: pip install tiktoken[/red]")
        return
    
    try:
        # Запуск на 2 минуты для правильного тестирования ограничения скорости
        await token_saturation_test(num_minutes=2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Тест прерван пользователем[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Тест не удался с ошибкой: {str(e)}[/red]")
        raise

if __name__ == "__main__":
    asyncio.run(main())