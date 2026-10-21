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



## 3. Définitions réutilisées (`$defs`)

Les références imbriquées suivantes font partie du contrat et ne doivent pas être remplacées par des champs libres : `hook`, `job_dto`, `event`, `step_result`, `snapshot_ref`, `active_attempt`, `error`.

## 4. Exemples conformes

Les exemples ci-dessous sont minimaux pour illustrer les flux ajoutés ; ils complètent `../contracts/exemples/v1/attempt.result.json` (résultat terminal). Ils ne promettent pas une implémentation.

## 5. Règles métier hors schéma

- Un ACK n’est émis qu’après persistance et déduplication transactionnelles côté serveur ; livraison at-least-once, doublon identique sans nouvel effet, même identifiant avec contenu différent rejeté.
- `partial` signifie notamment backup primaire réussi mais copy/post-hook échoué ; un retry de copy réutilise le snapshot.

## Source normative et validation

Valider localement avec `python3 scripts/validate-contracts.py`; le validateur construit un registre par `$id`, résout uniquement les références présentes dans le dépôt et échoue sur toute référence absente. Aucun accès réseau n’est autorisé.
