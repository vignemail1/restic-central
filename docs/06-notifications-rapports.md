# Notifications et rapports

Statut : comportement fonctionnel proposé.

## Incidents

Catégories : backup échoué, backup partiel, destination en échec, occurrence manquée, durée dépassée, agent injoignable, résultat inconnu et vérification échouée.

Une absence de contact ne prouve pas qu’un processus est bloqué. Les notifications décrivent les observations, la dernière activité connue et l’inspection recommandée.

Regrouper par agent, policy, destination et catégorie. Conserver l’heure d’ouverture, la dernière occurrence, la sévérité, l’acquittement et la résolution. Un acquittement n’est pas une résolution. Les périodes de maintenance ne doivent pas effacer l’historique.

## Notifications immédiates

Ouverture d’incident, escalade facultative et rétablissement. Définir une période de cooldown, le regroupement et la suppression des doublons. Un retry réussi peut résoudre un incident selon la règle de réussite sans effacer la tentative échouée.

Providers proposés : email, Matrix, Slack ; extensibilité via une interface commune. Un seul canal initial suffit pour le MVP ; le choix reste ouvert.

Chaque livraison possède un historique et une policy de retry. L’échec d’une notification ne modifie pas le résultat du backup. Les messages excluent les secrets et limitent les informations sensibles.

## Récapitulatif sur 24 heures

Fenêtre configurable, 24 heures par défaut. Présenter séparément les incidents ouverts dans la fenêtre, les incidents encore ouverts même s’ils sont plus anciens, les incidents résolus et les occurrences planifiées non exécutées.

Distinguer les fenêtres glissantes des jours calendaires. La fréquence d’envoi est distincte de la fenêtre : proposition initiale, récapitulatif quotidien à une heure configurable.

## Rapport sur 7 jours

Fenêtre configurable, 7 jours par défaut. Filtres : agent, policy, destination, statut et période. Le rapport initial utilise les heures planifiées des jobs ; afficher séparément les heures de début et de fin.

Métriques : occurrences attendues ; jobs créés, démarrés, réussis, incomplets, échoués, ignorés et manqués ; nombre de tentatives ; temps d’attente ; durée totale et par destination ; ancienneté de la dernière réussite complète ; dernière vérification ; métriques de volume disponibles.

Un taux de réussite doit préciser son dénominateur. Proposition : jobs entièrement réussis / occurrences attendues hors maintenance, avec catégories détaillées. Ne pas augmenter artificiellement le taux en comptant les retries comme de nouveaux jobs.

## Volumes de données

Distinguer les données logiques traitées, les données ajoutées au repository, les données ajoutées compressées lorsqu’elles sont disponibles et le trafic réseau réellement mesuré. Ne pas appeler toutes ces mesures « volume de sauvegarde ».

Un compteur manquant reste null ou indisponible, pas zéro. Indiquer sa source : Restic, mesure de l’agent ou calcul du serveur. Ne pas déduire le trafic réseau exact de la seule taille des données ajoutées.

Avec plusieurs destinations, les totaux par repository ne représentent pas nécessairement des données source uniques. Séparer les volumes source, backup et réplication.

## Fraîcheur et récupérabilité

Comparer la dernière réussite complète à la cible de fraîcheur/RPO. Présenter séparément la dernière vérification réussie et le dernier test de restauration. Une sauvegarde réussie ne remplace ni la vérification d’intégrité ni la validation de restauration au niveau applicatif.

## Présentation

Dashboard global, vue par agent, historique de policy, détails de job avec tentatives et destinations, et liste des incidents. Le format d’export reste à déterminer ; CSV est proposé. Afficher le fuseau horaire et les limites de période ; signaler les périodes avec un historique insuffisant.
