# Конфигурация Ollama

## Ollama Локально (Самостоятельный хостинг)

#### [Интеграция Ollama](https://ollama.com/)
Для локальных моделей с использованием Ollama добавьте следующее в ваш .env:

```bash
CAI_MODEL=qwen2.5:72b
OLLAMA_API_BASE=http://localhost:8000/v1 # обратите внимание, возможно, у вас другой эндпоинт
```

Убедитесь, что сервер Ollama запущен и доступен по указанному базовому URL. Вы можете заменить модель на любую другую, поддерживаемую вашим локальным экземпляром Ollama.

## Ollama Cloud

Для облачных моделей с использованием Ollama Cloud (GPU не требуется), добавьте следующее в ваш .env:

```bash
# API ключ от ollama.com
OLLAMA_API_KEY=your_api_key_here
OLLAMA_API_BASE=https://ollama.com

# Облачная модель (обратите внимание на префикс ollama_cloud/)
CAI_MODEL=ollama_cloud/gpt-oss:120b
```

**Требования:**
1. Создайте аккаунт на [ollama.com](https://ollama.com)
2. Сгенерируйте API ключ в вашем профиле
3. Используйте модели с префиксом `ollama_cloud/` (например, `ollama_cloud/gpt-oss:120b`)

**Ключевые различия:**
- Префикс: `ollama_cloud/` (облако) vs `ollama/` (локально)
- API ключ: Требуется для облака, не нужен для локального
- Эндпоинт: `https://ollama.com/v1` (облако) vs `http://localhost:8000/v1` (локально)

Смотрите [Документацию Ollama Cloud](ollama_cloud.md) для подробных инструкций по настройке.
