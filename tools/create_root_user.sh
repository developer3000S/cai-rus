#!/bin/bash

# Скрипт для создания пользователя с правами root и переключения на этого пользователя
# Использование: ./create_root_user.sh [имя_пользователя] [пароль]

set -e

# Значения по умолчанию
USERNAME="${1:-rootuser}"
PASSWORD="${2:-rootpass}"

echo "Создание пользователя: $USERNAME"

# Создание пользователя с домашним каталогом и оболочкой bash
if id "$USERNAME" &>/dev/null; then
    echo "Пользователь $USERNAME уже существует"
else
    sudo useradd -m -s /bin/bash "$USERNAME"
    echo "Пользователь $USERNAME создан"
fi

# Установка пароля для пользователя
echo "$USERNAME:$PASSWORD" | sudo chpasswd
echo "Пароль установлен для $USERNAME"

# Добавление пользователя в группу sudo для получения прав root
sudo usermod -aG sudo "$USERNAME"
echo "Пользователь $USERNAME добавлен в группу sudo"

# Предоставление доступа к sudo без пароля (полные права root)
echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$USERNAME > /dev/null
sudo chmod 0440 /etc/sudoers.d/$USERNAME
echo "Доступ к sudo без пароля предоставлен пользователю $USERNAME"

echo ""
echo "========================================="
echo "Пользователь $USERNAME создан с правами root"
echo "Пароль: $PASSWORD"
echo "========================================="
echo ""

# Создание скрипта запуска для нового пользователя
STARTUP_SCRIPT="/tmp/${USERNAME}_startup.sh"
cat > "$STARTUP_SCRIPT" << 'SCRIPT_EOF'
#!/bin/bash

echo "========================================="
echo "Переход в /workspace..."
echo "========================================="
cd /workspace || { echo "Не удалось перейти в /workspace"; exit 1; }

echo ""
echo "========================================="
echo "Установка CLI-инструментов из ./tools/cli.bash..."
echo "========================================="
if [ -f "./tools/cli.bash" ]; then
    bash ./tools/cli.bash
    echo ""
    echo "========================================="
    echo "Установка CLI завершена!"
    echo "========================================="
else
    echo "Предупреждение: ./tools/cli.bash не найден"
fi

echo ""
echo "========================================="
echo "Настройка завершена! Вы вошли как $(whoami)"
echo "Текущий каталог: $(pwd)"
echo "========================================="
echo ""

# Запуск интерактивной оболочки
exec bash -i
SCRIPT_EOF

chmod +x "$STARTUP_SCRIPT"

echo "Переключение на пользователя $USERNAME и запуск настройки..."
echo ""

# Переключение на нового пользователя и запуск скрипта запуска
exec sudo -i -u "$USERNAME" bash -c "bash $STARTUP_SCRIPT"
