# Ollama Cloud

Запуск больших языковых моделей без локального GPU с использованием облачного сервиса Ollama.

## Быстрый старт

### 1. Получение API-ключа

- Создайте аккаунт на [ollama.com](https://ollama.com)
- Сгенерируйте API-ключ в вашем профиле

### 2. Настройка `.env`

```bash
OLLAMA_API_KEY=ваш_api_ключ_здесь
OLLAMA_API_BASE=https://ollama.com
CAI_MODEL=ollama_cloud/gpt-oss:120b
```

### 3. Запуск

```bash
cai
```

## Доступные модели

Просмотрите в CAI с помощью `/model show` (предопределенный список включает модели Ollama Cloud):

- `ollama_cloud/gpt-oss:120b` — модель общего назначения 120B
- `ollama_cloud/llama3.3:70b` — Llama 3.3 70B
- `ollama_cloud/qwen2.5:72b` — Qwen 2.5 72B
- `ollama_cloud/deepseek-v3:671b` — DeepSeek V3 671B

Другие модели доступны на [ollama.com/library](https://ollama.com/library).

## Выбор модели

```bash
# По имени
CAI> /model ollama_cloud/gpt-oss:120b

# По номеру (после /model show)
CAI> /model 3
```

## Локально vs Облако

| Функция | Локально | Облако |
|---------|-------|-------|
| Префикс | `ollama/` | `ollama_cloud/` |
| API-ключ | Не требуется | Требуется |
| Эндпоинт | `http://localhost:8000/v1` | `https://ollama.com/v1` |
| GPU | Требуется | Не требуется |

## Решение проблем

**Ошибка Unauthorized**: Убедитесь, что `OLLAMA_API_KEY` установлен правильно.

**Путь не найден**: Убедитесь, что `OLLAMA_API_BASE=https://ollama.com` (без `/v1`).

**Модель не в списке**: Проверьте, что префикс модели `ollama_cloud/`, а не `ollama/`.

## Валидация

Проверьте соединение с помощью curl:

```bash
curl https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-oss:120b", "messages": [{"role": "user", "content": "test"}]}'
```

## Ссылки

- [Документация Ollama Cloud](https://ollama.com/docs/cloud)
- [Библиотека моделей](https://ollama.com/library)
- [Получить API-ключ](https://ollama.com/settings/keys)
