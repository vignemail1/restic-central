# Validated development decisions

Date: 2026-10-19. Status: design decisions validated by the project owner; no implementation or tests are implied. This document supplements [the revised specifications](09-specifications-revisees.md) and [the decision register](07-decisions.md). Where it makes a more specific decision, update the register and related specifications in the same change. Do not treat unresolved details below as approved.

## 1. Delivery sequence

Development is incremental; each step must have its own tests and acceptance criteria. The agreed order is:

1. **Autonomous agent:** manually supplied configuration, hooks, execution via system crontab or systemd timer, and durable job-state records in the Outbox.
2. **Server enrollment:** implement server-side agent enrollment.
3. **Agent enrollment:** add agent-side enrollment.
4. **Server job reporting:** implement server receipt and persistence of job information.
5. **Agent job reporting:** add agent delivery of job information through the Outbox.
6. **Server agent configuration:** implement server-side configuration management and delivery.
7. **Agent auto-configuration:** fetch and apply configuration from the configuration endpoint.
8. **Server scheduling:** implement server-managed scheduling and future BackupJob assignment.

The term “autonomous agent” in step 1 means locally configured execution without server enrollment or server scheduling; it does not approve an autonomous server-independent scheduling mode beyond the specified system timer/crontab use.

## 2. BackupJob result semantics

- A job is **partial** when the primary backup succeeds but replication fails.
- If no pre-hook is configured, the Restic backup exit status determines whether the backup operation succeeds.
- If a pre-hook is configured, it must return exit code 0 before the Restic backup is started. A failed pre-hook prevents the backup phase.
- If no post-hook is configured, the job succeeds when Restic succeeds.
- If a post-hook is configured, the job succeeds when the post-hook returns 0; if the post-hook fails after a successful Restic backup, the job is partial.
- Preserve individual hook, primary-backup, and replication results; aggregate job status must not erase step-level outcomes.

The precise status when the primary backup itself fails and a post-hook also fails, and the behavior when multiple hooks or replicas exist, still require explicit specification before implementation of aggregation.

## 3. Server-planned BackupJobs

- The server defines the next BackupJob for an agent.
- If its scheduled slot passes before the agent retrieves that planned job, the server replaces it with a new planned job for the new slot; the stale planned job must not remain executable.
- If a backup is already running when another scheduled job is due to start, the waiting job is marked canceled and the agent reports that cancellation to the server when possible, with a reason/state indicating that another job is already running.

This rule does not define behavior for manually requested jobs, non-backup job types, or an agent offline throughout replacement; specify those cases and idempotent cancellation/reconciliation before implementation. Cancellation of a planned job must not be confused with killing a running process.

## 4. Retention and offline maintenance

- Retention is client configuration expressed through Restic directives; the operator chooses the retention policy.
- An expired snapshot that has not been replicated is considered no longer valid and may be deleted under that configured policy.
- Agent-cached `forget` and `prune` jobs execute even when the server is unreachable. Their results are persisted to the Outbox and delivered when connectivity returns.

The exact Restic directive mapping, profile/repository isolation, pruning schedule, and safeguards against stale or superseded cached jobs must be specified and tested before enabling destructive operations.

## 5. Agent configuration and secrets

- Agent configuration other than secrets is stored in a filesystem hierarchy with restricted access.
- Secret storage must support secure retrieval after a client-machine reboot, including legacy BIOS systems without a TPM, UEFI systems, physical servers, and virtual machines.
- Initially, the project may rely on [fnox](https://fnox.jdx.dev/) for secret storage and provide secrets to Restic or hooks at process launch.

Before implementation, define the supported fnox integration and version, threat model, file/permission requirements, secret injection mechanism that avoids command-line and log exposure, and behavior when secrets cannot be unlocked after reboot. This decision does not claim that fnox has been integrated or independently security-reviewed.

## 6. Versioned JSON contracts

- Agent/server exchanges use versioned JSON data schemas. Every exchange must identify a schema version sufficient to agree on semantics; compatible evolution and unsupported-version behavior must be defined.
- Restic JSON output is not itself the server contract. Relevant Restic JSON data must be included as a nested/preserved payload in the server-defined schema so changes in Restic JSON can be tolerated without making raw Restic output the API contract.
- Agent configuration also follows a JSON schema.
- API contracts must cover the different actions, including backup, check, configuration, and enrollment, as well as job reporting and other supported operations.

Define schema ownership, version negotiation, validation, forward/backward compatibility, unknown fields, payload limits, and raw Restic payload retention/redaction. Publish schemas and contract tests before implementing the corresponding endpoints.

## 7. PostgreSQL, export, and operator access

- Use a current stable PostgreSQL release; record the exact supported/tested version range when selecting it for implementation.
- Server export must be consistent and sufficient to restore the complete server PostgreSQL state from the dump after total database loss. Coordinate the database dump with the server configuration and recovery material as required by the existing export specification; test full restoration.
- Initially, OpenLDAP authorization targets users using the `posixAccount` schema and a configurable search filter. Local accounts must also be supported, including a local superadmin account.
- Audit every operator action, including login, logout, modification, creation, and agent enrollment. Define a tamper-resistant-enough audit persistence and retention policy; never log credentials or secret values.

This does not choose a PostgreSQL major version, LDAP filter syntax/defaults, local-account recovery flow, password policy, role granularity, or export tooling. Those details require specification and tests.

## 8. Tests and gates

Each delivery step above has unit, integration, and failure-path tests appropriate to its scope. In particular, tests must cover Outbox durability across restart and server outage; hook exit-code gating; partial status for failed replication/post-hook; planned-job replacement and cancellation reporting; offline `forget`/`prune` result delivery; schema-version validation; full PostgreSQL restore; LDAP/local authentication; and audit coverage without secret leakage.

No development step is complete merely because the feature compiles. Do not enable destructive retention in production-like environments until isolation, stale-job handling, and restore/recovery tests pass.