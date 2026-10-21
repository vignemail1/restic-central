# Contrat REST et fiabilité

Statut : **matrice normative de cadrage des routes**, non preuve d’implémentation. Les routes sont classées **MVP** ou **futures**; une route future n’est pas une API livrée. Les payloads JSON renvoient aux schémas normatifs `contracts/schemas/v1/`.

## Transport, version et conventions communes

Toutes les routes serveur utilisent HTTPS avec vérification TLS. Le client envoie `Content-Type: application/json` et `Accept: application/json`. Une version de protocole est négociée avant les échanges métier par `version.negotiate.request`; le serveur sélectionne la version commune maximale. Une liste vide d’intersection ou une version non supportée produit une erreur explicite, sans downgrade silencieux. Les champs inconnus sont préservés dans `extensions` avant validation stricte, sans interprétation ni exécution.

Les routes agent utilisent `Authorization: Bearer <operational-credential>` et vérifient l’ownership de l’agent dans le token, jamais seulement un identifiant de chemin. Le token d’enrôlement est distinct, unique, à usage limité, révocable et valable au maximum 12 h; il ne peut appeler que l’enrollment. Les credentials opérationnels sont rotatifs et révocables; jusqu’à décision d’implémentation, la procédure exacte de rotation, la coexistence temporaire des credentials et la révocation hors ligne restent ouvertes et ne sont pas inventées par cette matrice.

Les routes opérateur utilisent une session applicative authentifiée (compte local ou OpenLDAP `posixAccount` selon le périmètre), avec cookie `Secure`/`HttpOnly`/`SameSite`, expiration, révocation et CSRF sur mutations. Toute action opérateur, y compris login/logout, lancement, annulation, rotation/révocation et reset, est auditée sans secret. Le mapping LDAP groupes→rôles est futur; l’autorisation MVP reste celle des rôles locaux explicitement configurés. Le reset du superadmin local est **hors ligne**, journalisé, et ne doit jamais être un endpoint web non authentifié.

Chaque requête mutante peut porter `Idempotency-Key`; `message_id` identifie l’enveloppe, `event_id` un événement et `idempotency_key` l’opération logique. Le serveur attribue `server_job_id`; un agent autonome conserve `local_job_uuid`.

Réponse JSON : enveloppe v1 quand un message est défini; sinon objet d’erreur `error.schema.json` (avec `correlation_id` si disponible). Codes communs : `400` contrat invalide, `401` session/credential absent ou invalide, `403` interdit, `404` ressource absente, `409` conflit ou même identifiant avec contenu différent, `413` taille, `415` média, `422` règle métier, `429` quota avec `Retry-After`, `500` erreur serveur et `503` indisponibilité temporaire. Les codes ci-dessous sont le contrat de cadrage de chaque route; les détails d’implémentation restent à valider. La matrice couvre 22 routes HTTP (13 MVP, 9 futures) et une procédure hors HTTP; ce décompte ne vaut pas preuve d’implémentation. Les opérations non listées, notamment consultation détaillée des logs par job, export des logs, recherche avancée, purge/rétention et endpoints de santé/métriques, restent hors contrat et doivent être ajoutées avant d’être considérées comme couvertes.

## Matrice normative de couverture

| Couverture | Méthode/path | Authentification et autorisation | Requête → réponse | Succès et erreurs prévues |
|---|---|---|---|---|
| MVP | POST `/api/v1/version/negotiate` | aucune identité métier; TLS | `version.negotiate.request` → `version.negotiate.response` ou `error` | 200; 400, 406 (aucune version commune), 415 |
| MVP | POST `/api/v1/agents/enroll` | token enrollment; machine pré-déclarée | `agent.enroll` → `agent.enroll.result` ou `error` | 201; 400, 401, 409, 422 |
| MVP | POST `/api/v1/agents/{agent_id}/heartbeat` | Bearer agent du même `agent_id` | `heartbeat` → `heartbeat` ou `error` | 202; 400, 401, 403, 404, 429 |
| MVP | GET `/api/v1/agents/{agent_id}/configuration` | Bearer agent du même `agent_id` | aucun corps → `config.get.response` ou `error` | 200; 401, 403, 404 |
| MVP | POST `/api/v1/agents/{agent_id}/jobs/claim` | Bearer agent du même `agent_id` | `job.claim.request` → `job.claim.response` ou `error` | 200; 400, 401, 403, 409, 429 |
| MVP | POST `/api/v1/attempts/{attempt_id}/accept` | Bearer agent propriétaire de la tentative | `job.accept` → `result.ack` ou `error` | 202; 400, 401, 403, 404, 409 |
| MVP | POST `/api/v1/attempts/{attempt_id}/renew` | Bearer agent propriétaire de la tentative | `attempt.renew` → `result.ack` ou `error` | 200; 400, 401, 403, 404, 409, 422 |
| MVP | POST `/api/v1/attempts/{attempt_id}/events` | Bearer agent propriétaire de la tentative | `event.batch` → `result.ack` ou `error` | 202; 400, 401, 403, 404, 409, 413 |
| MVP | POST `/api/v1/attempts/{attempt_id}/result` | Bearer agent propriétaire de la tentative | `attempt.result` ou `result.upload` → `result.ack` ou `error` | 202; 400, 401, 403, 404, 409, 413, 422 |
| MVP | POST `/api/v1/attempts/{attempt_id}/cancel` | Bearer agent propriétaire ou session opérateur autorisée | `job.cancel` → `job.cancel` ou `error` | 202; 400, 401, 403, 404, 409, 422 |
| MVP | POST `/api/v1/reconcile` | Bearer agent | `reconcile.request` → `reconcile.response` ou `error` | 200; 400, 401, 409 |
| MVP | POST `/api/v1/snapshots/reconcile` | Bearer agent | `snapshot.reconcile` → `result.ack` ou `error` | 202; 400, 401, 409, 422 |
| MVP | POST `/api/v1/outbox/ack` | Bearer agent | `result.ack` → `result.ack` ou `error` | 200; 400, 401, 409 |
| Futur | POST `/api/v1/operator/login` | aucune session; local/LDAP | credentials non contractuels → session ou `error` | 200; 400, 401, 429 |
| Futur | POST `/api/v1/operator/logout` | session opérateur valide | aucun corps → `error` éventuel | 204; 401 |
| Futur | POST `/api/v1/operator/agents/{agent_id}/rotate` | session opérateur avec droit d’identité | commande rotation à définir → résultat à définir ou `error` | 202; 401, 403, 404, 409, 422 |
| Futur | POST `/api/v1/operator/agents/{agent_id}/revoke` | session opérateur avec droit d’identité | commande révocation à définir → résultat à définir ou `error` | 202; 401, 403, 404, 409, 422 |
| Futur | POST `/api/v1/policies/{policy_id}/jobs` | session opérateur avec droit d’exécution | `operator.job.request` → `operator.job.response` ou `error` | 202; 400, 401, 403, 422 |
| Futur | GET `/api/v1/jobs/{server_job_id}` | session opérateur avec droit de lecture | aucun corps → `operator.job.response` ou `error` | 200; 401, 403, 404 |
| Futur | GET `/api/v1/reports/backups` | session opérateur avec droit de lecture | query `page_token`/`page_size` → `page.response` ou `error` | 200; 400, 401, 403 |
| Futur | POST `/api/v1/maintenance` | Bearer agent ou session opérateur autorisée | payload maintenance à définir → `result.ack` ou `error` | 202; 400, 401, 403, 422 |
| Futur | GET `/api/v1/audit` | session opérateur avec droit d’audit | query pagination → `page.response` ou `error` | 200; 400, 401, 403 |
| Hors HTTP MVP | procédure de reset du superadmin local | accès console/hors ligne, aucune session web | procédure opératoire à définir → audit local | succès hors HTTP; refus si préconditions absentes |

La corrélation des logs avec un job est autorisée pour les utilisateurs et rôles habilités via `server_job_id`, `local_job_uuid` ou `correlation_id`; elle ne donne pas accès aux logs ni aux données du job sans autorisation. Chaque ACK est émis seulement après stockage durable et déduplication transactionnelle; un doublon identique est ACKé sans effet de bord, un même identifiant avec contenu différent est rejeté en `409`. Les retries sont at-least-once, avec backoff/jitter bornés et respect de `Retry-After`; aucune exactly-once n’est promise. Les réponses `failed` couvrent pre-hook/backup invalide; `partial` couvre réplication/post-hook ou retry récupéré.
