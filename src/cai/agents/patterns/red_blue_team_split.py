"""
Паттерн параллельной оценки безопасности — red/blue team с разделённым контекстом.

Этот паттерн демонстрирует использование унифицированного класса Pattern для
параллельного выполнения агентов, при котором агенты red и blue team работают
в отдельных контекстах для независимого анализа.
"""

from cai.repl.commands.parallel import ParallelConfig

# Конфигурация паттерна
blue_team_red_team_split_context_pattern = {
    "name": "blue_team_red_team_split_context",
    "type": "parallel",
    "description": (
        "Агенты red и blue team с различными контекстами для " "комплексной оценки безопасности"
    ),
    "configs": [ParallelConfig("redteam_agent"), ParallelConfig("blueteam_agent")],
    "unified_context": False,
}
