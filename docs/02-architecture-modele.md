# Architecture et modèle de données

Statut : architecture proposée, non implémentée.

## Composants

```text
Administrateur -> interface/API du serveur
Serveur -> configurations, scheduler, jobs, événements, incidents, rapports
Agent -> HTTPS sortant vers le serveur : acquisition et reporting
Agent -> processus Restic -> repositories de sauvegarde
Serveur -> providers email / Matrix / Slack
```

Le serveur stocke les métadonnées de coordination. Les données de sauvegarde circulent entre l’agent et les repositories ; par défaut, elles ne transitent pas par le serveur de coordination.

## Responsabilités

Serveur : gérer les identités, configurations immuables, occurrences planifiées, réservations de jobs, états observés, incidents et livraisons de notifications.

Agent : valider la configuration, résoudre les secrets locaux, vérifier les prérequis, acquérir un lock, exécuter Restic sans shell implicite, collecter la sortie, persister les événements et réconcilier l’état après un redémarrage.

## Planification

Orientation MVP : le serveur est l’unique autorité de déclenchement des exécutions. L’agent conserve sa configuration, mais ne recrée pas indépendamment les occurrences planifiées. Pendant une panne du serveur, un job déjà accepté peut continuer ; aucun nouveau job central n’est acquis.

Tout futur mode autonome devra être explicite et faire l’objet d’une décision ultérieure. Ne jamais superposer deux schedulers sans protocole de déduplication.

Chaque schedule doit définir un fuseau horaire IANA, le comportement lors du changement d’heure, une fenêtre d’exécution autorisée, un jitter, une deadline de démarrage, une policy de rattrapage et les périodes de maintenance. Recommandation initiale : ne rattraper au plus qu’une occurrence pertinente, au lieu de rejouer tout l’historique en attente.

## Entités

| Entité | Informations principales |
|---|---|
| Agent | identité stable, capacités, version, dernier contact, statut d’enrôlement |
| Repository | backend, emplacement, options, références de secrets |
| BackupPolicy | sources, exclusions, destinations, schedule, règles de réussite |
| ConfigRevision | contenu immuable, version de schéma, empreinte |
| Job | policy, révision, heure planifiée, demandeur, état agrégé |
| Attempt | job, numéro de tentative, agent, timestamps, état, réservation |
| DestinationResult | repository, opération, code de sortie Restic, snapshot, métriques |
| Event | identifiant, tentative, séquence, type, timestamps, payload |
| Incident | clé de regroupement, ouverture, acquittement, résolution |
| NotificationDelivery | canal, destinataire, résultat, retry |

Un Job référence la révision réellement exécutée. Les changements de policy ne réécrivent pas l’historique. Une tentative échouée et son retry restent distincts.

## États d’exécution

```text
scheduled -> queued -> claimed -> running
                                   -> succeeded
                                   -> partial
                                   -> failed
                                   -> timed_out
                                   -> canceled
```

`skipped` désigne une occurrence volontairement ignorée, avec un motif. Les transitions autorisées et leurs prérequis doivent être validés par des tests. Un événement tardif ne doit pas faire régresser silencieusement un état terminal.

## État d’observation distinct

`healthy`, `unreachable`, `suspected_stuck` et `reconciliation_required` décrivent ce que sait le serveur, pas nécessairement le résultat du processus. Un agent injoignable peut avoir terminé sa sauvegarde. Afficher le dernier état connu et son timestamp.

## Persistance

Le moteur de stockage du serveur reste à déterminer dans cette conception initiale. Exiger des transactions, des contraintes d’unicité, des migrations et des procédures de backup et de restore testées. L’agent a besoin d’un stockage local persistant pour son outbox et ses tentatives. SQLite est une option à évaluer, pas un choix accepté.
