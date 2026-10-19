# Decision register

Revision: 2026-10-19, following project-owner validation. Design phase, not production ready.

REQUIREMENT: requested by the owner. ACCEPTED: explicitly validated. PROPOSED: not validated. SUPERSEDED: incompatible initial direction. OPEN: pending decision. PARTIALLY ACCEPTED: only the explicitly stated scope is validated.

The [revised specifications](09-specifications-revisees.md) are the normative detailed reference for topics they cover. This register records decision status and history, not a competing specification. If a status here conflicts with a detailed rule, stop and resolve the discrepancy before implementation; do not infer acceptance from publication alone.

## Requirements

E01 through E08 remain applicable: Restic, agents/server REST API, server scheduling, destinations and filesets, local lock, signaling jobs requiring inspection, 24-hour notifications, 7-day reporting, and non-production warning.

New requirements: multiple profiles per machine; machine/profile suspension and disabling; pre/post-hooks; configurable TLS verification; static multi-OS Go binaries; local manual execution; web interface with OpenLDAP and roles; consistent local server export; client-configured snapshot retention; primary backup followed by copy.

## P directions

| ID | Status | Decision |
|---|---|---|
| P01 | ACCEPTED, AMENDED | Server owns enrolled-agent automatic scheduling; local manual execution is allowed. The validated delivery order starts with a locally configured agent using system crontab/systemd timer, then enrollment/reporting/configuration, and server scheduling. This does not approve independent autonomous scheduling for enrolled agents. |
| P02 | ACCEPTED | Outbound HTTPS polling; no mandatory inbound agent network port. |
| P03 | ACCEPTED | Immutable versioned configurations attached to jobs. |
| P04 | ACCEPTED, LIMITED | Agent configuration excluding secrets is stored in a restricted filesystem hierarchy. Initially fnox may be used for secrets and secrets supplied to Restic/hooks at launch. Secure reboot retrieval is required across the stated hardware; integration, threat model, and injection details remain to specify. |
| P05 | ACCEPTED | Persistent outbox, at-least-once delivery, and deduplication. |
| P06 | ACCEPTED | Separate jobs, attempts, and per-destination results. |
| P07 | SUPERSEDED, REPLACED | Independent backups are replaced by primary backup followed by copy. Current accepted result semantics: a successful primary with failed replication is partial. |
| P08 | ACCEPTED, PARTIAL | A successful primary with failed replication is partial; failed post-hook after successful Restic backup is also partial. Preserve step-level outcomes. Combined failure/multiple-hook/replica aggregation remains open. |
| P09 | ACCEPTED | Timeout: alert and inspection, no forced termination by default. |
| P10 | PROPOSED | No automatic unlock based on timeout alone. |
| P11 | ACCEPTED, EXTENDED | Agent/server in Go, static and multi-OS; previous Linux-only restrictions superseded. Supported target matrix remains to define and test. |
| P12 | PARTIALLY SUPERSEDED | Hooks now in scope. HA and remote restore remain outside the proposed MVP. |
| P13 | ACCEPTED | Immediate incidents, daily summary, and recovery notification. |
| P14 | PROPOSED | Reports by scheduled occurrence, retries separate, missing metrics identified; no explicit owner validation found. |

## O decisions

| ID | Status | Decision or remaining question |
|---|---|---|
| O01 | ACCEPTED, PARTIAL | PostgreSQL is the server database; use a current stable release and provide a consistent, complete export enabling restoration after total database loss. Exact supported version/tooling remain to define. Agent-local persistence remains open. |
| O02 | ACCEPTED | HTTPS/TLS with individual token; optional mTLS. |
| O03 | OPEN | Minimum Restic version and compatibility matrix. |
| O04 | ACCEPTED TARGET | One year of jobs for 300 machines; profiles, attempts, events, and load to size. Server RPO/RTO remain open. |
| O05 | ACCEPTED SCHEDULING, PARTIAL | Server defines the next BackupJob. If its slot passes unretrieved, replace it with a new planned job. If another backup is running at the scheduled start, cancel the waiting job and report cancellation when possible with the already-running reason/state. Offline reconciliation and other job types remain open. Earlier exact catch-up and anchor rules remain as specified only where not in conflict. |
| O06 | ACCEPTED, PARTIAL | Primary success plus failed replication is partial. Hook rules: required pre-hook must return 0 before Restic; without pre-hook Restic exit status decides backup success; without post-hook Restic success means job success; failed post-hook after successful Restic means partial. Preserve step results. Combined failures, multiple hooks/replicas and optional destinations remain open. |
| O07 | ACCEPTED | Application consistency outside scope; hooks may prepare consistent files without a product-level application guarantee. |
| O08 | ACCEPTED, PARTIAL | Retention is configured through client Restic directives, with operator choosing policy. Expired non-replicated snapshots may be deleted. Cached forget/prune jobs execute offline and persist results in Outbox. Directive mapping, isolation, schedule and stale-job safeguards remain to specify before destructive use. |
| O09 | ACCEPTED, PARTIAL | Operator interface, OpenLDAP `posixAccount` users with configurable search filter, local accounts including a superadmin, and audit of every operator action (including login/logout, changes, creation, agent enrollment). Roles, recovery, LDAP details, audit protection/retention remain to specify. Consistent export is also accepted under O01. |
| O10 | OPEN | License, distribution, and updates; static multi-OS Go requirement accepted. |
| O11 | ACCEPTED, EXTENDED | Primary backup followed by copy; enrolled-agent server scheduling remains authoritative. Initial development stage may run a locally configured agent via OS timer/crontab before enrollment. |
| O12 | ACCEPTED, PARTIAL | Agent/server exchanges and agent configuration use versioned JSON schemas; Restic JSON is nested/preserved in server-defined contracts, not itself the API contract. Schema negotiation, compatibility and validation details remain to define. |

## Additional validated decisions

- Delivery sequence and stage gates are recorded in [validated development decisions](16-decisions-for-development.md) and [roadmap](08-roadmap-validation.md).
- A planned BackupJob not retrieved before its slot expires is replaced; a due job is canceled rather than launched concurrently with an already-running backup, with cancellation reported when possible.
- Operator authentication initially supports OpenLDAP `posixAccount` search and local accounts including superadmin; all operator actions are audited.
- No implementation, test pass, security review, or production readiness is implied by acceptance of design decisions.

## History and consequences

P02, P03, P05, P06, P09, P11, and P13 were explicitly validated previously. The owner subsequently validated the scoped changes recorded above; adjacent proposals remain unaccepted unless explicitly listed.

Hooks increase privileges and execution exposure: provide structured commands, local restrictions, time limits, and audit. Unverified TLS is possible but must be clearly marked as degraded. Local execution requires the same locking engine and idempotent server reconciliation.

Server downtime prevents new centrally triggered executions but must not prevent local manual execution using available configuration. Copy failure must not unnecessarily reread sources.

Future decisions must include context, alternatives, owner, date, and consequences; retain superseded decisions.