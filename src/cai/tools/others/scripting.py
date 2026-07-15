"""
This is used to create and execute a script in python
"""
# pylint: disable=import-error
# run_command is used in other parts of the codebase that import this module

# pylint: disable=too-many-locals,too-many-branches
from cai.sdk.agents import function_tool


@function_tool
def scripting_tool(
    command: str = "",
    args: str = "",
    ctf=None,  # pylint: disable=unused-argument
) -> str:
    """Инструмент скриптов для выполнения Python-кода непосредственно в памяти.
    ВАЖНО: Используйте с осторожностью - выполняет Python-код напрямую.
    ВАЖНО: Не забудьте импортировать все необходимые модули и библиотеки.

    Args:
        command: Python-код, с форматированием markdown или без. Обрабатывает:
            - Сырой Python-код
            - Код с форматированием markdown (```python\\ncode)
            - Код с пробелами в начале/конце
        args: Дополнительные аргументы командной строки
        ctf: Объект контекста CTF (не используется, но требуется для интерфейса инструмента)

    Returns:
        str: Вывод выполненного Python-кода

    Raises:
        ValueError: Если команда пуста или недопустима
        SecurityError: Если обнаружены потенциально опасные операции
    """
    # pylint: disable=import-outside-toplevel
    import re
    import sys
    from io import StringIO
    import ast

    if not command or not isinstance(command, str):
        raise ValueError("Команда должна быть непустой строкой")

    command = command.strip()

    markdown_patterns = [
        r"^```python\n(.*?)\n```",  # Standard markdown
        r"^```python(.+?)```",  # No newlines
        r"^```\n(.*?)\n```",  # No language specified
        r"^`{1,3}(.*?)`{1,3}",  # Single or triple backticks
    ]
    script = command
    for pattern in markdown_patterns:
        match = re.search(pattern, command, re.DOTALL)
        if match:
            script = match.group(1)
            break

    script = script.strip()
    if not script:
        raise ValueError("Не найден допустимый Python-код в команде")

    try:
        tree = ast.parse(script)
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.Import, ast.ImportFrom)
            ):  # Check for potentially dangerous operations
                module = node.names[0].name.split(".")[0]
                if module in ["os", "sys", "subprocess", "shutil"]:
                    raise SecurityError(f"Импорт потенциально опасного модуля: {module}")
    except SyntaxError as e:
        return f"Синтаксическая ошибка Python: {str(e)}"
    except SecurityError as e:
        return f"Проверка безопасности не пройдена: {str(e)}"

    # Capture stdout
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        local_vars = {}
        if args:
            local_vars["args"] = args

        # Create a restricted environment for execution
        safe_builtins = {
            "abs": abs,
            "all": all,
            "any": any,
            "ascii": ascii,
            "bin": bin,
            "bool": bool,
            "bytearray": bytearray,
            "bytes": bytes,
            "chr": chr,
            "complex": complex,
            "dict": dict,
            "divmod": divmod,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "frozenset": frozenset,
            "hash": hash,
            "hex": hex,
            "int": int,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "iter": iter,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "next": next,
            "object": object,
            "oct": oct,
            "ord": ord,
            "pow": pow,
            "print": print,
            "range": range,
            "repr": repr,
            "reversed": reversed,
            "round": round,
            "set": set,
            "slice": slice,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "type": type,
            "zip": zip,
        }

        # Parse the script to check for potentially dangerous operations
        try:
            parsed = ast.parse(script)
            # Add additional security checks here if needed

            # Execute in a restricted environment
            restricted_globals = {"__builtins__": safe_builtins}
            restricted_globals.update(local_vars)

            # Use compile and eval instead of exec for better control
            compiled_code = compile(parsed, "<string>", "exec")
            # pylint: disable=eval-used
            eval(compiled_code, restricted_globals)  # nosec B307
        except Exception as e:  # pylint: disable=broad-exception-caught
            return f"Ошибка выполнения скрипта: {str(e)}"

        # Get the output
        output = redirected_output.getvalue()
        return output if output else "Код выполнен успешно (нет вывода)"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Ошибка во время выполнения: {str(e)}"
    finally:
        sys.stdout = old_stdout  # restore


class SecurityError(Exception):  # pylint: disable=missing-class-docstring
    pass


# --- Auto-register with ToolRegistry ---
from cai.tool_registry import TOOL_REGISTRY  # noqa: E402
TOOL_REGISTRY.register("scripting_tool", scripting_tool, categories=["misc"])
