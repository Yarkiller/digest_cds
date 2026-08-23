# Digest CDS — UI Concepts

Статический HTML/CSS прототип по [docs/UI-SPEC.md](../../docs/UI-SPEC.md).

**Формат материалов:** статьи и презентации с тематическими обложками (SVG). Видео не используется.

## Как открыть

Откройте `index.html` в браузере (двойной клик или Live Server). Сборка не требуется.

## Экраны

| Файл | Маршрут (целевой) | Описание |
|------|-------------------|----------|
| `pages/home.html` | `/` | Главная: голосование, дайджест, материалы |
| `pages/login.html` | `/login` | Авторизация |
| `pages/digest.html` | `/digest` | Архив дайджеста |
| `pages/knowledge.html` | `/knowledge` | База знаний + поиск |
| `pages/material.html` | `/knowledge/:id` | Карточка материала |
| `pages/voting.html` | `/voting` | Голосование за тему |
| `pages/razbory.html` | `/razbory` | Список разборов |
| `pages/razbor.html` | `/razbory/:id` | Страница разбора (.ipynb) |
| `pages/admin-digest.html` | `/admin/digest` | Shortlist дайджеста |

## Структура

```
assets/covers/      — тематические обложки PNG (480×270) + SVG
styles/
├── tokens.css      — design tokens из UI-SPEC §2
├── typography.css  — типографика
├── layout.css      — shell, grid, sidebar
└── components.css  — кнопки, карточки, формы
```

## Шрифты

Inter и JetBrains Mono подключаются через Google Fonts CDN.
