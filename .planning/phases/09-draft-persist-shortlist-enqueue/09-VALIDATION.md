---
phase: "09"
slug: "draft-persist-shortlist-enqueue"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-27"
---

# Phase 09 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `ingestion-service/pyproject.toml` |
| **Quick run command** | `uv run pytest tests/unit/test_persist_port.py tests/unit/test_persist_mapper.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run the task's `<automated>` verify command
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | PERS-01 | — | ArticleDraft roles field validates against closed set | unit | `uv run pytest tests/unit/test_article_draft_roles.py -x` | ⬜ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `ingestion-service/tests/unit/test_persist_port.py` — port/fake contract stubs
- [ ] `ingestion-service/tests/unit/test_persist_mapper.py` — error mapping stubs
- [ ] `ingestion-service/tests/unit/test_supabase_persist_adapter.py` — adapter contract stubs

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Migration 007 applies cleanly to shared VM | PERS-01 | Shared dev database | Run `supabase db push` or apply migration manually, then insert a test draft via RPC |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
