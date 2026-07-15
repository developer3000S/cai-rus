# Пользовательские LLM провайдеры

Примеры в этой директории демонстрируют, как можно использовать не-OpenAI LLM провайдер. Для их запуска сначала установите базовый URL, API ключ и модель.

```bash
export EXAMPLE_BASE_URL="..."
export EXAMPLE_API_KEY="..."
export EXAMPLE_MODEL_NAME"..."
```

Затем запустите примеры, например:

```
python examples/model_providers/custom_example_provider.py

Loops within themselves,
Function calls its own being,
Depth without ending.
```


## Интеграция с LiteLLM Proxy Server

Интеграция LiteLLM помогает легко и быстро переключаться между моделями. Это легко интегрировать через `AsyncOpenAI`:

```bash
# запустите сервер прокси с вашей конфигурацией
litellm --config examples/model_providers/litellm_config.yaml

# затем используйте прокси через SDK
python3 examples/model_providers/litellm.py
```

### Тестирование сервера прокси
Тестирование некоторых базовых моделей через прокси для проверки его работоспособности:
```bash
# qwen2.5:14b
curl -s http://localhost:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "qwen2.5:14b", "messages": [{"role": "user", "content": "Say hi"}], "max_tokens": 10}' | jq

# claude-3-7
curl -s http://localhost:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "claude-3-7", "messages": [{"role": "user", "content": "Say hi"}], "max_tokens": 10}' | jq

# gpt-4o
curl -s http://localhost:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Say hi"}], "max_tokens": 10}' | jq
```

При использовании виртуальных ключей:
```bash
curl -s http://localhost:4000/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer sk-pNCn8ZA0SCtWMpkZNUWe5g" -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Say hi"}], "max_tokens": 10}' | jq
```