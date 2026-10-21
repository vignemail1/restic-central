# Modèles, relations et échanges — contrat v1

> **Statut : conception documentaire, non production-ready.** Ce document corrige et précise le modèle de `15-modeles-relations.md` pour les décisions consolidées du 2026-10-21. Il ne prétend pas que l’agent, le serveur, l’API, les migrations ou les tests sont implémentés. Les propositions métier non validées restent explicitement signalées.

Références normatives : [17-cadrage-llm-ready.md](17-cadrage-llm-ready.md), [18-audit-decisions-2026-10-21.md](18-audit-decisions-2026-10-21.md), [09-specifications-revisees.md](09-specifications-revisees.md), [04-api-fiabilite.md](04-api-fiabilite.md), [16-decisions-for-development.md](16-decisions-for-development.md). Le contrat machine-validable est [20-exchanges-v1.schema.json](20-exchanges-v1.schema.json), avec [20-exchanges-v1.example.json](20-exchanges-v1.example.json).

## 1. Règles du contrat JSON

- Draft JSON Schema **2020-12**, `schema_version: 1` entier, enveloppe versionnée et `message_type` explicite.
- Chaque pair annonce ses versions ; la version retenue est l’intersection **maximale commune**. Aucune intersection ou version non supportée produit une erreur explicite, sans downgrade silencieux.
- Les champs inconnus reçus sont conservés dans `extensions` (JSON borné) et ne sont jamais interprétés comme configuration, commande ou autorisation. Les implémentations peuvent refuser une enveloppe inconnue ; elles ne doivent pas l’exécuter.
- Les secrets ne sont jamais des DTO publics : seuls `secret_ref` (`env`, commande autorisée par clé, OS secret manager ou fnox) et références non sensibles circulent. Aucun mot de passe, token ou valeur de credential dans les logs, arguments ou résultats.
- `event_id`, `message_id` et clés d’idempotence sont opaques et stables. Un doublon identique est ACKé après déduplication transactionnelle ; un même identifiant avec contenu différent est rejeté.
- Les dates sont RFC 3339 avec timezone, transmises en UTC. Le serveur conserve temps nominal, début, fin, réception et, lorsque pertinent, mesure monotone de durée.
- `unknown` est une observation indéterminée, jamais une réussite. Une expiration de lease ne prouve pas l’arrêt du processus Restic.

## 2. Échanges couverts

Le schéma v1 décrit les DTO de : négociation de version, enrollment contrôlé (token 12 h à usage limité puis credential permanent rotatif), heartbeat/capacités, récupération de configuration, claim et acceptation de jobs, expiration/annulation, renouvellement de lease, événements idempotents, résultat terminal et résultats par étape, réconciliation, inventaire snapshots, erreurs structurées, pagination et notifications/rapports.

Les opérations de job supportées dans le DTO sont `backup`, `copy`, `forget`, `prune`, `check`, `stats`. Les origines sont `server_schedule`, `operator`, `local_manual` et `cached_maintenance`. Un résultat autonome/local est transmis par `result.upload` et acquitté par `result.ack` après persistance/déduplication serveur. Un job autonome/local reçoit son `local_job_uuid` durable avant exécution ; `server_job_id` est attribué à la réception serveur. L’identité d’un job autonome n’est donc pas confondue avec l’identité serveur.

Les opérations API/opérateur prévues dans la référence 04 sont représentées par les messages suivants : `agent.enroll`, `heartbeat`, `config.get.response`, `job.claim.*`, `attempt.renew`, `event.batch`, `attempt.result`, `result.upload`, `result.ack`, et `error`; les lectures paginées sont représentées par `page.response`. Les demandes opérateur sont `operator.job.request` et `operator.job.response`. Les chemins REST restent **illustratifs et non stables** tant qu’ils ne sont pas implémentés.

## 3. Graphe relationnel corrigé

- **Machine → Agent** : 0..N enrollments historiques ; au plus un agent actif autorisé par défaut, remplacement explicite. Cette cardinalité et la coexistence temporaire de credentials actifs restent à préciser avant SQL.
- **Machine → BackupProfile / Repository** : 0..N ; chaque profil et repository a un owner machine. Le contrat interdit le cross-machine pour destinations et copies.
- **BackupProfile → ProfileDestination** : 1..N pour un profil exécutable ; un primary et des destinations de réplication. Le nombre de replicas, required/optional et l’agrégation multi-destinations restent à valider.
- **BackupProfile → ConfigRevision** : 1..N après création ; révisions immuables et références historiques conservées ; au plus une current revision.
- **Schedule → Job** : 0..N occurrences historiques. Un job manuel peut ne pas avoir de schedule. L’occurrence est stable (agent, profile, scheduling revision, timestamp nominal) ; un retry ne crée pas un nouveau job.
- **Job → Attempt** : 0..N ; une tentative a un agent exécuteur, un numéro/identifiant unique et une lease renouvelable. La réservation est transactionnelle.
- **Attempt → Operation/StepResult/Event** : 0..N, ordonnés ; chaque étape conserve début, fin, état, code éventuel et erreur. Le heartbeat est distinct des execution events.
- **Repository → SnapshotRecord / RepositoryObservation** : inventaire séparé des jobs. Clé métier proposée : `(repository_id, restic_snapshot_id)`, car l’ID Restic n’est pas global. Un snapshot observé sans association fiable reste `observed_unknown` et ne peut déclencher une suppression.
- **Incident → NotificationDelivery** : une livraison peut concerner un incident ou un summary ; ACK opérateur ≠ résolution. L’échec de notification ne modifie jamais le résultat backup.

## 4. Sémantique d’exécution et de reprise

Séquence : lock machine → préconditions → pre-hooks → `restic backup` → association snapshot → `restic copy` → post-hooks selon condition → persistance → unlock. Arguments en liste, sans shell implicite. Un pre-hook non nul empêche Restic ; Restic interrompu, timeout ou sortie non décodable donne `failed`. Primary réussi + copy échouée donne `partial`; un retry de copy réutilise le snapshot sans nouveau backup. Un retry global réussi reste `partial` pour investigation, avec les étapes précédentes conservées.

Le résultat terminal porte le statut agrégé **et** les résultats de chaque étape. Il ne faut jamais inférer la réussite d’un snapshot, d’un fichier présent ou d’un ACK perdu. La persistance échouée (`persistence_failed`) n’est pas une réussite. L’Outbox est at-least-once, avec perte éventuelle ancienne observable (`outbox_loss`) en saturation ; aucun job actif/processus/configuration/état de déduplication n’est supprimé.

Un job non accepté à `start + 12 h` expire par défaut et ne peut pas démarrer. L’annulation distingue requête, réception agent et terminaison confirmée. Une machine lockée ne doit pas provoquer une redistribution aveugle : l’expiration nécessite réconciliation et ne clôt pas la preuve du processus.

## 5. Réconciliation et maintenance sûre

À la reconnexion, l’agent envoie active attempts et résultats persistés ; le serveur répond avec son état d’autorité, événements attendus et divergences. Un late result peut résoudre une observation `unknown` selon des règles explicites sans effacer l’incident historique. L’inventaire `snapshot.reconcile` ne fabrique jamais de jobs manquants.

`forget`, `prune`, `check`, `stats` restent scopés par machine/profile/repository. Toute opération destructive est réévaluée juste avant exécution, requiert un mapping fiable et un owner compatible ; sinon `blocked_unknown_scope`. `keep-last` minimum 1. Les règles exactes de rétention, copies optionnelles, hooks multiples, dépendances et catch-up restent à spécifier avant implémentation (propositions, pas décisions).

## 6. Constats et corrections de l’ancien modèle 15

1. Le statut « proposed conceptual model » était correct mais ne séparait pas assez le contrat d’échange des tables : ce document renvoie maintenant explicitement au schéma v1, sans présenter une migration SQL comme décidée.
2. Les identités `local_job_uuid` et `server_job_id`, l’idempotence Outbox et la déduplication sont désormais explicites.
3. Le modèle distinguait déjà expiration et arrêt ; la documentation précise maintenant qu’une lease expirée n’autorise ni retry ni redistribution sans réconciliation.
4. Les résultats primary/copy/hooks sont séparés ; `partial` est fixé pour primary réussi + copy échouée et le retry de copy ne relance pas backup.
5. L’inventaire snapshot est séparé des jobs et porte une provenance ; un snapshot inconnu n’autorise aucune purge.
6. Les anciennes ambiguïtés restent marquées : partage intra-machine, agents actifs lors d’un remplacement, agrégation de copies/hooks, retry copy comme job distinct, dépendances, mappings LDAP, format SQL polymorphe.
7. Les anciennes références à cron et à des destinations indépendantes ne sont pas reprises comme contrat courant : l’intervalle/anchor et primary-then-copy de la spécification révisée prévalent.

## 7. Limites et propositions ouvertes

Ce contrat n’invente pas les détails non validés : chemins REST stables, pagination exacte côté serveur, code HTTP, stratégie catch-up/jitter, procédure de révocation hors ligne, mapping LDAP/rôles, politique required/optional multi-copy, agrégation de plusieurs hooks, format final d’export, chiffrement/retention des exports, et commandes exactes de maintenance. Ils doivent obtenir une décision puis être ajoutés au schéma et testés.

MVP visé : programmes Go 1.27.x, Linux amd64, Restic >= 0.19.0 ; aucune promesse d’implémentation ou de production-readiness n’est faite par ces fichiers.
