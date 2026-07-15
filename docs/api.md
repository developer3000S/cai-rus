# Backend API CAI

Режим `cai --api` раскрывает stateful HTTP backend, построенный на FastAPI. Он использует агентов, созданных на сессию, чтобы сохранять состояние диалога, а также REST-маршруты для выполнения команд REPL или отправки запросов к модели.

## Запуск сервера

```bash
cai --api --api-host 0.0.0.0 --api-port 8080
# Если порт 8080 (или выбранный вами) занят, сервер автоматически выберет следующий свободный
# и выведет его в консоль.
```

Флаги CLI и переменные окружения:

| Флаг | Переменная | Описание |
| --- | --- | --- |
| `--api` | `CAI_API_MODE` | Включить HTTP backend. |
| `--api-host` | `CAI_API_HOST` | Привязка к хосту/интерфейсу (по умолчанию 127.0.0.1). |
| `--api-port` | `CAI_API_PORT` | Привязка к порту (по умолчанию 8000). |
| `--api-reload` | `CAI_API_RELOAD` | Автоперезапуск в режиме разработки (autoreload). |
| `--api-workers` | `CAI_API_WORKERS` | Процессы-воркеры (игнорируется при reload). |

Интерактивная документация доступна по `/api/docs`, а спецификация OpenAPI — по `/api/openapi.json`.

### Аутентификация

- API использует `ALIAS_API_KEY` клиента как секрет. Укажите `ALIAS_API_KEY` и отправьте его в заголовке `X-CAI-API-Key` (имя заголовка можно настроить через `CAI_API_KEY_HEADER`).
- Если `ALIAS_API_KEY` не задан, API остаётся незащищённым (только для локальной разработки). Для совместимости `CAI_API_KEY` принимается как fallback.

Подробный логинг аутентификации/авторизации:
- Уровень логов сервера: задайте `CAI_API_LOG_LEVEL` в `debug` (или `trace`) перед запуском `cai --api`.
- Логирование запросов (method/path/preview заголовков и тела): `CAI_API_LOG_REQUESTS=true`.
- Решения по аутентификации (почему 401): `CAI_API_LOG_AUTH=true`.
- Dev autoreload: `CAI_API_RELOAD=true`.

Пример:

```bash
ALIAS_API_KEY="your_key" \
CAI_API_LOG_LEVEL=debug \
CAI_API_LOG_REQUESTS=true \
CAI_API_LOG_AUTH=true \
CAI_API_RELOAD=true \
cai --api --api-host 0.0.0.0 --api-port 8080
```

### Типы контента

- JSON для тел запросов/ответов.
- Server-Sent Events (SSE) для стримингового endpoint (`text/event-stream`).

## Endpoints

Ниже — список endpoint’ов с примерами запросов/ответов и заголовками. Для авторизованных вызовов указывайте:

- `X-CAI-API-Key: $ALIAS_API_KEY`

Краткая сводка
- GET /api/v1/health
- GET /api/v1/commands
- POST /api/v1/commands/{command}
- POST /api/v1/sessions
- GET /api/v1/sessions
- GET /api/v1/sessions/{id}
- DELETE /api/v1/sessions/{id}
- POST /api/v1/sessions/{id}/reset
- POST /api/v1/sessions/{id}/messages
- POST /api/v1/sessions/{id}/messages/stream
- GET /api/v1/sessions/{id}/history
- POST /api/v1/sessions/{id}/interrupt
- POST /api/v1/sessions/{id}/reload
- GET /api/v1/agents
- GET /api/v1/models
- POST /api/v1/sessions/{id}/ux/final_message/stream_tokens
- POST /api/v1/ux/title
- POST /api/v1/ux/summarize

### GET /api/v1/health
- Описание: проверка “живости” (liveness). Аутентификация не требуется.
- Ответ 200:

```json
{"status":"ok","version":"<semver or dev>"}
```

### GET /api/v1/commands
- Описание: список всех команд REPL (имена, алиасы, подкоманды).
- Заголовки: `X-CAI-API-Key`
- Ответ 200:

```json
{
  "commands": [
    {"name":"/memory","description":"memory ops","aliases":[],"subcommands":["show"]},
    {"name":"/help","description":"display help","aliases":["/h"],"subcommands":[]}
  ]
}
```

### POST /api/v1/commands/{command}
- Описание: выполнить команду REPL.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`
- Тело:

```json
{"args": ["show"], "auto_correct": true}
```

- Ответ 200:

```json
{"handled": true, "suggested_command": null, "stdout": "...", "stderr": "", "exit_code": null}
```

### POST /api/v1/sessions
- Описание: создать новую stateful-сессию с собственным агентом и памятью.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`
- Тело:

```json
{"agent": "redteam_agent", "model": "alias1", "stateful": true, "metadata": {}}
```

- Ответ 201 (SessionDetailModel): содержит summary и пустую историю на старте.

### GET /api/v1/sessions
- Описание: список активных сессий (summaries).
- Заголовки: `X-CAI-API-Key`
- Ответ 200:

```json
{"sessions": [{"id":"<uuid>","agent":"redteam_agent","model":"alias1","stateful":true,"history_length":0, "created_at":"...","updated_at":"...","metadata":{}}]}
```

### GET /api/v1/sessions/{id}
- Описание: получить детали сессии (summary + полная история).
- Заголовки: `X-CAI-API-Key`

### DELETE /api/v1/sessions/{id}
- Описание: удалить сессию.
- Заголовки: `X-CAI-API-Key`
- Ответ 204 No Content

### POST /api/v1/sessions/{id}/reset
- Описание: сбросить stateful-агента сессии и очистить историю.
- Заголовки: `X-CAI-API-Key`
- Ответ 200: SessionDetailModel

### POST /api/v1/sessions/{id}/cancel
- Описание: отменить/прервать текущую выполняемую задачу в сессии (эквивалент Ctrl-C в CLI).
- Заголовки: `X-CAI-API-Key`
- Ответ 200:

```json
{"cancelled": true, "message": "Task in session <id> has been cancelled"}
```

или

```json
{"cancelled": false, "message": "No running task found in session <id>"}
```

### POST /api/v1/sessions/{id}/messages
- Описание: non-streamed inference. Запускает агента и возвращает итог.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`
- Тело (InferenceRequest):

```json
{"input": "List current risks", "context": {"org": "acme"}, "max_turns": 8}
```

- Ответ 200 (InferenceResponse):

```json
{
  "session": {"id": "<uuid>", ...},
  "result": {
    "messages": [/* semantic items: messages, tool calls, outputs, ... */],
    "history": [/* updated message list */],
    "final_output": {/* typed final output if agent uses an output schema, else string */},
    "text_output": "<assistant final text, if any>",
    "input_guardrails": [],
    "output_guardrails": []
  }
}
```

### POST /api/v1/sessions/{id}/messages/stream (SSE)
- Описание: потоковая передача “высокоуровневых шагов размышления” (без token streaming) и итоговой сводки. Внутри API выполняет non-streaming вызовы модели и отправляет шаги через server-side hooks (tools, handoffs, messages).
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`, `Accept: text/event-stream`
- Тело (InferenceRequest): аналогично non-streamed.
- Формат стрима: Server-Sent Events с двумя типами event’ов:
  - `event: reasoning_step` — один event на шаг с JSON `data` (примеры ниже).
  - `event: final` — финальный event с `{ steps, final_message, final_output }`.

Пэйлоады reasoning_step (без delta-токенов):

```json
// Сообщение, сгенерированное ассистентом
{"type":"message","agent":"Red Team","text":"...full assistant message..."}

// Вызов инструмента
{"type":"tool_call","agent":"Red Team","tool":"nmap_scan","arguments":{"target":"10.0.0.5"}}

// Результат инструмента
{"type":"tool_output","agent":"Red Team","output":"open ports: 22,80"}

// Переключение агента (handoff)
{"type":"handoff","from_agent":"Coordinator","to_agent":"Exploiter"}

// Явный сигнал переключения агента
{"type":"agent_switched","agent":"Exploiter"}
```

Финальный event payload:

```json
{
  "steps": [ /* the same reasoning steps emitted during the stream */ ],
  "final_message": "...last assistant message (if any)...",
  "final_output": {/* structured output if present, else string/null */}
}
```

Пример со `curl` (SSE):

```bash
curl -N \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  -d '{"input": "List current risks"}' \
  http://localhost:8080/api/v1/sessions/<SESSION_ID>/messages/stream
```

### POST /api/v1/sessions/{id}/messages/stream_tokens (SSE)
- Описание: стриминг на уровне токенов (и плюс reasoning steps). Endpoint позволяет включить streaming у провайдера внутри и отправляет token deltas по мере прихода. Используйте только если вам нужна точность до символов/токенов.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`, `Accept: text/event-stream`
- Тело (InferenceRequest): аналогично non-streamed.
- События стрима:
  - `event: token` с данными `{ "type": "token_delta", "text": "..." }` для каждого delta текста.
  - `event: token` с данными `{ "type": "message_start" }` и `{ "type": "message_end" }` для отметки границ.
  - `event: reasoning_step` для high-level шагов (та же схема, что и /messages/stream).
  - `event: final` с тем же summary payload, что и /messages/stream.

Примечания
- Token streaming может быть довольно “шумным”; клиент должен обрабатывать backpressure и использовать API, совместимый со стримингом.
- Для iOS предпочтительнее URLSession streaming (ниже пример); Safari’s EventSource не умеет задавать кастомные заголовки.

Пример curl (tokens):

```bash
curl -N \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  -d '{"input": "Write a haiku about ports"}' \
  http://localhost:8080/api/v1/sessions/<SESSION_ID>/messages/stream_tokens
```

iOS (Swift) пример стриминга (tokens)

```swift
let sid = "<SESSION_ID>"
var req = URLRequest(url: URL(string: "http://127.0.0.1:8080/api/v1/sessions/\(sid)/messages/stream_tokens")!)
req.httpMethod = "POST"
req.addValue("text/event-stream", forHTTPHeaderField: "Accept")
req.addValue("application/json", forHTTPHeaderField: "Content-Type")
req.addValue(ProcessInfo.processInfo.environment["ALIAS_API_KEY"] ?? "", forHTTPHeaderField: "X-CAI-API-Key")
req.httpBody = try! JSONSerialization.data(withJSONObject: ["input": "Hi"], options: [])

let task = URLSession.shared.streamTask(with: req)
task.resume()
task.readData(ofMinLength: 1, maxLength: 8192, timeout: 0) { data, atEOF, error in
    if let data = data, let s = String(data: data, encoding: .utf8) {
        // parse SSE lines: event: <name> / data: <json>
        print(s)
    }
}
```

Примечания по реализации (для любопытных разработчиков)
- Token streaming на API никогда не включает streaming токенов OpenAI chat completions. Вместо этого:
  - мы запускаем агента с non-streaming вызовами модели и отправляем события через RunHooks (start/end tools, handoffs, agent switches).
  - добавляем один message step после каждого хода ассистента (полный текст, без token deltas).
  - это гарантирует, что model streaming всегда выключен, при этом вы получаете live step updates.

## Схемы (поля request/response)

- HealthResponse
  - status: string
  - version: string

- CommandMetadata
  - name: string (например, "/memory")
  - description: string
  - aliases: string[] (например, ["/h"])
  - subcommands: string[] (например, ["show"])

- CommandsResponse
  - commands: CommandMetadata[]

- CommandRequest
  - args: string[] (опционально)
  - auto_correct: boolean (по умолчанию true)

- CommandResponse
  - handled: boolean
  - suggested_command: string | null
  - stdout: string
  - stderr: string
  - exit_code: number | null

- CancelTaskResponse
  - cancelled: boolean
  - message: string

- CreateSessionRequest
  - agent: string (опционально; по умолчанию из CAI_AGENT_TYPE)
  - model: string (опционально; по умолчанию из CAI_MODEL)
  - stateful: boolean (по умолчанию true)
  - metadata: object (опционально)

- SessionSummary
  - id: string (UUID)
  - agent: string
  - model: string
  - stateful: boolean
  - created_at: строка ISO8601
  - updated_at: строка ISO8601
  - history_length: number
  - metadata: object

- SessionDetail
  - все поля SessionSummary, плюс:
  - history: ResponseInputItem[] (список OpenAI Responses input items — user/system/assistant/tool)

- SessionsResponse
  - sessions: SessionSummary[]

- InferenceRequest
  - input: string | ResponseInputItem[]
  - context: object (опционально)
  - max_turns: number (опционально)

- RunResultPayload
  - messages: Item[] (список semantic items, созданных во время выполнения; см. ниже)
  - history: ResponseInputItem[] (оригинальный input + сгенерированные items, пригодно для продолжения)
  - final_output: any (типизированный итог, если агент задаёт output schema; иначе текст или null)
  - text_output: string | null (последнее текстовое сообщение ассистента, если есть)
  - input_guardrails: object[] (guardrail outputs для input)
  - output_guardrails: object[] (guardrail outputs для final output)

### Item: entry в messages[] (не стриминговый endpoint)
- Общая оболочка:
  - type: string (например, "message_output_item", "tool_call_item", "tool_call_output_item", "handoff_output_item")
  - agent: string | null (имя агента, который это сгенерировал)
  - payload: object (сырой Pydantic dump для underlying output/input item)
  - output: any (есть только для tool_call_output_item; структурированный return value инструмента)

- message_output_item
  - payload: ResponseOutputMessage (OpenAI Responses message с content array)
  - извлечение текста: text_output объединяет последний text chunk

- tool_call_item
  - payload: ResponseFunctionToolCall | ResponseComputerToolCall | ResponseFileSearchToolCall
  - типичные поля (function call): name, arguments

- tool_call_output_item
  - output: any (декодированный результат инструмента)

- handoff_output_item
  - payload: handoff input item
  - включает неявные имена source/target агента в envelope (agent + payload content)

### Streaming events (reasoning_step)
- Публикуются из /messages/stream; один SSE на шаг.
- step.type значения и поля:
  - message
    - agent: string | null
    - text: string (полный текст ассистента; без token deltas)
  - tool_call
    - agent: string | null
    - tool: string (имя tool/function)
    - arguments: object | string (как доступно)
  - tool_output
    - agent: string | null
    - output: any (структурированный результат инструмента)
  - handoff
    - from_agent: string | null
    - to_agent: string | null
  - agent_switched
    - agent: string | null (новый активный агент)

Финальный event (event: final)
- steps: массив отправленных reasoning_step payload’ов
- final_message: string | null
- final_output: any

## Ошибки и коды статуса
- 401 Unauthorized — отсутствует/неверный `X-CAI-API-Key` при включённой авторизации
  - {"detail":"Invalid or missing API key"}
- 404 Not Found — например, неизвестный session id
  - {"detail":"Session not found"}
- 422 Unprocessable Entity — неверное тело запроса
  - стандартная FastAPI validation error
- 500 Internal Server Error — неожиданная ошибка выполнения агента
  - {"detail":"Agent execution failed: ..."}

## Примеры для клиента (быстрые рецепты)

Python (requests; SSE через iter_lines)
```python
import json
import os
import requests

BASE = "http://127.0.0.1:8080/api/v1"
HEADERS = {"X-CAI-API-Key": os.environ.get("ALIAS_API_KEY", ""), "Content-Type": "application/json"}

# 1) Создаём сессию
sess = requests.post(f"{BASE}/sessions", headers=HEADERS, json={"agent":"redteam_agent","model":"alias1","stateful":True}).json()
sid = sess["id"]

# 2) Non-streamed
res = requests.post(f"{BASE}/sessions/{sid}/messages", headers=HEADERS, json={"input":"List current risks"}).json()
print(res["result"]["text_output"])  # итоговое сообщение

# 3) Streaming (SSE)
stream_headers = HEADERS | {"Accept": "text/event-stream"}
with requests.post(f"{BASE}/sessions/{sid}/messages/stream", headers=stream_headers, json={"input":"List current risks"}, stream=True) as r:
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith("event:"):
            evt = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data = json.loads(line.split(":", 1)[1].strip())
            if evt == "reasoning_step":
                print("step:", data)
            elif evt == "final":
                print("final:", data)
```

Node (browser/EventSource)
```js
const key = process.env.ALIAS_API_KEY;
const sid = "<SESSION_ID>"; // create via POST /sessions
const es = new EventSource(`http://localhost:8080/api/v1/sessions/${sid}/messages/stream`, {
  withCredentials: false
});
// Note: To send headers with SSE in the browser, proxy or use fetch+ReadableStream.
es.addEventListener('reasoning_step', ev => console.log('step', JSON.parse(ev.data)));
es.addEventListener('final', ev => console.log('final', JSON.parse(ev.data)));
```

Node (fetch + ReadableStream; заголовок auth)
```js
import fetch from 'node-fetch';
const key = process.env.ALIAS_API_KEY;
const sid = process.env.SID;
const resp = await fetch(`http://localhost:8080/api/v1/sessions/${sid}/messages/stream`, {
  method: 'POST',
  headers: { 'Content-Type':'application/json', 'Accept':'text/event-stream', 'X-CAI-API-Key': key },
  body: JSON.stringify({ input: 'List current risks' })
});
for await (const chunk of resp.body) {
  const s = chunk.toString();
  // parse SSE lines: event: <name> / data: <json>
  process.stdout.write(s);
}
```

Best practices
- Всегда добавляйте `Accept: text/event-stream` для стриминга.
- Ожидайте несколько `reasoning_step` событий, затем ровно один `final`.
- Token deltas в виде “промежуточных” токенов не отправляются; каждый message step содержит полный текст сообщения ассистента.
- Вызовы tool’ов могут быть частыми; учитывайте backpressure в клиенте.
- Держите таймаут соединения достаточно расслабленным для долгих задач.

## Примеры запросов (быстрое копирование/вставка)

```bash
# Healthcheck
curl -s http://localhost:8080/api/v1/health

# Список агентов
curl -s -H "X-CAI-API-Key: $ALIAS_API_KEY" http://localhost:8080/api/v1/agents | jq .

# Список моделей
curl -s -H "X-CAI-API-Key: $ALIAS_API_KEY" http://localhost:8080/api/v1/models | jq .

# Список команд
curl -s -H "X-CAI-API-Key: $ALIAS_API_KEY" http://localhost:8080/api/v1/commands

# Выполнить команду
curl -s -X POST http://localhost:8080/api/v1/commands/memory \
  -H 'Content-Type: application/json' \
  -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  -d '{"args": ["show"]}'

# Создать сессию
curl -s -X POST http://localhost:8080/api/v1/sessions \
  -H 'Content-Type: application/json' \
  -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  -d '{"agent": "redteam_agent", "model": "alias1", "stateful": true}'

# Прервать и перезагрузить
curl -s -X POST -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  http://localhost:8080/api/v1/sessions/<SESSION_ID>/interrupt
curl -s -X POST -H "Content-Type: application/json" -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  -d '{"preserve_history": true}' \
  http://localhost:8080/api/v1/sessions/<SESSION_ID>/reload

# Отправить non-streamed prompt
curl -s -X POST http://localhost:8080/api/v1/sessions/<SESSION_ID>/messages \
  -H 'Content-Type: application/json' \
  -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  -d '{"input": "List current risks"}'

# Стриминг reasoning steps (SSE)
curl -N -X POST http://localhost:8080/api/v1/sessions/<SESSION_ID>/messages/stream \
  -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' \
  -H "X-CAI-API-Key: $ALIAS_API_KEY" \
  -d '{"input": "List current risks"}'

# Сброс и удаление сессии
curl -s -X POST -H "X-CAI-API-Key: $ALIAS_API_KEY" http://localhost:8080/api/v1/sessions/<SESSION_ID>/reset
curl -s -X DELETE -H "X-CAI-API-Key: $ALIAS_API_KEY" http://localhost:8080/api/v1/sessions/<SESSION_ID>
```

## Примеры интерфейсов CLI

- `examples/cai_api_cli.py` — минимальный цикл: prompts → responses.
- `examples/cai_api_tester.py` — интерактивное меню, покрывающее все endpoints, включая стриминг.

### GET /api/v1/agents
- Описание: список доступных агентов и паттернов в рантайме (из `cai.agents`).
- Заголовки: `X-CAI-API-Key`
- Ответ 200 (AgentsResponse):

```json
{
  "agents": [
    {
      "name": "redteam_agent",
      "description": "...",
      "type": "agent",
      "pattern_type": null,
      "tools": [
        {"name": "nmap_scan", "description": "Scan a host or subnet"},
        {"name": "http_get", "description": "Fetch a URL"}
      ]
    },
    {
      "name": "swarm_pattern",
      "description": "Swarm agentic pattern",
      "type": "pattern",
      "pattern_type": "swarm",
      "tools": []
    }
  ]
}
```

### GET /api/v1/models
- Описание: список известных моделей, получаемый путём объединения каталога predefined model и `pricings/pricing.json` (если файл присутствует).
- Заголовки: `X-CAI-API-Key`
- Ответ 200 (ModelsResponse):

```json
{
  "models": [
    {
      "name": "alias1",
      "provider": "OpenAI",
      "category": "Alias",
      "description": "Best model for Cybersecurity AI tasks",
      "input_cost": 0.50,
      "output_cost": 0.50,
      "pricing": {
        "input_cost_per_token": 0.000005,
        "output_cost_per_token": 0.000005,
        "max_tokens": 128000,
        "max_input_tokens": 200000,
        "max_output_tokens": 128000,
        "supports_function_calling": true,
        "supports_vision": true,
        "supports_response_schema": true,
        "supports_tool_choice": true
      }
    }
  ]
}
```

### POST /api/v1/sessions/{id}/interrupt
- Описание: прервать выполняемую задачу в сессии (если она есть). Отменяет активную server-side run задачу.
- Заголовки: `X-CAI-API-Key`
- Ответ 200:

```json
{"interrupted": true}
```

### POST /api/v1/sessions/{id}/reload
- Описание: пересоздать агента для сессии. По желанию можно сохранить историю сообщений.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`
- Тело:

```json
{"preserve_history": true}
```

- Ответ 200: SessionDetailModel

<!-- Removed: /api/v1/sessions/{id}/ux/summarize and /api/v1/sessions/{id}/ux/title endpoints -->

### POST /api/v1/sessions/{id}/ux/final_message/stream_tokens (SSE)
- Описание: стриминг финального сообщения ассистента (token-level), которое объясняет пользователю, что только что произошло. Ваше приложение вызывает этот endpoint после завершения задачи, отправляя prompt (tone/instructions) и опционально steps, которые вы наблюдали на клиенте; если steps не переданы — backend использует server-side steps.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`, `Accept: text/event-stream`
- Тело (FinalMessageRequest):

```json
{
  "prompt": "Explain to the user what we found and next steps.",
  "steps": [ /* optional: client-collected steps; otherwise server uses session.last_steps */ ],
  "include_history": true,
  "max_turns": 8
}
```

- События стрима:
  - `event: token` с `{ "type": "message_start" }`
  - `event: token` с `{ "type": "token_delta", "text": "..." }` repeated
  - `event: token` с `{ "type": "message_end" }`
  - `event: reasoning_step` может появляться, если UX агент отправляет шаги
  - `event: final` с `{ "steps": [...], "final_message": "...", "final_output": ... }`

Примечания для iOS

### POST /api/v1/ux/title
- Описание: сгенерировать краткий заголовок через один tool call в модели `alias1` через LiteLLM. Не использует сессии.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`
- Тело:

```json
{
  "messages": [
    {"role": "user", "content": "Analiza CVE-2024-..."}
  ],
  "title_hint": "(opcional)"
}
```

- Ответ 200:

```json
{"title": "Analizando CVE-2024-..."}
```

### POST /api/v1/ux/summarize
- Описание: вернуть однострочный summary через один tool call в `alias1` через LiteLLM. Не использует сессии.
- Заголовки: `X-CAI-API-Key`, `Content-Type: application/json`
- Тело:

```json
{
  "messages": [
    {"role": "user", "content": "Escanea 10.0.0.5"}
  ],
  "steps": [
    {"type": "tool_call", "agent": "Red Team", "tool": "nmap_scan", "arguments": {"target": "10.0.0.5"}},
    {"type": "tool_output", "agent": "Red Team"}
  ],
  "max_len": 100
}
```

- Ответ 200:

```json
{"summary_text": "Tool output procesado por Red Team"}
```

Примечания по реализации
- Оба endpoints принуждают `tool_choice: required` с одной функцией `produce_title_and_summary` и всегда используют `model: alias1` с Alias `api_base` и `ALIAS_API_KEY`.
- Сервер не хранит и не читает state сессии.
- Вызывайте этот endpoint, чтобы стримить «финальное сообщение» задачи. Используйте UX-промпт, настроенный под ваш стиль («Кратко объясни в дружелюбном тоне, с указанием следующих шагов»).
- Если вы уже собрали steps на клиенте — передайте их; иначе backend использует `session.last_steps`.
- Рендерите приходящие `token_delta` куски в чат-бабл; завершайте на `message_end`/`final`.