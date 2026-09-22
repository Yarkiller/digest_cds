# Milestones

## v1 MVP (Shipped: 2026-09-22)

**Phases completed:** 5 phases, 40 plans, 94 tasks

**Delivered:** Corporate auth, the weekly prepared-article issue and archive, one honest vote, knowledge search and разборы, and admin shortlist → preview → send.

**Git range:** `cabd7eb` → `ba8be89` (330 commits, 2026-08-23 → 2026-09-22). 600 files, +77115 / −149 from the initial commit.

**Known verification overrides:** 4 newly acknowledged, 0 carried forward from a prior close (see STATE.md Deferred Items)

**Key accomplishments:**

- Offline FastAPI skeleton: Settings, GET /health, CORS allowlist, request_id middleware, and committed `.env.example`.
- ES256 JWKS verification, corporate email allowlist, and authenticated GET /me with ProfileRepository upsert — offline unit suite green.
- PingRecorder port + in-memory fake and JWT-gated POST /me/ping complete the D-13 Phase 1 API surface offline (PLAT-04 / D-10).
- Supabase profile + ping adapters and env-selected live composition are green offline; Auth dashboard seed is deferred for Plan 01-06 live proof.
- Login via supabase-js services, RequireAuth gated by VITE_USE_MOCKS, and meApi proof banner close AUTH-01/02/03 SPA contracts offline-green.
- PLAT-08 runbooks shipped; live FE↔BE proof human-approved (login → /me → /me/ping → activity_events).
- Self-service `/register` with Логин nickname, slim email+password login, and Playwright contracts closing UAT gap G-01-3.
- Planning and ops docs now match Plan 01-07 self-service registration: signUp INTEGRATE, amended D-08, runbook `/register` + «Логин».
- JWT-protected `GET /issues/current` through ports → in-memory → contentApi → typography IssuePage (hero+TOC or «Выпуск готовится»), with Wave 0 archive/material scaffolds
- Idempotent mock.js→SQL seed on shared VM plus service_role Issue/Material adapters replacing live in-memory content
- JWT-gated archive API + `/archive` reader UX with past IssuePage (no voting callout) and calm «Выпуск не найден» soft empty.
- Ready-only GET /materials/{slug} plus sanitized markdown MaterialPage with TOC and honesty rules (MAT-01/02/03, ISSUE-03).
- Read-only `voting_cycle` on current-issue DTO drives EditorialCallout open/closed/absent on `/` only — no vote write APIs.
- ServiceUnavailable splash (`/bad_gateway.png` + «Ошибочка вышла» + Повторить) with sticky content fail harness and green Phase 2 full Playwright+pytest gate under mocks
- JWT-protected GET/POST `/voting` returns BallotSnapshot via VoteRepository → in-memory, with PersistenceError→503 and InvalidVoteError→400 (D-40, D-52).
- Option-a open-cycle vote trigger + idempotent topic seed (LLM/RAG/AutoML) and live SupabaseVoteRepository wiring via service_role
- Unit-locked get_ballot leaders[] (single/tie/hide-when-zero) and D-48…50 empty/closed BallotSnapshot shapes — production logic already from 03-01; SPA copy deferred to 03-06.
- VOTE-03 complete: A→B upsert, closed/CAS 409+ballot with SPA adopt, mutation ErrorPanel vs GET splash, save toasts — phase voting gate green under mocks.
- SPA votingApi + VotingPage under mocks: honest never-voted UX, confirm-one-vote with D-52 snapshot apply, D-47 pointless-POST guard, no row «Лидирует» (D-40, D-44…47, D-52, D-56).
- Muted server-driven leader strip, shared RU plurals with honest «0 материалов», and D-48…50 closed/empty `/voting` states under Playwright mocks.
- JWT-gated `GET /knowledge/search` via QueryEmbedder → chunk.search → search_knowledge, omitting scores (KNOW-01 / D-59 / D-61).
- KnowledgePage Submit/Enter «Найти» wired to `knowledgeApi.searchKnowledge` under mocks, with blank/overlong inline guards and slug-linked hit rows (KNOW-01 / D-57…D-61).
- Analyst/DS/Все chips filter knowledge search on the server, and an empty analyst result resets only the role without substituting other materials
- JWT-gated `GET /razbory` chronology via RazborRepository → list_razbors, with empty 200 and 503 unavailable (RAZB-01 / D-66 / D-69).
- Razbory chronology SPA at `/razbory` with AppShell «Разборы», ChronologyItem rows (Анонс + editorial byline), and empty CTA to `/voting` only (RAZB-01 / D-66…D-69).
- GET /razbory/{id} + RazborPage ship sticky TOC longread, announcement stub honesty (D-68), and content_kind quality vs Обзор (D-73) without notebook download.
- Authenticated `GET /razbory/{id}/notebook` streams `.ipynb` under NOTEBOOK_ROOT with path containment, and published RazborPage shows honest dual download strips (D-70…72) without regressing announcement stubs.
- Idempotent migration 004 seeds 1024-d knowledge chunks and razbors with hybrid RPC; live composition wires Supabase adapters + StubQueryEmbedder; operator confirmed apply on knowledge-db.ru with NOTEBOOK_ROOT ready.
- Playwright knowledge + razbory honesty suites green under mocks; VALIDATION.md marked wave_0_complete / nyquist_compliant with explicit UI-SPEC backstops.
- Announcement chronology rows no longer expose «Читать разбор →»; they show the honest «готовится» placeholder while published rows keep the read link (G-04-2).
- Ports & Adapters admin shortlist GET behind `require_admin` (profiles.role) plus `/me` app_role alignment to employee/admin
- Approve/Reject via `set_shortlist_decision` + `POST /admin/shortlist/items/{id}/decision` with draft approve allowed and non-admin 403
- Mandatory email preview + StubMailer send that publishes a digest issue once, blocks drafts/empty/already-sent, and embeds `/issues/{n}` for ADMIN-08
- Role-gated Admin Digest triage SPA under mocks: 403 for employees, shortlist chrome with factor honesty, batch Approve/Reject, select-all/top-3, mandatory preview fingerprint gate, and confirm send.
- Idempotent migration 005 (delivery columns + demo shortlist seed) plus SupabaseShortlistRepository and StubMailer live wiring; operator confirmed schema applied on shared VM.
- Phase 5 honesty gate: Playwright covers 403/empty/top-N/preview/send/draft + ADMIN-08 returnUrl; VALIDATION Wave 0 marked complete; stub send surfaces «К выпуску →».
- Intro and ordered blocks reach `preview.body` end-to-end — «Вводный текст» is visible in «Превью письма» (G-05-1).
- Reorderable topic blocks and optional interstitials drive preview composition; `material_ids` permutation becomes publication order while locked send copy stays intact.
- G-05-2 closed: after stub send (or cold `digest_rest`), triage rows/checkboxes hide behind «дайджест успешно выпущен» + «через 7 дней», while locked «Отправка записана» / «Уже отправлено» stay

---
