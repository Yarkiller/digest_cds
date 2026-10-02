---
phase: "11"
slug: "address-tech-debt-captions-diagnostics-and-persist-error-cla"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-02"
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests/unit"]`) |
| **Quick run command** | `uv run pytest tests/unit/test_captions_error_mapping.py tests/unit/test_youtube_transcript_adapter.py tests/unit/test_supabase_draft_persister_contract.py tests/unit/test_persist_idempotency_overflow.py tests/unit/test_phase11_migration_009.py -q` |
| **Full suite command** | `uv run pytest tests/unit -q` |
| **Estimated runtime** | ~30–90 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quick run command (or the touched-file subset)
- **After every plan wave:** Run `uv run pytest tests/unit -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | CAP-02 / D-04 | T-11-01 | CookieInvalid → unknown_captions_error; no SDK in message | unit | `uv run pytest tests/unit/test_youtube_transcript_adapter.py tests/unit/test_captions_error_mapping.py -q` | ✅ / ❌ W0 CLI | ⬜ pending |
| TBD | TBD | TBD | CAP-02 / D-01 | T-11-01 | message free of proxy/SDK secrets | unit | `uv run pytest tests/unit/test_captions_error_mapping.py -q` | ✅ | ⬜ pending |
| TBD | TBD | TBD | CAP-02 / D-05 | T-11-01 | Captions failure → JSON stderr, no Traceback | unit | CliRunner contract | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PERS-02 / D-06 | T-11-02 | `23514` → batch_creation_failed | unit | persister contract | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PERS-02 / D-06 | T-11-02 | int HTTP code → rpc_error | unit | persister contract | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PERS-02 / D-07 | — | PERSIST_REASONS unchanged | unit | mapping freeze | ✅ pattern | ⬜ pending |
| TBD | TBD | TBD | CLI-02 / D-08–D-09 | T-11-03 | Sent-batch conflict → already_saved true (SQL) | unit | `test_phase11_migration_009.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CLI-02 / D-08 | T-11-03 | Fake overflow path returns already_saved | unit | invert overflow test | ✅ flip | ⬜ pending |
| TBD | TBD | TBD | CLI-04 | — | Checkmarks on success re-run | unit | CliRunner re-run | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Planner fills concrete Task IDs / Plan numbers when PLAN.md files are written.*

---

## Wave 0 Requirements

- [ ] `tests/unit/test_supabase_draft_persister_contract.py` — cases for `code="23514"` → batch error; `code=503` (int) → rpc_error; keep `check_violation` case
- [ ] `tests/unit/test_phase11_migration_009.py` — offline SQL: conflict fallback without exclusive `sent_at is null` raise; `'already_saved', true`; no second insert; grants pattern
- [ ] Invert `tests/unit/test_persist_idempotency_overflow.py::test_rerun_when_only_sent_batch_exists_raises_batch_creation_failed` (+ fake persist conflict branch)
- [ ] Optional: CliRunner captions failure → stderr JSON `unknown_captions_error`, stdout without Traceback
- [ ] Framework install: none — pytest already available

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Migration 009 applied on shared VM | CLI-02 / D-09 | Shared Studio apply; no CI migrate | Human applies `009` via Studio/`psql`; confirm RPC returns already_saved on sent-batch-only re-run |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
