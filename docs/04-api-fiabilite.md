# Contrat REST et fiabilité

Statut : contrat indicatif non implémenté. Les chemins ci-dessous ne constituent pas une API stable.

## Transport et identité

HTTPS avec validation des certificats. Communications initiées par l'agent ; polling ou long polling proposé. Chaque agent est authentifié et autorisé uniquement sur ses ressources. Les identifiants envoyés dans le corps ne remplacent jamais l'identité authentifiée.

## Ressources envisagées

| Méthode et chemin | Usage |
|---|---|
| POST /api/v1/agents/enroll | enrôlement contrôlé, mécanisme à définir |
| POST /api/v1/agents/{id}/heartbeat | disponibilité et capacités |
| GET /api/v1/agents/{id}/configuration | révision autorisée de configuration |
| POST /api/v1/agents/{id}/jobs/claim | acquisition atomique d'un job |
| POST /api/v1/attempts/{id}/renew | renouvellement de réservation |
| POST /api/v1/attempts/{id}/events | lot d'événements idempotents |
| POST /api/v1/attempts/{id}/result | résultat terminal idempotent |
| POST /api/v1/policies/{id}/jobs | demande manuelle, accès administrateur |
| GET /api/v1/jobs/{id} | état et résultats par destination |
| GET /api/v1/reports/backups | rapport filtré et paginé |

Prévoir pagination, limites de corps, validation stricte, erreurs structurées, identifiants de corrélation et versionnement. Les endpoints d'administration et d'agent ont des autorisations distinctes.

## Enveloppe événement

Champs minimaux : event_id, agent_id, job_id, attempt_id, config_revision, sequence_number, occurred_at, event_type, payload. Le serveur ajoute received_at. Dates transportées en UTC ; conserver les deux dates pour diagnostiquer retard et désynchronisation.

Le serveur déduplique par event_id, contrôle l'appartenance de la tentative et détecte les séquences manquantes ou hors ordre. Un doublon identique est acquitté sans nouvel effet ; le même identifiant avec contenu différent est rejeté.

## Outbox locale

Persister avant envoi. Acquitter seulement après confirmation de persistance serveur. Garantir une livraison au moins une fois, pas une promesse de livraison exactement une fois.

Retries avec backoff, jitter, limite et traitement des erreurs : 429 et erreurs temporaires peuvent être réessayés ; erreurs d'authentification déclenchent un état dégradé et ne produisent pas une boucle agressive. Respecter Retry-After lorsqu'applicable.

Configurer quota local, rétention, reprise après crash et politique de saturation. Les événements terminaux ont priorité ; les progressions peuvent être regroupées. L'absence d'espace pour persister doit produire une erreur visible, pas une perte silencieuse.

Un résultat en attente d'envoi n'autorise jamais le redémarrage automatique de la sauvegarde terminée.

## Réservations et concurrence

L'acquisition est transactionnelle. Une tentative reçoit un identifiant et une réservation renouvelable. Le serveur refuse les mises à jour provenant d'une tentative non autorisée.

L'expiration d'une réservation n'établit pas l'arrêt de Restic. Ne pas redistribuer automatiquement un job potentiellement actif à un autre agent. Réconciliation nécessaire avant relance ; une protection de fencing des écritures de métadonnées ne suffit pas à arrêter un processus qui écrit dans un dépôt.

## Réconciliation

Au reconnect, l'agent transmet ses tentatives actives et ses résultats persistés. Le serveur répond avec son état autoritatif de coordination et les événements attendus. Les divergences sont tracées. Un résultat tardif peut résoudre un état d'observation inconnu selon des règles explicites, sans effacer l'incident historique.

## Annulation

Distinguer demande d'annulation, réception agent et arrêt confirmé. Une API ne doit pas annoncer canceled uniquement parce qu'une demande a été enregistrée. Le traitement du groupe de processus et du délai de grâce dépendra du système supporté.
