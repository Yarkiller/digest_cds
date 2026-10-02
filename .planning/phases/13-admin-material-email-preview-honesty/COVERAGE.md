# Phase 13 — API Coverage Decision

**Decision:** No external API / SDK integration in this phase.

**Reason:** Phase 13 extends existing in-repo admin shortlist + StubMailer preview/send paths and FE admin chrome. No new third-party HTTP/SDK clients; email HTML is composed in-process with Python stdlib `html.escape`. Live SMTP remains deferred to v1.3.

**OPT-OUT:** N/A — full-coverage matrix not required when no external API is in scope.
