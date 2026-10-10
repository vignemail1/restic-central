# Notifications et rapports

Statut : comportement fonctionnel proposé.

## Incidents

Catégories : backup failed, backup partial, destination failed, échéance manquée, runtime dépassé, agent injoignable, résultat inconnu et vérification en échec.

Une absence de contact ne prouve pas un blocage du processus. La notification décrit ce qui est observé, la dernière activité connue et la vérification recommandée.

Regrouper par agent, politique, destination et catégorie. Conserver date d'ouverture, dernière occurrence, sévérité, acquittement et résolution. Un acquittement n'est pas une résolution. Une période de maintenance ne doit pas effacer l'historique.

## Notifications immédiates

Ouverture d'incident, escalade éventuelle et rétablissement. Définir cooldown, regroupement et suppression des doublons. Un retry réussi peut résoudre l'incident selon la règle de succès, sans effacer la tentative échouée.

Providers envisagés : email, Matrix, Slack ; extension par interface commune. Un canal initial suffit au MVP, son choix reste ouvert.

Chaque livraison dispose d'un historique et d'une politique de retry. Un échec de notification ne change pas le résultat de la sauvegarde. Les messages excluent les secrets et limitent les informations sensibles.

## Synthèse sur 24 heures

Fenêtre configurable, 24 heures par défaut. Présenter séparément : incidents ouverts dans la fenêtre, incidents encore ouverts même plus anciens, incidents résolus et échéances non satisfaites.

Distinguer fenêtre glissante et journée calendaire. La cadence d'envoi est distincte de la fenêtre : proposition initiale, synthèse quotidienne à heure configurable.

## Rapport sur 7 jours

Fenêtre configurable, 7 jours par défaut. Filtres : agent, politique, destination, statut et période. Rapport initial fondé sur l'échéance des jobs ; détailler séparément dates de démarrage et de fin.

Indicateurs : échéances attendues, jobs créés, démarrés, réussis, incomplets, échoués, ignorés et manqués ; nombre de tentatives ; temps d'attente ; durée totale et durée par destination ; âge du dernier succès complet ; dernière vérification ; volumes disponibles.

Un taux de succès doit préciser son dénominateur. Proposition : jobs complètement réussis / échéances attendues hors maintenance, avec catégories détaillées ; ne pas gonfler ce taux en comptant les retries comme de nouveaux jobs.

## Volumétrie

Distinguer taille logique traitée, données ajoutées au dépôt, données ajoutées après compression si disponibles et trafic réseau effectivement mesuré. Ne pas appeler toutes ces mesures volume sauvegardé.

Un compteur absent reste null ou indisponible, pas zéro. Identifier l'origine : Restic, mesure agent ou calcul serveur. Ne pas déduire le trafic réseau exact de la seule taille des données ajoutées.

En destinations multiples, les sommes par dépôt ne représentent pas nécessairement des données sources uniques. Séparer volumes source, backup et réplication.

## Fraîcheur et restaurabilité

Comparer le dernier succès complet à l'objectif de fraîcheur/RPO. Exposer séparément dernier check réussi et dernier test de restauration réussi. Un backup réussi ne remplace ni le contrôle d'intégrité ni la validation applicative d'une restauration.

## Présentation

Tableau de bord global, vue par agent, historique de politique, détail de job avec tentatives et destinations, liste d'incidents. Format d'export à décider ; CSV est proposé. Afficher le fuseau et les bornes de période ; une période sans historique suffisant doit être signalée.
