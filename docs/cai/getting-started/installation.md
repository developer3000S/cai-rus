# Установка

```bash
pip install cai-framework
```

## Использование CAI с Claude Code, Codex и OpenCode

Вы можете использовать CAI с различными помощниками по кодированию, сохраняя один и тот же репозиторий и окружение.

### Рекомендуемая настройка

1. Используйте одну виртуальную среду на уровне проекта.
2. Ведите один файл `.env` для конфигурации CAI.
3. Переиспользуйте одну и ту же ветку/worktree для всех помощников.
4. Проверяйте поведение CAI из терминала после правок, внесённых помощником.

### Независимый от помощника рабочий процесс

- Редактируйте и планируйте с помощью предпочитаемого помощника (Claude Code, Codex или OpenCode).
- Запускайте команды CAI из того же терминала/сессии проекта.
- Для многопроцессного выполнения используйте:
  - `/parallel add ...`
  - `/parallel run`
  - `/merge` (или `/parallel clear` для выхода без слияния)

## OS X
```bash
# Установите homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установите зависимости
brew update && \
    brew install git python@3.12

# Создайте виртуальную среду
python3.12 -m venv cai_env

# Установите пакет из локальной директории
source cai_env/bin/activate && pip install cai-framework

# Сгенерируйте файл .env и настройте по умолчанию
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nPROMPT_TOOLKIT_NO_CPR=1' > .env

# Запустите CAI
cai  # при первом запуске может занять до 30 секунд
```

## Ubuntu 24.04
```bash
sudo apt-get update && \
    sudo apt-get install -y git python3-pip python3.12-venv

# Создайте виртуальную среду
python3.12 -m venv cai_env

# Установите пакет из локальной директории
source cai_env/bin/activate && pip install cai-framework

# Сгенерируйте файл .env и настройте по умолчанию
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nPROMPT_TOOLKIT_NO_CPR=1' > .env

# Запустите CAI
cai  # при первом запуске может занять до 30 секунд
```

## Ubuntu 20.04
```bash
sudo apt-get update && \
    sudo apt-get install -y software-properties-common

# Получите Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# Создайте виртуальную среду
python3.12 -m venv cai_env

# Установите пакет из локальной директории
source cai_env/bin/activate && pip install cai-framework

# Сгенерируйте файл .env и настройте по умолчанию
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nPROMPT_TOOLKIT_NO_CPR=1' > .env

# Запустите CAI
cai  # при первом запуске может занять до 30 секунд
```

## Windows WSL
Перейдите на страницу Microsoft: `https://learn.microsoft.com/en-us/windows/wsl/install`. 
Здесь вы найдёте все инструкции по установке WSL

В Powershell напишите: ` wsl --install`

Для **перехвата пакетов** на WSL2 (`tcpdump` / `tshark`), см. [Перехват пакетов на WSL2](packet_capture_wsl.md) (`setcap`, Docker `NET_RAW`, валидный PCAP вместо текстовых заменителей).

```bash
sudo apt-get update && \
    sudo apt-get install -y git python3-pip python3-venv

# Создайте виртуальную среду
python3 -m venv cai_env

# Установите пакет из локальной директории
source cai_env/bin/activate && pip install cai-framework

# Сгенерируйте файл .env и настройте по умолчанию
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nPROMPT_TOOLKIT_NO_CPR=1' > .env

# Запустите CAI
cai  # при первом запуске может занять до 30 секунд
```

## Android

Рекомендуем иметь не менее 8 ГБ ОЗУ:

1. Сначала установите userland https://play.google.com/store/apps/details?id=tech.ula&hl=es

2. Установите Kali minimal в базовых опциях (бесплатно). [Любой другой вариант Kali, если предпочтительно]

3. Обновите ключи apt как в этом примере: https://superuser.com/questions/1644520/apt-get-update-issue-in-kali, в терминале Kali в UserLand выполните

```bash
# Получите новые ключи apt
wget http://http.kali.org/kali/pool/main/k/kali-archive-keyring/kali-archive-keyring_2024.1_all.deb

# Установите новые ключи apt
sudo dpkg -i kali-archive-keyring_2024.1_all.deb && rm kali-archive-keyring_2024.1_all.deb

# Обновите репозиторий APT
sudo apt-get update

# CAI требует python 3.12, установим его (CAI для kali на Android)
sudo apt-get update && sudo apt-get install -y git python3-pip build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev pkg-config
wget https://www.python.org/ftp/python/3.12.4/Python-3.12.4.tar.xz
tar xf Python-3.12.4.tar.xz
cd ./configure --enable-optimizations
sudo make altinstall # Эта команда выполняется долго

# Клонируйте исходный код CAI
git clone https://github.com/aliasrobotics/cai && cd cai

# Создайте виртуальную среду
python3.12 -m venv cai_env

# Установите пакет из локальной директории
source cai_env/bin/activate && pip3 install -e .

# Сгенерируйте файл .env и настройте
cp .env.example .env  # отредактируйте здесь ваши ключи/модели

# Запустите CAI
cai
``` 

### Поддержка пользовательского базового URL OpenAI

CAI поддерживает настройку пользовательского базового URL API OpenAI через переменную окружения `OPENAI_BASE_URL`. Это позволяет пользователям перенаправлять вызовы API на пользовательский endpoint, такой как прокси или самостоятельно размещённый совместимый с OpenAI сервис.

Пример конфигурации `.env`:
```
OLLAMA_API_BASE="https://custom-openai-proxy.com/v1"
```

Или напрямую из командной строки:
```bash
OLLAMA_API_BASE="https://custom-openai-proxy.com/v1" cai
```
