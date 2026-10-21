# Contrats JSON d’échange — inventaire v1

> **Portée réelle.** Ce document décrit les messages effectivement définis dans `20-exchanges-v1.schema.json` (Draft 2020-12), pas une API implémentée. Il complète le schéma : le schéma est la validation normative ; les règles métier et limites ci-dessous ne sont pas toutes exprimables en JSON Schema.

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

Chaque ligne renvoie explicitement au `$defs` indiqué. `—` signifie champ facultatif ou non applicable dans ce message.

| `message_type` | `$defs` payload | Champs obligatoires principaux | Idempotence / sûreté |
|---|---|---|---|
| `version.negotiate.request` | `version_negotiate_request` | `supported_schema_versions` | Intersection maximale commune ; pas de downgrade silencieux. |
| `version.negotiate.response` | `version_negotiate_response` | `selected_schema_version`, `server_supported_schema_versions` | Rejeter si version sélectionnée incompatible. |
| `agent.enroll` | `agent_enroll` | `agent_name`, `capabilities` | Aucune valeur de secret dans le DTO. |
| `agent.enroll.result` | `agent_enroll_result` | `agent_id`, `status` | Réponse corrélée, sans token en clair. |
| `heartbeat` | `heartbeat` | `agent_status` | Répétition tolérée ; pas de commande implicite. |
| `config.get.response` | `config_get_response` | `config_version`, `values` | Les secrets sont `secret_refs`, jamais des valeurs. |
| `job.claim.request` | `job_claim_request` | `agent_id` | Lecture/réservation bornée. |
| `job.claim.response` | `job_claim_response` | `claim_status` | Lease explicite ; expiration sûre. |
| `job.accept` | `job_accept` | `server_job_id`, `attempt_id`, `lease_expires_at` | Idempotency key ; acceptation explicite. |
| `job.cancel` | `job_cancel` | `server_job_id`, `reason` | Annulation auditable et idempotente. |
| `attempt.renew` | `attempt_renew` | `attempt_id`, `lease_expires_at` | Refuser le renouvellement d’une lease expirée selon politique. |
| `event.batch` | `event_batch` | `attempt_id`, `events` | `event_id` stable ; déduplication. |
| `attempt.result` | `attempt_result` | `attempt_id`, `server_job_id`, `status`, `idempotency_key`, `steps` | Résultat partiel explicite ; pas de ré-exécution sur doublon. |
| `snapshot.reconcile` | `snapshot_reconcile` | `repository_id`, `snapshots` | Observation bornée, sans suppression implicite. |
| `reconcile.request` | `reconcile_request` | `repository_id`, `observed_at` | Opération auditable et idempotente. |
| `reconcile.response` | `reconcile_response` | `repository_id`, `status` | Statut explicite, aucune réparation silencieuse. |
| `error` | `error` | `code`, `message`, `retryable` | Message non sensible ; retry explicite. |
| `page.response` | `page_response` | `items` | Curseur opaque et borné. |
| `notification.delivery` | `notification_delivery` | `notification_id`, `channel`, `status` | Déduplication par idempotency key. |
| `result.upload` | `result_upload` | `attempt_id`, `content_ref`, `idempotency_key` | Référence de contenu, pas de payload illimité. |
| `result.ack` | `result_ack` | `attempt_id`, `status` | `duplicate` est un acquittement sûr. |
| `operator.job.request` | `operator_job_request` | `repository_id`, `policy_id`, `idempotency_key` | Requête opérateur explicitement corrélée et autorisée. |
| `operator.job.response` | `operator_job_response` | `status` | Réponse sans secret ; `duplicate` explicite. |

## 3. Contrats transverses

### Identité, corrélation et temps

`message_id` identifie l’enveloppe ; `correlation_id` relie une réponse ou un événement à son flux ; `agent_id`, `server_job_id`, `attempt_id`, `repository_id` et `event_id` ont des rôles distincts. Les dates sont RFC 3339 avec timezone et sont transmises en UTC.

### Versioning et compatibilité

La négociation porte sur les versions réellement supportées. La version retenue est l’intersection maximale commune ; absence d’intersection ou proposition inconnue produit une erreur structurée. Une implémentation ne doit pas exécuter une enveloppe dont `schema_version` ou `message_type` n’est pas accepté.

### Idempotence et reprise

Les opérations à effets (`job.accept`, `job.cancel`, `attempt.renew`, `event.batch`, `attempt.result`, réconciliation, notifications et uploads) portent une clé d’idempotence ou un identifiant stable. Un doublon doit être reconnu sans répéter l’effet. Une lease expirée est une condition de sécurité, pas une invitation à reprendre silencieusement.

### Secrets et hooks

Un DTO public ne contient ni mot de passe, ni token, ni credential. Un `secret_ref` nomme une source autorisée (`env`, commande allowlistée, OS secret manager ou `fnox`) ; la valeur est résolue au dernier moment dans un périmètre contrôlé. Les hooks sont des références à des commandes allowlistées, jamais des shell strings reçues du serveur.

### Extensions et limites

`extensions` conserve des champs inconnus sans les interpréter. Il est borné en taille/profondeur par le transport et ne peut pas contourner les contrôles de sécurité. Les payloads volumineux passent par une référence de contenu (`content_ref`) et un upload séparé.

## 4. Définitions imbriquées importantes

Les références imbriquées suivantes font partie du contrat et ne doivent pas être remplacées par des champs libres : `hook`, `job_dto`, `event`, `step_result`, `snapshot_ref`, `active_attempt`, `error`.

### `hook`

Un hook contient un nom logique, une référence de commande autorisée et, si nécessaire, des `secret_refs`. Il est refusé si le serveur tente de transmettre une commande arbitraire ou une valeur sensible.

### `job_dto`

Un job relie `server_job_id`, `repository_id` et `policy_id`, puis expose des hooks bornés. Le job décrit l’intention ; `attempt_id` décrit l’exécution.

### `event` et `step_result`

Un event append-only est identifié par `event_id` et rattaché à une tentative dans `event_batch`. Un `step_result` distingue `queued`, `running`, `succeeded`, `failed` et `skipped`; l’erreur inclut `code`, message non sensible et `retryable`.

### `snapshot_ref`

Une référence de snapshot identifie un snapshot observé pour un repository et peut porter date d’observation et taille. Elle ne vaut pas preuve de restauration vérifiée.

## 5. Exemples minimaux complémentaires

Les exemples ci-dessous sont minimaux pour illustrer les flux ajoutés ; ils complètent `20-exchanges-v1.example.json` (résultat terminal). Ils ne promettent pas une implémentation.

### Version negotiation request

```json
{
  "schema_version": 1,
  "message_type": "version.negotiate.request",
  "message_id": "11111111-1111-4111-8111-111111111111",
  "sent_at": "2026-10-21T12:00:00Z",
  "payload": {"supported_schema_versions": [1]}
}
```

### Job claim response

```json
{
  "schema_version": 1,
  "message_type": "job.claim.response",
  "message_id": "11111111-1111-4111-8111-111111111111",
  "sent_at": "2026-10-21T12:00:00Z",
  "payload": {"claim_status": "empty"}
}
```

### Structured error

```json
{
  "schema_version": 1,
  "message_type": "error",
  "message_id": "11111111-1111-4111-8111-111111111111",
  "sent_at": "2026-10-21T12:00:00Z",
  "payload": {
    "code": "version_mismatch",
    "message": "No compatible schema version",
    "retryable": false
  }
}
```

## 6. Checklist d’implémentation

- Valider l’enveloppe et le payload avec Draft 2020-12 avant traitement.
- Vérifier `message_type`, corrélation, lease, idempotency key et autorisation avant tout effet.
- Dédupliquer messages, événements, notifications et uploads.
- Redacter secrets dans logs, erreurs, rapports et notifications.
- Rejeter explicitement les versions incompatibles, les hooks arbitraires et les extensions hors limites.
- Tester doublons, retards, expiration, partition, reprise, résultat partiel et réconciliation divergente.

## 7. Limites

Ce document est un inventaire documentaire. Les garanties transactionnelles, quotas exacts, mécanismes de transport, politiques de rétention et implémentation serveur/agent restent à décider ou à tester. Le schéma est la source normative des formes JSON ; cette page documente la sémantique et les limites non exprimables entièrement par le schéma.
