"""
Паттерн параллельной оценки безопасности — red/blue team с общим контекстом.

Этот паттерн демонстрирует использование унифицированного класса Pattern для
параллельного выполнения агентов, при котором агенты red и blue team используют
один и тот же контекст.
"""

from cai.repl.commands.parallel import ParallelConfig

# Конфигурация паттерна
blue_team_red_team_shared_context_pattern = {
    "name": "blue_team_red_team_shared_context",
    "type": "parallel",
    "description": "Агенты red и blue team с общим контекстом",
    "configs": [
        ParallelConfig("redteam_agent", unified_context=True),
        ParallelConfig("blueteam_agent", unified_context=True),
    ],
    "unified_context": True,
}
