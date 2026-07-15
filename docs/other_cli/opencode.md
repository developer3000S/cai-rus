# OpenCode

!!! danger "Сторонние каркасы — Предупреждение о конфиденциальности и безопасности"
    Сторонние каркасы могут обрабатывать ваши данные за пределами вашей среды.
    Для **конфиденциальности** и **оптимизации отказа от кибербезопасности** используйте **CAI** для получения лучшей производительности.

[OpenCode](https://opencode.ai) — это открытый терминальный ИИ помощник для кодирования. Он поддерживает провайдеров, совместимых с OpenAI, что означает, что API Alias может быть подключен напрямую без какого-либо прокси.

!!! warning "Отказ от поддержки"
    Alias Robotics **не предоставляет поддержку** для разработок или интеграций, связанных с OpenCode. Эта страница документирует только совместимость API. Alias просто разрешает использование API Alias через ваш предпочтительный каркас.

---

## Настройка

### 1. Получите ваш API ключ Alias

`ALIAS_API_KEY` (формат: `sk-...`) можно получить из одного из следующих источников:

- **[CAI PRO](https://aliasrobotics.com/cybersecurityai.php)** — полная платформа кибербезопасности с доступом к `alias1` и другим моделям.
- **[Alias LLMs](https://aliasrobotics.com/aliasLLMs.php)** — приобретите `alias2-mini` и другие языковые модели Alias напрямую.

### 2. Установка OpenCode

```bash
npm install -g opencode-ai
```

Или через Homebrew (macOS):

```bash
brew install sst/tap/opencode
```

### 3. Настройка провайдера Alias

OpenCode использует файл `~/.config/opencode/config.json`. Добавьте пользовательский провайдер, совместимый с OpenAI, указывающий на API Alias:

```json
{
  "provider": {
    "alias": {
      "api": "https://api.aliasrobotics.com:666/",
      "name": "Alias Robotics",
      "env": ["ALIAS_API_KEY"]
    }
  },
  "model": "alias/alias1"
}
```

Затем экспортируйте ваш ключ:

```bash
export ALIAS_API_KEY="sk-your-alias-api-key-here"
```

### 4. Запуск OpenCode

```bash
opencode
```

OpenCode определит настроенный провайдер и направит запросы в API Alias.

---

## Альтернатива: подход через переменные окружения

Если вы предпочитаете не редактировать файл конфигурации, OpenCode также поддерживает стандартные переменные окружения OpenAI:

```bash
export OPENAI_API_KEY="sk-your-alias-api-key-here"
export OPENAI_BASE_URL="https://api.aliasrobotics.com:666/"
opencode --model alias1
```

---

## Примечания

- Используйте `alias1` для лучшей производительности в области кибербезопасности или `alias0` для более быстрой и легкой альтернативы.
- Использование токенов и расчеты отображаются в панели вашего аккаунта Alias.

---

## Связанная информация

- [Быстрый старт CAI PRO](../cai_pro_quickstart.md)
- [Доступные модели](../cai_list_of_models.md)
- [Переменные окружения](../environment_variables.md)
