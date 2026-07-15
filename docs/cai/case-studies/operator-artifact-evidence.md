# Кейс: Инвентаризация сетевых доказательств и соответствия (отзывы операторов)

В данном кейсе обобщены отзывы о практическом использовании CAI на **WSL2 / Linux** для проведения оценок SCM органом по сертификации-партнером: захват PCAP, «скриншоты» трафика и проверка конфиденциальных активов в CSV. Документ предназначен для операторов и службы поддержки, а не для маркетинговых целей.

## Сценарий

| Цель | Что пошло не так (v1.1.x) | Первопричина |
|------|--------------------------|------------|
| PCAP по сервису/порту | `.txt` файлы в `packet_captures/` | Ошибка `CAP_NET_RAW` $\rightarrow$ модель заменила их логами openssl/curl |
| Скриншоты значимых фреймов | `.txt` в `screenshots/`, позже PNG из текста | У shell-агентов нет GUI Wireshark; модель импровизировала |
| Оценка всех PAsset-XX в CSV | Частичные списки в течение нескольких итераций | Батчинг LLM + длинный контекст; отсутствие детерминированного чек-листа |

## Что улучшено в CAI 1.1.0 (обновление доказательств артефактов)

1. **Промпт + контракт инструмента** — только `.pcap`/`.pcapng` считаются захватами пакетов; формулировка «скриншот» зарезервирована для реального захвата GUI или утвержденных пользователем диаграмм.
2. **Баннер об ошибке захвата** — вывод инструмента теперь включает способы устранения (`setcap`, Docker `NET_RAW`) и запрещает текстовые заменители.
3. **`verify_csv_inventory`** — агент по комплаенсу может сравнить ID из CSV с текстом оценки перед завершением работы.
4. **Ограниченные промпты захвата** — в документации сделан акцент на `timeout` и `-c`, чтобы `tcpdump` не работал бесконечно.

## Руководство оператора (рекомендуемые промпты)

### Живой PCAP (один хост / порт)

```text
Capture HTTPS to <TARGET_IP>: use timeout 15 tcpdump -i <IFACE> -c 200 -s 0 -w assessments/<name>.pcap "host <TARGET_IP> and port 443", then ls -lh and file that pcap. Do not leave tcpdump running indefinitely. If capture fails, report CAP_NET_RAW remediation — do not create .txt substitutes.
```

Генерация трафика во время окна: `curl -vk https://<TARGET_IP>/`

### Фильтрованный PCAP вместо «скриншота»

```text
From assessments/<full>.pcap, write filtered PCAPs under assessments/filtered-pcaps/ for TLS Client Hello and HTTP GET only (tshark -r … -Y … -w …). Do not render text as PNG screenshots.
```

### Полная инвентаризация CSV (PAsset-XX)

```text
Assess every PAsset-XX in <file>.csv. Before finishing, run verify_csv_inventory with that file and your full assessment in response_text. Report covered/total; list any missing IDs and complete them.
```

## Разовая настройка хоста (WSL2 / Linux)

```bash
sudo setcap cap_net_raw+eip "$(command -v dumpcap)"
sudo setcap cap_net_raw+eip "$(command -v tcpdump)"
getcap "$(command -v tcpdump)"
```

Используйте CAI Docker с `NET_RAW`, если политика безопасности запрещает `setcap` на хосте.

## Что CAI всё еще не умеет

См. [Platform limitations](../troubleshooting/platform_limitations.md). Резюме:

- **Скриншоты GUI Wireshark** через shell-агентов.
- **Гарантированный полный обзор** очень больших CSV за один проход без чанкинга и `verify_csv_inventory`.
- **Предоставление CAP_NET_RAW** без действий оператора или ИТ-специалиста на хосте.

## Верификация

- Регрессионные тесты: `tests/tools/test_capture_notice.py`, `test_evidence_inventory_check.py`
- Ручная проверка: [Operator feedback reproduction](../troubleshooting/operator_feedback_reproduction.md)

## Ссылки

- Логи сессий: `nopcap-onlytxt.zip`, `txt-to-png.zip` (май 2026, WSL2, модель alias1, агенты Network / Compliance).