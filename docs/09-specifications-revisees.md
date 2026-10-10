# Spécifications révisées

Révision : 2026-10-10. Statut : conception uniquement, NON PRÊT POUR LA PRODUCTION.

Ce document complète la conception initiale et fait autorité en cas de contradiction sur les sujets ci-dessous. Aucun comportement n'est implémenté. Les exigences viennent du porteur du projet ; les précisions marquées PROPOSITION restent à valider.

## 1. Profils et filesets

Une machine possède plusieurs profils de sauvegarde. Chaque profil a un identifiant stable, sa configuration versionnée, son fileset include/exclude, ses destinations, hooks, intervalle et règles de rétention.

Le modèle devient Agent -> BackupProfile -> ConfigRevision -> Job -> Attempt -> DestinationResult. BackupProfile précise la notion initiale BackupPolicy ; la mutualisation de modèles de politique reste possible sans confondre profil exécuté et modèle partagé.

Chaque événement et rapport identifie machine et profil. Le verrou exigé reste global à la machine : deux profils ne doivent pas exécuter simultanément leurs sauvegardes via l'agent. Un chevauchement est mis en attente ou signalé selon une politique à définir, jamais ignoré silencieusement.

## 2. Activation, suspension et maintenance

La programmation d'une machine ou d'un profil peut être désactivée ou suspendue.

PROPOSITION : disabled est un arrêt sans échéance de reprise ; suspended est une suspension avec début, fin optionnelle, motif et auteur. Une suspension machine s'applique à tous ses profils. Un profil activé ne contourne pas une désactivation machine.

Le scheduler ne déclenche pas les occurrences comprises dans l'arrêt prévu. Le reporting distingue maintenance planifiée, exécution manquée et échec. Les alertes d'absence attendue de la machine doivent tenir compte de sa maintenance sans masquer les erreurs réellement survenues.

PROPOSITION : une suspension ne tue pas un job déjà actif. Les jobs en file sont revérifiés avant démarrage et leurs reports/annulations sont audités. Un lancement manuel pendant suspension demande un override explicite tracé. Ces règles doivent être validées avant implémentation.

## 3. Intervalles et timestamps

La programmation automatique utilise un intervalle par client/profil, 24 h par défaut, et une ancre timestamp stable. La configuration client peut fournir l'intervalle par défaut ; un profil peut le surcharger.

Les occurrences nominales sont anchor_timestamp + n * interval_seconds. Elles ne sont pas calculées depuis la fin du dernier backup, afin d'éviter la dérive. Identité d'occurrence : agent, profil, révision de programmation et timestamp nominal.

PROPOSITION : timestamps Unix UTC en secondes pour les échéances, dates d'événements avec précision documentée ; durées mesurées avec une horloge monotone locale. Le serveur conserve timestamp nominal, démarrage, fin et réception séparément.

Les rapports convertissent les timestamps en datetime avec TZ explicitement affichée. L'intervalle de 24 h est une durée, pas une promesse de même heure locale lors d'un changement d'heure. Les programmations cron et leur exemple initial sont remplacés par ce modèle d'intervalle.

Rattrapage après panne, jitter, retard maximal et comportement lors d'une modification d'ancre restent à spécifier. PROPOSITION : au plus une occurrence rattrapée, sans rejouer toute l'accumulation. Un lancement manuel ne modifie pas l'ancre.

## 4. Pre-hooks et post-hooks

Les configurations permettent des commandes avant/après le lancement de Restic : dump de bases, préparation de fichiers, nettoyage temporaire ou autres actions. Les hooks font partie du périmètre ; leur exclusion initiale est remplacée.

PROPOSITION de contrat : commandes sous forme executable + args, sans shell implicite ; liste ordonnée, répertoire de travail, références d'environnement/secret, timeout et condition d'exécution. Un shell explicite éventuel doit être autorisé localement et audité.

Séquence recommandée : verrou machine -> préconditions -> pre-hooks -> backup primaire -> copies -> post-hooks -> persistance du résultat -> libération du verrou. Les copies consomment le snapshot, pas les fichiers préparés.

PROPOSITION : un pre-hook requis en échec empêche le backup ; le post-hook de nettoyage est tenté même en cas d'erreur précédente, s'il est configuré pour cela. Les échecs de hooks sont conservés séparément du résultat Restic. Un échec de nettoyage peut rendre le job dégradé sans effacer un snapshot réussi.

La portée exacte before/after par étape, les conditions always/on_success/on_failure et la table d'agrégation restent à ratifier. L'annulation ou le crash ne garantit pas l'exécution d'un cleanup : documenter une reprise et un nettoyage manuel. Le délai global inclut les hooks ; chaque hook a aussi son délai propre.

La cohérence applicative est hors scope : l'opérateur est responsable de préparer des fichiers cohérents via le pre-hook. Le produit orchestre et rapporte ; il ne certifie pas la cohérence d'une base de données.

## 5. Backup primaire et réplication

Un profil définit un repository primaire puis des destinations de réplication. Après le backup, utiliser restic copy sur le snapshot précisément identifié pour cette tentative, jamais une sélection ambiguë de type latest partagée entre profils.

Conserver le snapshot primaire et la correspondance des snapshots copiés par destination ; ne pas supposer des IDs identiques. L'agent dispose des droits et références de secrets nécessaires aux deux dépôts de chaque copy.

Une erreur de réplication est distincte d'une erreur du backup primaire. Les retries de copies réutilisent le snapshot source encore disponible ; ne pas refaire le backup pour la seule perte d'un accusé API ou l'échec d'une copy.

La concurrence des copies et la règle globale de succès restent ouvertes. PROPOSITION : seules les copies requises influencent le succès complet ; snapshots incomplets non répliqués par défaut sans choix explicite. Les copies, leur durée et leur volumétrie restent visibles individuellement.

## 6. Rétention côté client

La rétention des snapshots est définie dans la configuration client, avec paramètres par profil/dépôt si nécessaire. Le format et les valeurs par défaut restent ouverts.

Définir les sélections par machine/profil pour éviter qu'un forget touche les snapshots d'un autre profil sur un dépôt partagé. Préciser politiques du primaire et des réplicas, fenêtres de maintenance et séparation forget/prune.

PROPOSITION : ne pas supprimer le snapshot primaire d'une réplication requise encore en attente sans politique explicite d'expiration et incident. Les verrous et opérations de maintenance sont coordonnés. Aucune suppression destructive automatique n'est implicite dans cette spécification.

## 7. Commande locale agent

Un opérateur local peut déclencher un profil en dehors du scheduler serveur. Exemple indicatif, non implémenté : restic-central-agent backup run --profile system.

Le lancement passe par le même moteur, le même verrou machine, les mêmes hooks, destinations, références de secrets et outbox. Il ne lance pas un Restic indépendant du service.

Identifier origin=local_manual, demandeur local, révision, job et tentative. Si l'API est indisponible, utiliser une configuration locale disponible et autorisée, persister le job puis réconcilier au reconnect. Les IDs et événements restent idempotents.

PROPOSITION : communication CLI/service via IPC local avec permissions OS ; pas de port réseau entrant nécessaire. Définir comportement lorsque le service est arrêté, autorisations et override maintenance. Un lancement manuel n'est pas compté comme une échéance automatique supplémentaire.

## 8. TLS et authentification agent

La communication agent/serveur utilise HTTPS/TLS avec token individuel ; mTLS est optionnel. Lorsqu'activé, préciser si mTLS s'ajoute au token : PROPOSITION, conserver le token et exiger les deux contrôles.

La vérification du certificat serveur peut être activée ou désactivée dans la configuration client. PROPOSITION de défaut : activée ; permettre CA personnalisée pour les infrastructures privées.

En mode non vérifié, la connexion reste chiffrée mais l'identité du serveur n'est pas correctement authentifiée : afficher un avertissement explicite local et central, auditer la configuration et ne jamais rétrograder automatiquement après une erreur TLS. Ce mode expose notamment le token et les configurations à une interception active.

Les tokens sont révocables, rotatifs, propres à chaque agent, non journalisés. L'authentification des opérateurs web est distincte.

## 9. Go statique et multi-OS

Agent et serveur sont des programmes Go compilés statiques et multi-OS. Définir une matrice GOOS/GOARCH et livrer un artefact par cible, pas un binaire universel. Aucun support OS précis ni build validé n'est revendiqué à ce stade.

PROPOSITION : privilégier dépendances pure Go et CGO désactivé quand compatible ; vérifier effectivement l'absence de dépendances dynamiques selon la plateforme. Les dépendances DB, LDAP, TLS et IPC devront respecter cet objectif.

Restic reste un exécutable distinct dont l'installation/version/validation doit être définie. Statique ne signifie pas autosuffisant : configuration, certificats, données et intégrations externes restent nécessaires. Les tests de verrous, processus, chemins et services sont propres à chaque OS supporté.

## 10. Interface web et OpenLDAP

Une interface web permet aux opérateurs de consulter état, incidents et reporting machine/profil/job, ainsi que de déclencher l'export serveur. L'authentification OpenLDAP doit être possible et les rôles sont gérés dans l'application serveur.

Définir recherche d'utilisateur, bind, base DN, filtres, éventuel mapping de groupes et attribution des rôles. PROPOSITION : LDAP protégé par TLS, compte de recherche aux droits minimaux, sessions web sécurisées et contrôle d'autorisation serveur pour chaque action.

Ne pas assimiler connexion LDAP réussie à un rôle administrateur. Auditer suspensions, modifications, exports et actions privilégiées ; protéger les actions web contre CSRF. Gestion des comptes d'urgence et panne LDAP restent à arbitrer.

## 11. Export cohérent du serveur

Le serveur planifie un export cohérent de sa configuration, de sa DB et des éléments nécessaires à la reprise dans un dossier local. Il peut aussi être déclenché par interface web ou CLI locale, exemple indicatif : restic-central-server export create.

La sauvegarde de ce dossier par un autre processus est hors scope. L'export n'est pas la sauvegarde des dépôts Restic.

PROPOSITION : même moteur pour trois origines, verrou d'export, snapshot transactionnel ou méthode native adaptée à la DB ; ne pas copier à chaud arbitrairement ses fichiers. Capturer une révision cohérente de configuration avec la DB.

Écrire dans un emplacement temporaire, produire un manifeste avec version de format, date, révisions et checksums, puis publier atomiquement un export complet. Ne pas annoncer succès avant finalisation ; permissions restrictives, audit et échec visible.

Documenter secrets inclus/exclus et références externes nécessaires à la restauration. PROPOSITION : déclenchement planifié par intervalle ; chemin, intervalle, rétention d'exports et chiffrement à décider. Un test de restauration devra couvrir configuration, identités et jobs sans rejouer des exécutions anciennes.

## 12. Dimensionnement et reporting

Objectif : gérer un an de jobs pour 300 machines clientes. Plusieurs profils, copies, retries et événements peuvent multiplier le volume. Ce n'est pas une capacité mesurée.

Pour un profil quotidien par machine, base indicative : 109500 jobs sur 365 jours, hors lancements manuels. Dimensionner avec la somme des fréquences de tous les profils ; tentatives, résultats, hooks, logs et événements sont comptés séparément.

Fixer un jeu de charge reproductible avec profils par machine, fréquence, fan-out de copies, volume d'événements et historique. Définir ensuite objectifs de latence API/reporting, espace DB et procédure de purge. Un an de jobs ne fixe pas automatiquement la rétention des logs détaillés.

Conserver les rapports 7 jours et synthèses 24 h par défaut, filtrables par machine/profil/destination. Afficher datetime et TZ, maintenance planifiée, origine automatique/manuelle, résultats de hooks et copies. Les tentatives ne gonflent pas le nombre de jobs ; la réplication ne constitue pas une nouvelle sauvegarde source indépendante.

## 13. Validation et roadmap révisées

Ajouter aux tests prévus : deux profils concurrents ; suspension machine prioritaire ; jobs en file suspendus ; reprise sans dérive d'ancre ; lancement manuel hors ligne ; pre-hook échoué et cleanup ; copy échouée sans nouveau backup ; rétention isolée par profil ; TLS vérifié/non vérifié/CA privée/mTLS ; token révoqué ; LDAP et rôles ; export concurrent avec écritures DB et restauration ; builds et processus sur chaque OS ; charge annuelle 300 machines.

La roadmap initiale doit désormais inclure hooks, réplication, commande locale, rôles web et export cohérent. Leur ordre de livraison reste à décider ; leur inclusion ne signifie pas qu'ils sont disponibles.
