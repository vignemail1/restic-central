# restic-central

> STATUT : IDÉE DE PROJET / CONCEPTION — NON PRÊT POUR LA PRODUCTION.
> Ce dépôt documente un projet envisagé. Il ne fournit actuellement ni agent, ni serveur, ni interface opérationnelle. Aucun mécanisme de sécurité, de sauvegarde ou de restauration décrit ici n'est implémenté ou validé. Ne pas utiliser ce projet pour protéger des données réelles.

## Objectif

Concevoir un service central de pilotage et de supervision de sauvegardes exécutées par Restic sur plusieurs machines. Un agent local applique une configuration, exécute Restic et transmet les événements et résultats à une API REST. Le serveur planifie les jobs, suit leur état, détecte les anomalies, notifie les opérateurs et produit des rapports.

Restic reste le moteur de sauvegarde : restic-central n'a pas vocation à réimplémenter son format de dépôt, son chiffrement ou sa déduplication. Le serveur de coordination n'est pas, par défaut, un serveur de stockage des sauvegardes.

## Fonctionnalités envisagées

- Sources et exclusions configurables ; plusieurs destinations avec résultat individuel.
- Planification centralisée, exécution locale et verrou empêchant deux sauvegardes simultanées sur un agent.
- Remontée REST des démarrages, progressions, réussites, résultats incomplets et erreurs.
- Détection des échéances manquées, dépassements de durée et agents injoignables.
- Notifications email, Matrix et Slack ; synthèse des incidents sur 24 heures par défaut.
- Rapports sur 7 jours par défaut : durée, volumétrie, destinations et fraîcheur des sauvegardes.
- Configurations versionnées, références de secrets, événements persistants et journal d'audit.

Toutes ces fonctionnalités sont des objectifs, pas des capacités disponibles.

## Documentation

1. [Vision et exigences](docs/01-vision-exigences.md)
2. [Architecture et modèle de données](docs/02-architecture-modele.md)
3. [Configuration et exécution](docs/03-configuration-execution.md)
4. [Contrat REST et fiabilité](docs/04-api-fiabilite.md)
5. [Sécurité et exploitation](docs/05-securite-exploitation.md)
6. [Notifications et rapports](docs/06-notifications-rapports.md)
7. [Registre des décisions](docs/07-decisions.md)
8. [Roadmap et stratégie de validation](docs/08-roadmap-validation.md)

## Statut des décisions

Les exigences exprimées sont identifiées comme telles. Les orientations techniques recommandées restent PROPOSÉES tant qu'elles ne sont pas explicitement acceptées. La publication de ce document ne vaut pas approbation technique de ces orientations. Les contrats API et exemples YAML sont indicatifs et non exécutables.

## Contribution

À ce stade, contribuer signifie discuter les exigences, documenter les arbitrages, les risques et les critères de validation. Il n'existe pas encore de procédure d'installation, de release ni de garantie de compatibilité. Aucun choix de licence n'est acté par cette documentation.
