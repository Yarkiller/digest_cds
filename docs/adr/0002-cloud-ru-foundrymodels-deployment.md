# Развёртывание на Cloud.ru и обработка через FoundryModels

Сервис Digest CDS разворачивается на виртуальной машине Cloud.ru. Обработка внешнего контента (транскрибация YouTube, суммаризация, тегирование, эмбеддинги для поиска) выполняется через API FoundryModels Cloud.ru — не через публичные зарубежные API и не локальный Whisper на VM.

**Considered Options:** (A) Whisper on-prem; (B) публичные облачные API; (C) Cloud.ru VM + FoundryModels.

**Consequences:** весь стек и секреты живут в контуре Cloud.ru; зависимость от доступности FoundryModels; при смене провайдера потребуется адаптер для ML-pipeline.
