# Digital CDS — Spec v1

**Status:** accepted (grill-with-docs, 2026-08-23)  
**Инициатор:** CDS, СВА Сбербанка  
**Аудитория:** DS-эксперты и рядовые сотрудники СВА

## Problem

Сотрудники СВА тратят много времени на поиск и отбор релевантных материалов по новым технологиям. Нет единого источника знаний и механизма голосования за темы для совместного разбора.

## Solution

Веб-сервис на Cloud.ru для сбора YouTube-контента, транскрибации и тегирования через FoundryModels, еженедельного email-дайджеста, голосования за темы разборов, базы знаний с векторным поиском и подготовки .ipynb по победившим темам.

## Users & Roles

| Роль | Приоритет | v1 capabilities |
|---|---|---|
| **DS-эксперт** | 1 | Поиск, голосование, создание .ipynb для разборов |
| **Рядовой сотрудник СВА** | 2 | Дайджест, голосование, поиск в базе знаний |
| **Админ** (CDS/делегат) | — | YAML-конфиги, утверждение дайджеста, модерация |

Регистрация: email + пароль. Разрешённые домены: `@sberbank.ru`, `@omega.sbrf.ru` (ADR-0003).

## Core Flows

### 1. Content ingestion

1. **YAML-источники** (каналы, плейлисты, ключевые слова) + **ручное добавление URL** админом/экспертом.
2. **YouTube Data API v3** — мониторинг новых роликов по источникам.
3. **`yt-dlp`** — скачивание аудио для транскрибации.
4. **FoundryModels** (Cloud.ru): транскрибация → русское резюме → авто-теги → эмбеддинги.
5. Автоматическое создание **карточки знаний** (.md) в базе знаний.

### 2. Weekly digest

1. **Cron** (еженедельно) запускает CLI: сбор кандидатов за неделю → авто-ранжирование → **shortlist топ-5**.
2. Админ утверждает состав в **веб-UI** (галочки → «Отправить»).
3. Email-рассылка через **корпоративный SMTP Сбера**.
4. Копия дайджеста в архиве на сайте.

UI и материалы — на русском; исходное видео может быть на EN.

### 3. Voting & разбор

1. **Непрерывное голосование**: один голос на пользователя за **цикл голосования** (2 недели).
2. Тема может объединять несколько материалов.
3. По закрытии окна — победившая **тема** идёт на **разбор** (встреча раз в 2 недели).
4. DS-эксперт готовит **.ipynb**; на сайте — **HTML-рендер** (nbconvert), без исполнения кода.

### 4. Knowledge base search

- PostgreSQL + **pgvector** на той же VM (Docker Compose рядом с приложением).
- Векторный + полнотекстовый поиск по карточкам знаний на сайте.

### 5. Activity tracking (silent in v1)

Собираем **события активности** без UI:

- Просмотры материалов
- Открытия дайджестов
- Участие в голосованиях
- Поисковые запросы
- Время на странице

Данные для **лидерборда** (ADR-0001) — после v1.

## Architecture

| Component | Choice |
|---|---|
| Hosting | VM Cloud.ru |
| Backend | FastAPI (Python) |
| Frontend | React SPA |
| Database | PostgreSQL + pgvector (Docker Compose на VM Cloud.ru) |
| ML pipeline | FoundryModels API (Cloud.ru) |
| YouTube | Data API v3 + yt-dlp |
| Scheduler | cron + CLI commands on VM |
| Email | Corporate Sber SMTP |
| .ipynb display | nbconvert → static HTML |
| Config | YAML/JSON in repository |

## MVP Scope

### In v1

- [ ] Content ingestion (YAML + manual URL)
- [ ] Transcription & enrichment via FoundryModels
- [ ] Knowledge cards + vector search
- [ ] Weekly digest (auto-rank top-5 + admin approval UI)
- [ ] Email delivery
- [ ] Web: auth, digest archive, voting, search
- [ ] Bi-weekly разбор workflow + .ipynb HTML render
- [ ] Three roles (employee, DS-expert, admin)
- [ ] Silent activity event collection

### After v1

- [ ] Quiz cards (FoundryModels + author review)
- [ ] Public leaderboard (gamification)
- [ ] Leaderboard opt-out
- [ ] Jupyter viewer with cell execution
- [ ] Corporate SSO
- [ ] Extended CDS analytics dashboard

## ADRs

| ID | Decision |
|---|---|
| ADR-0001 | Public leaderboard (implement post-v1) |
| ADR-0002 | Cloud.ru VM + FoundryModels for ML |
| ADR-0003 | Email domains: @sberbank.ru, @omega.sbrf.ru |
| ADR-0004 | PostgreSQL + pgvector in Docker Compose on VM |

## Domain glossary

See [`CONTEXT.md`](../../CONTEXT.md) at repo root.

## Open items (for implementation)

- Конкретные модели FoundryModels (transcription, embedding) — уточнить при интеграции.
- YouTube Data API credentials и квоты.
- Параметры SMTP (хост, порт, заявка в Сбер).
- Алгоритм авто-ранжирования (веса: свежесть, просмотры YouTube, теги, LLM-score).

## Success criteria (v1)

1. Новое видео из YAML-источника автоматически появляется в базе знаний с транскриптом и тегами на русском.
2. Админ утверждает и отправляет дайджест из топ-5 за < 10 минут.
3. Пользователь СВА находит материал через поиск за < 30 секунд.
4. Голосование за тему и публикация .ipynb разбора работают end-to-end.
