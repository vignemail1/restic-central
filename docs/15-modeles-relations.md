# Modèles, relations et échanges — contrat v1

> **Statut : conception documentaire, non production-ready.** Ce document corrige et précise le modèle de `15-modeles-relations.md` pour les décisions consolidées du 2026-10-21. Il ne prétend pas que l’agent, le serveur, l’API, les migrations ou les tests sont implémentés. Les propositions métier non validées restent explicitement signalées.

Références normatives : [17-cadrage-llm-ready.md](17-cadrage-llm-ready.md), [18-audit-decisions-2026-10-21.md](18-audit-decisions-2026-10-21.md), [09-specifications-revisees.md](09-specifications-revisees.md), [04-api-fiabilite.md](04-api-fiabilite.md), [16-decisions-for-development.md](16-decisions-for-development.md). Le contrat machine-validable est [20-exchanges-v1.schema.json](20-exchanges-v1.schema.json), avec [20-exchanges-v1.example.json](20-exchanges-v1.example.json).

## 1. Règles du contrat JSON

- Draft JSON Schema **2020-12**, `schema_version: 1` entier, enveloppe versionnée et `message_type` explicite.
- Les UUID sont opaques et doivent rester stables dans les relations ; les dates sont RFC 3339 `date-time`.
- `payload` est typé par `message_type` ; les extensions explicites sont permises seulement aux emplacements prévus.
- Les secrets, tokens et références de secrets ne doivent jamais être exposés dans les événements, journaux ou résultats.

## 2. Échanges couverts

Le contrat couvre négociation de version, enrollment, heartbeat, configuration, claim/accept/cancel, lease, événements, résultats, réconciliation, erreurs, pagination, notifications, upload/ack et demandes opérateur. Les types normatifs et leurs payloads sont inventoriés dans [20-contrats-json-echanges.md](20-contrats-json-echanges.md).

## 3. Graphe relationnel corrigé

- **Machine** possède des agents et est la frontière d’appartenance des repositories.
- **Agent** représente une instance locale remplaçable ; `agent_instance_id` distingue les remplacements et n’autorise pas deux writers actifs sans décision explicite.
- **Repository** appartient à une seule machine ; le repository primaire et les destinations de copie sont référencés par identifiants, jamais par des secrets dans le contrat.
- **Profile** versionne sources, exclusions, hooks, rétention et repositories ciblés.
- **Job** est l’intention planifiée ou opérateur ; **Attempt** est une exécution concrète avec lease, événements ordonnés et résultat terminal.
- **Snapshot** est une observation/provenance Restic ; sa réconciliation ne fabrique pas une preuve d’exécution.
- **Outbox** porte les messages durables, l’idempotence et l’ack ; une perte ou saturation doit être observable.

## 4. Sémantique d’exécution et de reprise

Un seul backup actif par machine est la règle MVP. Un job accepté possède un `attempt_id`, une lease renouvelable et une clé d’idempotence. Une expiration de lease ou une interruption ne doit pas être présentée comme un succès : l’état `unknown` est conservé jusqu’à réconciliation. Les états `partial`, `failed`, `unknown`, `degraded` et `persistence_failed` restent distincts.

Les événements sont append-only côté agent et dédupliqués côté serveur par identifiant/idempotence. La reprise compare état autoritatif, événements attendus et résultats en attente ; elle ne ré-exécute pas aveuglément un backup dont l’issue est inconnue.

## 5. Réconciliation et maintenance sûre

La réconciliation couvre agents remplacés, outbox persistante, jobs actifs, résultats en attente et snapshots observés. Les actions de maintenance (forget, prune, check, stats, copies) restent des jobs explicites, auditables et soumis aux mêmes garde-fous de repository et de concurrence. Les notifications distinguent incident ouvert, récupération et rapports ; elles ne remplacent pas la preuve détaillée.

## 6. Constats et corrections de l’ancien modèle 15

- Le modèle historique mélangeait intention de job, tentative, événements et snapshots ; ils sont séparés ici.
- Le repository n’est pas globalement partagé : l’isolation par machine reste une invariant.
- Une copie n’est pas un backup primaire et une tentative de copie n’est pas le même objet qu’un job parent.
- `failed`, `partial` et `unknown` ne sont pas interchangeables ; une sortie process seule ne suffit pas à conclure.
- Les hooks sont ordonnés, bornés et sans exfiltration de secrets ; leur politique métier finale reste à décider.
- Le schéma et le document de contrat ne revendiquent aucune implémentation livrée.

## 7. Limites et propositions ouvertes

Ce contrat n’invente pas les détails non validés : chemins REST stables, pagination exacte côté serveur, code HTTP, stratégie catch-up/jitter, procédure de révocation hors ligne, mapping LDAP/rôles, politique required/optional multi-copy, agrégation de plusieurs hooks, format final d’export, chiffrement/retention des exports, et commandes exactes de maintenance. Ils doivent obtenir une décision puis être ajoutés au schéma et testés.

MVP visé : programmes Go 1.27.x, Linux amd64, Restic >= 0.19.0 ; aucune promesse d’implémentation ou de production-readiness n’est faite par ces fichiers.
