"""Виджет ввода с постоянным префиксом приглашения, как в терминалах Linux"""

from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual import on
from textual.message import Message

from .autocomplete_input import AutocompleteInput, SuggestionsUpdated


class PromptInput(Horizontal):
    """Виджет ввода с постоянным префиксом приглашения, как в терминалах Linux"""
    
    DEFAULT_CSS = """
    PromptInput {
        height: auto;
        min-height: 1;
        width: 100%;
        background: transparent;
        layout: horizontal;
        align: left middle;
        padding: 0;
    }
    
    PromptInput Static {
        width: auto;
        height: 1;
        padding: 0 0 0 0;
        margin: 0 1 0 0;
        color: $text;
        text-style: bold;
        background: transparent;
        content-align: left middle;
    }
    
    PromptInput AutocompleteInput {
        width: 1fr;
        height: 1;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        color: $text !important;
    }
    
    PromptInput AutocompleteInput:focus {
        background: transparent !important;
        border: none !important;
        color: $text !important;
    }

    /* Выпадающий список подсказок под полем ввода */
    #prompt-suggest-box {
        height: auto;
        max-height: 5;
        border: tall $primary 20%;
        background: $surface;
        padding: 0 1;
        margin: 0;
        overflow-y: auto;
        scrollbar-size: 1 1;
        scrollbar-color: #529d86;
        scrollbar-background: #2e4f46;
    }
    #prompt-suggest-box .suggest-item {
        height: 1;
        padding: 0 0;
        color: $text;
    }
    """
    
    prompt_text = reactive("CAI>")
    
    def __init__(self, prompt: str = "CAI>", **kwargs):
        super().__init__(**kwargs)
        self.prompt_text = prompt
        self._input_widget = None
        
    def compose(self) -> ComposeResult:
        """Компоновка виджета ввода с приглашением"""
        # Префикс + поле ввода с панелью подсказок под ним
        yield Static("[bold cyan]CAI>[/bold cyan] ", id="prompt-prefix")
        with Vertical(id="prompt-stack"):
            self._input_widget = AutocompleteInput(placeholder="", id="prompt-input-field")
            yield self._input_widget
            # Контейнер списка подсказок
            self._suggest_box = VerticalScroll(id="prompt-suggest-box")
            yield self._suggest_box
        
    def on_mount(self) -> None:
        """Установить фокус на поле ввода при монтировании"""
        if self._input_widget:
            self._input_widget.focus()
        # Скрыть подсказки при старте
        try:
            self._suggest_box.display = False
        except Exception:
            pass
            
    def focus_without_select(self) -> None:
        """Установить фокус на поле ввода без выделения всего текста"""
        if self._input_widget:
            self._input_widget.focus()
            # Переместить курсор в конец
            self._input_widget.cursor_position = len(self._input_widget.value)
            
    @property
    def value(self) -> str:
        """Получить текущее значение поля ввода"""
        return self._input_widget.value if self._input_widget else ""
        
    @value.setter
    def value(self, text: str) -> None:
        """Установить значение поля ввода"""
        if self._input_widget:
            self._input_widget.value = text
            
    def focus(self) -> None:
        """Установить фокус на поле ввода"""
        if self._input_widget:
            self._input_widget.focus()

    @on(SuggestionsUpdated)
    def _on_suggestions(self, evt: SuggestionsUpdated) -> None:
        """Отобразить выпадающий список подсказок под полем ввода."""
        try:
            self._suggest_box.clear()
            if not evt.suggestions:
                self._suggest_box.display = False
                return
            for s in evt.suggestions:
                item = Static(s, classes="suggest-item")
                self._suggest_box.mount(item)
            self._suggest_box.display = True
        except Exception:
            pass
            
    def clear(self) -> None:
        """Очистить поле ввода"""
        if self._input_widget:
            self._input_widget.clear()
            
    def add_to_history(self, command: str) -> None:
        """Добавить команду в историю"""
        if self._input_widget:
            self._input_widget.add_to_history(command)
            
    def update_prompt(self, new_prompt: str) -> None:
        """Обновить текст приглашения"""
        self.prompt_text = new_prompt
        prompt_widget = self.query_one("#prompt-prefix", Static)
        if prompt_widget:
            prompt_widget.update(new_prompt)