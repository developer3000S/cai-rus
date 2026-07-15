"""
Model command for CAI REPL.
This module provides commands for viewing and changing the current LLM model.
"""
import datetime
import os

# Standard library imports
from typing import Any, Dict, List, Optional

# Third-party imports
import requests  # pylint: disable=import-error
from rich import box
from rich.console import Console  # pylint: disable=import-error
from rich.panel import Panel  # pylint: disable=import-error
from rich.table import Table  # pylint: disable=import-error
from rich.markup import escape  # pylint: disable=import-error
from rich.text import Text  # pylint: disable=import-error

from cai.repl.commands.base import Command, register_command
from cai.repl.ui.banner import _CAI_GREEN, _quick_guide_subpanel_title
from cai.util import COST_TRACKER, get_ollama_api_base, get_ollama_auth_headers

console = Console()

_MODEL_HEADER = f"bold {_CAI_GREEN}"
_MODEL_MUTED = "#9aa0a6"


def _model_table(*, title: str = "", **kwargs: Any) -> Table:
    defaults: Dict[str, Any] = {
        "show_header": True,
        "header_style": _MODEL_HEADER,
        "title_style": _MODEL_HEADER,
        "box": box.ROUNDED,
        "border_style": _CAI_GREEN,
        "padding": (0, 1),
    }
    if title:
        defaults["title"] = title
    defaults.update(kwargs)
    return Table(**defaults)


def _model_info_panel(body: str, title: str) -> Panel:
    return Panel(
        Text.from_markup(body, overflow="fold"),
        title=_quick_guide_subpanel_title(title),
        title_align="left",
        border_style=_CAI_GREEN,
        box=box.ROUNDED,
        padding=(1, 1),
    )


def _print_model_selection_error(body: str, *, title: str = "Invalid selection") -> None:
    """Error panel for invalid ``/model`` name or index (red border, CAI title style)."""
    console.print(
        Panel(
            Text.from_markup(body, overflow="fold"),
            title=_quick_guide_subpanel_title(title),
            title_align="left",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 1),
        )
    )


def _print_model_usage_header() -> None:
    z = _CAI_GREEN
    console.print(f"\n[bold {z}]Использование:[/bold {z}]")


def _print_model_usage_catalog_lines() -> None:
    """Usage footer after ``/model show`` table (palette-aligned)."""
    z = _CAI_GREEN
    _print_model_usage_header()
    console.print(
        f"  [bold {z}]/model show[/bold {z}] [dim]— полный каталог[/dim]"
    )
    console.print(
        f"  [bold {z}]/model show supported[/bold {z}] [dim]— только модели с function calling[/dim]"
    )
    console.print(
        f"  [bold {z}]/model show <term>[/bold {z}] [dim]— фильтр по имени[/dim]"
    )
    console.print(
        f"  [bold {z}]/model show supported <term>[/bold {z}] [dim]— фильтр по поддерживаемым[/dim]"
    )
    console.print(
        f"  [bold {z}]/model <name>[/bold {z}] [dim]/[/dim] [bold {z}]/model <n>[/bold {z}] "
        f"[dim]— установить CAI_MODEL[/dim]"
    )


def _print_model_usage_short_list_lines() -> None:
    """Usage footer after bare ``/model`` short table."""
    z = _CAI_GREEN
    _print_model_usage_header()
    console.print(
        f"  [bold {z}]/model <model_name>[/bold {z}] [dim]— выбрать по имени (напр.[/dim] "
        f"[bold {z}]/model claude-3-7-sonnet-20250219[/bold {z}][dim])[/dim]"
    )
    console.print(
        f"  [bold {z}]/model <number>[/bold {z}] [dim]— выбрать по номеру строки (тот же индекс, что и[/dim] "
        f"[bold {z}]/model show[/bold {z}][dim])[/dim]"
    )
    console.print(
        f"  [bold {z}]/model show[/bold {z}] [dim]— полный каталог LiteLLM + функции[/dim]"
    )
    console.print(
        f"  [dim]Примечание: номер строки пропускает слоты только LiteLLM, не указанные выше; см.[/dim] "
        f"[bold {z}]/model show[/bold {z}] [dim]для полного порядка.[/dim]"
    )


LITELLM_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)

# Global cache: same numbering for bare ``/model`` (short table) and ``/model show``
_GLOBAL_MODEL_CACHE = []
_GLOBAL_MODEL_NUMBERS = {}


def get_predefined_model_categories() -> Dict[str, List[Dict[str, str]]]:
    """Get the predefined model categories as the single source of truth.

    This function serves as the authoritative source for all available models
    across the CAI system. Other modules should import and use this function
    to ensure consistency.

    Updated December 2025 based on LiteLLM pricing data.

    Returns:
        Dictionary mapping category names to lists of model dictionaries
    """
    return {
        "Alias": [
            {
                "name": "alias1",
                "description": (
                    "Лучшая модель для задач ИИ в кибербезопасности"
                )
            },
            {
                "name": "alias3",
                "description": (
                    "Модель CSI по умолчанию через Alias API"
                )
            },
            {
                "name": "alias2-mini",
                "description": (
                    "Компактная модель кибербезопасности Alias через Alias API; поддерживает abliteration"
                )
            }
        ],
        "Anthropic Claude": [
            {
                "name": "claude-opus-4-5-20251101",
                "description": (
                    "Самая мощная модель Claude (200K ctx, $5/$25 за MTok)"
                )
            },
            {
                "name": "claude-sonnet-4-5-20250929",
                "description": (
                    "Последний Sonnet — отличен для кодинга и агентов (200K ctx)"
                )
            },
            {
                "name": "claude-sonnet-4-20250514",
                "description": (
                    "Claude Sonnet 4 с окном контекста 1M ($3/$15 за MTok)"
                )
            },
            {
                "name": "claude-opus-4-1-20250805",
                "description": (
                    "Opus 4.1 — агентные задачи и рассуждения ($15/$75 за MTok)"
                )
            },
            {
                "name": "claude-haiku-4-5-20251001",
                "description": (
                    "Быстрый Haiku 4.5 — низкая задержка (200K ctx, $1/$5 за MTok)"
                )
            },
            {
                "name": "claude-3-7-sonnet-20250219",
                "description": (
                    "Claude 3.7 Sonnet — сложные рассуждения (200K ctx)"
                )
            },
            {
                "name": "claude-3-5-sonnet-20241022",
                "description": (
                    "Claude 3.5 Sonnet — сбалансированная производительность (200K ctx)"
                )
            },
            {
                "name": "claude-3-5-haiku-20241022",
                "description": (
                    "Claude 3.5 Haiku — быстрый и эффективный ($0.80/$4 за MTok)"
                )
            },
        ],
        "OpenAI": [
            {
                "name": "gpt-5.2",
                "description": (
                    "Последний GPT-5.2 (400K ctx, $1.75/$14 за MTok)"
                )
            },
            {
                "name": "gpt-5",
                "description": (
                    "Базовая модель GPT-5 (272K ctx, $1.25/$10 за MTok)"
                )
            },
            {
                "name": "gpt-4.1",
                "description": (
                    "GPT-4.1 с окном контекста 1M ($2/$8 за MTok)"
                )
            },
            {
                "name": "gpt-4.1-mini",
                "description": (
                    "GPT-4.1 Mini — экономичный (1M ctx, $0.40/$1.60)"
                )
            },
            {
                "name": "gpt-4o",
                "description": (
                    "GPT-4o мультимодальная (128K ctx, $2.50/$10 за MTok)"
                )
            },
            {
                "name": "gpt-4o-mini",
                "description": (
                    "GPT-4o Mini — очень дешёвая (128K ctx, $0.15/$0.60)"
                )
            },
            {
                "name": "o3",
                "description": (
                    "Модель рассуждений O3 (200K ctx, $2/$8 за MTok)"
                )
            },
            {
                "name": "o3-mini",
                "description": (
                    "Рассуждения O3 Mini (200K ctx, $1.10/$4.40 за MTok)"
                )
            },
            {
                "name": "o4-mini",
                "description": (
                    "Рассуждения O4 Mini (200K ctx, $1.10/$4.40 за MTok)"
                )
            },
            {
                "name": "o1",
                "description": (
                    "Модель рассуждений O1 (200K ctx, $15/$60 за MTok)"
                )
            },
        ],
        "Google Gemini": [
            {
                "name": "gemini/gemini-2.5-pro",
                "description": (
                    "Gemini 2.5 Pro (1M ctx, $1.25/$10 за MTok)"
                )
            },
            {
                "name": "gemini/gemini-2.5-flash",
                "description": (
                    "Gemini 2.5 Flash — быстрый (1M ctx, $0.30/$2.50 за MTok)"
                )
            },
            {
                "name": "gemini/gemini-2.5-flash-lite",
                "description": (
                    "Gemini 2.5 Flash Lite (1M ctx, $0.10/$0.40 за MTok)"
                )
            },
            {
                "name": "gemini/gemini-2.0-flash",
                "description": (
                    "Gemini 2.0 Flash (1M ctx, $0.10/$0.40 за MTok)"
                )
            },
            {
                "name": "gemini/gemini-3-pro-preview",
                "description": (
                    "Gemini 3 Pro Preview (1M ctx, $2/$12 за MTok)"
                )
            },
            {
                "name": "gemini/gemini-3-flash-preview",
                "description": (
                    "Gemini 3 Flash Preview (1M ctx, $0.50/$3 за MTok)"
                )
            },
        ],
        "DeepSeek": [
            {
                "name": "deepseek/deepseek-v3.2",
                "description": (
                    "DeepSeek V3.2 последний (164K ctx, $0.28/$0.40 за MTok)"
                )
            },
            {
                "name": "deepseek/deepseek-v3",
                "description": (
                    "DeepSeek V3 универсальная (128K ctx, $0.27/$1.10)"
                )
            },
            {
                "name": "deepseek/deepseek-r1",
                "description": (
                    "DeepSeek R1 рассуждения (128K ctx, $0.55/$2.19 за MTok)"
                )
            },
            {
                "name": "deepseek-chat",
                "description": (
                    "DeepSeek Chat API (131K ctx, $0.60/$1.70 за MTok)"
                )
            },
            {
                "name": "deepseek-reasoner",
                "description": (
                    "DeepSeek Reasoner API (131K ctx, $0.60/$1.70 за MTok)"
                )
            },
        ],
        "Ollama Cloud": [
            {
                "name": "ollama_cloud/gpt-oss:120b",
                "description": (
                    "Ollama Cloud — большая модель 120B параметров (GPU не требуется)"
                )
            },
            {
                "name": "ollama_cloud/llama3.3:70b",
                "description": (
                    "Ollama Cloud — модель Llama 3.3 70B (GPU не требуется)"
                )
            },
            {
                "name": "ollama_cloud/qwen2.5:72b",
                "description": (
                    "Ollama Cloud — модель Qwen 2.5 72B (GPU не требуется)"
                )
            },
            {
                "name": "ollama_cloud/deepseek-v3:671b",
                "description": (
                    "Ollama Cloud — модель DeepSeek V3 671B (GPU не требуется)"
                )
            }
        ]
    }


def get_all_predefined_models() -> List[Dict[str, Any]]:
    """Get all predefined models as a flat list with enriched data.

    Returns:
        List of model dictionaries with name, provider, category, description, and pricing
    """
    model_categories = get_predefined_model_categories()
    all_models = []

    # Simple mapping from category to provider name
    category_to_provider = {
        "Alias": "Alias Robotics",  # Alias models use OpenAI as base
        "Anthropic Claude": "Anthropic",
        "OpenAI": "OpenAI",
        "DeepSeek": "DeepSeek",
        "Ollama Cloud": "Ollama Cloud"
    }

    for category, models in model_categories.items():
        provider = category_to_provider.get(category, "Unknown")

        for model in models:
            # Get pricing info using COST_TRACKER
            input_cost_per_token, output_cost_per_token = COST_TRACKER.get_model_pricing(
                model["name"]
            )

            # Convert to dollars per million tokens
            input_cost_per_million = None
            output_cost_per_million = None

            if input_cost_per_token is not None and input_cost_per_token > 0:
                input_cost_per_million = input_cost_per_token * 1000000
            if output_cost_per_token is not None and output_cost_per_token > 0:
                output_cost_per_million = output_cost_per_token * 1000000

            all_models.append({
                "name": model["name"],
                "provider": provider,
                "category": category,
                "description": model["description"],
                "input_cost": input_cost_per_million,
                "output_cost": output_cost_per_million
            })

    return all_models


def get_predefined_model_names() -> List[str]:
    """Get a simple list of all predefined model names.

    This is useful for autocompletion and simple model name lists.

    Returns:
        List of model name strings
    """
    return [model["name"] for model in get_all_predefined_models()]


def load_all_available_models() -> tuple[List[str], List[Dict[str, Any]]]:
    """Load all available models (predefined + LiteLLM + Ollama) in consistent order.

    This ensures /model and /model show use the same numbering.

    Returns:
        Tuple of (all_model_names, ollama_models_data)
    """
    # Predefined models
    predefined = [model["name"] for model in get_all_predefined_models()]

    # LiteLLM models
    litellm_names = []
    try:
        response = requests.get(LITELLM_URL, timeout=5)
        if response.status_code == 200:
            # Filter out obsolete Ollama Cloud models (replaced by ollama_cloud/ prefix)
            litellm_names = [
                model_name for model_name in sorted(response.json().keys())
                if not (model_name.startswith("ollama/") and "-cloud" in model_name)
            ]
    except Exception:  # pylint: disable=broad-except
        pass

    # Ollama models
    ollama_data = []
    ollama_names = []
    try:
        api_base = get_ollama_api_base()
        ollama_base = api_base.replace('/v1', '')

        # Add authentication headers for Ollama Cloud if needed
        headers = {}
        is_cloud = "ollama.com" in api_base
        timeout = 5 if is_cloud else 1  # Cloud needs more time

        if is_cloud:
            headers = get_ollama_auth_headers()

        response = requests.get(f"{ollama_base}/api/tags", headers=headers, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            ollama_data = data.get('models', data.get('items', []))
            ollama_names = [m.get('name', '') for m in ollama_data if m.get('name')]
    except Exception:  # pylint: disable=broad-except
        pass

    all_models = predefined + litellm_names + ollama_names
    return all_models, ollama_data


def _execute_model_show(show_args: Optional[List[str]] = None) -> bool:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements,line-too-long # noqa: E501
    """Full LiteLLM catalog table and filters."""
    show_only_supported = False
    search_term = None
    args = list(show_args) if show_args else []

    if args:
        if "supported" in args:
            show_only_supported = True
            args = [arg for arg in args if arg != "supported"]

        if args:
            search_term = args[0].lower()

    global _GLOBAL_MODEL_CACHE, _GLOBAL_MODEL_NUMBERS
    all_model_names, ollama_models_data = load_all_available_models()
    _GLOBAL_MODEL_CACHE = all_model_names
    _GLOBAL_MODEL_NUMBERS = {
        str(i): model_name
        for i, model_name in enumerate(_GLOBAL_MODEL_CACHE, 1)
    }

    try:
        with console.status(f"[bold {_CAI_GREEN}]Загрузка данных моделей...[/]"):
            response = requests.get(LITELLM_URL, timeout=5)

            if response.status_code != 200:
                console.print(
                    f"[red]Ошибка загрузки данных моделей: HTTP {response.status_code}[/red]"
                )
                return True

            model_data = response.json()

        title = "Все доступные модели"
        if show_only_supported:
            title = "Поддерживаемые модели (с Function Calling)"
        if search_term:
            title += f" - Поиск: '{search_term}'"

        model_table = _model_table(title=title)
        model_table.add_column("#", style="bold white", justify="right")
        model_table.add_column("Модель", style=_CAI_GREEN)
        model_table.add_column("Провайдер", style=_MODEL_MUTED)
        model_table.add_column("Макс. токенов", style=_MODEL_MUTED, justify="right")
        model_table.add_column("Стоимость ввода ($/M)", style=_MODEL_MUTED, justify="right")
        model_table.add_column("Стоимость вывода ($/M)", style=_MODEL_MUTED, justify="right")
        model_table.add_column("Функции", style="white")

        total_models = 0
        displayed_models = 0

        predefined_models = get_all_predefined_models()
        for model in predefined_models:
            model_name = model["name"]

            if search_term and search_term not in model_name.lower():
                continue

            displayed_models += 1
            total_models += 1

            try:
                model_index = _GLOBAL_MODEL_CACHE.index(model_name) + 1
            except ValueError:
                continue

            input_cost_str = (
                f"${model['input_cost']:.2f}"
                if model["input_cost"] is not None
                else "Unknown"
            )
            output_cost_str = (
                f"${model['output_cost']:.2f}"
                if model["output_cost"] is not None
                else "Unknown"
            )

            model_table.add_row(
                str(model_index),
                model_name,
                model["provider"],
                "N/A",
                input_cost_str,
                output_cost_str,
                model.get("description", ""),
            )

        for model_name, model_info in sorted(model_data.items()):
            try:
                model_index = _GLOBAL_MODEL_CACHE.index(model_name) + 1
            except ValueError:
                continue
            total_models += 1

            supports_functions = model_info.get("supports_function_calling", False)
            if show_only_supported and not supports_functions:
                continue

            if search_term and search_term not in model_name.lower():
                continue

            displayed_models += 1

            provider = model_info.get("litellm_provider", "Неизвестно")
            if provider == "text-completion-openai":
                provider = "OpenAI"
            elif provider == "openai":
                provider = "OpenAI"
            elif "/" in model_name:
                provider = model_name.split("/")[0].capitalize()

            max_tokens = model_info.get("max_tokens", "N/A")

            input_cost = model_info.get("input_cost_per_token", 0)
            output_cost = model_info.get("output_cost_per_token", 0)

            input_cost_per_million = input_cost * 1000000 if input_cost else 0
            output_cost_per_million = output_cost * 1000000 if output_cost else 0

            if input_cost_per_million:
                input_cost_str = f"${input_cost_per_million:.4f}"
            else:
                input_cost_str = "Бесплатно"

            if output_cost_per_million:
                output_cost_str = f"${output_cost_per_million:.4f}"
            else:
                output_cost_str = "Бесплатно"

            features = []
            if model_info.get("supports_vision"):
                features.append("Видение")
            if model_info.get("supports_function_calling"):
                features.append("Function calling")
            if model_info.get("supports_parallel_function_calling"):
                features.append("Параллельные функции")
            if model_info.get("supports_audio_input") or model_info.get("supports_audio_output"):
                features.append("Аудио")
            if model_info.get("mode") == "embedding":
                features.append("Эмбеддинги")
            if model_info.get("mode") == "image_generation":
                features.append("Генерация изображений")

            features_str = ", ".join(features) if features else "Генерация текста"

            model_table.add_row(
                str(model_index),
                model_name,
                provider,
                str(max_tokens),
                input_cost_str,
                output_cost_str,
                features_str,
            )

        for model in ollama_models_data:
            model_name = model.get("name", "")

            if search_term and search_term not in model_name.lower():
                continue

            try:
                model_index = _GLOBAL_MODEL_CACHE.index(model_name) + 1
            except ValueError:
                continue

            total_models += 1
            displayed_models += 1

            model_size = model.get("size", 0)
            size_str = ""
            if model_size:
                size_mb = model_size / (1024 * 1024)
                if model_size < 1024 * 1024 * 1024:
                    size_str = f"{size_mb:.1f} MB"
                else:
                    size_gb = size_mb / 1024
                    size_str = f"{size_gb:.1f} GB"

            model_description = "Локальная модель"
            if size_str:
                model_description += f" ({size_str})"

            model_table.add_row(
                str(model_index),
                model_name,
                "Ollama",
                "Разная",
                "Бесплатно",
                "Бесплатно",
                model_description,
            )

        console.print(model_table)

        summary_text = (
            f"\n[bold {_CAI_GREEN}]Показано {displayed_models} из {total_models} моделей"
        )
        if show_only_supported:
            summary_text += " с поддержкой function calling"
        if search_term:
            summary_text += f" по запросу '{search_term}'"
        summary_text += f"[/bold {_CAI_GREEN}]"
        console.print(summary_text)

        _print_model_usage_catalog_lines()

        data_source = (
            "https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json"
        )
        console.print(f"\n[dim]Источник данных: {data_source}[/dim]")

    except Exception as e:  # pylint: disable=broad-except
        console.print(f"[red]Ошибка загрузки данных моделей: {str(e)}[/red]")

    return True


class ModelCommand(Command):
    """Command for viewing and changing the current LLM model."""

    def __init__(self):
        """Initialize the model command."""
        super().__init__(
            name="/model",
            description="Просмотр или изменение текущей модели LLM",
            aliases=["/mod"]
        )

        # Cache for model information
        self.cached_models = []
        # Map of numbers to model names
        self.cached_model_numbers = {}
        self.last_model_fetch = (
            datetime.datetime.now() - datetime.timedelta(minutes=10)
        )

    def handle(self, args: Optional[List[str]] = None) -> bool:
        """Handle ``/model`` (list, ``show``, or set model)."""
        if args and args[0] == "show":
            return _execute_model_show(args[1:])
        return self.handle_model_command(list(args) if args else [])

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def handle_model_command(self, args: List[str]) -> bool:
        """Change the model used by CAI.

        Args:
            args: List containing the model name to use or a number to select
                from the list

        Returns:
            bool: True if the model was changed successfully
        """
        # Load all models with consistent numbering and update global cache
        global _GLOBAL_MODEL_CACHE, _GLOBAL_MODEL_NUMBERS
        _GLOBAL_MODEL_CACHE, ollama_models_data = load_all_available_models()
        _GLOBAL_MODEL_NUMBERS = {
            str(i): model_name
            for i, model_name in enumerate(_GLOBAL_MODEL_CACHE, 1)
        }
        self.cached_models = _GLOBAL_MODEL_CACHE
        self.cached_model_numbers = _GLOBAL_MODEL_NUMBERS

        # Get predefined and litellm counts for display
        ALL_MODELS = get_all_predefined_models()
        predefined_model_names = [model["name"] for model in ALL_MODELS]
        litellm_model_names = [m for m in self.cached_models[len(predefined_model_names):]
                               if m not in [d.get('name') for d in ollama_models_data]]

        if not args:  # pylint: disable=too-many-nested-blocks
            # Display current model
            model_info = os.getenv("CAI_MODEL", "Неизвестно")
            console.print(
                _model_info_panel(
                    f"Текущая модель: [bold {_CAI_GREEN}]{model_info}[/bold {_CAI_GREEN}]",
                    "Активная модель",
                )
            )

            model_table = _model_table(title="Доступные модели")
            model_table.add_column("#", style="bold white", justify="right")
            model_table.add_column("Модель", style=_CAI_GREEN)
            model_table.add_column("Провайдер", style=_MODEL_MUTED)
            model_table.add_column("Категория", style=_MODEL_MUTED)
            model_table.add_column("Стоимость ввода ($/M)", style=_MODEL_MUTED, justify="right")
            model_table.add_column("Стоимость вывода ($/M)", style=_MODEL_MUTED, justify="right")
            model_table.add_column("Описание", style="white")

            # Add predefined models with numbers
            for i, model in enumerate(ALL_MODELS, 1):
                # Format pricing info as dollars per million tokens
                input_cost_str = (
                    f"${model['input_cost']:.2f}"
                    if model['input_cost'] is not None else "Неизвестно"
                )
                output_cost_str = (
                    f"${model['output_cost']:.2f}"
                    if model['output_cost'] is not None else "Неизвестно"
                )
                output_cost_str = (
                    f"${model['output_cost']:.2f}"
                    if model['output_cost'] is not None else "Неизвестно"
                )

                model_table.add_row(
                    str(i),
                    model["name"],
                    model["provider"],
                    model["category"],
                    input_cost_str,
                    output_cost_str,
                    model["description"]
                )

            # Ollama models (display from already loaded data)
            if ollama_models_data:
                start_index = len(predefined_model_names) + len(litellm_model_names) + 1
                for i, model in enumerate(ollama_models_data, start_index):
                    model_name = model.get('name', '')
                    model_size = model.get('size', 0)
                    size_str = ""
                    if model_size:
                        size_mb = model_size / (1024 * 1024)
                        if model_size < 1024 * 1024 * 1024:
                            size_str = f"{size_mb:.1f} MB"
                        else:
                            size_gb = size_mb / 1024
                            size_str = f"{size_gb:.1f} GB"

                    model_description = "Локальная модель"
                    if size_str:
                        model_description += f" ({size_str})"

                    model_table.add_row(
                        str(i),
                        model_name,
                        "Ollama",
                        "Локальная",
                        "Бесплатно",
                        "Бесплатно",
                        model_description
                    )
            else:  # pylint: disable=broad-except
                # Add a note about Ollama if we couldn't fetch models
                start_index = len(predefined_model_names) + len(litellm_model_names) + 1
                model_table.add_row(
                    str(start_index),
                    "llama3",
                    "Ollama",
                    "Локальная",
                    "Бесплатно",
                    "Бесплатно",
                    "Локальная модель Llama 3 (если установлена)")
                model_table.add_row(str(start_index + 1),
                                    "mistral",
                                    "Ollama",
                                    "Локальная",
                                    "Бесплатно",
                                    "Бесплатно",
                                    "Локальная модель Mistral (если установлена)")
                model_table.add_row(str(start_index + 2),
                                    "...",
                                    "Ollama",
                                    "Локальная",
                                    "Бесплатно",
                                    "Бесплатно",
                                    "Другие локальные модели (если установлены)")

            console.print(model_table)

            _print_model_usage_short_list_lines()
            return True

        model_arg = (args[0] or "").strip()
        if not model_arg:
            _print_model_selection_error(
                "[red]Не указано имя или номер модели.[/red]\n"
                f"Выполните [bold {_CAI_GREEN}]/model[/bold {_CAI_GREEN}] для краткого списка или "
                f"[bold {_CAI_GREEN}]/model show[/bold {_CAI_GREEN}] для полного каталога.",
                title="Неверный выбор",
            )
            return True

        known = set(self.cached_models)
        n = len(self.cached_models)

        if model_arg.isdigit():
            model_index = int(model_arg) - 1
            if 0 <= model_index < n:
                model_name = self.cached_models[model_index]
            else:
                lo, hi = (1, n) if n else (0, 0)
                _print_model_selection_error(
                    f"[red]Номер[/red] [bold]{escape(model_arg)}[/bold] [red]вне диапазона "
                    f"(используйте[/red] [bold]{lo}[/bold][red]–[/red][bold]{hi}[/bold] [red]для "
                    f"загруженного каталога).[/red]\n"
                    f"Выполните [bold {_CAI_GREEN}]/model[/bold {_CAI_GREEN}] или "
                    f"[bold {_CAI_GREEN}]/model show[/bold {_CAI_GREEN}] для нумерованного списка.",
                    title="Неверный номер",
                )
                return True
        elif model_arg in known:
            model_name = model_arg
        else:
            _print_model_selection_error(
                f"[red]Неизвестная модель[/red] [bold]{escape(model_arg)}[/bold][red].[/red]\n"
                f"[dim]Её нет среди {n} идентификаторов в текущем каталоге.[/dim]\n"
                f"Выполните [bold {_CAI_GREEN}]/model[/bold {_CAI_GREEN}] или "
                f"[bold {_CAI_GREEN}]/model show[/bold {_CAI_GREEN}], чтобы выбрать корректное имя.",
                title="Неизвестная модель",
            )
            return True

        os.environ["CAI_MODEL"] = model_name

        change_message = (
            f"Модель изменена на: [bold {_CAI_GREEN}]{model_name}[/bold {_CAI_GREEN}]\n"
            f"[{_MODEL_MUTED}]Примечание: изменение вступит в силу при следующем взаимодействии с агентом[/]"
        )
        console.print(
            _model_info_panel(change_message, "Модель изменена"),
            end="",
        )
        return True


register_command(ModelCommand())
