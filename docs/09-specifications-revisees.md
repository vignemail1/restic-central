# Revised specifications

Revision: 2026-10-19. Status: design only, NOT PRODUCTION READY. No behavior is implemented.

This document supplements the initial design and takes precedence where the topics below conflict. Requirements come from the project owner; details marked PROPOSAL remain subject to validation. Decisions explicitly validated on 2026-10-19 are recorded in [the decision register](07-decisions.md) and [validated development decisions](16-decisions-for-development.md). Acceptance of a scoped rule does not validate adjacent proposals.

## 1. Profiles and filesets

A machine has multiple backup profiles. Each profile has a stable identifier, versioned configuration, include/exclude fileset, destinations, hooks, interval, and retention rules.

The model becomes Agent -> BackupProfile -> ConfigRevision -> Job -> Attempt -> DestinationResult. BackupProfile refines the initial BackupPolicy concept; shared policy templates remain possible without confusing an executed profile with a shared template.

Every event and report identifies machine and profile. The required lock remains machine-wide: two profiles must not execute backups simultaneously through the agent. Overlapping work is queued or reported according to a policy yet to be defined, never silently ignored.

## 2. Activation, suspension, and maintenance

A machine or profile schedule can be disabled or suspended.

PROPOSAL: disabled means stopped without a resumption deadline; suspended means a suspension with start, optional end, reason, and author. Machine suspension applies to all profiles. An enabled profile cannot bypass a disabled machine.

The scheduler does not trigger occurrences within planned downtime. Reporting distinguishes planned maintenance, missed execution, and failure. Expected machine-absence alerts must account for maintenance without masking errors that actually occurred.

PROPOSAL: suspension does not kill an already active job. Queued jobs are rechecked before starting; postponements/cancellations are audited. Manual execution during suspension requires an explicit audited override. Validate these rules before implementation.

## 3. Intervals and timestamps

Automatic scheduling uses a per-client/profile interval, defaulting to 24 hours, and a stable timestamp anchor. Client configuration may provide a default interval; a profile may override it.

Nominal occurrences are anchor_timestamp + n * interval_seconds. They are not calculated from the previous backup's finish time, avoiding drift. Occurrence identity: agent, profile, scheduling revision, and nominal timestamp.

PROPOSAL: UTC Unix timestamps in seconds for scheduled times, documented event-time precision, and local monotonic-clock duration measurement. The server separately retains nominal, start, finish, and receipt times.

Reports convert timestamps into datetime with explicitly displayed TZ. A 24-hour interval is a duration, not a promise of the same local time across daylight-saving changes. Cron schedules and the initial example are superseded by this interval model.

Catch-up after downtime, jitter, maximum delay, and anchor-change behavior remain to be specified. PROPOSAL: catch up at most one occurrence instead of replaying an entire backlog. Manual execution does not change the anchor.

## 4. Pre-hooks and post-hooks

Configurations support commands before/after Restic execution: database dumps, file preparation, temporary-data cleanup, or other actions. Hooks are in scope; their initial exclusion is superseded.

PROPOSED contract: executable + args, no implicit shell; ordered list, working directory, environment/secret references, timeout, and execution condition. Any explicit shell must be locally authorized and audited.

Recommended sequence: machine lock -> prerequisites -> pre-hooks -> primary backup -> copies -> post-hooks -> result persistence -> lock release. Copies consume the snapshot, not the prepared source files.

**Validated result rules (scoped):** a configured pre-hook must return 0 before Restic backup starts; without a pre-hook, Restic's exit status determines backup success. Without a post-hook, the job succeeds when Restic succeeds. With a post-hook, the job succeeds if the hook returns 0; a failed post-hook after a successful Restic backup makes the job partial. Preserve individual hook, primary-backup, and replication results.

A failed required pre-hook prevents backup. A cleanup post-hook is attempted after earlier failure only if its configured condition allows it. The status when primary backup and post-hook both fail, multiple-hook aggregation, exact per-step scope and conditions remain open. Cancellation or crash does not guarantee cleanup: document recovery and manual cleanup. The overall limit includes hooks; each hook also has its own limit.

Application consistency is outside scope: the operator is responsible for preparing consistent files through pre-hooks. The product orchestrates and reports; it does not certify database consistency.

## 5. Primary backup and replication

A profile defines a primary repository and replication destinations. After backup, use restic copy on the snapshot specifically identified for that attempt, never an ambiguous latest selection shared across profiles.

Retain the primary snapshot and mappings to copied snapshots per destination; do not assume identical IDs. The agent has the permissions and secret references needed for both repositories involved in each copy.

**Validated:** a job is partial if the primary backup succeeded but replication failed. Copy retries reuse the source snapshot while available; do not repeat backup solely because an API acknowledgment was lost or a copy failed.

Copy concurrency and aggregate results when multiple or optional destinations exist remain open. PROPOSAL: only required copies affect complete success; incomplete snapshots are not replicated by default without an explicit choice. Copies, duration, and volume remain individually visible.

## 6. Client-side retention

**Validated:** retention is configured on the client through Restic directives, with the operator choosing the policy. An expired snapshot that has not been replicated is considered no longer valid and may be deleted under that configured policy. Cached `forget` and `prune` jobs execute while the server is unreachable; results are persisted in the Outbox for later delivery.

The exact directive mapping, profile/repository isolation, primary and replica policies, maintenance windows, stale/superseded cached-job safeguards, and separation of forget/prune remain to be specified and tested before enabling destructive operations. No additional destructive deletion behavior is implied.

## 7. Local agent command

A local operator can trigger a profile outside server scheduling. Illustrative, unimplemented example: restic-central-agent backup run --profile system.

Execution uses the same engine, machine lock, hooks, destinations, secret references, and outbox. It does not run Restic independently of the service.

Identify origin=local_manual, local requester, revision, job, and attempt. If the API is unavailable, use available authorized local configuration, persist the job, and reconcile on reconnect. IDs and events remain idempotent.

PROPOSAL: CLI/service communication through local IPC with OS permissions; no inbound network port required. Define behavior when the service is stopped, permissions, and maintenance overrides. Manual execution is not an additional automatic occurrence.

## 8. TLS and agent authentication

Agent/server communication uses HTTPS/TLS with an individual token; mTLS is optional. When enabled, clarify whether mTLS supplements the token: PROPOSAL, retain the token and require both checks.

Server-certificate verification can be enabled or disabled in client configuration. PROPOSED default: enabled; support custom CAs for private infrastructure.

In unverified mode, the connection remains encrypted but server identity is not properly authenticated: display explicit local and central warnings, audit configuration, and never downgrade automatically after a TLS error. This mode exposes tokens and configurations to active interception.

Tokens are revocable, rotatable, agent-specific, and not logged. Web-operator authentication is separate.

## 9. Static multi-OS Go binaries

Agent and server are statically compiled multi-OS Go programs. Define a GOOS/GOARCH matrix and deliver an artifact per target, not a universal binary. No particular OS support or validated build is claimed at this stage.

PROPOSAL: prefer pure-Go dependencies and disable CGO where compatible; actually verify the absence of dynamic dependencies on each platform. DB, LDAP, TLS, and IPC dependencies must satisfy this objective.

Restic remains a separate executable whose installation, version, and validation must be defined. Static does not mean self-sufficient: configuration, certificates, data, and external integrations remain necessary. Locking, process, path, and service tests are specific to each supported OS.

## 10. Web interface and OpenLDAP

**Validated initial authentication scope:** OpenLDAP users using `posixAccount` with a configurable search filter, and local accounts including a local superadmin. Every operator action must be audited, including login, logout, modifications, creation, and agent enrollment.

The exact user search/bind procedure, base DN, optional group mapping, role assignment, TLS requirements, secure sessions, authorization checks, audit tamper resistance and retention remain to specify. Successful LDAP authentication does not imply administrator privileges. Emergency-account recovery and LDAP outages remain to be addressed. Protect web actions against CSRF.

## 11. Consistent server export

The server schedules a consistent export of configuration, database, and recovery material into a local directory. It can also be triggered through the web interface or local CLI; illustrative example: restic-central-server export create.

**Validated:** PostgreSQL export must be consistent and sufficient to restore complete server PostgreSQL state after total database loss. Coordinate the dump with server configuration and recovery material as required; full restoration must be tested. Backup of the export directory by another process is outside scope. The export is not a backup of Restic repositories.

PROPOSAL: one engine for all three origins, an export lock, and a transactional snapshot or native method appropriate to the database; do not arbitrarily copy live database files. Capture a configuration revision consistent with the database.

Write to a temporary location, produce a manifest with format version, timestamp, revisions, and checksums, then atomically publish a complete export. Do not announce success before finalization; use restrictive permissions, audit, and visible errors.

Document included/excluded secrets and external references needed for restoration. PROPOSAL: interval-based scheduling; directory, interval, export retention, and encryption remain undecided. Restore tests must cover configuration, identities, and jobs without replaying old executions.

## 12. Sizing and reporting

Target: one year of jobs for 300 client machines. Multiple profiles, copies, retries, and events may multiply data volume. This is not a measured capacity.

For one daily profile per machine, illustrative baseline: 109500 jobs over 365 days, excluding manual launches. Size using the sum of all profile frequencies; count attempts, results, hooks, logs, and events separately.

Define a reproducible load dataset with profiles per machine, frequency, copy fan-out, event volume, and history. Then define API/reporting latency goals, database space, and purge procedures. One year of jobs does not automatically set detailed-log retention.

Keep default 7-day reports and 24-hour summaries, filterable by machine/profile/destination. Display datetime and TZ, planned maintenance, automatic/manual origin, hook results, and copies. Attempts do not inflate job counts; replication is not a new independent source backup.

## 13. Revised validation and roadmap

The validated delivery order is recorded in [the roadmap](08-roadmap-validation.md). Add tests for concurrent profiles; machine-suspension precedence; suspended queued jobs; resumption without anchor drift; offline manual execution; failed pre-hook and cleanup; failed copy without new backup; per-profile retention isolation; verified/unverified TLS/private CA/mTLS; revoked token; LDAP and roles; export concurrent with DB writes and restoration; builds and processes on each OS; annual load for 300 machines.
