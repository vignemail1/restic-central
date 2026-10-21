# restic-central

## Objectif

`restic-central` fournit un serveur central et un agent local pour orchestrer des sauvegardes Restic, sans confondre observation, exécution et preuve de réussite. Un repository appartient exclusivement à une machine et un seul backup est actif par machine.

## État du projet

**Documentation consolidée — conception validée, implémentation non livrée.** Le dépôt n'est pas déclarable en production tant que l'agent, le serveur, les migrations, les contrats, les tests de panne et le runbook de restauration ne sont pas présents et validés.

Les décisions les plus récentes et le cadrage exécutable sont regroupés dans :

- [Décisions consolidées et audit du 2026-10-21](docs/18-audit-decisions-2026-10-21.md)
- [Cadrage LLM-ready](docs/17-cadrage-llm-ready.md)
- [Schéma bootstrap JSON Schema v1](docs/19-schema-bootstrap-v1.json)

La documentation historique reste disponible ; ces trois fichiers constituent l'index de référence pour l'implémentation à venir. Aucune décision historique n'est supprimée par cette synchronisation.

## Parcours de lecture

1. [Vision et exigences](docs/01-vision-exigences.md)
2. [Architecture et modèle](docs/02-architecture-modele.md)
3. [Configuration et exécution](docs/03-configuration-execution.md)
4. [API et fiabilité](docs/04-api-fiabilite.md)
5. [Sécurité et exploitation](docs/05-securite-exploitation.md)
6. [Décisions](docs/07-decisions.md)
7. [Roadmap et validation](docs/08-roadmap-validation.md)
8. [Spécifications révisées](docs/09-specifications-revisees.md)
9. [PostgreSQL](docs/11-decision-postgresql.md)
10. [Isolation des repositories](docs/12-isolation-repositories.md)
11. [Rétention et planning](docs/13-retention-planning.md)
12. [Modèles et relations](docs/15-modeles-relations.md)
13. [Décisions de développement historiques](docs/16-decisions-for-development.md)
14. [Cadrage LLM-ready normatif](docs/17-cadrage-llm-ready.md)
15. [Audit et décisions consolidées](docs/18-audit-decisions-2026-10-21.md)
16. [Contrat bootstrap v1](docs/19-schema-bootstrap-v1.json)
17. [Contrats JSON d’échange v1](docs/20-contrats-json-echanges.md)
18. [Schéma des échanges v1](docs/20-exchanges-v1.schema.json)
19. [Exemple d’échange v1](docs/20-exchanges-v1.example.json)

## Statut des gates

- [ ] Agent et serveur Go 1.27.x, initialement Linux amd64
- [ ] Persistance durable, migrations, API et contrats versionnés
- [ ] Outbox at-least-once, déduplication et saturation observable
- [ ] Hooks, sémantique `failed`/`partial`/`unknown` et tests de panne
- [ ] Enrollment, LDAP StartTLS, sessions, CSRF et audit opérateur
- [ ] Restic >= 0.19.0, packaging, SBOM/licences et builds reproductibles
- [ ] Export quotidien, inventaire et restauration démontrée en <=24 h
