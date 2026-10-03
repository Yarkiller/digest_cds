---
phase: 13-admin-material-email-preview-honesty
source: 13-REVIEW.md
updated: 2026-10-03T09:30:00Z
---

# Phase 13 — Review Disposition

Ledger for the review committed in `abade75` (plans 13-07, 13-08, and post-merge fix `0c6dd13`). Each finding is `open` until triaged. The previous ledger's IDs referred to an earlier review and are superseded by this file.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| WR-01 | warning | open | Welcome toast state lives in the banner effect, so IssuePage's loading-to-ready remount drops a toast that is already on screen and restarts the dismiss timer. |
| WR-02 | warning | open | `armWelcomeToast()` can throw if sessionStorage is blocked, and login/register treat that as a failed sign-in after the session already exists. |
| WR-03 | warning | open | Material preview renders «~1 мин» when `reading_minutes` is missing. |
| IN-01 | info | open | `postPing` has no remaining caller and does not share the sticky `/me` outage flag. |
| IN-02 | info | open | Mock email HTML invents a slug when the backend can emit an empty segment. |
| IN-03 | info | open | Mock `escapeHtml` does not escape apostrophes the way Python `html.escape(..., quote=True)` does. |

**Blocking for verify:** none (code-review gate is advisory).
