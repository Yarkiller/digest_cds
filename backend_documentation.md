# Backend Digest CDS

Документ сдачи домашнего задания «Развертывание Backend и интеграция с Frontend».

Репозиторий: [https://github.com/Yarkiller/digest_cds](https://github.com/Yarkiller/digest_cds)  
Ветка: `research/otus-assignment`

Рабочее приложение для приёмки: локальные FastAPI и Vite против уже развёрнутой БД. Пошаговый запуск — [`docs/agents/local-platform-runbook.md`](docs/agents/local-platform-runbook.md).

## Архитектура

Выбран **вариант B: self-hosted**. На отдельной VM работает Supabase (PostgreSQL, Auth, PostgREST, Studio) по адресу `https://knowledge-db.ru/`. Обоснование и отклонённые варианты (managed Supabase Cloud, голый PostgreSQL, managed PostgreSQL Cloud.ru) — в [`docs/adr/0004-self-hosted-supabase-on-vm.md`](docs/adr/0004-self-hosted-supabase-on-vm.md).

Приложение общается с этой БД через собственный HTTP API, а не через прямой доступ браузера к таблицам.

```text
web/ (Vite + React)
  ├─ Supabase JS: регистрация и вход (publishable key)
  └─ fetch → FastAPI (VITE_API_BASE_URL)
        backend/  domain → application (use cases, ports) → interface/http
        supabase-integration/  адаптер портов, service role только на сервере
        PostgreSQL + pgvector + RLS на VM
```

Секретный ключ Supabase живёт в серверном `.env`. Во фронт попадают только `VITE_SUPABASE_URL` и `VITE_SUPABASE_PUBLISHABLE_KEY`.

## Шаги задания

| Шаг | Где в репозитории |
|-----|-------------------|
| 1. Схема и миграции | [`supabase-integration/migrations/001_initial_schema.sql`](supabase-integration/migrations/001_initial_schema.sql) … `005_phase5_admin_shortlist.sql`. Сущности: `profiles`, ingestion (`ingestion_sources`, `ingestion_jobs`, `source_texts`), публикация (`materials`, `material_tags`, `material_relations`), выпуск (`digest_issues`, `digest_issue_items`, shortlist), `knowledge_chunks` (`vector(1024)`), голосование (`voting_cycles`, `topics`, `topic_materials`, `votes`), `razbors`, `activity_events`. `profiles.id` ссылается на `auth.users`. |
| 2. Инфраструктура | Self-hosted Supabase на VM. Выбор зафиксирован в ADR-0004. |
| 3. Развёртывание БД | Инстанс `https://knowledge-db.ru/` уже поднят. В репозитории: [`deploy/Dockerfile`](deploy/Dockerfile), [`deploy/docker-compose.yml`](deploy/docker-compose.yml), [`.env.example`](.env.example). Миграции применены через Studio SQL Editor. |
| 4. API | FastAPI, роутеры в [`backend/src/backend/interface/http/routes/`](backend/src/backend/interface/http/routes/). Ниже список операций; CRUD больше трёх. |
| 5. Безопасность | Supabase Auth, проверка JWT в [`backend/src/backend/interface/http/deps.py`](backend/src/backend/interface/http/deps.py), RLS в миграции `001`, CORS allowlist в [`backend/src/backend/interface/http/app.py`](backend/src/backend/interface/http/app.py), секреты в gitignored `.env`. |
| 6. Интеграция Frontend | Клиенты в [`web/src/services/`](web/src/services/) (`contentApi`, `votingApi`, `knowledgeApi`, `authApi`, `meApi`). При `VITE_USE_MOCKS=false` данные читаются и пишутся на сервер. |
| 7. Ошибки и логи | 400 / 401 / 403 / 404 / 409 / 422 / 503. JSON-лог `request_finished` в stdout ([`middleware.py`](backend/src/backend/interface/http/middleware.py)). |
| 8. Тесты | `uv run pytest` и Playwright `npm run test:web`. Контракты HTTP: `tests/unit/test_http_*.py`. |
| 9. Документация | Этот файл, README, runbook. |

## Инструкции по развёртыванию

### Уже работающая БД

База доступна по `https://knowledge-db.ru/`. Проверка Auth:

```bash
curl -s https://knowledge-db.ru/auth/v1/settings
```

Повторно применять миграции на общий инстанс не нужно. Канонический SQL — каталог `supabase-integration/migrations/`. Порядок: `001` … `005`. Описание таблиц и policies: [`supabase-integration/README.md`](supabase-integration/README.md).

### Postgres из репозитория

Образ — `supabase/postgres:17.6.1.136` (схема `auth`, роли, pgvector). Пароль задаётся снаружи.

```bash
# из корня репозитория, значение только в окружении
POSTGRES_PASSWORD='choose-a-local-password' docker compose -f deploy/docker-compose.yml up --build
```

Проверка:

```bash
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml exec db pg_isready -U postgres -h localhost
```

Порт слушает только `127.0.0.1:5432`. Имена `POSTGRES_PASSWORD` и `POSTGRES_DB` есть в [`.env.example`](.env.example); файл `.env` в git не коммитится.

### API и Frontend

1. Скопировать `.env.example` в `.env` и заполнить `SUPABASE_URL`, ключи, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_ISSUER`. Для живых адаптеров: `APP_CONTAINER=live`.
2. `API_CORS_ORIGINS` должен включать origin Vite (`http://127.0.0.1:5173` и `http://localhost:5173`).
3. Запуск API:

```bash
uv sync
uv run --env-file .env uvicorn backend.interface.http.app:create_default_app --factory --host 127.0.0.1 --port 8000
```

4. Для фронта создать `web/.env.local` (Vite читает env из `web/`, файл в gitignore):

```dotenv
VITE_SUPABASE_URL=https://knowledge-db.ru
VITE_SUPABASE_PUBLISHABLE_KEY=<publishable key>
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCKS=false
```

5. `npm install && npm install --prefix web && npm run dev`. Открыть [http://127.0.0.1:5173](http://127.0.0.1:5173), зарегистрироваться корпоративной почтой и пройти выпуск, голосование и базу знаний.

`VITE_USE_MOCKS=true` оставлен дефолтом для офлайн-тестов Playwright. Живая сдача использует `false`: после ошибки сети клиент не подменяет ответ моком.

## API

База: `http://127.0.0.1:8000`. Кроме `GET /health`, нужен заголовок `Authorization: Bearer <access_token>`. Токен выдаёт Supabase Auth после входа.

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/health` | Живость процесса, без авторизации. Тело: `{"status":"ok"}`. |
| GET | `/me` | Текущий профиль. |
| PATCH | `/me` | Обновить `display_name` (1…120 символов). |
| POST | `/me/ping` | Записать `activity_events`. |
| GET | `/issues/current` | Текущий опубликованный выпуск. |
| GET | `/issues/{number}` | Выпуск по номеру. Нет выпуска → 404. |
| GET | `/archive` | Прошлые выпуски. |
| GET | `/materials/{slug}` | Материал в статусе `ready`. Черновик и неизвестный slug → 404. |
| GET | `/knowledge/search?q=` | Поиск по базе знаний. |
| GET | `/voting/current` | Бюллетень открытого цикла. |
| POST | `/voting/votes` | Создать или подтвердить голос текущего пользователя. |
| GET | `/razbory` | Список разборов. |
| GET | `/razbory/{id}` | Карточка разбора. |
| GET | `/admin/shortlist` | Шортлист. Роль `admin`, иначе 403. |
| POST | `/admin/shortlist/items/{material_id}/decision` | Решение по кандидату. |
| POST | `/admin/shortlist/preview` | Превью письма. |
| POST | `/admin/shortlist/send` | Публикация выпуска и запись отправки. |

### Примеры запросов

Проверка API:

```bash
curl -s http://127.0.0.1:8000/health
```

Токен (пароль и ключ только из своего `.env`, в репозиторий не класть):

```bash
curl -s "$SUPABASE_URL/auth/v1/token?grant_type=password" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@sberbank.ru","password":"<password>"}'
```

Из ответа взять `access_token`.

Чтение выпуска:

```bash
curl -s http://127.0.0.1:8000/issues/current \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Отправка голоса:

```bash
curl -s -X POST http://127.0.0.1:8000/voting/votes \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic_id":"<topic-uuid>"}'
```

Обновление отображаемого имени:

```bash
curl -s -X PATCH http://127.0.0.1:8000/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"display_name":"Мария"}'
```

## Безопасность

- Вход и регистрация — Supabase Auth. Браузер использует publishable key. Домен почты ограничен `ALLOWED_EMAIL_DOMAINS` (`@sberbank.ru`, `@omega.sbrf.ru`).
- FastAPI проверяет JWT (ES256, JWKS). Нет или битый токен → **401**. Роль не `admin` на `/admin/*` → **403**.
- RLS включён на таблицах `public` в `001_initial_schema.sql`. Для `authenticated`: чтение `materials` и `knowledge_chunks` только в статусе `ready`, чтение выпусков, свои строки `votes` и свой `profiles`. Запись пайплайна идёт через `service_role` на сервере и обходит RLS. Anon-политик на закрытые таблицы нет.
- CORS: список `API_CORS_ORIGINS`, credentials включены, методы `GET`, `POST`, `PATCH`, `OPTIONS`. Заголовок `*` с credentials не используется.
- `.env` в [`.gitignore`](.gitignore). В примере окружения значения ключей пустые.

## Ошибки и логирование

| Ситуация | Ответ |
|----------|--------|
| Нет Authorization или JWT недействителен | 401 |
| Нет прав (не admin) | 403 |
| Пустой или слишком длинный поисковый запрос, невалидный голос | 400, `detail` с кодом (`empty_query`, `invalid_vote`, …) |
| Тело не совпало со схемой Pydantic (лишние поля, пустой `display_name`) | 422 |
| Нет материала или выпуска | 404 |
| Цикл голосования закрыт или конфликт версии голоса | 409 |
| БД или адаптер недоступны | 503 (`issues_unavailable`, `voting_unavailable`, `knowledge_unavailable`, …) |

Каждый запрос пишет в stdout одну JSON-строку `request_finished` с `method`, `path`, `status` и `request_id`. Тот же id возвращается заголовком `X-Request-ID`. Заголовок `Authorization` в лог не попадает. На VM Supabase дополнительные логи Auth и Postgres смотрят в Studio / логах контейнеров.

Фронт при `VITE_USE_MOCKS=false` показывает ошибку запроса и не подменяет её локальным моком.

## Процесс разработки с AI

Схема и API собирались с AI-ассистентом (Cursor) и проверялись по коду и тестам.

1. **База.** По сущностям продукта (выпуск, материал, голос, профиль, чанк знаний, разбор, шортлист) ассистент предложил SQL: таблицы, связи, enum-статусы, `vector(1024)` и `pg_trgm`. Черновик сверили с доменной моделью и поправили: внешний ключ `profiles` → `auth.users`, RLS и policies `auth.uid()` на голоса и профиль, закрытый доступ anon. Итог — миграции `001`–`005` и контрактный тест `tests/unit/test_schema_migration_contract.py`.
2. **Инфраструктура.** Сравнение вариантов (self-hosted Supabase, голый Postgres, managed-облака) зафиксировано в ADR-0004. В репозиторий добавлены Dockerfile и compose на официальный образ `supabase/postgres`, чтобы описание БД лежало рядом с миграциями.
3. **API.** Эндпоинты писались циклом Red–Green–Refactor: сначала падающий pytest (`tests/unit/test_http_*.py`), затем тонкий роутер. Бизнес-правила остались в use case, роутер только переводит доменные ошибки в HTTP.
4. **Отладка.** По JSON-логу `request_finished` и коду `detail` отделяли 401 (JWT/JWKS) от 503 (адаптер БД) и 400 (валидация запроса). Подсказки ассистента сверяли с падением теста, а не принимали патч без красного прогона.

Ограничение: ассистент не видит секреты VM. Ключи, пароль Postgres и JWT в промпты и в этот файл не попадали.
