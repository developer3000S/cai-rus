"""Агент атак воспроизведения и контрнаступления
Специализированный модуль агента, ориентированный на сетевые атаки воспроизведения,
манипуляцию пакетами и контрнаступательные техники для тестирования безопасности
и реагирования на инциденты.
Агент специализируется на:
- Захвате и анализе сетевых пакетов
- Атаках воспроизведения трафика против различных протоколов
- Воспроизведении последовательностей аутентификации и токенов сессий
- Манипуляции и инъекции трафика
- Симуляции атак «человек посередине»
- Перехвате TCP-сессий
- Техниках эксплуатации протоколов
- Тестировании защиты от атак воспроизведения
Цели:
- Обнаружение и эксплуатация уязвимостей воспроизведения
- Тестирование безопасности реализации протоколов
- Симуляция продвинутых постоянных угроз
- Оценка защитных мер против атак воспроизведения
"""

from openai import AsyncOpenAI
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel  # pylint: disable=import-error
from cai.util import load_prompt_template, create_system_prompt_renderer
from cai.config import get_config
from dotenv import load_dotenv
from cai.tools.command_and_control.sshpass import (  # pylint: disable=import-error # noqa: E501
    run_ssh_command_with_credentials,
)

from cai.tools.reconnaissance.generic_linux_command import (  # pylint: disable=import-error # noqa: E501
generic_linux_command,
)

from cai.tools.reconnaissance.exec_code import (  # pylint: disable=import-error # noqa: E501
    execute_code,
)
from cai.tools.web.search_web import (  # pylint: disable=import-error # noqa: E501
    make_web_search_with_explanation,
)

# Импорт сетевых инструментов
from cai.tools.network.capture_traffic import (  # pylint: disable=import-error # noqa: E501
    capture_remote_traffic,
    remote_capture_session,
)

load_dotenv()
_cfg = get_config()

# Промпты
replay_attack_agent_prompt = load_prompt_template("prompts/system_replay_attack_agent.md")

# Формируем список инструментов на основе доступных API-ключей (через CAIConfig) [S]
tools = [
    generic_linux_command,
    run_ssh_command_with_credentials,
    execute_code,
    capture_remote_traffic,
    remote_capture_session,
]

# Добавляем условные инструменты на основе доступных API-ключей [S]
if _cfg.perplexity_api_key:
    tools.append(make_web_search_with_explanation)


# Создаём экземпляр агента
replay_attack_agent = Agent(
    name="Replay Attack Agent",
    instructions=create_system_prompt_renderer(
        replay_attack_agent_prompt,
        cyber_micro_profile_key="replay",
    ),
    description="""Agent that specializes in network replay attacks and counteroffensive techniques.
                   Expert in packet manipulation, traffic replay, and protocol exploitation.""",
    model=OpenAIChatCompletionsModel(
        model=_cfg.model,
        openai_client=AsyncOpenAI(),
    ),
    tools=tools,
)
