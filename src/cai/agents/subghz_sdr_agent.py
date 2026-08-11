"""Агент анализа радиочастот в диапазоне Sub-GHz с использованием HackRF One"""

import os
from dotenv import load_dotenv
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel  # pylint: disable=import-error
from openai import AsyncOpenAI
from cai.util import create_system_prompt_renderer, load_prompt_template
from cai.tools.command_and_control.sshpass import (  # pylint: disable=import-error # noqa: E501
    run_ssh_command_with_credentials,
)

from cai.tools.reconnaissance.generic_linux_command import (  # pylint: disable=import-error # noqa: E501
generic_linux_command,
)
from cai.tools.web.search_web import (  # pylint: disable=import-error # noqa: E501
    make_web_search_with_explanation,
)

from cai.tools.reconnaissance.exec_code import (  # pylint: disable=import-error # noqa: E501
    execute_code,
)

load_dotenv()
# Промпты
subghz_agent_system_prompt = load_prompt_template("prompts/subghz_agent.md")

# Формируем список функций
functions = [
    generic_linux_command,
    run_ssh_command_with_credentials,
    execute_code,
]

# Добавляем функцию make_web_search_with_explanation, если установлена переменная окружения PERPLEXITY_API_KEY
if os.getenv("PERPLEXITY_API_KEY"):
    functions.append(make_web_search_with_explanation)

# Создаём агента
subghz_sdr_agent = Agent(
    name="Sub-GHz SDR Specialist",
    instructions=create_system_prompt_renderer(
        subghz_agent_system_prompt,
        cyber_micro_profile_key="sdr",
    ),
    description="""Agent for sub-GHz radio frequency analysis using HackRF One.
                   Specializes in signal capture, replay, and protocol analysis for IoT, 
                   automotive, industrial, and wireless security applications.""",
    tools=functions,
    model=OpenAIChatCompletionsModel(
        model=os.getenv("CAI_MODEL", "alias1"),
        openai_client=AsyncOpenAI(),
    ),
)
