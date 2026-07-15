# Пример MCP SSE

Этот пример использует локальный SSE сервер в [server.py](server.py).

Запуск:

```
uv run python examples/mcp/sse_example/main.py
```

## Детали

Пример использует `MCPServerSse` из `agents.mcp` (см. `main.py`; те же типы MCP серверов, что и в `cai.sdk.agents.mcp` CAI). URL SSE должен соответствовать вашему серверу (обычно `http://localhost:8000/sse`).
