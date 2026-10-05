# Roadmap: Digest CDS

## Milestones

- ✅ **[v1 MVP](milestones/v1-ROADMAP.md)** — Phases 1-5 (shipped 2026-09-22)
- ✅ **[v1.1 YouTube → LLM → Supabase ingestion](milestones/v1.1-ROADMAP.md)** — Phases 6-11 (shipped 2026-10-02)
- ✅ **[v1.2 Admin UX + diagnostics + PIPE-01 MVP](milestones/v1.2-ROADMAP.md)** — Phases 12-16 (shipped 2026-10-05)

## Phases

<details>
<summary>✅ v1 MVP (Phases 1-5) — SHIPPED 2026-09-22</summary>

- [x] Phase 1: Platform Foundation & Auth (8/8 plans) — completed 2026-09-19
- [x] Phase 2: Issue, Materials & Archive (6/6 plans) — completed 2026-09-20
- [x] Phase 3: Voting Cycle (6/6 plans) — completed 2026-09-20
- [x] Phase 4: Knowledge & Razbory (10/10 plans) — completed 2026-09-21
- [x] Phase 5: Admin Digest Publish (9/9 plans) — completed 2026-09-22

Full phase detail: [milestones/v1-ROADMAP.md](milestones/v1-ROADMAP.md)

</details>

<details>
<summary>✅ v1.1 YouTube → LLM → Supabase ingestion (Phases 6-11) — SHIPPED 2026-10-02</summary>

- [x] Phase 6: Ports & DTOs (3/3 plans) — completed 2026-09-26
- [x] Phase 7: Captions Adapter (3/3 plans) — completed 2026-09-26
- [x] Phase 8: DeepSeek Article & Templates (4/4 plans) — completed 2026-09-27
- [x] Phase 9: Draft Persist & Shortlist Enqueue (4/4 plans) — completed 2026-09-27
- [x] Phase 10: CLI Composition & UAT (5/5 plans) — completed 2026-10-01
- [x] Phase 11: Captions diagnostics & persist error classification (4/4 plans) — completed 2026-10-02

Full phase detail: [milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md)

</details>

<details>
<summary>✅ v1.2 Admin UX + diagnostics + PIPE-01 MVP (Phases 12-16) — SHIPPED 2026-10-05</summary>

- [x] Phase 12: Admin shortlist empty-batch contract (3/3 plans) — completed 2026-10-02
- [x] Phase 13: Admin material & email preview honesty (8/8 plans) — completed 2026-10-03
- [x] Phase 14: Draft→ready & justification honesty (8/8 plans) — completed 2026-10-04
- [x] Phase 15: CLI --debug diagnostics (3/3 plans) — completed 2026-10-04
- [x] Phase 16: PIPE-01 MVP config UI (4/4 plans) — completed 2026-10-05

Full phase detail: [milestones/v1.2-ROADMAP.md](milestones/v1.2-ROADMAP.md)

</details>

## Backlog

### Phase 999.1: Follow-up — Phase 13 deferred UAT follow-up: Test 1 (BACKLOG)

**Goal:** Resolve the UAT checkpoint deferred during Phase 13 verification
**Source phase:** 13
**Deferred at:** 2026-10-03 during /gsd-verify-work 13 session completion
**Follow-ups:**
- [ ] Test 1: O3 — Reader /materials/<slug> returns error page. Check: slug validity, reader endpoint health, SPA route. Not Phase 13 scope. File for Phase 14 / debug session. (deferred 2026-10-03)

### Phase 999.2: Follow-up — Phase 13 deferred UAT follow-up: Test 3 (BACKLOG)

**Goal:** Resolve the UAT checkpoint deferred during Phase 13 verification
**Source phase:** 13
**Deferred at:** 2026-10-03 during /gsd-verify-work 13 session completion
**Follow-ups:**
- [ ] Test 3: O3 — «Открыть материал →» from email/admin preview leads to error page. Reader /materials/<slug> route issue, not admin preview. Separate ticket. (deferred 2026-10-03)

### Phase 999.3: Follow-up — Phase 13 deferred UAT follow-up: Test 3 (BACKLOG)

**Goal:** Resolve the UAT checkpoint deferred during Phase 13 verification
**Source phase:** 13
**Deferred at:** 2026-10-03 during /gsd-verify-work 13 session completion
**Follow-ups:**
- [ ] Test 3: Hover on «Превью материала» keeps the default arrow cursor instead of pointer. Fix cursor-pointer on that control. Not Phase 13. (deferred 2026-10-03)

### Phase 999.4: Follow-up — Phase 14 deferred UAT follow-up: Test 1 (BACKLOG)

**Goal:** Resolve the UAT checkpoint deferred during Phase 14 verification
**Source phase:** 14
**Deferred at:** 2026-10-04 during /gsd-verify-work 14 session completion
**Follow-ups:**
- [ ] Test 1: UX (для Phase 15+): две операции на одно editorial-решение избыточны для single-operator workflow — объединить Approve (decision) + Mark ready (material_status) в одну кнопку «Одобрить и подготовить → ready»; переименовать «Сделать ready» → «Отобрать», ready → «Отобран». (deferred 2026-10-03)

### Phase 999.5: Follow-up — Phase 16 deferred UAT follow-up: admin nav grouping (BACKLOG)

**Goal:** Resolve the UAT checkpoint deferred during Phase 16 verification
**Source phase:** 16
**Deferred at:** 2026-10-04 during /gsd-verify-work 16 session completion
**Follow-ups:**
- [ ] Test 0: UX (предпочтение, не SPEC): убрать top-level nav-пункт «Пайплайн»; открывать конфиг только из админ-раздела. Вариант C — tab-bar «Дайджест | Пайплайн» на админ-страницах, top-level «Админ» → /admin/digest. Route /admin/pipeline не меняется, новый route не нужен. При реализации обновить 16-UI-SPEC A-2 и писать TDD (failing Playwright test first). (deferred 2026-10-04)

### Phase 999.6: Follow-up — Phase 16 deferred UAT follow-up: unsaved-changes guard WR-04/WR-05 (BACKLOG)

**Goal:** Resolve the UAT checkpoint deferred during Phase 16 verification
**Source phase:** 16
**Deferred at:** 2026-10-04 during /gsd-verify-work 16 session completion
**Follow-ups:**
- [ ] Test 3: WR-04/WR-05 — unsaved-changes guard принят как known limitation: window.confirm внутри beforeunload ненадёжен в реальных браузерах, router-level guard не зарегистрирован, поэтому in-app SPA-навигация молча теряет черновик. БД безопасна (не сохранил → не записано); теряется только набранный текст. Fix: корректный beforeunload (event.preventDefault/returnValue) + router guard (useBlocker) с той же копией «Есть несохранённые изменения. Уйти без сохранения?». (deferred 2026-10-04)

### Phase 999.7: Follow-up — Phase 16 code-review advisory WR-01: YAML merge-key regression (BACKLOG)

**Goal:** Restore valid YAML merge-key (`<<`) acceptance in the strict pipeline-config validator without weakening duplicate-key rejection
**Source phase:** 16
**Deferred at:** 2026-10-05 at v1.2 milestone close
**Follow-ups:**
- [ ] WR-01: `_StrictSafeLoader.construct_mapping` pre-constructs key nodes before `flatten_mapping`, so a valid YAML merge-key document (`<<`) is rejected with a cryptic internal-tag error instead of merging. Fails closed (still a structured 400 `{errors:[...]}`, zero writes) and the fixed 4-key `extra="forbid"` schema cannot yield a valid config from such a document, so it is not a v1.2 must-have. Fix: run `flatten_mapping` (or pre-resolve merge keys) BEFORE duplicate-key detection so `<<` documents behave like `SafeLoader` while duplicate-key rejection stays intact. Advisory only — fails closed. (deferred 2026-10-05)
