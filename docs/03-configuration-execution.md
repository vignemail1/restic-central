# Configuration and execution

Status: initial design, retained for historical context. Where this document conflicts with [the revised specifications](09-specifications-revisees.md), the revised specifications take precedence. This document is not an independent source of current requirements.

For canonical terminology, see the [domain glossary](14-glossaire.md). For conceptual relationships, see [models, relationships, and invariants](15-modeles-relations.md).

## Configuration separation

Agent configuration: identity, server endpoint, authentication, local storage paths, Restic binary, and local limits.

The initial design described a backup policy with sources, exclusions, repositories, central schedule, constraints, time limits, and optional retention. Current profile requirements are specified in document 09; retain this distinction between historical names and current terminology.

## Illustrative example (historical)

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

Fields and values are provisional. This historical example uses cron and independent destinations, both superseded by document 09 where applicable. Its time limits are not suitable defaults for every environment. Any future configuration format, exclusion semantics, and translation to Restic arguments must be specified and tested.

## Prerequisites

Check required paths, permissions, and expected mounts; do not silently back up an empty directory standing in for a missing volume. Define behavior for each optional or required source.

Define whether backups stay within one filesystem and how symbolic links are handled. For application data, plan consistent dumps or snapshots. Files being modified do not guarantee database consistency.

Hook behavior and safety requirements are covered by document 09; do not treat the initial MVP exclusion as current. Any implementation needs an allowlist, restricted environment, timeout, error handling, and cleanup rules even after failure.

## Multiple destinations

The initial design considered independent backups per repository and sequential destinations. This is superseded by the primary-backup-then-copy direction in document 09. Success aggregation, required versus optional destinations, and incomplete snapshots remain topics to resolve as indicated in the revised specifications and decision register.

Retries should target only necessary operations, preserve traceability, and account for the possibility that another attempt creates a new snapshot.

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

The initial proposal was to flag an anomaly for inspection when a limit is exceeded, not automatically kill Restic. Automatic termination requires a separate decision. Lack of progress alone is not sufficient evidence of a stuck process.

## Locking and recovery

A local OS-level lock covers all agent backups and local commands using the same execution manager. External Restic invocations are not implicitly covered.

The server reserves jobs; maintenance operations are coordinated per repository. Native Restic locks are preserved. No automatic unlock based on a timeout alone.

After restart, inspect persisted attempts and any process still running. A PID alone is insufficient to identify an old process. Do not retry while the previous execution remains uncertain.

## Maintenance

Plan separate jobs for forget, prune, check, copy, and restore tests. Snapshot deletion and destructive maintenance require specific permissions and safeguards.

Validation references:
- https://restic.readthedocs.io/en/stable/040_backup.html
- https://restic.readthedocs.io/en/stable/075_scripting.html
- https://restic.readthedocs.io/en/stable/045_working_with_repos.html

These links are references to verify during implementation; no version compatibility is claimed here.
