# Modèles, relations et échanges — contrat v1

> **Statut : conception documentaire, non production-ready.** Ce document corrige et précise le modèle de `15-modeles-relations.md` pour les décisions consolidées du 2026-10-21. Il ne prétend pas que l’agent, le serveur, l’API, les migrations ou les tests sont implémentés. Les propositions métier non validées restent explicitement signalées.

Références normatives : [17-cadrage-llm-ready.md](17-cadrage-llm-ready.md), [18-audit-decisions-2026-10-21.md](18-audit-decisions-2026-10-21.md), [09-specifications-revisees.md](09-specifications-revisees.md), [04-api-fiabilite.md](04-api-fiabilite.md), [16-decisions-for-development.md](16-decisions-for-development.md). Le contrat machine-validable est [20-exchanges-v1.schema.json](20-exchanges-v1.schema.json), avec [20-exchanges-v1.example.json](20-exchanges-v1.example.json).

## 1. Règles du contrat JSON

- Draft JSON Schema **2020-12**, `schema_version: 1` entier, enveloppe versionnée et `message_type` explicite.
- Chaque pair annonce ses versions ; la version retenue est l’intersection **maximale commune**. Aucune intersection ou version non supportée produit une erreur explicite, sans downgrade silencieux.
- Les champs inconnus reçus sont conservés dans `extensions` (JSON borné) et ne sont jamais interprétés comme configuration, commande ou autorisation. Les implémentations peuvent refuser une enveloppe inconnue ; elles ne doivent pas l’exécuter.
- Les secrets ne sont jamais des DTO publics : seuls `secret_ref` (`env`, commande autorisée par clé, OS secret manager ou fnox) et références non sensibles circulent. Aucun mot de passe, token ou valeur de credential dans les logs, arguments ou résultats.
- `event_id`, `message_id` et clés d’idempotence sont opaques et stables. Un doublon est acquitté sans ré-exécution et les transitions de statut sont monotones.

## 2. Échanges couverts

Le contrat v1 couvre notamment la négociation de version, l’enrôlement agent, le heartbeat, la lecture de configuration, la réservation/acceptation/annulation de jobs, le renouvellement d’une tentative, les batches d’événements, les résultats de tentative, la réconciliation de snapshots, les erreurs, la pagination, les notifications, l’upload/acquittement de résultat et les demandes opérateur. La liste exhaustive et les `$defs` normatifs sont dans [20-exchanges-v1.schema.json](20-exchanges-v1.schema.json) ; l’inventaire lisible est [20-contrats-json-echanges.md](20-contrats-json-echanges.md).

Chaque message porte une enveloppe commune (`schema_version`, `message_type`, `message_id`, `sent_at`, `payload`) et peut porter `correlation_id`, `agent_id` et `extensions`. Les identifiants sont des UUID dans le contrat actuel, opaques pour la sémantique métier.

## 3. Graphe relationnel corrigé

- **Repository** représente une cible logique ; ses références d’accès et paramètres sensibles restent hors DTO public.
- **Job** décrit l’intention planifiée et référence un repository, une politique et des hooks bornés.
- **JobAttempt** représente une exécution concrète, avec lease, idempotency key, timestamps, statut terminal ou reprise.
- **StepResult** détaille les étapes sans transformer une sortie d’outil en commande.
- **Event** est append-only et corrélé à une tentative ; sa livraison est idempotente.
- **Snapshot** est une observation/référence de backup, pas une preuve implicite de restauration.
- **NotificationDelivery** et **ResultUpload** suivent leur propre état et accusé de réception.
- Les relations serveur sont des références stables (`repository_id`, `server_job_id`, `attempt_id`, `event_id`) ; elles ne confondent pas identifiant serveur, UUID local et clé d’idempotence.

## 4. Sémantique d’exécution et de reprise

La réservation est suivie d’un `job.accept` explicite ou d’une expiration de lease. Une tentative peut être renouvelée ; l’agent doit arrêter proprement une lease expirée et le serveur doit tolérer les messages retardés sans ré-exécution. `attempt.result` est idempotent par `idempotency_key`, accepte un résultat partiel, et ne rend pas un job réussi si une étape obligatoire a échoué.

Les opérations sont bornées par timeout, retry policy et limites de taille. Les erreurs portent un `code`, un message non sensible et `retryable`; les détails d’implémentation et secrets restent exclus. Les hooks sont des références autorisées, jamais des shell strings arbitraires.

## 5. Réconciliation et maintenance sûre

La réconciliation compare des observations bornées et versionnées ; elle ne supprime ni ne réécrit silencieusement une donnée divergente. Les suppressions/rotations demandent une politique explicite, une idempotency key et une trace d’audit. Les versions de schéma sont négociées ; une version inconnue est rejetée avec erreur structurée.

Les champs libres sont placés dans `extensions`, validés par taille/profondeur et préservés sans exécution. Les DTO publics ne contiennent pas de credential. Les logs, notifications et rapports redigent les secrets par défaut.

## 6. Constats et corrections de l’ancien modèle 15

1. Séparer les identifiants serveur, UUID locaux, événements et clés d’idempotence.
2. Modéliser explicitement `JobAttempt`, `StepResult`, lease et résultat partiel.
3. Remplacer les payloads polymorphes implicites par `message_type` et `$defs` versionnés.
4. Ne pas confondre snapshot observé, résultat de backup et restauration vérifiée.
5. Transporter les secrets par références autorisées uniquement.
6. Rendre les doublons, reprises, retards et erreurs retryable explicites.
7. Considérer la réconciliation comme une opération contrôlée et auditable, non comme une réparation destructive automatique.

## 7. Limites et propositions ouvertes

Ce document et le schéma définissent un contrat documentaire v1 ; ils ne constituent pas une preuve d’implémentation. Restent à décider et tester : la politique exacte de rétention, la taxonomie complète des hooks autorisés, les quotas de transport, le stockage des payloads volumineux, les garanties de transaction et les scénarios de reprise après partition. Toute extension doit préserver la compatibilité négociée, l’idempotence et l’absence de secrets dans les DTO/logs.
