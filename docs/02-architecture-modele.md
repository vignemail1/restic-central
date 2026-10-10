# Architecture et modèle de données

Statut : architecture proposée, non implémentée.

## Composants

```text
Administrateur -> interface/API du serveur
Serveur -> configurations, scheduler, jobs, événements, incidents, rapports
Agent -> HTTPS sortant vers le serveur : acquisition et remontées
Agent -> processus Restic -> dépôts de sauvegarde
Serveur -> providers email / Matrix / Slack
```

Le serveur conserve les métadonnées de coordination. Les données sauvegardées circulent entre l'agent et les dépôts ; elles ne transitent pas par le serveur de coordination par défaut.

## Responsabilités

Serveur : gérer les identités, configurations immuables, échéances, réservations de jobs, états observés, incidents et livraisons de notifications.

Agent : valider la configuration, résoudre les secrets locaux, contrôler les préconditions, acquérir un verrou, lancer Restic sans shell implicite, collecter les sorties, persister les événements et réconcilier l'état après redémarrage.

## Planification

Orientation MVP : le serveur est l'unique autorité de déclenchement. L'agent conserve la configuration mais ne recrée pas indépendamment les échéances. En panne serveur, un job déjà accepté peut continuer ; aucun nouveau job central n'est acquis.

Le mode autonome éventuel sera explicite et fera l'objet d'un arbitrage ultérieur. Ne jamais superposer deux schedulers sans protocole de déduplication.

Chaque planification doit définir fuseau IANA, comportement aux changements d'heure, fenêtre autorisée, jitter, délai de démarrage, politique de rattrapage et périodes de maintenance. Recommandation initiale : rattraper au plus une occurrence devenue pertinente, sans rejouer toute une accumulation.

## Entités

| Entité | Informations principales |
|---|---|
| Agent | identité stable, capacités, version, dernier contact, statut d'enrôlement |
| Repository | backend, emplacement, options, références de secrets |
| BackupPolicy | sources, exclusions, destinations, planification, règles de succès |
| ConfigRevision | contenu immuable, version de schéma, empreinte |
| Job | politique, révision, échéance, demandeur, état agrégé |
| Attempt | job, numéro, agent, dates, état, réservation |
| DestinationResult | dépôt, opération, code Restic, snapshot, métriques |
| Event | identifiant, tentative, séquence, type, dates, payload |
| Incident | clé de regroupement, ouverture, acquittement, résolution |
| NotificationDelivery | canal, destinataire, résultat, retry |

Un Job référence la révision réellement exécutée. Une modification de politique ne réécrit pas l'historique. Une tentative en échec et son retry restent distincts.

## États d'exécution

```text
scheduled -> queued -> claimed -> running
                                   -> succeeded
                                   -> partial
                                   -> failed
                                   -> timed_out
                                   -> canceled
```

`skipped` désigne une occurrence volontairement ignorée, avec motif. Les transitions autorisées et leurs préconditions devront être validées par tests. Un événement tardif ne doit pas faire régresser silencieusement un état terminal.

## Observation séparée

`healthy`, `unreachable`, `suspected_stuck` et `reconciliation_required` décrivent la connaissance du serveur, pas nécessairement le résultat du processus. Un agent injoignable peut avoir terminé sa sauvegarde. Afficher le dernier état connu et son horodatage.

## Persistance

Le choix du moteur de stockage serveur reste ouvert. Exiger transactions, contraintes d'unicité, migrations, sauvegarde et restauration testées. L'agent nécessite un stockage local persistant pour l'outbox et les tentatives. SQLite est une option à évaluer, pas un choix acté.
