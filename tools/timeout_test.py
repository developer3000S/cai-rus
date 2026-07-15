#!/usr/bin/env python3
"""
Попытка вызвать litellm.Timeout отправкой множества больших параллельных запросов.
"""

import warnings
warnings.filterwarnings("ignore")

import asyncio
import os
import litellm
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import time

# Загрузка переменных окружения
load_dotenv()

console = Console()
litellm.suppress_debug_info = True
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

API_BASE = "https://api.aliasrobotics.com:666/"
API_KEY = os.getenv("ALIAS_API_KEY", "").strip()
MODEL = os.getenv("CAI_MODEL", "alias1")

# Генерация большого промпта для увеличения времени обработки
LARGE_PROMPT = """
Пожалуйста, проанализируйте следующий сложный сценарий и предоставьте подробный ответ:

""" + "\n".join([f"Точка {i}: " + "x" * 100 for i in range(50)])

async def make_heavy_request(request_id: int, timeout: float = 5.0):
    """Выполнение тяжелого запроса с большим промптом и коротким тайм-аутом."""
    start_time = time.time()
    try:
        response = await litellm.acompletion(
            model=MODEL,
            messages=[{"role": "user", "content": LARGE_PROMPT}],
            api_base=API_BASE,
            api_key=API_KEY,
            custom_llm_provider="openai",
            max_tokens=1000,  # Запрос большого количества токенов
            temperature=0.7,
            timeout=timeout  # Короткий тайм-аут
        )
        return {
            "id": request_id,
            "status": "success",
            "duration": time.time() - start_time
        }
    except litellm.exceptions.Timeout as e:
        console.print(f"\n[bold red]⏱️  ТАЙМАУТ![/bold red] Запрос {request_id} превысил лимит времени после {time.time() - start_time:.2f}s")
        console.print(f"[red]Ошибка: {str(e)}[/red]")
        return {
            "id": request_id,
            "status": "timeout",
            "duration": time.time() - start_time,
            "error": str(e)
        }
    except litellm.exceptions.RateLimitError as e:
        return {
            "id": request_id,
            "status": "rate_limit",
            "duration": time.time() - start_time,
            "error": str(e)
        }
    except Exception as e:
        return {
            "id": request_id,
            "status": "error",
            "duration": time.time() - start_time,
            "error": str(e)[:100]
        }

async def main():
    console.print(Panel(
        "[bold cyan]Тест на вызов тайм-аута[/bold cyan]\n\n"
        f"Модель: {MODEL}\n"
        f"Стратегия: Большие промпты + короткие тайм-ауты + параллельные запросы\n"
        f"Цель: Воспроизвести исключения litellm.Timeout",
        title="🚀 Запуск теста"
    ))
    
    # Тест 1: Один запрос с очень коротким тайм-аутом
    console.print("\n[yellow]Тест 1: Один запрос с тайм-аутом 2 секунды...[/yellow]")
    result = await make_heavy_request(1, timeout=2.0)
    if result["status"] == "timeout":
        console.print("[green]✓ Тайм-аут успешно вызван![/green]")
    
    # Тест 2: Несколько параллельных тяжелых запросов с короткими тайм-аутами
    console.print("\n[yellow]Тест 2: 20 параллельных тяжелых запросов с тайм-аутом 5 секунд...[/yellow]")
    tasks = []
    for i in range(20):
        task = make_heavy_request(i + 1, timeout=5.0)
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    # Подсчитываем результаты
    timeouts = sum(1 for r in results if r["status"] == "timeout")
    successes = sum(1 for r in results if r["status"] == "success")
    rate_limits = sum(1 for r in results if r["status"] == "rate_limit")
    errors = sum(1 for r in results if r["status"] == "error")
    
    console.print(f"\n[bold]Результаты:[/bold]")
    console.print(f"Длительность: {duration:.2f}s")
    console.print(f"⏱️  Тайм-ауты: {timeouts}")
    console.print(f"✅ Успешные: {successes}")
    console.print(f"⚠️  Лимиты скорости: {rate_limits}")
    console.print(f"❌ Ошибки: {errors}")
    
    if timeouts > 0:
        console.print(Panel(
            f"[bold green]✓ litellm.Timeout успешно воспроизведен![/bold green]\n\n"
            f"Получено {timeouts} исключений тайм-аута из {len(results)} запросов.\n"
            f"Это подтверждает, что мы можем воспроизвести поведение тайм-аута.",
            title="Тайм-аут воспроизведен",
            border_style="green"
        ))
        
        # Показываем пример ошибки тайм-аута
        timeout_result = next(r for r in results if r["status"] == "timeout")
        console.print(f"\n[yellow]Пример ошибки тайм-аута:[/yellow]")
        console.print(f"{timeout_result['error']}")
    else:
        console.print("\n[red]Тайм-ауты не вызваны. Инфраструктура может хорошо справляться с нагрузкой.[/red]")

if __name__ == "__main__":
    asyncio.run(main())