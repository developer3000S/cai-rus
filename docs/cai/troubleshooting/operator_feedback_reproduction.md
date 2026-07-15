# Воспроизведение сценариев обратной связи от операторов в поле

Это руководство воспроизводит проблемы с PCAP / скриншотами / инвентаризациями из журналов сессий май 2026 года, предоставленных партнёрским сертифицирующим органом, а также способы проверки исправлений в CAI **v1.1.0+** (изменения артефактов доказательств на ветке `cai-v1.1.0`).

## Приложенные журналы (справочно)

| Zip | Сессия | Основной симптом |
|-----|---------|--------------|
| `nopcap-onlytxt.zip` | Compliance / SCM-1 | Ошибка `CAP_NET_RAW` → `.txt` в `packet_captures/` |
| `txt-to-png.zip` | Network analyzer | `.txt` «скриншоты» → ImageMagick PNG |

## 1) Уведомление об ошибке прав перехвата PCAP

**Воспроизведение (реальный перехват не требуется):**

```bash
cd cai
python3 -c "
from cai.tools.evidence.capture_notice import apply_packet_capture_notice
cmd = 'tcpdump -i any -w /tmp/t.pcap -c 1'
out = '''tcpdump: any: You don't have permission to perform this capture
(Attempt to create packet socket failed - CAP_NET_RAW may be required)'''
print(apply_packet_capture_notice(cmd, out))
"
```

**Ожидаемый результат:** вывод начинается с `[CAI PACKET-CAPTURE FAILURE]`.

**На WSL без setcap:**

```bash
tcpdump -i any -c 1 -w /tmp/test.pcap 2>&1 | head -5
```

Выполните ту же команду через CAI `generic_linux_command`; модель должна увидеть уведомление и не должна записывать вывод openssl/curl в `packet_captures/`.

**Исправьте окружение и повторите тест:**

```bash
sudo setcap cap_net_raw+eip "$(command -v dumpcap)"
```

## 2) Ложные скриншоты (txt → png)

**Воспроизведение подсказки пользователя (сетевой агент или агент CTF):**

> Установите связь с открытыми портами на 192.0.2.104, создайте pcaps по портам в assessments/ и сделайте скриншоты заметных частей в pcaps.

**До исправления:** агент записывает `assessments/screenshots/*.txt` (текст tshark).

**После исправления пользователем:** агент должен предпочитать `assessments/filtered-pcaps/*.pcap` и не должен утверждать, что PNG из ImageMagick являются захватами GUI Wireshark.

**Проверка в рабочем пространстве:**

```bash
find assessments -name '*.txt' -path '*/screenshots/*'
file assessments/real-screenshots/*.png 2>/dev/null | head -3
```

PNG-файлы, которые являются «PNG image data», но содержат только отрисованный текст, — это **диаграммы**, а не скриншоты GUI — ожидаемое ограничение.

## 3) Полнота инвентаризации CSV

```bash
cd cai
.venv/bin/python3 -m pytest \
  tests/tools/test_capture_notice.py \
  tests/tools/test_evidence_inventory_check.py \
  tests/tools/test_tool_generic_linux_command.py::test_packet_capture_failure_notice_detects_tcpdump_error \
  tests/tools/test_tool_generic_linux_command.py::test_packet_capture_failure_notice_skips_tshark_read_only \
  tests/tools/test_tool_generic_linux_command.py::test_generic_linux_command_prepends_capture_notice \
  -q --timeout=60
```

**Ожидаемый результат:** `8 passed` за несколько секунд. Если pytest зависает после `....`, старая сборка ожидала интерактивный пароль sudo — обновитесь до ветки, которая пропускает повтор sudo, когда уведомление о перехвате пакетов уже присутствует, затем нажмите Ctrl+C и перезапустите.

**Интерактивный тест:**

1. Создайте `workspace/test_assets.csv` с `PAsset-01` … `PAsset-10`.
2. Попросите агента Compliance оценить все; вставьте частичный ответ в `verify_csv_inventory` через вызов инструмента.
3. Убедитесь, что `MISSING` перечисляет пробелы.

## 4) Воспроизведение журналов JSONL (только чтение)

```bash
unzip -p ~/Downloads/nopcap-onlytxt.zip '*.jsonl' | \
  python3 -c "
import sys, json, re
for i, line in enumerate(sys.stdin, 1):
    if 'CAP_NET_RAW' in line or 'packet_captures' in line and '.txt' in line:
        print(i, line[:200])
" | head -20
```

Это подтверждает ошибки прав и текстовые заменители в исходной сессии.

## Что остаётся невозможным (сообщите оператору)

См. `docs/cai/troubleshooting/platform_limitations.md` для пояснений для заказчика.
