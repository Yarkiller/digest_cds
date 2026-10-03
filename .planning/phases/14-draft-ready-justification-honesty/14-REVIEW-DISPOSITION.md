---
phase: 14-draft-ready-justification-honesty
source: 14-REVIEW.md
updated: 2026-10-03T13:25:00Z
---

# Phase 14 — Review Disposition

Ledger for `14-REVIEW.md` after wave execution. Each finding is `open` until triaged.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| CR-01 | critical | open | Live `markReady` treats shortlist refetch failure as promote failure and rolls UI back to draft while server already saved ready. |
| WR-01 | warning | open | `mark_materials_ready` aborts on mid-batch PersistenceError instead of returning partial `results[]`. |
| WR-02 | warning | open | Non-empty blank factors list can shadow readable flat keys for honesty labels. |
| IN-01 | info | open | `promoteReady` discards successful `markReady` DTO and refetches again. |
| IN-02 | info | open | Batch `material_ids` has no upper bound. |

**Blocking for verify:** none (code-review gate is advisory).
