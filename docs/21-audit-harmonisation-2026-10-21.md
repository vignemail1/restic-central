# Audit d’harmonisation documentaire — 2026-10-21

## Périmètre et état vérifié

Audit exécuté sur `vignemail1/restic-central`, branche `docs/llm-cadrage-decisions-2026-10-21`, dont le HEAD vérifié avant correction était `2e508d66492a001259afe819150034733a6f2e31` (le SHA historique `c28e1bb…` était inexact). La branche `main` a été laissée intacte. Ce fichier est un rapport d’audit : il ne remplace pas les contrats JSON ni les documents normatifs.

Le dépôt contient les documents `docs/01` à `docs/20`, les schémas et exemples sous `contracts/`, ainsi que les scripts de validation. La publication existante couvre déjà la plupart des décisions validées ; les points ci-dessous sont les règles canoniques à appliquer lorsque des formulations historiques divergent.

## Règles validées à harmoniser

- Ordre de livraison : agent autonome + hooks + Outbox, enrollment serveur, enrollment client, résultats serveur, résultats client, configuration serveur, auto-configuration client, scheduling serveur.
- MVP : agent et serveur Linux amd64 ; macOS arm64 et Windows amd64 futurs ; Go 1.27 ; Restic >= 0.19.0.
- Configuration restreinte séparée des données variables durables. Outbox durable, at-least-once ; en saturation, éviction stricte des événements les plus anciens et perte observable ; aucun état actif supprimé.
- Échec primaire/pre-hook, Restic interrompu/timeout/sortie indécodable : `failed`. Réplication ou post-hook échoué après backup réussi : `partial`. Un échec primaire reste `failed`, même si un post-hook échoue simultanément ; les résultats par étape sont conservés. Un retry réussi reste `partial` pour investigation. Post-hook après échec pre-hook : configurable, `false` par défaut.
- Job serveur non récupéré : remplacement futur ; ACK d’expiration par défaut à `start + 12 h`. Un job en overlap est annulé avec motif `running`.
- Maintenance offline mise en cache et résultats remontés via Outbox. Snapshot primaire expiré ou inexistant : réplication abandonnée et `failed`. Rétention opérateur via directives Restic `keep-*`, avec protection obligatoire d’au moins le dernier snapshot valide par machine/profile/repository ; un snapshot expiré non répliqué peut être supprimé selon la policy, sauf cette protection et les autres garde-fous. Les snapshots à réussite inconnue ou non identifiés restent protégés ; aucune interdiction générale supplémentaire des snapshots en attente de copy n’est ajoutée.
- Secrets par variable d’environnement ou commande par clé ; fnox est une option initiale. Aucun secret ni identifiant de job dans les logs.
- Enrollment : machine pré-déclarée, token unique et révocable, valable 12 h, renouvellement manuel uniquement.
- `schema_version` entier commençant à 1 ; négociation par version commune maximale, refus sans intersection. Extensions JSON DB préservées sans interprétation ni exécution. `server_job_id` attribué à l’ingestion ; déduplication durable, ACK après persistance, puis suppression Outbox.
- LDAP `posixAccount` avec filtre additionnel et StartTLS vérifié. Superadmin local de récupération et safeguards de session. Le mapping LDAP groupes→rôles est explicitement futur/différé ; il n’est pas un blocker de l’authentification et du périmètre initial. Toute action opérateur auditée.
- PostgreSQL : dump cohérent et restaurable de l’état serveur ; export quotidien ; RTO 24 h accepté, perte de jobs jusqu’à 3 jours acceptée. Dépendances MIT et compatibilité à inventorier.
- Contrats normatifs indépendants, IDs stables, registre local offline partagé et définitions communes non dupliquées.

## Statut des divergences restantes

Les formulations historiques marquées `PROPOSITION`, notamment sur suspension, catch-up/jitter, routes HTTP et codes de réponse, restent proposées ou différées et ne doivent pas être lues comme des validations. Les détails d’agrégation de plusieurs destinations/hooks, la méthode exacte de rotation/révocation hors ligne et certains détails d’export restent à préciser ; le mapping LDAP groupes→rôles est une évolution future, pas un blocker. Les propositions restent explicitement étiquetées et ne créent pas de règle concurrente.

## Vérifications exécutées

- Branches et HEAD vérifiés via GitHub ; aucune opération sur `main`, aucun merge, aucune fermeture et aucune suppression.
- Arborescences `docs`, `contracts` et `scripts` inventoriées ; les schémas normatifs sont sous `contracts/schemas/v1/`.
- Les documents et exemples disponibles ont été inspectés par recherche ciblée des termes de décision.
- La validation JSON n’est pas réussie : l’exécution s’arrête d’abord sur `ModuleNotFoundError: No module named jsonschema` à la ligne 9 de `scripts/validate-contracts.py`. L’inspection statique de la source montre toutefois que les 24 schémas `contracts/schemas/v1/*.schema.json` n’ont pas de `$id` top-level : par exemple `contracts/schemas/v1/_shared.schema.json:2-4` ne contient que `$schema`, `$ref` et `$comment`, et `contracts/schemas/v1/agent.enroll.schema.json:1` ne contient que `$schema`, `allOf` et `$ref`. Le chargeur `validate_paths` (lignes 44-52) exige ce champ et produirait `$id manquant` pour chacun après installation de la dépendance ; aucun schéma n’a été réécrit dans ce correctif. Le validateur ne peut donc pas être déclaré passant.

## Références d’ancrage

- `docs/16-decisions-for-development.md` : décisions de développement canoniques, notamment hooks et résultats.
- `docs/07-decisions.md` : registre des statuts et historique.
- `docs/09-specifications-revisees.md` : règles détaillées canoniques, notamment résultats, rétention et LDAP.
- `docs/11-decision-postgresql.md` : choix PostgreSQL.
- `docs/13-retention-planning.md` : planification/rétention et protection du dernier snapshot.
- `docs/20-contrats-json-echanges.md` : catalogue explicatif ; les schémas v1 sous `contracts/schemas/v1/` restent normatifs.
- `contracts/README.md` et `scripts/validate-contracts.py` : organisation et validation offline.

