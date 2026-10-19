# Roadmap and validation strategy

Status: delivery order validated by the project owner on 2026-10-19; no milestone completed, implementation delivered, or deadline guaranteed. Decisions are recorded in [the decision register](07-decisions.md) and [validated development decisions](16-decisions-for-development.md). Each step has its own tests and acceptance criteria. The project remains design-only and NOT PRODUCTION READY until implementation and explicit qualification.

## Delivery sequence

1. **Autonomous agent:** manually supplied configuration, hooks, execution through system crontab or systemd timer, and durable job-state records in the Outbox. No server enrollment is required in this step.
2. **Server enrollment:** implement server-side agent enrollment.
3. **Agent enrollment:** add agent-side enrollment.
4. **Server job reporting:** implement server receipt and persistence of job information.
5. **Agent job reporting:** add agent delivery of job information through the Outbox.
6. **Server agent configuration:** implement server-side configuration management and delivery.
7. **Agent auto-configuration:** fetch and apply configuration from the configuration endpoint.
8. **Server scheduling:** implement server-managed scheduling and future BackupJob assignment.

“Autonomous” in step 1 refers to locally configured execution using the operating-system timer/crontab, not approval for a separate autonomous scheduling mode in the enrolled system. Hooks are in scope from step 1. Retention jobs must not be enabled until their destructive-operation safeguards and acceptance tests are satisfied.

## Step exit gates

Each step must define and pass its own tests before the next integration is treated as complete. At minimum:

- **1 — Agent:** configuration validation; pre-hook failure prevents Restic; Restic and post-hook exit-code aggregation according to the validated rules; partial results for failed replication and failed post-hook after successful backup; machine lock; timer/crontab invocation; Outbox durability across restart and server outage; no secret leakage.
- **2–3 — Enrollment:** authentication, identity binding, duplicate/re-enrollment behavior, revocation/replacement, and failure/retry tests on both server and agent sides.
- **4–5 — Reporting:** versioned-contract validation, idempotent at-least-once delivery, duplicate/out-of-order events, transactional persistence-before-acknowledgment, offline queueing, and reconnect reconciliation.
- **6–7 — Configuration:** versioned JSON schema validation, immutable configuration revisions, endpoint authorization, compatible/unsupported schema behavior, safe persistence without secrets, and agent restart/reload behavior.
- **8 — Scheduling:** stable occurrence identity, replacement of an unretrieved expired planned job, machine-wide serialization, cancellation reporting when another backup is running, offline/reconnect behavior, and timestamp/time-zone boundaries.

Before declaring the whole system ready for operational use, also test offline `forget`/`prune` with Outbox delivery, retention isolation and stale-job safeguards, failed replication and post-hook partial status, full PostgreSQL export restoration, OpenLDAP `posixAccount` search and local superadmin, complete operator audit, supported OS/architecture builds, and recovery scenarios. Do not claim production readiness from phase completion alone.

## Cross-cutting test strategy

- **Unit:** configuration and schema validation, Restic argument compilation, exit-code translation, hook gating, result aggregation, state transitions, occurrence identity, retention mapping, and time calculations.
- **Contract:** authentication/authorization, version compatibility and unsupported versions, idempotence, pagination where applicable, invalid and oversized payloads, unknown fields, and out-of-order events.
- **Integration:** actual Restic binary and disposable repository; backup, hook execution, copy, check, forget/prune, and restore. Use synthetic data only.
- **Resilience:** API outage after Restic finishes, crash before/after acknowledgment, duplicates, full disk, agent restart, stale planned jobs, unavailable secrets, expired/revoked credentials, and late results.
- **Concurrency:** simultaneous requests, multiple profiles under machine-wide locking, restart during backup, multiple scheduler workers, and concurrent maintenance.
- **Security:** secret leakage, filesystem permissions, safe secret injection, unauthorized paths/URLs, payload limits, token rotation/revocation, LDAP/local role enforcement, audit coverage, and cross-agent isolation.
- **Database/export:** migration compatibility, concurrent writes during export, complete dump and configuration recovery after total database loss, and restore without replaying historical jobs.

## Operational quality controls

For Go: formatting, `go vet`, tests, race detector, and configured linting. For any added Bash: ShellCheck. For documentation: Markdown lint, JSON schema validation, relative-link checks, and secret detection. CI should run the applicable controls; no test or lint results are currently claimed.

Production qualification additionally requires security review, contract/version compatibility, documented migrations and rollback, restore tests, observability, reproducible installation, operator/incident procedures, and an explicit production-readiness decision.