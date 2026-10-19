# Vision et exigences

Statut : conception uniquement, non prêt pour la production.

## Problème traité

Centraliser l’orchestration et l’observation des sauvegardes Restic sur plusieurs clients, sans nécessairement centraliser les données de sauvegarde ni les secrets des repositories. La réussite de l’exécution d’un processus ne prouve pas à elle seule que les données sont récupérables au niveau applicatif.

## Exigences exprimées

- Un client reçoit une configuration, exécute Restic et transmet le résultat via une API REST.
- Le serveur traite les rapports, planifie les exécutions et affiche les résultats.
- Plusieurs repositories sont pris en charge ; chaque destination décrit son type, ses paramètres et ses credentials.
- La policy contient les sources incluses et les exclusions.
- Le client dispose d’un endpoint de reporting et de credentials d’accès.
- Un lock côté client empêche deux sauvegardes simultanées.
- Une limite de durée signale un job potentiellement bloqué qui nécessite une inspection manuelle.
- Les erreurs sont notifiées par email, Matrix, Slack ou d’autres providers.
- La fenêtre du récapitulatif des erreurs est de 24 heures par défaut et configurable.
- La fenêtre de reporting est de 7 jours par défaut et configurable ; elle inclut la durée et les métriques de volume de données.
- Le README et la documentation doivent afficher clairement que le projet est en phase de conception.

## Objectifs supplémentaires proposés

Détecter les tâches qui ne démarrent jamais ; résister à une indisponibilité temporaire de l’API ; distinguer les sauvegardes incomplètes des erreurs fatales ; suivre les révisions de configuration ; protéger les secrets ; tester les restaurations.

## Terminologie

- Agent : service local responsable de l’exécution.
- Policy : définition versionnée d’une sauvegarde.
- Job : occurrence logique d’une policy, planifiée ou manuelle.
- Attempt : une tentative d’exécution d’un job.
- Destination : repository ciblé par une opération.
- Incident : problème suivi dans le temps, distinct d’une notification.
- RPO : ancienneté maximale visée pour les données récupérables.

## Limites initiales proposées

Pas de restauration distante automatique, pas de scheduler hautement disponible, pas de multi-tenancy complète ni d’exécution arbitraire de commandes distribuées. Les intégrations de cohérence applicative doivent être spécifiées avant activation.

## Questions de dimensionnement

À définir avant implémentation : nombre d’agents et de policies, destinations par policy, fréquence des événements, taille des logs, historique conservé, débit de l’API, indisponibilité acceptable et objectifs de reprise du service central. Aucun engagement de performance n’a été établi.
