# Feuille de route et stratégie de validation

Statut : ordre de livraison validé par le porteur du projet le 2026-10-19 ; aucune étape n’est terminée, aucune implémentation n’est livrée et aucune échéance n’est garantie. Les décisions sont consignées dans le [registre des décisions](07-decisions.md) et les [décisions validées pour le développement](16-decisions-for-development.md). Chaque étape possède ses propres tests et critères d’acceptation. Le projet reste en conception et **NON PRÊT POUR LA PRODUCTION** jusqu’à son implémentation et sa qualification explicite.

## Ordre de livraison

1. **Agent autonome :** configuration fournie manuellement, hooks, exécution via system crontab ou systemd timer, et enregistrement durable des états de jobs dans l’Outbox. Aucun enrôlement auprès du serveur n’est requis pour cette étape.
2. **Enrôlement serveur :** implémenter la gestion de l’enrôlement des agents côté serveur.
3. **Enrôlement agent :** ajouter la gestion de l’enrôlement côté agent.
4. **Reporting serveur des jobs :** implémenter la réception et la persistance des informations de jobs côté serveur.
5. **Reporting agent des jobs :** ajouter l’envoi des informations de jobs par l’agent via l’Outbox.
6. **Configuration des agents côté serveur :** implémenter la gestion et la distribution de configuration côté serveur.
7. **Auto-configuration de l’agent :** récupérer et appliquer la configuration depuis l’endpoint dédié.
8. **Planification serveur :** implémenter la planification gérée par le serveur et l’affectation future des BackupJobs.

« Autonome » à l’étape 1 désigne une exécution configurée localement via le timer/crontab du système d’exploitation ; cela n’approuve pas un mode de planification autonome distinct dans le système enrôlé. Les hooks sont inclus dès l’étape 1. Les jobs de rétention ne doivent pas être activés avant que leurs garde-fous contre les opérations destructives et leurs tests d’acceptation soient satisfaits.

## Critères de sortie des étapes

Chaque étape doit définir et réussir ses propres tests avant que l’intégration suivante soit considérée comme achevée. Au minimum :

- **1 — Agent :** validation de configuration ; l’échec d’un pre-hook empêche Restic ; agrégation des codes de sortie Restic/post-hook selon les règles validées ; résultats partiels en cas de réplication échouée ou de post-hook échoué après un backup réussi ; lock machine ; invocation timer/crontab ; durabilité de l’Outbox après redémarrage et panne serveur ; absence de fuite de secrets.
- **2–3 — Enrôlement :** authentification, liaison d’identité, comportement en cas de doublon/réenrôlement, révocation/remplacement et tests d’échec/retry côté serveur et agent.
- **4–5 — Reporting :** validation des contrats versionnés, livraison idempotente at-least-once, événements doublonnés/hors ordre, persistance transactionnelle avant accusé de réception, mise en file hors ligne et réconciliation à la reconnexion.
- **6–7 — Configuration :** validation des schémas JSON versionnés, révisions de configuration immuables, autorisation de l’endpoint, gestion des schémas compatibles/non pris en charge, persistance sûre sans secrets et comportement de redémarrage/rechargement de l’agent.
- **8 — Planification :** identité stable des occurrences, remplacement d’un job planifié expiré et non récupéré, sérialisation à l’échelle de la machine, remontée de l’annulation lorsqu’un autre backup est en cours, comportement hors ligne/reconnexion et limites de timestamps/fuseaux horaires.

Avant de déclarer le système prêt à l’exploitation, tester aussi `forget`/`prune` hors ligne avec livraison Outbox, l’isolation de la rétention et les garde-fous contre les jobs obsolètes, les statuts partiels de réplication et post-hook échoués, la restauration complète d’un export PostgreSQL, la recherche OpenLDAP `posixAccount` et le superadmin local, l’audit complet des opérateurs, les builds pour les OS/architectures pris en charge et les scénarios de reprise. Ne pas revendiquer l’aptitude à la production sur la seule base de l’achèvement des étapes.

## Stratégie de tests transversale

- **Unitaires :** validation de configuration et de schéma, compilation des arguments Restic, traduction des codes de sortie, conditions d’exécution des hooks, agrégation des résultats, transitions d’état, identité des occurrences, correspondance de rétention et calculs de temps.
- **Contrat :** authentification/autorisation, compatibilité des versions et versions non prises en charge, idempotence, pagination le cas échéant, payloads invalides ou trop volumineux, champs inconnus et événements hors ordre.
- **Intégration :** véritable binaire Restic et repository jetable ; backup, exécution des hooks, copy, check, forget/prune et restore. Utiliser uniquement des données synthétiques.
- **Résilience :** panne API après la fin de Restic, crash avant/après acquittement, doublons, disque plein, redémarrage agent, jobs planifiés obsolètes, secrets indisponibles, credentials expirés/révoqués et résultats tardifs.
- **Concurrence :** requêtes simultanées, plusieurs profiles avec lock à l’échelle de la machine, redémarrage pendant un backup, plusieurs workers scheduler et maintenance concurrente.
- **Sécurité :** fuite de secrets, permissions filesystem, injection sûre des secrets, chemins/URLs non autorisés, limites de payload, rotation/révocation des tokens, contrôle des rôles LDAP/locaux, couverture d’audit et isolation inter-agents.
- **Base/export :** compatibilité des migrations, écritures concurrentes pendant l’export, dump complet et récupération de configuration après perte totale de la base, restauration sans rejouer les jobs historiques.

## Contrôles qualité opérationnels

Pour Go : formatage, `go vet`, tests, race detector et linting configuré. Pour tout Bash ajouté : ShellCheck. Pour la documentation : Markdown lint, validation des schémas JSON, vérification des liens relatifs et détection de secrets. La CI doit exécuter les contrôles applicables ; aucun résultat de test ou lint n’est actuellement revendiqué.

La qualification de production exige aussi une revue de sécurité, la compatibilité des contrats/versions, des migrations et procédures de rollback documentées, des tests de restore, l’observabilité, une installation reproductible, des procédures opérateur/incidents et une décision explicite d’aptitude à la production.
