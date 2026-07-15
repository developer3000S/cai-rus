# Трассировка

Так же, как и для [агентов](../tracing.md), голосовые конвейеры также автоматически трассируются.

Вы можете прочитать документацию по трассировке выше для получения 기본ной информации, но вы также можете настроить трассировку конвейера через [`VoicePipelineConfig`][cai.sdk.agents.voice.pipeline_config.VoicePipelineConfig].

Ключевые поля, связанные с трассировкой:

-   [`tracing_disabled`][cai.sdk.agents.voice.pipeline_config.VoicePipelineConfig.tracing_disabled] — управляет тем, отключена ли трассировка. По умолчанию трассировка включена.
-   [`trace_include_sensitive_data`][cai.sdk.agents.voice.pipeline_config.VoicePipelineConfig.trace_include_sensitive_data] — управляет тем, включают ли трассировки потенциально конфиденциальные данные, такие как аудио транскрипции. Это specifically для голосового конвейера, а не для того, что происходит внутри вашего рабочего процесса.
-   [`trace_include_sensitive_audio_data`][cai.sdk.agents.voice.pipeline_config.VoicePipelineConfig.trace_include_sensitive_audio_data] — управляет тем, включают ли трассировки аудио данные.
-   [`workflow_name`][cai.sdk.agents.voice.pipeline_config.VoicePipelineConfig.workflow_name] — Имя рабочего процесса трассировки.
-   [`group_id`][cai.sdk.agents.voice.pipeline_config.VoicePipelineConfig.group_id] — `group_id` трассировки, который позволяет связывать несколько трассировок.
-   [`trace_metadata`][cai.sdk.agents.voice.pipeline_config.VoicePipelineConfig.tracing_disabled] — Дополнительные метаданные для включения в трассировку.
