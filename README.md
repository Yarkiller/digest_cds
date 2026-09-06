# Digest CDS

Digest CDS — корпоративный сервис сбора, структурирования и распространения
знаний для сотрудников СВА. В репозитории: канонический UI Concept 3
(Editorial) и React-приложение ДЗ на его основе.

## Ссылки

| Что | Куда |
|-----|------|
| GitHub | [https://github.com/Yarkiller/digest_cds](https://github.com/Yarkiller/digest_cds) |
| Отчёт о разработке | [`docs/digest-cds/development_report.md`](docs/digest-cds/development_report.md) |
| ТЗ | [`docs/digest-cds/technical_specification.md`](docs/digest-cds/technical_specification.md) |
| Скриншоты адаптива | [`docs/digest-cds/responsive-evidence/`](docs/digest-cds/responsive-evidence/) |

## Технологический стек

| Слой | Выбор |
|------|-------|
| Сборка / dev-сервер | Vite |
| UI-фреймворк | React |
| Роутинг | React Router |
| Стилизация | Tailwind CSS (токены из `design-frontend/styles/tokens.css`) |
| Автотесты | Playwright |

Зависимости приложения: [`web/package.json`](web/package.json).  
Зависимости тестов (корень): [`package.json`](package.json).

### Минимум 3 основные функции

1. **Выпуск и материал** — текущий выпуск и страница статьи (`/`, `/materials/:id`).
2. **Голосование** — выбор и подтверждение темы цикла (`/voting`).
3. **База знаний** — поиск, фильтры и список материалов (`/knowledge`).

## Демо (локальный запуск)

```bash
# из корня репозитория
npm install
npm install --prefix web
npm run dev
```

Открыть: [http://127.0.0.1:5173](http://127.0.0.1:5173)

Эквивалент:

```bash
cd web
npm install
npm run dev
```

Production-сборка: `npm run build` (из корня или `web/`), превью: `npm run preview --prefix web`.

## Тесты

```bash
npx playwright test
```

- `design-frontend` — эталон макетов на `http://127.0.0.1:8765`
- `web` — React-приложение на `http://127.0.0.1:5174` (поднимает Vite автоматически)

Только web: `npx playwright test --project=web`

## Каноническая структура

```text
.
├── web/                   # Vite + React + Tailwind (приложение ДЗ)
├── design-frontend/       # эталон UI Concept 3 (статика)
├── docs/
│   ├── digest-cds/        # ТЗ, отчёт, user stories, скриншоты
│   ├── adr/
│   └── agents/
├── tests/                 # Playwright
├── CONTEXT.md
├── AGENTS.md
└── archive/
```

## Эталон макетов

```bash
python -m http.server 8765
```

[http://localhost:8765/design-frontend/index.html](http://localhost:8765/design-frontend/index.html)

Карта экранов: [`design-frontend/README.md`](design-frontend/README.md).
