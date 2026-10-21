# Audit et décisions consolidées — 2026-10-21

## Verdict

La conception est suffisamment décidée pour commencer l'implémentation, mais le projet est **non prêt pour la production**. L'agent, le serveur, migrations, contrats, tests de panne, packaging et runbook de restauration restent à livrer. Ce document ne remplace pas le cadrage ; il en fixe les décisions normatives et le statut.

## Décisions normatives

- Go 1.27.x ; MVP agent et serveur Linux amd64 ; macOS arm64 et Windows amd64 futurs. La présence des outils et versions doit être vérifiée dans CI/build, jamais supposée.
- Restic >= 0.19.0, installation par dépôt, `mise` ou release vérifiée ; refus des versions plus anciennes.
- Configuration et données d'exécution séparées ; persistance durable stricte par `fsync`/rename/DB transactionnelle. Échec de persistance = `persistence_failed`.
- Outbox at-least-once et ACK après persistance. Saturation : éviction possible des anciens événements, perte observable et durable ; aucun état actif supprimé.
- Pre/post hooks conservés en MVP. Pre-hook échoué bloque Restic ; post-hook après pre-hook échoué désactivé par défaut. Restic interrompu, timeout ou sortie non décodable = `failed`. Copy échouée après primary réussi = `partial`; retry réussi reste `partial` pour investigation.
- `unknown` signifie observation indéterminée. Les statuts détaillés par étape sont conservés.
- `schema_version` entier à partir de 1 ; intersection maximale commune, refus sans intersection ; champs inconnus conservés en JSON et jamais exécutés.
- Jobs autonomes : ID serveur à réception, identité locale durable avant exécution, déduplication et suppression Outbox après ACK persistant.
- Enrollment : agent pré-déclaré, token unique/révocable valable 12 h, renouvellement manuel. Secrets via env/commande explicitement autorisée par clé ; aucun secret dans les logs. La corrélation des logs par `server_job_id`, `local_job_uuid` ou `correlation_id` est autorisée aux utilisateurs habilités, sous contrôle d’accès, minimisation et rétention.
- LDAP posixAccount avec StartTLS vérifié ; superadmin local de récupération hors ligne ; sessions et CSRF côté application.
- Scheduling et maintenance sûrs : expiration d'un job non accepté à 12 h par défaut ; réévaluation des maintenances expirées ; aucune action destructive aveugle. Rétention keep-last minimum 1 et isolation Restic.
- Export serveur quotidien ; perte d'historique jobs tolérée jusqu'à 3 jours ; RTO 24 h. Inventaire snapshots séparé et non générateur de jobs.
- MIT sous réserve de compatibilité des dépendances ; cette synchronisation ne crée pas de fichier LICENSE.

## Gates encore ouverts

1. Implémenter agent, serveur, schémas, migrations, API, export et UI.
2. Prouver crash recovery, disque plein, Outbox saturée, idempotence, hooks, LDAP, révocation offline, rétention et restauration.
3. Vérifier packaging reproductible et installations Restic >= 0.19.0 sur les cibles annoncées.
4. Produire un runbook exécutable et une restauration <=24 h.

Les fichiers historiques restent présents et inchangés ; les contradictions éventuelles sont résolues par les décisions ci-dessus et par [le cadrage normatif](17-cadrage-llm-ready.md).