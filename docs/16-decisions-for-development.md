# Décisions validées pour le développement

Date : 2026-10-19. Statut : décisions de conception validées par le porteur du projet ; aucune implémentation ni réussite de tests n’est implicite. Ce document complète les [spécifications révisées](09-specifications-revisees.md) et le [registre des décisions](07-decisions.md). Lorsqu’il précise une décision, mettre à jour le registre et les spécifications associées dans la même modification. Ne pas considérer les détails non résolus ci-dessous comme approuvés.

## 1. Ordre de livraison

Le développement est incrémental ; chaque étape doit avoir ses propres tests et critères d’acceptation. L’ordre convenu est :

1. **Agent autonome :** configuration fournie manuellement, hooks, exécution via system crontab ou systemd timer, et enregistrement durable des états de jobs dans l’Outbox.
2. **Enrôlement serveur :** implémenter la gestion de l’enrôlement des agents côté serveur.
3. **Enrôlement agent :** ajouter la gestion de l’enrôlement côté agent.
4. **Reporting serveur des jobs :** implémenter la réception et la persistance des informations de jobs côté serveur.
5. **Reporting agent des jobs :** ajouter l’envoi des informations de jobs par l’agent via l’Outbox.
6. **Configuration des agents côté serveur :** implémenter la gestion et la distribution de configuration côté serveur.
7. **Auto-configuration de l’agent :** récupérer et appliquer la configuration depuis l’endpoint dédié.
8. **Planification serveur :** implémenter la planification gérée par le serveur et l’affectation future des BackupJobs.

Le terme « agent autonome » à l’étape 1 signifie une exécution configurée localement sans enrôlement ni planification serveur ; il n’approuve pas de mode de planification autonome indépendant du serveur au-delà de l’utilisation spécifiée du system timer/crontab.

## 2. Sémantique des résultats de BackupJob

- Un job est **partiel** lorsque le backup primaire réussit mais que la réplication échoue.
- Si aucun pre-hook n’est configuré, le code de sortie du backup Restic détermine si l’opération de backup réussit.
- Si un pre-hook est configuré, il doit retourner le code de sortie 0 avant le démarrage de Restic. Un pre-hook échoué empêche la phase de backup.
- Si aucun post-hook n’est configuré, le job réussit lorsque Restic réussit.
- Si un post-hook est configuré, le job réussit lorsque le backup Restic réussit et que le post-hook retourne 0 ; si le post-hook échoue après un backup Restic réussi, le job est partiel. Un échec du backup primaire reste `failed`, même si un post-hook de cleanup réussit.
- Préserver les résultats individuels des hooks, du backup primaire et de la réplication ; le statut agrégé du job ne doit pas effacer les résultats par étape.

Lorsque le backup primaire échoue, le job est `failed`, y compris si un post-hook échoue simultanément ; les résultats des deux étapes sont conservés séparément. Le comportement avec plusieurs hooks ou réplicas nécessite encore une spécification explicite avant l’implémentation de l’agrégation.

## 3. BackupJobs planifiés par le serveur

- Le serveur définit le prochain BackupJob d’un agent.
- Si son créneau planifié passe avant que l’agent récupère ce job planifié, le serveur le remplace par un nouveau job planifié pour le nouveau créneau ; l’ancien job planifié ne doit plus rester exécutable.
- Si un backup est déjà en cours au moment où un autre job planifié doit démarrer, le job en attente est marqué annulé et l’agent transmet cette annulation au serveur lorsque possible, avec un motif/état indiquant qu’un autre job est déjà en cours.

Cette règle ne définit pas le comportement des jobs demandés manuellement, des types de jobs autres que le backup, ni d’un agent resté hors ligne pendant le remplacement ; spécifier ces cas et la réconciliation/annulation idempotente avant implémentation. L’annulation d’un job planifié ne doit pas être confondue avec l’arrêt d’un processus actif.

## 4. Rétention et maintenance hors ligne

- La rétention est une configuration client exprimée par des directives Restic ; l’opérateur choisit la policy de rétention.
- Un snapshot expiré qui n’a pas été répliqué est considéré comme n’étant plus valide et peut être supprimé selon la policy configurée.
- Les jobs `forget` et `prune` mis en cache par l’agent s’exécutent même lorsque le serveur est injoignable. Leurs résultats sont persistés dans l’Outbox et transmis lorsque la connectivité revient.

La correspondance exacte des directives Restic, l’isolation par profile/repository, le schedule de prune et les garde-fous contre les jobs mis en cache obsolètes ou remplacés doivent être spécifiés et testés avant d’activer des opérations destructives.

## 5. Configuration de l’agent et secrets

- La configuration de l’agent hors secrets est stockée dans une hiérarchie filesystem à accès restreint.
- Le stockage des secrets doit permettre une récupération sécurisée après le reboot d’une machine cliente, y compris les systèmes BIOS legacy sans TPM, systèmes UEFI, serveurs physiques et machines virtuelles.
- Initialement, le projet peut s’appuyer sur [fnox](https://fnox.jdx.dev/) pour le stockage des secrets et fournir les secrets à Restic ou aux hooks au lancement du processus.

Avant implémentation, définir l’intégration fnox prise en charge et sa version, le threat model, les exigences de fichiers/permissions, le mécanisme d’injection évitant l’exposition dans la ligne de commande et les logs, ainsi que le comportement si les secrets ne peuvent pas être déverrouillés après reboot. Cette décision ne prétend pas que fnox est intégré ou a fait l’objet d’une revue de sécurité indépendante.

## 6. Contrats JSON versionnés

- Les échanges agent/serveur utilisent des schémas de données JSON versionnés. Chaque échange doit identifier une version de schéma suffisante pour s’accorder sur la sémantique ; l’évolution compatible et le comportement face aux versions non prises en charge doivent être définis.
- La sortie JSON de Restic ne constitue pas à elle seule le contrat serveur. Les données JSON Restic pertinentes doivent être incluses dans un payload imbriqué/préservé au sein du schéma défini par le serveur afin de tolérer les changements de Restic sans faire de sa sortie brute le contrat API.
- La configuration agent suit également un schéma JSON.
- Les contrats API couvrent les différentes actions, notamment backup, check, configuration et enrôlement, ainsi que le reporting des jobs et les autres opérations prises en charge.

Définir la propriété des schémas, la négociation de version, la validation, la compatibilité avant/arrière, les champs inconnus, les limites de payload et la rétention/redaction du payload Restic brut. Publier les schémas et tests de contrat avant d’implémenter les endpoints correspondants.

## 7. PostgreSQL, export et accès opérateur

- Utiliser une version stable actuelle de PostgreSQL ; consigner la plage exacte des versions prises en charge/testées au moment du choix d’implémentation.
- L’export serveur doit être cohérent et suffisant pour restaurer l’état PostgreSQL complet du serveur à partir du dump après une perte totale de la base. Coordonner le dump avec la configuration serveur et le matériel de reprise requis par la spécification d’export existante ; tester la restauration complète.
- Initialement, l’autorisation OpenLDAP cible les utilisateurs utilisant le schéma `posixAccount` et un filtre de recherche configurable. Les comptes locaux doivent aussi être pris en charge, notamment un compte superadmin local.
- Auditer chaque action opérateur, y compris login, logout, modification, création et enrôlement d’agent. Définir une persistance et une rétention d’audit suffisamment résistantes à l’altération ; ne jamais consigner credentials ou valeurs de secrets.

Cela ne choisit ni une version majeure de PostgreSQL, ni la syntaxe/valeur par défaut du filtre LDAP, ni le mécanisme de récupération de compte local, la policy de mot de passe, la granularité des rôles ou les outils d’export. Ces détails exigent spécification et tests.

## 8. Tests et critères de passage

Chaque étape de livraison ci-dessus possède des tests unitaires, d’intégration et de chemins d’échec adaptés à son périmètre. En particulier, tester la durabilité de l’Outbox après redémarrage et panne serveur ; le contrôle des codes de sortie des hooks ; le statut partiel en cas de réplication/post-hook échoué ; le remplacement des jobs planifiés et le reporting de leur annulation ; la livraison des résultats `forget`/`prune` hors ligne ; la validation des versions de schéma ; la restauration PostgreSQL complète ; l’authentification LDAP/locale ; et la couverture d’audit sans fuite de secrets.

Une étape de développement n’est pas terminée simplement parce que la fonctionnalité compile. Ne pas activer la rétention destructive dans des environnements proches de la production avant la réussite des tests d’isolation, de gestion des jobs obsolètes et de reprise/restauration.

