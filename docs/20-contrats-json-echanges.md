# Contrats JSON d’échange — inventaire v1

> **Portée réelle.** Ce document décrit les messages effectivement définis dans `20-exchanges-v1.schema.json` (Draft 2020-12), pas une API implémentée. Il complète le schéma : le schéma est la validation normative ; les règles métier et limites ci-dessous ne sont pas toutes exprimables en JSON Schema.

## 1. Enveloppe commune

| Champ | Type/contrainte | Requis | Notes |
|---|---|---:|---|
| `schema_version` | integer = `1`; const=1 | oui | Version du contrat |
| `message_type` | string; enum des 23 types | oui | Routage typé |
| `message_id` | string; UUID | oui | Identifiant unique du message |
| `correlation_id` | string; UUID | non | Trace d’une interaction |
| `agent_id` | string; UUID | non | Identifiant logique de l’agent |
| `sent_at` | string; date-time | oui | RFC 3339 |
| `payload` | object typé par message | oui | Voir inventaire |
| `extensions` | object libre | non | Extension explicitement permise |

## 2. Inventaire exhaustif par type de message

### `version.negotiate.request` → `$defs/payload_version_negotiate_request`

Message agent vers serveur pour annoncer versions supportées, taille maximale et capacités.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `supported_schema_versions` | array<integer>; minItems=1, maxItems=16 | oui |
| `max_message_bytes` | integer; 1024..104857600 | oui |
| `agent_id` | UUID | oui |
| `sent_at` | date-time | oui |
| `capabilities` | array<string>; maxItems=256 | non |
| `extensions` | object | non |

### `version.negotiate.response` → `$defs/payload_version_negotiate_response`

Réponse serveur avec version choisie, versions disponibles et horodatage.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `selected_schema_version` | integer >=1 | oui |
| `server_supported_schema_versions` | array<integer>; 1..16 | oui |
| `sent_at` | date-time | oui |
| `max_message_bytes` | integer; 1024..104857600 | non |
| `extensions` | object | non |

### `agent.enroll` → `$defs/payload_agent_enroll`

Enrollment initial ; le token n’est pas journalisé et la réponse de credential doit être protégée.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `enrollment_token` | string; 20..4096 caractères | oui |
| `machine_id` | UUID | oui |
| `agent_instance_id` | UUID | oui |
| `agent_version` | string; 1..128 | oui |
| `platform` | const `linux/amd64` | oui |
| `restic_version` | pattern `0.x.y...` | non |
| `sent_at` | date-time | oui |
| `extensions` | object | non |

### `agent.enroll.result` → `$defs/payload_agent_enroll_result`

Résultat d’enrollment ; la valeur de credential est sensible et ne doit pas être persistée en clair.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `agent_id` | UUID | oui |
| `credential` | object `{kind, value}` | oui |
| `expires_at` | date-time | oui |
| `sent_at` | date-time | oui |
| `extensions` | object | non |

### `heartbeat` → `$defs/payload_heartbeat`

État agent, tentatives actives et santé de l’outbox.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `agent_id`, `agent_instance_id` | UUID | oui |
| `observed_at` | date-time | oui |
| `state` | `online`, `degraded`, `offline_pending` | oui |
| `active_attempts` | array; maxItems=32 | oui |
| `outbox` | compteurs et état de perte | oui |

### `config.get.response` → `$defs/payload_config_get_response`

Configuration effective identifiée par révision ; les secrets sont des références autorisées, jamais des valeurs.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `config_revision_id`, `profile_id`, `machine_id` | UUID | révision oui; autres non |
| `config_revision` | integer >=1 | oui |
| `effective_from` | date-time | oui |
| `profile` | object avec `name`, `primary_repository`, `sources`, `hooks`, `retention` | non |
| `sent_at` | date-time | oui |
| `extensions` | object | non |

### `job.claim.request` → `$defs/payload_job_claim_request`

Demande de travail atomique ; MVP : une seule place disponible.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `agent_id` | UUID | oui |
| `available_slots` | const `1` | oui |
| `sent_at` | date-time | oui |
| `known_server_job_ids` | array<UUID>; maxItems=1000 | non |
| `extensions` | object | non |

### `job.claim.response` → `$defs/payload_job_claim_response`

Décision de claim ; `job` est présent pour la décision `job`.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `decision` | `none` ou `job` | oui |
| `job` | `job_dto` | non |
| `sent_at` | date-time | oui |
| `extensions` | object | non |

### `job.accept` → `$defs/payload_job_accept`

Accusé de prise en charge avec lease initiale.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `server_job_id`, `local_job_uuid`, `attempt_id` | UUID | oui |
| `accepted_at`, `expires_at` | date-time | oui |
| `config_revision_id` | UUID | non |
| `extensions` | object | non |

### `job.cancel` → `$defs/payload_job_cancel`

Demande/résultat de cancel idempotent.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `server_job_id`, `local_job_uuid`, `request_id` | UUID | oui |
| `state` | enum cancel_requested/canceled/already_finished/not_found | oui |
| `reason` | string 1..512 | oui |
| `requested_at` | date-time | oui |
| `confirmed_at` | date-time | non |
| `extensions` | object | non |

### `attempt.renew` → `$defs/payload_attempt_renew`

Renouvellement de lease.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `attempt_id`, `server_job_id`, `lease_id` | UUID | oui |
| `renewed_at`, `lease_expires_at` | date-time | oui |
| `extensions` | object | non |

### `event.batch` → `$defs/payload_event_batch`

Lot append-only d’événements ordonnés.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `attempt_id` | UUID | oui |
| `events` | array<event>; 1..1000 | oui |
| `extensions` | object | non |

### `attempt.result` → `$defs/payload_attempt_result`

Résultat terminal ou intermédiaire d’une tentative, avec étapes et idempotence.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `attempt_id`, `server_job_id`, `local_job_uuid` | UUID | oui |
| `status` | enum état job | oui |
| `started_at`, `finished_at` | date-time | oui |
| `steps` | array<step_result>; 1..10000 | oui |
| `idempotency_key` | string 1..256 | oui |
| `snapshot`, `error`, `restic_json` | objets typés | non |
| `extensions` | object | non |

### `snapshot.reconcile` → `$defs/payload_snapshot_reconcile`

Observation de snapshots sans conclure à une réussite de job.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `repository_id` | UUID | oui |
| `machine_id` | UUID | non |
| `observed_at` | date-time | oui |
| `mode` | `full` ou `incremental` | oui |
| `collector` | string | non |
| `snapshots` | array<snapshot_ref>; maxItems=100000 | oui |
| `extensions` | object | non |

### `reconcile.request` → `$defs/payload_reconcile_request`

Demande de réconciliation des actifs et résultats en attente.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `agent_id` | UUID | oui |
| `sent_at` | date-time | oui |
| `active_attempts` | array<active_attempt>; maxItems=32 | oui |
| `pending_results` | array; maxItems=1000 | oui |
| `extensions` | object | non |

### `reconcile.response` → `$defs/payload_reconcile_response`

État autoritatif et divergences à traiter.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `authoritative_state` | object | oui |
| `expected_event_ids` | array<string>; maxItems=10000 | oui |
| `divergences` | array; maxItems=1000 | non |
| `sent_at` | date-time | oui |
| `extensions` | object | non |

### `error` → `$defs/payload_error`

Erreur structurée sans secret.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `code`, `message` | string | oui |
| `retryable` | boolean | oui |
| `request_id` | UUID | oui |
| `details` | object | non |
| `retry_after_seconds` | integer >=0 | non |
| `extensions` | object | non |

### `page.response` → `$defs/payload_page_response`

Réponse paginée générique ; le détail du curseur reste une décision serveur.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `items` | array<object>; maxItems=1000 | oui |
| `page` | integer >=1 | oui |
| `page_size` | integer 1..1000 | oui |
| `has_more` | boolean | oui |
| `next_cursor` | string/null | non |
| `as_of` | date-time | non |
| `extensions` | object | non |

### `notification.delivery` → `$defs/payload_notification_delivery`

Notification d’incident/rapport et statut de livraison.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `notification_id` | UUID | oui |
| `incident_id` | UUID/null | non |
| `kind` | incident_opened/recovered/summary_24h/report_7d | oui |
| `occurred_at` | date-time | oui |
| `severity` | info/warning/critical | oui |
| `message` | string max 10000 | oui |
| `recipients` | array<string>; 1..1000 | oui |
| `delivery_status` | pending/sent/failed | non |
| `extensions` | object | non |

### `result.upload` → `$defs/payload_result_upload`

Upload idempotent d’un résultat.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `attempt_id` | UUID | oui |
| `idempotency_key` | string 1..256 | oui |
| `result` | `payload_attempt_result` | oui |
| `sent_at` | date-time | oui |
| `extensions` | object | non |

### `result.ack` → `$defs/payload_result_ack`

Accusé d’acceptation, duplication ou rejet.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `attempt_id` | UUID | oui |
| `idempotency_key` | string 1..256 | oui |
| `status` | accepted/duplicate/rejected | oui |
| `acknowledged_at` | date-time | oui |
| `request_id` | UUID | non |
| `error` | error | non |
| `extensions` | object | non |

### `operator.job.request` → `$defs/payload_operator_job_request`

Demande opérateur d’exécution d’un job.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `request_id`, `machine_id`, `profile_id` | UUID | oui |
| `job_type` | backup/copy/forget/prune/check/stats | oui |
| `config_revision_id` | UUID | non |
| `requested_at` | date-time | oui |
| `reason` | string 1..512 | non |
| `extensions` | object | non |

### `operator.job.response` → `$defs/payload_operator_job_response`

Décision opérateur et job éventuel.

| Champ | Type/contrainte | Requis |
|---|---|---:|
| `request_id` | UUID | oui |
| `decision` | accepted/rejected | oui |
| `job` | job_dto | non |
| `sent_at` | date-time | oui |
| `error` | error | non |
| `extensions` | object | non |

## 3. Définitions réutilisées (`$defs`)

Les objets `hook`, `job_dto`, `event`, `step_result`, `snapshot_ref`, `active_attempt` et `error` sont définis dans le schéma. Leurs champs obligatoires, bornes, enums et `additionalProperties` font foi dans le JSON Schema ; ce document ne les duplique pas intégralement.

## 4. Exemples conformes

Les exemples ci-dessous sont minimaux pour illustrer les flux ajoutés ; ils complètent `20-exchanges-v1.example.json` (résultat terminal). Ils ne promettent pas une implémentation.

```json
{
  "schema_version": 1,
  "message_type": "heartbeat",
  "message_id": "00000000-0000-4000-8000-000000000001",
  "sent_at": "2026-10-21T12:00:00Z",
  "payload": {
    "agent_id": "00000000-0000-4000-8000-000000000002",
    "agent_instance_id": "00000000-0000-4000-8000-000000000003",
    "observed_at": "2026-10-21T12:00:00Z",
    "state": "online",
    "active_attempts": [],
    "outbox": {"pending_count": 0, "oldest_pending_at": null, "loss_state": "none"}
  }
}
```

```json
{
  "schema_version": 1,
  "message_type": "job.claim.request",
  "message_id": "00000000-0000-4000-8000-000000000004",
  "sent_at": "2026-10-21T12:00:00Z",
  "payload": {
    "agent_id": "00000000-0000-4000-8000-000000000002",
    "available_slots": 1,
    "sent_at": "2026-10-21T12:00:00Z"
  }
}
```

```json
{
  "schema_version": 1,
  "message_type": "result.ack",
  "message_id": "00000000-0000-4000-8000-000000000005",
  "sent_at": "2026-10-21T12:00:00Z",
  "payload": {
    "attempt_id": "00000000-0000-4000-8000-000000000006",
    "idempotency_key": "attempt-0001",
    "status": "accepted",
    "acknowledged_at": "2026-10-21T12:00:00Z"
  }
}
```

## 5. Règles métier hors schéma

- Une seule exécution backup active par machine ; lease et idempotence déterminent la reprise.
- `unknown` est conservé lorsqu’une interruption empêche de prouver l’issue ; snapshot observé n’est pas preuve de succès.
- Les relations entre UUID, ordre temporel, autorisation, absence de secrets et cohérence serveur sont validées par code et tests.
- Les tokens, credentials, URLs sensibles et valeurs d’environnement restent hors des logs et événements.
- L’outbox durable, la déduplication et la saturation sont observables ; une perte est un incident explicite.

## 6. Limites et lacunes explicites

- Le schéma ne garantit pas les relations temporelles (`finished_at` après `started_at`), la cohérence croisée des UUID, ni l’absence de secrets.
- `additionalProperties: false` s’applique à l’enveloppe et aux objets typés ; les extensions doivent utiliser le champ `extensions` prévu.
- Les codes HTTP, routes REST finales, auth, rotation/révocation et détail du curseur restent à spécifier par la couche API.
- `operator.job.request/response` couvre la demande de job opérateur, pas toutes les opérations d’administration (configuration, révocation, rapports, incidents).
- Le schéma ne garantit pas les relations temporelles (`finished_at` après `started_at`), la cohérence croisée des UUID, ni l’absence de secrets.
- Statut : conception documentaire, non production-ready.
