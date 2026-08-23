# PostgreSQL на той же VM через Docker Compose

База данных — PostgreSQL с pgvector, развёрнута на той же виртуальной машине Cloud.ru, что и приложение, через Docker Compose. Managed PostgreSQL Cloud.ru не используем.

**Considered Options:** (A) PostgreSQL в Docker Compose на VM; (B) Managed PostgreSQL Cloud.ru.

**Consequences:** один контур деплоя и меньше зависимостей от managed-сервисов; ответственность за бэкапы, обновления и отказоустойчивость БД лежит на команде; масштабирование БД отдельно от приложения сложнее.
