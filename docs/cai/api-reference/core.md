# Справочник по основному API

## Agent

Класс `Agent` является основной абстракцией для реализации ИИ-агентов в CAI.

```python
from cai import Agent

class MyAgent(Agent):
    def __init__(self):
        super().__init__()
        # Initialize your agent here
        
    async def run(self, input_data):
        # Implement your agent's logic here
        pass
```

### Основные методы

- `__init__()`: Инициализация агента
- `run(input_data)`: Основной метод выполнения
- `add_tool(tool)`: Добавление инструмента агенту
- `remove_tool(tool_name)`: Удаление инструмента из агента

## Tools

Инструменты (Tools) — это строительные блоки, которые агенты используют для взаимодействия с внешним миром.

```python
from cai import Tool

class MyTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Description of what the tool does"
        )
    
    async def execute(self, **kwargs):
        # Implement tool logic here
        pass
```

### Встроенные инструменты

- `LinuxCmd`: Выполнение команд Linux
- `WebSearch`: Выполнение веб-поиска
- `Code`: Выполнение кода
- `SSHTunnel`: Создание SSH-туннелей

## Patterns

Паттерны (Patterns) — это переиспользуемые модели поведения агентов, которые можно комбинировать между собой.

```python
from cai import Pattern

class MyPattern(Pattern):
    def __init__(self):
        super().__init__()
        
    async def execute(self, context):
        # Implement pattern logic here
        pass
```

## Handoffs

Передачи управления (Handoffs) позволяют агентам передавать контроль другим агентам или операторам-людям.

```python
from cai import Handoff

class MyHandoff(Handoff):
    def __init__(self):
        super().__init__()
        
    async def execute(self, context):
        # Implement handoff logic here
        pass
```

## Tracing

Трассировка (Tracing) обеспечивает видимость процесса выполнения агента.

```python
from cai import Tracer

tracer = Tracer()
tracer.start_trace()
# ... agent execution ...
tracer.end_trace()
```

## HITL (Human In The Loop)

HITL позволяет операторам-людям взаимодействовать с агентами в процессе выполнения.

```python
from cai import HITL

class MyHITL(HITL):
    def __init__(self):
        super().__init__()
        
    async def execute(self, context):
        # Implement HITL logic here
        pass
```