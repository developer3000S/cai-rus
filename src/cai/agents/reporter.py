"""Агент-репортёр — создаёт профессиональные отчёты по результатам оценки безопасности"""

import os
from dotenv import load_dotenv
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel  # pylint: disable=import-error
from openai import AsyncOpenAI
from cai.util import create_system_prompt_renderer, load_prompt_template

load_dotenv()
# Промпты
reporting_agent_system_prompt = load_prompt_template("prompts/system_reporting_agent.md")

# Инструменты выполнения не используются: репортёр только синтезирует
# разговор в HTML. Это предотвращает выполнение инструкций пентеста,
# которые могут оставаться в истории чата.


# Создаём экземпляр агента-репортёра
reporting_agent = Agent(
    name="reporting agent",
    instructions=create_system_prompt_renderer(
        reporting_agent_system_prompt,
        cyber_micro_profile_key="reporting",
    ),
    description="""Agent that generates reports in html.""",
    tools=[],
    model=OpenAIChatCompletionsModel(
        model=os.getenv("CAI_MODEL", "alias1"),
        openai_client=AsyncOpenAI(),
    ),
)
