"""
Паттерн Purple Team GCTR — команды red и blue с общим отслеживанием CTR.

Этот паттерн запускает агентов red и blue team параллельно с:
- Единым контекстом (общей историей сообщений)
- Совместным отслеживанием использования инструментов обеими командами
- Общим CTR-анализом, запускаемым каждые CAI_GCTR_NITERATIONS суммарных вызовов инструментов
- Дайджестом CTR, инъектируемым в системные запросы обоих агентов через CAI_CTR_DIGEST_MODE
"""

from cai.repl.commands.parallel import ParallelConfig

# Примечание: этот паттерн использует стандартных агентов red и blue team GCTR.
# Для настоящей координации purple team с общим подсчётом инструментов необходима
# кастомная реализация, совместно использующая CTRHooks между обоими агентами.
#
# Агенты, определённые в purple_teamer_gctr.py (redteam_agent и blueteam_agent),
# используют экземпляр SharedCTRHooks для отслеживания суммарного использования
# инструментов обеими командами.

# Конфигурация паттерна для purple team с общим GCTR
purple_team_gctr_pattern = {
    "name": "purple_team_gctr",
    "type": "parallel",
    "description": "Purple team (red + blue) с общим отслеживанием GCTR — объединяет активность red и blue team для единого теоретико-игрового анализа",
    "configs": [
        # Используются варианты purple team из purple_teamer_gctr.py
        # Эти агенты совместно используют единый экземпляр CTRHooks для общего отслеживания
        ParallelConfig("purple_redteam_agent", unified_context=True),
        ParallelConfig("purple_blueteam_agent", unified_context=True),
    ],
    "unified_context": True,
}
