---
phase: 13-admin-material-email-preview-honesty
source: 13-REVIEW.md
updated: 2026-10-03T07:25:00Z
---

# Phase 13 — Review Disposition

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| CR-01 | critical | backlog | **Latent API contract**, not current SPA breakage. Publish uses `material_ids` when present; mail HTML/plain follows `blocks` via `compose_digest_segments` / `_html_content_blocks`. AdminDigestPage always derives both from the same `issueBlocks`, so preview/send honesty holds on the product path. Fix (reject conflicting orders or unify on blocks) is a follow-up plan — not required for Phase 13 verify. |
| WR-01 | warning | backlog | SPA syncs full approved∩ready into `issueBlocks`; subset preview→send fail is API-only latent. Align contracts in a later hardening plan. |
| WR-02 | warning | backlog | Empty-slug `/materials/` CTA — edge case; FE modal already omits link. Follow-up. |
| WR-03 | warning | backlog | Operator-controlled `SITE_URL`; cheap scheme allowlist deferred. Sandboxed iframe mitigates admin preview. |
| WR-04 | warning | backlog | FE `reading_minutes` null→`1` display default; live DTO usually supplies minutes. Follow-up honesty polish. |
| IN-01 | info | backlog | Mock slug fallback vs backend empty-slug — Playwright-on-mocks parity. |
| IN-02 | info | backlog | Mock `escapeHtml` apostrophe gap — low risk with double-quoted hrefs. |
| IN-03 | info | backlog | Private `_html_content_blocks` import — refactor when shared composition module lands. |

**Blocking for verify:** none (code-review gate is advisory; CR-01 not exercised by current client).
