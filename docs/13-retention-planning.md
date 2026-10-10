# Rétention et planning mis en cache par les clients

Date : 2026-10-10. Projet en conception — NON PRÊT POUR LA PRODUCTION.

Ce document complète les décisions existantes et remplace les dispositions incompatibles sur le déclenchement. EXIGENCE reprend la demande du porteur ; PROPOSITION identifie les précisions restant à valider.

## 1. Règles de conservation et déclencheurs

EXIGENCE : la purge est un type de job. Deux critères de conservation sont proposés : keep-last=X conserve les X derniers jobs réussis ; keep-after=DATE_SPEC conserve les snapshots réussis après la date indiquée. DATE_SPEC accepte une date/heure absolue complète ou une durée relative, par exemple 8w = now moins huit semaines.

Ces critères définissent ce qui doit être conservé ; ils ne définissent pas quand le job de purge démarre. La programmation du job forget doit donc être configurée séparément : intervalle ou heure quotidienne, et éventuellement déclenchement manuel. Une dépendance après backup/copy est une PROPOSITION complémentaire, non obligatoire par défaut.

Ne pas confondre forget, qui retire les snapshots sélectionnés, et prune, qui récupère les données devenues inutiles. Prévoir des jobs et résultats séparés ; prune possède sa programmation propre ou une dépendance explicite.

## 2. Sémantique des critères

PROPOSITION : appliquer la politique par machine, profil et repository. Combiner les critères par union : conserver ce qui satisfait keep-last OU keep-after, puis ajouter les protections. Si un seul critère est configuré, appliquer celui-ci. Sans critère, ne rien supprimer.

keep-last compte des jobs logiques réussis, pas les tentatives ni les copies. PROPOSITION : réussite complète du job de backup selon sa règle globale ; ordonner par date de fin puis identifiant stable. Un résultat incomplet ne devient pas réussi par la seule présence d'un snapshot.

La correspondance job -> snapshot primaire -> snapshots répliqués doit être persistante et exploitable par l'agent. Les IDs source et destination ne sont pas supposés identiques. Conserver les snapshots associés aux jobs retenus ; ne pas effacer l'historique des jobs lors de forget.

Cas à préciser : succès sans nouveau snapshot avec skip-if-unchanged, plusieurs jobs associés au même snapshot, échec de copy après backup réussi et retries. PROPOSITION : les X derniers jobs réussis peuvent référencer moins de X snapshots distincts ; ne pas fabriquer des snapshots pour satisfaire un compteur.

keep-after compare le timestamp du snapshot au seuil. PROPOSITION : borne strictement supérieure, conformément au mot après ; les dates égales ne satisfont pas ce critère mais peuvent être protégées par keep-last. La définition exacte du succès du snapshot doit être rattachée à un résultat backup complet, pas déduite seulement de ses tags.

Date absolue : format RFC3339 avec offset ou Z requis. Durée relative : grammaire documentée, avec w = 7 jours et d = 24 h ; 8w = 56 jours. Autres unités restent à définir, sans interprétation ambiguë de mois calendaires.

PROPOSITION : now est l'horodatage UTC d'évaluation transmis par le serveur pour cette tentative, figé et conservé dans le plan de suppression. Un retry ne recalcule pas silencieusement un seuil différent ; si une réévaluation est nécessaire, créer un nouveau plan explicite.

## 3. Traduction vers Restic et garde-fous

Ne pas assimiler keep-last jobs réussis à --keep-last snapshots. Ne pas assimiler keep-after relatif à now à --keep-within, dont la référence native est le dernier snapshot. keep-after est un champ de restic-central, pas un flag Restic promis par cette conception.

L'agent inspecte les métadonnées des snapshots, réconcilie les associations aux jobs, calcule les ensembles conservés et supprimables, puis appelle forget sur les IDs explicitement sélectionnés. Aucune liste de fichiers sauvegardés n'est nécessaire.

PROPOSITION de sécurité : préserver les snapshots non identifiés, de succès inconnu, utilisés par une copy requise en attente ou protégés explicitement. En cas d'historique incomplet, de perte de correspondance ou de doute sur l'appartenance au profil, ne pas supprimer automatiquement.

Valider X entier strictement positif ; toute politique autorisant une suppression totale demande un choix explicite distinct. Ne jamais faire oublier les snapshots d'un autre profil. Avant application, vérifier à nouveau les préconditions et la disponibilité des snapshots ciblés sous coordination locale ; persister un plan expurgé avec seuil et nombres conservés/supprimés.

La durée de conservation des associations snapshot/job peut devoir dépasser l'année de reporting si des snapshots plus anciens sont encore retenus. Archiver les associations indispensables plutôt que supprimer aveuglément ces métadonnées.

## 4. Déclenchement quotidien et intervalle

EXIGENCE : le backup peut être programmé à une heure du jour, par exemple 18:00:00. Le mode intervalle ancré déjà prévu reste disponible.

PROPOSITION : deux modes exclusifs, interval avec ancre UTC et durée, daily_time avec HH:MM:SS et timezone IANA explicite. Exemple quotidien : 18:00:00 Europe/Paris. Une heure seule ne définit pas un instant UTC.

Le serveur calcule l'instant suivant puis transmet un timestamp d'exécution. Le client n'a pas à recalculer le calendrier local. Les rapports affichent datetime avec TZ.

Règles proposées pour daily_time : une occurrence par jour civil ; heure inexistante au passage DST décalée au premier instant valide ; heure répétée exécutée une seule fois à la première occurrence. Ces choix restent à valider. Le mode interval ne promet pas une heure locale constante lors du changement d'heure.

## 5. Distribution anticipée et cache

EXIGENCE : le serveur calcule le prochain job de chaque type pour chaque client non désactivé ; le client récupère la tâche et la lance au moment défini. Le client vérifie régulièrement les changements et adapte son planning local.

Le serveur reste l'autorité du calendrier ; le client est l'exécuteur temporisé des occurrences déjà distribuées. Cela remplace l'idée que le client ne récupère un job qu'au moment de son lancement. Cela n'autorise pas un scheduler client à générer librement de nouvelles occurrences.

Chaque tâche distribuée doit identifier job_id, type, machine, profil ou repository, config_revision, planning_revision, scheduled_at et contraintes/dependances. PROPOSITION : ajouter not_before, start_deadline et valid_until pour borner l'autorisation d'exécution hors ligne.

Le serveur calcule les prochaines tâches par type ET périmètre : un client peut avoir plusieurs profils backup et plusieurs repositories à maintenir. Ne pas réduire le planning à une unique tâche backup par machine.

Le cache local est persistant. PROPOSITION : réconciliation périodique par révision/ETag et réponse faisant autorité ; appliquer atomiquement nouvelles tâches, remplacements et annulations. Éviter un cache partiellement mis à jour. L'intervalle de polling reste configurable et à définir.

Une occurrence garde une identité idempotente ; réviser une heure ne crée pas deux autorisations simultanées. Une tâche commencée conserve la configuration réellement exécutée. Un changement de planning n'interrompt pas automatiquement un processus actif.

## 6. Déconnexion, suspension et exécution

Une désactivation/suspension supprime les départs futurs côté serveur et invalide les tâches correspondantes lors de la prochaine synchronisation. Un client déconnecté ne peut pas connaître instantanément une suspension décidée à distance.

PROPOSITION : autoriser les backups déjà distribués dans leur fenêtre de validité ; exiger une confirmation fraîche pour forget/prune avant toute suppression. Si l'API est indisponible, reporter ces tâches destructives. La politique hors ligne exacte doit être validée et exposée aux opérateurs.

Avant exécution : vérifier identité/propriété du dépôt, révision autorisée, validité temporelle, suspension connue, dépendances, préconditions et verrou local. Si la tâche attend le verrou, contrôler encore sa deadline avant démarrage.

La réservation d'une tâche future est distincte du lease d'exécution : ne pas laisser expirer le lease parce que le client attend scheduled_at. Après crash/redémarrage, réconcilier les tentatives actives avant lancement. Les commandes locales manuelles gardent le même verrou et ne modifient pas le calendrier automatique.

PROPOSITION : surveiller la dérive d'horloge, utiliser l'UTC pour les instants et l'horloge monotone pour les durées ; ne pas lancer une purge si l'heure de référence est incertaine.

## 7. Types de jobs de maintenance

Prévoir forget, prune, check et stats avec calendrier propre par repository appartenant à la machine. Réplication copy liée au backup et contrôles après prune peuvent être modélisés par dépendances explicites. Ce document ne valide pas automatiquement tout le workflow de maintenance proposé auparavant.

## 8. Validation

Tester union des critères, bornes temporelles, dates RFC3339 invalides, durées relatives, historique incomplet, snapshots inconnus, copie en attente, profils multiples, succès sans snapshot, calendrier quotidien/DST, planning remplacé/annulé, offline et validité, purge reportée sans API, verrou occupé, redémarrage et absence de doublons.

Référence de sémantique Restic : https://restic.readthedocs.io/en/stable/060_forget.html

Les autres amendements en attente restent des publications distinctes. Aucun schéma de configuration ou endpoint stable n'est livré par ce document.
