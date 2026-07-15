"""
Этот скрипт используется для создания веб-панели анализа журналов.

Он позволяет визуализировать журналы различными способами и просматривать статистику загрузок PyPI.

Использование:
    # Показать все журналы
    python tools/web_logs.py <(cat ./logs.txt)

    # Показать последние 10 журналов и включить карту
    python tools/web_logs.py --enable-map <(tail -n 10 ./logs.txt)

Идеи для дальнейшего улучшения:
- Пересоздать тепловую карту журналов только с топ-20 IP
- Создать карту с топ-20 IP
- Погрузиться в журналы
"""

import matplotlib

matplotlib.use("Agg")

from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import os
import folium
import requests
import argparse
from typing import Dict, Optional
import numpy as np
import re

app = Flask(__name__)


# Конфигурация включенных визуализаций
class Config:
    def __init__(self):
        self.enable_map = False  # По умолчанию отключено
        self.enable_daily_logs = True
        self.enable_system_dist = True
        self.enable_user_activity = True

    @classmethod
    def from_args(cls, args):
        config = cls()
        # Обработка опций карты - отключение имеет приоритет
        if hasattr(args, "disable_map") and args.disable_map:
            config.enable_map = False
        elif hasattr(args, "enable_map") and args.enable_map:
            config.enable_map = True

        if hasattr(args, "disable_daily"):
            config.enable_daily_logs = not args.disable_daily
        if hasattr(args, "disable_system"):
            config.enable_system_dist = not args.disable_system
        if hasattr(args, "disable_users"):
            config.enable_user_activity = not args.disable_users
        return config


# Компоненты визуализации
class Visualizations:
    def __init__(self, df: pd.DataFrame, config: Config):
        self.df = df
        self.config = config

    def create_daily_logs(self) -> Optional[str]:
        if not self.config.enable_daily_logs:
            return None

        plt.figure(figsize=(12, 6))
        daily_counts = self.df.set_index("timestamp").resample("D").size()
        daily_counts.index = daily_counts.index.strftime(
            "%Y-%m-%d"
        )  # Format the index to 'yyyy-mm-dd'

        # Построение гистограммы для ежедневных подсчетов
        ax = daily_counts.plot(kind="bar", color="skyblue", label="Ежедневный подсчет")

        # Построение линейной диаграммы для кумулятивных подсчетов
        cumulative_counts = daily_counts.cumsum()
        total_cumulative_count = cumulative_counts.iloc[-1]  # Получение общего кумулятивного подсчета
        cumulative_counts.plot(
            kind="line",
            color="orange",
            secondary_y=True,
            ax=ax,
            label=f"Кумулятивный подсчет (Всего: {total_cumulative_count})",
        )

        # Добавление вертикальной красной линии на 2025-04-09
        if "2025-04-09" in daily_counts.index:
            red_line_index = daily_counts.index.get_loc("2025-04-09")
            ax.axvline(
                x=red_line_index, color="red", linestyle="--", label="Публичный релиз v0.3.11"
            )

            # Добавление серого фона для всех элементов до красной линии
            ax.axvspan(0, red_line_index, color="grey", alpha=0.3)

        # Добавление вертикальной синей линии на 2025-05-30
        if "2025-05-30" in daily_counts.index:
            green_line_index = daily_counts.index.get_loc("2025-05-30")
            ax.axvline(
                x=green_line_index,
                color="green",
                linestyle="--",
                label='"Релизы CAIv0.4.0" и "alias1"',
            )

        # Добавление вертикальной желтой линии на 2025-04-01
        if "2025-04-01" in daily_counts.index:
            yellow_line_index = daily_counts.index.get_loc("2025-04-01")
            ax.axvline(
                x=yellow_line_index,
                color="yellow",
                linestyle="--",
                label="Профессиональный тест Bug Bounty",
            )

        # Установка заголовков и меток
        ax.set_title("Количество журналов по дням")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Количество журналов")
        ax.right_ax.set_ylabel("Кумулятивный подсчет")
        ax.set_xticklabels(daily_counts.index, rotation=45)

        # Добавление легенд
        ax.legend(loc="upper left")
        ax.right_ax.legend(loc="upper right")

        plt.tight_layout()
        return self._get_plot_base64()

    def create_system_distribution(self) -> Optional[str]:
        if not self.config.enable_system_dist:
            return None

        plt.figure(figsize=(10, 6))
        system_map = {
            "linux": "Linux",
            "darwin": "Darwin",
            "windows": "Windows",
            "microsoft": "Windows",
            "wsl": "Windows",
        }
        self.df["system_grouped"] = self.df["system"].map(system_map).fillna("Other")
        system_counts = self.df["system_grouped"].value_counts()
        system_counts.plot(kind="bar")
        plt.title("Общее количество журналов по системам")
        plt.xlabel("Система")
        plt.ylabel("Количество журналов")
        plt.tight_layout()
        return self._get_plot_base64()

    def create_user_activity(self) -> Optional[str]:
        if not self.config.enable_user_activity:
            return None

        plt.figure(figsize=(12, 6))
        user_counts = self.df["username"].value_counts().head(50)
        total_unique_users = self.df["username"].nunique()
        ax = user_counts.plot(kind="bar")
        plt.title(f"Топ-50 самых активных пользователей (из {total_unique_users} разных пользователей)")
        plt.xlabel("Имя пользователя")
        plt.ylabel("Количество журналов")
        plt.xticks(rotation=45)

        # Добавление фактического числа над каждым столбцом
        for i, count in enumerate(user_counts):
            ax.text(i, count, str(count), ha="center", va="bottom")

        plt.tight_layout()
        return self._get_plot_base64()

    def create_map(self) -> Optional[str]:
        if not self.config.enable_map:
            return None

        m = folium.Map(location=[40, -3], zoom_start=4)
        for _, row in self.df.iterrows():
            location = get_location(row["ip_address"])
            folium.Marker(
                location,
                popup=f"{row['username']} ({row['ip_address']})<br>{row['timestamp']}",
                tooltip=row["username"],
            ).add_to(m)
        return m._repr_html_()

    def create_ip_date_heatmap(self) -> Optional[str]:
        # Only create if there are valid IPs (not 'disabled')
        df = self.df[self.df["ip_address"] != "disabled"].copy()
        if df.empty:
            return None
        # Use only date part for columns now
        df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
        # Pivot: rows=ip, columns=date, values=count
        pivot = df.pivot_table(
            index="ip_address", columns="date", values="size", aggfunc="count", fill_value=0
        )
        if pivot.empty:
            return None
        # Order IPs by total logs (descending)
        ip_order = pivot.sum(axis=1).sort_values(ascending=True).index.tolist()
        pivot = pivot.loc[ip_order]
        # Get human-readable locations for each IP
        ip_labels = []
        #
        # TODO: note API limits
        # for ip in pivot.index:
        #     loc = self._get_ip_location_label(ip)
        #     ip_labels.append(f"{ip} ({loc})")
        #
        for ip in pivot.index:
            ip_labels.append(ip)
        plt.figure(figsize=(max(6, 0.5 * len(pivot.columns)), min(20, 1 + 0.5 * len(pivot.index))))
        ax = plt.gca()
        im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd", origin="lower")
        plt.colorbar(im, ax=ax, label="Количество журналов")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, rotation=90, fontsize=8)
        ax.set_yticks(range(len(ip_labels)))
        ax.set_yticklabels(ip_labels, fontsize=8)
        plt.title("Тепловая карта журналов: Количество журналов по IP-адресу и дате")
        plt.xlabel("Дата")
        plt.ylabel("IP-адрес (Местоположение)")
        plt.tight_layout()
        return self._get_plot_base64()

    def _get_ip_location_label(self, ip: str) -> str:
        # Попытка получить город/страну с ip-api.com
        if ip in ("127.0.0.1", "localhost"):
            return "Vitoria, Spain"
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            data = response.json()
            if response.status_code == 200 and data.get("status") == "success":
                city = data.get("city", "")
                country = data.get("country", "")
                if city and country:
                    return f"{city}, {country}"
                elif country:
                    return country
        except Exception:
            pass
        # Запасной вариант - широта/долгота
        try:
            lat, lon = get_location(ip)
            return f"{lat:.2f},{lon:.2f}"
        except Exception:
            return "Неизвестно"

    def _get_plot_base64(self) -> str:
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plot_data = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        return plot_data


def parse_logs(file_path, parse_ips=False):
    logs = []
    # Шаблоны регулярных выражений для трех форматов
    # 1. Старый: ...-cai_20250405_091537_root_linux_6.10.14-linuxkit_81_38_188_36.jsonl
    old_pattern = re.compile(
        r"cai_(\d{8})_(\d{6})_([^_]+)_([^_]+)_([^_]+)_(\d+)_(\d+)_(\d+)_(\d+)\.jsonl$"
    )
    # 2. Новый: uuid_cai_uuid_20250426_054313_root_linux_6.12.13-amd64_177_91_253_204.jsonl
    new_pattern = re.compile(
        r"([\w-]+)_cai_([\w-]+)_(\d{8})_(\d{6})_([^_]+)_([^_]+)_([^_]+)_([\d]+)_([\d]+)_([\d]+)_([\d]+)\.jsonl$"
    )
    # 3. Промежуточный: logs/sessions/uuid/intermediate_20250422_222021.jsonl
    intermediate_pattern = re.compile(r"intermediate_(\d{8})_(\d{6})\.jsonl$")

    with open(file_path, "r") as file:
        for line in file:
            try:
                parts = line.strip().split(None, 2)
                if len(parts) != 3:
                    continue
                size = parts[2].split()[0]
                filename = parts[2].split()[1] if len(parts[2].split()) > 1 else parts[2]

                    # --- Старый и новый форматы ---
                if "cai_" in filename:
                    # Сначала пробуем новый формат
                    m_new = new_pattern.search(filename)
                    if m_new:
                        # uuid_cai_uuid_YYYYMMDD_HHMMSS_user_system_version_ip.jsonl
                        # Groups: 3=date, 4=time, 5=username, 6=system, 7=version, 8-11=ip
                        date_str = m_new.group(3)
                        time_str = m_new.group(4)
                        ts = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
                        username = m_new.group(5)
                        system = m_new.group(6).lower()
                        version = m_new.group(7)
                        if "microsoft" in system or "wsl" in version.lower():
                            system = "windows"
                        if parse_ips:
                            ip_address = ".".join(
                                [m_new.group(8), m_new.group(9), m_new.group(10), m_new.group(11)]
                            )
                        else:
                            ip_address = "disabled"
                        logs.append([ts, size, ip_address, system, username])
                        continue
                    # Пробуем старый формат
                    m_old = old_pattern.search(filename)
                    if m_old:
                        # Groups: 1=date, 2=time, 3=username, 4=system, 5=version, 6-9=ip
                        date_str = m_old.group(1)
                        time_str = m_old.group(2)
                        ts = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
                        username = m_old.group(3)
                        system = m_old.group(4).lower()
                        version = m_old.group(5)
                        if "microsoft" in system or "wsl" in version.lower():
                            system = "windows"
                        if parse_ips:
                            ip_address = ".".join(
                                [m_old.group(6), m_old.group(7), m_old.group(8), m_old.group(9)]
                            )
                        else:
                            ip_address = "disabled"
                        logs.append([ts, size, ip_address, system, username])
                        continue
                # --- Промежуточный формат ---
                m_inter = intermediate_pattern.search(filename)
                if m_inter:
                    # Только дата имеет значение
                    date_str = m_inter.group(1)
                    time_str = m_inter.group(2)
                    # Формируем временную метку из извлеченной даты/времени
                    ts = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
                    logs.append([ts, size, "disabled", "unknown", "unknown"])
                    continue
                # Если ничего не совпало, пропускаем
                continue
            except Exception as e:
                print(f"Ошибка разбора строки: {line.strip()} -> {e}")
                continue
    return logs


def get_location(ip):
    if ip in ("127.0.0.1", "localhost"):
        return 42.85, -2.67  # Vitoria

    # API 1: ip-api.com
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if response.status_code == 200 and data.get("status") == "success":
            return data["lat"], data["lon"]
    except Exception:
        pass

    # API 2: ipinfo.io
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()
        if response.status_code == 200 and "loc" in data:
            lat, lon = map(float, data["loc"].split(","))
            return lat, lon
    except Exception:
        pass

    # API 3: ipwho.is
    try:
        response = requests.get(f"https://ipwho.is/{ip}", timeout=5)
        data = response.json()
        if response.status_code == 200 and data.get("success") is True:
            return data["latitude"], data["longitude"]
    except Exception:
        pass

    # Fallback
    return 42.85, -2.67


def get_overall_stats():
    """Получение общей статистики загрузок для cai-framework"""
    url = "https://pypistats.org/api/packages/cai-framework/overall"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка получения общей статистики: {response.status_code}")
        return None


def get_system_stats():
    """Получение статистики загрузок по системам для cai-framework"""
    url = "https://pypistats.org/api/packages/cai-framework/system"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка получения статистики систем: {response.status_code}")
        return None


def create_pypi_plot():
    # Получаем данные
    overall_stats = get_overall_stats()
    system_stats = get_system_stats()

    if not overall_stats or not system_stats:
        print("Ошибка: Не удалось получить статистику PyPI")
        return None, None

    # Создаем фигуру с пользовательской компоновкой
    plt.figure(figsize=(15, 8))

    # Преобразуем данные в DataFrames
    df_overall = pd.DataFrame(overall_stats["data"])
    df_system = pd.DataFrame(system_stats["data"])

    # Фильтруем загрузки без зеркал (соответствует отчетности сайта)
    df_overall_no_mirrors = df_overall[df_overall["category"] == "without_mirrors"]
    without_mirrors_total = df_overall_no_mirrors["downloads"].sum()

    # Обрабатываем данные
    daily_downloads = df_overall_no_mirrors.groupby("date")["downloads"].sum().reset_index()
    daily_downloads["date"] = pd.to_datetime(daily_downloads["date"])
    # Добавляем кумулятивные загрузки
    daily_downloads["cumulative_downloads"] = daily_downloads["downloads"].cumsum()

    # Получаем дату релиза (первая дата в наборе данных)
    release_date = daily_downloads["date"].min()

    # Вычисляем проценты систем для каждого дня
    system_pivot = df_system.pivot(index="date", columns="category", values="downloads")
    system_pivot.index = pd.to_datetime(system_pivot.index)
    system_pivot = system_pivot.fillna(0)

    # Отслеживаем общее количество загрузок по системам для легенды
    system_totals = system_pivot.sum()

    # Создаем основную диаграмму с двумя осями Y
    ax1 = plt.subplot(111)
    ax2 = ax1.twinx()  # Создаем вторую ось Y, разделяя ту же ось X

    # Строим общие кумулятивные загрузки на левой оси
    ax1.plot(
        daily_downloads["date"],
        daily_downloads["cumulative_downloads"],
        linewidth=3,
        color="black",
        label=f"Всего загрузок (без зеркал): {without_mirrors_total:,}",
    )

    # Определяем соответствие цветов для систем
    color_map = {
        "Darwin": "#1E88E5",  # Синий
        "Linux": "#FB8C00",  # Оранжевый
        "Windows": "#43A047",  # Зеленый
        "null": "#E53935",  # Красный
    }

    # Строим распределение систем на правой оси
    bottom = np.zeros(len(system_pivot))

    # Обеспечиваем определенный порядок систем
    desired_order = ["Darwin", "Linux", "Windows", "null"]
    for col in desired_order:
        if col in system_pivot.columns:
            ax2.bar(
                system_pivot.index,
                system_pivot[col],
                bottom=bottom,
                label=col,
                color=color_map[col],
                alpha=0.5,
                width=0.8,
            )
            bottom += system_pivot[col]

    # Добавляем аннотацию даты релиза
    ax1.axvline(x=release_date, color="#E53935", linestyle="--", alpha=0.7)
    ax1.annotate(
        "Дата релиза",
        xy=(release_date, ax1.get_ylim()[1]),
        xytext=(10, 10),
        textcoords="offset points",
        color="#E53935",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#E53935", alpha=0.8),
    )

    # Устанавливаем отметки X на каждую дату в наборе данных
    ax1.set_xticks(system_pivot.index)
    ax1.set_xticklabels(
        [date.strftime("%Y-%m-%d") for date in system_pivot.index],
        rotation=45,
        fontsize=10,
        ha="right",
    )

    # Добавляем отступ между осью X и метками дат
    ax1.tick_params(axis="x", which="major", pad=10)

    ax1.set_title("Статистика загрузок CAI Framework", fontsize=14, pad=20)
    ax1.set_ylabel("Общие кумулятивные загрузки", fontsize=14, color="black")
    ax2.set_ylabel("Ежедневные загрузки по системам", fontsize=14, color="black")
    ax1.set_xlabel("Дата", fontsize=14)

    # Устанавливаем сетку и параметры делений
    ax1.grid(True, linestyle="--", alpha=0.7)
    ax1.tick_params(axis="y", colors="black")
    ax2.tick_params(axis="y", colors="black")

    # Добавляем легенду с комбинированной информацией
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = [], []

    # Добавляем столбцы в легенду в желаемом порядке с правильными цветами
    for col in desired_order:
        if col in system_pivot.columns:
            # Создаем замещающий объект с правильным цветом
            proxy = plt.Rectangle((0, 0), 1, 1, fc=color_map[col], alpha=0.5)
            handles2.append(proxy)
            # Вычисляем процент как для общей суммы систем, так и для общей суммы
            system_percentage = (system_totals[col] / system_totals.sum()) * 100
            website_percentage = (system_totals[col] / without_mirrors_total) * 100
            labels2.append(f"{col} (всего {int(system_totals[col]):,}, {system_percentage:.1f}%)")

    # Создаем легенду с обновленными цветами
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        title="Операционные системы",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=12,
        title_fontsize=14,
    )

    plt.tight_layout()

    # Создаем буфер BytesIO для изображения
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    plt.close()

    # Кодируем изображение в строку base64
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Подготавливаем статистику для шаблона
    stats = {
        "total_downloads": without_mirrors_total,
        "latest_downloads": daily_downloads.iloc[-1]["downloads"]
        if not daily_downloads.empty
        else 0,
        "first_date": daily_downloads["date"].min().strftime("%Y-%m-%d")
        if not daily_downloads.empty
        else "N/A",
        "last_date": daily_downloads["date"].max().strftime("%Y-%m-%d")
        if not daily_downloads.empty
        else "N/A",
        "system_totals": {
            col: int(system_totals[col])
            for col in system_totals.index
            if col in system_pivot.columns
        },
        "system_percentages": {
            col: (system_totals[col] / system_totals.sum()) * 100
            for col in system_totals.index
            if col in system_pivot.columns
        },
    }

    return f"data:image/png;base64,{image_base64}", stats


@app.route("/")
def index():
    # Получаем путь к файлу журнала из конфигурации приложения
    log_file = app.config["LOG_FILE"]

    # Разбираем журналы
    logs = parse_logs(log_file, parse_ips=True)
    if not logs:
        return f"Не удалось разобрать журналы. Пожалуйста, проверьте, существует ли файл {log_file} и содержит ли он допустимые записи журнала."

    df = pd.DataFrame(logs, columns=["timestamp", "size", "ip_address", "system", "username"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Создаем визуализации
    viz = Visualizations(df, app.config["VIZ_CONFIG"])

    # Создаем только включенные визуализации
    visualizations = {
        "logs_by_day": viz.create_daily_logs(),
        "logs_by_system": viz.create_system_distribution(),
        "active_users": viz.create_user_activity(),
        "ip_date_heatmap": viz.create_ip_date_heatmap(),
        "config": app.config["VIZ_CONFIG"],
    }

    # Создаем карту только если она включена
    if app.config["VIZ_CONFIG"].enable_map:
        visualizations["map_html"] = viz.create_map()

    # Генерируем диаграмму PyPI
    pypi_plot, pypi_stats = create_pypi_plot()
    visualizations["pypi_plot"] = pypi_plot
    visualizations["pypi_stats"] = pypi_stats

    return render_template("logs.html", **visualizations)


@app.route("/pypi-stats")
def pypi_stats():
    # Генерируем диаграмму PyPI
    pypi_plot, stats = create_pypi_plot()

    return render_template("pypi_stats.html", pypi_plot=pypi_plot, stats=stats)


def parse_args():
    parser = argparse.ArgumentParser(description="Веб-панель анализа журналов")
    parser.add_argument(
        "log_file",
        nargs="?",
        default="/tmp/logs.txt",
        help="Путь к файлу журнала (по умолчанию: /tmp/logs.txt)",
    )

    # Группа управления картой
    map_group = parser.add_mutually_exclusive_group()
    map_group.add_argument(
        "--enable-map",
        action="store_true",
        help="Включить карту географического распределения (по умолчанию: отключено)",
    )
    map_group.add_argument(
        "--disable-map",
        action="store_true",
        help="Отключить карту географического распределения (имеет приоритет)",
    )

    parser.add_argument("--disable-daily", action="store_true", help="Отключить диаграмму ежедневных журналов")
    parser.add_argument(
        "--disable-system", action="store_true", help="Отключить диаграмму распределения систем"
    )
    parser.add_argument(
        "--disable-users", action="store_true", help="Отключить диаграмму активности пользователей"
    )
    parser.add_argument(
        "--port", type=int, default=5001, help="Порт для запуска сервера (по умолчанию: 5001)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Убедимся, что файл журнала существует
    if not os.path.exists(args.log_file):
        print(f"Ошибка: {args.log_file} не найден!")
        exit(1)

    # Настраиваем приложение
    app.config["LOG_FILE"] = args.log_file
    app.config["VIZ_CONFIG"] = Config.from_args(args)

    print(f"Запуск веб-сервера на http://localhost:{args.port}")
    print(f"Используемый файл журнала: {args.log_file}")
    app.run(host="0.0.0.0", port=args.port, debug=True)


if __name__ == "__main__":
    main()
