"""
Очередь запросов — управляет запросами в очереди для последовательного выполнения
"""

import asyncio
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class QueuedPrompt:
    """Запрос, ожидающий выполнения"""
    prompt: str
    terminal_number: Optional[int] = None  # None означает все терминалы
    timestamp: datetime = None
    priority: int = 0  # Более высокий приоритет выполняется первым
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PromptQueue:
    """Управляет очередью запросов для выполнения"""
    
    def __init__(self):
        self._queue: List[QueuedPrompt] = []
        self._lock = asyncio.Lock()
        self._processing = False
        self._process_task: Optional[asyncio.Task] = None
        self._current_prompt: Optional[QueuedPrompt] = None
        self._process_callback: Optional[Callable] = None
        self.logger = logging.getLogger("PromptQueue")
        
    def set_process_callback(self, callback: Callable) -> None:
        """Устанавливает функцию обратного вызова для обработки запросов"""
        self._process_callback = callback
        
    async def add_prompt(self, prompt: str, terminal_number: Optional[int] = None, priority: int = 0) -> None:
        """Добавляет запрос в очередь"""
        async with self._lock:
            queued_prompt = QueuedPrompt(
                prompt=prompt,
                terminal_number=terminal_number,
                priority=priority
            )
            
            # Вставка по приоритету (более высокий приоритет — первый)
            insert_pos = 0
            for i, existing in enumerate(self._queue):
                if existing.priority < priority:
                    insert_pos = i
                    break
                insert_pos = i + 1
                
            self._queue.insert(insert_pos, queued_prompt)
            self.logger.info(f"Added prompt to queue: '{prompt[:50]}...' (priority: {priority})")
            
        # Запускаем обработку, если ещё не выполняется
        if not self._processing:
            # единственная задача-обработчик
            self._process_task = asyncio.create_task(self._process_queue(), name="tui-prompt-queue")
            
    async def _process_queue(self) -> None:
        """Обрабатывает запросы из очереди"""
        async with self._lock:
            if self._processing:
                return
            self._processing = True
            
        try:
            while True:
                # Получаем следующий запрос
                async with self._lock:
                    if not self._queue:
                        break
                    self._current_prompt = self._queue.pop(0)
                    
                # Обрабатываем запрос
                if self._process_callback:
                    try:
                        await self._process_callback(
                            self._current_prompt.prompt,
                            self._current_prompt.terminal_number
                        )
                    except Exception as e:
                        self.logger.error(f"Error processing prompt: {e}")
                        
                # Небольшая задержка между запросами (по умолчанию без изменений)
                await asyncio.sleep(0.5)
                
        finally:
            async with self._lock:
                self._processing = False
                self._current_prompt = None
                self._process_task = None
                
    def get_queue_status(self) -> Dict[str, Any]:
        """Возвращает текущий статус очереди"""
        return {
            "queue_length": len(self._queue),
            "processing": self._processing,
            "current_prompt": self._current_prompt.prompt if self._current_prompt else None,
            "prompts": [
                {
                    "prompt": p.prompt[:50] + "..." if len(p.prompt) > 50 else p.prompt,
                    "terminal": p.terminal_number,
                    "priority": p.priority,
                    "timestamp": p.timestamp.isoformat()
                }
                for p in self._queue[:5]  # Показываем первые 5 запросов
            ]
        }
        
    def clear_queue(self) -> int:
        """Очищает все запросы в очереди и возвращает количество удалённых"""
        count = len(self._queue)
        self._queue.clear()
        self.logger.info(f"Cleared {count} prompts from queue")
        return count
        
    def remove_prompt(self, index: int) -> bool:
        """Удаляет конкретный запрос по индексу"""
        if 0 <= index < len(self._queue):
            removed = self._queue.pop(index)
            self.logger.info(f"Removed prompt: '{removed.prompt[:50]}...'")
            return True
        return False
        
    def get_queue_size(self) -> int:
        """Возвращает текущий размер очереди"""
        return len(self._queue)
        
    def is_processing(self) -> bool:
        """Проверяет, обрабатывается ли очередь в данный момент"""
        return self._processing


# Глобальный экземпляр очереди запросов
PROMPT_QUEUE = PromptQueue()
