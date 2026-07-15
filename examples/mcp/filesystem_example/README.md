# Пример MCP Filesystem

Этот пример использует [MCP сервер файловой системы](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem), запущенный локально через `npx`.

Запуск:

```
uv run python examples/mcp/filesystem_example/main.py
```

## Детали

Пример использует класс `MCPServerStdio` из `agents.mcp` с командой:

```bash
npx -y "@modelcontextprotocol/server-filesystem" <samples_directory>
```

Ему предоставляется доступ только к директории `sample_files`, находящейся рядом с примером, которая содержит некоторые примеры данных.

Внутри:

1. Сервер запускается в дочернем процессе и предоставляет набор инструментов, таких как `list_directory()`, `read_file()` и т.д.
2. Мы добавляем экземпляр сервера в Агент через `mcp_servers=[...]`.
3. Каждый раз при запуске агента мы обращаемся к MCP серверу для получения списка инструментов через `server.list_tools()`. Результат можно кэшировать при настройке.
4. Если LLM выбирает использование MCP инструмента, среда выполнения вызывает сервер через `server.call_tool()`.
