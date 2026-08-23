# Concept 3 — Editorial UI

Визуальный прототип **Concept 3** («Digest CDS: издание») на основе [UI-SPEC_3.md](./UI-SPEC_3.md).

## Как открыть

Откройте в браузере:

```
Homework_by_project/UI_concepts/Concept_3/index.html
```

Или конкретный экран, например `pages/issue.html`.

## Содержимое

| Путь | Экран |
|------|-------|
| `pages/issue.html` | Текущий выпуск (главная) |
| `pages/archive.html` | Архив выпусков |
| `pages/knowledge.html` | База знаний (MaterialListRow) |
| `pages/material.html` | Статья с prose-колонкой и TOC |
| `pages/voting.html` | TopicBallot |
| `pages/razbory.html` | Список разборов |
| `pages/razbor.html` | Longread разбора |
| `pages/login.html` | Авторизация |
| `pages/admin-digest.html` | Shortlist дайджеста |

## Структура

```
Concept_3/
├── UI-SPEC_3.md
├── index.html          # галерея экранов
├── README.md
├── styles/
│   ├── tokens.css      # warm paper palette
│   ├── typography.css  # Source Serif 4 + IBM Plex Sans
│   ├── layout.css
│   └── components.css  # IssueTOC, TopicBallot, …
└── pages/
```

Обложки материалов — локально в `assets/covers/` (5 PNG + SVG).

## Отличия от Concept 1 и 2

- **C1** — корпоративный dashboard, Inter, card grid
- **C2** — dark gamification, Manrope, XP/streak
- **C3** — editorial longread, serif headlines, issue-based home
