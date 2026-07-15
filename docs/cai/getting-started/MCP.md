# MCP

CAI поддерживает Model Context Protocol (MCP) для интеграции внешних инструментов и сервисов с AI-агентами. Распространенные паттерны:

1. **STDIO (Standard Input/Output)** — Для локальных процессов, включая stdio-прокси **Burp Suite MCP** от PortSwigger (извлеките `mcp-proxy-all.jar` из MCP Server BApp; URL Burp SSE по умолчанию обычно `http://127.0.0.1:9876`):

```bash
CAI>/mcp load stdio burp java -jar /path/to/mcp-proxy-all.jar --sse-url http://127.0.0.1:9876
```

2. **SSE (Server-Sent Events)** — Прямой HTTP/SSE работает только в том случае, если сервер отправляет соответствующий ответ `Content-Type: text/event-stream`. Многие инструменты (включая встроенный SSE в Burp) работают нестабильно с клиентом CAI; для Burp рекомендуется использовать **stdio**.

```bash
CAI>/mcp load http://127.0.0.1:8000/sse myserver
```

Другие stdio-серверы:

```bash
CAI>/mcp load stdio myserver python mcp_server.py
```

После подключения добавьте инструменты MCP агенту (сначала имя сервера, затем ID или индекс агента). REPL выведет таблицу с каждым инструментом и его статусом.

```bash
CAI>/mcp add burp redteam_agent
```

Вы можете вывести список всех активных MCP-соединений и типы их транспорта:

```bash
CAI>/mcp list
```

Другие полезные подкоманды: `/mcp status`, `/mcp associations`, `/mcp test <server>` и `/mcp help` (та же сводка, что и в `/help mcp` и `/h mcp`).

[https://github.com/user-attachments/assets/386a1fd3-3469-4f84-9396-2a5236febe1f](https://github.com/user-attachments/assets/386a1fd3-3469-4f84-9396-2a5236febe1f)

## Пример: Управление Chrome с помощью CAI

1. Установите node, следуя инструкциям на [официальном сайте](https://nodejs.org/en/download/current)
2. Установите Chrome (Chromium не совместим с данным функционалом)
3. Выполните следующие команды:

```bash
CAI>/mcp load stdio devtools npx chrome-devtools-mcp@latest
CAI>/mcp add devtools redteam_agent
CAI>/agent redteam_agent
```

После этого вы получите полный контроль над Chrome с помощью red team агента.