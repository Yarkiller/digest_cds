# Digest CDS — UI-SPEC v1

**Status:** draft (2026-08-23)  
**Stack:** React SPA (see [spec v1](../.scratch/digest-cds/spec.md))  
**Domain glossary:** [CONTEXT.md](../CONTEXT.md)  
**Language UI:** русский

Design contract для v1. Post-v1 экраны (лидерборд, карточки с вопросами, analytics) помечены явно.

**Контентный контракт:** UI показывает только подготовленные агентом статьи. Они создаются из транскрипции внешнего видео или импортированного текста, дополняются уточняющим поиском и анализом; видео/аудио и необработанный транскрипт не являются материалом, не встраиваются и не сохраняются как материал. Ссылка на внешний источник допускается только как provenance. Сложные термины должны ссылаться на отдельные поясняющие статьи при первом уместном упоминании.

---

## 1. Принципы

| # | Принцип | Реализация |
|---|---------|------------|
| P1 | Контент в центре | Карточка материала и резюме — главный визуальный якорь |
| P2 | Один сценарий на экран | Голосование, поиск и админ-shortlist — отдельные маршруты |
| P3 | Корпоративная сдержанность | Без gamification-UI в v1; янтарный акцент только для активного цикла голосования |
| P4 | DS-слой | Теги, monospace, .ipynb-viewer — «инженерный» акцент поверх делового каркаса |
| P5 | ≤30 с до материала | Глобальный поиск в header на всех authenticated-страницах |

---

## 2. Design tokens

Значения заданы в px для макета; в React маппятся на CSS custom properties (`:root`).

### 2.1 Color

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg-app` | `#F7F8FA` | Фон приложения |
| `--color-bg-surface` | `#FFFFFF` | Карточки, модалки, header |
| `--color-bg-muted` | `#F3F4F6` | Code blocks, secondary panels |
| `--color-bg-voting` | `#FFFBEB` | Фон блока активного голосования |
| `--color-bg-highlight` | `#CCFBF1` | Подсветка фрагмента в результатах поиска |
| `--color-text-primary` | `#1A1D26` | Основной текст |
| `--color-text-secondary` | `#5C6370` | Метаданные, captions |
| `--color-text-disabled` | `#9CA3AF` | Disabled, placeholders |
| `--color-border` | `#E2E5EB` | Разделители, обводки карточек |
| `--color-border-strong` | `#CBD5E1` | Input focus ring (outer) |
| `--color-primary` | `#0F4C81` | Nav active, primary buttons, links default |
| `--color-primary-hover` | `#0C3D66` | Hover primary |
| `--color-accent` | `#0D9488` | Теги, search focus, DS-метки |
| `--color-accent-hover` | `#0F766E` | Hover accent |
| `--color-voting` | `#D97706` | CTA голосования, полоска цикла |
| `--color-voting-muted` | `#FDE68A` | Progress bar голосования (fill) |
| `--color-success` | `#059669` | «Отправить дайджест», success toast |
| `--color-danger` | `#DC2626` | Ошибки форм, destructive (редко) |
| `--color-info` | `#0284C7` | Info banners (.ipynb read-only) |

**Contrast:** body text on `--color-bg-surface` ≥ 4.5:1; secondary text ≥ 3:1.

### 2.2 Typography

**Font stacks**

```css
--font-sans: "Inter", "Segoe UI", system-ui, sans-serif;
--font-mono: "JetBrains Mono", "Consolas", monospace;
```

Inter подключать через `@fontsource/inter` (weights 400, 500, 600). JetBrains Mono — 400 для code blocks.

**Scale**

| Token | Size | Line height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `--text-display` | 32px | 40px (1.25) | 600 | H1 страницы (материал, разбор) |
| `--text-h1` | 24px | 32px (1.33) | 600 | Заголовок выпуска дайджеста |
| `--text-h2` | 20px | 28px (1.4) | 600 | Секции, заголовки карточек |
| `--text-h3` | 16px | 24px (1.5) | 600 | Подзаголовки, topic title |
| `--text-body` | 16px | 26px (1.625) | 400 | Резюме и текст подготовленной статьи |
| `--text-body-sm` | 14px | 22px (1.57) | 400 | UI labels, nav items |
| `--text-caption` | 13px | 18px (1.38) | 400 | Даты, счётчики, meta |
| `--text-overline` | 12px | 16px (1.33) | 500 | BADGE, section labels (uppercase, letter-spacing 0.04em) |
| `--text-code` | 14px | 22px (1.57) | 400 | Inline code, monospace |

**Reading width:** prose blocks (резюме, текст статьи, .ipynb markdown) — `max-width: 720px`.

### 2.3 Spacing

8px base grid. Использовать только значения из шкалы.

| Token | Value |
|-------|-------|
| `--space-0` | 0 |
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |
| `--space-16` | 64px |

**Layout defaults**

| Element | Padding / gap |
|---------|---------------|
| Page horizontal padding | `--space-6` (mobile), `--space-8` (≥768px) |
| Section vertical gap | `--space-8` |
| Card internal padding | `--space-5` (compact), `--space-6` (default) |
| Card grid gap | `--space-4` |
| Stack gap (form fields) | `--space-4` |
| Inline gap (tags, buttons) | `--space-2` |

### 2.4 Radius & elevation

| Token | Value |
|-------|-------|
| `--radius-sm` | 4px |
| `--radius-md` | 6px |
| `--radius-lg` | 8px |
| `--radius-full` | 9999px |
| `--shadow-sm` | `0 1px 2px rgba(26, 29, 38, 0.06)` |
| `--shadow-md` | `0 1px 3px rgba(26, 29, 38, 0.08), 0 1px 2px rgba(26, 29, 38, 0.04)` |
| `--shadow-lg` | `0 4px 12px rgba(26, 29, 38, 0.1)` |

Cards: `--radius-lg` + `--shadow-md`. Buttons/inputs: `--radius-md`.

### 2.5 Breakpoints

| Token | Min width | Layout |
|-------|-----------|--------|
| `--bp-sm` | 640px | 1 → 2 col cards |
| `--bp-md` | 768px | Sidebar collapsible |
| `--bp-lg` | 1024px | 2-col digest archive |
| `--bp-xl` | 1280px | Max container 1200px, sticky side TOC |

```css
--container-max: 1200px;
--header-height: 56px;
--sidebar-width: 240px;
--toc-width: 200px;
```

### 2.6 Motion

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | 120ms | Hover, focus |
| `--duration-normal` | 200ms | Accordion, toast |
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | All transitions |

Respect `prefers-reduced-motion`: отключать transitions > 0.

---

## 3. Global layout

### 3.1 App shell (authenticated)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ HEADER  h=56px  bg=surface  border-bottom                              │
│ [Logo Digest CDS] [Nav links]     [SearchBar flex-1 max 480px]  [User] │
├──────────────────────────────────────────────────────────────────────────┤
│ MAIN  bg=app  padding-x=24–32  max-w=1200 centered                      │
│   {Outlet}                                                               │
└──────────────────────────────────────────────────────────────────────────┘
```

**Header nav items (v1):**

| Label | Route | Roles |
|-------|-------|-------|
| Главная | `/` | all |
| Дайджест | `/digest` | all |
| База знаний | `/knowledge` | all |
| Голосование | `/voting` | all |
| Разборы | `/razbory` | all |
| Админ | `/admin` | admin |

Active link: `--color-primary` text + 2px bottom border `--color-primary`.

**User menu:** имя, `RoleBadge`, «Выйти».

### 3.2 Auth layout (unauthenticated)

Centered card `max-width: 400px`, без global search. Routes: `/login`, `/register`.

---

## 4. Components

### 4.1 Button

| Variant | Background | Text | Height | Padding-x |
|---------|------------|------|--------|-----------|
| `primary` | `--color-primary` | white | 40px | 16px |
| `accent` | `--color-accent` | white | 40px | 16px |
| `voting` | `--color-voting` | white | 40px | 16px |
| `success` | `--color-success` | white | 40px | 16px |
| `secondary` | transparent | `--color-primary` | 40px | 16px + border |
| `ghost` | transparent | `--color-text-secondary` | 36px | 12px |

Font: `--text-body-sm`, weight 500. Disabled: opacity 0.5, no pointer.

### 4.2 SearchBar

- Height: 40px; radius `--radius-md`; border 1px `--color-border`.
- Focus: border `--color-accent`, outer ring 2px `--color-border-strong`.
- Placeholder: «Поиск по базе знаний…»
- Debounce: 300ms; loading spinner 16px справа inside input.
- Min width in header: 280px; max 480px.

### 4.3 MaterialCard

```
┌─────────────────────────────────────────────────────────┐
│ [thumb 120×68]  title (h3, max 2 lines)                 │
│                 summary (body-sm, max 2 lines, secondary)│
│                 [TagPill × n]              date (caption) │
└─────────────────────────────────────────────────────────┘
```

- Padding: `--space-5`; gap thumb–content: `--space-4`.
- Thumb radius: `--radius-md`; object-fit cover.
- Hover: `--shadow-lg`, transition `--duration-fast`.
- Optional: relevance badge (caption) для search results.

### 4.4 TopicCard (голосование)

- Min height: 180px; padding `--space-6`.
- Left border 4px: `--color-voting` if selected, `--color-border` otherwise.
- Vote bar: height 6px, bg `#E5E7EB`, fill `--color-voting-muted`.
- Vote count: caption, без имён пользователей.

States: `default` | `selected` (check icon + «Ваш выбор») | `disabled` (цикл закрыт).

### 4.5 TagPill

- Height: 24px; padding 0 10px; radius `--radius-full`.
- Bg: `#ECFDF5`; text: `--color-accent`; font caption.
- Hover: underline; click → navigate `/knowledge?tag=…`.

### 4.6 RoleBadge

| Role | Label | Bg | Text |
|------|-------|-----|------|
| employee | Сотрудник СВА | `#EFF6FF` | `#1D4ED8` |
| ds-expert | DS-эксперт | `#ECFDF5` | `#047857` |
| admin | Админ | `#F3F4F6` | `#374151` |

Overline 12px, padding 2px 8px, radius `--radius-sm`.

### 4.7 VotingTimer

- Overline label «Цикл голосования» + dates range (body-sm).
- Progress: full width, h=4px; fill `--color-voting`.
- Status text: «Ваш голос: не отдан» | «Ваш голос: Тема X» | «Цикл завершён».

### 4.8 DigestIssueHeader

- Overline: «Дайджест №{n}»
- H1: «{start_date} — {end_date}»
- Caption: «{count} материалов»

### 4.9 NotebookViewer

- Info banner top: bg `#EFF6FF`, text info — «Код не выполняется — только просмотр».
- Content: nbconvert HTML inside `.notebook-prose`.
- Code cells: bg `--color-bg-muted`, padding `--space-4`, radius `--radius-md`, font `--text-code` mono.
- Sticky TOC left (≥1280px): `--toc-width`, anchor links body-sm.

### 4.10 AdminShortlistRow

- Height: 56px; checkbox 20px at left `--space-4`.
- Columns: rank | MaterialCard compact | score (mono caption) | preview link.
- Unchecked row: opacity 0.7.

### 4.11 EmptyState

- Icon 48px muted + h2 + body-sm secondary + optional CTA.
- Vertical padding `--space-16`.

### 4.12 Toast

- Bottom-right, min-width 280px, padding `--space-4`, shadow `--shadow-lg`.
- Auto-dismiss 4s. Variants: success | error | info.

---

## 5. Routes & wireframes

### 5.1 Route map

```
/login
/register
/                          HomePage
/digest                    DigestArchivePage
/digest/:issueId           DigestIssuePage
/knowledge                 KnowledgeBasePage
/knowledge/:materialId     MaterialPage
/voting                    VotingPage
/razbory                   RazboryListPage
/razbory/:razborId         RazborPage
/admin                     AdminLayout
/admin/digest              AdminDigestShortlistPage
/admin/sources             AdminSourcesPage
/admin/moderation          AdminModerationPage
```

React Router v6. Protected routes: all except `/login`, `/register`. Admin nested routes: `role === admin`.

---

### 5.2 `/login`

```
┌──────────────────────────────┐
│         Digest CDS           │
│    СВА · DS-направление      │
│                              │
│  Email                       │
│  [________________________]  │
│  Пароль                      │
│  [________________________]  │
│                              │
│  [      Войти (primary)    ] │
│                              │
│  Нет аккаунта? Регистрация   │
│  Доступ: @sberbank.ru,       │
│          @omega.sbrf.ru      │
└──────────────────────────────┘
```

Card padding `--space-8`; field stack gap `--space-4`.

---

### 5.3 `/` — HomePage

```
┌─ main max-w=1200 ──────────────────────────────────────────────────────┐
│                                                                        │
│  ┌─ VotingBanner  bg=voting  border-l 4px voting  p=24 ─────────────┐ │
│  │ VotingTimer                                                       │ │
│  │ h2: Выберите тему для разбора {date}                              │ │
│  │ [TopicCard][TopicCard][TopicCard]  →  [Проголосовать] if !voted   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                        gap 32          │
│  ┌─ 2-col ≥1024 ──────────────────────────────────────────────────┐  │
│  │ ┌ LatestDigestCard ──────┐  ┌ UpcomingRazborCard ─────────────┐  │  │
│  │ │ Дайджест №12           │  │ Ближайший разбор                │  │  │
│  │ │ 5 материалов · 18 мар  │  │ Тема-победитель · 14 апр       │  │  │
│  │ │ [Открыть →]            │  │ [Открыть разбор →]             │  │  │
│  │ └────────────────────────┘  └─────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                        gap 32          │
│  h2: Недавно в базе знаний                                             │
│  [MaterialCard][MaterialCard][MaterialCard]   grid 3 col ≥1280         │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

If voting closed: VotingBanner replaced by muted caption + link «Архив голосований» (post-v1) or «Следующий цикл {date}».

---

### 5.4 `/digest` — DigestArchivePage

```
┌─ 2-col ≥1024 ──────────────────────────────────────────────────────────┐
│ SIDEBAR w=240          │ MAIN                                          │
│ h2: Архив              │ DigestIssueHeader                             │
│ ─────────────────      │ ─────────────────────────────────────────     │
│ ● №12  18–24 мар       │ [MaterialCard full width]                     │
│   №11  11–17 мар       │ [MaterialCard]                                │
│   №10  4–10 мар        │ [MaterialCard]                                │
│   …                    │ …                                             │
└────────────────────────┴───────────────────────────────────────────────┘
```

Sidebar: scroll independent; active issue `--color-primary` + bg `#EFF6FF`.

Mobile: sidebar → horizontal scroll chips above content.

---

### 5.5 `/knowledge` — KnowledgeBasePage

```
┌─ main ─────────────────────────────────────────────────────────────────┐
│ h1: База знаний                                                          │
│                                                                          │
│ ┌ SearchBar large  h=48  w=100% max-w=640 ─────────────────────────────┐ │
│ │ 🔍  Спросите своими словами…                                         │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌ Filters row ─────────────────────────────────────────────────────────┐ │
│ │ Теги [v]  Период [v]  Источник [v]          Сбросить фильтры        │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ caption: Найдено 24 материала                                            │
│                                                                          │
│ [MaterialCard + highlight snippet]                                       │
│ [MaterialCard]                                                           │
│ [MaterialCard]                                                           │
│ …                                                                        │
│ [Load more]                                                              │
└──────────────────────────────────────────────────────────────────────────┘
```

Search highlight: `<mark>` styled with `--color-bg-highlight`.

---

### 5.6 `/knowledge/:materialId` — MaterialPage

```
┌─ ≥1280: 2-col ─────────────────────────────────────────────────────────┐
│ CONTENT max 720px              │ TOC sticky w=200 (≥1280 only)         │
│                                │ · Резюме                              │
│ [Hero image / cover]           │ · Теги                                │
│ h1 title                       │ · Полный текст                        │
│ caption: добавлен · provenance │ · Связанные статьи                    │
│                                │                                       │
│ h2 Резюме                      │                                       │
│ body prose…                    │                                       │
│                                │                                       │
│ TagPill row                    │                                       │
│                                │                                       │
│ h2 Полный текст                │                                       │
│ article prose                  │                                       │
│                                │                                       │
│ aside box: В дайджесте №12     │                                       │
│            Темы: …             │                                       │
└────────────────────────────────┴───────────────────────────────────────┘
```

Обложка — статичное изображение статьи. В material view нет видеоплеера и загрузки видео/аудио; provenance-ссылка на внешний источник, если она разрешена политикой, открывается отдельно.

---

### 5.7 `/voting` — VotingPage

```
┌─ main max-w=960 centered ──────────────────────────────────────────────┐
│ h1: Голосование за тему разбора                                        │
│ VotingTimer full width                                                 │
│ body-sm: Один голос за цикл. Вы можете изменить выбор до {end_date}.   │
│                                                                        │
│ grid 1 col mobile / 2 col ≥640 / 3 col ≥1024                           │
│ [TopicCard] [TopicCard] [TopicCard]                                    │
│ [TopicCard] …                                                          │
│                                                                        │
│ sticky bottom bar (mobile only): [Проголосовать] voting variant        │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 5.8 `/razbory` — RazboryListPage

```
h1: Разборы
caption: Встречи раз в две недели · материалы от DS-экспертов

┌ list ────────────────────────────────────────┐
│ [date]  Topic title                        │
│         Author · RoleBadge                   │
│         [Открыть разбор →]                   │
├────────────────────────────────────────────┤
│ …                                          │
└────────────────────────────────────────────┘
```

Row padding `--space-5`; border-bottom `--color-border`.

---

### 5.9 `/razbory/:razborId` — RazborPage

```
┌─ same layout as MaterialPage + NotebookViewer ─────────────────────────┐
│ header: topic title, date razbor, author + RoleBadge                   │
│ NotebookViewer (full width prose max 720px centered)                    │
└────────────────────────────────────────────────────────────────────────┘
```

DS-экpert: optional banner «Вы автор» + link upload .ipynb (admin/backend flow, UI TBD).

---

### 5.10 `/admin/digest` — AdminDigestShortlistPage

```
┌─ admin main ───────────────────────────────────────────────────────────┐
│ overline: Админ                                                          │
│ h1: Shortlist дайджеста                                                  │
│ caption: Неделя {range} · топ-5 после авто-ранжирования                  │
│                                                                          │
│ ┌ table-like list ─────────────────────────────────────────────────────┐ │
│ │ [x] 1. AdminShortlistRow …                                         │ │
│ │ [x] 2. …                                                           │ │
│ │ [ ] 3. …                                                           │ │
│ │ …                                                                  │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ footer sticky:  [Предпросмотр письма]     [Отправить дайджест →]       │
└──────────────────────────────────────────────────────────────────────────┘
```

Preview: modal max-w 640px, renders same as email/digest issue.

Send disabled if 0 selected; confirm dialog before send.

---

### 5.11 `/admin/sources` — AdminSourcesPage

Read-only preview YAML sources (channels, playlists, keywords) + link to repo config path. Manual URL form: input + «Добавить материал».

---

### 5.12 `/admin/moderation` — AdminModerationPage

Table: material | status | actions (hide, re-tag trigger). Minimal v1 — list + hide toggle.

---

## 6. React SPA structure

Recommended folder layout aligned with routes and components above.

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── src/
│   ├── main.tsx
│   ├── App.tsx                    # RouterProvider
│   ├── styles/
│   │   ├── tokens.css             # :root vars from §2
│   │   ├── typography.css
│   │   ├── layout.css
│   │   └── notebook.css           # nbconvert overrides
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── AuthLayout.tsx
│   │   │   └── AdminLayout.tsx
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── TagPill.tsx
│   │   │   ├── RoleBadge.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── Toast.tsx
│   │   ├── material/
│   │   │   └── MaterialCard.tsx
│   │   ├── voting/
│   │   │   ├── TopicCard.tsx
│   │   │   └── VotingTimer.tsx
│   │   ├── digest/
│   │   │   └── DigestIssueHeader.tsx
│   │   ├── notebook/
│   │   │   └── NotebookViewer.tsx
│   │   └── admin/
│   │       └── AdminShortlistRow.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── digest/
│   │   ├── knowledge/
│   │   ├── voting/
│   │   ├── razbory/
│   │   └── admin/
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   └── useDebouncedSearch.ts
│   ├── api/                       # fetch wrappers → FastAPI
│   └── routes.tsx                 # route config + guards
```

**Suggested libraries (v1):**

| Concern | Choice |
|---------|--------|
| Build | Vite + React 18 + TypeScript |
| Routing | react-router-dom v6 |
| Data fetching | TanStack Query |
| Forms | react-hook-form (auth, admin URL) |
| CSS | CSS Modules or vanilla CSS with tokens (no heavy UI kit v1) |

**API boundaries (UI expects):**

- `GET /materials`, `GET /materials/:id`, `GET /materials/search?q=&tags=`
- `GET /digest/issues`, `GET /digest/issues/:id`
- `GET /voting/current`, `POST /voting/vote`
- `GET /razbory`, `GET /razbory/:id` (HTML notebook payload)
- `GET /admin/digest/shortlist`, `POST /admin/digest/send`
- `POST /auth/login`, `POST /auth/register`, `GET /auth/me`

---

## 7. Accessibility

- Language: `<html lang="ru">`.
- Focus visible: 2px ring `--color-accent`, offset 2px.
- All interactive targets ≥ 44×44px touch (mobile).
- Images: alt from material title; decorative thumbs alt="".
- Vote buttons: `aria-pressed` on selected TopicCard.
- Search: `role="search"`, results in `aria-live="polite"` region.
- Color not sole indicator: icons + text for states.

---

## 8. Post-v1 placeholders (do not implement in v1)

| Feature | Route sketch | Notes |
|---------|--------------|-------|
| Лидерборд | `/leaderboard` | ADR-0001; public ranking |
| Карточка с вопросами | `/materials/:id/quiz` | After digest / razbor |
| Analytics dashboard | `/admin/analytics` | CDS-only |
| Leaderboard opt-out | `/settings/privacy` | TBD |

---

## 9. Acceptance checklist (UI)

- [ ] Tokens in `tokens.css` match §2 exactly.
- [ ] Header SearchBar present on all authenticated pages.
- [ ] MaterialPage readable at 720px prose width.
- [ ] VotingPage enforces one-vote UX (selected state + timer).
- [ ] Admin shortlist completable in < 10 min (checkbox + preview + send).
- [ ] Responsive: home + material + digest usable at 375px width.
- [ ] All user-visible strings in Russian; domain terms per CONTEXT.md.

---

## 10. References

- [Spec v1](../.scratch/digest-cds/spec.md)
- [CONTEXT.md](../CONTEXT.md)
- [ADR-0001](./adr/0001-public-leaderboard-gamification.md)
- [ADR-0003](./adr/0003-email-domain-restriction.md)
