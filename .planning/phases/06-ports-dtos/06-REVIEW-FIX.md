---
phase: 06-ports-dtos
fixed_at: 2026-09-26T14:57:15.832Z
review_path: .planning/phases/06-ports-dtos/06-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 3
status: all_fixed
---

# Phase 06: Code Review Fix Report

**Fixed at:** 2026-09-26T14:57:15.832Z
**Source review:** `.planning/phases/06-ports-dtos/06-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (Critical + Warning; Info skipped per `fix_scope: critical_warning`)
- Fixed: 3
- Skipped: 3 (IN-01, IN-02, IN-03 — Info, out of scope)

**Verification:** TDD RED→GREEN for each finding; 53 phase-06 unit tests passed after fixes.

## Fixed Issues

### WR-01: `ports` package barrel omits `TranscriptProvider`

**Files modified:** `data-collection/src/data_collection/ports/__init__.py`, `tests/unit/test_data_collection_public_api.py`
**Commit:** `c91d0cf`
**Applied fix:** Re-export `TranscriptProvider` from `data_collection.ports` alongside `ArticleGenerator`. Added `test_ports_package_exports_transcript_provider`.

### WR-02: `Transcript.language` length bounds apply before strip

**Files modified:** `data-collection/src/data_collection/dto/transcript.py`, `tests/unit/test_transcript_dto.py`
**Commit:** `97f4501`
**Applied fix:** Dropped Field `min_length`/`max_length` on `language`; enforce 2–10 after strip in `_strip_language`. Added assert that `"  zh-Hans  "` constructs as `"zh-Hans"`.

### WR-03: Naive `datetime` accepted for provenance timestamps

**Files modified:** `data-collection/src/data_collection/dto/video_metadata.py`, `data-collection/src/data_collection/dto/material_draft.py`, `tests/unit/test_video_metadata_dto.py`, `tests/unit/test_material_draft_dto.py`
**Commit:** `38b1024`
**Applied fix:** `_require_aware` validators reject timezone-naive `published_at` / `source_published_at`; `None` and aware values still OK.

## Skipped Issues

### IN-01: Duplicated `_strip_non_blank` validators across DTOs
**Reason:** Info — out of `critical_warning` scope.

### IN-02: `FakeArticleGenerator.calls` typed as bare `list[dict]`
**Reason:** Info — out of `critical_warning` scope.

### IN-03: `require_material_draft` parameter type hides the runtime guard
**Reason:** Info — out of `critical_warning` scope.

---

_Fixed: 2026-09-26T14:57:15.832Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
