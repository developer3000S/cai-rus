"""Агент для создания сценариев использования (Use Case Agent)"""

import os
from dotenv import load_dotenv
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from cai.tools.reconnaissance.generic_linux_command import null_tool
from cai.util import load_prompt_template, create_system_prompt_renderer

load_dotenv()
model_name = os.getenv("CAI_MODEL", "alias1")

# Загрузка промпта
use_case_agent_system_prompt = load_prompt_template("prompts/system_use_cases.md")

# # Определение списка инструментов
# tools = [
#     generic_linux_command,
#     list_dir,
#     cat_file,
#     edit_file,
#     replace_in_file,
#     read_file,
#     append_to_file,
#     create_file,
#     pwd_command,
#     find_file,
#     execute_code,
# ]
tools = [null_tool]
# Создание агента
use_case_agent = Agent(
    name="Use Case Agent",
    description="""Agent that creates high-quality cybersecurity case studies 
                   demonstrating how CAI tackles various security scenarios, 
                   CTF challenges, and cybersecurity exercises.""",
    instructions=create_system_prompt_renderer(
        use_case_agent_system_prompt,
        cyber_micro_profile_key="usecase",
    ),
    tools=tools,
    model=OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=AsyncOpenAI(),
    ),
)


# Функция передачи управления
def transfer_to_use_case_agent(**kwargs):  # pylint: disable=W0613
    """Передача управления агенту сценариев использования.
    Принимает любые именованные аргументы, но игнорирует их."""
    return use_case_agent
