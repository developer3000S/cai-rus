# Скрипт для настройки различных CLI-ассистентов

# Использование nvm (рекомендуется)
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# Перезапустите терминал или выполните source nvm
source ~/.nvm/nvm.sh
# Установите последнюю LTS-версию Node.js
nvm install --lts

## Claude Code CLI
# Установка claude code
npm install -g @anthropic-ai/claude-code

## Codex CLI
npm install -g @openai/codex
# затем, 
#   codex login
#   codex -s workspace-write -a on-request -m gpt-5 -c model_reasoning_effort="high" --search