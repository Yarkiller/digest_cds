# Roadmap: Digest CDS

## Milestones

- ✅ **[v1 MVP](milestones/v1-ROADMAP.md)** — Phases 1-5 (shipped 2026-09-22)
- ✅ **[v1.1 YouTube → LLM → Supabase ingestion](milestones/v1.1-ROADMAP.md)** — Phases 6-11 (shipped 2026-10-02)
- 🚧 **v1.2 Admin UX + diagnostics + PIPE-01 MVP** — Phases 12-16 (in progress)

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

### 🚧 v1.2 Admin UX + diagnostics + PIPE-01 MVP (In Progress)

**Milestone Goal:** Admin can honestly review and promote ingested drafts; operators get secret-safe `--debug` diagnostics; PIPE-01 ships as config + validation + UI only (no full pipeline execution).

**Non-goals (explicit):**
- Live SMTP / signup confirmation mail — deferred to v1.3 (MAIL-01, MAIL-02)
- PIPE full pipeline execution — deferred to v1.3 (PIPE-EXEC-*)
- Ingestion HTTP/scheduler / Whisper-on-VM — still out of scope (ING-*)

- [x] **Phase 12: Admin shortlist empty-batch contract** - Fix Phase 10 carry unit so empty shortlist returns 200 with empty items (completed 2026-10-02)
- [x] **Phase 13: Admin material & email preview honesty** - Preview shows body/provenance/counts/reader link; email HTML + interstitial + no test chrome (completed 2026-10-03)
- [x] **Phase 14: Draft→ready & justification honesty** - Admin promotes draft→ready in UI; Обоснование is real or honestly empty (completed 2026-10-04)
- [ ] **Phase 15: CLI --debug diagnostics** - Richer secret-safe stage diagnostics; default progress contracts unchanged
- [ ] **Phase 16: PIPE-01 MVP config UI** - View/edit/validate/persist pipeline YAML; no run/trigger execution

## Phase Details

### Phase 12: Admin shortlist empty-batch contract

**Goal**: Empty admin shortlist responses match the locked HTTP contract so the Phase 10 carry unit passes
**Depends on**: Nothing (first v1.2 phase; v1.1 complete)
**Requirements**: FIX-01
**Success Criteria** (what must be TRUE):
  1. `test_admin_shortlist_no_batches_returns_null_batch_id` and `test_admin_shortlist_empty_unsent_batch_returns_batch_id` pass under the unit suite (D-05)
  2. An empty unsent batch returns HTTP 200 with an empty `items` list (not a schema/validation 500)
  3. Response fields required by the contract (`sent_at`, `week_label`, and related extras) align so clients are not blocked by missing/extra schema noise

**Plans**: 3/3 plans complete

Plans:
**Wave 1**
- [x] 12-01-PLAN.md — HTTP tracer: rename no-batch + empty-unsent required-key proofs

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 12-02-PLAN.md — 12-FIX-01-LOCK.md + REQUIREMENTS/ROADMAP/PROJECT proof strings
- [x] 12-03-PLAN.md — FE emptyUnsentDto harness + Playwright empty-unsent

### Phase 13: Admin material & email preview honesty

**Goal**: Admin can inspect a real material body and a real email HTML preview before send
**Depends on**: Phase 12
**Requirements**: ADUX-01, ADUX-02, ADUX-03, ADUX-04
**Success Criteria** (what must be TRUE):
  1. On `/admin/digest`, material preview shows `body_markdown`, `provenance_label`, char/word counts, and a working link to `/materials/<slug>` (not title+dek only)
  2. «Превью письма» renders real email HTML including intro, summaries, and links (not titles-only)
  3. Interstitial connecting text preserves paragraph breaks so `\n\n` is visible as whitespace / separate paragraphs
  4. Leaked `test-header` (and equivalent seed/test chrome) does not appear on admin preview surfaces after cleanup

**Plans**: 8/8 plans complete

Plans:
**Wave 1**
- [x] 13-01-PLAN.md — Tracer: enriched GET /admin/shortlist full-item DTO + FIX-01 lock growth (ADUX-01)

**Wave 2** *(blocked on Wave 1)*
- [x] 13-02-PLAN.md — Shared email HTML + interstitial + preview wire + ban unit asserts (ADUX-02/03/04)
- [x] 13-03-PLAN.md — Material modal markdown honesty UI (ADUX-01)

**Wave 3** *(blocked on Wave 2)*
- [x] 13-04-PLAN.md — Email iframe + connecting-text hint (ADUX-02/03)
- [x] 13-06-PLAN.md — Send/mailer HTML parity + D-12 proof (ADUX-02)

**Wave 4** *(blocked on Wave 3)*
- [x] 13-05-PLAN.md — Ban-list sync + migration 010 scrub + shared-VM apply gate (ADUX-04)

**Wave 5** *(gap closure, blocked on Wave 4)*
- [x] 13-07-PLAN.md — Pin material and email preview close controls (G-13-1, G-13-2, G-13-3)

**Wave 6** *(gap closure, blocked on Wave 5)*
- [x] 13-08-PLAN.md — Drop the duplicate email item list under the iframe (G-13-3b)

**UI hint**: yes

### Phase 14: Draft→ready & justification honesty

**Goal**: Admin can unblock send without SQL and see honest shortlist justification
**Depends on**: Phase 13
**Requirements**: ADUX-05, ADUX-06
**Success Criteria** (what must be TRUE):
  1. Admin can set a material from `draft` → `ready` in the admin UI without a direct SQL workaround
  2. After promotion, D-85 send gate no longer blocks that material solely for still being draft
  3. Shortlist «Обоснование» shows populated `score_factors` when available from pipeline config MVP, or an explicit empty/unavailable state (never a silent fake justification)

**Plans**: 8/8 plans complete (5 executed + 3 gap closure)

Plans:
**Wave 1**
- [x] 14-01-PLAN.md — Tracer: single POST /admin/materials/{id}/ready unblocks D-85 send

**Wave 2** *(blocked on Wave 1)*
- [x] 14-02-PLAN.md — Batch ready partial success + Approve≠ready lock

**Wave 3** *(blocked on Wave 2)*
- [x] 14-03-PLAN.md — FE promote UX + exact D-15 Обоснование honesty lock

**Wave 4** *(gap closure, blocked on Wave 3)*
- [x] 14-04-PLAN.md — G-14-2: decouple promote from refetch, kill silent revert

**Wave 5** *(gap closure, blocked on Wave 4)*
- [x] 14-05-PLAN.md — G-14-2a/2b: disambiguate status axes + dedupe footer

**Wave 6** *(gap closure, blocked on Wave 5)*
- [x] 14-06-PLAN.md — G-14-1/G-14-4: disambiguate material_relations embed so live get()/get_by_slug() work
- [x] 14-07-PLAN.md — G-14-2: remove batch promote CTA + approved-drafts hint

**Wave 7** *(gap closure, blocked on Wave 6)*
- [x] 14-08-PLAN.md — G-14-3: pointer cursor on interactive admin controls

**UI hint**: yes

### Phase 15: CLI --debug diagnostics

**Goal**: Operators can opt into richer ingest diagnostics without secret leakage or regressing default progress
**Depends on**: Phase 14
**Requirements**: DBG-01, DBG-02
**Success Criteria** (what must be TRUE):
  1. `ingestion-service` CLI accepts `--debug` and prints richer stage diagnostics on stderr/stdout
  2. Debug output never leaks secrets, proxy credentials, cookies, or full transcript bodies
  3. With `--debug` off, existing staged progress and `IngestError.to_dict()` contracts remain unchanged

**Plans**: TBD
- [x] 15-01-PLAN.md
- [x] 15-02-PLAN.md

### Phase 16: PIPE-01 MVP config UI

**Goal**: Admin can view, validate, and persist pipeline config without running the pipeline
**Depends on**: Phase 15
**Requirements**: PIPE-01, PIPE-02, PIPE-03
**Success Criteria** (what must be TRUE):
  1. Admin can view and edit YAML (or equivalent structured) pipeline config through an admin UI
  2. Invalid config is rejected before save with field-level or structured errors (no silent accept)
  3. Validated config persists and is readable on subsequent admin sessions (storage behind a port; UI has no deep Supabase coupling)
  4. No run/trigger/scheduler execution of the pipeline ships in this phase (execution stays v1.3)

**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1–5 | v1 | 40/40 | Complete | 2026-09-22 |
| 6–11 | v1.1 | 23/23 | Complete | 2026-10-02 |
| 12. Admin shortlist empty-batch contract | v1.2 | 3/3 | Complete    | 2026-10-02 |
| 13. Admin material & email preview honesty | v1.2 | 8/8 | Complete    | 2026-10-03 |
| 14. Draft→ready & justification honesty | v1.2 | 8/8 | Complete    | 2026-10-04 |
| 15. CLI --debug diagnostics | v1.2 | 2/2 | In Progress|  |
| 16. PIPE-01 MVP config UI | v1.2 | 0/? | Not started | - |

**Coverage:** 12/12 v1.2 requirements mapped (FIX-01, ADUX-01…06, DBG-01…02, PIPE-01…03). No orphans.

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
