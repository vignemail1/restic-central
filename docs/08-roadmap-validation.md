# Roadmap and validation strategy

Status: proposed plan; no milestone completed or deadline guaranteed.

## Phase 0 — design

Validate decision-register directions; resolve authentication, persistence, scheduling, and Restic compatibility. Produce a configuration schema, OpenAPI contract, and testable transition table.

Exit criterion: critical ambiguities addressed, MVP scope accepted, test criteria defined.

## Phase 1 — agent engine

Validated configuration, secret references, prerequisites, Restic execution, locking, JSON parsing, per-destination results, and local journal. Test only with disposable repositories and synthetic data.

## Phase 2 — coordination

Agent identities, versioned policies, scheduler, transactional acquisition, heartbeat, outbox, and reconciliation. Prevent duplicates without promising exactly-once execution in all circumstances.

## Phase 3 — monitoring

Incidents, time limits, missed occurrences, first notification provider, 24-hour summary, 7-day report, and minimal dashboard.

## Phase 4 — experimental hardening

Audit, failure tests, resource limits, server backup, operator documentation, packaging, and compatibility matrix. This phase alone does not justify a production-ready claim without explicit review.

## Extensions

Additional providers, autonomous mode, copy replication, controlled maintenance, restore tests, validated macOS support, advanced administrator authentication, and potential HA. Each extension needs risk analysis.

## Test strategy

- Unit: validation, argument compilation, exit-code translation, aggregation, transitions, time-window calculations, and scheduling across daylight-saving changes.
- Contract: authentication, authorization, idempotence, pagination, invalid payloads, and out-of-order events.
- Integration: actual Restic binary and disposable repository; backup, incomplete result, restore, and check.
- Resilience: API outage after Restic finishes, crash before/after acknowledgment, duplicates, full disk, agent restart, expired reservation, and late result.
- Concurrency: simultaneous requests, restart during backup, multiple scheduler workers, and concurrent maintenance.
- Security: secret leakage, unauthorized paths/URLs, payload size, rotation/revocation, and agents attempting access to another agent's jobs.
- Notifications: deduplication, recovery, unavailable channel, retries, and summaries including older open incidents.

## Priority acceptance criteria

1. Two simultaneous requests do not run two backups through the same agent.
2. A backup completed during API downtime reports its result after reconnect without repeating the backup.
3. An incomplete result is never presented as complete success.
4. An occurrence that never starts is visible as an anomaly.
5. An unreachable agent is not automatically declared a stuck process.
6. Each destination has an identifiable result and metrics.
7. Changed configuration does not alter existing job history.
8. Retries do not artificially increase the successful-job count.
9. A restore test verifies expected content.
10. No real secret appears in logs, reports, commits, or notifications.

## Proposed quality controls

For Go: formatting, go vet, tests, race detector, and configured linting. For any added Bash: ShellCheck. For documentation: Markdown lint, YAML validation according to example status, relative-link checks, and secret detection. CI must run these controls; no lint results are currently claimed.

## Potential production qualification

Require security review, contract versioning, tested compatibility, documented migrations and rollback, restore tests, observability, reproducible installation, and incident procedures. Production qualification requires an explicit decision; it must never follow automatically from documentation existing.
