---
status: pending
phase: 10-cli-composition-uat
requirement: CLI-03
decisions: [D-13, D-14, D-15, D-16]
source:
  - 10-01-SUMMARY.md
  - 10-02-SUMMARY.md
  - 10-03-SUMMARY.md
  - 10-04-PLAN.md
  - 10-05-SUMMARY.md
started: pending
updated: pending
---

# Phase 10 — Manual UAT (CLI-03)

Four-video matrix (D-14). Operator picks live captioned URLs at UAT time (D-15). Evidence is this note only — **do not add a Playwright test** for `/admin/digest` live UAT (D-13). Do not modify `backend/` or `web/` so drafts appear. Do not paste `SUPABASE_SECRET_KEY` / `DEEPSEEK_API_KEY` into this file (T-10-11).

## Command (CLI-05 / D-02)

```bash
# from repo root — ingestion-service/.env only (never root backend .env)
uv run --env-file ingestion-service/.env ingest <url> --template lecture|podcast
```

See also: `docs/agents/local-platform-runbook.md` §5d.

## Digest checks per row (D-16)

For each video, open `/admin/digest` and confirm:

- [ ] Row is on an **unsent** shortlist batch
- [ ] Material `status=draft`
- [ ] Body is **Russian**
- [ ] English source: provenance label ends with ` · пер. с англ.`
- [ ] Lecture headings present: `## Тезис` / `## Ход рассуждения` / `## Вывод`
- [ ] Podcast headings present: `## О чём разговор` / `## Позиции` / `## Что запомнить`

Optional: re-run one URL — expect `already_saved: true`, exit 0, same `material_id` / `slug`, no duplicate shortlist row (CLI-02).

## Current Test

[awaiting operator]

## Matrix rows

### 1. lecture + ru

| Field | Value |
|-------|-------|
| URL | _pending (chosen at UAT)_ |
| template | `lecture` |
| material_id | _pending_ |
| slug | _pending_ |
| already_saved (first run) | _pending_ |
| /admin/digest (D-16) | _pending_ |

result: pending

### 2. lecture + en

| Field | Value |
|-------|-------|
| URL | _pending (chosen at UAT)_ |
| template | `lecture` |
| material_id | _pending_ |
| slug | _pending_ |
| already_saved (first run) | _pending_ |
| EN provenance ends with ` · пер. с англ.` | _pending_ |
| /admin/digest (D-16) | _pending_ |

result: pending

### 3. podcast + ru

| Field | Value |
|-------|-------|
| URL | _pending (chosen at UAT)_ |
| template | `podcast` |
| material_id | _pending_ |
| slug | _pending_ |
| already_saved (first run) | _pending_ |
| /admin/digest (D-16) | _pending_ |

result: pending

### 4. podcast + en

| Field | Value |
|-------|-------|
| URL | _pending (chosen at UAT)_ |
| template | `podcast` |
| material_id | _pending_ |
| slug | _pending_ |
| already_saved (first run) | _pending_ |
| EN provenance ends with ` · пер. с англ.` | _pending_ |
| /admin/digest (D-16) | _pending_ |

result: pending

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps

[none yet — fill rows during human-verify checkpoint]
