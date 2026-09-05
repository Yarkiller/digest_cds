# Digest CDS

Digest CDS — корпоративный сервис сбора, структурирования и распространения
знаний для сотрудников СВА. В репозитории: канонический UI Concept 3
(Editorial) и React-приложение ДЗ на его основе.

## Технологический стек

| Слой | Выбор |
|------|-------|
| Сборка / dev-сервер | Vite |
| UI-фреймворк | React |
| Роутинг | React Router |
| Стилизация | Tailwind CSS (токены из `design-frontend/styles/tokens.css`) |
| Автотесты | Playwright |

### Минимум 3 основные функции

1. **Выпуск и материал** — текущий выпуск и страница статьи.
2. **Голосование** — выбор и подтверждение темы цикла.
3. **База знаний** — поиск, фильтры и список материалов.

Подробности — в [`docs/digest-cds/technical_specification.md`](docs/digest-cds/technical_specification.md) §3 и §3.3.

## Текущий статус

- **`web/`** — React-приложение ДЗ (Vite, hot reload).
- **`design-frontend/`** — эталон Editorial UI (макеты, токены, stubs).

## Каноническая структура

```text
.
├── web/                   # Vite + React + Tailwind (приложение ДЗ)
├── design-frontend/       # эталон UI Concept 3 (статика)
├── docs/
│   ├── digest-cds/        # ТЗ, user stories, критерии приёмки
│   ├── adr/               # архитектурные решения
│   └── agents/            # правила работы с доменной документацией
├── tests/                 # Playwright (корень репозитория)
├── .scratch/digest-cds/   # рабочая спецификация
├── CONTEXT.md             # доменный словарь
├── AGENTS.md              # правила AI-агентов
└── archive/               # исторические артефакты
```

## Запуск React-приложения

```bash
cd web
npm install
npm run dev
```

Открыть: `http://localhost:5173`

Подробнее: [`web/README.md`](web/README.md).

## Запуск эталона макетов

```bash
python -m http.server 8765
```

`http://localhost:8765/design-frontend/index.html`

Карта экранов: [`design-frontend/README.md`](design-frontend/README.md).

## Тесты

```bash
npx playwright test
```
