# Contrats JSON v1

Cette arborescence remplace le contrat monolithique pour permettre un fichier autonome par `message_type` :

- `schemas/v1/<message>.schema.json` : Draft 2020-12, `$id` stable, définitions locales et refs résolubles.
- `exemples/v1/<message>.json` : un exemple par type, avec `schema_version: 1`.

Les exemples sont des données de contrat illustratives, sans secrets ni chemins sensibles. Le champ `restic_json` est réservé à la sortie JSON Restic bornée et préservée ; il ne transforme pas cette sortie en contrat API.

## Sorties Restic et provenance

Les formes Restic ne sont pas inventées dans ces exemples. La documentation officielle stable consultée le 21 octobre 2026 décrit le JSON output et les formats `backup`, `check`, `snapshots`, `copy` et autres dans [Scripting — JSON output](https://restic.readthedocs.io/en/stable/075_scripting.html), ainsi que le contexte et le snapshot créé par `backup` dans [Backing up](https://restic.readthedocs.io/en/stable/040_backup.html). Les versions précises des extraits changent avec la documentation stable : toujours conserver la version de Restic observée avec la sortie et traiter une forme inconnue comme `unknown`/`failed`, jamais comme une réussite.

Le dépôt accepte Restic `>=0.19.0` selon le cadrage documentaire, mais cette arborescence ne prétend pas valider un binaire local. Aucun secret d’accès, mot de passe ou token n’est inclus.

## Règles de compatibilité

La négociation sélectionne la version commune maximale. Une version inconnue ou un champ inconnu est conservé dans `extensions`, sans interprétation ni exécution. Les résultats sont idempotents via `message_id`/`idempotency_key`; l’Outbox doit persister avant envoi et l’ack après déduplication et stockage.

Voir `docs/20-contrats-json-echanges.md` pour l’inventaire explicatif. La source normative est dans `contracts/schemas/v1/`; les exemples exécutables sont dans `contracts/exemples/v1/`. Valider hors ligne avec `python3 scripts/validate-contracts.py`, puis exécuter `python3 scripts/test_validate_contracts.py`.
