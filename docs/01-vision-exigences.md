# Vision et exigences

Statut : conception uniquement, non prêt pour la production.

## Problème traité

Centraliser le pilotage et l'observation de sauvegardes Restic de plusieurs clients, sans centraliser nécessairement les données ni les secrets des dépôts. Une réussite du processus ne constitue pas, à elle seule, une preuve de restaurabilité applicative.

## Exigences exprimées

- Un client reçoit une configuration, lance Restic et remonte le résultat par API REST.
- Le serveur gère les remontées, planifie les déclenchements et affiche les résultats.
- Plusieurs repositories sont possibles ; chaque destination décrit son type, ses paramètres et ses credentials.
- La politique contient les sources à inclure et les exclusions.
- Le client dispose d'un endpoint de remontée d'état et de credentials d'accès.
- Un verrou client interdit deux sauvegardes simultanées.
- Une durée limite permet de signaler un job potentiellement bloqué et nécessitant une vérification manuelle.
- Les erreurs sont notifiées par email, Matrix, Slack ou autres providers.
- La fenêtre de synthèse des erreurs est de 24 heures par défaut et configurable.
- La fenêtre de rapport est de 7 jours par défaut et configurable ; durée et volumétrie y figurent.
- README et documentation doivent afficher clairement le statut de projet en conception.

## Objectifs complémentaires proposés

Détecter aussi les tâches jamais démarrées ; survivre à une indisponibilité temporaire de l'API ; différencier backup incomplet et erreur fatale ; tracer les révisions de configuration ; protéger les secrets ; tester les restaurations.

## Terminologie

- Agent : service local chargé de l'exécution.
- Politique : définition versionnée d'une sauvegarde.
- Job : occurrence logique d'une politique, prévue ou manuelle.
- Tentative : essai d'exécution d'un job.
- Destination : dépôt ciblé par une opération.
- Incident : anomalie suivie dans le temps, distincte d'une notification.
- RPO : objectif maximal d'ancienneté des données récupérables.

## Limites initiales proposées

Pas de restauration distante automatique, pas de haute disponibilité du scheduler, pas de multi-tenancy complet, pas d'exécution arbitraire de commandes distribuées. Les intégrations de cohérence applicative restent à spécifier avant activation.

## Questions de dimensionnement

À renseigner avant implémentation : nombre d'agents et de politiques, destinations par politique, fréquence des événements, taille des logs, historique conservé, débit API, indisponibilité acceptable et objectifs de restauration du service central. Aucun engagement de performance n'est établi.
