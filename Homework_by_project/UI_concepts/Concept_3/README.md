# Concept 3 — Editorial UI

Визуальный прототип **Concept 3** («Digest CDS: издание») на основе [UI-SPEC_3.md](./UI-SPEC_3.md).

**Backlog C3 (2026-08-23):** пункты C3-01…C3-18 закрыты в прототипе (см. [backlog_UI.md](../backlog_UI.md)).

## Как открыть

Откройте в браузере:

```
Homework_by_project/UI_concepts/Concept_3/index.html
```

Или конкретный экран, например `pages/issue.html`.  
Для stubs (голосование, KB-фильтры, admin modal) нужен HTTP-сервер или `file://` с разрешённым JS.

## Содержимое

| Путь | Экран | Stubs (`scripts/app.js`) |
|------|-------|--------------------------|
| `pages/issue.html` | Текущий выпуск + audit dek | — |
| `pages/archive.html` | Архив выпусков | — |
| `pages/knowledge.html` | База: Role/Tag/Format/Topic, analyst corpus | фильтры, load more, empty |
| `pages/material.html` | Статья с prose-колонкой и TOC | — |
| `pages/voting.html` | TopicBallot (без pre-select) | выбор + confirm toast |
| `pages/razbory.html` | Список разборов | — |
| `pages/razbor.html` | Longread: metrics, RRF, `.ipynb`, refs | — |
| `pages/login.html` | Авторизация | — |
| `pages/admin-digest.html` | Shortlist: batch, draft/ready, preview | approve/reject, email modal |

## Структура

```
Concept_3/
├── UI-SPEC_3.md
├── index.html
├── README.md
├── scripts/app.js      # прототипные stubs
├── styles/
├── assets/
│   ├── covers/
│   └── notebooks/hybrid-retrieval.ipynb
└── pages/
```

## Отличия от Concept 1 и 2

- **C1** — корпоративный dashboard, Inter, card grid
- **C2** — dark gamification, Manrope, XP/streak
- **C3** — editorial longread, serif headlines, issue-based home
