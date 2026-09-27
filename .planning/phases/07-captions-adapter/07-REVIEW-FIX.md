---
phase: 07-captions-adapter
fix_iteration: 1
fix_scope: critical_warning
reviewed: 2026-09-27T09:15:00Z
fixed: 2026-09-27T09:30:00Z
---

# Phase 07: Review Fix Report (iteration 1)

**Scope:** `critical_warning` — Critical (CR-*) and Warning (WR-*) only.  
**Source:** `07-REVIEW.md`

## Fixed

| ID | Commit | Summary |
|----|--------|---------|
| CR-01 | `8e2162a` | Safe adapter exception messages (no raw `context`); mappers build `message` from reason + `video_id`; redaction tests assert `message` / `to_dict()["message"]` |
| WR-01 | `f2f397d` | Catch `YouTubeTranscriptApiException` (covers `CookieInvalid` / `CookieError`); unit case for `CookieInvalid` → `CaptionsError` |
| WR-02 | `2c06275` | Strip URL userinfo in `InvalidYouTubeUrl` diagnostics; URL mapper allowlists context + safe message; redaction tests |
| WR-03 | `1373659` | Join caption snippets with space + whitespace normalize; multi-snippet unit test |
| WR-04 | `47554e1` | oEmbed `429` / `5xx` → `MetadataNetworkError` (404/403 stay `MetadataUnavailable`); status parametrization tests |
| WR-05 | `5098bd3` | Coerce non-string `language_code`; wrap `AttributeError`/`TypeError` → `CaptionsError`; unit case for `language_code=None` |

## Skipped (out of scope)

| ID | Reason |
|----|--------|
| IN-02 | Live integration stubs — deferred to Phase 10; not critical_warning |
| IN-03 | Adapter constructor `Any` typing — info only; not critical_warning |

## Auto-resolved by CR/WR fixes

| ID | Notes |
|----|-------|
| IN-01 | Message/envelope redaction assertions added as part of CR-01 |

## Deferred

None.

## Test results

```text
uv run pytest \
  tests/unit/test_captions_error_mapping.py \
  tests/unit/test_metadata_error_mapping.py \
  tests/unit/test_youtube_transcript_adapter.py \
  tests/unit/test_youtube_oembed_adapter.py \
  tests/unit/test_ingest_error.py \
  tests/unit/test_extract_video_id.py
→ 103 passed
```

**Remaining test failures:** none in the fix suite above.

## Commits (newest last)

1. `8e2162a` — `fix(07): CR-01 redact secrets from error messages`
2. `f2f397d` — `fix(07): WR-01 map Cookie and SDK exceptions to CaptionsError`
3. `2c06275` — `fix(07): WR-02 redact URL userinfo from diagnostics`
4. `1373659` — `fix(07): WR-03 join caption snippets with spaces`
5. `47554e1` — `fix(07): WR-04 map oEmbed 5xx and 429 to MetadataNetworkError`
6. `5098bd3` — `fix(07): WR-05 coerce malformed language_code to CaptionsError`

---

_Fixer: gsd-code-fixer · iteration 1 · scope critical_warning_
