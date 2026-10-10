# restic-central

> STATUT : IDÉE DE PROJET / CONCEPTION — NON PRÊT POUR LA PRODUCTION.
> Aucun agent, serveur ou interface opérationnelle n'est fourni. Les fonctionnalités décrites sont des objectifs non implémentés et non validés. Ne pas utiliser ce projet pour protéger des données réelles.

## Objectif

Concevoir un orchestrateur de sauvegardes Restic multi-machines : agents et serveur en Go, binaires statiques et multi-OS, API REST, supervision et interface web opérateur. Restic reste le moteur ; le serveur central n'est pas le stockage des sauvegardes.

## Fonctionnalités spécifiées

- Plusieurs profils par machine, avec filesets include/exclude distincts.
- Intervalles de sauvegarde ancrés sur un timestamp stable, 24 h par défaut.
- Désactivation et suspension au niveau machine ou profil.
- Pre-hooks et post-hooks configurables, notamment préparation et nettoyage de fichiers temporaires.
- Backup vers un dépôt primaire puis réplication par restic copy.
- Lancement manuel local par un opérateur, avec le même verrou et les mêmes remontées.
- API HTTPS avec token individuel ; mTLS optionnel ; vérification du certificat configurable.
- Notifications multicanaux, synthèse 24 h et rapports 7 jours configurables.
- Interface web, authentification OpenLDAP possible et rôles applicatifs.
- Export cohérent local du serveur, planifié ou déclenché par interface/CLI, pour sauvegarde par un processus externe.
- Objectif de conservation : un an de jobs pour 300 machines, à qualifier par tests.

## Documentation et ordre de lecture

La [révision des spécifications](docs/09-specifications-revisees.md) fait autorité sur les points modifiés. Les documents 01 à 08 conservent la conception initiale ; leurs dispositions contradictoires sont remplacées par cette révision, notamment cron, exclusion des hooks, backups indépendants et ciblage Linux seul.

1. [Spécifications révisées — document prioritaire](docs/09-specifications-revisees.md)
2. [Registre actualisé des décisions](docs/07-decisions.md)
3. [Vision initiale](docs/01-vision-exigences.md)
4. [Architecture initiale](docs/02-architecture-modele.md)
5. [Configuration et exécution initiales](docs/03-configuration-execution.md)
6. [API et fiabilité](docs/04-api-fiabilite.md)
7. [Sécurité et exploitation initiales](docs/05-securite-exploitation.md)
8. [Notifications et rapports](docs/06-notifications-rapports.md)
9. [Roadmap initiale](docs/08-roadmap-validation.md)

## Maturité

Les décisions acceptées sont des engagements de conception, pas des fonctionnalités livrées. Les noms de commandes, champs et endpoints restent indicatifs. Aucun résultat de tests, lint, benchmark ou audit n'est revendiqué. La licence, les versions supportées et les modalités de distribution restent à définir.
