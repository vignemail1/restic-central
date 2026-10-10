# Vision and requirements

Status: design only, not production ready.

## Problem addressed

Centralize the orchestration and observation of Restic backups across multiple clients without necessarily centralizing backup data or repository secrets. Successful process execution alone does not prove application-level recoverability.

## Expressed requirements

- A client receives a configuration, runs Restic, and reports the result through a REST API.
- The server handles reports, schedules execution, and displays results.
- Multiple repositories are supported; each destination describes its type, parameters, and credentials.
- The policy contains included sources and exclusions.
- The client has a reporting endpoint and access credentials.
- A client-side lock prevents two simultaneous backups.
- A time limit identifies a potentially stuck job requiring manual inspection.
- Errors are notified through email, Matrix, Slack, or other providers.
- The error-summary window defaults to 24 hours and is configurable.
- The reporting window defaults to 7 days and is configurable; it includes duration and data-volume metrics.
- The README and documentation must clearly display the project's design-phase status.

## Proposed additional goals

Detect tasks that never start; survive temporary API unavailability; distinguish incomplete backups from fatal errors; track configuration revisions; protect secrets; test restores.

## Terminology

- Agent: the local service responsible for execution.
- Policy: a versioned backup definition.
- Job: a logical occurrence of a policy, scheduled or manual.
- Attempt: one execution attempt for a job.
- Destination: the repository targeted by an operation.
- Incident: a problem tracked over time, distinct from a notification.
- RPO: the target maximum age of recoverable data.

## Proposed initial boundaries

No automatic remote restoration, no highly available scheduler, no full multi-tenancy, and no arbitrary distributed command execution. Application-consistency integrations must be specified before activation.

## Sizing questions

To define before implementation: agent and policy counts, destinations per policy, event frequency, log size, retained history, API throughput, acceptable downtime, and recovery objectives for the central service. No performance commitment has been established.
