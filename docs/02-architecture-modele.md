# Architecture and data model

Status: proposed architecture, not implemented.

## Components

```text
Administrator -> server interface/API
Server -> configurations, scheduler, jobs, events, incidents, reports
Agent -> outbound HTTPS to server: acquisition and reporting
Agent -> Restic process -> backup repositories
Server -> email / Matrix / Slack providers
```

The server stores coordination metadata. Backup data flows between the agent and repositories; by default, it does not pass through the coordination server.

## Responsibilities

Server: manage identities, immutable configurations, scheduled occurrences, job reservations, observed states, incidents, and notification deliveries.

Agent: validate configuration, resolve local secrets, check prerequisites, acquire a lock, run Restic without an implicit shell, collect output, persist events, and reconcile state after restart.

## Scheduling

MVP direction: the server is the sole execution-trigger authority. The agent retains its configuration but does not independently recreate scheduled occurrences. During a server outage, an already accepted job may continue; no new central job is acquired.

Any future autonomous mode will be explicit and subject to a later decision. Never layer two schedulers without a deduplication protocol.

Each schedule must define an IANA timezone, daylight-saving behavior, permitted execution window, jitter, start deadline, catch-up policy, and maintenance periods. Initial recommendation: catch up at most one relevant occurrence instead of replaying an entire backlog.

## Entities

| Entity | Main information |
|---|---|
| Agent | stable identity, capabilities, version, last contact, enrollment status |
| Repository | backend, location, options, secret references |
| BackupPolicy | sources, exclusions, destinations, schedule, success rules |
| ConfigRevision | immutable content, schema version, fingerprint |
| Job | policy, revision, scheduled time, requester, aggregate state |
| Attempt | job, attempt number, agent, timestamps, state, reservation |
| DestinationResult | repository, operation, Restic exit code, snapshot, metrics |
| Event | identifier, attempt, sequence, type, timestamps, payload |
| Incident | grouping key, opening, acknowledgment, resolution |
| NotificationDelivery | channel, recipient, result, retry |

A Job references the revision actually executed. Policy changes do not rewrite history. A failed attempt and its retry remain separate.

## Execution states

```text
scheduled -> queued -> claimed -> running
                                   -> succeeded
                                   -> partial
                                   -> failed
                                   -> timed_out
                                   -> canceled
```

`skipped` denotes a deliberately ignored occurrence, with a reason. Allowed transitions and their prerequisites must be validated by tests. A late event must not silently regress a terminal state.

## Separate observation state

`healthy`, `unreachable`, `suspected_stuck`, and `reconciliation_required` describe the server's knowledge, not necessarily the process result. An unreachable agent may already have finished its backup. Display the last known state and its timestamp.

## Persistence

The server storage engine remains undecided. Require transactions, uniqueness constraints, migrations, and tested backup and restore procedures. The agent needs persistent local storage for its outbox and attempts. SQLite is an option to evaluate, not an accepted choice.
