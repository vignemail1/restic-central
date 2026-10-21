# restic-central

## Objectif

`restic-central` fournit un serveur central et un agent local pour orchestrer des sauvegardes Restic, sans confondre observation, exécution et preuve de réussite.

## Documentation consolidée

- [Cadrage LLM-ready](docs/17-cadrage-llm-ready.md)
- [Audit et décisions du 2026-10-21](docs/18-audit-decisions-2026-10-21.md)
- [Contrats JSON et catalogue v1](docs/20-contrats-json-echanges.md)
- [README des contrats séparés](contracts/README.md)
- Schémas : `contracts/schemas/v1/<message>.schema.json`
- Exemples : `contracts/exemples/v1/<message>.json`

Les anciens documents restent disponibles. La restructuration ne supprime pas d’information historique : le contrat monolithique est conservé comme référence de transition jusqu’à validation d’une migration complète.

## Statut

Documentation de conception, non production. Les contrats v1 sont Draft 2020-12, avec un fichier autonome par type de message, `schema_version: 1`, refs résolubles et exemples sans secrets.

## Invariants

Négociation sur la version commune maximale ; versions et champs inconnus conservés sans exécution ; Outbox persistée avant envoi et ack après déduplication ; résultats idempotents ; une sortie Restic illisible ou inconnue n’est jamais une réussite implicite.
