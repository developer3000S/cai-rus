# Кибербезопасностная ИИ-система (`CAI`)


[![version](https://badge.fury.io/py/cai-framework.svg)](https://badge.fury.io/py/cai-framework)
[![downloads](https://static.pepy.tech/badge/cai-framework)](https://pepy.tech/projects/cai-framework)
[![Linux](https://img.shields.io/badge/Linux-Supported-brightgreen?logo=linux&logoColor=white)](https://github.com/aliasrobotics/cai)
[![OS X](https://img.shields.io/badge/OS%20X-Supported-brightgreen?logo=apple&logoColor=white)](https://github.com/aliasrobotics/cai)
[![Windows](https://img.shields.io/badge/Windows-Supported-brightgreen?logo=windows&logoColor=white)](https://github.com/aliasrobotics/cai)
[![Android](https://img.shields.io/badge/Android-Supported-brightgreen?logo=android&logoColor=white)](https://github.com/aliasrobotics/cai)
[![Discord](https://img.shields.io/badge/Discord-7289DA?logo=discord&logoColor=white)](https://discord.gg/fnUFcTaQAC)
[![arXiv](https://img.shields.io/badge/arXiv-2504.06017-b31b1b.svg)](https://arxiv.org/pdf/2504.06017)
[![arXiv](https://img.shields.io/badge/arXiv-2506.23592-b31b1b.svg)](https://arxiv.org/pdf/2506.23592)
[![arXiv](https://img.shields.io/badge/arXiv-2508.13588-b31b1b.svg)](https://arxiv.org/pdf/2508.13588)
[![arXiv](https://img.shields.io/badge/arXiv-2508.21669-b31b1b.svg)](https://arxiv.org/pdf/2508.21669)
[![arXiv](https://img.shields.io/badge/arXiv-2509.14096-b31b1b.svg)](https://arxiv.org/pdf/2509.14096) 
[![arXiv](https://img.shields.io/badge/arXiv-2509.14139-b31b1b.svg)](https://arxiv.org/pdf/2509.14139)
[![arXiv](https://img.shields.io/badge/arXiv-2510.17521-b31b1b.svg)](https://arxiv.org/pdf/2510.17521)
[![arXiv](https://img.shields.io/badge/arXiv-2510.24317-b31b1b.svg)](https://arxiv.org/pdf/2510.24317)

 

 

 

 
 
 

 Professional Edition с неограниченными токенами alias1 | 📊 Посмотреть бенчмарки | 🚀 Узнать больше 

 
 
 
 
 
 
 
 
 
 
 
 

 
 
 
 
 
 🔓 Community Edition 
 Исследования и обучение · Идеально для исследователей и студентов 
 pip install cai-framework 
 
 ✅ Бесплатно для исследований 
 🤖 300+ ИИ-моделей 
 🌍 Поддержка сообщества 
 📚 Открытый исходный код 
 🔧 Расширяемый фреймворк 
 
 
 
 🚀 Professional Edition 
 Для предприятий и продакшена · €350/мес · Неограниченные токены alias1 
 
 → Перейти на PRO 
 
 
 ⚡ модель alias1 - ∞ неограниченные токены 
 🚫 Ноль отказов - Неограниченный ИИ 
 🏆 Превосходит GPT-5 в CTF бенчмарках 
 🛡️ Профессиональная поддержка включена 
 🇪🇺 Европейский суверенитет данных 
 
 
 
 
 
 
 
 CAI PRO с моделью alias1 превосходит GPT-5 в бенчмарках кибербезопасности AI vs AI | Посмотреть полные бенчмарки → 
 
 
 
 
 
-->

Кибербезопасностная ИИ-система (CAI) — это лёгкий фреймворк с открытым исходным кодом, который помогает специалистам по безопасности создавать и разворачивать автоматизацию атак и защиты на базе ИИ. CAI — это *де-факто* фреймворк для AI Security: его используют тысячи отдельных пользователей и сотни организаций. Независимо от того, являетесь ли вы исследователем безопасности, этичным хакером, ИТ-специалистом или организацией, стремящейся улучшить свою систему защиты, CAI предоставляет строительные блоки для создания специализированных ИИ-агентов, которые помогают с митигацией, поиском уязвимостей, эксплуатацией и оценкой безопасности.


## 🔓 Запуск CAI без ключа Alias API (`CAI_LICENSE_OFF`)

CAI может работать **без `ALIAS_API_KEY`** (то есть без лицензии Alias Robotics), если установить переменную окружения **`CAI_LICENSE_OFF=1`**.

Когда `CAI_LICENSE_OFF` задан как `1`, `true` или `yes`:

- Проверка лицензии при старте **пропускается** — `ALIAS_API_KEY` не требуется.
- CAI запускается в **open-source режиме**, а обновления направляются на публичный пакет PyPI `cai-framework`, а не на приватный индекс пакетов Alias.
- Можно использовать любой другой поддерживаемый провайдер моделей (OpenAI, Anthropic, DeepSeek, Ollama и т.д.), настроив `CAI_MODEL` и соответствующий API-ключ провайдера.

Быстрый старт без лицензии:


```bash
export CAI_LICENSE_OFF=1
cai
```

Или одной строкой:

```bash
CAI_LICENSE_OFF=1 cai
```

> Примечание: Модель `alias1` по-прежнему требует действующий `ALIAS_API_KEY`. `CAI_LICENSE_OFF` лишь обходит лицензионный фильтр фреймворка — он не предоставляет доступ к моделям, хостящимся в Alias.

**Основные возможности:**
- 🤖 **300+ ИИ-моделей**: Поддержка OpenAI, Anthropic, DeepSeek, Ollama и других.
- 🔧 **Встроенные инструменты безопасности**: Готовые инструменты для разведки, эксплуатации и повышения привилегий.
- 🏆 **Проверено в бою**: Доказано в CTF на HackTheBox, программах bug bounty и реальных [кейсах по безопасности](https://aliasrobotics.com/case-studies-robot-cybersecurity.php).
- 🎯 **Агентская архитектура**: Модульный дизайн фреймворка для создания специализированных агентов под разные задачи безопасности.
- 🛡️ **Защитные барьеры (Guardrails)**: Встроенная защита от инъекций промптов и выполнения опасных команд.
- 📚 **Ориентация на исследования**: Исследовательский фундамент для демократизации ИИ в кибербезопасности для сообщества.

> [!NOTE]
> Читайте технический отчет: [CAI: An Open, Bug Bounty-Ready Cybersecurity AI](https://arxiv.org/pdf/2504.06017)
>
> Для дальнейшего ознакомления обратитесь к разделам [Влияние](#-impact) и [Цитирование CAI](#citation).

| [`Robotics` - CAI и alias1 на: Гуманоидном роботе Unitree G1](https://aliasrobotics.com/case-study-humanoid-robot-g1.php) | [`OT` - CAI и alias1 на: Dragos OT CTF 2025](https://aliasrobotics.com/case-study-dragos-CTF.php) |
|------------------------------------------------|---------------------------------|
| CAI выявляет уязвимости и нарушения конфиденциальности в гуманоидных роботах Unitree G1, включая несанкционированную передачу телеметрии на серверы, связанные с Китаем, открытые RSA-ключи с правами записи для всех пользователей и потенциальные возможности слежки, нарушающие GDPR и международные законы о конфиденциальности. | CAI на базе alias1 демонстрирует исключительную эффективность в кибербезопасности операционных технологий (OT), заняв место в Топ-10 на Dragos OT CTF 2025. ИИ-агент достиг 1-го места в период с 7-го по 8-й час соревнований, выполнил 32 из 34 заданий и сохранял преимущество в скорости в 37% над лучшими человеческими командами. |
| [![](docs/assets/images/case-study-humanoid-portada.png)](https://aliasrobotics.com/case-study-humanoid-robot-g1.php) | [![](docs/assets/images/case-study-dragosCTF.png)](https://aliasrobotics.com/case-study-dragos-CTF.php) |

| [`IT` (Bug Bounty) - CAI на: Платформе HackerOne](https://aliasrobotics.com/case-study-hackerone.php) | [`OT` - CAI и alias0 на: Тепловых насосах Ecoforest](https://aliasrobotics.com/case-study-ecoforest.php) |
|------------------------------------------------|---------------------------------|
| Ведущие инженеры HackerOne используют CAI для изучения агентных ИИ-архитектур нового поколения и создания собственных продуктов безопасности. Агент Retester в CAI напрямую вдохновил созданный HackerOne агент дедупликации на базе ИИ, который сейчас развернут в продакшене для обработки миллионов отчетов об уязвимостях в масштабе. | CAI обнаруживает критическую уязвимость в тепловых насосах Ecoforest, позволяющую осуществлять несанкционированный удаленный доступ и приводящую к потенциально катастрофическим сбоям. Тестирование безопасности с помощью ИИ выявило открытые учетные данные и слабости шифрования DES, затрагивающие все установленные устройства в Европе. |
| [![](docs/assets/images/case-study-hackerone.png)](https://aliasrobotics.com/case-study-hackerone.php) | [![](https://aliasrobotics.com/img/case-study-portada-ecoforest.png)](https://aliasrobotics.com/case-study-ecoforest.php) |

| [`Robotics` - CAI и alias0 на: Мобильных индустриальных роботах (MiR)](https://aliasrobotics.com/case-study-cai-mir.php) | [`IT` (Web) - CAI и alias0 на: E-commerce Mercado Libre](https://aliasrobotics.com/case-study-mercado-libre.php) |
|------------------------------------------------|---------------------------------|
| Тестирование безопасности платформы MiR (Mobile Industrial Robot) с помощью CAI через автоматизированные атаки с инъекцией сообщений ROS. Это исследование демонстрирует, как поиск уязвимостей на базе ИИ может выявить несанкционированный доступ к системам управления роботами и триггерам тревоги. | Поиск уязвимостей API в Mercado Libre с помощью CAI через автоматизированные атаки перечисления. Это исследование демонстрирует, как тестирование безопасности на базе ИИ может выявить риски утечки пользовательских данных в e-commerce платформах в больших масштабах. |
| [![](https://aliasrobotics.com/img/case-study-portada-mir-cai.png)](https://aliasrobotics.com/case-study-cai-mir.php) | [![](https://aliasrobotics.com/img/case-study-portada-mercado-libre.png)](https://aliasrobotics.com/case-study-mercado-libre.php) |

| [`OT` - CAI и alias0 на: MQTT брокере](https://aliasrobotics.com/case-study-cai-mqtt-broker.php) | [`IT` (Web) - CAI и alias0 на: PortSwigger Web Security Academy](https://aliasrobotics.com/case-study-portswigger-1.php) |
|------------------------------------------------|---------------------------------|
| Тестирование с помощью CAI выявило критические недостатки в MQTT брокере внутри контейнеризированной OT-сети. Без аутентификации CAI подписался на топики температуры и влажности и внедрил ложные значения, исказив данные на дашбордах Grafana. | Эксплуатация состояния гонки (race condition) в уязвимости загрузки файлов с помощью CAI. Это исследование демонстрирует, как тестирование безопасности на базе ИИ может идентифицировать и эксплуатировать временные окна в веб-приложениях, успешно загружая и исполняя веб-шеллы через автоматизированные параллельные запросы. |
| [![](https://aliasrobotics.com/img/case-study-portada-mqtt-broker-cai.png)](https://aliasrobotics.com/case-study-cai-mqtt-broker.php) | [![](docs/assets/images/portada-portswigger-web-1.jpg)](https://aliasrobotics.com/case-study-portswigger-1.php) |

> [!WARNING]
> :warning: CAI находится в активной разработке, поэтому не ожидайте от него безупречной работы. Вместо этого помогите нам, создав issue или [отправив PR](https://github.com/aliasrobotics/cai/pulls).
>
> Доступ к этой библиотеке и использование информации, материалов (или их частей) **не предусмотрены и запрещены там, где такой доступ или использование нарушают применимые законы или правила**. Авторы ни в коем случае не поощряют и не пропагандируют несанкционированное вмешательство в работу систем. Это может нанести серьезный вред людям и привести к материальному ущербу.
>
> *Авторы CAI ни в коем случае не поощряют и не пропагандируют несанкционированное вмешательство в компьютерные системы. Пожалуйста, не используйте данный исходный код для киберпреступности. Занимайтесь пентестом во благо*. Загружая, используя или модифицируя этот исходный код, вы соглашаетесь с условиями [`LICENSE`](LICENSE) и ограничениями, изложенными в файле [`DISCLAIMER`](DISCLAIMER).

## :bookmark: Содержание

- [Кибербезопасностная ИИ-система (`CAI`)](#кибербезопасностная-ии-система-cai)

 - [:bookmark: Table of Contents](#bookmark-table-of-contents)
 - [🎯 Влияние](#-impact)
 - [🏆 Соревнования и челленджи](#-competitions-and-challenges)
 - [📊 Исследовательское влияние](#-research-impact)
 - [📚 Исследовательские продукты: `Cybersecurity AI`](#-research-products-cybersecurity-ai)
 - [PoCs](#pocs)
 - [Мотивация](#motivation)
- [:bust\_in\_silhouette: Почему CAI?](#bust_in_silhouette-why-cai)

- [Этические принципы CAI](#ethical-principles-behind-cai)
 - [Альтернативы с закрытым исходным кодом](#closed-source-alternatives)
 - [Обучение — «CAI Fluency»](#learn---cai-fluency)
 - [:nut\_and\_bolt: Установка](#nut_and_bolt-install)

 - [OS X](#os-x)
 - [Ubuntu 24.04](#ubuntu-2404)
 - [Ubuntu 20.04](#ubuntu-2004)
 - [Windows WSL](#windows-wsl)
 - [Android](#android)
 - [:nut\_and\_bolt: Настройка файла `.env`](#nut_and_bolt-setup-env-file)
 - [🔹 Поддержка кастомного OpenAI Base URL](#-custom-openai-base-url-support)
 - [:triangular\_ruler: Архитектура:](#triangular_ruler-architecture)
 - [🔹 Агент](#-agent)
 - [🔹 Инструменты](#-tools)
 - [🔹 Передачи (Handoffs)](#-handoffs)
 - [🔹 Паттерны](#-patterns)
 - [🔹 Ходы и взаимодействия](#-turns-and-interactions)
 - [🔹 Трассировка](#-tracing)
 - [🔹 Защитные барьеры (Guardrails)](#-guardrails)
 - [🔹 Человек в контуре (HITL)](#-human-in-the-loop-hitl)
 - [:rocket: Быстрый старт](#rocket-quickstart)
 - [Переменные окружения](#environment-variables)
 - [Интеграция с OpenRouter](#openrouter-integration)
 - [Azure OpenAI](#azure-openai)
 - [MCP](#mcp)
 - [Разработка](#development)
 - [Вклад в проект](#contributions)
 - [Дополнительные требования: caiextensions](#optional-requirements-caiextensions)
 - [:information\_source: Сбор данных об использовании](#information_source-usage-data-collection)
 - [Воспроизведение CI-настройки локально](#reproduce-ci-setup-locally)
 - [FAQ](#faq)
 - [Цитирование](#citation)
 - [Благодарности](#acknowledgements)
 - [Академическое сотрудничество](#academic-collaborations)

## 🎯 Влияние


### 🏆 Соревнования и челленджи

[![](https://img.shields.io/badge/HTB_ranking-top_90_Spain_(5_days)-red.svg)](https://app.hackthebox.com/users/2268644)
[![](https://img.shields.io/badge/HTB_ranking-top_50_Spain_(6_days)-red.svg)](https://app.hackthebox.com/users/2268644)
[![](https://img.shields.io/badge/HTB_ranking-top_30_Spain_(7_days)-red.svg)](https://app.hackthebox.com/users/2268644)
[![](https://img.shields.io/badge/HTB_ranking-top_500_World_(7_days)-red.svg)](https://app.hackthebox.com/users/2268644)
[![](https://img.shields.io/badge/HTB_"Human_vs_AI"_CTF-top_1_(AIs)_world-red.svg)](https://ctf.hackthebox.com/event/2000/scoreboard)
[![](https://img.shields.io/badge/HTB_"Human_vs_AI"_CTF-top_1_Spain-red.svg)](https://ctf.hackthebox.com/event/2000/scoreboard)
[![](https://img.shields.io/badge/HTB_"Human_vs_AI"_CTF-top_20_World-red.svg)](https://ctf.hackthebox.com/event/2000/scoreboard)
[![](https://img.shields.io/badge/HTB_"Human_vs_AI"_CTF-750_$-yellow.svg)](https://ctf.hackthebox.com/event/2000/scoreboard)
[![](https://img.shields.io/badge/Mistral_AI_Robotics_Hackathon-2500_$-yellow.svg)](https://lu.ma/roboticshack?tk=RuryKF)

### 📊 Исследовательское влияние

- Создали основу LLM-ориентированной защиты AI с PentestGPT, заложив фундамент исследовательского домена `Cybersecurity AI` [![arXiv](https://img.shields.io/badge/arXiv-2308.06782-4a9b8e.svg)](https://arxiv.org/pdf/2308.06782)

- Сформировали линию исследований `Cybersecurity AI`, опубликовав **8 статей и технических отчетов** в рамках активного научного сотрудничества [![arXiv](https://img.shields.io/badge/arXiv-2504.06017-63bfab.svg)](https://arxiv.org/pdf/2504.06017) [![arXiv](https://img.shields.io/badge/arXiv-2506.23592-7dd3c0.svg)](https://arxiv.org/abs/2506.23592) [![arXiv](https://img.shields.io/badge/arXiv-2508.13588-52a896.svg)](https://arxiv.org/abs/2508.13588) [![arXiv](https://img.shields.io/badge/arXiv-2508.21669-85e0d1.svg)](https://arxiv.org/abs/2508.21669) [![arXiv](https://img.shields.io/badge/arXiv-2509.14096-3e8b7a.svg)](https://arxiv.org/abs/2509.14096) [![arXiv](https://img.shields.io/badge/arXiv-2509.14139-6bc7b5.svg)](https://arxiv.org/abs/2509.14139) [![arXiv](https://img.shields.io/badge/arXiv-2510.17521-b31b1b.svg)](https://arxiv.org/abs/2510.17521) [![arXiv](https://img.shields.io/badge/arXiv-2510.24317-b31b1b.svg)](https://arxiv.org/abs/2510.24317)

- Продемонстрировали **3 600-кратное улучшение производительности** по сравнению с людьми-пентестерами в стандартизированных CTF-бенчмарках [![arXiv](https://img.shields.io/badge/arXiv-2504.06017-63bfab.svg)](https://arxiv.org/pdf/2504.06017)
- Выявили **уязвимости с уровнем серьезности CVSS 4.3-7.5** в продакшн-системах с помощью автоматизированной оценки безопасности [![arXiv](https://img.shields.io/badge/arXiv-2504.06017-63bfab.svg)](https://arxiv.org/pdf/2504.06017)
- **Демократизация исследований уязвимостей с помощью ИИ**: CAI позволяет как экспертам из других областей, так и опытным исследователям более эффективно находить уязвимости, расширяя сообщество исследователей безопасности и позволяя малым и средним предприятиям проводить автономные оценки безопасности [![arXiv](https://img.shields.io/badge/arXiv-2504.06017-63bfab.svg)](https://arxiv.org/pdf/2504.06017)
- **Систематическая оценка больших языковых моделей** как проприетарных, так и открытых архитектур, выявившая значительные разрывы между заявленными вендорами возможностями и эмпирическими метриками производительности в кибербезопасности [![arXiv](https://img.shields.io/badge/arXiv-2504.06017-63bfab.svg)](https://arxiv.org/pdf/2504.06017)
- Определили **уровни автономности в кибербезопасности** и представили аргументы в пользу автономности против автоматизации в данной области [![arXiv](https://img.shields.io/badge/arXiv-2506.23592-7dd3c0.svg)](https://arxiv.org/abs/2506.23592)
- **Совместные исследовательские инициативы** с международными академическими институтами, направленные на разработку учебных программ и методик обучения кибербезопасности [![arXiv](https://img.shields.io/badge/arXiv-2508.13588-52a896.svg)](https://arxiv.org/abs/2508.13588)
- **Разработали комплексный фреймворк защиты от инъекций промптов в ИИ-агентах безопасности**: создали и эмпирически подтвердили многослойную систему защиты, решающую выявленные проблемы инъекций промптов [![arXiv](https://img.shields.io/badge/arXiv-2508.21669-85e0d1.svg)](https://arxiv.org/abs/2508.21669)
- Исследовали кибербезопасность гуманоидных роботов с помощью CAI и выявили новые векторы атак, показывающие, как робот может `(а)` одновременно работать как скрытый узел наблюдения и `(б)` использоваться в качестве платформы для активных киберопераций [![arXiv](https://img.shields.io/badge/arXiv-2509.14096-3e8b7a.svg)](https://arxiv.org/abs/2509.14096) [![arXiv](https://img.shields.io/badge/arXiv-2509.14139-6bc7b5.svg)](https://arxiv.org/abs/2509.14139)

### 📚 Исследовательские продукты: `Cybersecurity AI`


| CAI, An Open, Bug Bounty-Ready Cybersecurity AI [![arXiv](https://img.shields.io/badge/arXiv-2504.06017-63bfab.svg)](https://arxiv.org/pdf/2504.06017) | The Dangerous Gap Between Automation and Autonomy [![arXiv](https://img.shields.io/badge/arXiv-2506.23592-7dd3c0.svg)](https://arxiv.org/abs/2506.23592) | CAI Fluency, A Framework for Cybersecurity AI Fluency [![arXiv](https://img.shields.io/badge/arXiv-2508.13588-52a896.svg)](https://arxiv.org/abs/2508.13588) | Hacking the AI Hackers via Prompt Injection [![arXiv](https://img.shields.io/badge/arXiv-2508.21669-85e0d1.svg)](https://arxiv.org/abs/2508.21669) |
|---|---|---|---|
| [](https://arxiv.org/pdf/2504.06017) | [](https://www.arxiv.org/pdf/2506.23592) | [](https://arxiv.org/pdf/2508.13588) | [](https://arxiv.org/pdf/2508.21669) |

 | Humanoid Robots as Attack Vectors [![arXiv](https://img.shields.io/badge/arXiv-2509.14139-6bc7b5.svg)](https://arxiv.org/abs/2509.14139) | The Cybersecurity of a Humanoid Robot [![arXiv](https://img.shields.io/badge/arXiv-2509.14096-3e8b7a.svg)](https://arxiv.org/abs/2509.14096) | Evaluating Agentic Cybersecurity in Attack/Defense CTFs [![arXiv](https://img.shields.io/badge/arXiv-2510.17521-b31b1b.svg)](https://arxiv.org/abs/2510.17521) | CAIBench: A Meta-Benchmark for Evaluating Cybersecurity AI Agents [![arXiv](https://img.shields.io/badge/arXiv-2510.24317-b31b1b.svg)](https://arxiv.org/abs/2510.24317) |
|---|---|---|---|
| [](https://arxiv.org/pdf/2509.14139) | [](https://arxiv.org/pdf/2509.14096) | [](https://arxiv.org/pdf/2510.17521) | [](https://arxiv.org/pdf/2510.24317) |

## PoCs
| CAI с `alias0` на атаках с инъекцией сообщений ROS в роботе MiR-100 | CAI с `alias0` на поиске уязвимостей API в Mercado Libre |
|-----------------------------------------------|---------------------------------|
| [![asciicast](https://asciinema.org/a/dNv705hZel2Rzrw0cju9HBGPh.svg)](https://asciinema.org/a/dNv705hZel2Rzrw0cju9HBGPh) | [![asciicast](https://asciinema.org/a/9Hc9z1uFcdNjqP3bY5y7wO1Ww.svg)](https://asciinema.org/a/9Hc9z1uFcdNjqP3bY5y7wO1Ww) |

| CAI на JWT@PortSwigger CTF — Cybersecurity AI | CAI на HackableII Boot2Root CTF — Cybersecurity AI |
|-----------------------------------------------|---------------------------------|
| [![asciicast](https://asciinema.org/a/713487.svg)](https://asciinema.org/a/713487) | [![asciicast](https://asciinema.org/a/713485.svg)](https://asciinema.org/a/713485) |

Больше кейсов и PoC доступны по адресу [https://aliasrobotics.com/case-studies-robot-cybersecurity.php](https://aliasrobotics.com/case-studies-robot-cybersecurity.php).

## Мотивация
### :bust_in_silhouette: Почему CAI?

Ландшафт кибербезопасности претерпевает драматическую трансформацию по мере того, как ИИ всё глубже интегрируется в операции по обеспечению безопасности. **Мы прогнозируем, что к 2028 году инструменты тестирования безопасности на базе ИИ по количеству превысят число людей-пентестеров**. Этот сдвиг представляет собой фундаментальное изменение в нашем подходе к решению задач кибербезопасности. *ИИ — это не просто очередной инструмент, он становится необходимым для устранения сложных уязвимостей и опережения изощренных угроз. Поскольку организации сталкиваются с более продвинутыми кибератаками, тестирование безопасности с помощью ИИ станет решающим фактором для поддержания надежной защиты.*

Эта работа опирается на предыдущие усилия[^4], и аналогично мы считаем, что демократизация доступа к продвинутым ИИ-инструментам кибербезопасности жизненно важна для всего сообщества. Именно поэтому мы выпускаем Cybersecurity AI (`CAI`) как фреймворк с открытым исходным кодом. Наша цель — дать исследователям безопасности, этичным хакерам и организациям возможность создавать и развертывать мощные инструменты безопасности на базе ИИ. Делая эти возможности общедоступными, мы стремимся уравнять шансы и гарантировать, что передовые технологии ИИ в безопасности не будут ограничены только хорошо финансируемыми частными компаниями или государственными структурами.

Программы Bug Bounty стали краеугольным камнем современной кибербезопасности, предоставляя организациям важнейший механизм выявления и исправления уязвимостей в их системах до того, как они будут эксплуатированы. Эти программы доказали свою высокую эффективность в защите как общественной, так и частной инфраструктуры, позволяя исследователям находить критические уязвимости, которые иначе могли бы остаться незамеченными. CAI специально разработан для усиления этих усилий, предоставляя легкий, эргономичный фреймворк для создания специализированных ИИ-агентов, которые могут помогать в различных аспектах охоты за Bug Bounty — от первоначальной разведки до валидации уязвимостей и составления отчетов. Наш фреймворк стремится дополнить человеческий опыт возможностями ИИ, помогая исследователям работать более эффективно и тщательно в стремлении сделать цифровые системы более безопасными.

### Этические принципы CAI


Вы можете задаться вопросом, этично ли выпускать CAI *в открытый доступ*, учитывая его возможности и последствия для безопасности. Наше решение сделать этот фреймворк открытым руководствуется двумя основными этическими принципами:

1. **Демократизация ИИ в кибербезопасности**: Мы считаем, что продвинутые ИИ-инструменты кибербезопасности должны быть доступны всему сообществу, а не только богатым частным компаниям или государственным структурам. Выпуская CAI как open-source фреймворк, мы стремимся дать возможность исследователям безопасности, этичным хакерам и организациям создавать и развертывать мощные инструменты на базе ИИ, уравнивая возможности в сфере кибербезопасности.

2. **Прозрачность возможностей ИИ в безопасности**: Основываясь на результатах наших исследований, понимании технологии и анализе ведущих технических отчетов, мы утверждаем, что текущие вендоры LLM занижают возможности своих моделей в области кибербезопасности. Это крайне опасно и вводит в заблуждение. Разрабатывая CAI открыто, мы предоставляем прозрачный бенчмарк того, что ИИ-системы на самом деле могут делать в контексте кибербезопасности, позволяя принимать более обоснованные решения о состоянии защиты.

CAI построен на следующих основных принципах:
- **ИИ-фреймворк, ориентированный на кибербезопасность**: CAI специально разработан для сценариев кибербезопасности, стремясь к частичной и полной автоматизации наступательных и оборонительных задач.
- **Открытый исходный код, бесплатно для исследований**: CAI имеет открытый исходный код и бесплатен для исследовательских целей. Мы стремимся демократизировать доступ к ИИ и кибербезопасности. Для профессионального или коммерческого использования, включая on-premise развертывание, выделенную техническую поддержку и кастомные расширения, пожалуйста, [свяжитесь с нами](mailto:research@aliasrobotics.com) для получения лицензии.
- **Легкость**: CAI спроектирован так, чтобы быть быстрым и простым в использовании.
- **Модульный и агент-центричный дизайн**: CAI работает на основе агентов и агентских паттернов, что обеспечивает гибкость и масштабируемость. Вы можете легко добавить наиболее подходящих агентов и паттерн для вашего конкретного случая в кибербезопасности.
- **Интеграция инструментов**: CAI включает в себя уже встроенные инструменты и позволяет пользователю легко интегрировать свои собственные инструменты с собственной логикой.
- **Интегрированное логирование и трассировка**: использование [`phoenix`](https://github.com/Arize-ai/phoenix), open-source инструмента трассировки и логирования для LLM. Это обеспечивает пользователю детальную прослеживаемость действий агентов и их выполнения.
- **Поддержка нескольких моделей**: более 300 поддерживаемых моделей благодаря [LiteLLM](https://github.com/BerriAI/litellm). Самые популярные провайдеры:
 - **Anthropic**: `Claude 3.7`, `Claude 3.5`, `Claude 3`, `Claude 3 Opus`
 - **OpenAI**: `O1`, `O1 Mini`, `O3 Mini`, `GPT-4o`, `GPT-4.5 Preview`
 - **DeepSeek**: `DeepSeek V3`, `DeepSeek R1`
 - **Ollama**: `Qwen2.5 72B`, `Qwen2.5 14B` и др.

### Альтернативы с закрытым исходным кодом

Кибербезопасность на базе ИИ — критически важная область, однако многие группы ошибочно пытаются развивать её через закрытые методы ради чистой экономической выгоды, используя схожие техники и опираясь на существующие закрытые (часто принадлежащие третьим лицам) модели. Такой подход не только растрачивает ценные инженерные ресурсы, но и представляет собой экономическую потерю, приводя к избыточным усилиям, так как они часто в итоге «изобретают велосипед». Вот некоторые из закрытых инициатив, за которыми мы следим и которые пытаются использовать genAI и агентные фреймворки в ИИ для кибербезопасности:

- [Autonomous Cyber](https://www.acyber.co/)
- [CrackenAGI](https://cracken.ai/)
- [ETHIACK](https://ethiack.com/)
- [Horizon3](https://horizon3.ai/)
- [Irregular](https://www.irregular.com/)
- [Kindo](https://www.kindo.ai/)
- [Lakera](https://lakera.ai)
- [Mindfort](www.mindfort.ai)
- [Mindgard](https://mindgard.ai/)
- [NDAY Security](https://ndaysecurity.com/)
- [Penligent](https://penligent.ai/) 
- [Runsybil](https://www.runsybil.com)
- [Selfhack](https://www.selfhack.fi)
- [Sola Security](https://sola.security/)
- [SQUR](https://squr.ai/)
- [Staris](https://staris.tech/)
- [Sxipher](https://www.sxipher.com/) (кажется, прекращен)
- [Terra Security](https://www.terra.security)
- [Vibeproxy](https://vibeproxy.app/) 
- [Xint](https://xint.io/)
- [XBOW](https://www.xbow.com)
- [ZeroPath](https://www.zeropath.com)
- [Zynap](https://www.zynap.com)
- [7ai](https://7ai.com)

## Обучение — `CAI` Fluency

 
 
 
 
 
 
 

> [!NOTE]
>
> Технический отчет CAI Fluency ([arXiv:2508.13588](https://arxiv.org/pdf/2508.13588)) устанавливает формальные образовательные рамки для грамотности в области ИИ для кибербезопасности.

| | Описание | English | Spanish |
|-------|----------------|---------|---------|
| **Эпизод 0**: Что такое CAI? | Объяснение Cybersecurity AI (`CAI`) | [![Watch the video](https://img.youtube.com/vi/nBdTxbKM4oo/0.jpg)](https://www.youtube.com/watch?v=nBdTxbKM4oo) | [![Watch the video](https://img.youtube.com/vi/FaUL9HXrQ5k/0.jpg)](https://www.youtube.com/watch?v=FaUL9HXrQ5k) |
| **Эпизод 1**: Фреймворк `CAI` | Видение и Этика - Исследуйте основную мотивацию CAI и углубитесь в важнейшие этические принципы, руководствующие его разработкой. Поймите мотивацию CAI и то, как вы можете активно способствовать будущему кибербезопасности и фреймворка CAI. | [![Watch the video](https://img.youtube.com/vi/QEiGdsMf29M/0.jpg)](https://www.youtube.com/watch?v=QEiGdsMf29M&list=PLLc16OUiZWd4RuFdN5_Wx9xwjCVVbopzr&index=3) | |
| **Эпизод 2**: От нуля до кибер-героя | Погружение в кибербезопасность с ИИ - Комплексное руководство для абсолютных новичков, чтобы стать практиками кибербезопасности, используя CAI и ИИ-инструменты. Узнайте, как использовать искусственный интеллект для ускорения вашего обучения, от понимания базовых концепций безопасности до проведения реальных оценок безопасности, не требуя предварительного опыта. | [![Watch the video](https://img.youtube.com/vi/hSTLHOOcQoY/0.jpg)](https://www.youtube.com/watch?v=hSTLHOOcQoY&list=PLLc16OUiZWd4RuFdN5_Wx9xwjCVVbopzr&index=14) | |
| **Эпизод 3**: Туториал по Vibe-Hacking | «Мой первый взлом» - руководство по Vibe-Hacking для новичков. Мы демонстрируем простой веб-взлом с использованием агента по умолчанию и показываем, как использовать инструменты и интерпретировать вывод CAI с помощью Python API. Вы также научитесь сравнивать различные LLM-модели, чтобы найти лучшую для ваших целей. | [![Watch the video](https://img.youtube.com/vi/9vZ_Iyex7uI/0.jpg)](https://www.youtube.com/watch?v=9vZ_Iyex7uI&list=PLLc16OUiZWd4RuFdN5_Wx9xwjCVVbopzr&index=1) | [![Watch the video](https://img.youtube.com/vi/iAOMaI1ftiA/0.jpg)](https://www.youtube.com/watch?v=iAOMaI1ftiA&list=PLLc16OUiZWd4RuFdN5_Wx9xwjCVVbopzr&index=2) |
| **Эпизод 4**: Интро в ReAct | Эволюция LLM - Узнайте, как LLM эволюционировали от базовых языковых моделей до продвинутых мультиагентных ИИ-систем. От базовых LLM к Chain-of-Thought и Reasoning LLM, затем к ReAct и мультиагентным архитектурам. Познакомьтесь с базовыми терминами. | [![Watch the video](https://img.youtube.com/vi/tLdFO1flj_o/0.jpg)](https://www.youtube.com/watch?v=tLdFO1flj_o&list=PLLc16OUiZWd4RuFdN5_Wx9xwjCVVbopzr&index=13) | |
| **Эпизод 5**: CAI в CTF челленджах | Погрузитесь в соревнования Capture The Flag (CTF) с помощью CAI. Узнайте, как использовать ИИ-агентов для решения различных задач кибербезопасности, включая веб-эксплуатацию, криптографию, реверс-инжиниринг и форензику. Узнайте, как настроить CAI для соревновательного хакинга и максимизировать результаты в CTF с помощью интеллектуальной автоматизации. | [![Watch the video](https://img.youtube.com/vi/MrXTQ0e2to4/0.jpg)](https://www.youtube.com/watch?v=MrXTQ0e2to4&list=PLLc16OUiZWd4RuFdN5_Wx9xwjCVVbopzr&index=13) | [![Watch the video](https://img.youtube.com/vi/r9US_JZa9_c/0.jpg)](https://www.youtube.com/watch?v=r9US_JZa9_c&list=PLLc16OUiZWd4RuFdN5_Wx9xwjCVVbopzr&index=12) |
| | | | |
| **Приложение 1**: Релиз `CAI` 0.5.x | Представляем версию 0.5 `CAI`, включая новый мультиагентный функционал, новые команды, такие как `/history`, `/compact`, `/graph` или `/memory`, и кейс, показывающий, как `CAI` нашел критическую уязвимость в OT тепловых насосах по всему миру. | [![Watch the video](https://img.youtube.com/vi/OPFH0ANUMMw/0.jpg)](https://www.youtube.com/watch?v=OPFH0ANUMMw) | [![Watch the video](https://img.youtube.com/vi/Q8AI4E4gH8k/0.jpg)](https://www.youtube.com/watch?v=Q8AI4E4gH8k) |
| **Приложение 2**: Релиз `CAI` 0.4.x и `alias0` | Представляем версию 0.4 `CAI` со *стримингом* и улучшенной поддержкой MCP. Мы также представляем `alias0`, Privacy-First Cybersecurity AI, интеллект «модель-над-моделями», который реализует архитектуру Privacy-by-Design и достигает передовых результатов в бенчмарках кибербезопасности. | [![Watch the video](https://img.youtube.com/vi/NZjzfnvAZcc/0.jpg)](https://www.youtube.com/watch?v=NZjzfnvAZcc) | |
| **Приложение 3**: Первая встреча сообщества Cybersecurity AI | Первая встреча сообщества Cybersecurity AI (`CAI`), более 40 участников из академии, индустрии и обороны собрались, чтобы обсудить open-source каркас CAI — проект, предназначенный для создания агентных ИИ-систем для кибербезопасности, которые являются открытыми, модульными и готовыми к Bug Bounty. | [![Watch the video](https://img.youtube.com/vi/4JqaTiVlgsw/0.jpg)](https://www.youtube.com/watch?v=4JqaTiVlgsw) | |
| **Приложение 4**: `CAI PRO` PoC | Короткая демонстрация возможностей [CAI PRO](https://aliasrobotics.com/cybersecurityai.php), показывающая Professional Edition с неограниченными токенами `alias1`, неограниченным ИИ и функциями тестирования безопасности корпоративного уровня. | ![CAI PRO Demo](media/caipro_poc.gif) | |
| **Приложение 5**: `CAI` PoC | Короткая демонстрация Community Edition, показывающая основные возможности open-source фреймворка для тестирования безопасности и поиска уязвимостей на базе ИИ. | ![CAI Demo](media/cai_poc.gif) | |
| **Приложение 6**: CAI в `Jaula del N00B` | CAI (CIBERSEGURIDAD CON IA) LUIJAIT EN LA JAULA DEL N00B - Демонстрация и обсуждение возможностей фреймворка CAI в популярном испанском подкасте/шоу по кибербезопасности. | | [![Watch the video](https://img.youtube.com/vi/KD2_xzIOkWg/0.jpg)](https://www.youtube.com/watch?v=KD2_xzIOkWg) |

## :nut_and_bolt: Установка


> [!NOTE]
> **Пользователи CAI Professional Edition**: Если у вас есть активная подписка CAI Pro, мы предоставляем специальные руководства по установке для версий 0.5 и 0.6. Официальная поддержка доступна для Ubuntu 24.04 (x86_64). Инструкции по установке для других операционных систем предоставляются «как есть» без официальной поддержки:
> - [Руководство по установке CAI Pro v0.6](docs/Installation_Guide_for_CAI_Pro_v0.6.md)
> - [Руководство по установке CAI Pro v0.5](docs/Installation_Guide_for_CAI_Pro_v0.5.md)

### Установка редакции Community


```bash
pip install cai-framework
```

Всегда создавайте новое виртуальное окружение, чтобы обеспечить правильную установку зависимостей при обновлении CAI.

В следующих подразделах приведено более детальное руководство по выбранным популярным операционным системам. Инструкции по установке для разработчиков см. в разделе [Разработка](#development).
Синтаксис переменных окружения для API-ключей см. в документации LiteLLM. [LiteLLM Documentation](https://docs.litellm.ai/docs/tutorials/installation)

### OS X
```bash
brew update && \
    brew install git python@3.12

# Создание виртуального окружения
python3.12 -m venv cai_env

# Установка пакета из локального каталога
source cai_env/bin/activate && pip install cai-framework

# Генерация файла .env и настройка значений по умолчанию
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nPROMPT_TOOLKIT_NO_CPR=1\nCAI_STREAM=false' > .env

# Запуск CAI
cai  # первый запуск может занять до 30 секунд
```

### Ubuntu 24.04
```bash
sudo apt-get update && \
    sudo apt-get install -y git python3-pip python3.12-venv

# Создание виртуального окружения
python3.12 -m venv cai_env

# Установка пакета из локального каталога
source cai_env/bin/activate && pip install cai-framework

# Генерация файла .env и настройка значений по умолчанию
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nPROMPT_TOOLKIT_NO_CPR=1\nCAI_STREAM=false' > .env

# Запуск CAI
cai  # первый запуск может занять до 30 секунд
```

### Ubuntu 20.04
```bash
sudo apt-get update && \
    sudo apt-get install -y software-properties-common

# Установка Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# Создание виртуального окружения
python3.12 -m venv cai_env

# Установка пакета из локального каталога
source cai_env/bin/activate && pip install cai-framework

# Генерация файла .env и настройка значений по умолчанию
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nPROMPT_TOOLKIT_NO_CPR=1\nCAI_STREAM=false' > .env

# Запуск CAI
cai  # первый запуск может занять до 30 секунд
```

### Windows WSL
Перейдите на страницу Microsoft: https://learn.microsoft.com/en-us/windows/wsl/install. Здесь вы найдете все инструкции по установке WSL.

Из Powershell введите: `wsl --install`

```bash

sudo apt-get update && \
    sudo apt-get install -y git python3-pip python3-venv

# Создание виртуального окружения
python3 -m venv cai_env

# Установка пакета из локального каталога
source cai_env/bin/activate && pip install cai-framework

# Генерация файла .env и настройка значений по умолчанию. Если Ollama работает на вашем Windows-хосте, WSL должен использовать IP вашего хоста для доступа к ней.
echo -e 'OPENAI_API_KEY="sk-1234"\nANTHROPIC_API_KEY=""\nOLLAMA=""\nOLLAMA_API_BASE="http://Your.Host.Ip.Here:11434"\nPROMPT_TOOLKIT_NO_CPR=1\nCAI_STREAM=false' > .env

# Запуск CAI
cai  # первый запуск может занять до 30 секунд
```

Вы можете столкнуться с проблемами при запуске cai на ubuntu, так как некоторые агенты предполагают, что они работают в инстансе Kali, и не могут найти нужные инструменты. 
В качестве альтернативы вы можете использовать файл docker compose в папке dockerized. Это также работает внутри wsl, если установлен docker.
В этом случае скачайте папку dockerized (не обязательно весь репозиторий) и запустите из неё.
Синтаксис переменных окружения для API-ключей см. в документации LiteLLM. [LiteLLM Documentation](https://docs.litellm.ai/docs/tutorials/installation)

```bash
# Сборка и запуск docker compose. Сборка занимает около 20 мин.
docker compose build && docker compose up -d

# Доступ к cai
docker compose exec cai cai
```

### Android

Рекомендуется иметь как минимум 8 ГБ оперативной памяти:

1. Прежде всего, установите userland https://play.google.com/store/apps/details?id=tech.ula&hl=es

2. Установите Kali minimal в базовых опциях (бесплатно). [Или любой другой вариант kali, если предпочитаете]

3. Обновите ключи apt, как в этом примере: https://superuser.com/questions/1644520/apt-get-update-issue-in-kali, внутри терминала Kali в UserLand выполните:

```bash
# Получение новых ключей apt
wget http://http.kali.org/kali/pool/main/k/kali-archive-keyring/kali-archive-keyring_2024.1_all.deb

# Установка новых ключей apt
sudo dpkg -i kali-archive-keyring_2024.1_all.deb && rm kali-archive-keyring_2024.1_all.deb

# Обновление APT репозитория
sudo apt-get update

# CAI требует python 3.12, установим его (CAI для kali в Android)
sudo apt-get update && sudo apt-get install -y git python3-pip build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev pkg-config
wget https://www.python.org/ftp/python/3.12.4/Python-3.12.4.tar.xz
tar xf Python-3.12.4.tar.xz
cd ./configure --enable-optimizations
sudo make altinstall # Эта команда выполняется долго

# Клонирование исходного кода CAI
git clone https://github.com/aliasrobotics/cai && cd cai

# Создание виртуального окружения
python3.12 -m venv cai_env

# Установка пакета из локального каталога
source cai_env/bin/activate && pip3 install -e .

# Генерация файла .env и настройка
cp .env.example .env  # отредактируйте здесь ваши ключи/модели

# Запуск CAI
cai
```

### :nut_and_bolt: Настройка файла `.env`

CAI использует файл `.env` для загрузки конфигурации при запуске. Для облегчения настройки в репозитории предоставлен пример файла [`.env.example`](.env.example), который служит шаблоном для настройки CAI и ваших API-ключей LLM для работы с желаемыми моделями.

:warning: Важно:

CAI НЕ предоставляет API-ключи для каких-либо моделей по умолчанию. Не просите нас предоставить ключи, используйте свои собственные или хостите свои модели.

:warning: Примечание:

Поле OPENAI_API_KEY не должно оставаться пустым. Оно должно содержать либо "sk-123" (в качестве заглушки), либо ваш настоящий API-ключ. См. https://github.com/aliasrobotics/cai/issues/27.

:warning: Примечание:

Если вы используете модель alias1, убедитесь, что версия CAI >0.4.0. Вот пример .env для её использования:

```bash
OPENAI_API_KEY="sk-1234"
OLLAMA=""
ALIAS_API_KEY="<sk-your-key>"  # примечание: добавьте свой ключ
CAI_STREAM=False
CAI_MODEL="alias1"
```

### 🔹 Поддержка кастомного OpenAI Base URL

CAI поддерживает настройку кастомного базового URL-адреса OpenAI API через переменную окружения `OPENAI_BASE_URL`. Это позволяет пользователям перенаправлять API-вызовы на кастомный эндпоинт, такой как прокси или самостоятельно хостящийся OpenAI-совместимый сервис.

Пример конфигурации записи в `.env`:
```
OLLAMA_API_BASE="https://custom-openai-proxy.com/v1"
```

Или напрямую из командной строки:
```bash
OLLAMA_API_BASE="https://custom-openai-proxy.com/v1" cai
```

## :triangular_ruler: Архитектура:

CAI фокусируется на том, чтобы сделать **координацию** и **выполнение** действий агентов кибербезопасности легкими, высококонтролируемыми и полезными для людей. Для этого он опирается на 8 столпов: `Agents` (Агенты), `Tools` (Инструменты), `Handoffs` (Передачи), `Patterns` (Паттерны), `Turns` (Ходы), `Tracing` (Трассировка), `Guardrails` (Защитные барьеры) и `HITL` (Человек в контуре).

```
                  ┌───────────────┐           ┌───────────┐
                  │      HITL     │◀─────-───▶│   Turns   │
                  └───────┬───────┘           └───────────┘
                          │
                          ▼
┌───────────┐       ┌───────────┐       ┌───────────┐      ┌───────────┐
│  Patterns │◀──-──▶│  Handoffs │◀──-─▶ │   Agents  │◀──-─▶│    LLMs   │
└───────────┘       └─────┬─────┘       └─────┬─────┘      └───────────┘
                          │                   │
                          │                   ▼
┌────────────┐       ┌────┴──────┐       ┌───────────┐     ┌────────────┐
│ Extensions │◀────▶ │  Tracing  │       │   Tools   │◀──▶ │ Guardrails │
└────────────┘       └───────────┘       └───────────┘     └────────────┘
                                              │
                          ┌─────────────┬─────┴────┬─────────────┐
                          ▼             ▼          ▼             ▼
                    ┌───────────┐┌───────────┐┌────────────┐┌───────────┐
                    │ LinuxCmd  ││ WebSearch ││    Code    ││ SSHTunnel │
                    └───────────┘└───────────┘└────────────┘└───────────┘
```

Если вы хотите глубже изучить код, используйте следующие файлы в качестве отправной точки для работы с CAI:

* [__init__.py](https://github.com/aliasrobotics/cai/blob/main/src/cai/__init__.py)
* [cli.py](https://github.com/aliasrobotics/cai/blob/main/src/cai/cli.py) - точка входа для интерфейса командной строки
* [util.py](https://github.com/aliasrobotics/cai/blob/main/src/cai/util.py) - вспомогательные функции
* [agents](https://github.com/aliasrobotics/cai/blob/main/src/cai/agents) - реализации агентов
* [internal](https://github.com/aliasrobotics/cai/blob/main/src/cai/internal) - внутренние функции CAI (эндпоинты, метрики, логирование и т.д.)
* [prompts](https://github.com/aliasrobotics/cai/blob/main/src/cai/prompts) - база промптов агентов
* [repl](https://github.com/aliasrobotics/cai/blob/main/src/cai/repl) - эстетика CLI и команды
* [sdk](https://github.com/aliasrobotics/cai/blob/main/src/cai/sdk) - SDK команд CAI
* [tools](https://github.com/aliasrobotics/cai/tree/main/src/cai/tools) - инструменты агентов

### 🔹 Агент

По сути, CAI абстрагирует свое поведение в области кибербезопасности через `Agents` (Агентов) и агентские `Patterns` (Паттерны). Агент — это *интеллектуальная система, которая взаимодействует с некоторой средой*. С технической точки зрения, в CAI мы придерживаемся робототехнического определения, согласно которому агент — это всё, что может рассматриваться как система, воспринимающая свою среду через сенсоры, рассуждающая о своих целях и действующая в соответствии с этим в данной среде через актуаторы (*адаптировано* из Russel & Norvig, AI: A Modern Approach). В кибербезопасности `Агент` взаимодействует с системами и сетями, используя периферийные устройства и сетевые интерфейсы в качестве сенсоров, рассуждает соответствующим образом, а затем выполняет сетевые действия, как если бы это были актуаторы. Соответственно, в CAI `Агенты` реализуют модель агента `ReACT` (Reasoning and Action — Рассуждение и Действие)[^3]. Для получения дополнительной информации см. [пример здесь](https://github.com/aliasrobotics/cai/blob/main/examples/basic/hello_world.py) с полным кодом выполнения и обратитесь к этому [jupyter notebook](https://github.com/aliasrobotics/cai/blob/main/fluency/my-first-hack/my_first_hack.ipynb) для ознакомления с туториалом по использованию.

```python
from cai.sdk.agents import Agent, Runner, OpenAIChatCompletionsModel

import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

agent = Agent(
      name="Custom Agent",
      instructions="""You are a Cybersecurity expert Leader""",
      model=OpenAIChatCompletionsModel(
          model=os.getenv('CAI_MODEL', "openai/gpt-4o"),
          openai_client=AsyncOpenAI(),
          )
      )

message = "Tell me about recursion in programming."
result = await Runner.run(agent, message)
```

### 🔹 Инструменты

`Tools` (Инструменты) позволяют агентам кибербезопасности предпринимать действия, предоставляя интерфейсы для выполнения системных команд, запуска сканирований безопасности, анализа уязвимостей и взаимодействия с целевыми системами и API. Это основные возможности, которые позволяют агентам CAI эффективно выполнять задачи безопасности. В CAI инструменты включают встроенные утилиты кибербезопасности (такие как LinuxCmd для выполнения команд, WebSearch для сбора OSINT, Code для динамического выполнения скриптов и SSHTunnel для безопасного удаленного доступа), механизмы вызова функций, позволяющие интегрировать любую функцию Python как инструмент безопасности, и функциональность «агент-как-инструмент», которая позволяет использовать специализированных агентов безопасности (таких как агенты разведки или эксплуатации) другими агентами, создавая мощные совместные рабочие процессы без необходимости формальных передач между агентами. Для получения дополнительной информации, пожалуйста, обратитесь к [примеру здесь](https://github.com/aliasrobotics/cai/blob/main/examples/basic/tools.py) для полной конфигурации пользовательских функций.

```python
from cai.sdk.agents import Agent, Runner, OpenAIChatCompletionsModel
from cai.tools.reconnaissance.exec_code import execute_code
from cai.tools.reconnaissance.generic_linux_command import generic_linux_command

import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

agent = Agent(
      name="Custom Agent",
      instructions="""You are a Cybersecurity expert Leader""",
      tools= [
        generic_linux_command,
        execute_code
      ],
      model=OpenAIChatCompletionsModel(
          model=os.getenv('CAI_MODEL', "openai/gpt-4o"),
          openai_client=AsyncOpenAI(),
          )
      )

message = "Tell me about recursion in programming."
result = await Runner.run(agent, message)
```

Вы можете найти различные [инструменты](tools). Они сгруппированы в 6 основных категорий, вдохновленных цепочкой кибер-атак (security kill chain) [^2]:

1. Разведка и подготовка оружия (Reconnaissance and weaponization) - *reconnaissance* (криптография, листинг и т.д.)
2. Эксплуатация (Exploitation) - *exploitation*
3. Повышение привилегий (Privilege escalation) - *escalation*
4. Горизонтальное перемещение (Lateral movement) - *lateral*
5. Эксфильтрация данных (Data exfiltration) - *exfiltration*
6. Командный центр (Command and control) - *control*

### 🔹 Передачи (Handoffs)

`Handoffs` (Передачи) позволяют одному `Агенту` делегировать задачи другому агенту, что крайне важно в операциях кибербезопасности, где на разных этапах требуется специализированный опыт. В нашем фреймворке `Handoffs` реализованы как инструменты для LLM, где **функция передачи/трансфера**, такая как `transfer_to_flag_discriminator`, позволяет `ctf_agent` передать управление `flag_discriminator_agent`, как только он решит, что нашел флаг. Это создает цепочку валидации безопасности, где первый агент занимается эксплуатацией и поиском флага, а второй специализируется на проверке флага, обеспечивая надлежащее разделение обязанностей и используя специализированные возможности различных моделей для разных задач безопасности. Для получения дополнительной информации, пожалуйста, обратитесь к [примеру здесь](https://github.com/aliasrobotics/cai/blob/main/examples/cai/agent_patterns/handoffs.py) для ознакомления с полным кодом выполнения.

```python
from cai.sdk.agents import function_tool
from cai.tools.common import run_command
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel, HandoffInputData, Runner, function_tool, handoff, trace
from cai.sdk.agents.extensions import handoff_filters

import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

@function_tool
def execute_cli_command(command: str) -> str:
    return run_command(command)

flag_discriminator = Agent(
    name="Flag discriminator",
    description="Agent focused on extracting the flag from the output",
    instructions="You are an agent tailored to extract the flag from a given output.",
    model=OpenAIChatCompletionsModel(
        model=os.getenv('CAI_MODEL', "qwen2.5:14b"),
        openai_client=AsyncOpenAI(),
    ) 
)

ctf_agent = Agent(
    name="CTF agent",
    description="Agent focused on conquering security challenges",
    instructions="You are a Cybersecurity expert Leader facing a CTF",
    tools=[
        execute_cli_command,
    ],
    model=OpenAIChatCompletionsModel(
        model= os.getenv('CAI_MODEL', "qwen2.5:14b"),
        openai_client=AsyncOpenAI(),
    ), 
    handoffs = [flag_discriminator]
)
```

### 🔹 Паттерны

Агентский `Pattern` (Паттерн) — это *структурированная парадигма проектирования* в системах искусственного интеллекта, где автономные или полуавтономные агенты работают в рамках определенного *фреймворка взаимодействия* (паттерна) для достижения цели. Эти `Паттерны` определяют методы организации, координации и коммуникации между агентами, направляя процесс принятия решений, выполнения задач и делегирования.

Агентский паттерн (`AP`) может быть формально определен как кортеж:

\\[
AP = (A, H, D, C, E)
\\]

где:

- **\\(A\\) (Agents):** Набор автономных сущностей, \\( A = \\{a_1, a_2, ..., a_n\\} \\), каждая из которых имеет определенные роли, возможности и внутренние состояния.
- **\\(H\\) (Handoffs):** Функция \\( H: A \times T \to A \\), которая определяет, как задачи \\( T \\) передаются между агентами на основе предопределенной логики (например, правил, переговоров, торгов).
- **\\(D\\) (Decision Mechanism):** Функция принятия решения \\( D: S \to A \\), где \\( S \\) представляет состояния системы, а \\( D \\) определяет, какой агент предпринимает действие в любой given момент времени.
- **\\(C\\) (Communication Protocol):** Функция обмена сообщениями \\( C: A \times A \to M \\), где \\( M \\) — пространство сообщений, определяющее, как агенты обмениваются информацией.
- **\\(E\\) (Execution Model):** Функция \\( E: A \times I \to O \\), где \\( I \\) — пространство входных данных, а \\( O \\) — пространство выходных данных, определяющая, как агенты выполняют задачи.

При создании `Паттернов` мы обычно классифицируем их по одной из следующих категорий, хотя существуют и другие:

| **Категории агентских** `Паттернов` | **Описание** |
|--------------------|------------------------|
| `Swarm` (Децентрализованный) | Агенты разделяют задачи и самостоятельно распределяют обязанности без центрального оркестратора. Передачи происходят динамически. *Примером peer-to-peer агентского паттерна является `CTF Agentic Pattern`, который предполагает работу команды агентов вместе для решения CTF-задачи с динамическими передачами.* |
| `Hierarchical` (Иерархический) | Агент верхнего уровня (например, "PlannerAgent") назначает задачи через структурированные передачи специализированным субагентам. В качестве альтернативы структура агентов жестко закодирована в агентском паттерне с предопределенными передачами. |
| `Chain-of-Thought` (Последовательный рабочий процесс) | Структурированный конвейер, где Агент А создает вывод, передает его Агенту Б для повторного использования или уточнения и так далее. Передачи следуют линейной последовательности. *Примером паттерна chain-of-thought является `ReasonerAgent`, который задействует LLM типа Reasoning, предоставляющую контекст основному агенту для решения CTF-задачи в линейной последовательности.*[^1] |
| `Auction-Based` (Конкурентное распределение) | Агенты «торгуются» за задачи на основе приоритета, возможностей или стоимости. Агент принятия решений оценивает заявки и передает задачи наиболее подходящему агенту. |
| `Recursive` (Рекурсивный) | Один агент постоянно уточняет собственный вывод, выступая одновременно и исполнителем, и оценщиком, с передачами (внутренними или внешними) самому себе. *Примером рекурсивного агентского паттерна является `CodeAgent` (при использовании в качестве рекурсивного агента), который постоянно уточняет собственный вывод, выполняя код и обновляя свои инструкции.* |

Для получения дополнительной информации и примеров распространенных агентских паттернов см. [папку с примерами](https://github.com/aliasrobotics/cai/blob/main/examples/agent_patterns/README.md).

### 🔹 Ходы и взаимодействия
Во время агентского потока (разговора) мы различаем **взаимодействия** и **ходы**.

- **Взаимодействия (Interactions)** — это последовательные обмены между одним или несколькими агентами. Каждое выполнение логики агента соответствует одному *взаимодействию*. Поскольку `Агент` в CAI обычно реализует модель агента `ReACT`[^3], каждое *взаимодействие* состоит из 1) шага рассуждения через инференс LLM и 2) действия путем вызова от нуля до n `Инструментов`. Это определено в `process_interaction()` в [core.py](cai/core.py).
- **Ходы (Turns)**: Ход представляет собой цикл из одного или нескольких **взаимодействий**, который завершается, когда выполняющий `Агент` (или `Паттерн`) возвращает `None`, полагая, что дальнейших действий предпринимать не нужно. Это определено в `run()`, см. [core.py](cai/core.py).

> [!NOTE]
> Агенты CAI не связаны с Assistants в Assistants API. Они названы похоже для удобства, но в остальном совершенно не связаны. CAI полностью работает на Chat Completions API и, следовательно, не имеет состояния (stateless) между вызовами.

### 🔹 Трассировка

CAI реализует наблюдаемость ИИ, принимая стандарт OpenTelemetry, и для этого использует [Phoenix](https://github.com/Arize-ai/phoenix), который предоставляет комплексные возможности трассировки через инструментарий на базе OpenTelemetry, позволяя вам мониторить и анализировать ваши операции безопасности в режиме реального времени. Эта интеграция обеспечивает детальную видимость взаимодействий агентов, использования инструментов и векторов атак на протяжении всего процесса пентеста, что облегчает отладку сложных цепочек эксплуатации, отслеживание процессов поиска уязвимостей и оптимизацию производительности агентов для более эффективной оценки безопасности.

![](media/tracing.png)

### 🔹 Защитные барьеры (Guardrails)

`Guardrails` обеспечивают критический слой безопасности для агентов CAI, защищая от атак с инъекцией промптов и предотвращая выполнение опасных команд. Эти барьеры работают параллельно с агентами, валидируя как входные, так и выходные данные для обеспечения безопасной работы. Фреймворк включает:

- **Входные барьеры (Input Guardrails)**: Обнаруживают и блокируют попытки инъекции промптов до того, как они достигнут агентов, используя сопоставление с паттернами, обнаружение Unicode-омографов и анализ на базе ИИ.
- **Выходные барьеры (Output Guardrails)**: Валидируют выводы агентов перед выполнением, предотвращая опасные команды, такие как reverse shells, fork bombs или эксфильтрация данных.
- **Многослойная защита**: Защита на этапах ввода, обработки и выполнения с валидацией на уровне инструментов.
- **Поддержка Base64/Base32**: Автоматически декодирует и анализирует закодированные полезные нагрузки для обнаружения скрытых вредоносных команд.
- **Настраиваемость**: Могут быть включены/выключены через переменную окружения `CAI_GUARDRAILS`.

Для подробного описания реализации см. [docs/guardrails.md](docs/guardrails.md) и [docs/cai_prompt_injection.md](docs/cai_prompt_injection.md).

### 🔹 Человек в контуре (HITL)

```
                      ┌─────────────────────────────────┐
                      │                                 │
                      │      Cybersecurity AI (CAI)     │
                      │                                 │
                      │       ┌─────────────────┐       │
                      │       │  Autonomous AI  │       │
                      │       └────────┬────────┘       │
                      │                │                │
                      │                │                │
                      │       ┌────────▼─────────┐      │
                      │       │ HITL Interaction │      │
                      │       └────────┬─────────┘      │
                      │                │                │
                      └────────────────┼────────────────┘
                                       │
                                       │ Ctrl+C (cli.py)
                                       │
                           ┌───────────▼───────────┐
                           │   Human Operator(s)   │
                           │  Expertise | Judgment │
                           │    Teleoperation      │
                           └───────────────────────┘
```

CAI предоставляет фреймворк для создания ИИ в кибербезопасности с сильным акцентом на *полуавтономную* работу, так как реальность такова, что **полностью автономные** системы кибербезопасности всё ещё преждевременны и сталкиваются со значительными трудностями при решении сложных задач. Хотя CAI исследует автономные возможности, мы признаем, что эффективные операции безопасности по-прежнему требуют человеческого телеуправления, обеспечивающего экспертизу, суждение и надзор в процессе безопасности.

Соответственно, модуль Human-In-The-Loop (`HITL`) является основным принципом проектирования CAI, признающим, что человеческое вмешательство и телеуправление являются важными компонентами ответственного тестирования безопасности. Через интерфейс `cli.py` пользователи могут беспрепятственно взаимодействовать с агентами в любой момент выполнения, просто нажав `Ctrl+C`. Это реализовано в [core.py](cai/core.py), а также в абстракциях REPL [REPL](cai/repl).

## :rocket: Быстрый старт

Чтобы запустить CAI после установки, просто введите `cai` в CLI:

```bash
└─# cai

          CCCCCCCCCCCCC      ++++++++   ++++++++      IIIIIIIIII
       CCC::::::::::::C  ++++++++++       ++++++++++  I::::::::I
     CC:::::::::::::::C ++++++++++         ++++++++++ I::::::::I
    C:::::CCCCCCCC::::C +++++++++    ++     +++++++++ II::::::II
   C:::::C       CCCCCC +++++++     +++++     +++++++   I::::I
  C:::::C                +++++     +++++++     +++++    I::::I
  C:::::C                ++++                   ++++    I::::I
  C:::::C                 ++                     ++     I::::I
  C:::::C                  +   +++++++++++++++   +      I::::I
  C:::::C                    +++++++++++++++++++        I::::I
  C:::::C                     +++++++++++++++++         I::::I
   C:::::C       CCCCCC        +++++++++++++++          I::::I
    C:::::CCCCCCCC::::C         +++++++++++++         II::::::II
     CC:::::::::::::::C           +++++++++           I::::::::I
       CCC::::::::::::C             +++++             I::::::::I
          CCCCCCCCCCCCC               ++              IIIIIIIIII

                      Cybersecurity AI (CAI), vX.Y.Z
                          Bug bounty-ready AI

CAI>
```

Это должно инициализировать CAI и предоставить промпт для выполнения любой задачи по безопасности, которую вы хотите осуществить. Панель навигации внизу отображает важную системную информацию. Эта информация помогает вам понимать ваше окружение при работе с CAI.

Вот короткое [демо-видео](https://asciinema.org/a/zm7wS5DA2o0S9pu1Tb44pnlvy), которое поможет вам начать работу с CAI. Мы пройдем по базовым шагам — от запуска инструмента до выполнения вашей первой задачи на базе ИИ в терминале. Независимо от того, новичок вы или просто любопытствуете, этот гид покажет, как легко начать использовать CAI.

Теперь вводите команды в `CAI` и начинайте свои упражнения по безопасности. Лучший способ обучения — на примерах:

### Переменные окружения
Для использования приватных моделей вам предоставлен файл [`.env.example`](.env.example). Скопируйте его и переименуйте в `.env`. Заполните соответствующие API-ключи, и вы готовы к использованию CAI.
 
 Список переменных окружения 

| Переменная | Описание |
|----------|-------------|
| CTF_NAME | Название CTF-челленджа для запуска (например, "picoctf_static_flag") |
| CTF_CHALLENGE | Конкретное название задания внутри CTF для тестирования |
| CTF_SUBNET | Сетевая подсеть для CTF-контейнера |
| CTF_IP | IP-адрес CTF-контейнера |
| CTF_INSIDE | Нужно ли захватывать CTF изнутри контейнера |
| CAI_MODEL | Модель для использования агентами |
| CAI_DEBUG | Уровень отладочного вывода (0: Только вывод инструментов, 1: Подробный вывод отладки, 2: Отладка CLI) |
| CAI_BRIEF | Включить/выключить краткий режим вывода |
| CAI_MAX_TURNS | Максимальное количество ходов для взаимодействий агентов |
| CAI_TRACING | Включить/выключить трассировку OpenTelemetry |
| CAI_AGENT_TYPE | Указать тип агентов для использования (boot2root, one_tool...) |
| CAI_STATE | Включить/выключить режим с сохранением состояния (stateful) |
| CAI_MEMORY | Включить/выключить режим памяти (episodic, semantic, all) |
| CAI_MEMORY_ONLINE | Включить/выключить онлайн-режим памяти |
| CAI_MEMORY_OFFLINE | Включить/выключить офлайн-память |
| CAI_ENV_CONTEXT | Добавить директории и текущее окружение в контекст LLM |
| CAI_MEMORY_ONLINE_INTERVAL | Количество ходов между обновлениями онлайн-памяти |
| CAI_PRICE_LIMIT | Лимит стоимости разговора в долларах |
| CAI_REPORT | Включить/выключить режим репортера (ctf, nis2, pentesting) |
| CAI_SUPPORT_MODEL | Модель для использования агентом поддержки |
| CAI_SUPPORT_INTERVAL | Количество ходов между запусками агента поддержки |
| CAI_WORKSPACE | Определяет имя рабочего пространства |
| CAI_WORKSPACE_DIR | Указывает путь к директории, где находится рабочее пространство |
| CAI_GUARDRAILS | Включить/выключить защитные барьеры для защиты от инъекций промптов (по умолчанию: true) |

 

### Интеграция с OpenRouter

Платформа Cybersecurity AI (CAI) предлагает бесшовную интеграцию с OpenRouter, унифицированным интерфейсом для больших языковых моделей (LLM). Эта интеграция крайне важна для пользователей, которые хотят использовать продвинутые возможности ИИ в своих задачах кибербезопасности. OpenRouter выступает в качестве моста, позволяя CAI взаимодействовать с различными LLM, тем самым расширяя гибкость и мощность ИИ-агентов, используемых в CAI.

Чтобы включить поддержку OpenRouter в CAI, вам нужно настроить окружение, добавив определенные записи в ваш файл `.env`. Эта настройка гарантирует, что CAI сможет взаимодействовать с API OpenRouter, облегчая использование сложных моделей, таких как Meta-LLaMA. Вот как вы можете это настроить:

```bash
CAI_AGENT_TYPE=redteam_agent
CAI_MODEL=openrouter/meta-llama/llama-4-maverick
OPENROUTER_API_KEY=<sk-your-key>  # примечание: добавьте свой ключ
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

### Azure OpenAI

Платформа Cybersecurity AI (CAI) бесшовно интегрируется с Azure OpenAI, позволяя организациям запускать CAI на моделях, размещенных в корпоративной среде (например, gpt-4o). Этот путь идеален для команд, которые должны работать в рамках управления Azure, используя при этом продвинутые возможности моделей.
Чтобы включить поддержку Azure OpenAI в CAI, настройте окружение, добавив следующие записи в ваш .env. Это гарантирует, что CAI сможет связаться с вашим эндпоинтом развертывания Azure и правильно пройти аутентификацию.

```bash
CAI_AGENT_TYPE=redteam_agent
CAI_MODEL=azure/<model-name-deployed>
# Обязательно: оставить не пустым даже при использовании Azure
OPENAI_API_KEY=dummy
# Учетные данные и эндпоинт Azure
AZURE_API_KEY=<your-azure-openai-key>
AZURE_API_BASE=https://<resource>.openai.azure.com/openai/deployments/<deployment-name>/chat/completions?api-version=2025-01-01-preview
```

### MCP

CAI поддерживает Model Context Protocol (MCP) для интеграции внешних инструментов и сервисов с ИИ-агентами. MCP поддерживается через два механизма транспорта:

1. **SSE (Server-Sent Events)** - Для веб-серверов, которые отправляют обновления через HTTP-соединения:
```bash
CAI>/mcp load http://localhost:9876/sse burp
```

2. **STDIO (Standard Input/Output)** - Для локального межпроцессного взаимодействия:
```bash
CAI>/mcp load stdio myserver python mcp_server.py
```

После подключения вы можете добавить инструменты MCP любому агенту:
```bash
CAI>/mcp add burp redteam_agent
Adding tools from MCP server 'burp' to agent 'Red Team Agent'...
                                 Adding tools to Red Team Agent
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Tool                              ┃ Status ┃ Details                                         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ send_http_request                 │ Added  │ Available as: send_http_request                 │
│ create_repeater_tab               │ Added  │ Available as: create_repeater_tab               │
│ send_to_intruder                  │ Added  │ Available as: send_to_intruder                  │
│ url_encode                        │ Added  │ Available as: url_encode                        │
│ url_decode                        │ Added  │ Available as: url_decode                        │
│ base64encode                      │ Added  │ Available as: base64encode                      │
│ base64decode                      │ Added  │ Available as: base64decode                      │
│ generate_random_string            │ Added  │ Available as: generate_random_string            │
│ output_project_options            │ Added  │ Available as: output_project_options            │
│ output_user_options               │ Added  │ Available as: output_user_options               │
│ set_project_options               │ Added  │ Available as: set_project_options               │
│ set_user_options                  │ Added  │ Available as: set_user_options                  │
│ get_proxy_http_history            │ Added  │ Available as: get_proxy_http_history            │
│ get_proxy_http_history_regex      │ Added  │ Available as: get_proxy_http_history_regex      │
│ get_proxy_websocket_history       │ Added  │ Available as: get_proxy_websocket_history       │
│ get_proxy_websocket_history_regex │ Added  │ Available as: get_proxy_websocket_history_regex │
│ set_task_execution_engine_state   │ Added  │ Available as: set_task_execution_engine_state   │
│ set_proxy_intercept_state         │ Added  │ Available as: set_proxy_intercept_state         │
│ get_active_editor_contents        │ Added  │ Available as: get_active_editor_contents        │
│ set_active_editor_contents        │ Added  │ Available as: set_active_editor_contents        │
└───────────────────────────────────┴────────┴─────────────────────────────────────────────────┘
Added 20 tools from server 'burp' to agent 'Red Team Agent'.
CAI>/agent 13
CAI>Create a repeater tab
```

Вы можете вывести список всех активных MCP-соединений и их типов транспорта:
```bash
CAI>/mcp list
```

https://github.com/user-attachments/assets/386a1fd3-3469-4f84-9396-2a5236febe1f

## Разработка

Разработка упрощена с помощью dev-окружений VS Code. Чтобы попробовать наше окружение разработки, клонируйте репозиторий, откройте VS Code и перейдите в режим dev-контейнера:

![CAI Development Environment](media/cai_devenv.gif)

### Вклад в проект

Если вы хотите внести вклад в этот проект, используйте [**Pre-commit**](https://pre-commit.com/) перед созданием MR.

```bash
pip install pre-commit
pre-commit # для подготовленных файлов
pre-commit run --all-files # для всех файлов
```

### Дополнительные требования: caiextensions

В настоящее время расширения недоступны публично, так как инженерные затраты на их поддержку значительны. Вместо этого мы предоставляем выбранные кастомные caiextensions компаниям-партнерам в рамках сотрудничества.

### :information_source: Сбор данных об использовании

CAI предоставляется бесплатно для исследователей. Чтобы улучшить точность обнаружения CAI, продвинуть открытые исследования безопасности, а также разрабатывать и обучать будущие модели, мы просим вас внести вклад в сообщество CAI, разрешив сбор данных об использовании. Эти данные помогают нам выявлять области для улучшения, понимать, как используется фреймворк, расставлять приоритеты для новых функций, а также поддерживать усилия по обучению и оценке моделей.

Правовым основанием для сбора данных является ст. 6 (1)(f) GDPR — законный интерес CAI в поддержке, улучшении и развитии инструментов и исследований безопасности — с применением мер защиты согласно ст. 89 для исследовательских целей.

Собираемые данные включают:

- Базовую системную информацию (тип ОС, версия Python)
- Имя пользователя и информацию об IP
- Паттерны использования инструментов и метрики производительности
- Взаимодействия с моделями и статистику использования токенов

Мы серьезно относимся к вашей конфиденциальности и собираем только то, что необходимо для улучшения CAI, поддержки исследований, а также ответственного обучения и оценки моделей. Для получения дополнительной информации свяжитесь с research＠aliasrobotics.com. Вы можете отключить некоторые функции сбора данных через переменную окружения `CAI_TELEMETRY`, хотя мы рекомендуем оставить её включенной, чтобы внести вклад в текущие исследования и разработку моделей:

```bash
CAI_TELEMETRY=False cai
```

### Воспроизведение CI-настройки локально

Чтобы симулировать CI/CD конвейер, вы можете запустить следующее на машинах Gitlab runner:

```bash
docker run --rm -it \
  --privileged \
  --network=exploitflow_net \
  --add-host="host.docker.internal:host-gateway" \
  -v /cache:/cache \
  -v /var/run/docker.sock:/var/run/docker.sock:rw \
  registry.gitlab.com/aliasrobotics/alias_research/cai:latest bash
```

## FAQ
 OLLAMA выдает ошибки 404 

API Ollama в режиме OpenAI использует `/v1/chat/completions`, в то время как библиотека `openai` использует `base_url` + `/chat/completions`.

Мы придерживаемся последнего варианта для общего соответствия сообществу gen AI и поддерживаем первый вариант, позволяя пользователям самостоятельно добавлять `v1` через:

```bash
OLLAMA_API_BASE=http://IP:PORT/v1
```

Подробнее об этом в следующих issue:
- https://github.com/aliasrobotics/cai/issues/76
- https://github.com/aliasrobotics/cai/issues/83
- https://github.com/aliasrobotics/cai/issues/82

 

 Где найти все caiextensions? 

См. [все caiextensions](https://gitlab.com/aliasrobotics/alias_research/caiextensions)

 

 Как установить расширение report caiextension? 

[См. здесь](#optional-requirements-caiextensions)
 

 Как настроить SSH-доступ для Gitlab? 

Сгенерируйте новый SSH-ключ
```bash
ssh-keygen -t ed25519
```

Добавьте ключ в SSH-агент
```bash
ssh-add ~/.ssh/id_ed25519
```

Добавьте публичный ключ в Gitlab
Скопируйте ключ и добавьте его в Gitlab по адресу https://gitlab.com/-/user_settings/ssh_keys
```bash
cat ~/.ssh/id_ed25519.pub
```

Для проверки:
```bash
ssh -T git@gitlab.com
Welcome to GitLab, @vmayoral!
```

 

 Как очистить кэш Python? 

```bash
find . -name "*.pyc" -delete && find . -name "__pycache__" -delete
```

 

 Если сетевое взаимодействие с хостом не работает с ollama, проверьте, не было ли оно отключено в Docker из-за того, что вы не авторизованы 

Docker в OS X иногда ведет себя странно. Проверьте, появилось ли следующее сообщение:

*Host networking has been disabled because you are not signed in. Please sign in to enable it*.

Убедитесь, что эта проблема решена, а также что Dev Container не перенаправляет порт 8000 (при необходимости нажмите x в разделе портов).

Для проверки соединения изнутри VSCode devcontainer:
```bash
curl -v http://host.docker.internal:8000/api/version
```

 
 Запуск CAI против любой цели 

![cai-004-first-message](imgs/readme_imgs/cai-004-first-message.png)

Начальный пользовательский промпт в данном случае: `Target IP: 192.168.3.10, perform a full network scan`.

Агент начал выполнять сканирование nmap. Вы можете либо взаимодействовать с агентом и давать ему дополнительные инструкции, либо дать ему работать дальше, чтобы увидеть, что он исследует.
 

 
 Как взаимодействовать с агентом? Нажмите дважды CTRL + C 

![cai-005-ctrl-c](imgs/readme_imgs/cai-005-ctrl-c.png)

Если вы хотите использовать режим HITL, вы можете сделать это, нажав дважды ```Ctrl + C```.
Это позволит вам взаимодействовать (через промпт) с агентом в любой момент. Агент не потеряет предыдущий контекст, так как он хранится в переменной `history`, которая передается ему и любому вызываемому агенту. Это позволяет любому агенту использовать предыдущую информацию, быть более точным и эффективным.
 

 
 Можно ли сменить модель во время работы CAI? /model 

Используйте ```/model``` для смены модели.

![cai-007-model-change](imgs/readme_imgs/cai-007-model-change.png)

 

 
 Как вывести список всех доступных агентов? /agent 

Используйте ```/agent``` для вывода списка всех доступных агентов.

![cai-010-agents-menu](imgs/readme_imgs/cai-010-agents-menu.png)

 

 
 Где можно посмотреть все переменные окружения? /env 

![cai-008-config](imgs/readme_imgs/cai-008-config.png)
 

 
 Как отслеживать использование токенов и затраты? 

Используйте **`/cost`** в REPL для статистики расходов сессии и токенов, **`/compact`**, когда разговоры становятся слишком длинными, и (в режиме **TUI**) индикаторы стоимости и модели для каждого терминала в интерфейсе.

```bash
CAI> /cost
```

Полный список команд см. в [справочнике команд CLI](docs/cli/commands_reference.md).
 

 
 Как узнать больше о CLI? /help 

![cai-006-help](imgs/readme_imgs/cai-006-help.png)
 

 
 Как проследить за всем выполнением? 
Переменная окружения `CAI_TRACING` позволяет пользователю установить `CAI_TRACING=true` для включения трассировки или `CAI_TRACING=false` для её отключения.
Когда CAI запускается в первый раз, пользователю предоставляются два пути: лог выполнения и лог трассировки.

![cai-009-logs](imgs/readme_imgs/cai-009-logs.png)

 

 
 Можно ли расширить возможности CAI, используя логи предыдущих запусков? 

Да. На сегодняшний день CAI работает лучше всего, опираясь на обучение в контексте (In‑Context Learning, ICL). Вместо создания долгосрочных хранилищ рекомендуется загружать соответствующие предыдущие логи напрямую в текущую сессию, чтобы модель могла рассуждать с ними в контексте.

Используйте команду `/load`, чтобы добавить JSONL-логи в контекст CAI (это заменяет устаревший инструмент загрузки памяти):

```bash
CAI>/load logs/cai_20250408_111856.jsonl         # Загрузить в текущего агента
CAI>/load <file> agent <name>                    # Загрузить в конкретного агента
CAI>/load <file> all                             # Распределить между всеми агентами
CAI>/load <file> parallel                        # Сопоставить с настроенными параллельными агентами
# Совет: если вы опустите <file>, /load использует `logs/last`. Алиас: /l
```

CAI выводит путь к JSONL-логу текущего запуска при старте (выделено оранжевым), который вы можете передать в `/load`:

![cai-009-logs](imgs/readme_imgs/cai-009-logs.png)

Устаревшие примечания: более ранние механизмы «расширения памяти» (эпизодические/семантические хранилища и офлайн-инъекции) сохранены только для справки. См. [src/cai/agents/memory.py](src/cai/agents/memory.py) для получения информации о бэкграунде и устаревших деталях. Наше текущее направление отдает приоритет ICL перед постоянной памятью.

 

 
 Можно ли расширить возможности CAI с помощью скриптов или дополнительной информации? 

В настоящее время CAI поддерживает текстовую информацию. Вы можете добавить любую дополнительную информацию о цели, с которой работаете, просто скопировав и вставив её напрямую в системный или пользовательский промпт.

**Как?** Добавив её в системный ([`system_master_template.md`](cai/repl/templates/system_master_template.md)) или пользовательский промпт ([`user_master_template.md`](cai/repl/templates/user_master_template.md)). Вы всегда можете напрямую указать путь к файлу в промпте модели, и она выполнит ```cat```.
 

 Как работает лицензия CAI? 

Текущая лицензия CAI не ограничивает использование в исследовательских целях. Вы можете свободно использовать CAI для оценки безопасности (пентестов), разработки дополнительных функций и интеграции в свою исследовательскую деятельность, при условии соблюдения местных законов.

Если вы или ваша организация начнете получать коммерческую выгоду от CAI (например, предлагать услуги пентеста на базе CAI), потребуется коммерческая лицензия, чтобы помочь поддерживать проект.

Сам по себе CAI не является коммерческой инициативой. Наша цель — создать устойчивый open-source проект. Мы просто просим тех, кто извлекает прибыль из CAI, вносить свой вклад и поддерживать нашу текущую разработку.

 

 Я получаю ошибку `Unable to locate package python3.12-venv` при установке зависимостей в моей системе на базе debian! 

Самый простой способ обойти это — просто установить [`python3.12`](https://www.python.org/downloads/release/python-3120/) из исходного кода.

 

## Цитирование

Если вы хотите процитировать нашу работу, пожалуйста, используйте следующее (в порядке даты публикации):

```bibtex
@article{mayoral2025cai,
  title={CAI: An Open, Bug Bounty-Ready Cybersecurity AI},
  author={Mayoral-Vilches, V{\'\i}ctor and Navarrete-Lozano, Luis Javier and Sanz-G{\'o}mez, Mar{\'\i}a and Espejo, Lidia Salas and Crespo-{\'A}lvarez, Marti{\~n}o and Oca-Gonzalez, Francisco and Balassone, Francesco and Glera-Pic{\'o}n, Alfonso and Ayucar-Carbajo, Unai and Ruiz-Alcalde, Jon Ander and Rass, Stefan and Pinzger, Martin and Gil-Uriarte, Endika},
  journal={arXiv preprint arXiv:2504.06017},
  year={2025}
}

@article{mayoral2025automation,
  title={Cybersecurity AI: The Dangerous Gap Between Automation and Autonomy},
  author={Mayoral-Vilches, V{\'\i}ctor},
  journal={arXiv preprint arXiv:2506.23592},
  year={2025}
}

@article{mayoral2025fluency,
  title={CAI Fluency: A Framework for Cybersecurity AI Fluency},
  author={Mayoral-Vilches, V{\'\i}ctor and Wachter, Jasmin and Chavez, Crist{\'o}bal RJ and Schachner, Cathrin and Navarrete-Lozano, Luis Javier and Sanz-G{\'o}mez, Mar{\'\i}a},
  journal={arXiv preprint arXiv:2508.13588},
  year={2025}
}

@article{mayoral2025hacking,
  title={Cybersecurity AI: Hacking the AI Hackers via Prompt Injection},
  author={Mayoral-Vilches, V{\'\i}ctor and Rynning, Per Mannermaa},
  journal={arXiv preprint arXiv:2508.21669},
  year={2025}
}

@article{mayoral2025humanoid,
  title={Cybersecurity AI: Humanoid Robots as Attack Vectors},
  author={Mayoral-Vilches, V{\'\i}ctor},
  journal={arXiv preprint arXiv:2509.14139},
  year={2025}
}

@article{balassone2025evaluation,
  title={Cybersecurity AI: Evaluating Agentic Cybersecurity in Attack/Defense CTFs},
  author={Balassone, Francesco and Mayoral-Vilches, V{\'\i}ctor and Rass, Stefan and Pinzger, Martin and Perrone, Gaetano and Romano, Simon Pietro and Schartner, Peter},
  journal={arXiv preprint arXiv:2510.17521},
  year={2025}
}

@article{mayoral2025caibench,
  title={CAIBench: A Meta-Benchmark for Evaluating Cybersecurity AI Agents},
  author={Mayoral-Vilches, V{\'\i}ctor and Balassone, Francesco and Navarrete-Lozano, Luis Javier and Sanz-G{\'o}mez, Mar{\'\i}a and Crespo-{\'A}lvarez, Marti{\~n}o and Rass, Stefan and Pinzger, Martin},
  journal={arXiv preprint arXiv:2510.24317},
  year={2025}
}
```

## Благодарности

CAI был первоначально разработан [Alias Robotics](https://aliasrobotics.com) и софинансирован европейским проектом EIC accelerator RIS (GA 101161136) — конкурс HORIZON-EIC-2023-ACCELERATOR-01. Оригинальные агентские принципы вдохновлены библиотекой [`swarm`](https://github.com/openai/swarm) от OpenAI и перенесены в новые прототипы. Этот проект также использует другие соответствующие open-source блоки, включая [`LiteLLM`](https://github.com/BerriAI/litellm) и [`phoenix`](https://github.com/Arize-ai/phoenix).

### Академическое сотрудничество
CAI извлекает выгоду из текущего исследовательского сотрудничества с академическими институтами. Исследователи, заинтересованные в совместных проектах, доступе к наборам данных или академических лицензиях, должны связаться с research@aliasrobotics.com. Мы предоставляем специальную поддержку для:
- Исследовательских проектов PhD
- Академических бенчмарк-исследований 
- Инициатив в области образования по безопасности
- Open-source вкладов от исследовательских лабораторий

 
[^1]: Можно утверждать, что агентский паттерн Chain-of-Thought является частным случаем иерархического агентского паттерна.
[^2]: Kamhoua, C. A., Leslie, N. O., & Weisman, M. J. (2018). Game theoretic modeling of advanced persistent threat in internet of things. Journal of Cyber Security and Information Systems.
[^3]: Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023, January). React: Synergizing reasoning and acting in language models. In International Conference on Learning Representations (ICLR).
[^4]: Deng, G., Liu, Y., Mayoral-Vilches, V., Liu, P., Li, Y., Xu, Y., ... & Rass, S. (2024). {PentestGPT}: Evaluating and harnessing large language models for automated penetration testing. In 33rd USENIX Security Symposium (USENIX Security 24) (pp. 847-864).