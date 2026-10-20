# Décision : PostgreSQL pour le serveur

Date : 2026-10-10. Statut : ACCEPTÉ par le porteur du projet pour le choix du moteur serveur.

> Projet en conception — NON PRÊT POUR LA PRODUCTION. Aucun schéma, driver, migration, export ou déploiement n’est actuellement implémenté ou validé.

## Décision O01

Le serveur restic-central utilise PostgreSQL comme base de données. Cette décision remplace le statut OUVERT d’O01 pour le stockage serveur dans le registre [07-decisions.md](07-decisions.md) et les documents initiaux. Le choix de persistance locale de l’agent reste OUVERT : PostgreSQL côté serveur n’impose pas un serveur PostgreSQL sur chaque client.

La recommandation SQLite formulée pendant la discussion n’a pas été acceptée pour le serveur. Ne pas prévoir deux backends serveur au MVP sans nouvelle décision explicite.

## Périmètre de persistance

Prévoir la persistance relationnelle des machines, profiles, révisions de configuration, schedules, suspensions, jobs, tentatives, résultats par destination, hooks, incidents, notifications, identités/rôles applicatifs et audit. Les métadonnées et statistiques demandées doivent être dimensionnées sans inventaire des fichiers sauvegardés.

Objectif inchangé : un an de jobs pour 300 machines, avec plusieurs profiles possibles. Cela reste une cible de validation, pas une performance mesurée. Fréquence des événements, nombre de profiles, copies et tentatives doivent entrer dans les essais de charge.

## Contraintes de conception

- Agent et serveur restent des programmes Go compilés statiques et multi-OS. PostgreSQL constitue un service de données distinct ; le binaire serveur n’est pas un déploiement autonome de la base.
- Valider un driver Go compatible avec cet objectif, un pool de connexions borné et des délais de requête. Le driver n’est pas encore choisi.
- Utiliser transactions, contraintes d’unicité et clés étrangères pour l’intégrité ; un accusé de réception d’événement doit suivre sa persistance réussie.
- Définir des migrations versionnées, une policy de compatibilité et une procédure de mise à jour.
- Séparer les privilèges d’exploitation applicative et de migration ; ne pas utiliser un compte superuser pour les requêtes courantes.
- Stocker les credentials de connexion hors du dépôt et des logs ; définir la protection TLS selon le réseau de déploiement.
- PostgreSQL ne décide pas à lui seul de la concurrence du scheduler, de la reprise des leases ni de la haute disponibilité applicative. Ces sujets demandent un protocole explicite.

## Export cohérent local du serveur

L’exigence d’export planifié ou manuel via web/CLI est conservée : configuration, DB et éléments de reprise sont exportés dans un dossier local pour backup par un processus externe hors périmètre.

La méthode d’export PostgreSQL reste à définir et tester : export logique natif ou autre méthode validée. Ne pas copier arbitrairement les fichiers d’une base active. Définir comment maintenir la cohérence entre l’état DB et la configuration externe pendant l’export. Si un utilitaire externe est requis, documenter sa présence, sa version et sa compatibilité ; ne pas promettre un export sans dépendance supplémentaire.

Publier uniquement les exports complets, avec manifeste, version de schéma et contrôles d’intégrité. Documenter les secrets externes nécessaires, les permissions et la restauration. La restauration ne doit pas relancer aveuglément des jobs historiques.

## Arbitrages restant ouverts

Version minimale de PostgreSQL et versions testées ; driver Go ; outil de migration ; dimensionnement du pool ; schéma et index ; rétention des événements détaillés ; stratégie d’export/restauration ; RPO/RTO ; déploiement de la base ; éventuelle haute disponibilité ; stockage local de l’agent.

Le partitionnement, des extensions ou un backend analytique séparé ne sont pas imposés : leur nécessité devra être établie par les requêtes et mesures réelles.

## Validation attendue

Tests de migrations, rollback opérationnel, accès concurrents, idempotence, pertes de connexion, indisponibilité DB, redémarrage, historique annuel, reporting pendant ingestion et restauration d’un export. Vérifier les builds sur chaque OS/architecture annoncée et l’absence de secrets dans les logs.

## Portée de cette publication

Cette décision n’approuve pas automatiquement les autres propositions de conception. L’amendement sur les options Restic et les statistiques demeure une publication distincte tant qu’il n’a pas été explicitement approuvé.
