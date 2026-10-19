# Glossaire du domaine

Phase de conception — **NON PRÊT POUR LA PRODUCTION**. Révision : 2026-10-10.

Ce fichier est la source canonique de la terminologie du domaine. Les autres documents doivent y faire référence plutôt que dupliquer les définitions. Les modèles conceptuels et cardinalités de [Modèles, relations et invariants](15-modeles-relations.md) restent des propositions ; ils ne constituent ni un schéma SQL livré ni une approbation implicite de toutes les règles.

## Identité et configuration

| Terme / modèle | Définition |
|---|---|
| Machine | Identité stable de l’hôte sauvegardé ; possède ses profiles et repositories. Ce n’est pas simplement le hostname. |
| Client / agent / Agent | Programme exécuté sur la machine pour synchroniser les schedules, exécuter Restic et transmettre les résultats. Son identité d’enrôlement peut changer sans nécessairement changer celle de la machine. |
| Serveur | Programme Go de coordination, API, web et reporting utilisant PostgreSQL. Ce n’est pas le repository de sauvegarde. |
| Profile / BackupProfile | Définition d’une sauvegarde de machine : fileset, destinations, hooks, options et rétention. |
| Fileset / FileSet | Sélection des sources incluses et exclusions. Il s’agit de configuration, pas d’une liste des fichiers effectivement sauvegardés. |
| Policy | Terme générique à préciser, par exemple policy de rétention ou de maintenance. BackupPolicy désignait initialement le profile ; utiliser BackupProfile pour l’instance exécutée. Le modèle de templates de profiles partagés n’est pas encore défini. |
| Révision / ConfigRevision | Version immuable de la configuration effective utilisée pour une exécution. Une nouvelle configuration ne modifie pas les exécutions précédentes. |
| Référence de secret / SecretReference | Identifiant servant à résoudre un secret, pas sa valeur. Distinguer les tokens API, credentials du backend et secret Restic. |
| Hook / HookDefinition | Action configurée avant ou après une opération ; HookResult est son résultat d’exécution. Un hook seul ne garantit pas la cohérence applicative. |

## Repositories et snapshots

| Terme / modèle | Définition |
|---|---|
| Repository | Repository Restic appartenant à une seule machine. Un backend de stockage peut héberger plusieurs repositories isolés. |
| Backend | Service ou protocole de stockage ; ne représente ni la propriété machine ni un snapshot. |
| Destination / ProfileDestination | Association entre un profile et un repository, avec rôle primaire ou réplication et règle obligatoire/facultative. Le rôle appartient à cette association. |
| Snapshot / SnapshotRecord | Point de sauvegarde identifié dans un repository ; le serveur ne stocke que les métadonnées et associations, pas l’inventaire des fichiers. |
| Réplication / copy | Copie d’un snapshot d’un repository vers un autre repository appartenant à la même machine ; distincte d’une nouvelle lecture des sources. |
| Replica | Snapshot présent dans une destination de réplication ; son ID n’est pas supposé identique à celui du snapshot primaire. |
| Rétention / RetentionPolicy | Règles déterminant quels snapshots conserver ; ne spécifie pas à elle seule quand le nettoyage s’effectue. |
| forget | Opération retirant les snapshots sélectionnés ; distincte de la suppression physique des données devenues inutiles. |
| prune | Opération nettoyant les données du repository qui ne sont plus nécessaires ; ne signifie pas appliquer la policy de rétention d’un profile. |
| check | Opération de vérification d’un repository ; préciser si elle est structurelle ou lit les données, ainsi que son périmètre. |
| stats / RepositoryObservation | Collecte datée de statistiques de repository, qualifiée par son mode et sa sélection ; des collectes répétées ne sont pas des volumes à additionner. |

## Planification et exécution

| Terme / modèle | Définition |
|---|---|
| Schedule | Règle calculant les occurrences futures : intervalle ancré ou heure quotidienne avec fuseau horaire. |
| Planning / PlanningRevision | Ensemble versionné de tâches calculé par le serveur et distribué à un client. Ce n’est pas un scheduler client autonome. |
| Occurrence | Échéance logique de planification avec identité unique et déduplication. |
| Job | Travail logique demandé, planifié ou manuel, avec cible et configuration. Les retries ne sont pas de nouveaux jobs. |
| Attempt | Tentative d’exécution d’un job. Un job peut nécessiter plusieurs tentatives. |
| Step / Operation | Unité exécutée pendant une tentative, telle qu’un pre-hook, backup, copy ou post-hook. Modèle proposé pour les jobs composites. |
| Résultat de destination / DestinationResult | Résultat d’une opération sur un repository donné, avec code, état, snapshot facultatif et métriques. |
| Dépendance / JobDependency | Condition entre jobs, par exemple un check après prune. Relation orientée et acyclique. |
| Réservation / lease | Autorisation temporaire de coordination ; son expiration ne prouve pas l’arrêt d’un processus Restic. |
| Lock | Exclusion d’exécution au niveau machine, coordination repository ou Restic. Ces niveaux ne sont pas interchangeables. |
| Suspension / MaintenanceWindow | Empêchement planifié de démarrages pour une machine, un profile ou un repository, avec périmètre explicitement défini. |
| Désactivation | Arrête la planification sans reprise automatique implicite. Ne signifie pas suppression de l’objet. |

## Observation et exploitation

| Terme / modèle | Définition |
|---|---|
| Event / Event | Fait horodaté transmis de manière idempotente ; occurred_at et received_at ont des significations distinctes. |
| Outbox | Stockage local des événements en attente de livraison, conservés jusqu’à acquittement. Ce n’est pas l’historique serveur. |
| Heartbeat | Signal de présence de l’agent ; ne prouve pas la progression d’un backup. |
| État d’exécution | Résultat ou progression du travail, par exemple running, succeeded, partial ou failed. |
| État d’observation | Ce que sait le serveur, par exemple joignable, injoignable ou incertain ; ne prouve pas le résultat réel. |
| Réussite complète | Résultat satisfaisant la règle de réussite du job ; l’agrégation primaire/copies/hooks reste à formaliser. |
| Incident / Incident | Anomalie suivie jusqu’à résolution ; l’acquittement n’est pas la résolution. |
| Notification / NotificationDelivery | Livraison d’un message d’incident ou récapitulatif ; un échec de livraison ne modifie pas le résultat du backup. |
| Rapport | Vue calculée sur une période et des dimensions machine/profile/repository ; préciser la population et le dénominateur. |
| Export / ServerExport | Copie locale cohérente de l’état serveur pour backup externe ; pas un backup des repositories Restic. |
| Opérateur / Operator | Identité humaine dotée de rôles applicatifs ; distincte d’un Agent et de son token. |
| Audit / AuditEvent | Enregistrement d’une action administrative ou sensible, distinct de la progression Restic. |

## Distinctions importantes

Un job peut réussir sans créer de nouveau snapshot. Une copy peut échouer alors que le backup primaire réussit. Un agent injoignable peut avoir terminé un job. La maintenance machine n’est pas la maintenance repository. Un export serveur n’est pas une restauration applicative. Un compteur manquant n’est pas égal à zéro.

## Documents associés

Le document 10, consacré aux options et statistiques, n’est pas publié dans le dépôt. Son contenu ne peut pas être considéré comme une spécification disponible ; consulter les documents existants et valider explicitement toute proposition avant implémentation.
