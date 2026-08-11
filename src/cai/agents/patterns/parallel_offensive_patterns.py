from cai.repl.commands.parallel import ParallelConfig

# Конфигурация паттерна
offsec_pattern = {
    "name": "offsec_pattern",
    "type": "parallel",
    "description": (
        "Bug bounty и роевые атаки red team с различными контекстами для " "наступательных операций по безопасности"
    ),
    "configs": [ParallelConfig("redteam_swarm_pattern"), ParallelConfig("bb_triage_swarm_pattern")],
    "unified_context": False,
}
