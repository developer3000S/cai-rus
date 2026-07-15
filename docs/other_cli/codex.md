# Codex CLI

!!! danger "Сторонние каркасы — Предупреждение о конфиденциальности и безопасности"
    Сторонние каркасы могут обрабатывать ваши данные за пределами вашей среды.
    Для **конфиденциальности** и **оптимизации отказа от кибербезопасности** используйте **CAI** для получения лучшей производительности.

[Codex CLI](https://github.com/openai/codex) — это открытый терминальный ИИ агент для кодирования от OpenAI. Поскольку он использует **формат API OpenAI** нативно, он может подключаться напрямую к API Alias без какого-либо прокси.

!!! warning "Отказ от поддержки"
    Alias Robotics **не предоставляет поддержку** для разработок или интеграций, связанных с Codex CLI. Эта страница документирует только совместимость API. Alias просто разрешает использование API Alias через ваш предпочтительный каркас.

---

## Настройка

### 1. Получите ваш API ключ Alias

`ALIAS_API_KEY` (формат: `sk-...`) можно получить из одного из следующих источников:

- **[CAI PRO](https://aliasrobotics.com/cybersecurityai.php)** — полная платформа кибербезопасности с доступом к `alias1` и другим моделям.
- **[Alias LLMs](https://aliasrobotics.com/aliasLLMs.php)** — приобретите `alias2-mini` и другие языковые модели Alias напрямую.

### 2. Установка Codex CLI

```bash
npm install -g @openai/codex
```

### 3. Настройка переменных окружения

```bash
export OPENAI_API_KEY="sk-your-alias-api-key-here"
export OPENAI_BASE_URL="https://api.aliasrobotics.com:666/"
```

Чтобы сохранить эти переменные, добавьте их в профиль shell (`~/.zshrc`, `~/.bashrc` и т.д.):

```bash
echo 'export OPENAI_API_KEY="sk-your-alias-api-key-here"' >> ~/.zshrc
echo 'export OPENAI_BASE_URL="https://api.aliasrobotics.com:666/"' >> ~/.zshrc
source ~/.zshrc
```

### 4. Запуск Codex с моделью Alias

```bash
codex --model alias1
```

Или настройте модель для конкретной сессии:

```bash
OPENAI_API_KEY="sk-your-alias-api-key-here" \
OPENAI_BASE_URL="https://api.aliasrobotics.com:666/" \
codex --model alias1
```

---

## Примечания

- API Alias полностью совместим с OpenAI — никакой дополнительной настройки не требуется, кроме указания базового URL и API ключа.
- Используйте `alias1` для лучшей производительности в области кибербезопасности или `alias0` для более быстрой и легкой альтернативы.
- Использование токенов и расчеты отображаются в панели вашего аккаунта Alias.

---

## Связанная информация

- [Быстрый старт CAI PRO](../cai_pro_quickstart.md)
- [Доступные модели](../cai_list_of_models.md)
- [Переменные окружения](../environment_variables.md)
