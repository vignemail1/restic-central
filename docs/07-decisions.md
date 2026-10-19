# Decision register

Revision: 2026-10-10, following project-owner validation. Design phase, not production ready.

REQUIREMENT: requested by the owner. ACCEPTED: explicitly validated. PROPOSED: not validated. SUPERSEDED: incompatible initial direction. OPEN: pending decision.

The [revised specifications](09-specifications-revisees.md) are the normative detailed reference for topics they cover. This register records decision status and history, not a competing specification. If a status here conflicts with a detailed rule, stop and resolve the discrepancy before implementation; do not infer acceptance from publication alone.

## Requirements

E01 through E08 remain applicable: Restic, agents/server REST API, server scheduling, destinations and filesets, local lock, signaling jobs requiring inspection, 24-hour notifications, 7-day reporting, and non-production warning.

New requirements: multiple profiles per machine; machine/profile suspension and disabling; pre/post-hooks; configurable TLS verification; static multi-OS Go binaries; local manual execution; web interface with OpenLDAP and roles; consistent local server export; client-configured snapshot retention; primary backup followed by copy.

## P directions

| ID | Status | Decision |
|---|---|---|
| P01 | PROPOSED, AMENDED | Server owns automatic scheduling; local manual execution explicitly allowed. Automatic autonomous mode undecided. |
| P02 | ACCEPTED | Outbound HTTPS polling; no mandatory inbound agent network port. |
| P03 | ACCEPTED | Immutable versioned configurations attached to jobs. |
| P04 | PROPOSED | Repository secrets resolved on agent; notification secrets on server. |
| P05 | ACCEPTED | Persistent outbox, at-least-once delivery, and deduplication. |
| P06 | ACCEPTED | Separate jobs, attempts, and per-destination results. |
| P07 | SUPERSEDED | Primary backup followed by copy rather than independent backups. Overall success rule still to define. |
| P08 | PROPOSED | Separate partial state; observation state distinct from execution. |
| P09 | ACCEPTED | Timeout: alert and inspection, no forced termination by default. |
| P10 | PROPOSED | No automatic unlock based on timeout alone. |
| P11 | ACCEPTED, EXTENDED | Agent/server in Go, static and multi-OS; previous Linux-only restrictions superseded. |
| P12 | PARTIALLY SUPERSEDED | Hooks now in scope. HA and remote restore remain outside the proposed MVP. |
| P13 | ACCEPTED | Immediate incidents, daily summary, and recovery notification. |
| P14 | PROPOSED | Reports by scheduled occurrence, retries separate, missing metrics identified. |

## O decisions

| ID | Status | Decision or remaining question |
|---|---|---|
| O01 | OPEN | Server storage engine and agent-local persistence. |
| O02 | ACCEPTED | HTTPS/TLS with individual token; optional mTLS. |
| O03 | OPEN | Minimum Restic version and compatibility matrix. |
| O04 | ACCEPTED TARGET | One year of jobs for 300 machines; profiles, attempts, events, and load to size. Server RPO/RTO remain open. |
| O05 | ACCEPTED SCHEDULING | Regular intervals, default 24 h, stable timestamp anchor; datetime display with TZ. Exact catch-up policy still open. |
| O06 | OPEN | Primary/copy aggregation, optional destinations, and incomplete results. |
| O07 | ACCEPTED | Application consistency outside scope; hooks may prepare consistent files without a product-level application guarantee. |
| O08 | ACCEPTED SNAPSHOT POLICY | Snapshot retention configured on client. Detailed log/event/audit retention still open. |
| O09 | ACCEPTED SCOPE | Operator web interface, OpenLDAP support, application roles; consistent local export scheduled or manual through web/CLI. UI stack and first provider still open. |
| O10 | OPEN | License, distribution, and updates; static multi-OS Go requirement accepted. |
| O11 | ACCEPTED REPLICATION | Primary backup followed by copy; automatic autonomous mode still open. |

## History and consequences

P02, P03, P05, P06, P09, P11, and P13 were explicitly validated by the project owner. Other proposals do not become accepted merely through publication.

Hooks increase privileges and execution exposure: provide structured commands, local restrictions, time limits, and audit. Unverified TLS is possible but must be clearly marked as degraded. Local execution requires the same locking engine and idempotent server reconciliation.

Server downtime prevents new centrally triggered executions but must not prevent local manual execution using available configuration. Copy failure must not unnecessarily reread sources.

Future decisions must include context, alternatives, owner, date, and consequences; retain superseded decisions.
