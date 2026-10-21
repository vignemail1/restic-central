# Audit d’harmonisation documentaire — 2026-10-21

## Périmètre et état vérifié

Audit exécuté sur `vignemail1/restic-central`, branche `docs/llm-cadrage-decisions-2026-10-21`, dont le HEAD vérifié avant correction était `c28e1bbf16186be35e7d4a6e71e1af6ca0642682`. La branche `main` a été laissée intacte. Ce fichier est un rapport d’audit : il ne remplace pas les contrats JSON ni les documents normatifs.

Le dépôt contient les documents `docs/01` à `docs/20`, les schémas et exemples sous `contracts/`, ainsi que les scripts de validation. La publication existante couvre déjà la plupart des décisions validées ; les points ci-dessous sont les règles canoniques à appliquer lorsque des formulations historiques divergent.

## Règles validées à harmoniser

- Ordre de livraison : agent autonome + hooks + Outbox, enrollment serveur, enrollment client, résultats serveur, résultats client, configuration serveur, auto-configuration client, scheduling serveur.
- MVP : agent et serveur Linux amd64 ; macOS arm64 et Windows amd64 futurs ; Go 1.27 ; Restic >= 0.19.0.
- Configuration restreinte séparée des données variables durables. Outbox durable, at-least-once ; en saturation, éviction stricte des événements les plus anciens et perte observable ; aucun état actif supprimé.
- Échec primaire/pre-hook, Restic interrompu/timeout/sortie indécodable : `failed`. Réplication ou post-hook échoué après backup réussi : `partial`. Un retry réussi reste `partial` pour investigation. Post-hook après échec pre-hook : configurable, `false` par défaut.
- Job serveur non récupéré : remplacement futur ; ACK d’expiration par défaut à `start + 12 h`. Un job en overlap est annulé avec motif `running`.
- Maintenance offline mise en cache et résultats remontés via Outbox. Snapshot primaire expiré ou inexistant : réplication abandonnée et `failed`. Rétention opérateur via directives Restic `keep-*`, avec protection d’au moins le dernier snapshot valide ; un snapshot expiré non répliqué peut être supprimé selon la policy.
- Secrets par variable d’environnement ou commande par clé ; fnox est une option initiale. Aucun secret ni identifiant de job dans les logs.
- Enrollment : machine pré-déclarée, token unique et révocable, valable 12 h, renouvellement manuel uniquement.
- `schema_version` entier commençant à 1 ; négociation par version commune maximale, refus sans intersection. Extensions JSON DB préservées sans interprétation ni exécution. `server_job_id` attribué à l’ingestion ; déduplication durable, ACK après persistance, puis suppression Outbox.
- LDAP `posixAccount` avec filtre additionnel et StartTLS vérifié. Superadmin local de récupération et safeguards de session. Autorisation opérateur complète initialement par mapping de groupes, avec évolution future. Toute action opérateur auditée.
- PostgreSQL : dump cohérent et restaurable de l’état serveur ; export quotidien ; RTO 24 h accepté, perte de jobs jusqu’à 3 jours acceptée. Dépendances MIT et compatibilité à inventorier.
- Contrats normatifs indépendants, IDs stables, registre local offline partagé et définitions communes non dupliquées.

## Statut des divergences restantes

Les formulations historiques marquées `PROPOSITION`, notamment sur suspension, catch-up/jitter, routes HTTP et codes de réponse, restent proposées ou différées et ne doivent pas être lues comme des validations. Les détails d’agrégation de plusieurs destinations/hooks, la procédure LDAP complète de mapping de rôles, la méthode exacte de rotation/révocation hors ligne et certains détails d’export restent à préciser ; aucune décision nouvelle n’est inventée ici.

## Vérifications exécutées

- Branches et HEAD vérifiés via GitHub ; aucune opération sur `main`, aucun merge, aucune fermeture et aucune suppression.
- Arborescences `docs`, `contracts` et `scripts` inventoriées ; le commit `c28e1bb` vérifié comme publication du contrat documentaire.
- Les documents et exemples disponibles ont été inspectés par recherche ciblée des termes de décision.
- Validation JSON hors ligne préparée mais non déclarée réussie : l’environnement d’exécution ne fournissait pas le module Python `jsonschema` requis par `scripts/validate-contracts.py`. Aucun résultat de test de schéma n’est donc revendiqué.

## Références d’ancrage

- `docs/17-cadrage-llm-ready.md` : séquence, versions, Outbox, hooks, enrollment, scheduling, sécurité et RPO.
- `docs/18-audit-decisions-2026-10-21.md` : audit décisionnel existant.
- `docs/20-contrats-json-echanges.md` : catalogue explicatif ; les schémas v1 sous `contracts/schemas/v1/` restent normatifs.
- `contracts/README.md` et `scripts/validate-contracts.py` : organisation et validation offline.
