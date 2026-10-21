# Cadrage LLM-ready de développement — restic-central

> Document normatif consolidé à partir du cadrage de développement et des décisions validées le 2026-10-21. Les termes techniques anglais sont conservés lorsqu'ils désignent un contrat ou un mécanisme.

## 1. Mission et invariants

Construire deux programmes Go : un agent local et un serveur central. L'agent exécute Restic ; le serveur planifie, conserve les métadonnées, reçoit les résultats et expose l'exploitation. Un repository est exclusivement possédé par une machine. Un seul backup est actif par machine.

Préférer `failed`, `partial`, `unknown` ou `degraded` à une réussite inférée. Toute opération destructive est explicite, correctement scopée, réévaluée juste avant exécution et auditée.

## 2. Ordre de livraison immuable

1. Agent autonome : configuration locale, hooks, timer/crontab, moteur Restic, lock, DB locale, Outbox.
2. Enrollment serveur : machine pré-déclarée et token unique, révocable, valable 12 h.
3. Enrollment agent : credential permanent rotatif et révocable.
4. Reporting serveur : réception transactionnelle et déduplication.
5. Reporting agent : Outbox at-least-once.
6. Configuration serveur : révisions immuables et endpoint autorisé.
7. Auto-configuration agent : négociation/validation/application atomique.
8. Scheduling serveur : occurrences par profile/repository, remplacement et annulation.

Chaque étape exige tests unitaires, intégration, panne et migration avant d'être déclarée terminée.

## 3. Plateformes et dépendances

- Go **1.27.x** : vérifier la version et les outils dans la CI/build, ne jamais les supposer disponibles.
- MVP : agent et serveur **Linux amd64**. Préparer ensuite macOS arm64 et Windows amd64.
- Restic externe, version contrôlée au démarrage et dans les diagnostics : **>= 0.19.0**. Installation documentée par dépôt, `mise` ou release officielle vérifiée par checksum/signature ; aucune version téléchargée depuis une configuration distante.
- SBOM, licences MIT et transitives, audit de compatibilité et attribution requis. L'absence de fichier `LICENSE` n'est pas une décision de créer ce fichier ici.

## 4. Persistance et réception d'un job

Séparer strictement configuration et données d'exécution. La configuration non secrète utilise des révisions immuables sur filesystem restreint. La DB locale durable conserve jobs, tentatives, opérations, état actif, mapping snapshots et Outbox.

Réception : valider identité, propriété, version et horaires ; ouvrir une transaction ; attribuer un `local_job_uuid` durable avant exécution ; persister l'état `received` ; commit durable ; seulement ensuite exécuter. Le serveur attribue `server_job_id` à la réception et déduplique l'identité locale durable.

Écriture fichier : temp dans le même filesystem, `fsync` fichier, `rename` atomique, `fsync` répertoire. Disque plein, permission, corruption ou échec de sync : `persistence_failed`, aucune confirmation de réussite. Ne jamais supprimer l'état actif pour débloquer.

## 5. Contrat JSON versionné

`schema_version` est un entier et commence à 1. Chaque pair annonce ses versions supportées ; la négociation utilise l'intersection et refuse explicitement l'absence d'intersection, sans downgrade silencieux. Les champs inconnus sont conservés dans `unknown_fields`/`extensions` JSON de l'autre DB, sans être interprétés comme configuration.

```json
{
  "schema_version": 1,
  "message_type": "job.result",
  "message_id": "uuid",
  "correlation_id": "uuid",
  "agent_id": "uuid",
  "server_job_id": "uuid",
  "local_job_uuid": "uuid",
  "sent_at": "2026-10-21T11:45:00Z",
  "payload": {},
  "extensions": {}
}
```

Limiter profondeur, taille et nombre de clés. `restic_json` est borné et redigé ; il reste un payload imbriqué, jamais le contrat API. Voir [le schéma v1](19-schema-bootstrap-v1.json).

## 6. Outbox et ACK

Chaque résultat est écrit avant envoi. Livraison at-least-once, retry avec backoff borné et jitter, clé idempotente `event_id`. Le serveur ACK uniquement après persistance et déduplication transactionnelles. L'Outbox est supprimée après ACK persistant.

Une saturation peut évincer les événements les plus anciens, mais elle doit exposer compteur monotone, `oldest_dropped_at`, volume/nombre perdu, alerte et état `degraded/outbox_loss`. Elle ne supprime ni job actif, ni tentative, ni processus, ni configuration, ni déduplication. L'éviction est testée et observable.

## 7. Backup, copy et hooks

Ordre : lock machine ; préconditions ; pre-hook ; `restic backup` ; association snapshot ; `restic copy` ; post-hook selon condition ; persistance ; unlock. Arguments en liste, sans shell implicite. Secrets par référence à variable d'environnement ou commande autorisée par clé, exécutable absolu et timeout ; jamais en arguments ou logs.

- Pre-hook code non nul : Restic non lancé ; `posthook_on_failed_prehook=false` par défaut.
- Échec, timeout, interruption, crash ou sortie Restic non décodable : `failed`.
- Restic réussi + post-hook échoué : `partial`.
- Primary réussi + copy échouée : `partial`; retry de copy réutilise le snapshot, sans nouveau backup.
- Un retry réussi devient `partial` pour l'investigation, avec les statuts par étape conservés.
- `unknown` représente une observation indéterminée, pas un succès.

## 8. Scheduling et maintenance

Le serveur est autorité des occurrences automatiques. Un job non accepté à `start + 12 h` par défaut expire et ne peut être démarré. La maintenance réconcilie les jobs expirés sans exécution destructive aveugle. Une révocation reçue à la reconnexion est appliquée avant nouveau démarrage.

Priorité : sécurité/révocation > backup/copy en cours > reporting > maintenance destructive. `forget`, `prune`, `check`, `stats` restent scopés par machine/profile/repository ; keep-last minimum 1 et règles Restic isolées. Une maintenance nécessite un mapping fiable et un owner compatible, sinon `blocked_unknown_scope`.

## 9. Enrollment, web et LDAP

Machine pré-déclarée ; token d'enrollment unique, révocable, à usage limité et valable 12 h ; renouvellement manuel uniquement. Credential permanent rotatif en fichier `0600`/OS secret manager. OpenLDAP impose StartTLS vérifié, CA/hostname, filtre incluant `objectClass=posixAccount` et échappement de l'identifiant.

Sessions opaques côté serveur, cookies `Secure`/`HttpOnly`/`SameSite`, rotation, expiration, révocation et CSRF sur mutation. Superadmin local de récupération : provisioning et reset hors ligne, journalisés ; jamais endpoint web non authentifié.

## 10. Export, reprise et build

Export central quotidien atomique : dump PostgreSQL cohérent, config/révisions, manifest checksums, métadonnées d'identité et références externes. RPO jobs : 3 jours ; RTO cible : 24 h. L'inventaire snapshots est séparé des jobs et ne fabrique pas de jobs manquants. Aucun replay automatique d'un job ancien ou incertain.

La CI doit vérifier Go 1.27.x, tests, race detector, `go vet`, lint, SBOM, licences, reproductibilité et types binaires. Les commandes Restic réellement utilisées (`backup`, `copy`, `forget`, `prune`, `check`, `stats`) doivent être testées.

## 11. Matrice de passage

Tester crash/disque plein/atomicité/corruption ; lock et concurrence ; hooks et timeouts ; partial/copy retry ; Outbox ACK perdu, doublons, ordre inversé et saturation ; négociation schema v1 et champs inconnus ; enrollment 12 h, révocation et rotation ; LDAP StartTLS, sessions/CSRF ; isolation repository et rétention ; maintenance expirée ; export/restauration <=24 h ; charge cible 300 machines/1 an.

## 12. Interdits

Ne pas downgrader Go/Restic silencieusement ; ne pas enregistrer secrets ; ne pas traiter un PID comme preuve ; ne pas supprimer état actif ; ne pas confondre snapshot observé et job réussi ; ne pas faire confiance au reverse proxy ; ne pas exécuter une maintenance avec mapping incomplet ; ne pas déclarer production avant preuve de restauration et tests de panne.