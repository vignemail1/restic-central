# Contrats JSON d’échange — inventaire v1

> **Portée réelle.** Ce document explique les messages et règles métier, sans être la source normative des schémas. Les sources normatives sont les fichiers Draft 2020-12 de `../contracts/schemas/v1/`, avec définitions communes dans `_shared.schema.json`; les exemples sont dans `../contracts/exemples/v1/`. Les anciens fichiers JSON de `docs/` sont historiques et ne doivent pas être utilisés par une implémentation ou la CI.

## 1. Enveloppe commune

| Champ | Type / contrainte | Requis | Sémantique |
|---|---|---:|---|
| `schema_version` | integer = `1`; const=1 | oui |  |
| `message_type` | string (`version.negotiate.request`, `version.negotiate.response`, `agent.enroll`, `agent.enroll.result`, `heartbeat`, `config.get.response`, `job.claim.request`, `job.claim.response`, `job.accept`, `job.cancel`, `attempt.renew`, `event.batch`, `attempt.result`, `snapshot.reconcile`, `reconcile.request`, `reconcile.response`, `error`, `page.response`, `notification.delivery`, `result.upload`, `result.ack`, `operator.job.request`, `operator.job.response`);  | oui |  |
| `message_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `correlation_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `agent_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `payload` | object;  | oui |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

`payload` est un objet dont la forme dépend de `message_type`; `extensions` est conservé sans interprétation. Les identifiants sont opaques. Les dates sont RFC 3339 avec fuseau, transmises en UTC.

## 2. Inventaire exhaustif par type de message

Chaque ligne renvoie explicitement au `$defs` indiqué. `—` signifie champ non défini dans ce payload. Les champs `extensions` sont décrits mais leur contenu est volontairement ouvert.
### `version.negotiate.request` → `$defs/payload_version_negotiate_request`

Annonce des versions; la réponse sélectionne la version commune maximale, sinon erreur explicite.

| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `supported_schema_versions` | array<integer>; minItems=1, maxItems=16 | oui |  |
| `max_message_bytes` | integer; minimum=1024, maximum=104857600 | oui |  |
| `agent_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `capabilities` | array<string>; minItems=0, maxItems=256 | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `version.negotiate.response` → `$defs/payload_version_negotiate_response`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `selected_schema_version` | integer; minimum=1 | oui |  |
| `server_supported_schema_versions` | array<integer>; minItems=1, maxItems=16 | oui |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `max_message_bytes` | integer; minimum=1024, maximum=104857600 | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `agent.enroll` → `$defs/payload_agent_enroll`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `enrollment_token` | string; minLength=20, maxLength=4096 | oui | Secret d’enrollment à usage limité; ne pas journaliser. |
| `machine_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `agent_instance_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `agent_version` | string; minLength=1, maxLength=128 | oui |  |
| `platform` | string = `linux/amd64`; const=linux/amd64 | oui |  |
| `restic_version` | string; pattern=^0\.[0-9]+\.[0-9]+.*$ | non |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `agent.enroll.result` → `$defs/payload_agent_enroll_result`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
---|---|---:|---|
| `agent_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `credential` | object;  | oui |  |
| `expires_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `heartbeat` → `$defs/payload_heartbeat`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
---|---|---:|---|
| `agent_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `agent_instance_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `observed_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `state` | string (`online`, `degraded`, `offline_pending`);  | oui |  |
| `agent_version` | string;  | non |  |
| `restic_version` | string;  | non |  |
| `active_attempts` | array<object>; minItems=0, maxItems=32 | oui |  |
| `outbox` | object;  | oui | Outbox durable; perte observable, sans suppression d’état actif. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `config.get.response` → `$defs/payload_config_get_response`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `config_revision_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `config_revision` | integer; minimum=1 | oui |  |
| `effective_from` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `profile_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `machine_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `profile` | object;  | non |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `job.claim.request` → `$defs/payload_job_claim_request`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `agent_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `available_slots` | integer = `1`; const=1 | oui |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `known_server_job_ids` | array<string>; minItems=0, maxItems=1000 | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `job.claim.response` → `$defs/payload_job_claim_response`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
---|---|---:|---|
| `decision` | string (`none`, `job`);  | oui |  |
| `job` | `job_dto`;  | non |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `job.accept` → `$defs/payload_job_accept`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `server_job_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `local_job_uuid` | string; format=uuid | oui | Identifiant UUID opaque. |
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `accepted_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `expires_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `config_revision_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `job.cancel` → `$defs/payload_job_cancel`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `server_job_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `local_job_uuid` | string; format=uuid | oui | Identifiant UUID opaque. |
| `request_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `state` | string (`cancel_requested`, `canceled`, `already_finished`, `not_found`);  | oui |  |
| `reason` | string; minLength=1, maxLength=512 | oui |  |
| `requested_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `confirmed_at` | string; format=date-time | non | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `attempt.renew` → `$defs/payload_attempt_renew`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `server_job_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `lease_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `renewed_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `lease_expires_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `event.batch` → `$defs/payload_event_batch`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
---|---|---:|---|
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `events` | array<`event`>; minItems=1, maxItems=1000 | oui |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `attempt.result` → `$defs/payload_attempt_result`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `server_job_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `local_job_uuid` | string; format=uuid | oui | Identifiant UUID opaque. |
| `status` | string (`received`, `accepted`, `running`, `succeeded`, `partial`, `failed`, `unknown`, `degraded`, `expired`, `canceled`, `cancel_requested`, `blocked_unknown_scope`, `persistence_failed`);  | oui | État métier; unknown n’est jamais une réussite. |
| `started_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `finished_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `steps` | array<`step_result`>; minItems=1, maxItems=10000 | oui |  |
| `idempotency_key` | string; minLength=1, maxLength=256 | oui |  |
| `snapshot` | `snapshot_ref`;  | non |  |
| `error` | object;  | non |  |
| `restic_json` | object;  | non | Payload Restic borné et préservé, pas le contrat API. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `snapshot.reconcile` → `$defs/payload_snapshot_reconcile`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `repository_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `machine_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `observed_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `mode` | string (`full`, `incremental`);  | oui |  |
| `collector` | string; minLength=1, maxLength=128 | non |  |
| `snapshots` | array<`snapshot_ref`>; minItems=0, maxItems=100000 | oui |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `reconcile.request` → `$defs/payload_reconcile_request`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `agent_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `active_attempts` | array<`active_attempt`>; minItems=0, maxItems=32 | oui |  |
| `pending_results` | array<object>; minItems=0, maxItems=1000 | oui |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `reconcile.response` → `$defs/payload_reconcile_response`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `authoritative_state` | object;  | oui |  |
| `expected_event_ids` | array<string>; minItems=0, maxItems=10000 | oui |  |
| `divergences` | array<object>; minItems=0, maxItems=1000 | non |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `error` → `$defs/payload_error`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `code` | string;  | oui |  |
| `message` | string;  | oui |  |
| `retryable` | boolean;  | oui |  |
| `request_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `details` | object;  | non |  |
| `retry_after_seconds` | integer; minimum=0 | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `page.response` → `$defs/payload_page_response`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `items` | array<object>; maxItems=1000 | oui |  |
| `page` | integer; minimum=1 | oui |  |
| `page_size` | integer; minimum=1, maximum=1000 | oui |  |
| `has_more` | boolean;  | oui |  |
| `next_cursor` | ['string', 'null']; maxLength=2048 | non |  |
| `as_of` | string; format=date-time | non | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `notification.delivery` → `$defs/payload_notification_delivery`



| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `notification_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `incident_id` | string | null;  | non |  |
| `kind` | string (`incident_opened`, `incident_recovered`, `summary_24h`, `report_7d`);  | oui |  |
| `occurred_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `severity` | string (`info`, `warning`, `critical`);  | oui |  |
| `message` | string; maxLength=10000 | oui |  |
| `recipients` | array<string>; minItems=1, maxItems=1000 | oui |  |
| `delivery_status` | string (`pending`, `sent`, `failed`);  | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `result.upload` → `$defs/payload_result_upload`

Upload durable du résultat terminal; le serveur répond par result.ack après persistance/déduplication.

| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `idempotency_key` | string; minLength=1, maxLength=256 | oui |  |
| `result` | `payload_attempt_result`;  | oui |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `result.ack` → `$defs/payload_result_ack`

Accusé applicatif durable de result.upload; un doublon identique peut être ACKé sans nouvel effet.

| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `idempotency_key` | string; minLength=1, maxLength=256 | oui |  |
| `status` | string (`accepted`, `duplicate`, `rejected`);  | oui |  |
| `acknowledged_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `request_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `error` | `error`;  | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `operator.job.request` → `$defs/payload_operator_job_request`

Demande authentifiée d’un opérateur; l’identité et les permissions viennent de la session, pas d’un identifiant fourni par le client.

| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `request_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `machine_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `profile_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `job_type` | string (`backup`, `copy`, `forget`, `prune`, `check`, `stats`);  | oui |  |
| `config_revision_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `requested_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `reason` | string; minLength=1, maxLength=512 | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `operator.job.response` → `$defs/payload_operator_job_response`

Réponse à une demande opérateur; l’acceptation ne signifie pas que l’exécution est terminée.

| Champ | Type / contraintes | Requis | Sémantique définie par le schéma |
|---|---|---:|---|
| `request_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `decision` | string (`accepted`, `rejected`);  | oui |  |
| `job` | `job_dto`;  | non |  |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `error` | `error`;  | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

## 3. Définitions réutilisées (`$defs`)

Les références imbriquées suivantes font partie du contrat et ne doivent pas être remplacées par des champs libres : `hook`, `job_dto`, `event`, `step_result`, `snapshot_ref`, `active_attempt`, `error`.
### `$defs/hook`

| Champ | Type / contraintes | Requis | Sémantique |
---|---|---:|---|
| `executable` | string; pattern=^/ | oui |  |
| `args` | array<string>; minItems=0, maxItems=256 | oui |  |
| `working_directory` | string;  | non |  |
| `timeout_seconds` | integer; minimum=1, maximum=86400 | oui |  |
| `condition` | string (`always`, `on_success`, `on_failure`, `post_primary`);  | oui |  |
| `environment_refs` | array<object>; minItems=0, maxItems=256 | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `$defs/job_dto`

| Champ | Type / contraintes | Requis | Sémantique |
---|---|---:|---|
| `server_job_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `local_job_uuid` | string; format=uuid | oui | Identifiant UUID opaque. |
| `machine_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `profile_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `job_type` | string (`backup`, `copy`, `forget`, `prune`, `check`, `stats`);  | oui |  |
| `origin` | string (`server_schedule`, `operator`, `local_manual`, `cached_maintenance`);  | oui |  |
| `state` | string (`received`, `accepted`, `running`, `succeeded`, `partial`, `failed`, `unknown`, `degraded`, `expired`, `canceled`, `cancel_requested`, `blocked_unknown_scope`, `persistence_failed`);  | oui | État métier; unknown n’est jamais une réussite. |
| `scheduled_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `expires_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `config_revision_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `target_repository_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `$defs/event`

| Champ | Type / contraintes | Requis | Sémantique |
---|---|---:|---|
| `event_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `sequence_number` | integer; minimum=1 | oui |  |
| `occurred_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `event_type` | string; pattern=^[a-z][a-z0-9_.-]{1,127}$ | oui |  |
| `payload` | object;  | oui | Données d’événement bornées; pas de secret. |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `$defs/step_result`

| Champ | Type / contraintes | Requis | Sémantique |
---|---|---:|---|
| `step_id` | string; minLength=1, maxLength=256 | oui |  |
| `step_type` | string (`pre_hook`, `backup`, `copy`, `post_hook`, `forget`, `prune`, `check`, `stats`);  | oui |  |
| `status` | string (`received`, `accepted`, `running`, `succeeded`, `partial`, `failed`, `unknown`, `degraded`, `expired`, `canceled`, `cancel_requested`, `blocked_unknown_scope`, `persistence_failed`);  | oui | État métier; unknown n’est jamais une réussite. |
| `started_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `finished_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `exit_code` | integer;  | non |  |
| `repository_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `source_snapshot_id` | string; maxLength=256 | non |  |
| `destination_snapshot_id` | string; maxLength=256 | non |  |
| `error` | object;  | non |  |
| `metrics` | object;  | non |  |

### `$defs/snapshot_ref`

| Champ | Type / contraintes | Requis | Sémantique |
---|---|---:|---|
| `repository_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `restic_snapshot_id` | string; pattern=^[0-9a-f]{8,64}$ | oui |  |
| `observed_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `provenance` | string (`created`, `reused`, `replicated`, `observed_unknown`);  | oui |  |
| `source_snapshot_id` | string;  | non |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. Taille et profondeur bornées par transport. |

### `$defs/active_attempt`

| Champ | Type / contraintes | Requis | Sémantique |
---|---|---:|---|
| `attempt_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `server_job_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `local_job_uuid` | string; format=uuid | oui | Identifiant UUID opaque. |
| `state` | string (`received`, `accepted`, `running`, `succeeded`, `partial`, `failed`, `unknown`, `degraded`, `expired`, `canceled`, `cancel_requested`, `blocked_unknown_scope`, `persistence_failed`);  | oui | État métier; unknown n’est jamais une réussite. |
| `lease_expires_at` | string; format=date-time | non | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `last_sequence_number` | integer; minimum=0 | non |  |

### `$defs/error`

| Champ | Type / contraintes | Requis | Sémantique |
---|---|---:|---|
| `code` | string; pattern=^[a-z][a-z0-9_.-]{1,63}$ | oui |  |
| `message` | string; maxLength=2000 | oui |  |
| `retryable` | boolean;  | oui |  |
| `details` | object;  | non |  |

## 4. Exemples conformes

Les exemples ci-dessous sont minimaux pour illustrer les flux ajoutés ; ils complètent `../contracts/exemples/v1/attempt.result.json` (résultat terminal). Ils ne promettent pas une implémentation.

```json
{
  "schema_version": 1,
  "message_type": "result.upload",
  "message_id": "00000000-0000-4000-8000-000000000001",
  "sent_at": "2026-10-21T12:00:00Z",
  "payload": {
    "attempt_id": "00000000-0000-4000-8000-000000000002",
    "idempotency_key": "attempt-2-final",
    "result": {
      "attempt_id": "00000000-0000-4000-8000-000000000002",
      "server_job_id": "00000000-0000-4000-8000-000000000003",
      "local_job_uuid": "00000000-0000-4000-8000-000000000004",
      "status": "failed",
      "started_at": "2026-10-21T11:00:00Z",
      "finished_at": "2026-10-21T11:05:00Z",
      "steps": [
        {
          "step_id": "backup",
          "step_type": "backup",
          "status": "failed",
          "started_at": "2026-10-21T11:00:00Z",
          "finished_at": "2026-10-21T11:05:00Z"
        }
      ],
      "idempotency_key": "attempt-2-final"
    },
    "sent_at": "2026-10-21T12:00:00Z"
  }
}
```

```json
{
  "schema_version": 1,
  "message_type": "result.ack",
  "message_id": "00000000-0000-4000-8000-000000000005",
  "sent_at": "2026-10-21T12:01:00Z",
  "payload": {
    "attempt_id": "00000000-0000-4000-8000-000000000002",
    "idempotency_key": "attempt-2-final",
    "status": "accepted",
    "acknowledged_at": "2026-10-21T12:01:00Z",
    "request_id": "00000000-0000-4000-8000-000000000006"
  }
}
```

```json
{
  "schema_version": 1,
  "message_type": "operator.job.request",
  "message_id": "00000000-0000-4000-8000-000000000007",
  "sent_at": "2026-10-21T12:02:00Z",
  "payload": {
    "request_id": "00000000-0000-4000-8000-000000000008",
    "machine_id": "00000000-0000-4000-8000-000000000009",
    "profile_id": "00000000-0000-4000-8000-000000000010",
    "job_type": "backup",
    "requested_at": "2026-10-21T12:02:00Z"
  }
}
```

## 5. Règles métier hors schéma

- Un ACK n’est émis qu’après persistance et déduplication transactionnelles côté serveur ; livraison at-least-once, doublon identique sans nouvel effet, même identifiant avec contenu différent rejeté.
- `result.upload` est durable côté agent avant envoi ; perte d’ACK ne justifie jamais de relancer automatiquement un backup.
- `unknown` n’est jamais une réussite ; expiration de lease ne prouve pas l’arrêt du processus. Réconciliation avant redistribution/retry.
- `partial` signifie notamment backup primaire réussi mais copy/post-hook échoué ; un retry de copy réutilise le snapshot.
- L’identité authentifiée de l’agent/opérateur, l’autorisation, l’ownership machine/repository, l’ordre des séquences, l’unicité et les bornes transport ne sont pas entièrement démontrés par ce schéma.
- Secrets : références seulement pour hooks ; les credentials/tokens ne doivent pas être journalisés.

## 6. Limites et lacunes explicites

- Les chemins HTTP, codes de réponse, session LDAP/CSRF, révocation/rotation, stratégie de retry/catch-up, pagination exacte, export et UI restent non implémentés ou illustratifs.
- Le schéma accepte certains objets libres (`extensions`, payloads Restic, métriques, état autoritaire) : leur contenu n’est pas un contrat exhaustif.
- `operator.job.request/response` couvre la demande de job opérateur, pas toutes les opérations d’administration (configuration, révocation, rapports, incidents).
- Le schéma ne garantit pas les relations temporelles (`finished_at` après `started_at`), la cohérence croisée des UUID, ni l’absence de secrets.
- Statut : conception documentaire, non production-ready.

## Source normative et validation

La terminologie de ce document est française, avec les noms de champs et types de messages anglais conservés tels quels pour garantir l’interopérabilité. Valider localement avec `python3 scripts/validate-contracts.py`; le validateur construit un registre par `$id`, résout uniquement les références présentes dans le dépôt et échoue sur toute référence absente. Aucun accès réseau n’est autorisé.
