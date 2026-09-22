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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1 | not recorded | 5 | First close. Gap-closure plans and mock Playwright gates became the default. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1 | pytest + Playwright per phase | not measured | Ports & Adapters layout kept |

### Top Lessons (Verified Across Milestones)

1. Close the debug file when the fix lands, or the next milestone close will surface it again.
2. Live mail and signup SMTP are separate from the product requirements that shipped in v1.
