#!/usr/bin/env python3
"""
Корректное тестирование ограничения скорости путем проверки текущего статуса и ожидания при необходимости.
"""

import warnings
warnings.filterwarnings("ignore")

import asyncio
import os
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import time

# Загрузка переменных окружения
load_dotenv()

console = Console()

API_BASE = "https://api.aliasrobotics.com:666/"
API_KEY = os.getenv("ALIAS_API_KEY", "").strip()
MODEL = os.getenv("CAI_MODEL", "alias1")

async def check_rate_limit_status(session: httpx.AsyncClient):
    """Проверка текущего статуса ограничения скорости."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10,
        "temperature": 0.7
    }
    
    try:
        response = await session.post(
            f"{API_BASE}v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10.0
        )
        
        return {
            "status": response.status_code,
            "rpm_limit": int(response.headers.get("x-ratelimit-limit-requests", 60)),
            "rpm_remaining": int(response.headers.get("x-ratelimit-remaining-requests", 0)),
            "tpm_limit": int(response.headers.get("x-ratelimit-limit-tokens", 500000)),
            "tpm_remaining": int(response.headers.get("x-ratelimit-remaining-tokens", 0))
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return {
                "status": 429,
                "rpm_limit": 60,
                "rpm_remaining": 0,
                "error": "В настоящее время действует ограничение скорости"
            }
        raise

async def make_request(session: httpx.AsyncClient, request_id: int):
    """Выполнение одного запроса."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10,
        "temperature": 0.7
    }
    
    try:
        response = await session.post(
            f"{API_BASE}v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10.0
        )
        
        return {
            "id": request_id,
            "status": response.status_code,
            "rpm_remaining": response.headers.get("x-ratelimit-remaining-requests", "?")
        }
    except httpx.HTTPStatusError as e:
        return {
            "id": request_id,
            "status": e.response.status_code,
            "rpm_remaining": e.response.headers.get("x-ratelimit-remaining-requests", "?")
        }

async def main():
    console.print(Panel(
        "[bold cyan]Тестирование ограничения скорости с проверкой статуса[/bold cyan]\n\n"
        "Этот скрипт проверит текущий статус ограничения скорости и проведет тестирование соответственно.",
        title="🚀 Запуск теста"
    ))
    
    async with httpx.AsyncClient() as session:
        # Сначала проверяем текущий статус ограничения скорости
        console.print("\n[yellow]Проверка текущего статуса ограничения скорости...[/yellow]")
        status = await check_rate_limit_status(session)
        
        if status["status"] == 429:
            console.print("[red]В настоящее время действует ограничение скорости! Пожалуйста, подождите минуту и попробуйте снова.[/red]")
            return
        
        console.print(f"RPM Limit: {status['rpm_limit']}")
        console.print(f"RPM Remaining: {status['rpm_remaining']}")
        
        if status['rpm_remaining'] < 65:
            console.print(f"\n[yellow]Осталось только {status['rpm_remaining']} запросов в текущем окне.[/yellow]")
            console.print("[yellow]Ожидание 60 секунд для сброса ограничения скорости...[/yellow]")
            await asyncio.sleep(60)
            
            # Проверяем снова
            status = await check_rate_limit_status(session)
            console.print(f"\nПосле ожидания - RPM Осталось: {status['rpm_remaining']}")
        
        # Теперь отправляем 65 запросов, чтобы превысить лимит 60
        console.print(f"\n[bold green]Отправка 65 запросов для превышения лимита {status['rpm_limit']} RPM...[/bold green]\n")
        
        tasks = []
        for i in range(65):
            tasks.append(make_request(session, i + 1))
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        # Подсчитываем результаты
        success_200 = sum(1 for r in results if r["status"] == 200)
        rate_limited_429 = sum(1 for r in results if r["status"] == 429)
        
        console.print(f"\n[bold]Результаты:[/bold]")
        console.print(f"Длительность: {duration:.2f}s")
        console.print(f"✅ Успешные (200): {success_200}")
        console.print(f"⚠️  Ограничены скоростью (429): {rate_limited_429}")
        
        # Показываем некоторые отдельные результаты
        console.print(f"\n[bold]Примеры результатов:[/bold]")
        for i in [0, 30, 58, 59, 60, 61, 62, 63, 64]:
            if i < len(results):
                r = results[i]
                status_str = "[green]200[/green]" if r["status"] == 200 else "[red]429[/red]"
                console.print(f"Request {r['id']:2d}: Status {status_str}, RPM Remaining: {r['rpm_remaining']}")
        
        if rate_limited_429 > 0:
            console.print(Panel(
                f"[bold green]✓ Ограничение скорости подтверждено![/bold green]\n\n"
                f"Успешно отправлено {success_200} запросов перед достижением ограничения скорости.\n"
                f"Остальные {rate_limited_429} запросов были ограничены со статусом 429.",
                title="Тест успешно пройден",
                border_style="green"
            ))

if __name__ == "__main__":
    asyncio.run(main())