# REST contract and reliability

Status: illustrative, unimplemented contract. The paths below do not constitute a stable API.

## Transport and identity

HTTPS with certificate verification. Agent-initiated communication; polling or long polling is proposed. Each agent is authenticated and authorized only for its own resources. IDs submitted in request bodies never replace the authenticated identity.

## Proposed resources

| Method and path | Purpose |
|---|---|
| POST /api/v1/agents/enroll | controlled enrollment; mechanism to define |
| POST /api/v1/agents/{id}/heartbeat | availability and capabilities |
| GET /api/v1/agents/{id}/configuration | authorized configuration revision |
| POST /api/v1/agents/{id}/jobs/claim | atomic job acquisition |
| POST /api/v1/attempts/{id}/renew | reservation renewal |
| POST /api/v1/attempts/{id}/events | idempotent event batch |
| POST /api/v1/attempts/{id}/result | idempotent terminal result |
| POST /api/v1/policies/{id}/jobs | manual request, administrator access |
| GET /api/v1/jobs/{id} | state and per-destination results |
| GET /api/v1/reports/backups | filtered, paginated report |

Provide pagination, request-size limits, strict validation, structured errors, correlation IDs, and versioning. Administration and agent endpoints have separate permissions.

## Event envelope

Minimum fields: event_id, agent_id, job_id, attempt_id, config_revision, sequence_number, occurred_at, event_type, payload. The server adds received_at. Timestamps are transmitted in UTC; retain both dates to diagnose delays and clock differences.

The server deduplicates by event_id, checks attempt ownership, and detects missing or out-of-order sequences. An identical duplicate is acknowledged without another side effect; the same ID with different content is rejected.

## Local outbox

Persist before sending. Acknowledge only after confirmation of server-side persistence. Provide at-least-once delivery, not a promise of exactly-once delivery.

Retries use backoff, jitter, bounds, and error classification: 429 and temporary errors may be retried; authentication errors trigger a degraded state instead of an aggressive loop. Honor Retry-After where applicable.

Configure local quota, retention, crash recovery, and saturation policy. Terminal events take priority; progress updates may be coalesced. Insufficient space to persist must cause a visible error, not silent data loss.

A result awaiting transmission never authorizes automatically restarting the completed backup.

## Reservations and concurrency

Acquisition is transactional. An attempt receives an ID and a renewable reservation. The server rejects updates from unauthorized attempts.

Reservation expiry does not prove Restic has stopped. Do not automatically redistribute a potentially active job to another agent. Reconciliation is required before retrying; fencing metadata writes alone cannot stop a process writing to a repository.

## Reconciliation

On reconnect, the agent sends active attempts and persisted results. The server replies with its authoritative coordination state and expected events. Divergences are recorded. A late result may resolve an unknown observation state under explicit rules without erasing the historical incident.

## Cancellation

Distinguish cancellation request, agent receipt, and confirmed termination. An API must not report canceled merely because a request was recorded. Process-group handling and grace periods depend on the supported operating system.
