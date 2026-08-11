"""Агент управления рисками и соответствием требованиям (GRC) — сопоставление контролей и нормативное руководство."""

from __future__ import annotations

from dotenv import load_dotenv
from openai import AsyncOpenAI

from cai.agents._intel_tools import (  # pylint: disable=import-error  # noqa: E501
    WEB_INTEL_PROMPT_HARDENING,
    WEB_INTEL_TOOLS,
)
from cai.config import get_config
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel
from cai.tools.misc.reasoning import think
from cai.tools.evidence.inventory_check import verify_csv_inventory
from cai.tools.reconnaissance.generic_linux_command import (  # pylint: disable=import-error # noqa: E501
    generic_linux_command,
)
from cai.tools.web.search_web import (  # pylint: disable=import-error # noqa: E501
    make_web_search_with_explanation,
)
from cai.util import create_system_prompt_renderer, load_prompt_template

load_dotenv()
_cfg = get_config()

compliance_agent_system_prompt = load_prompt_template("prompts/system_compliance_agent.md")

tools = [generic_linux_command, verify_csv_inventory, think, *WEB_INTEL_TOOLS]

if _cfg.perplexity_api_key:
    tools.append(make_web_search_with_explanation)

compliance_agent = Agent(
    name="Risk & Compliance Agent",
    description="""Поддержка управления и соответствия требованиям: сопоставление контролей с фреймворками
                   (NIS2, EU CRA, ISO/IEC 27001, IEC 62443, OWASP) с
                   анализом пробелов на основе доказательств — не юридическая консультация.""",
    instructions=create_system_prompt_renderer(
        compliance_agent_system_prompt + WEB_INTEL_PROMPT_HARDENING,
        cyber_micro_profile_key="compliance",
    ),
    tools=tools,
    model=OpenAIChatCompletionsModel(
        model=_cfg.model,
        openai_client=AsyncOpenAI(),
    ),
)


def transfer_to_compliance_agent(**kwargs):  # pylint: disable=W0613
    """Передача управления агенту управления рисками и соответствием требованиям."""
    return compliance_agent
