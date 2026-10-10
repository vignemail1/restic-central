# Configuration et exécution

Statut : schéma conceptuel proposé, pas une configuration utilisable.

## Séparation des configurations

Configuration agent : identité, endpoint du serveur, authentification, chemins de stockage local, binaire Restic, limites locales.

Politique de sauvegarde : sources, exclusions, dépôts, planification centrale, contraintes, délais et rétention éventuelle. Le serveur stocke des références de secrets ; la résolution locale est privilégiée.

## Exemple indicatif

```yaml
schema_version: 1
policy_id: system-backup
revision: 1
sources:
  include: [/etc, /home]
  exclude: [/home/*/.cache]
  required_mounts: [/home]
destinations:
  - id: primary
    backend: s3
    repository: s3:https://storage.example.invalid/backups/system
    required: true
    secrets:
      repository_password: {source: env, name: RESTIC_PASSWORD}
      access_key: {source: env, name: AWS_ACCESS_KEY_ID}
      secret_key: {source: env, name: AWS_SECRET_ACCESS_KEY}
execution:
  strategy: independent
  destination_order: sequential
  success_rule: all_required
  max_runtime: 4h
  timeout_action: alert_only
schedule:
  authority: server
  expression: '0 2 * * *'
  timezone: Europe/Paris
  start_deadline: 1h
  catch_up: latest_only
```

Les champs et valeurs sont provisoires. Les délais de l'exemple ne constituent pas des valeurs adaptées à tous les environnements. La grammaire cron, les exclusions et leur traduction vers Restic doivent être spécifiées puis testées.

## Préconditions

Vérifier chemins requis, permissions et montages attendus ; ne pas sauvegarder silencieusement un répertoire vide remplaçant un volume absent. Définir le comportement pour chaque source optionnelle ou obligatoire.

Définir si la sauvegarde doit rester sur un filesystem et comment traiter les liens symboliques. Pour les données applicatives, prévoir dumps ou snapshots cohérents. Des fichiers en cours de modification ne garantissent pas la cohérence d'une base de données.

Les hooks futurs devront avoir une liste d'autorisation, un environnement limité, un timeout, un traitement des erreurs et une règle de nettoyage même en cas d'échec. Ils sont hors MVP.

## Destinations multiples

Stratégie indépendante : lancer un backup par dépôt. Orientation MVP : destinations séquentielles ; les lectures successives peuvent observer des données différentes.

Stratégie backup puis copy : créer un snapshot primaire puis le copier vers les dépôts secondaires. Cette évolution doit gérer séparément échec primaire, réplication, authentification des deux dépôts et identification des snapshots. Ne pas supposer des identifiants identiques entre dépôts.

Le job réussit si toutes ses destinations obligatoires réussissent complètement. Une destination facultative en échec reste visible et peut produire un incident sans transformer automatiquement le job en échec. Si une destination obligatoire est incomplète, le résultat global ne peut pas être succeeded. La table d'agrégation exhaustive reste à formaliser.

Un retry vise uniquement les opérations nécessaires, conserve la traçabilité et doit tenir compte du fait qu'un nouvel essai peut produire un nouveau snapshot.

## Exécution Restic

Lancer le processus avec arguments structurés et environnement contrôlé, sans concaténation shell. Collecter stdout JSON et stderr séparément. Préserver code de sortie, version Restic et résumé final.

Pour backup, distinguer notamment réussite complète et snapshot incomplet : le code 3 ne doit pas être assimilé à une réussite complète. La table de codes et les champs JSON doivent être vérifiés contre chaque version de Restic supportée. Ne pas appliquer indistinctement les règles de backup à check, copy ou prune.

Les erreurs de parsing sont explicites ; ne pas inventer de métriques absentes.

## Délais

- start_deadline : retard maximal avant démarrage.
- max_runtime : durée totale autorisée.
- heartbeat_timeout : absence de contact agent.
- progress_timeout : absence de progression, détection facultative.
- termination_grace_period : délai entre arrêt gracieux et escalade.

Par défaut proposé, un dépassement signale une anomalie et nécessite une vérification ; il ne tue pas automatiquement Restic. L'arrêt automatique est une option distincte. L'absence de progression n'est pas une preuve suffisante de blocage.

## Verrouillage et reprise

Un verrou système local couvre toutes les sauvegardes de l'agent et les commandes locales passant par le même gestionnaire. Les invocations Restic externes ne sont pas implicitement couvertes.

Le serveur réserve les jobs ; les opérations de maintenance sont coordonnées par dépôt. Les verrous natifs Restic sont conservés. Aucun unlock automatique à partir d'un simple timeout.

Après redémarrage, inspecter les tentatives persistées et le processus éventuellement encore vivant. Un PID seul ne suffit pas à identifier un ancien processus. Ne pas relancer tant que l'exécution précédente reste incertaine.

## Maintenance

Prévoir ultérieurement des jobs distincts pour forget, prune, check, copy et tests de restauration. La suppression de snapshots et la maintenance destructive nécessitent droits et protections spécifiques.

Références de validation :
- https://restic.readthedocs.io/en/stable/040_backup.html
- https://restic.readthedocs.io/en/stable/075_scripting.html
- https://restic.readthedocs.io/en/stable/045_working_with_repos.html

Ces liens sont des références à vérifier pendant l'implémentation ; aucune compatibilité de version n'est annoncée ici.
