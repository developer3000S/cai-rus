"""
Первый прототип агента-рассуждателя

использует рассуждатель в качестве вызова инструмента

поддержка мета-агента может быть лучше реализована через @cai.sdk.agents.meta.reasoner_support
"""

from cai.tools.misc.reasoning import think
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel  # pylint: disable=import-error
from openai import AsyncOpenAI
from cai.util import load_prompt_template, create_system_prompt_renderer
from cai.config import get_config

_cfg = get_config()
thought_agent_system_prompt = load_prompt_template("prompts/system_thought_router.md")

# Агент мыслительного процесса для анализа и планирования
thought_agent = Agent(
    name="ThoughtAgent",
    model=OpenAIChatCompletionsModel(
        model=_cfg.model,
        openai_client=AsyncOpenAI(),
    ),
    description="""Agent focused on analyzing and planning the next steps
                   in a security assessment or CTF challenge.""",
    instructions=create_system_prompt_renderer(
        thought_agent_system_prompt,
        cyber_micro_profile_key="thought_router",
    ),
    tools=[think],
)
