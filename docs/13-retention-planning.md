# Rétention et planification mises en cache par les clients

Date : 2026-10-10. Projet en conception — NON PRÊT POUR LA PRODUCTION.

Ce document complète les décisions existantes et remplace les dispositions incompatibles sur le déclenchement. **EXIGENCE** reprend la demande du porteur ; **PROPOSITION** identifie les précisions restant à valider.

## 1. Règles de conservation et déclencheurs

**EXIGENCE :** la purge est un type de job. Deux critères de conservation sont proposés : `keep-last=X` conserve les X derniers jobs réussis ; `keep-after=DATE_SPEC` conserve les snapshots réussis après la date indiquée. DATE_SPEC accepte une date/heure absolue complète ou une durée relative, par exemple `8w` = `now` moins huit semaines.

Ces critères définissent ce qui doit être conservé ; ils ne définissent pas quand le job `forget` démarre. La planification du job `forget` doit donc être configurée séparément : intervalle ou heure quotidienne, et éventuellement déclenchement manuel. Une dépendance après backup/copy est une proposition complémentaire, non obligatoire par défaut.

Ne pas confondre `forget`, qui retire les snapshots sélectionnés, et `prune`, qui récupère les données devenues inutiles. Prévoir des jobs et résultats distincts ; `prune` possède sa propre planification ou une dépendance explicite.

## 2. Sémantique des critères

**Règle normative :** appliquer la policy par machine, profile et repository. Combiner les critères par union : conserver ce qui satisfait `keep-last` OU `keep-after`, puis ajouter les protections. **Protéger au minimum le dernier snapshot valide de chaque périmètre machine/profile/repository**, indépendamment des critères. Si aucun snapshot valide n’existe, ne pas fabriquer de protection ; si l’historique est incomplet ou incertain, ne pas supprimer automatiquement. Sans critère, ne rien supprimer.

`keep-last` compte des jobs logiques réussis, pas les tentatives ni les copies. **PROPOSITION :** utiliser la réussite complète du job de backup selon sa règle globale ; trier par date de fin puis identifiant stable. Un résultat incomplet ne devient pas réussi par la seule présence d’un snapshot.

La correspondance job -> snapshot primaire -> snapshots répliqués doit être persistante et exploitable par l’agent. Les IDs source et destination ne sont pas supposés identiques. Conserver les snapshots associés aux jobs retenus ; ne pas effacer l’historique des jobs lors de `forget`.

Cas à préciser : réussite sans nouveau snapshot avec `skip-if-unchanged`, plusieurs jobs associés au même snapshot, échec de copy après backup réussi et retries. **PROPOSITION :** les X derniers jobs réussis peuvent référencer moins de X snapshots distincts ; ne pas fabriquer de snapshots pour satisfaire un compteur.

`keep-after` compare le timestamp du snapshot au seuil. **PROPOSITION :** borne strictement supérieure, conformément au mot « après » ; les dates égales ne satisfont pas ce critère, mais peuvent être protégées par `keep-last`. La définition exacte de réussite du snapshot doit être rattachée à un résultat de backup complet, pas déduite uniquement de ses tags.

Date absolue : format RFC3339 avec offset ou Z requis. Durée relative : grammaire documentée, avec `w` = 7 jours et `d` = 24 h ; `8w` = 56 jours. Les autres unités restent à définir, sans interprétation ambiguë des mois calendaires.

**PROPOSITION :** `now` est le timestamp UTC d’évaluation transmis par le serveur pour cette tentative, figé et conservé dans le plan de suppression. Un retry ne recalcule pas silencieusement un seuil différent ; si une réévaluation est nécessaire, créer un nouveau plan explicite.

## 3. Traduction vers Restic et garde-fous

Ne pas assimiler `keep-last` jobs réussis à `--keep-last` snapshots. Ne pas assimiler `keep-after` relatif à `now` à `--keep-within`, dont la référence native est le dernier snapshot. `keep-after` est un champ restic-central, pas un flag Restic promis par cette conception.

L’agent inspecte les métadonnées des snapshots, réconcilie les associations aux jobs, calcule les ensembles conservés et supprimables, puis appelle `forget` sur les IDs explicitement sélectionnés. Aucun inventaire des fichiers sauvegardés n’est nécessaire.

**Règle normative de sécurité :** préserver les snapshots non identifiés, à réussite inconnue ou explicitement protégés, ainsi que le dernier snapshot valide du périmètre. En cas d’historique incomplet, de correspondance perdue ou de doute sur l’appartenance au profile, ne pas supprimer automatiquement.

Valider que X est un entier strictement positif ; toute policy autorisant une suppression totale exige un choix explicite distinct. Ne jamais appliquer `forget` aux snapshots d’un autre profile. Avant application, vérifier de nouveau les préconditions et la disponibilité des snapshots ciblés sous coordination locale ; persister un plan expurgé indiquant seuil et nombres conservés/supprimés.

La durée de conservation des associations snapshot/job peut devoir dépasser l’année de reporting si des snapshots plus anciens sont encore retenus. Archiver les associations indispensables au lieu de supprimer aveuglément ces métadonnées.

## 4. Planification quotidienne et par intervalle

**EXIGENCE :** le backup peut être planifié à une heure du jour, par exemple 18:00:00. Le mode intervalle ancré déjà prévu reste également disponible.

**PROPOSITION :** deux modes exclusifs, `interval` avec ancre UTC et durée, et `daily_time` avec HH:MM:SS et timezone IANA explicite. Exemple quotidien : `18:00:00 Europe/Paris`. Une heure seule ne définit pas un instant UTC.

Le serveur calcule l’instant suivant puis transmet un timestamp d’exécution. Le client n’a pas à recalculer le calendrier local. Les rapports affichent datetime avec TZ.

Règles proposées pour `daily_time` : une occurrence par jour civil ; une heure inexistante lors du passage DST est décalée au premier instant valide ; une heure répétée est exécutée une seule fois, à sa première occurrence. Ces choix restent à valider. Le mode intervalle ne promet pas une heure locale constante lors du changement d’heure.

## 5. Distribution anticipée et cache

**EXIGENCE :** le serveur calcule le prochain job de chaque type pour chaque client non désactivé ; le client récupère la tâche et la lance à l’heure définie. Le client vérifie régulièrement les changements et adapte sa planification locale.

Le serveur reste l’autorité du calendrier ; le client est l’exécuteur temporisé des occurrences déjà distribuées. Cela remplace l’idée que le client ne récupère un job qu’au moment de son lancement. Cela n’autorise pas un scheduler client à générer librement de nouvelles occurrences.

Chaque tâche distribuée doit identifier `job_id`, type, machine, profile ou repository, `config_revision`, `planning_revision`, `scheduled_at` et contraintes/dépendances. **PROPOSITION :** ajouter `not_before`, `start_deadline` et `valid_until` pour borner l’autorisation d’exécution hors ligne.

Le serveur calcule les prochaines tâches par type ET périmètre : un client peut avoir plusieurs profiles backup et plusieurs repositories à maintenir. Ne pas réduire la planification à une tâche backup unique par machine.

Le cache local est persistant. **PROPOSITION :** réconciliation périodique par révision/ETag et réponse faisant autorité ; appliquer atomiquement les nouvelles tâches, remplacements et annulations. Éviter un cache partiellement mis à jour. L’intervalle de polling reste configurable et à définir.

Une occurrence conserve une identité idempotente ; réviser une heure ne crée pas deux autorisations simultanées. Une tâche commencée conserve la configuration effectivement exécutée. Un changement de planification n’interrompt pas automatiquement un processus actif.

## 6. Déconnexion, suspension et exécution

Une désactivation/suspension supprime les départs futurs côté serveur et invalide les tâches correspondantes à la prochaine synchronisation. Un client déconnecté ne peut pas connaître instantanément une suspension décidée à distance.

**PROPOSITION :** autoriser les backups déjà distribués dans leur fenêtre de validité ; exiger une confirmation récente pour `forget`/`prune` avant toute suppression. Si l’API est indisponible, reporter ces tâches destructives. La policy exacte hors ligne doit être validée et présentée aux opérateurs.

Avant exécution : vérifier identité/propriété du dépôt, révision autorisée, validité temporelle, suspension connue, dépendances, préconditions et lock local. Si la tâche attend le lock, contrôler encore sa deadline avant le démarrage.

La réservation d’une tâche future est distincte du lease d’exécution : ne pas laisser expirer le lease pendant l’attente de `scheduled_at`. Après crash/redémarrage, réconcilier les tentatives actives avant lancement. Les commandes locales manuelles utilisent le même lock et ne modifient pas le calendrier automatique.

**PROPOSITION :** surveiller la dérive d’horloge, utiliser UTC pour les instants et l’horloge monotone pour les durées ; ne pas lancer une purge si l’heure de référence est incertaine.

## 7. Types de jobs de maintenance

Prévoir `forget`, `prune`, `check` et `stats` avec un calendrier propre à chaque repository appartenant à la machine. `forget` ne peut jamais supprimer le dernier snapshot valide protégé par la règle ci-dessus. La réplication `copy` liée au backup et les contrôles après `prune` peuvent être modélisés par des dépendances explicites. Ce document ne valide pas automatiquement l’ensemble du workflow de maintenance proposé précédemment.

## 8. Validation

Tester l’union des critères, les bornes temporelles, les dates RFC3339 invalides, les durées relatives, l’historique incomplet, les snapshots inconnus, une copy en attente, plusieurs profiles, la réussite sans snapshot, le calendrier quotidien/DST, les tâches planifiées remplacées/annulées, le mode offline et la validité, le report de purge sans API, le lock occupé, le redémarrage et l’absence de doublons.

Référence de sémantique Restic : https://restic.readthedocs.io/en/stable/060_forget.html

Les autres amendements en attente restent des publications distinctes. Aucun schéma de configuration ni endpoint stable n’est livré par ce document.
