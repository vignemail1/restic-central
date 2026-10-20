# Options statistiques et métriques

Date : 2026-10-20. Statut : document de conception, **NON PRÊT POUR LA PRODUCTION**.

Ce document publie les options de travail relatives aux statistiques, aux rapports et aux observations de `restic-central`. Il complète [les spécifications révisées](09-specifications-revisees.md), [le registre des décisions](07-decisions.md), [la décision PostgreSQL](11-decision-postgresql.md), [l'isolation des repositories](12-isolation-repositories.md), [la planification de rétention](13-retention-planning.md) et [les modèles et relations](15-modeles-relations.md). Il ne constitue ni un schéma SQL, ni un contrat REST stable, ni une validation de choix encore ouverts.

Les mots `ACCEPTÉ`, `PROPOSITION OUVERTE` et `NON-OBJECTIF` décrivent explicitement le statut de chaque élément. Une proposition publiée ici n'est pas une décision acceptée.

## 1. Principes et périmètre

`restic-central` conserve des métadonnées de coordination et des résultats transmis par les agents. Le flux de données de backup va de l'agent vers les repositories ; le serveur central n'héberge pas les repositories de backup.

Les statistiques doivent permettre de répondre à des questions opérationnelles :

- quelles occurrences étaient attendues, exécutées, réussies ou manquées ;
- quel est l'état de chaque `BackupProfile`, `DestinationResult`, `Attempt` et `Repository` ;
- quand un backup complet ou un `check` a-t-il réussi pour la dernière fois ;
- quelle est la fraîcheur par rapport à une cible de type RPO ;
- combien de temps les opérations et leurs étapes ont-elles pris ;
- quels volumes ont été mesurés, par quelle source et avec quelle incertitude ;
- quels incidents, tentatives répétées, hooks et copies restent ouverts ou incomplets.

### 1.1 Non-inventaire des fichiers

Le périmètre **n'inclut pas l'inventaire des fichiers sauvegardés**. `FileSet` décrit les chemins inclus/exclus de la configuration ; il ne devient pas une télémétrie de chaque fichier. Le serveur ne doit pas recevoir ni agréger de liste de fichiers, de taille par fichier, de hash par fichier ou de catalogue de contenu pour produire les métriques décrites ici.

Les compteurs concernent les jobs, tentatives, étapes, snapshots connus par leurs associations fiables, repositories, événements, durées et volumes agrégés. Une statistique de volume ne doit jamais être présentée comme un inventaire de fichiers.

### 1.2 Statut global

Le projet reste au stade de l'idée et de la conception. Aucun agent, serveur, UI, API, test, benchmark, capacité mesurée ou audit de production n'est livré. Les exemples de champs, endpoints et métriques ci-dessous sont des options à spécifier et tester, pas des fonctionnalités disponibles.

## 2. Références acceptées et contraintes à confirmer

Les éléments suivants reprennent des exigences ou décisions de référence. Les points explicitement marqués **PROPOSITION OUVERTE** ne sont pas approuvés ; les autres contraintes sont reprises à des fins de cohérence et ne valent pas, à elles seules, nouvelle décision.

### 2.1 Identité et granularité

- **CONTRAINTE REPRISE** : les métriques identifient au minimum `Machine`, `BackupProfile`, `ConfigRevision`, `Job`, `Attempt` et `DestinationResult` lorsque l'objet existe.
- **ACCEPTÉ (`P06`)** : un `Job` logique est distinct de ses `Attempt` et de ses résultats par destination. Un retry n'augmente pas le nombre de jobs.
- **ACCEPTÉ (`O11`)** : une copie (`restic copy`) est une opération de réplication liée à un snapshot source identifié ; elle n'est pas un second backup indépendant et ne doit pas faire relire les sources.
- **CONTRAINTE REPRISE** : les repositories primaire et répliqués restent distingués. Leurs volumes ne doivent pas être additionnés comme s'ils représentaient des données source distinctes.
- **PROPOSITION OUVERTE** : séparer l'état d'exécution et l'état d'observation serveur : `unreachable`, `suspected_stuck` ou `reconciliation_required` ne prouvent pas le résultat du processus.

### 2.2 Rétention et données historiques

- **ACCEPTÉ** : la rétention des instantanés est configurée côté client, par profil/repository lorsque nécessaire (`O08`).
- **PROPOSITION OUVERTE** : `forget` et `prune` sont des opérations différentes ; leurs jobs, résultats et éventuelles statistiques devraient être distingués.
- Aucun `prune` ou `forget` destructif ne doit être déduit d'une métrique. Une association snapshot/job incertaine, un snapshot inconnu ou une règle de rétention invalide impose une absence de suppression automatique.
- **PROPOSITION OUVERTE** : la durée de conservation des logs, événements et audit reste à définir. La rétention des snapshots n'établit pas automatiquement la rétention des détails opérationnels.

### 2.3 Rapports et fenêtres

- **PROPOSITION OUVERTE** : prévoir un résumé de 24 heures et un rapport de 7 jours ; leurs détails seraient filtrables par machine/profil/destination.
- **PROPOSITION OUVERTE** : faire porter le périmètre du rapport de 7 jours sur les heures planifiées des jobs, en présentant séparément les heures de début et de fin.
- **CONTRAINTE REPRISE** : les périodes affichent explicitement le fuseau horaire et leurs bornes. Une fenêtre glissante ne doit pas être confondue avec un jour calendaire.
- **ACCEPTÉ (`P13`)** : les notifications couvrent les incidents immédiats, le résumé quotidien et la notification de rétablissement ; cela n'approuve pas une formule particulière de success rate.

### 2.4 Dimensionnement

La cible de conception est de prendre en charge une année de jobs pour 300 machines. L'illustration d'un profil quotidien par machine donne 109 500 jobs sur 365 jours, hors lancements manuels ; ce n'est pas une capacité mesurée. Le dimensionnement doit compter séparément profils, tentatives, résultats par destination, hooks, événements, incidents, livraisons et logs détaillés.

## 3. Métriques demandées

Cette section définit le minimum fonctionnel à couvrir par la spécification et les futurs tests. Elle ne fixe pas encore le stockage final ni tous les agrégats.

### 3.1 Occurrences et jobs

Par période et par `Machine`/`BackupProfile`/destination :

- occurrences attendues ;
- jobs créés, démarrés, réussis, incomplets, échoués, annulés, ignorés (`skipped`) et manqués ;
- jobs en attente ou en cours ;
- nombre d'`Attempt`, séparé du nombre de jobs ;
- nombre et durée des tentatives répétées ;
- délai d'attente avant démarrage (`queued`/`claimed` vers `running`) ;
- âge de la dernière réussite complète ;
- origine `automatic` ou `local_manual` ;
- distinction entre maintenance planifiée, absence attendue, observation inconnue et échec réel.

Une occurrence attendue dans une fenêtre de maintenance ne doit pas être comptée comme un échec. Une occurrence non créée à cause d'une règle de scheduling doit rester explicable et ne pas disparaître du dénominateur sans catégorie.

### 3.2 Durées et exécution

Conserver séparément, lorsqu'elles sont disponibles :

- durée totale de l'`Attempt` ;
- temps d'attente ;
- durée de la sauvegarde primaire ;
- durée de chaque `copy` par destination ;
- durée des pre-hooks et post-hooks ;
- durée de `forget`, `prune`, `check` et `stats` ;
- timestamps `scheduled_at`, `started_at`, `finished_at`, `occurred_at` et `received_at` selon l'événement concerné.

Les timestamps d'événement et de réception sont distincts afin de diagnostiquer livraison hors ligne, retards et dérives d'horloge. Les durées utilisent une horloge monotone côté agent lorsque possible ; cela ne transforme pas un timestamp local en vérité serveur.

### 3.3 Résultats et fiabilité

Par job et destination :

- état global et états par destination ;
- Restic exit code lorsque disponible ;
- snapshot source ou destination lorsque l'association est fiable ;
- résultat des hooks ;
- résultat de la dernière vérification (`check`) ;
- résultat du dernier test de restauration, séparé de la sauvegarde et du `check` ;
- incidents ouverts, acknowledged, resolved et leur catégorie ;
- nombre de résultats en attente d'outbox ou de réconciliation ;
- âge du dernier résultat connu et âge de la dernière communication agent.

Une perte de contact n'est pas une preuve d'échec ou de terminaison. Le rapport doit afficher `last_known_state` et son timestamp plutôt que convertir automatiquement l'absence d'événement en échec.

### 3.4 Fraîcheur et recoverability

Exposer séparément :

- dernière réussite complète du backup ;
- âge de cette réussite par rapport à la cible de fraîcheur/RPO ;
- dernier `check` réussi ;
- dernier test de restauration réussi ;
- présence d'une copy requise en attente ou en échec.

Un backup réussi ne remplace ni un contrôle d'intégrité ni une validation de restauration au niveau applicatif. La cohérence applicative reste hors périmètre ; les hooks peuvent préparer des fichiers cohérents, sans garantie produit de cohérence de base de données.

## 4. Volumes : définitions et limites

Les volumes sont des mesures agrégées et typées. Un champ indisponible est `null`/unavailable, jamais zéro par défaut.

Lorsque la source le permet, distinguer au minimum :

| Mesure | Signification | Source possible |
|---|---|---|
| `logical_data_processed` | données logiques traitées par Restic ou l'agent | Restic ou agent |
| `repository_data_added` | données ajoutées au repository | Restic |
| `compressed_data_added` | données ajoutées après compression, si exposé | Restic |
| `network_bytes_measured` | trafic effectivement mesuré | agent/transport |
| `repository_storage_observed` | observation de stockage d'un repository à un instant donné | agent/observation |

Ces valeurs ne sont pas interchangeables. Il est interdit de déduire un trafic réseau exact de `repository_data_added`, ou de présenter `repository_storage_observed` comme le volume d'un backup. Chaque valeur conserve `source`, `observed_at`, `scope` et, si nécessaire, un indicateur de disponibilité/qualité.

Pour plusieurs destinations, produire des totaux par repository et distinguer :

- volume source/logical traité ;
- volume ajouté au primary repository ;
- volume ajouté aux repositories de réplication ;
- espace observé dans chaque repository.

Un total inter-repositories peut compter plusieurs copies des mêmes données ; il ne représente donc pas un volume source unique.

## 5. Formules et dénominateurs à ne pas confondre

### 5.1 Success rate

Le dashboard peut proposer un success rate, mais son dénominateur doit être visible. Option cohérente avec les documents existants, à confirmer dans la spécification :

```text
complete_success_rate =
  jobs complètement réussis /
  occurrences attendues hors maintenance planifiée
```

Les catégories `partial`, `failed`, `skipped`, `missed` et `unknown` doivent rester visibles. Les tentatives répétées n'ajoutent pas de jobs au dénominateur. Une occurrence dont le résultat est encore inconnu ne doit pas être silencieusement classée réussie ou retirée.

La règle d'agrégation entre sauvegarde primaire et required copies reste une question ouverte (`O06`). Aucun seuil de réussite complète ne doit être implémenté comme décision acquise.

### 5.2 Tendances et agrégats

Les moyennes, percentiles, pires durées et tendances peuvent aider au planification de capacité, mais doivent préciser : période, population, unités, gestion des valeurs nulles et présence de jobs manuels. Un percentile calculé sur des tentatives n'est pas directement comparable à un percentile calculé sur des jobs.

Un agrégat ne doit pas masquer les événements nécessaires à l'audit ni empêcher l'application de la rétention de données détaillées. Les agrégats doivent être recalculables ou porter leur période et leur version de calcul.

## 6. Propositions ouvertes à évaluer

Les points suivants sont pertinents, mais ne sont pas approuvés.

1. **Modèle de collecte** : normaliser les compteurs dans `DestinationResult` et les observations de repository dans `RepositoryObservation`, plutôt que concaténer des payloads Restic bruts. Conserver éventuellement le payload brut expurgé pour diagnostic, sous réserve de la politique de secrets et de rétention.
2. **Agrégation temporelle** : calculer à la demande pour les fenêtres courtes, puis matérialiser des rollups journaliers pour la rétention à long terme. Définir auparavant une version de formule et une stratégie de correction des événements tardifs.
3. **Source canonique des volumes** : utiliser une valeur Restic lorsqu'elle est sémantiquement définie, une mesure agent pour le trafic, et une observation séparée pour l'espace repository. Aucun fallback silencieux entre unités différentes.
4. **Exports** : prévoir un export CSV des rapports et un format lisible par machine et versionné. Le choix CSV est seulement proposé dans [notifications et rapports](06-notifications-rapports.md) ; le format, les permissions et la pagination restent à décider.
5. **Labels de qualité** : afficher `measured`, `reported`, `estimated` ou `unavailable` afin de rendre l'incertitude visible. Les valeurs estimées ne doivent pas être utilisées dans un success rate sans règle explicite.
6. **Rétention opérationnelle** : définir séparément rétention pour les événements détaillés, logs, audit, rapports, outbox et agrégats. Cette décision doit respecter la confidentialité des chemins et noms de fichiers, destinations et logs.
7. **Cohérence avec Restic** : préciser les versions Restic supportées et l'analyse validée avant de dépendre d'un champ de sortie. La version minimale et la matrice de compatibilité restent ouvertes (`O03`).
8. **Calcul des alertes** : dériver des incidents de transitions et de fenêtres attendues, sans transformer chaque absence de heartbeat en échec. Cooldown, grouping et duplicate suppression restent à définir.
9. **Observations repository** : autoriser des mesures périodiques `stats`/espace avec un périmètre explicite, sans découvrir ni transmettre la liste des fichiers. La fréquence, le coût et le caractère obligatoire restent ouverts.

Ces options doivent être ratifiées avec contexte, alternatives, responsable, date, conséquences et tests avant d'être transformées en exigence ou en API.

## 7. Non-objectifs

Ce document ne valide pas :

- un schéma PostgreSQL, une migration ou un endpoint REST stable ;
- un choix de moteur de stockage, de pile d'interface utilisateur, de format d'export ou de fournisseur de notifications ;
- une capacité, une SLA de latence, un benchmark ou une garantie de conservation mesurée ;
- l'inventaire, la recherche, le hashage ou le suivi individuel des fichiers sauvegardés ;
- l'extraction d'un volume réseau exact lorsque Restic ou l'agent ne le mesure pas ;
- la déduction de la taille des données source depuis l'espace repository ;
- l'assimilation d'un `snapshot_id` ou de la présence de données à une preuve de succès ;
- l'exécution automatique de `forget` ou `prune`, ni une politique de suppression par défaut ;
- la cohérence au niveau applicatif ou la validation automatique d'une restauration applicative ;
- la haute disponibilité, la restauration à distance et tout comportement non accepté dans le MVP ;
- l'affirmation que le projet est prêt pour la production.

## 8. Données, confidentialité et rétention

Les noms de fichiers et chemins, logs et destinations peuvent être sensibles. Les statistiques doivent limiter le contenu collecté, éviter les secrets et respecter une politique de permissions et d'audit. Les notifications et exports doivent appliquer le même principe ; un agrégat ne doit pas contourner une obligation de suppression.

Les événements doivent conserver l'identifiant, la séquence et les timestamps nécessaires à la réconciliation, selon la rétention décidée. La suppression des détails ne doit pas réécrire l'historique d'un job ni transformer un résultat connu en succès inconnu. Les décisions de rétention détaillée restent ouvertes.

## 9. Validation attendue avant implémentation

Avant de considérer ces statistiques comme implémentées, il faudra au minimum :

- un jeu de données reproductible avec plusieurs profils par machine, différentes fréquences, foisonnement de copies, hooks, tentatives répétées et volume d'événements ;
- des tests de jobs sans nouveau snapshot, de snapshot partagé par plusieurs jobs et d'IDs primaire/réplique distincts ;
- des tests de maintenance planifiée, occurrence manquée, livraison hors ligne, événements tardifs, événements dupliqués et réconciliation ;
- des tests de valeurs nulles/indisponibles, unités de volume, source des mesures et absence d'inventaire de fichiers ;
- une vérification des filtres par machine/profil/destination, des fuseaux horaires et bornes de fenêtre ;
- des tests de rétention des événements/journaux/audits et de non-divulgation des secrets ;
- un test de charge représentant une année pour 300 machines, avec conclusions mesurées sur API, production de rapports, espace en base de données et purge ;
- une revue de cohérence avec [les spécifications révisées](09-specifications-revisees.md), [les décisions](07-decisions.md) et [les décisions de développement](16-decisions-for-development.md).

Tant que ces validations et les décisions ouvertes ne sont pas closes, les métriques restent une conception à implémenter et le dépôt demeure **NON PRÊT POUR LA PRODUCTION**.
