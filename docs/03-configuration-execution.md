# Configuration and execution

Status: proposed conceptual schema, not a usable configuration.

## Configuration separation

Agent configuration: identity, server endpoint, authentication, local storage paths, Restic binary, and local limits.

Backup policy: sources, exclusions, repositories, central schedule, constraints, time limits, and optional retention. The server stores secret references; local resolution is preferred.

## Illustrative example

```yaml
schema_version: 1
policy_id: system-backup
revision: 1
sources:
  include: [/etc, /home]
  exclude: [/home/*/.cache]
  required_mounts: [/home]
destinations:
  - id: primary
    backend: s3
    repository: s3:https://storage.example.invalid/backups/system
    required: true
    secrets:
      repository_password: {source: env, name: RESTIC_PASSWORD}
      access_key: {source: env, name: AWS_ACCESS_KEY_ID}
      secret_key: {source: env, name: AWS_SECRET_ACCESS_KEY}
execution:
  strategy: independent
  destination_order: sequential
  success_rule: all_required
  max_runtime: 4h
  timeout_action: alert_only
schedule:
  authority: server
  expression: '0 2 * * *'
  timezone: Europe/Paris
  start_deadline: 1h
  catch_up: latest_only
```

Fields and values are provisional. The example's time limits are not suitable defaults for every environment. Cron syntax, exclusions, and their translation into Restic arguments must be specified and tested.

## Prerequisites

Check required paths, permissions, and expected mounts; do not silently back up an empty directory standing in for a missing volume. Define behavior for each optional or required source.

Define whether backups stay within one filesystem and how symbolic links are handled. For application data, plan consistent dumps or snapshots. Files being modified do not guarantee database consistency.

Future hooks must have an allowlist, restricted environment, timeout, error handling, and cleanup rules even after failure. They are outside the MVP.

## Multiple destinations

Independent strategy: run a backup for each repository. MVP direction: sequential destinations; successive reads may observe different data.

Backup-then-copy strategy: create a primary snapshot and copy it to secondary repositories. This extension must separately handle primary failure, replication, authentication for both repositories, and snapshot identification. Do not assume identical snapshot IDs across repositories.

The job succeeds if every required destination succeeds completely. An optional destination failure remains visible and may open an incident without automatically making the job fail. If a required destination is incomplete, the overall result cannot be succeeded. The exhaustive aggregation table remains to be formalized.

Retries target only necessary operations, preserve traceability, and account for the possibility that another attempt creates a new snapshot.

## Running Restic

Start the process with structured arguments and a controlled environment, without shell-command concatenation. Collect JSON stdout and stderr separately. Preserve the exit code, Restic version, and final summary.

For backup, distinguish complete success from an incomplete snapshot: exit code 3 must not be treated as complete success. Exit-code mappings and JSON fields must be checked against every supported Restic version. Do not apply backup rules indiscriminately to check, copy, or prune.

Parsing errors are explicit; do not invent missing metrics.

## Time limits

- start_deadline: maximum delay before starting.
- max_runtime: maximum total runtime.
- heartbeat_timeout: time without agent contact.
- progress_timeout: time without progress; optional detection.
- termination_grace_period: time between graceful termination and escalation.

Proposed default: exceeding a limit flags an anomaly and requires inspection; it does not automatically kill Restic. Automatic termination is a separate option. Lack of progress alone is not sufficient evidence of a stuck process.

## Locking and recovery

A local OS-level lock covers all agent backups and local commands using the same execution manager. External Restic invocations are not implicitly covered.

The server reserves jobs; maintenance operations are coordinated per repository. Native Restic locks are preserved. No automatic unlock based on a timeout alone.

After restart, inspect persisted attempts and any process still running. A PID alone is insufficient to identify an old process. Do not retry while the previous execution remains uncertain.

## Maintenance

Plan separate future jobs for forget, prune, check, copy, and restore tests. Snapshot deletion and destructive maintenance require specific permissions and safeguards.

Validation references:
- https://restic.readthedocs.io/en/stable/040_backup.html
- https://restic.readthedocs.io/en/stable/075_scripting.html
- https://restic.readthedocs.io/en/stable/045_working_with_repos.html

These links are references to verify during implementation; no version compatibility is claimed here.
