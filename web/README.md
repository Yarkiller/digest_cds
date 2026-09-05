# Digest CDS — web app

React-приложение ДЗ (Vite + React Router + Tailwind CSS v4).

## Запуск

```bash
cd web
npm install
npm run dev
```

Откроется `http://localhost:5173` (hot reload включён).

## Scripts

| Команда | Назначение |
|---------|------------|
| `npm run dev` | Dev-сервер Vite |
| `npm run build` | Production-сборка в `dist/` |
| `npm run preview` | Превью сборки |
| `npm run lint` | Oxlint |

## Структура

```text
src/
├── components/AppShell.jsx   # оболочка + навигация
├── pages/                    # issue / voting / knowledge (заглушки)
├── App.jsx                   # роутинг
├── main.jsx
└── index.css                 # Tailwind + design tokens
```

Эталон макетов остаётся в `../design-frontend/`.
