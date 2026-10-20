# Spécifications révisées

Révision : 2026-10-19. Statut : conception uniquement, **NON PRÊT POUR LA PRODUCTION**. Aucun comportement n’est implémenté.

Ce document complète la conception initiale et prévaut lorsque les sujets ci-dessous la contredisent. Les exigences proviennent du porteur du projet ; les éléments marqués **PROPOSITION** restent à valider. Les décisions explicitement validées le 2026-10-19 sont consignées dans le [registre des décisions](07-decisions.md) et les [décisions validées pour le développement](16-decisions-for-development.md). La validation d’une règle limitée à un périmètre ne valide pas les propositions voisines.

## 1. Profiles et filesets

Une machine possède plusieurs profiles de sauvegarde. Chaque profile a un identifiant stable, une configuration versionnée, un fileset d’inclusion/exclusion, des destinations, des hooks, un intervalle et des règles de rétention.

Le modèle devient Agent -> BackupProfile -> ConfigRevision -> Job -> Attempt -> DestinationResult. BackupProfile précise le concept initial de BackupPolicy ; des templates de policy partagés restent possibles sans confondre un profile exécuté avec un template partagé.

Chaque événement et rapport identifie la machine et le profile. Le lock requis reste à l’échelle machine : deux profiles ne doivent pas exécuter simultanément des backups via l’agent. Le travail qui se chevauche est mis en file ou signalé selon une policy restant à définir, jamais ignoré silencieusement.

## 2. Activation, suspension et maintenance

Le schedule d’une machine ou d’un profile peut être désactivé ou suspendu.

**PROPOSITION :** désactivé signifie arrêté sans échéance de reprise ; suspendu signifie suspension avec début, fin facultative, motif et auteur. La suspension d’une machine s’applique à tous ses profiles. Un profile activé ne peut pas contourner une machine désactivée.

Le scheduler ne déclenche pas d’occurrences pendant une période d’indisponibilité planifiée. Le reporting distingue maintenance planifiée, exécution manquée et échec. Les alertes d’absence attendue d’une machine doivent tenir compte de la maintenance sans masquer les erreurs réellement survenues.

**PROPOSITION :** la suspension n’arrête pas un job déjà actif. Les jobs en file sont revérifiés avant leur démarrage ; les reports/annulations sont audités. L’exécution manuelle pendant une suspension nécessite une dérogation explicite auditée. Valider ces règles avant implémentation.

## 3. Intervalles et timestamps

La planification automatique utilise un intervalle par client/profile, de 24 heures par défaut, et un timestamp d’ancrage stable. La configuration client peut fournir un intervalle par défaut ; un profile peut le remplacer.

Les occurrences nominales sont calculées comme anchor_timestamp + n * interval_seconds. Elles ne sont pas calculées depuis la fin du backup précédent, ce qui évite la dérive. Identité d’occurrence : agent, profile, révision de planification et timestamp nominal.

**PROPOSITION :** timestamps Unix UTC en secondes pour les heures planifiées, précision des heures d’événements documentée et mesure de durée avec horloge monotone locale. Le serveur conserve séparément les heures nominale, de début, de fin et de réception.

Les rapports convertissent les timestamps en datetime avec TZ explicitement affiché. Un intervalle de 24 heures est une durée, pas une promesse de même heure locale lors des changements d’heure. Les schedules cron et l’exemple initial sont remplacés par ce modèle d’intervalle.

Le rattrapage après indisponibilité, le jitter, le délai maximal et le comportement lors d’un changement d’ancrage restent à spécifier. **PROPOSITION :** ne rattraper au plus qu’une occurrence plutôt que rejouer tout l’historique. Une exécution manuelle ne modifie pas l’ancrage.

## 4. Pre-hooks et post-hooks

Les configurations prennent en charge des commandes avant/après l’exécution de Restic : dumps de base de données, préparation de fichiers, nettoyage de données temporaires ou autres actions. Les hooks sont dans le périmètre ; leur exclusion initiale est remplacée.

**Contrat proposé :** exécutable + args, sans shell implicite ; liste ordonnée, répertoire de travail, environnement/références de secrets, timeout et condition d’exécution. Tout shell explicite doit être autorisé localement et audité.

Séquence recommandée : lock machine -> prérequis -> pre-hooks -> backup primaire -> copies -> post-hooks -> persistance du résultat -> libération du lock. Les copies utilisent le snapshot, pas les fichiers source préparés.

**Règles de résultat validées (périmètre défini) :** un pre-hook configuré doit retourner 0 avant le démarrage du backup Restic ; sans pre-hook, le code de sortie Restic détermine la réussite du backup. Sans post-hook, le job réussit si Restic réussit. Avec un post-hook, le job réussit si le hook retourne 0 ; un post-hook échoué après un backup Restic réussi rend le job partiel. Préserver individuellement les résultats des hooks, du backup primaire et de la réplication.

Un pre-hook requis échoué empêche le backup. Un post-hook de cleanup n’est tenté après un échec antérieur que si sa condition configurée l’autorise. Le statut si backup primaire et post-hook échouent tous deux, l’agrégation de plusieurs hooks, le périmètre exact de chaque étape et les conditions restent ouverts. Une annulation ou un crash ne garantit pas le cleanup : documenter la reprise et le nettoyage manuel. La limite globale inclut les hooks ; chaque hook possède également sa propre limite.

La cohérence applicative est hors périmètre : l’opérateur est responsable de préparer des fichiers cohérents via les pre-hooks. Le produit orchestre et rend compte ; il ne certifie pas la cohérence d’une base de données.

## 5. Backup primaire et réplication

Un profile définit un repository primaire et des destinations de réplication. Après le backup, utiliser restic copy sur le snapshot spécifiquement identifié pour cette tentative, jamais une sélection « latest » ambiguë partagée entre profiles.

Conserver le snapshot primaire et les correspondances vers les snapshots copiés par destination ; ne pas supposer que les IDs sont identiques. L’agent possède les permissions et références de secrets nécessaires aux deux repositories impliqués dans chaque copy.

**Validé :** un job est partiel si le backup primaire réussit mais que la réplication échoue. Les retries de copy réutilisent le snapshot source tant qu’il est disponible ; ne pas répéter le backup uniquement parce qu’un acquittement API est perdu ou qu’une copy a échoué.

La concurrence des copies et l’agrégation des résultats avec plusieurs destinations, ou des destinations facultatives, restent ouvertes. **PROPOSITION :** seules les copies obligatoires affectent la réussite complète ; les snapshots incomplets ne sont pas répliqués par défaut sans choix explicite. Copies, durées et volumes restent visibles individuellement.

## 6. Rétention côté client

**Validé :** la rétention est configurée côté client au moyen de directives Restic, l’opérateur choisissant la policy. Un snapshot expiré qui n’a pas été répliqué est considéré comme n’étant plus valide et peut être supprimé selon la policy configurée. Les jobs `forget` et `prune` mis en cache s’exécutent lorsque le serveur est injoignable ; leurs résultats sont persistés dans l’Outbox pour livraison ultérieure.

La correspondance exacte des directives, l’isolation profile/repository, les policies primaire et réplicas, les fenêtres de maintenance, les garde-fous contre les jobs mis en cache obsolètes/remplacés et la séparation de forget/prune restent à spécifier et tester avant d’activer des opérations destructives. Aucun autre comportement de suppression destructive n’est implicitement approuvé.

## 7. Commande locale de l’agent

Un opérateur local peut déclencher un profile en dehors de la planification serveur. Exemple illustratif non implémenté : `restic-central-agent backup run --profile system`.

L’exécution utilise le même moteur, lock machine, hooks, destinations, références de secrets et Outbox. Elle n’exécute pas Restic indépendamment du service.

Identifier l’origine `local_manual`, le demandeur local, la révision, le job et la tentative. Si l’API est indisponible, utiliser la configuration locale autorisée disponible, persister le job et réconcilier à la reconnexion. IDs et événements restent idempotents.

**PROPOSITION :** communication CLI/service via IPC local avec permissions OS ; aucun port réseau entrant requis. Définir le comportement si le service est arrêté, les permissions et les dérogations de maintenance. L’exécution manuelle ne constitue pas une occurrence automatique supplémentaire.

## 8. TLS et authentification de l’agent

La communication agent/serveur utilise HTTPS/TLS avec token individuel ; mTLS est facultatif. Lorsqu’il est activé, préciser si mTLS complète le token : **PROPOSITION**, conserver le token et exiger les deux contrôles.

La vérification du certificat serveur peut être activée ou désactivée dans la configuration client. **Défaut proposé :** activée ; prendre en charge les CA personnalisées pour les infrastructures privées.

En mode non vérifié, la connexion reste chiffrée, mais l’identité serveur n’est pas correctement authentifiée : afficher des avertissements explicites localement et centralement, auditer la configuration et ne jamais rétrograder automatiquement après une erreur TLS. Ce mode expose tokens et configurations à une interception active.

Les tokens sont révocables, rotatifs, propres à chaque agent et ne sont jamais consignés dans les logs. L’authentification des opérateurs web est distincte.

## 9. Binaires Go statiques multi-OS

L’agent et le serveur sont des programmes Go statiquement compilés pour plusieurs OS. Définir une matrice GOOS/GOARCH et livrer un artefact par cible, pas un binaire universel. Aucun OS pris en charge ni build validé n’est revendiqué à ce stade.

**PROPOSITION :** privilégier les dépendances pure Go et désactiver CGO lorsque compatible ; vérifier effectivement l’absence de dépendances dynamiques sur chaque plateforme. Les dépendances DB, LDAP, TLS et IPC doivent satisfaire cet objectif.

Restic reste un exécutable distinct dont l’installation, la version et la validation doivent être définies. Statique ne signifie pas autonome : configuration, certificats, données et intégrations externes restent nécessaires. Les tests de locks, processus, chemins et services sont propres à chaque OS pris en charge.

## 10. Interface web et OpenLDAP

**Périmètre initial d’authentification validé :** utilisateurs OpenLDAP utilisant `posixAccount` avec filtre de recherche configurable, ainsi que des comptes locaux dont un superadmin local. Chaque action opérateur doit être auditée, notamment login, logout, modifications, créations et enrôlement d’agent.

La procédure exacte de recherche/bind, le base DN, le mapping de groupes facultatif, l’attribution des rôles, les exigences TLS, les sessions sécurisées, les contrôles d’autorisation, la résistance à l’altération et la rétention de l’audit restent à spécifier. Une authentification LDAP réussie n’implique pas des privilèges administrateur. La récupération du compte d’urgence et les pannes LDAP restent à traiter. Protéger les actions web contre CSRF.

## 11. Export serveur cohérent

Le serveur planifie un export cohérent de la configuration, de la base et du matériel de reprise dans un répertoire local. Il peut aussi être déclenché via l’interface web ou la CLI locale ; exemple illustratif : `restic-central-server export create`.

**Validé :** l’export PostgreSQL doit être cohérent et suffisant pour restaurer l’état complet du serveur PostgreSQL après une perte totale de la base. Coordonner le dump avec la configuration serveur et le matériel de reprise requis ; tester la restauration complète. Le backup du répertoire d’export par un autre processus est hors périmètre. L’export n’est pas un backup des repositories Restic.

**PROPOSITION :** un moteur commun aux trois origines, un lock d’export et un snapshot transactionnel ou une méthode native adaptée à la base ; ne pas copier arbitrairement des fichiers de base actifs. Capturer une révision de configuration cohérente avec la base.

Écrire dans un emplacement temporaire, produire un manifeste avec version de format, timestamp, révisions et checksums, puis publier atomiquement un export complet. Ne pas annoncer la réussite avant finalisation ; appliquer des permissions restrictives, auditer et rendre les erreurs visibles.

Documenter les secrets inclus/exclus et les références externes nécessaires à la restauration. **PROPOSITION :** planification par intervalle ; répertoire, intervalle, rétention des exports et chiffrement restent indécis. Les tests de restauration doivent couvrir configuration, identités et jobs sans rejouer les anciennes exécutions.

## 12. Dimensionnement et reporting

Cible : un an de jobs pour 300 machines clientes. Plusieurs profiles, copies, retries et événements peuvent multiplier le volume de données. Il ne s’agit pas d’une capacité mesurée.

Pour un profile quotidien par machine, base illustrative : 109500 jobs sur 365 jours, hors lancements manuels. Dimensionner en sommant les fréquences de tous les profiles ; compter séparément tentatives, résultats, hooks, logs et événements.

Définir un jeu de charge reproductible avec profiles par machine, fréquence, éventail de copies, volume d’événements et historique. Puis définir les objectifs de latence API/reporting, l’espace DB et les procédures de purge. Un an de jobs ne définit pas automatiquement la rétention détaillée des logs.

Conserver les rapports par défaut de 7 jours et les récapitulatifs de 24 heures, filtrables par machine/profile/destination. Afficher datetime et TZ, maintenance planifiée, origine automatique/manuelle, résultats des hooks et copies. Les tentatives n’augmentent pas le nombre de jobs ; la réplication n’est pas une nouvelle sauvegarde indépendante des sources.

## 13. Validation révisée et feuille de route

L’ordre de livraison validé est consigné dans la [feuille de route](08-roadmap-validation.md). Ajouter des tests pour profiles concurrents ; priorité des suspensions machine ; jobs en file suspendus ; reprise sans dérive d’ancrage ; exécution manuelle hors ligne ; échec de pre-hook et cleanup ; copy échouée sans nouveau backup ; isolation de rétention par profile ; TLS vérifié/non vérifié/CA privée/mTLS ; token révoqué ; LDAP et rôles ; export concurrent avec écritures DB et restauration ; builds et processus sur chaque OS ; charge annuelle pour 300 machines.
