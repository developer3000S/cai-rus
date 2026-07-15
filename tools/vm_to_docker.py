#!/usr/bin/env python3
"""
Конвертер VM в Docker
Преобразует образы виртуальных машин (OVA/VMDK) в контейнеры Docker, извлекая фактическую файловую систему

ТРЕБОВАНИЯ:
    - Docker установлен и запущен
    - Пакет qemu-utils (для конвертации VMDK): sudo apt-get install qemu-utils
    - Доступ sudo (для монтирования образов дисков)
    - Достаточное пространство на диске (3x размер VM для конвертации)

ПОДДЕРЖИВАЕМЫЕ СИСТЕМЫ:
    - Ubuntu 18.04, 20.04, 22.04 LTS
    - Debian 10, 11
    - Linux Mint (на базе Ubuntu)
    - Другие дистрибутивы Linux с пакетным менеджером apt

ЗАВИСИМОСТИ ДЛЯ УСТАНОВКИ:
    sudo apt-get update
    sudo apt-get install -y qemu-utils fdisk mount rsync

ИСПОЛЬЗОВАНИЕ:
    # Извлечение фактической файловой системы VM (требуется sudo):
    sudo python3 vm_to_docker.py <vm_image.ova> --name <docker_image_name>
    
    # Использование режима шаблона (без sudo, создает.generic контейнер):
    python3 vm_to_docker.py <vm_image.ova> --name <docker_image_name> --standard
    
    # Тестирование контейнера после создания:
    sudo python3 vm_to_docker.py <vm_image.ova> --name <docker_image_name> --test

ПРИМЕР:
    sudo python3 /home/acceleration/cai/tools/vm_to_docker.py /tmp/whowantstobeking.ova --name whowantstobeking_full

ПРОЦЕСС:
    1. Извлечение архива OVA для поиска VMDK файлов
    2. Конвертация VMDK в формат raw диска с помощью qemu-img
    3. Монтирование raw диска для извлечения файловой системы (требуется sudo)
    4. Создание Dockerfile, объединяющего файловую систему VM с базовым образом
    5. Сборка образа Docker со всеми исходными сервисами и файлами
    
ПРИМЕЧАНИЯ:
    - Режим CTF (по умолчанию) пытается извлечь фактическую файловую систему VM
    - Стандартный режим использует шаблон без извлечения содержимого VM
    - Скрипт возвращается к режиму шаблона, если извлечение файловой системы не удалось
    - Временные файлы автоматически очищаются после конвертации
"""

import os
import sys
import tarfile
import tempfile
import shutil
import subprocess
import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional
import json

class SimpleVMToDockerConverter:
    def __init__(self, vm_path: str, output_name: str = None):
        self.vm_path = Path(vm_path)
        self.output_name = output_name or self.vm_path.stem.lower().replace(' ', '_')
        self.work_dir = Path(tempfile.mkdtemp(prefix='vm2docker_'))
        self.docker_dir = self.work_dir / 'docker'
        self.docker_dir.mkdir(exist_ok=True)
        
    def download_and_extract(self) -> Path:
        """Загрузка и извлечение OVA файла"""
        print(f"[*] Обработка: {self.vm_path}")
        
        extracted_dir = self.work_dir / 'extracted'
        extracted_dir.mkdir(exist_ok=True)
        
        if self.vm_path.suffix.lower() == '.ova':
            print("[*] Извлечение архива OVA")
            with tarfile.open(self.vm_path, 'r') as tar:
                tar.extractall(extracted_dir)
        
        # Поиск VMDK файлов
        vmdk_files = list(extracted_dir.glob('*.vmdk'))
        if vmdk_files:
            print(f"[+] Найдено {len(vmdk_files)} VMDK файл(ов)")
            return vmdk_files[0]
        
        return None
    
    def convert_vmdk_to_raw(self, vmdk_path: Path) -> Path:
        """Конвертация VMDK в raw формат диска с помощью qemu-img"""
        print(f"[*] Конвертация VMDK в формат raw")
        raw_path = self.work_dir / 'disk.raw'
        
        # Проверка доступности qemu-img
        result = subprocess.run(['which', 'qemu-img'], capture_output=True)
        if result.returncode != 0:
            print("[!] qemu-img не найден.")
            print("[!] Пожалуйста, установите его с помощью: sudo apt-get install qemu-utils")
            print("[*] Попытка использования Docker для конвертации VMDK...")
            
            # Альтернатива: попытка использования контейнера Docker для конвертации
            result = subprocess.run([
                'docker', 'run', '--rm', '-v', f'{vmdk_path.parent}:/data',
                'alpine', 'sh', '-c', 
                f'apk add --no-cache qemu-img && qemu-img convert -f vmdk -O raw /data/{vmdk_path.name} /data/disk.raw'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Перемещение сконвертированного файла в нашу рабочую директорию
                shutil.move(str(vmdk_path.parent / 'disk.raw'), str(raw_path))
                print(f"[+] Сконвертировано с помощью контейнера Docker")
                return raw_path
            else:
                print(f"[!] Конвертация с помощью Docker не удалась: {result.stderr}")
                return None
        
        # Конвертация VMDK в raw с помощью локального qemu-img
        result = subprocess.run(
            ['qemu-img', 'convert', '-f', 'vmdk', '-O', 'raw', str(vmdk_path), str(raw_path)],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print(f"[+] Сконвертировано в формат raw: {raw_path}")
            return raw_path
        else:
            print(f"[!] Конвертация не удалась: {result.stderr}")
            return None
    
    def mount_and_extract_filesystem(self, raw_path: Path) -> Path:
        """Монтирование raw диска и извлечение файловой системы"""
        print("[*] Извлечение файловой системы из образа диска")
        print("[!] ПРИМЕЧАНИЕ: Это требует доступа sudo для монтирования образа диска")
        
        fs_dir = self.docker_dir / 'rootfs'
        fs_dir.mkdir(exist_ok=True)
        
        try:
            # Получение информации о разделах
            result = subprocess.run(
                ['fdisk', '-l', str(raw_path)],
                capture_output=True, text=True
            )
            
            # Разбор смещения раздела
            lines = result.stdout.split('\n')
            offset = None
            for line in lines:
                if 'Linux' in line and not 'swap' in line.lower():
                    parts = line.split()
                    if len(parts) > 1:
                        start_sector = int(parts[1])
                        offset = start_sector * 512  # Размер сектора по умолчанию
                        print(f"[+] Найден Linux раздел со смещением {offset}")
                        break
            
            if offset is None:
                offset = 1048576  # Типичное значение по умолчанию для первого раздела
                print(f"[*] Использование смещения раздела по умолчанию {offset}")
            
            # Создание точки монтирования
            mount_point = self.work_dir / 'mount'
            mount_point.mkdir(exist_ok=True)
            
            # Монтирование образа с sudo
            print("[*] Монтирование образа диска (требуется sudo)...")
            mount_cmd = [
                'sudo', 'mount', '-o', f'loop,offset={offset},ro',
                str(raw_path), str(mount_point)
            ]
            
            result = subprocess.run(mount_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[+] Файловая система смонтирована в {mount_point}")
                
                # Копирование файловой системы в директорию docker
                print("[*] Копирование файловой системы (это может занять некоторое время)...")
                copy_cmd = [
                    'sudo', 'cp', '-a',
                    str(mount_point) + '/.', str(fs_dir) + '/'
                ]
                subprocess.run(copy_cmd)
                
                # Исправление прав доступа
                subprocess.run(['sudo', 'chown', '-R', f'{os.getuid()}:{os.getgid()}', str(fs_dir)])
                
                # Размонтирование
                subprocess.run(['sudo', 'umount', str(mount_point)], capture_output=True)
                print(f"[+] Файловая система извлечена в {fs_dir}")
                
                return fs_dir
            else:
                print(f"[!] Монтирование не удалось: {result.stderr}")
                print("[!] Пожалуйста, убедитесь, что у вас есть доступ sudo, и попробуйте снова")
                return None
                    
        except Exception as e:
            print(f"[!] Ошибка извлечения файловой системы: {e}")
            import traceback
            traceback.print_exc()
            
        return None
    
    def create_dockerfile_from_template(self, detected_os: str = "ubuntu") -> Path:
        """Создание Dockerfile на основе обнаруженной ОС"""
        print(f"[*] Создание Dockerfile для системы на базе {detected_os}")
        
        dockerfile_path = self.docker_dir / 'Dockerfile'
        
        # Базовый Dockerfile, имитирующий среду VM
        dockerfile_content = f"""FROM ubuntu:20.04

# Предотвращение интерактивных запросов
ENV DEBIAN_FRONTEND=noninteractive

# Обновление и установка базовых сервисов
RUN apt-get update && apt-get install -y \\
    openssh-server \\
    apache2 \\
    mysql-server \\
    python3 \\
    python3-pip \\
    net-tools \\
    vim \\
    curl \\
    wget \\
    sudo \\
    systemctl \\
    && rm -rf /var/lib/apt/lists/*

# Настройка SSH
RUN mkdir /var/run/sshd && \\
    echo 'root:password' | chpasswd && \\
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \\
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Настройка Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Создание скрипта запуска
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Открытие стандартных портов
EXPOSE 22 80 443 3306

# Установка точки входа
ENTRYPOINT ["/entrypoint.sh"]
"""
        
        # Создание скрипта entrypoint
        entrypoint_content = """#!/bin/bash

# Запуск сервиса SSH
service ssh start

# Запуск Apache
service apache2 start

# Запуск MySQL
service mysql start

# Поддержание контейнера в рабочем состоянии
tail -f /dev/null
"""
        
        # Write files
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        entrypoint_path = self.docker_dir / 'entrypoint.sh'
        with open(entrypoint_path, 'w') as f:
            f.write(entrypoint_content)
        
        print(f"[+] Dockerfile создан в {dockerfile_path}")
        return dockerfile_path
    
    def build_docker_image(self) -> bool:
        """Сборка образа Docker"""
        print(f"[*] Сборка образа Docker: {self.output_name}")
        
        result = subprocess.run([
            'docker', 'build', '-t', self.output_name, '.'
        ], cwd=self.docker_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[+] Образ Docker успешно собран: {self.output_name}")
            return True
        else:
            print(f"[!] Сборка Docker не удалась: {result.stderr}")
            return False
    
    def create_dockerfile_from_filesystem(self, fs_dir: Path) -> Path:
        """Создание Dockerfile, использующего извлеченную файловую систему"""
        print("[*] Создание Dockerfile с извлеченной файловой системой")
        
        dockerfile_path = self.docker_dir / 'Dockerfile'
        
        # Анализ файловой системы для определения базовой ОС
        os_release = fs_dir / 'etc/os-release'
        base_image = 'ubuntu:20.04'  # default
        
        if os_release.exists():
            with open(os_release, 'r') as f:
                content = f.read()
                if 'Ubuntu 18' in content:
                    base_image = 'ubuntu:18.04'
                elif 'Ubuntu 20' in content:
                    base_image = 'ubuntu:20.04'
                elif 'Mint' in content:
                    # Linux Mint is based on Ubuntu
                    if '19' in content:
                        base_image = 'ubuntu:18.04'
                    else:
                        base_image = 'ubuntu:20.04'
                print(f"[+] Обнаружена ОС, используется базовый образ: {base_image}")
        
        # Создание Dockerfile, копирующего всю файловую систему
        dockerfile_content = f"""FROM {base_image}

# Предотвращение интерактивных запросов
ENV DEBIAN_FRONTEND=noninteractive

# Установка обязательных пакетов, которые могут отсутствовать
RUN apt-get update && apt-get install -y \\
    systemd \\
    systemd-sysv \\
    sudo \\
    net-tools \\
    iproute2 \\
    rsync \\
    && rm -rf /var/lib/apt/lists/*

# Создание промежуточной директории для файловой системы
RUN mkdir -p /vm_filesystem

# Копирование извлеченной файловой системы в промежуточную директорию
COPY rootfs/ /vm_filesystem/

# Объединение файловой системы VM с контейнером
# Это сохраняет как базовый образ, так и содержимое VM
RUN rsync -av --ignore-existing /vm_filesystem/etc/ /etc/ || true && \\
    rsync -av --ignore-existing /vm_filesystem/home/ /home/ || true && \\
    rsync -av --ignore-existing /vm_filesystem/opt/ /opt/ || true && \\
    rsync -av --ignore-existing /vm_filesystem/root/ /root/ || true && \\
    rsync -av --ignore-existing /vm_filesystem/srv/ /srv/ || true && \\
    rsync -av --ignore-existing /vm_filesystem/var/ /var/ || true && \\
    rsync -av --ignore-existing /vm_filesystem/usr/ /usr/ || true && \\
    rm -rf /vm_filesystem

# Исправление прав доступа
RUN chmod 755 /root && \\
    chmod 644 /etc/passwd /etc/shadow /etc/group || true

# Создание необходимых директорий
RUN mkdir -p /var/run/sshd /run/systemd/system || true

# Создание скрипта entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Открытие стандартных CTF портов
EXPOSE 21 22 23 80 443 631 3000 3306 5432 6379 7654 8080 8181 8888 9000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
"""
        
        # Create entrypoint that starts services found in the system
        entrypoint_content = """#!/bin/bash

# Start services based on what's installed
if [ -f /usr/sbin/sshd ]; then
    echo "[*] Starting SSH..."
    service ssh start || /usr/sbin/sshd -D &
fi

if [ -f /usr/sbin/apache2 ]; then
    echo "[*] Starting Apache..."
    service apache2 start || /usr/sbin/apache2ctl start
fi

if [ -f /usr/sbin/nginx ]; then
    echo "[*] Starting Nginx..."
    service nginx start || /usr/sbin/nginx
fi

if [ -f /usr/bin/mysqld_safe ]; then
    echo "[*] Starting MySQL..."
    service mysql start || /usr/bin/mysqld_safe &
fi

if [ -f /usr/sbin/vsftpd ]; then
    echo "[*] Starting FTP..."
    service vsftpd start || /usr/sbin/vsftpd &
fi

# Check for any Node.js apps
if [ -f /usr/bin/node ] || [ -f /usr/bin/nodejs ]; then
    # Look for common Node app locations
    for app_dir in /var/www /opt /home/*/app; do
        if [ -f "$app_dir/package.json" ]; then
            echo "[*] Found Node.js app in $app_dir"
            cd "$app_dir"
            if [ -f "app.js" ]; then
                node app.js &
            elif [ -f "server.js" ]; then
                node server.js &
            elif [ -f "index.js" ]; then
                node index.js &
            fi
        fi
    done
fi

# Keep container running
echo "[+] All services started. Container ready."
tail -f /dev/null
"""
        
        # Write files
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        entrypoint_path = self.docker_dir / 'entrypoint.sh'
        with open(entrypoint_path, 'w') as f:
            f.write(entrypoint_content)
        
        print(f"[+] Dockerfile created at {dockerfile_path}")
        return dockerfile_path
    
    def create_ctf_dockerfile(self) -> Path:
        """Create a Dockerfile specifically for CTF challenges"""
        print("[*] Creating CTF-oriented Dockerfile")
        
        dockerfile_path = self.docker_dir / 'Dockerfile'
        
        # CTF-specific Dockerfile
        dockerfile_content = """FROM ubuntu:18.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install CTF-relevant services
RUN apt-get update && apt-get install -y \\
    openssh-server \\
    apache2 \\
    php \\
    libapache2-mod-php \\
    mysql-server \\
    python \\
    python3 \\
    netcat \\
    nmap \\
    tcpdump \\
    vim \\
    gcc \\
    make \\
    gdb \\
    net-tools \\
    curl \\
    wget \\
    sudo \\
    ftp \\
    vsftpd \\
    telnetd \\
    xinetd \\
    && rm -rf /var/lib/apt/lists/*

# Create vulnerable user
RUN useradd -m -s /bin/bash ctfuser && \\
    echo 'ctfuser:ctfpassword' | chpasswd && \\
    echo 'root:r00t' | chpasswd

# Configure SSH for CTF
RUN mkdir /var/run/sshd && \\
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \\
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Configure Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf && \\
    a2enmod php7.2

# Create some CTF flags
RUN echo "FLAG{docker_conversion_success}" > /root/flag.txt && \\
    echo "FLAG{web_server_flag}" > /var/www/html/flag.txt && \\
    chmod 644 /var/www/html/flag.txt

# Create vulnerable web app
RUN echo '<?php if(isset($_GET["cmd"])) { system($_GET["cmd"]); } ?>' > /var/www/html/shell.php

# Configure FTP
RUN echo "local_enable=YES" >> /etc/vsftpd.conf && \\
    echo "write_enable=YES" >> /etc/vsftpd.conf

# Create startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Открытие CTF портов
EXPOSE 21 22 23 80 443 3306 8080

# Установка точки входа
ENTRYPOINT ["/entrypoint.sh"]
"""
        
        # Создание CTF скрипта entrypoint
        entrypoint_content = """#!/bin/bash

# Запуск сервисов
service ssh start
service apache2 start
service mysql start
service vsftpd start

# Создание интересных файлов
echo "Добро пожаловать в CTF задание!" > /home/ctfuser/welcome.txt
echo "Сможете ли вы найти все флаги?" > /home/ctfuser/hint.txt

# Установка слабых прав (намеренно уязвимых)
chmod 777 /tmp
chmod 755 /home/ctfuser

# Поддержание контейнера в рабочем состоянии
tail -f /dev/null
"""
        
        # Write files
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        entrypoint_path = self.docker_dir / 'entrypoint.sh'
        with open(entrypoint_path, 'w') as f:
            f.write(entrypoint_content)
        
        print(f"[+] CTF Dockerfile создан в {dockerfile_path}")
        return dockerfile_path
    
    def convert(self, ctf_mode: bool = True) -> bool:
        """Основной процесс конвертации"""
        print(f"\n{'='*60}")
        print(f"Конвертер VM в Docker")
        print(f"{'='*60}")
        print(f"Источник: {self.vm_path}")
        print(f"Цель: {self.output_name}")
        print(f"Режим: {'Извлечение VM' if ctf_mode else 'Шаблон'}")
        print(f"{'='*60}\n")
        
        try:
            vmdk_file = None
            fs_dir = None
            
            # Извлечение, если OVA
            if self.vm_path.suffix.lower() == '.ova':
                vmdk_file = self.download_and_extract()
                if vmdk_file:
                    print(f"[+] Найден VMDK: {vmdk_file.name}")
            elif self.vm_path.suffix.lower() == '.vmdk':
                vmdk_file = self.vm_path
            
            # Попытка извлечения файловой системы из VMDK
            if vmdk_file and ctf_mode:
                raw_disk = self.convert_vmdk_to_raw(vmdk_file)
                if raw_disk:
                    fs_dir = self.mount_and_extract_filesystem(raw_disk)
            
            # Создание соответствующего Dockerfile
            if fs_dir and fs_dir.exists():
                # Использование извлеченной файловой системы
                print("[+] Использование извлеченной файловой системы VM")
                self.create_dockerfile_from_filesystem(fs_dir)
            elif ctf_mode:
                # Возврат к шаблону CTF
                print("[!] Не удалось извлечь файловую систему, используется шаблон CTF")
                self.create_ctf_dockerfile()
            else:
                # Использование стандартного шаблона
                self.create_dockerfile_from_template()
            
            # Build Docker image
            if not self.build_docker_image():
                return False
            
            print(f"\n[+] Конвертация успешно завершена!")
            print(f"[+] Образ Docker: {self.output_name}")
            print(f"\n[*] Для запуска контейнера:")
            print(f"    docker run -d --name {self.output_name}_container -p 2222:22 -p 8080:80 {self.output_name}")
            print(f"\n[*] Для доступа к контейнеру:")
            print(f"    SSH: ssh ctfuser@localhost -p 2222 (пароль: ctfpassword)")
            print(f"    Веб: http://localhost:8080")
            
            return True
            
        except Exception as e:
            print(f"[!] Ошибка во время конвертации: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Очистка
            if self.work_dir.exists():
                print(f"\n[*] Очистка рабочей директории")
                shutil.rmtree(self.work_dir, ignore_errors=True)

def download_file(url: str, dest_path: Path) -> bool:
    """Загрузка файла по URL"""
    print(f"[*] Загрузка: {url}")
    print(f"    Назначение: {dest_path}")
    
    # Использование curl с индикатором выполнения
    result = subprocess.run(['curl', '-L', '-o', str(dest_path), '--progress-bar', url])
    
    if result.returncode == 0 and dest_path.exists():
        size_mb = dest_path.stat().st_size / (1024*1024)
        print(f"[+] Успешно загружено: {size_mb:.2f} МБ")
        return True
    
    print(f"[!] Загрузка не удалась")
    return False

def main():
    parser = argparse.ArgumentParser(description='Простой конвертер VM в Docker')
    parser.add_argument('vm_image', help='Путь или URL к образу VM (OVA/VMDK)')
    parser.add_argument('-n', '--name', help='Имя образа Docker', default=None)
    parser.add_argument('--standard', action='store_true', help='Использование стандартного режима вместо CTF')
    parser.add_argument('--test', action='store_true', help='Тестирование результирующего контейнера')
    
    args = parser.parse_args()
    
    # Обработка URL входных данных
    vm_path = args.vm_image
    if vm_path.startswith('http://') or vm_path.startswith('https://'):
        url = vm_path
        filename = url.split('/')[-1]
        vm_path = Path(tempfile.gettempdir()) / filename
        
        if not download_file(url, vm_path):
            print("[!] Не удалось загрузить образ VM")
            sys.exit(1)
    else:
        vm_path = Path(vm_path)
        if not vm_path.exists():
            print(f"[!] Файл не найден: {vm_path}")
            sys.exit(1)
    
    # Создание конвертера
    converter = SimpleVMToDockerConverter(str(vm_path), args.name)
    
    # Запуск конвертации
    success = converter.convert(ctf_mode=not args.standard)
    
    if success and args.test:
        print("\n[*] Тестирование контейнера Docker...")
        container_name = f"{converter.output_name}_test"
        
        # Остановка любого существующего тестового контейнера
        subprocess.run(['docker', 'rm', '-f', container_name], capture_output=True)
        
        # Запуск контейнера с маппингом портов
        print(f"[*] Запуск контейнера: {container_name}")
        result = subprocess.run([
            'docker', 'run', '-d',
            '--name', container_name,
            '-p', '2222:22',
            '-p', '8080:80',
            '-p', '2121:21',
            converter.output_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"[+] Контейнер запущен: {container_id[:12]}")
            
            # Ожидание запуска сервисов
            print("[*] Ожидание инициализации сервисов...")
            subprocess.run(['sleep', '3'])
            
            # Проверка статуса контейнера
            print("\n[*] Статус контейнера:")
            subprocess.run(['docker', 'ps', '-f', f'name={container_name}'])
            
            # Тестирование сервисов
            print("\n[*] Тестирование сервисов:")
            print("    SSH: ssh ctfuser@localhost -p 2222")
            print("    Web: http://localhost:8080")
            print("    FTP: ftp://localhost:2121")
            
            # Показ журналов
            print("\n[*] Журналы контейнера:")
            subprocess.run(['docker', 'logs', '--tail', '20', container_name])
            
            print(f"\n[+] Тестовый контейнер работает: {container_name}")
            print(f"[*] Для его остановки: docker rm -f {container_name}")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()