# Contrats JSON d’échange — inventaire v1

> **Portée réelle.** Ce document explique les messages et règles métier, sans être la source normative des schémas. Les sources normatives sont les fichiers Draft 2020-12 de `../contracts/schemas/v1/`, avec définitions communes dans `_shared.schema.json`; les exemples sont dans `../contracts/exemples/v1/`. Les anciens fichiers JSON de `docs/` sont historiques et ne doivent pas être utilisés par une implémentation ou la CI.

## 1. Enveloppe commune

| Champ | Type / contrainte | Requis | Sémantique |
|---|---|---:|---|
| `schema_version` | integer = `1`; const=1 | oui |  |
| `message_type` | string;  | oui | Type de message défini par les schémas v1. |
| `message_id` | string; format=uuid | oui | Identifiant UUID opaque. |
| `correlation_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `agent_id` | string; format=uuid | non | Identifiant UUID opaque. |
| `sent_at` | string; format=date-time | oui | Horodatage RFC 3339 avec timezone, transmis en UTC. |
| `payload` | object;  | oui |  |
| `extensions` | object;  | non | Champs inconnus conservés sans interprétation ni exécution. |

`payload` est un objet dont la forme dépend de `message_type`; `extensions` est conservé sans interprétation. Les identifiants sont opaques. Les dates sont RFC 3339 avec fuseau, transmises en UTC.

## Source normative et validation

La source normative est exclusivement constituée des schémas Draft 2020-12 présents dans `../contracts/schemas/v1/`, avec définitions communes dans `_shared.schema.json`; les exemples sont dans `../contracts/exemples/v1/`. Ce document est explicatif et ne doit pas être utilisé comme schéma d’exécution. Valider localement avec `python3 scripts/validate-contracts.py`; le validateur construit un registre par `$id`, résout uniquement les références présentes dans le dépôt et échoue sur toute référence absente. Aucun accès réseau n’est autorisé.
