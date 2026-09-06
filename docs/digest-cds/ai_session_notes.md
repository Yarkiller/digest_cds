# AI session notes (homework Steps 5–6)

Working notes absorbed into [`../../development_report.md`](../../development_report.md). Keep this file as a short appendix.

## Tools used

- Cursor agent (Composer) for Red–Green–Refactor and Playwright specs
- Multimodal review: screenshot of the header search dialog (user-provided) to judge layout duplication
- Playwright for automated UI / state / edge coverage

## Visual bug → AI debugging → fix

### Symptom

Header search opened a modal with destination links («База знаний», «Текущий выпуск», «Голосование») that duplicated primary navigation. The search field itself was undersized relative to the dialog chrome.

### AI-assisted diagnosis

From the screenshot: modal content was navigation, not search results; header already exposed the same destinations. Recommendation: remove the modal and keep an enlarged inline field.

### Fix

- Removed dialog / destination list from `SearchPill`
- Enlarged inline `type="search"` in the shell header (`min-h-12`, ≥240px)
- Ctrl+K focuses the field; Enter navigates to `/knowledge?q=…`
- Knowledge page seeds filters from `q`

### Regression test

`keeps header search as an enlarged inline field without a modal` — no dialog, size checks, focus shortcut, query hand-off.

## Other AI-assisted debugging in this milestone

| Issue | How found | Fix |
|-------|-----------|-----|
| Vote locator broke when label switched to «Сохраняем…» | Playwright failure after loading-state assertion | Stable `data-testid="confirm-vote"` |
| Loading state too short to observe | Flaky `data-state=loading` | Simulated latency ~600ms |
| Empty-state recovery asserted wrong count copy | Spec expected «Найдено N» | Align with Concept 3: «Показано N из M» |
| Header search ignored typed query | Extended Step 5 assertion | Pass `?q=` and read it on KnowledgePage |

## Automated test map (web app)

| Group | Coverage |
|-------|----------|
| Main flows | Issue → material; voting confirm; knowledge tag facet |
| UI states | Vote loading→success; KB empty recovery; load-more skeleton; inline header search |
| Edge / error | Unknown material id; confirm disabled without selection |
| Responsive | 390/320 overflow checks; desktop identity + search width; mobile voting CTA in viewport |

Run: `npx playwright test --project=web`

## Step 6 — adaptive layout (AI + media queries)

### Goal

Prove mobile/desktop adaptation and fix narrow-phone overflow.

### AI-assisted media-query guidance

Tailwind breakpoints used after agent review of Concept 3 shell:

- `sm:` — restore min search width (≥240px), show TOC meta
- `md:` — show user identity; widen search (`max-w-sm`)
- Mobile-first: `min-w-0` on search so 320px shells do not force horizontal scroll; nav wraps to full width (`order-last w-full`)

### Bug fixed in this step

Rigid `min-w-[240px]` on the header search overflowed at **320px** (`scrollWidth` 344 > 321). Replaced with `min-w-0 sm:min-w-[240px]`.

### Evidence

See [`responsive-evidence/`](./responsive-evidence/).
