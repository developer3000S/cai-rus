# Claude Code

!!! danger "Сторонние каркасы — Предупреждение о конфиденциальности и безопасности"
    Сторонние каркасы могут обрабатывать ваши данные за пределами вашей среды.
    Для **конфиденциальности** и **оптимизации отказа от кибербезопасности** используйте **CAI** для получения лучшей производительности.

!!! warning "Отказ от поддержки"
    Alias Robotics **не предоставляет поддержку** для разработок или интеграций, связанных с Claude Code. Эта страница документирует только совместимость API. Alias просто разрешает использование API Alias через ваш предпочтительный каркас.

---

## Шаг 1: Установка Claude Code

### Предварительные требования

- **Node.js 18** или новее
- Для **macOS** используйте [nvm](https://github.com/nvm-sh/nvm) для установки Node.js — установка пакета напрямую может вызвать проблемы с разрешениями
- Для **Windows** дополнительно установите [Git for Windows](https://gitforwindows.org/)

```bash
# Установка Claude Code
npm install -g @anthropic-ai/claude-code

# Перейдите в ваш проект
cd your-awesome-project

# Запуск
claude
```

!!! note
    Если пользователи macOS встречают проблемы с разрешениями при установке, используйте `nvm` для установки Node.js.

---

## Шаг 2: Настройка API Alias

### 1. Получите ваш API ключ Alias

`ALIAS_API_KEY` (формат: `sk-...`) можно получить из одного из следующих источников:

- **[CAI PRO](https://aliasrobotics.com/cybersecurityai.php)** — полная платформа кибербезопасности с доступом к `alias1` и другим моделям.
- **[Alias LLMs](https://aliasrobotics.com/aliasLLMs.php)** — приобретите `alias2-mini` и другие языковые модели Alias напрямую.

### 2. Настройка переменных окружения

Настройте переменные окружения, используя один из следующих способов для macOS/Linux или Windows.

!!! note
    Некоторые команды не выводят результат при установке переменных окружения — это нормально, пока не появляются ошибки. Может потребоваться новое окно терминала для вступления изменений в силу.

#### macOS & Linux

Отредактируйте файл конфигурации Claude Code `~/.claude/settings.json`. Добавьте или измените поля `env` `ANTHROPIC_BASE_URL` и `ANTHROPIC_AUTH_TOKEN`.

Замените `your_alias_api_key` на API ключ, полученный на предыдущем шаге.

```json
{
    "env": {
        "ANTHROPIC_AUTH_TOKEN": "your_alias_api_key",
        "ANTHROPIC_BASE_URL": "https://api.aliasrobotics.com:666/",
        "API_TIMEOUT_MS": "3000000"
    }
}
```

#### Windows Cmd

Выполните следующие команды в Cmd. Замените `your_alias_api_key` на API ключ, полученный на предыдущем шаге.

```cmd
setx ANTHROPIC_AUTH_TOKEN your_alias_api_key
setx ANTHROPIC_BASE_URL https://api.aliasrobotics.com:666/
```

#### Windows PowerShell

Выполните следующие команды в PowerShell. Замените `your_alias_api_key` на API ключ, полученный на предыдущем шаге.

```powershell
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_AUTH_TOKEN', 'your_alias_api_key', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_BASE_URL', 'https://api.aliasrobotics.com:666/', 'User')
```

---

## Шаг 3: Начало работы с Claude Code

После завершения настройки начните использовать Claude Code в вашем терминале:

```bash
cd your-project-directory
claude
```

Использование токенов и расчеты появятся в вашем аккаунте Alias.

---

## Связанная информация

- [Быстрый старт CAI PRO](../cai_pro_quickstart.md)
- [Доступные модели](../cai_list_of_models.md)
- [Переменные окружения](../environment_variables.md)
