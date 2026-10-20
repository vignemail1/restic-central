# Registre des décisions

Révision : 2026-10-19, après validation par le porteur du projet. Phase de conception, non prêt pour la production.

REQUIREMENT : demandé par le porteur. ACCEPTED : explicitement validé. PROPOSED : non validé. SUPERSEDED : orientation initiale incompatible, remplacée. OPEN : décision en attente. PARTIALLY ACCEPTED : seul le périmètre explicitement indiqué est validé.

Les [spécifications révisées](09-specifications-revisees.md) constituent la référence détaillée normative pour les sujets qu’elles couvrent. Ce registre consigne le statut et l’historique des décisions ; il ne constitue pas une spécification concurrente. Si un statut contredit une règle détaillée, interrompre l’implémentation et résoudre l’écart ; ne pas déduire une validation de la seule publication.

## Exigences

E01 à E08 restent applicables : Restic, API REST agent/serveur, planification serveur, destinations et filesets, lock local, signalement des jobs nécessitant une inspection, notifications sur 24 heures, rapports sur 7 jours et avertissement de non-production.

Nouvelles exigences : plusieurs profiles par machine ; suspension et désactivation de la machine ou du profile ; pre-hooks/post-hooks ; vérification TLS configurable ; binaires Go statiques multi-OS ; exécution manuelle locale ; interface web avec OpenLDAP et rôles ; export local cohérent du serveur ; rétention des snapshots configurée côté client ; backup primaire suivi de copy.

## Orientations P

| ID | Statut | Décision |
|---|---|---|
| P01 | ACCEPTED, AMENDED | Le serveur contrôle la planification automatique des agents enrôlés ; l’exécution manuelle locale est autorisée. L’ordre de livraison validé commence par un agent configuré localement via system crontab/systemd timer, puis ajoute enrôlement, reporting, configuration et planification serveur. Cela n’approuve pas une planification autonome indépendante pour les agents enrôlés. |
| P02 | ACCEPTED | Polling HTTPS sortant ; aucun port réseau entrant obligatoire sur l’agent. |
| P03 | ACCEPTED | Configurations immuables et versionnées, attachées aux jobs. |
| P04 | ACCEPTED, LIMITED | La configuration de l’agent hors secrets est stockée dans une hiérarchie filesystem à accès restreint. fnox peut initialement être utilisé pour les secrets, fournis à Restic/hooks au lancement. La récupération sécurisée après reboot est requise sur le matériel visé ; l’intégration, le threat model et l’injection restent à spécifier. |
| P05 | ACCEPTED | Outbox persistante, livraison at-least-once et déduplication. |
| P06 | ACCEPTED | Jobs, tentatives et résultats par destination distincts. |
| P07 | SUPERSEDED, REPLACED | Les backups indépendants sont remplacés par un backup primaire suivi de copy. Sémantique de résultat acceptée : un backup primaire réussi avec réplication échouée est partiel. |
| P08 | ACCEPTED, PARTIAL | Un backup primaire réussi avec réplication échouée est partiel ; un post-hook échoué après un backup Restic réussi l’est également. Préserver les résultats par étape. L’agrégation des échecs combinés et des hooks/réplicas multiples reste ouverte. |
| P09 | ACCEPTED | Timeout : alerte et inspection, sans arrêt forcé par défaut. |
| P10 | PROPOSED | Aucun unlock automatique sur la seule base d’un timeout. |
| P11 | ACCEPTED, EXTENDED | Agent/serveur en Go, statiques et multi-OS ; les anciennes restrictions Linux-only sont remplacées. La matrice des cibles prises en charge reste à définir et tester. |
| P12 | PARTIALLY SUPERSEDED | Les hooks sont maintenant dans le périmètre. HA et restauration distante restent hors du MVP proposé. |
| P13 | ACCEPTED | Incidents immédiats, récapitulatif quotidien et notification de rétablissement. |
| P14 | PROPOSED | Rapports par occurrence planifiée, retries distincts et métriques manquantes identifiées ; aucune validation explicite du porteur n’a été trouvée. |

## Décisions O

| ID | Statut | Décision ou question restante |
|---|---|---|
| O01 | ACCEPTED, PARTIAL | PostgreSQL est la base du serveur ; utiliser une version stable actuelle et fournir un export cohérent et complet permettant une restauration après perte totale de la base. Version et outils exacts à définir. Persistance locale de l’agent encore ouverte. |
| O02 | ACCEPTED | HTTPS/TLS avec token individuel ; mTLS facultatif. |
| O03 | OPEN | Version minimale de Restic et matrice de compatibilité. |
| O04 | ACCEPTED TARGET | Un an de jobs pour 300 machines ; dimensionner profiles, tentatives, événements et charge. RPO/RTO du serveur encore ouverts. |
| O05 | ACCEPTED SCHEDULING, PARTIAL | Le serveur définit le prochain BackupJob. Si le créneau passe sans récupération par l’agent, remplacer le job prévisionnel. Si un autre backup est en cours à l’heure prévue, annuler le job en attente et signaler l’annulation si possible avec le motif/état indiquant qu’un job est déjà en cours. Réconciliation hors ligne et autres types de jobs encore ouverts. Les règles antérieures de rattrapage et d’ancrage restent applicables uniquement lorsqu’elles ne sont pas contradictoires. |
| O06 | ACCEPTED, PARTIAL | Réussite primaire et réplication échouée = partiel. Règles des hooks : le pre-hook requis doit retourner 0 avant Restic ; sans pre-hook, le code de sortie Restic décide de la réussite du backup ; sans post-hook, la réussite de Restic signifie réussite du job ; post-hook échoué après Restic réussi = partiel. Préserver les résultats par étape. Échecs combinés, hooks/réplicas multiples et destinations facultatives restent ouverts. |
| O07 | ACCEPTED | Cohérence applicative hors périmètre ; des hooks peuvent préparer des fichiers cohérents sans garantie applicative du produit. |
| O08 | ACCEPTED, PARTIAL | Rétention configurée via les directives Restic côté client, l’opérateur choisit la policy. Un snapshot expiré non répliqué peut être supprimé. Les jobs `forget`/`prune` mis en cache s’exécutent hors ligne et persistent leurs résultats dans l’Outbox. Correspondance des directives, isolation, schedule et garde-fous contre les jobs obsolètes à préciser avant toute opération destructive. |
| O09 | ACCEPTED, PARTIAL | Interface opérateur, utilisateurs OpenLDAP `posixAccount` avec filtre de recherche configurable, comptes locaux dont un superadmin, audit de chaque action opérateur (login/logout, modifications, créations, enrôlement d’agent inclus). Rôles, récupération, détails LDAP, protection/rétention de l’audit restent à préciser. Export cohérent également accepté sous O01. |
| O10 | OPEN | Licence, distribution et mises à jour ; exigence de Go statique multi-OS acceptée. |
| O11 | ACCEPTED, EXTENDED | Backup primaire suivi de copy ; le serveur reste l’autorité de planification des agents enrôlés. La première étape de développement peut exécuter un agent configuré localement via timer OS/crontab avant enrôlement. |
| O12 | ACCEPTED, PARTIAL | Les échanges agent/serveur et la configuration agent utilisent des schémas JSON versionnés ; le JSON Restic est imbriqué/préservé dans les contrats définis par le serveur, sans constituer le contrat API lui-même. Négociation de schéma, compatibilité et validation à définir. |

## Autres décisions validées

- L’ordre de livraison et les critères d’étape sont consignés dans les [décisions validées pour le développement](16-decisions-for-development.md) et la [feuille de route](08-roadmap-validation.md).
- Un BackupJob planifié non récupéré avant expiration de son créneau est remplacé ; un job arrivé à échéance est annulé plutôt que lancé en parallèle d’un backup déjà en cours, et l’annulation est remontée si possible.
- L’authentification opérateur prend initialement en charge la recherche OpenLDAP `posixAccount` et les comptes locaux dont un superadmin ; toutes les actions opérateur sont auditées.
- Aucune implémentation, réussite de tests, revue de sécurité ou aptitude à la production ne découle de l’acceptation des décisions de conception.

## Historique et conséquences

P02, P03, P05, P06, P09, P11 et P13 ont été explicitement validées précédemment. Le porteur a ensuite validé les changements de périmètre consignés ci-dessus ; les propositions adjacentes restent non acceptées sauf indication explicite.

Les hooks augmentent les privilèges et l’exposition à l’exécution : fournir des commandes structurées, restrictions locales, limites de durée et audit. TLS sans vérification est possible, mais doit être clairement signalé comme dégradé. L’exécution locale nécessite le même moteur de lock et une réconciliation serveur idempotente.

Une panne du serveur empêche les nouvelles exécutions déclenchées centralement, mais ne doit pas empêcher une exécution manuelle locale avec une configuration disponible. Un échec de copy ne doit pas provoquer inutilement une nouvelle lecture des sources.

Toute décision future doit inclure contexte, alternatives, porteur, date et conséquences ; conserver les décisions remplacées.
