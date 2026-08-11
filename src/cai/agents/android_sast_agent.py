"""
Данный модуль определяет агентов для статического анализа безопасности Android-приложений (SAST).

Включает:
- `app_logic_mapper_agent`: Агент для анализа логики приложения.
- `android_sast_agent`: Агент для статического анализа и обнаружения уязвимостей в Android-приложениях.
"""

from cai.sdk.agents import Agent, OpenAIChatCompletionsModel
from cai.tools.reconnaissance.generic_linux_command import generic_linux_command
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

from cai.util import load_prompt_template, create_system_prompt_renderer
from cai.tools.reconnaissance.exec_code import (
    execute_code
)


# Промпты
android_sast_system_prompt = load_prompt_template("prompts/system_android_sast.md")
app_logic_mapper_system_prompt = load_prompt_template("prompts/system_android_app_logic_mapper.md")



# Определение списка инструментов на основе доступных API-ключей
tools = [
    generic_linux_command,
    execute_code,
]


load_dotenv()
model_name = os.getenv("CAI_MODEL", "alias1")
api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder-key-for-local-models")

app_logic_mapper = Agent(
    name="AppLogicMapper",
    description="Agent specializing in application analysis to understand the logic of operation and return a complete map of it.",
    instructions=create_system_prompt_renderer(
        app_logic_mapper_system_prompt,
        cyber_micro_profile_key="android",
    ),
    tools=tools,
    model=OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=AsyncOpenAI(api_key=api_key),
    ),
)



android_sast = Agent(
    name="AndroidSAST",
    description="Agent specializing in static application security testing and vulnerability discovery for Android applications",
    instructions=create_system_prompt_renderer(
        android_sast_system_prompt,
        cyber_micro_profile_key="android",
    ),
    tools=[
        app_logic_mapper.as_tool(
            tool_name="app_mapper",
            tool_description="application analysis to understand the logic of operation and return a complete map of it."
        ),
        generic_linux_command,
        execute_code,
        ],
    model=OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=AsyncOpenAI(api_key=api_key),
    ),
)

