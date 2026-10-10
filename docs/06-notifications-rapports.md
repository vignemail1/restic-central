# Notifications and reports

Status: proposed functional behavior.

## Incidents

Categories: backup failed, backup partial, destination failed, missed occurrence, runtime exceeded, unreachable agent, unknown result, and failed verification.

Missing contact does not prove a stuck process. Notifications describe observations, last known activity, and recommended inspection.

Group by agent, policy, destination, and category. Retain opening time, latest occurrence, severity, acknowledgment, and resolution. Acknowledgment is not resolution. Maintenance periods must not erase history.

## Immediate notifications

Incident opening, optional escalation, and recovery. Define cooldown, grouping, and duplicate suppression. A successful retry may resolve an incident according to the success rule without erasing the failed attempt.

Proposed providers: email, Matrix, Slack; extensibility through a common interface. One initial channel is sufficient for the MVP; the choice remains open.

Each delivery has a history and retry policy. Notification failure does not change the backup result. Messages exclude secrets and limit sensitive information.

## 24-hour summary

Configurable window, default 24 hours. Separately present incidents opened within the window, incidents still open even if older, resolved incidents, and unmet scheduled occurrences.

Distinguish rolling windows from calendar days. Sending frequency is separate from the window: initial proposal, a daily summary at a configurable time.

## 7-day report

Configurable window, default 7 days. Filters: agent, policy, destination, status, and period. The initial report uses job scheduled times; show start and finish times separately.

Metrics: expected occurrences; created, started, successful, incomplete, failed, skipped, and missed jobs; attempt count; waiting time; total and per-destination duration; age of the last complete success; latest verification; available volume metrics.

A success rate must state its denominator. Proposal: completely successful jobs / expected occurrences outside maintenance, with detailed categories. Do not inflate the rate by counting retries as new jobs.

## Data volumes

Distinguish logical data processed, data added to the repository, compressed added data when available, and actually measured network traffic. Do not label all these measurements backup volume.

A missing counter remains null or unavailable, not zero. Identify its source: Restic, agent measurement, or server calculation. Do not infer exact network traffic solely from added-data size.

With multiple destinations, per-repository totals do not necessarily represent unique source data. Separate source, backup, and replication volumes.

## Freshness and recoverability

Compare the latest complete success with the freshness/RPO target. Separately expose the latest successful check and restore test. Successful backup does not replace integrity checking or application-level restore validation.

## Presentation

Global dashboard, per-agent view, policy history, job details with attempts and destinations, and incident list. Export format remains undecided; CSV is proposed. Display timezone and period boundaries; signal periods with insufficient history.
