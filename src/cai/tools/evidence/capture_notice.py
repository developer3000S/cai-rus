"""Обнаружение неудачных захватов пакетов в реальном времени и добавление уведомления для модели."""

from __future__ import annotations

import re

_PACKET_CAPTURE_TOOL_RE = re.compile(r"\b(tcpdump|tshark|dumpcap|wireshark)\b", re.I)
_PACKET_CAPTURE_FAILURE_RE = re.compile(
    r"cap_net_raw|packet socket failed|permission to perform this capture|"
    r"couldn't run dumpcap|dumpcap.*permission denied|0 packets captured",
    re.I,
)
_PACKET_CAPTURE_NOTICE = (
    "[CAI ОШИБКА ЗАХВАТА ПАКЕТОВ]\n"
    "Захват пакетов в реальном времени не удался (часто требуются права CAP_NET_RAW / dumpcap).\n"
    "НЕ заменяйте PCAPы на curl/openssl/логи, сохраненные как .txt, в путях захвата или скриншотов.\n"
    "Немедленно сообщите оператору. Исправление: sudo setcap cap_net_raw+eip $(which dumpcap); "
    "запускайте захват внутри CAI Docker (--cap-add=NET_RAW); или анализируйте существующий .pcap.\n"
    "Фильтрация существующего PCAP с помощью tshark -r ... -Y ... -w допустима.\n"
)


def packet_capture_failure_notice(command: str, output: str) -> str | None:
    """Возвращает уведомление, когда команда захвата в реальном времени завершилась неудачно."""
    if not output or not _PACKET_CAPTURE_TOOL_RE.search(command):
        return None
    if re.search(r"\b-r\b", command, re.I) and not re.search(r"\b-i\b", command, re.I):
        return None
    if not _PACKET_CAPTURE_FAILURE_RE.search(output):
        return None
    return _PACKET_CAPTURE_NOTICE


def apply_packet_capture_notice(command: str, output: str) -> str:
    """Добавляет уведомление о сбое захвата к выводу инструмента, если применимо."""
    if not isinstance(output, str):
        return output
    notice = packet_capture_failure_notice(command, output)
    if notice:
        return f"{notice}\n{output}"
    return output
