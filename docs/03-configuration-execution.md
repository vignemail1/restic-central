# Configuration et exécution

Statut : conception initiale conservée à titre historique. En cas de conflit avec les [spécifications révisées](09-specifications-revisees.md), celles-ci prévalent. Ce document n’est pas une source indépendante d’exigences actuelles.

Pour la terminologie canonique, consulter le [glossaire du domaine](14-glossaire.md). Pour les relations conceptuelles, consulter [modèles, relations et invariants](15-modeles-relations.md).

## Séparation de la configuration

Configuration de l’agent : identité, endpoint serveur, authentification, chemins de stockage local, binaire Restic et limites locales.

La conception initiale décrivait une policy de sauvegarde avec sources, exclusions, repositories, schedule central, contraintes, limites de durée et rétention facultative. Les exigences actuelles relatives aux profiles sont définies dans le document 09 ; conserver la distinction entre les anciens noms et la terminologie actuelle.

## Exemple illustratif (historique)

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

Les champs et valeurs sont provisoires. Cet exemple historique utilise cron et des destinations indépendantes, tous deux remplacés par le document 09 lorsque applicable. Ses limites de durée ne conviennent pas par défaut à tous les environnements. Tout futur format de configuration, sémantique des exclusions et traduction en arguments Restic doivent être spécifiés et testés.

## Prérequis

Vérifier les chemins requis, les permissions et les mounts attendus ; ne pas sauvegarder silencieusement un répertoire vide qui remplacerait un volume manquant. Définir le comportement pour chaque source facultative ou obligatoire.

Définir si les sauvegardes restent dans un seul filesystem et comment les liens symboliques sont traités. Pour les données applicatives, prévoir des dumps ou snapshots cohérents. Des fichiers en cours de modification ne garantissent pas la cohérence d’une base de données.

Le comportement et les exigences de sécurité des hooks sont couverts par le document 09 ; ne pas considérer comme actuelle leur exclusion initiale du MVP. Toute implémentation nécessite une allowlist, un environnement restreint, un timeout, la gestion des erreurs et des règles de cleanup même en cas d’échec.

## Destinations multiples

La conception initiale envisageait des sauvegardes indépendantes par repository et des destinations séquentielles. Cette approche est remplacée par la direction « backup primaire puis copy » du document 09. L’agrégation des statuts, les destinations obligatoires ou facultatives et les snapshots incomplets restent à résoudre selon les spécifications révisées et le registre des décisions.

Les retries doivent cibler uniquement les opérations nécessaires, préserver la traçabilité et tenir compte du fait qu’une autre tentative peut créer un nouveau snapshot.

## Exécution de Restic

Démarrer le processus avec des arguments structurés et un environnement contrôlé, sans concaténer des commandes shell. Collecter séparément stdout JSON et stderr. Préserver le code de sortie, la version de Restic et le résumé final.

Pour un backup, distinguer une réussite complète d’un snapshot incomplet : le code de sortie 3 ne doit pas être traité comme une réussite complète. Les correspondances entre codes de sortie et champs JSON doivent être vérifiées pour chaque version de Restic prise en charge. Ne pas appliquer indistinctement les règles du backup à check, copy ou prune.

Les erreurs de parsing doivent être explicites ; ne pas inventer les métriques manquantes.

## Limites de durée

- start_deadline : délai maximal avant le démarrage.
- max_runtime : durée totale maximale.
- heartbeat_timeout : durée sans contact avec l’agent.
- progress_timeout : durée sans progression ; détection facultative.
- termination_grace_period : délai entre une demande d’arrêt gracieux et l’escalade.

La proposition initiale consistait à signaler une anomalie à inspecter en cas de dépassement, sans tuer automatiquement Restic. Un arrêt automatique nécessite une décision distincte. Une absence de progression ne suffit pas à prouver qu’un processus est bloqué.

## Verrouillage et reprise

Un lock local au niveau du système d’exploitation couvre tous les backups de l’agent et les commandes locales utilisant le même moteur d’exécution. Les invocations externes de Restic ne sont pas couvertes implicitement.

Le serveur réserve les jobs ; les opérations de maintenance sont coordonnées par repository. Les locks natifs Restic sont conservés. Aucun unlock automatique sur la seule base d’un timeout.

Après redémarrage, inspecter les tentatives persistées et tout processus encore actif. Un PID seul ne suffit pas à identifier un ancien processus. Ne pas réessayer tant que l’exécution précédente reste incertaine.

## Maintenance

Prévoir des jobs distincts pour forget, prune, check, copy et les tests de restauration. La suppression de snapshots et la maintenance destructive exigent des permissions et garde-fous spécifiques.

Références de validation :
- https://restic.readthedocs.io/en/stable/040_backup.html
- https://restic.readthedocs.io/en/stable/075_scripting.html
- https://restic.readthedocs.io/en/stable/045_working_with_repos.html

Ces liens sont des références à vérifier pendant l’implémentation ; aucune compatibilité de version n’est revendiquée ici.
