"""
Реализация паттерна циклического роя для операций Red Team

Этот модуль создаёт скоординированную мультиагентную систему, в которой специализированные агенты
совместно работают над задачами оценки безопасности. Паттерн реализует направленный граф
связей агентов, где каждый агент может передавать контекст (историю сообщений)
другому агенту через функции передачи управления, формируя полную коммуникационную сеть
для всестороннего анализа безопасности.
"""

from cai.agents.red_teamer import redteam_agent
from cai.agents.thought import thought_agent
from cai.agents.mail import dns_smtp_agent
from cai.sdk.agents import handoff


# Клонируем агентов, чтобы не изменять исходные экземпляры
_redteam_agent_copy = redteam_agent.clone()
_thought_agent_copy = thought_agent.clone()
_dns_smtp_agent_copy = dns_smtp_agent.clone()

# Очищаем существующие передачи управления для обеспечения независимости
_redteam_agent_copy.handoffs = []
_thought_agent_copy.handoffs = []
_dns_smtp_agent_copy.handoffs = []

# Создаём передачи управления с помощью функции handoff из SDK
_dns_smtp_handoff = handoff(
    agent=_dns_smtp_agent_copy,
    tool_description_override="Use for DNS scans and domain reconnaissance about DMARC and DKIM records",
)

_redteam_handoff = handoff(
    agent=_redteam_agent_copy,
    tool_description_override="Transfer to Red Team Agent for security assessment and exploitation tasks",
)

_thought_handoff = handoff(
    agent=_thought_agent_copy,
    tool_description_override="Transfer to Thought Agent for analysis and planning",
)

_thought_agent_copy.name = "Red team manager"
# Регистрируем передачи управления для создания межагентных каналов связи
_redteam_agent_copy.handoffs.append(_dns_smtp_handoff)
_dns_smtp_agent_copy.handoffs.append(_redteam_handoff)
_thought_agent_copy.handoffs.append(_redteam_handoff)

# Инициализируем роевой паттерн с агентом-мыслителем в качестве точки входа
redteam_swarm_pattern = _thought_agent_copy
redteam_swarm_pattern.pattern = "swarm"

# Помечаем всех агентов в рое атрибутом паттерна
_redteam_agent_copy.pattern = "swarm"
_dns_smtp_agent_copy.pattern = "swarm"
