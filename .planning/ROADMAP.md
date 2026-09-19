# Roadmap: Digest CDS

## Overview

Brownfield path from mock UI + in-memory ports to a production-shaped Digest CDS on Cloud.ru: first make DB, API, auth, security, and FE↔BE real; then ship the editorial reader (issue/materials/archive), voting cycle, knowledge + разборы, and finally admin shortlist→send. Public leaderboard, quizzes, and YAML pipeline UI stay post-v1.

## Phases

- [ ] **Phase 1: Platform Foundation & Auth** - Live Supabase, FastAPI, security, FE↔BE, corporate login
- [ ] **Phase 2: Issue, Materials & Archive** - Current issue, prepared articles, archive
- [ ] **Phase 3: Voting Cycle** - One honest vote, change while open, audit-language ballot
- [ ] **Phase 4: Knowledge & Razbory** - Semantic search, role filters, разбор longread/notebook
- [ ] **Phase 5: Admin Digest Publish** - Shortlist triage, preview, send, email + archive

## Phase Details

### Phase 1: Platform Foundation & Auth

**Goal**: Operators and developers have a working secured stack; СВА users can log in with corporate email and the SPA talks to real APIs
**Depends on**: Nothing (first phase)
**Requirements**: PLAT-01, PLAT-02, PLAT-03, PLAT-04, PLAT-05, PLAT-06, PLAT-07, PLAT-08, AUTH-01, AUTH-02, AUTH-03
**Success Criteria** (what must be TRUE):

  1. Self-hosted Supabase is up with schema/RLS; app secrets are env-only; CORS allows the SPA origin
  2. FastAPI serves health and authenticated domain endpoints without critical errors; structured logs capture failures
  3. User with allowed corporate domain can log in and land on current issue (or returnUrl); disallowed domain never gets a session
  4. Frontend loads at least one protected resource from the server and can POST a mutation that persists
  5. Network/validation errors are handled per global error UX; README/deploy docs successfully bring up local + documented Cloud.ru path

**Plans**: 3/7 plans executed

Plans:

- [ ] 01-PLAN-CHECK.md
- [x] 01-01-PLAN.md — Package gate + public FastAPI (/health, CORS, request_id) + .env.example
- [x] 01-02-PLAN.md — Corporate email + ES256 JWT + GET /me
- [x] 01-03-PLAN.md — POST /me/ping + PingRecorder + composition in-memory
- [ ] 01-04-PLAN.md — Live Supabase adapters, composition, manual Auth seed
- [ ] 01-05-PLAN.md — SPA Auth, RequireAuth, meApi, Playwright auth flows
- [ ] 01-06-PLAN.md — Local/Cloud.ru docs + live FE↔BE proof checkpoint

### Phase 2: Issue, Materials & Archive

**Goal**: Readers open the current editorial issue, read prepared articles (never media-as-material), and revisit past issues
**Depends on**: Phase 1
**Requirements**: ISSUE-01, ISSUE-02, ISSUE-03, ISSUE-04, MAT-01, MAT-02, MAT-03
**Success Criteria** (what must be TRUE):

  1. User opens current published issue with cover/period/title and IssueTOC, or sees honest empty «выпуск готовится»
  2. Voting-cycle EditorialCallout reflects open vs closed state correctly
  3. User reads a material as prose + section TOC with «Статья» badge/provenance/tags/related links as available; unknown id shows editorial 404
  4. Audit-dek appears under title when present; archive opens a past issue or empty-archive CTA to current

**Plans**: TBD
**UI hint**: yes

### Phase 3: Voting Cycle

**Goal**: Each authenticated user casts and may change exactly one vote in an open cycle with transparent ballot UX
**Depends on**: Phase 2
**Requirements**: VOTE-01, VOTE-02, VOTE-03, VOTE-04
**Success Criteria** (what must be TRUE):

  1. Before voting, status is «голос не отдан» with no pre-selected topic; leading topic is separate from personal choice
  2. Confirming a vote stores exactly one vote and shows «Ваш голос:» with topic; empty submit is blocked
  3. Changing A→B while open updates counters/status; after close, change is rejected with closed-cycle message
  4. Topics show audit-language description and material count (including «0 материалов»)

**Plans**: TBD
**UI hint**: yes

### Phase 4: Knowledge & Razbory

**Goal**: Analysts and scientists find materials by meaning and role, and consume разборы with TOC and notebook artifacts
**Depends on**: Phase 2
**Requirements**: KNOW-01, KNOW-02, KNOW-03, KNOW-04, RAZB-01, RAZB-02, RAZB-03, RAZB-04
**Success Criteria** (what must be TRUE):

  1. Semantic search returns relevant hits or honest empty; whitespace-only query does not execute search
  2. Analyst/DS filters behave correctly; analyst empty state never substitutes irrelevant ML tops
  3. Razbor list shows name/date/status (or empty CTA); multi-section разбор has sticky TOC navigation
  4. Notebook download works when attached and is clearly disabled when missing; metrics/overview labeling is honest

**Plans**: TBD
**UI hint**: yes

### Phase 5: Admin Digest Publish

**Goal**: Админ triages the weekly shortlist and ships an approved digest to СВА with archive and email link integrity
**Depends on**: Phase 2
**Requirements**: ADMIN-01, ADMIN-02, ADMIN-03, ADMIN-04, ADMIN-05, ADMIN-06, ADMIN-07, ADMIN-08
**Success Criteria** (what must be TRUE):

  1. Admin sees ≤5 ranked candidates with draft/ready and scoring factors (or honest «недоступно»); non-admin gets 403
  2. Approve/Reject and batch select-all/top-N persist visibly; send blocked if drafts included or selection empty
  3. Preview matches ready selection; failed preview does not count as verified send
  4. Successful send updates archive and success UI without uncontrolled duplicates; failure leaves selection and not-sent state
  5. Digest email link reaches issue after login via returnUrl when needed

**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Platform Foundation & Auth | 3/7 | In Progress|  |
| 2. Issue, Materials & Archive | 0/TBD | Not started | - |
| 3. Voting Cycle | 0/TBD | Not started | - |
| 4. Knowledge & Razbory | 0/TBD | Not started | - |
| 5. Admin Digest Publish | 0/TBD | Not started | - |
