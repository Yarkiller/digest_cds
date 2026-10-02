# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1 — MVP

**Shipped:** 2026-09-22
**Phases:** 5 | **Plans:** 40 | **Tasks:** 94

### What Was Built

- Corporate login and self-service `/register` on live Supabase, with FastAPI health, JWT, and FE↔BE proof
- Current issue, prepared-article reader, and archive
- One honest vote: confirm, change while open, closed-cycle rejection, audit-language ballot
- Semantic knowledge search with role filters, plus разборы longread, TOC, and notebook download
- Admin shortlist triage, letter preview with intro and ordered blocks, publish-on-send, and post-send rest

### What Worked

- Ports & Adapters plus Red–Green–Refactor kept domain code free of Supabase and FastAPI
- Gap-closure plans (01-07/01-08, 04-10, 05-07…05-09) closed UAT findings without reopening finished phases
- Mock-first Playwright gates made honesty checks repeatable before live adapters landed

### What Was Inefficient

- Debug sessions stayed `diagnosed` after the fixing plans shipped, so close had to acknowledge them
- Phases 1–3 left Nyquist `VALIDATION.md` in draft, and several live FE↔BE smokes stayed human-gated
- Rank rewrite before `claim_and_publish_digest` is still non-atomic (CR-01)

### Patterns Established

- Admin authorization reads `profiles.role` through `require_admin`, never a JWT role claim
- Successful send publishes an issue and claims `sent_at` before stub mail
- Announcement разборы and the post-send shortlist hide actions that would look available

### Key Lessons

1. When a gap-closure plan ships, mark the debug session resolved in the same change.
2. Treat SMTP (signup confirmation and digest delivery) as an ops milestone, separate from the editorial product path.
3. Keep REQUIREMENTS wording aligned with locked UI decisions (ISSUE-01 still said «cover» after the typography-only hero).

### Cost Observations

- Model mix: not recorded for this milestone
- Commits: 330 from `cabd7eb` (2026-08-23) through `ba8be89` (2026-09-22)
- Notable: timed plans clustered around 7 minutes; a few live-schema plans ran about 45 minutes

---

## Milestone: v1.1 — YouTube → LLM → Supabase ingestion

**Shipped:** 2026-10-02
**Phases:** 6 (6–11) | **Plans:** 23 | **Tasks:** 60

### What Was Built

- Typed `data-collection` ingestion contracts and in-memory port fakes
- YouTube captions + oEmbed adapters with fail-closed stage envelopes
- DeepSeek lecture/podcast article generation (honesty, budget, redacted errors)
- Atomic draft persist + shortlist enqueue (migrations 007–009)
- Typer CLI one-shot with idempotency, staged progress, four-video UAT
- Phase 11 hardening: secret-safe captions diagnostics, persist classify, sent-batch `already_saved`

### What Worked

- Hexagonal boundary: CLI/adapters never mixed `Transcript` with `MaterialDraft`
- Live Studio SQL apply ritual for migrations stayed explicit and blocking
- Phase 11 inserted after audit tech_debt without reopening finished phase DoD

### What Was Inefficient

- Phases 9–10 verification went stale after Phase 11; close used override_closeout
- Nyquist VALIDATION.md for phases 6–8 left draft through milestone close
- Admin UX UAT findings accumulated as follow-ups instead of a planned polish phase

### Patterns Established

- Ingestion writes Supabase only; backend/SPA stay readers
- `IngestError.to_dict()` on stderr; no SDK/proxy secrets in operator JSON
- Conflict-safe persist via RPC `already_saved` + unique `youtube_video_id`

### Key Lessons

1. After a tech-debt insert phase, re-verify prior phases or accept override_closeout explicitly.
2. Park UAT polish (admin preview/email/draft→ready) as the next milestone, not silent debt.
3. Keep Nyquist reconcile (`/gsd-validate-phase`) on the critical path before audit, not after.

### Cost Observations

- Model mix: not recorded for this milestone
- Commits: 218 from `45db99f` (2026-09-26) through `fff73a3` (2026-10-02)
- Notable: Phase 10 live UAT plan spanned ~48h wall clock; Phase 11-04 migration apply ~140min

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1 | not recorded | 5 | First close. Gap-closure plans and mock Playwright gates became the default. |
| v1.1 | not recorded | 6 | Separate ingestion CLI + RPC persist; audit tech_debt closed via inserted Phase 11. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1 | pytest + Playwright per phase | not measured | Ports & Adapters layout kept |
| v1.1 | pytest unit + CliRunner + SQL contract tests; manual CLI-03 UAT | not measured | `ingestion-service` + DeepSeek adapter |

### Top Lessons (Verified Across Milestones)

1. Close the debug file when the fix lands, or the next milestone close will surface it again.
2. Live mail and signup SMTP are separate from the product requirements that shipped in v1.
3. Inserted tech-debt phases need explicit re-verify of prior VERIFICATION.md or documented override.
