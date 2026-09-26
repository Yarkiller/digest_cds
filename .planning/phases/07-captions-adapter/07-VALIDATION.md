---
phase: 7
slug: captions-adapter
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-09-26
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | root `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests/unit"]` |
| **Quick run command** | `uv run pytest tests/unit/test_extract_video_id.py tests/unit/test_youtube_transcript_adapter.py tests/unit/test_ingest_error.py -x` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run targeted new unit file(s) with `-x`
- **After every plan wave:** Run `uv run pytest`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-W0 | 01 | 0 | CAP-01/CAP-02 | — | N/A | infra | register `integration` marker; scaffold deps | ❌ W0 | ⬜ pending |
| 07-url | 01 | 1 | CAP-01 | T-07-SSRF | Allowlist YouTube URL forms; reject non-YouTube | unit | `uv run pytest tests/unit/test_extract_video_id.py -x` | ❌ W0 | ⬜ pending |
| 07-cap | 02 | 1 | CAP-01/CAP-02 | T-07-REASON | Locked reason codes; fail-closed CaptionsError | unit | `uv run pytest tests/unit/test_youtube_transcript_adapter.py -x` | ❌ W0 | ⬜ pending |
| 07-map | 02 | 2 | CAP-02 | T-07-PROXY | No proxy URL in error context | unit | `uv run pytest tests/unit/test_captions_error_mapping.py tests/unit/test_ingest_error.py -x` | ❌ W0 | ⬜ pending |
| 07-meta | 03 | 2 | CAP-01 | T-07-SSRF | Canonical watch URL only after id extract | unit | `uv run pytest tests/unit/test_youtube_oembed_adapter.py -x` | ❌ W0 | ⬜ pending |
| 07-fake | 03 | 2 | D-15/D-26 | — | Additive failure catalogs | unit | `uv run pytest tests/unit/test_fake_transcript_provider_failures.py tests/unit/test_fake_video_metadata_provider.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Register `integration` pytest marker; keep default unit-only collection
- [ ] RED tests for `extract_video_id` accept/reject matrix (D-01…D-05)
- [ ] RED tests for transcript adapter language preference + error mapping (mocked SDK)
- [ ] RED tests for oEmbed adapter + MetadataError mapping (mocked httpx)
- [ ] RED tests for `IngestError.to_dict()` envelope
- [ ] RED tests for additive fake failure catalogs (D-15/D-26)
- [ ] Scaffold `ingestion-service` workspace member + `data-collection` deps (`youtube-transcript-api`, `httpx[socks]`, `PySocks`)
- [ ] Extend runbook with `YOUTUBE_PROXY_URL` + optional live tests
- [ ] Assert no Supabase migrations / persist writers / Typer CLI / openai deps in this phase

*Existing infrastructure: pytest + `tests/unit/` covers Phase 6 ports/fakes — extend, do not replace.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live captions via AdGuard SOCKS | CAP-01 | Network + local proxy | Set `YOUTUBE_PROXY_URL=socks5://192.168.1.68:1080`; `RUN_YOUTUBE_INTEGRATION=1 uv run pytest -m integration` per runbook |
| Cloud.ru without proxy → `youtube_blocked` | CAP-02 | Ops confirmation | Document risk; do not “fix” with Whisper |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
