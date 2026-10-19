# Contrat REST et fiabilité

Statut : contrat illustratif, non implémenté. Les chemins ci-dessous ne constituent pas une API stable.

## Transport et identité

HTTPS avec vérification du certificat. Communication initiée par l’agent ; le polling ou long polling est proposé. Chaque agent est authentifié et autorisé uniquement pour ses propres ressources. Les identifiants transmis dans le corps des requêtes ne remplacent jamais l’identité authentifiée.

## Ressources proposées

| Méthode et chemin | Fonction |
|---|---|
| POST /api/v1/agents/enroll | enrôlement contrôlé ; mécanisme à définir |
| POST /api/v1/agents/{id}/heartbeat | disponibilité et capacités |
| GET /api/v1/agents/{id}/configuration | révision de configuration autorisée |
| POST /api/v1/agents/{id}/jobs/claim | acquisition atomique d’un job |
| POST /api/v1/attempts/{id}/renew | renouvellement de réservation |
| POST /api/v1/attempts/{id}/events | lot d’événements idempotent |
| POST /api/v1/attempts/{id}/result | résultat terminal idempotent |
| POST /api/v1/policies/{id}/jobs | demande manuelle, accès administrateur |
| GET /api/v1/jobs/{id} | état et résultats par destination |
| GET /api/v1/reports/backups | rapport filtré et paginé |

Prévoir pagination, limites de taille des requêtes, validation stricte, erreurs structurées, identifiants de corrélation et versionnage. Les endpoints d’administration et d’agent ont des permissions distinctes.

## Enveloppe d’événement

Champs minimaux : event_id, agent_id, job_id, attempt_id, config_revision, sequence_number, occurred_at, event_type, payload. Le serveur ajoute received_at. Les timestamps sont transmis en UTC ; conserver les deux dates pour diagnostiquer les retards et écarts d’horloge.

Le serveur déduplique par event_id, vérifie la propriété de la tentative et détecte les séquences manquantes ou hors ordre. Un doublon identique est acquitté sans nouvel effet de bord ; le même ID avec un contenu différent est rejeté.

## Outbox local

Persister avant l’envoi. Acquitter uniquement après confirmation de la persistance côté serveur. Fournir une livraison at-least-once, sans promettre une livraison exactly-once.

Les retries utilisent backoff, jitter, limites et classification des erreurs : 429 et erreurs temporaires peuvent être réessayées ; les erreurs d’authentification déclenchent un état dégradé plutôt qu’une boucle agressive. Respecter Retry-After le cas échéant.

Configurer le quota local, la rétention, la reprise après crash et la politique en cas de saturation. Les événements terminaux sont prioritaires ; les mises à jour de progression peuvent être regroupées. Un espace insuffisant pour persister doit provoquer une erreur visible, pas une perte silencieuse de données.

Un résultat en attente de transmission n’autorise jamais le redémarrage automatique du backup déjà terminé.

## Réservations et concurrence

L’acquisition est transactionnelle. Une tentative reçoit un ID et une réservation renouvelable. Le serveur rejette les mises à jour des tentatives non autorisées.

L’expiration d’une réservation ne prouve pas que Restic s’est arrêté. Ne pas redistribuer automatiquement un job potentiellement actif à un autre agent. Une réconciliation est nécessaire avant un retry ; le fencing des écritures de métadonnées ne peut pas empêcher un processus d’écrire dans un repository.

## Réconciliation

À la reconnexion, l’agent transmet ses tentatives actives et résultats persistés. Le serveur répond avec son état de coordination faisant autorité et les événements attendus. Les divergences sont consignées. Un résultat tardif peut résoudre un état d’observation inconnu selon des règles explicites, sans effacer l’incident historique.

## Annulation

Distinguer la demande d’annulation, sa réception par l’agent et l’arrêt confirmé. Une API ne doit pas déclarer un job annulé simplement parce qu’une demande a été enregistrée. La gestion des groupes de processus et les périodes de grâce dépendent du système d’exploitation pris en charge.
