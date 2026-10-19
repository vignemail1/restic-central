# Domain glossary

Design phase — **NOT PRODUCTION READY**. Revision: 2026-10-10.

This file is the canonical source for domain terminology. Other documents should link here rather than duplicate definitions. The conceptual models and cardinalities in [Models, relationships, and invariants](15-modeles-relations.md) remain proposals; they are neither a delivered SQL schema nor implicit approval of every rule.

## Identity and configuration

| Term / model | Definition |
|---|---|
| Machine | Stable identity of the backed-up host; owns its profiles and repositories. It is not simply the hostname. |
| Client / agent / Agent | Program running on the machine to synchronize schedules, execute Restic, and report results. Its enrollment identity may change without necessarily changing the machine. |
| Server | Go coordination, API, web, and reporting program using PostgreSQL. It is not the backup repository. |
| Profile / BackupProfile | Definition of a machine backup: fileset, destinations, hooks, options, and retention. |
| Fileset / FileSet | Selection of included sources and exclusions. It is configuration, not a list of files actually backed up. |
| Policy | Generic term that must be qualified, e.g. retention or maintenance policy. BackupPolicy initially referred to the profile; use BackupProfile for the executed instance. A shared profile-template model is not yet defined. |
| Revision / ConfigRevision | Immutable version of the effective configuration used by an execution. New configuration does not alter previous executions. |
| Secret reference / SecretReference | Identifier used to resolve a secret, not its value. Distinguish API tokens, backend credentials, and the Restic secret. |
| Hook / HookDefinition | Configured action before or after operations; HookResult is its execution result. A hook alone does not guarantee application consistency. |

## Repositories and snapshots

| Term / model | Definition |
|---|---|
| Repository | Restic repository owned by one machine. A storage backend may host multiple isolated repositories. |
| Backend | Storage service or protocol; it does not represent machine ownership or a snapshot. |
| Destination / ProfileDestination | Association between a profile and repository, with a primary or replication role and a required/optional rule. The role belongs to this association. |
| Snapshot / SnapshotRecord | Backup point identified in a repository; the server stores metadata and associations only, not a file inventory. |
| Replication / copy | Copy of a snapshot from one repository to another repository owned by the same machine; distinct from rereading the sources. |
| Replica | Snapshot present at a replication destination; its ID is not assumed to equal the primary snapshot ID. |
| Retention / RetentionPolicy | Rules determining which snapshots are kept; does not by itself specify when cleanup occurs. |
| forget | Operation that removes selected snapshots; distinct from physically deleting data that is no longer needed. |
| prune | Operation that cleans up repository data no longer needed; it does not mean applying a profile retention policy. |
| check | Repository verification operation; specify whether it is structural or reads data, and its scope. |
| stats / RepositoryObservation | Dated repository-statistics collection, qualified by mode and selection; repeated collections are not volumes to add together. |

## Scheduling and execution

| Term / model | Definition |
|---|---|
| Schedule | Rule calculating future occurrences: an anchored interval or a daily time with a time zone. |
| Planning / PlanningRevision | Versioned set of tasks calculated by the server and distributed to a client. It is not an autonomous client scheduler. |
| Occurrence | Logical schedule deadline with a unique identity and deduplication. |
| Job | Logical requested, scheduled, or manual work with a target and configuration. Retries are not new jobs. |
| Attempt | Execution attempt for a job. A job may require multiple attempts. |
| Step / Operation | Unit executed during an attempt, such as a pre-hook, backup, copy, or post-hook. A proposed model for composite jobs. |
| Destination result / DestinationResult | Result of an operation on a specific repository, with code, state, optional snapshot, and metrics. |
| Dependency / JobDependency | Condition between jobs, such as a check after prune. A directed, acyclic relationship. |
| Reservation / lease | Temporary coordination authorization; its expiration does not prove a Restic process has stopped. |
| Lock | Execution exclusion at machine, repository-coordination, or Restic level. These levels are not interchangeable. |
| Suspension / MaintenanceWindow | Planned prevention of starts for a machine, profile, or repository, with explicitly defined scope. |
| Disablement | Stops scheduling without implicit automatic resumption. It is not deletion of the object. |

## Observation and operations

| Term / model | Definition |
|---|---|
| Event / Event | Timestamped fact transmitted idempotently; occurred_at and received_at have distinct meanings. |
| Outbox | Local storage of events awaiting delivery, retained until acknowledged. It is not the server history. |
| Heartbeat | Agent-presence signal; not proof of backup progress. |
| Execution state | Work result or progress, such as running, succeeded, partial, or failed. |
| Observation state | What the server knows, such as reachable, unreachable, or uncertain; it does not prove the actual result. |
| Complete success | Result satisfying the job's success rule; aggregation of primary, copies, and hooks remains to be formalized. |
| Incident / Incident | Tracked anomaly through resolution; acknowledging is not resolving. |
| Notification / NotificationDelivery | Delivery of an incident message or summary; delivery failure does not change the backup result. |
| Report | View calculated over a period and machine/profile/repository dimensions; specify the population and denominator. |
| Export / ServerExport | Consistent local copy of server state for external backup; not a backup of Restic repositories. |
| Operator / Operator | Human identity with application roles; distinct from an Agent and its token. |
| Audit / AuditEvent | Record of an administrative or sensitive action, distinct from Restic progress. |

## Important distinctions

A job can succeed without creating a new snapshot. A copy can fail while the primary backup succeeds. An unreachable agent may have completed a job. Machine maintenance is not repository maintenance. A server export is not an application restore. A missing counter is not zero.

## Related documents

Document 10, on options and statistics, is not published in the repository. Its contents cannot be treated as available specifications; consult existing documents and explicitly validate any proposal before implementation.
