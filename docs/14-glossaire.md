# Glossaire du domaine

Projet en conception — NON PRÊT POUR LA PRODUCTION. Révision : 2026-10-10.

Ce glossaire définit les termes employés dans les spécifications. Les modèles supplémentaires sont des propositions de normalisation, pas un schéma SQL livré ni une validation implicite de toutes leurs règles. Voir [les relations](15-modeles-relations.md).

## Identité et configuration

| Terme / modèle | Définition |
|---|---|
| Machine / Machine | Identité stable de l'hôte sauvegardé ; propriétaire de ses profils et repositories. Ne se réduit pas au hostname. |
| Client / agent / Agent | Programme exécuté sur la machine, chargé de synchroniser le planning, exécuter Restic et remonter les résultats. Son identité d'enrôlement peut changer sans changer nécessairement la machine. |
| Serveur | Programme Go de coordination, API, web et reporting ; utilise PostgreSQL. Ce n'est pas le repository de sauvegarde. |
| Profil / BackupProfile | Définition d'une sauvegarde d'une machine : fileset, destinations, hooks, options et rétention. |
| Fileset / FileSet | Sélection des sources à inclure et exclusions. C'est une configuration de sélection, pas la liste des fichiers effectivement sauvegardés. |
| Politique / Policy | Terme générique à qualifier : politique de rétention, de maintenance, etc. BackupPolicy désignait initialement le profil ; utiliser BackupProfile pour l'instance exécutée. Un modèle partagé de profil n'est pas encore défini. |
| Révision / ConfigRevision | Version immuable de la configuration effective utilisée par une exécution. Une nouvelle configuration ne modifie pas les anciennes exécutions. |
| Référence de secret / SecretReference | Identifiant de résolution d'un secret, pas sa valeur. Distinguer token API, credentials backend et secret Restic. |
| Hook / HookDefinition | Action configurée avant/après les opérations ; HookResult est son résultat d'exécution. Ne garantit pas à lui seul la cohérence applicative. |

## Dépôts et snapshots

| Terme / modèle | Définition |
|---|---|
| Repository / Repository | Dépôt Restic appartenant à une seule machine. Un backend de stockage peut héberger plusieurs dépôts isolés. |
| Backend | Service ou protocole de stockage ; ne représente ni la propriété machine ni un snapshot. |
| Destination / ProfileDestination | Association profil-repository avec rôle primaire ou réplication et règle d'obligation. Le rôle dépend de cette association. |
| Snapshot / SnapshotRecord | Point de sauvegarde identifié dans un repository ; côté serveur, seulement métadonnées et associations, pas inventaire de fichiers. |
| Réplication / copy | Copie d'un snapshot d'un dépôt vers un autre dépôt de la même machine ; distincte d'une nouvelle lecture des sources. |
| Réplica | Snapshot présent dans une destination de réplication ; son ID n'est pas supposé égal à celui du primaire. |
| Rétention / RetentionPolicy | Règles déterminant les snapshots conservés ; ne définit pas à elle seule l'heure de purge. |
| forget | Opération retirant des snapshots sélectionnés ; distincte de la suppression physique des données devenues inutiles. |
| prune | Opération de nettoyage des données non nécessaires du dépôt ; ne signifie pas appliquer une politique de rétention de profil. |
| check | Opération de contrôle du dépôt ; préciser contrôle structurel ou lecture des données et périmètre. |
| stats / RepositoryObservation | Collecte datée de statistiques d'un repository, qualifiée par mode et sélection ; ce n'est pas un volume à additionner à chaque collecte. |

## Planification et exécution

| Terme / modèle | Définition |
|---|---|
| Programmation / Schedule | Règle calculant les prochaines occurrences : intervalle ancré ou heure quotidienne avec TZ. |
| Planning / PlanningRevision | Ensemble versionné de tâches calculées par le serveur et distribuées à un client. Ce n'est pas un scheduler autonome client. |
| Occurrence | Échéance logique d'une programmation, identifiée et dédupliquée. |
| Job / Job | Travail logique demandé, planifié ou manuel, avec cible et configuration. Ne pas compter les retries comme de nouveaux jobs. |
| Tentative / Attempt | Essai d'exécution d'un job. Plusieurs tentatives peuvent être nécessaires. |
| Étape / Operation | Unité exécutée dans une tentative : pre-hook, backup, copy, post-hook, etc. Proposition de modèle pour les jobs composites. |
| Résultat destination / DestinationResult | Résultat d'une opération sur un dépôt précis, avec code, état, snapshot éventuel et métriques. |
| Dépendance / JobDependency | Condition entre jobs, par exemple contrôle après prune. Relation dirigée sans cycle. |
| Réservation / lease | Autorisation temporaire de coordination ; son expiration ne prouve pas l'arrêt d'un processus Restic. |
| Verrou | Exclusion d'exécution : local machine, coordination dépôt ou verrou Restic. Ces niveaux ne se remplacent pas. |
| Suspension / MaintenanceWindow | Arrêt planifié des départs pour une machine, un profil ou un dépôt, selon portée explicitement définie. |
| Désactivation | Arrêt de la programmation sans reprise automatique implicite. N'est pas la suppression de l'objet. |

## Observation et exploitation

| Terme / modèle | Définition |
|---|---|
| Événement / Event | Fait horodaté transmis de manière idempotente ; occurred_at et received_at ont des sens distincts. |
| Outbox | Stockage local des événements à transmettre, conservés jusqu'à acquittement. Ce n'est pas l'historique serveur. |
| Heartbeat | Signal de présence de l'agent ; pas une preuve de progression du backup. |
| État d'exécution | Résultat ou progression du travail : running, succeeded, partial, failed, etc. |
| État d'observation | Ce que sait le serveur : joignable, injoignable, état incertain ; ne prouve pas le résultat réel. |
| Succès complet | Résultat satisfaisant la règle de succès du job ; l'agrégation primaire/copies/hooks reste à formaliser. |
| Incident / Incident | Anomalie suivie jusqu'à résolution ; acquitter n'est pas résoudre. |
| Notification / NotificationDelivery | Livraison d'un message d'incident ou synthèse ; un échec de livraison ne change pas le backup. |
| Rapport | Vue calculée sur une période et des dimensions machine/profil/dépôt ; préciser population et dénominateur. |
| Export / ServerExport | Copie cohérente locale de l'état serveur pour sauvegarde externe ; ce n'est pas une sauvegarde des repositories Restic. |
| Opérateur / Operator | Identité humaine avec rôles applicatifs ; distincte d'un Agent et de son token. |
| Audit / AuditEvent | Trace d'une action administrative ou sensible, distincte des progressions Restic. |

## Distinctions obligatoires

Un job peut réussir sans nouveau snapshot. Une copy peut échouer alors que le backup primaire a réussi. Un agent injoignable peut avoir terminé un job. Une maintenance machine n'est pas une maintenance du repository. Un export serveur n'est pas une restauration applicative. Un compteur absent n'est pas zéro.

Les détails du document 10 sur les options et statistiques restent une publication en attente ; ce glossaire ne prétend pas qu'il est présent dans le dépôt.
