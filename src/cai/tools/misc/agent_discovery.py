"""
Инструмент обнаружения агентов для Selection Agent

Этот инструмент позволяет агенту выбора динамически обнаруживать и анализировать
все доступные агенты в системе CAI для формирования обоснованных рекомендаций.
"""

import importlib
import os
import pkgutil
from functools import lru_cache
from typing import Dict, List, Any
from cai.sdk.agents import Agent, function_tool


@lru_cache(maxsize=1)
def _check_available_agents() -> Dict[str, Any]:
    """
    Проверяет все доступные агенты в системе CAI и возвращает их подробную информацию.

    Кэшируется с помощью ``lru_cache(maxsize=1)``: каталог агентов статичен на
    протяжении всей сессии (без горячей перезагрузки модулей агентов), поэтому
    полный обход ``pkgutil.iter_modules`` + ``importlib.import_module`` при каждом
    вызове инструмента LLM (маршрутизация оркестратора, поиск ``_get_agent_number`` и т.д.)
    является избыточным. Вызывающие функции должны обрабатывать возвращаемый словарь как доступный только для чтения.

    Returns:
        Dict с полной информацией о всех доступных агентах
    """
    agents_info = {}
    
    # Import the agents module
    import cai.agents
    
    # Scan the main agents directory
    for _, name, _ in pkgutil.iter_modules(cai.agents.__path__, cai.agents.__name__ + "."):
        try:
            module = importlib.import_module(name)
            
            # Look for Agent instances in the module
            for attr_name in dir(module):
                if attr_name.startswith("_"):
                    continue
                    
                attr = getattr(module, attr_name)
                if isinstance(attr, Agent):
                    agent_info = {
                        "name": attr.name,
                        "description": getattr(attr, "description", "Описание отсутствует"),
                        "module": name,
                        "variable_name": attr_name,
                        "tools": [],
                        "capabilities": [],
                        "specialization": _extract_specialization(attr.name, getattr(attr, "description", "")),
                        "use_cases": _extract_use_cases(getattr(attr, "description", ""))
                    }
                    
                    # Extract tool information
                    if hasattr(attr, "tools") and attr.tools:
                        for tool in attr.tools:
                            if hasattr(tool, "name"):
                                agent_info["tools"].append({
                                    "name": tool.name,
                                    "description": getattr(tool, "description", "")
                                })
                    
                    agents_info[attr_name] = agent_info
                    
        except (ImportError, AttributeError) as e:
            continue
    
    # Also check patterns subdirectory
    patterns_path = os.path.join(os.path.dirname(cai.agents.__file__), "patterns")
    if os.path.exists(patterns_path):
        for _, name, _ in pkgutil.iter_modules([patterns_path], cai.agents.__name__ + ".patterns."):
            try:
                module = importlib.import_module(name)
                
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue
                        
                    attr = getattr(module, attr_name)
                    if isinstance(attr, Agent):
                        agent_info = {
                            "name": attr.name,
                            "description": getattr(attr, "description", "Описание отсутствует"),
                            "module": name,
                            "variable_name": attr_name,
                            "type": "pattern",
                            "tools": [],
                            "capabilities": [],
                            "specialization": _extract_specialization(attr.name, getattr(attr, "description", "")),
                            "use_cases": _extract_use_cases(getattr(attr, "description", ""))
                        }
                        
                        agents_info[attr_name] = agent_info
                        
            except (ImportError, AttributeError):
                continue
    
    # Create indexed list for easy reference
    agent_list = list(agents_info.keys())
    indexed_agents = {}
    for i, agent_key in enumerate(agent_list, 1):
        indexed_agents[i] = {
            "key": agent_key,
            "info": agents_info[agent_key]
        }
    
    return {
        "total_agents": len(agents_info),
        "agents": agents_info,
        "indexed_agents": indexed_agents,
        "agent_list": agent_list,
        "categories": _categorize_agents(agents_info)
    }


def _analyze_task_requirements(task_description: str) -> Dict[str, Any]:
    """
    Анализирует описание задачи пользователя для извлечения ключевых требований и характеристик.
    
    Args:
        task_description: Описание пользователя того, чего он хочет достичь
        
    Returns:
        Dict с анализом требований задачи
    """
    task_lower = task_description.lower()
    
    # Define task categories and keywords
    task_categories = {
        "penetration_testing": [
            "пентест", "пентестинг", "тестирование на проникновение", "оценка безопасности",
            "уязвимость", "атака", "взлом", "проникновение", "красная команда", "pentest", "penetration test", "security assessment", "vulnerability assessment",
            "exploit", "attack", "breach", "hack", "infiltration", "red team"
        ],
        "bug_bounty": [
            "багбаунти", "поиск уязвимостей", "веб-безопасность", "тестирование API",
            "ответственное раскрытие", "безопасность", "охота за уязвимостями",
            "bug bounty", "vulnerability discovery", "web security", "api testing",
            "responsible disclosure", "security bug", "vulnerability hunting"
        ],
        "blue_team": [
            "защита", "оборона", "синяя команда", "мониторинг", "обнаружение",
            "реагирование на инциденты", "контроль безопасности", "поиск угроз",
            "defense", "defensive", "blue team", "monitoring", "detection",
            "incident response", "security monitoring", "threat hunting", "soc"
        ],
        "forensics": [
            "форензика", "DFIR", "реагирование на инциденты", "цифровая форензика",
            "расследование", "доказательства", "анализ вредоносного ПО", "расследование взлома",
            "forensics", "dfir", "incident response", "digital forensics",
            "investigation", "evidence", "malware analysis", "breach investigation"
        ],
        "reverse_engineering": [
            "реверс-инжиниринг", "анализ бинарников", "анализ прошивок",
            "дассемблирование", "декомпиляция", "анализ вредоносного ПО", "анализ кода",
            "reverse engineering", "binary analysis", "firmware analysis",
            "disassembly", "decompilation", "malware analysis", "code analysis"
        ],
        "network_security": [
            "сеть", "анализ трафика", "захват пакетов", "мониторинг сети",
            "анализ протоколов", "сетевая форензика",
            "network", "traffic analysis", "packet capture", "network monitoring",
            "protocol analysis", "wireshark", "tcpdump", "network forensics"
        ],
        "wireless_security": [
            "wifi", "беспроводная сеть", "bluetooth", "радио", "rf", "802.11",
            "безопасность беспроводных сетей", "взлом wifi", "пентест беспроводных сетей",
            "wireless", "wireless security", "wifi hacking", "wireless penetration"
        ],
        "memory_analysis": [
            "анализ памяти", "форензика памяти", "анализ процессов",
            "анализ среды выполнения", "дамп памяти", "анализ кучи",
            "memory analysis", "memory forensics", "process analysis",
            "runtime analysis", "memory dump", "heap analysis"
        ],
        "ctf": [
            "ctf", "захват флага", "соревнование", "задача", "конкурс",
            "безопасностное соревнование", "хакерское задание",
            "capture the flag", "challenge", "flag", "competition",
            "security challenge", "hacking challenge"
        ],
        "reporting": [
            "отчёт", "документация", "сводка", "результаты", "аналитический отчёт",
            "отчёт по безопасности", "резюме для руководства",
            "report", "documentation", "summary", "findings", "analysis report",
            "security report", "executive summary"
        ]
    }
    
    # Analyze task characteristics
    detected_categories = []
    confidence_scores = {}
    
    for category, keywords in task_categories.items():
        matches = sum(1 for keyword in keywords if keyword in task_lower)
        if matches > 0:
            detected_categories.append(category)
            confidence_scores[category] = matches / len(keywords)
    
    # Determine complexity and scope
    complexity_indicators = {
        "simple": ["простая", "базовая", "быстрая", "лёгкая", "simple", "basic", "quick", "fast", "easy"],
        "medium": ["подробная", "детальная", "тщательная", "полная", "comprehensive", "detailed", "thorough", "complete"],
        "complex": ["продвинутая", "углублённая", "расширенная", "сложная", "complex", "advanced", "deep", "extensive", "sophisticated"]
    }
    
    complexity = "medium"  # default
    for level, indicators in complexity_indicators.items():
        if any(indicator in task_lower for indicator in indicators):
            complexity = level
            break
    
    # Determine if multiple agents might be needed
    multi_agent_indicators = [
        "комплексная", "полная", "завершённая", "полный цикл", "несколько",
        "оба", "все", "различные", "разные перспективы",
        "comprehensive", "full", "complete", "end-to-end", "multiple",
        "both", "all", "various", "different perspectives"
    ]
    
    needs_multiple_agents = any(indicator in task_lower for indicator in multi_agent_indicators)
    
    return {
        "task_description": task_description,
        "detected_categories": detected_categories,
        "confidence_scores": confidence_scores,
        "complexity": complexity,
        "needs_multiple_agents": needs_multiple_agents,
        "primary_category": max(confidence_scores.items(), key=lambda x: x[1])[0] if confidence_scores else "general",
        "recommendations": _generate_initial_recommendations(detected_categories, complexity, needs_multiple_agents)
    }


def _extract_specialization(name: str, description: str) -> str:
    """Извлекает основную специализацию из имени и описания агента"""
    specializations = {
        "red team": ["red team", "penetration", "exploit", "attack"],
        "blue team": ["blue team", "defense", "monitoring", "protection"],
        "bug bounty": ["bug bounty", "vulnerability discovery", "web security"],
        "forensics": ["forensics", "dfir", "investigation", "incident response"],
        "reverse engineering": ["reverse engineering", "binary analysis", "firmware"],
        "network security": ["network", "traffic", "protocol", "packet"],
        "wireless": ["wifi", "wireless", "radio", "rf"],
        "memory analysis": ["memory", "process", "runtime"],
        "reporting": ["report", "documentation", "summary"],
        "ctf": ["ctf", "challenge", "flag"],
        "general": ["general", "basic", "tool", "command"]
    }
    
    # Handle None values safely
    safe_name = name or ""
    safe_description = description or ""
    text = (safe_name + " " + safe_description).lower()
    
    for spec, keywords in specializations.items():
        if any(keyword in text for keyword in keywords):
            return spec
    
    return "general"


def _extract_use_cases(description: str) -> List[str]:
    """Извлекает потенциальные варианты использования из описания агента"""
    use_cases = []
    
    use_case_patterns = {
        "Тестирование на проникновение": ["penetration", "pentest", "security assessment"],
        "Оценка уязвимостей": ["vulnerability", "security testing", "weakness"],
        "Анализ сети": ["network", "traffic", "protocol"],
        "Веб-безопасность": ["web", "api", "application"],
        "Анализ системы": ["system", "host", "server"],
        "Анализ вредоносного ПО": ["malware", "binary", "reverse"],
        "Реагирование на инциденты": ["incident", "response", "investigation"],
        "Соответствие требованиям": ["compliance", "audit", "standard"],
        "CTF-задачи": ["ctf", "challenge", "flag"],
        "Отчётность": ["report", "documentation", "findings"]
    }
    
    # Handle None values safely
    safe_description = description or ""
    desc_lower = safe_description.lower()
    
    for use_case, keywords in use_case_patterns.items():
        if any(keyword in desc_lower for keyword in keywords):
            use_cases.append(use_case)
    
    return use_cases


def _categorize_agents(agents_info: Dict[str, Any]) -> Dict[str, List[str]]:
    """Категоризирует агентов по их специализации"""
    categories = {}
    
    for agent_name, info in agents_info.items():
        spec = info.get("specialization", "general")
        if spec not in categories:
            categories[spec] = []
        categories[spec].append(agent_name)
    
    return categories


def _generate_initial_recommendations(categories: List[str], complexity: str, needs_multiple: bool) -> List[str]:
    """Генерирует начальные рекомендации на основе анализа задачи"""
    recommendations = []
    
    if "penetration_testing" in categories:
        recommendations.append("Рассмотрите redteam_agent для комплексного тестирования на проникновение")
    
    if "bug_bounty" in categories:
        recommendations.append("Рассмотрите bug_bounter_agent для поиска уязвимостей")
    
    if "blue_team" in categories:
        recommendations.append("Рассмотрите blueteam_agent для анализа защитной безопасности")
    
    if "forensics" in categories:
        recommendations.append("Рассмотрите dfir_agent для цифровой форензики и реагирования на инциденты")
    
    if "network_security" in categories:
        recommendations.append("Рассмотрите network_security_analyzer_agent для анализа сети")
    
    if "wireless_security" in categories:
        recommendations.append("Рассмотрите wifi_security_agent для тестирования безопасности беспроводных сетей")
    
    if "reverse_engineering" in categories:
        recommendations.append("Рассмотрите reverse_engineering_agent для анализа бинарников")
    
    if "memory_analysis" in categories:
        recommendations.append("Рассмотрите memory_analysis_agent для анализа среды выполнения")
    
    if "reporting" in categories:
        recommendations.append("Рассмотрите reporting_agent для формирования отчётов")
    
    if needs_multiple:
        recommendations.append("Рассмотрите использование нескольких агентов или шаблона для комплексного покрытия")
    
    if complexity == "complex":
        recommendations.append("Для сложных задач могут быть полезны иерархические шаблоны или шаблоны роя")
    
    return recommendations


def _get_agent_number(agent_name: str) -> Dict[str, Any]:
    """
    Получает числовой индекс конкретного агента для удобной ссылки в команде.
    
    Args:
        agent_name: Имя/ключ агента для поиска
        
    Returns:
        Dict с номером агента, командой и подробностями
    """
    # Get all agents
    agents_data = _check_available_agents()
    indexed_agents = agents_data.get("indexed_agents", {})
    
    # Find the agent
    for number, agent_data in indexed_agents.items():
        if agent_data["key"].lower() == agent_name.lower():
            agent_info = agent_data["info"]
            return {
                "agent_number": number,
                "agent_key": agent_data["key"],
                "agent_name": agent_info.get("name", agent_data["key"]),
                "command": f"/agent {number}",
                "alt_command": f"/agent {agent_data['key']}",
                "found": True,
                "description": agent_info.get("description", "Описание отсутствует")
            }
    
    return {
        "found": False,
        "message": f"Агент '{agent_name}' не найден",
        "total_agents": agents_data.get("total_agents", 0)
    }


# Create the function tools for the agent.
# `name_override` is used so the names exposed to the LLM (and matched by
# ``_COMPACT_HIDDEN_TOOL_NAMES``) don't carry the leading underscore from
# the private helper functions above.
check_available_agents = function_tool(
    _check_available_agents,
    name_override="check_available_agents",
)
analyze_task_requirements = function_tool(
    _analyze_task_requirements,
    name_override="analyze_task_requirements",
)
get_agent_number = function_tool(
    _get_agent_number,
    name_override="get_agent_number",
)
