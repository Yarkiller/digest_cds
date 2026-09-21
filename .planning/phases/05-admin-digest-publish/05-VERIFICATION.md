---
phase: 05-admin-digest-publish
verified: 2026-09-21T15:55:58Z
status: human_needed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
decision_coverage:
  honored: 17
  total: 17
  not_honored: []
advisory_review:
  source: 05-REVIEW.md
  status: issues_found
  critical: 1
  warning: 5
  note: "CR-01 non-atomic claim→publish is advisory only — does not fail must_haves (plan accepted UPDATE WHERE sent_at IS NULL and/or RPC; ADMIN-07 network-failure wording is pre-claim)"
human_verification:
  - test: "Log in as profiles.role=admin on live stack; open /admin/digest"
    expected: "≤5 ranked rows with draft/ready + score/factors or «обоснование недоступно»; employee deep-link shows ForbiddenPage"
    why_human: "Playwright proves mocks; live seed + role promote need operator eyes"
  - test: "Approve ≥1 ready, open email preview, confirm send (StubMailer)"
    expected: "«Отправка записана», archive issue appears, send locks as already-sent; approved draft blocks send"
    why_human: "End-to-end publish+stub mail on shared VM is not covered by unit/in-memory HTTP alone"
  - test: "Open stub/success issue link unauthenticated → login?returnUrl=/issues/{n} → issue"
    expected: "sanitizeReturnUrl keeps same-origin path; lands on published issue after login"
    why_human: "auth.spec covers mock gate; live cookie/session + real issue number needs one manual pass"
  - test: "Acknowledge 05-REVIEW CR-01 risk (claim before publish)"
    expected: "Accept stuck sent_at if publish fails post-claim, or schedule RPC/compensation follow-up"
    why_human: "Quality/reliability finding outside must_have fail criteria; product decision required"
next_action: "Human verification required. Complete the manual tests in the phase's *-UAT.md, then re-run the verify step until status is passed."
next_command: "/gsd-verify-work 05"
---

# Phase 5: Admin Digest Publish Verification Report

**Phase Goal:** Админ triages the weekly shortlist and ships an approved digest to СВА with archive and email link integrity  
**Verified:** 2026-09-21T15:55:58Z  
**Status:** human_needed  
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Roadmap Success Criteria (non-negotiable contract). Plan frontmatter truths were checked as supporting detail under artifacts / requirements — none reduce this set.

| # | Truth | Status | Evidence |
| --- | ------- | ---------- | -------------- |
| 1 | Admin sees ≤5 ranked candidates with draft/ready and scoring factors (or honest «недоступно»); non-admin gets 403 | ✓ VERIFIED | `require_admin` in `deps.py` gates on `profiles.role`; GET `/admin/shortlist` via `get_admin_shortlist` + `honest_factor_labels`; HTTP 403 for employee in `test_http_admin.py`; SPA ForbiddenPage + Playwright `admin.spec.js`; live DB seed ≤5 items |
| 2 | Approve/Reject and batch select-all/top-N persist visibly; send blocked if drafts included or selection empty | ✓ VERIFIED | `set_shortlist_decision` + decision HTTP route; AdminDigestPage `selectAll`/`selectTopN` (TOP_N=3); send disabled on approved drafts / empty ready; unit + Playwright draft-block cases |
| 3 | Preview matches ready selection; failed preview does not count as verified send | ✓ VERIFIED | `preview_digest_email` approved∩ready only; preview never sets `sent_at` (`test_preview_digest.py`, `test_http_admin.py`); SPA `emailPreviewed` only after success; fail preview keeps send locked (`admin.spec.js`) |
| 4 | Successful send updates archive and success UI without uncontrolled duplicates; failure leaves selection and not-sent state | ✓ VERIFIED | `send_digest` claim→publish→StubMailer; message «Отправка записана»; second send `AlreadySentError`→409; draft/empty→400 leave `sent_at` null; unit+HTTP tests green. **Advisory:** post-claim publish failure can stick `sent_at` (05-REVIEW CR-01) — see Advisory Findings |
| 5 | Digest email link reaches issue after login via returnUrl when needed | ✓ VERIFIED | Stub body `/issues/{n}`; success CTA href; `sanitizeReturnUrl` + `auth.spec.js` ADMIN-08 returnUrl + open-redirect rejection |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `backend/.../deps.py` (`require_admin`) | Profile-role admin gate | ✓ VERIFIED | Exists, substantive, used by admin routes |
| `backend/.../routes/admin.py` | shortlist/decision/preview/send | ✓ VERIFIED | Wired in `app.py`; Depends(require_admin) |
| `backend/.../ports/shortlist_repository.py` | Shortlist port | ✓ VERIFIED | get_current_batch / set_decision / claim_sent |
| `backend/.../use_cases/send_digest.py` | Publish-on-send | ✓ VERIFIED | Ordering publish then mailer; `/issues/{n}` |
| `backend/.../use_cases/preview_digest_email.py` | Preview DTO | ✓ VERIFIED | approved∩ready |
| `backend/.../infrastructure/stub_mailer.py` | StubMailer + smtp fail-fast | ✓ VERIFIED | `resolve_mailer` raises on smtp |
| `web/src/pages/AdminDigestPage.jsx` | Triage UI | ✓ VERIFIED | Role gate, checkboxes, preview/send |
| `web/src/pages/ForbiddenPage.jsx` | 403 copy | ✓ VERIFIED | «Недостаточно прав» + «На выпуск» |
| `web/src/services/adminApi.js` | Admin HTTP client | ✓ VERIFIED | shortlist/decision/preview/send |
| `supabase-integration/migrations/005_phase5_admin_shortlist.sql` | Delivery cols + seed + RPC | ✓ VERIFIED | File + live columns confirmed via Supabase query |
| `supabase-integration/.../shortlist_repository.py` | Live adapter | ✓ VERIFIED | Wired in `live.py` with service_role client |
| `docs/agents/local-platform-runbook.md` §4e | Stub/seed/admin promote | ✓ VERIFIED | Section present |
| `tests/admin.spec.js` | Playwright honesty gate | ✓ VERIFIED | 403, top-3, preview, send, already-sent |
| `tests/unit/test_http_admin.py` + `test_send_digest.py` | Backend contracts | ✓ VERIFIED | 37 related unit tests passed this run |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `POST /admin/shortlist/preview` | `preview_digest_email` | `require_admin` | ✓ WIRED | `admin.py` → use-case; no `sent_at` mutation |
| `POST /admin/shortlist/send` | `send_digest` → publish + StubMailer | claim then mail | ✓ WIRED | Claim UPDATE `sent_at IS NULL`; then `issues.publish`; stub body |
| `AdminDigestPage` | `adminApi` | fetchShortlist / setDecision / previewEmail / sendDigest | ✓ WIRED | Services + route `/admin/digest` in `App.jsx` |
| `create_service_role_client` | `SupabaseShortlistRepository` | `build_live_container` | ✓ WIRED | `live.py` lines shortlist=…, mailer=resolve_mailer |
| Migration 005 | live `digest_shortlist_*` | operator apply | ✓ WIRED | Live query: batch `week_start=2026-09-15`, delivery columns present, 5 items |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| AdminDigestPage rows | `items` from `fetchShortlist` | GET `/admin/shortlist` → ShortlistRepository | Yes (live Supabase or in-memory/mocks) | ✓ FLOWING |
| Preview modal | `previewEmail()` | `preview_digest_email` over current batch | Yes (approved∩ready) | ✓ FLOWING |
| Send success CTA | `issue_url` | `send_digest` after `issues.publish` | Yes (`/issues/{n}`) | ✓ FLOWING |
| Live delivery cols | `delivery_status` etc. | Migration + RPC OR Python claim | Partial — Python path does not stamp delivery cols (advisory WR-01) | ⚠️ HOLLOW (columns exist; Python path leaves NULL after send) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Send/preview/HTTP admin + factors | `uv run pytest tests/unit/test_send_digest.py test_preview_digest.py test_http_admin.py test_score_factors.py test_set_shortlist_decision.py test_phase5_migration_005.py -q` | 37 passed | ✓ PASS |
| Live adapter + StubMailer wiring | `uv run pytest tests/unit/test_supabase_shortlist_repository_contract.py test_live_container_wiring.py test_stub_mailer.py -q` | 19 passed | ✓ PASS |
| Live schema/seed | Supabase `digest_shortlist_batches` + `items` query | batch id=1 unsent; 5 ranks; delivery cols exist | ✓ PASS |
| Playwright admin flows | Existence: `tests/admin.spec.js` (not re-run full e2e suite) | Specs present; no `.skip` | ✓ PASS (existence) |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| ADMIN-01 | 05-01, 05-04, 05-05, 05-06 | ≤5 shortlist; non-admin 403; empty honesty | ✓ SATISFIED | HTTP 403, SPA Forbidden, empty Playwright, live ≤5 seed |
| ADMIN-02 | 05-02, 05-04 | Approve/Reject persist | ✓ SATISFIED | `set_shortlist_decision` + UI captions |
| ADMIN-03 | 05-02, 05-03, 05-04 | draft/ready badges; draft blocks send | ✓ SATISFIED | DTO field + DraftInSendPoolError 400 + UI hint |
| ADMIN-04 | 05-03, 05-04, 05-06 | Preview matches ready; fail ≠ verified | ✓ SATISFIED | preview use-case + SPA gate + Playwright |
| ADMIN-05 | 05-01, 05-04 | ≥2 factors or «обоснование недоступно» | ✓ SATISFIED | `honest_factor_labels` + UI `factorText` |
| ADMIN-06 | 05-04, 05-06 | Select-all / top-N; manual uncheck keeps others | ✓ SATISFIED | AdminDigestPage + Playwright |
| ADMIN-07 | 05-03, 05-04, 05-05, 05-06 | Confirm send, archive, 409, pre-claim failure unsent | ✓ SATISFIED | send_digest + 409 + tests; StubMailer honesty |
| ADMIN-08 | 05-03, 05-06 | Email `/issues/{n}` + returnUrl after login | ✓ SATISFIED | Stub body + auth.spec ADMIN-08 |

**Orphaned requirements:** none — all Phase 5 IDs appear in plan frontmatter.

### Decision Coverage

All trackable CONTEXT.md decisions are honored by shipped artifacts (17/17). Gate non-blocking.

### Test Quality Audit

| Test File | Linked Req | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| `tests/unit/test_http_admin.py` | ADMIN-01…08 | yes | 0 | no | Behavioral/HTTP | PASS |
| `tests/unit/test_send_digest.py` | ADMIN-03/07/08 | yes | 0 | no | Behavioral | PASS |
| `tests/unit/test_preview_digest.py` | ADMIN-04 | yes | 0 | no | Value | PASS |
| `tests/unit/test_score_factors.py` | ADMIN-05 | yes | 0 | no | Value | PASS |
| `tests/admin.spec.js` | ADMIN-01/04/06/07/08 | yes | 0 | no | Behavioral (mock) | PASS |
| `tests/auth.spec.js` | ADMIN-08 | yes | 0 | no | Behavioral (mock) | PASS |

**Disabled tests on requirements:** 0  
**Circular patterns detected:** 0  
**Insufficient assertions:** 0 blockers (Playwright is mock-harness — flagged for human live UAT, not test-quality BLOCKER)

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `send_digest.py` | 79–102 | Claim before publish (non-atomic vs RPC) | ℹ️ Advisory (CR-01) | Publish failure after claim → stuck `sent_at` / 409; not a must_have FAIL per plan `and/or` claim path |
| `shortlist_repository.py` | 122–151 | claim_sent does not call `claim_and_publish_digest` | ℹ️ Advisory (WR-01 related) | Delivery columns stay NULL on Python path |
| `005_…sql` seed rank 1 | ~165 | `factors: []` with flat labels | ℹ️ Advisory | `honest_factor_labels` prefers empty `factors` list → first seed row shows «обоснование недоступно» despite flat keys |

No `TBD`/`FIXME`/`XXX` debt markers in phase key production files.

### Advisory Findings (05-REVIEW.md — do not fail solely on these)

From `05-REVIEW.md` (`status: issues_found`, 1 critical / 5 warning):

1. **CR-01 (critical, advisory here):** Live send claims `sent_at` before `IssueRepository.publish`; migration RPC `claim_and_publish_digest` unused. Must_haves accept atomic claim via `UPDATE … WHERE sent_at IS NULL` **and/or** RPC — claim concurrency is met; full claim+publish atomicity is a hardening gap.
2. **WR-01:** Delivery columns never written by Python claim path (live batch currently `delivery_status=null`).
3. Other review warnings (demo factors shape, in-memory `sent_at` edge cases, SPA `issue_url` sanitization) — tracked as follow-ups, not must_have failures.

### Human Verification Required

### 1. Live admin shortlist

**Test:** Log in as `profiles.role=admin` on live stack; open `/admin/digest`. Employee deep-link `/admin/digest`.  
**Expected:** ≤5 ranked rows with draft/ready + factors or honesty copy; employee sees «Недостаточно прав» + «На выпуск».  
**Why human:** Playwright uses mock harness; live seed/role need confirmation.

### 2. Live preview + stub send

**Test:** Approve ≥1 ready (no approved drafts), preview email, confirm send.  
**Expected:** «Отправка записана», issue in archive, send locked; approved draft keeps send disabled.  
**Why human:** Shared-VM publish + StubMailer side effects.

### 3. ADMIN-08 returnUrl on live issue

**Test:** Unauthenticated open of `/issues/{n}` (or login with `returnUrl=/issues/{n}`).  
**Expected:** Login then land on published issue; `//evil` rejected.  
**Why human:** Real session + real issue number.

### 4. CR-01 product acknowledgment

**Test:** Decide accept stuck-claim risk vs schedule RPC/compensation.  
**Expected:** Explicit accept or follow-up ticket.  
**Why human:** Reliability trade-off outside automated must_have fail criteria.

### Gaps Summary

No must-have gaps. Automated roadmap truths and ADMIN-01…08 are satisfied in code with unit/HTTP evidence; migration 005 is live. Status is **human_needed** solely for live/visual UAT and advisory CR-01 acknowledgment — not `gaps_found`.

---

_Verified: 2026-09-21T15:55:58Z_  
_Verifier: Claude (gsd-verifier)_
