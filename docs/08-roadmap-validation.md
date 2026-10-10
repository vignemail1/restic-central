# Roadmap et stratégie de validation

Statut : plan proposé, aucun jalon réalisé ou délai garanti.

## Phase 0 — conception

Valider les orientations du registre ; résoudre authentification, persistance, planification et compatibilité Restic. Produire schéma de configuration, contrat OpenAPI et table de transitions testable.

Critère de sortie : ambiguïtés critiques traitées, périmètre MVP accepté, critères de tests définis.

## Phase 1 — moteur agent

Configuration validée, références de secrets, préconditions, lancement Restic, verrou, parsing JSON, résultats par destination et journal local. Tester avec dépôts et données synthétiques uniquement.

## Phase 2 — coordination

Identités agents, politiques versionnées, scheduler, acquisition transactionnelle, heartbeat, outbox et réconciliation. Empêcher les doublons sans promettre une exécution exactement une fois en toutes circonstances.

## Phase 3 — supervision

Incidents, dépassements de délais, échéances manquées, premier provider de notification, synthèse 24 h, rapport 7 jours et tableau de bord minimal.

## Phase 4 — durcissement expérimental

Audit, tests de panne, limites de ressources, sauvegarde du serveur, documentation opérateur, packaging et matrice de compatibilité. Cette phase ne suffit pas à annoncer production-ready sans revue explicite.

## Évolutions

Autres providers, mode autonome, réplication copy, maintenance contrôlée, tests de restauration, macOS validé, authentification administrateur avancée et éventuelle HA. Chaque évolution nécessite son analyse de risques.

## Stratégie de tests

- Unitaires : validation, compilation des arguments, traduction des codes, agrégation, transitions, calcul de fenêtres et planification avec changements d'heure.
- Contrat : authentification, autorisations, idempotence, pagination, payloads invalides et événements hors ordre.
- Intégration : binaire Restic réel et dépôt jetable ; backup, résultat incomplet, restauration et check.
- Résilience : coupure API après fin Restic, crash avant/après acquittement, doublons, disque plein, agent redémarré, réservation expirée et résultat tardif.
- Concurrence : deux demandes simultanées, redémarrage pendant backup, plusieurs workers scheduler et maintenance concurrente.
- Sécurité : fuite de secrets, chemins et URLs non autorisés, taille de payload, rotation/révocation et agent tentant d'accéder aux jobs d'un autre.
- Notifications : déduplication, rétablissement, canal indisponible, retries et synthèses incluant les anciens incidents ouverts.

## Critères d'acceptation prioritaires

1. Deux demandes simultanées ne lancent pas deux sauvegardes via le même agent.
2. Une sauvegarde finie avec API indisponible transmet son résultat après reconnexion sans refaire le backup.
3. Un résultat incomplet n'est jamais présenté comme succès complet.
4. Une échéance jamais démarrée est visible comme anomalie.
5. Un agent injoignable n'est pas automatiquement déclaré processus bloqué.
6. Chaque destination a un résultat et une métrique identifiables.
7. Une configuration modifiée ne change pas l'historique des jobs existants.
8. Les retries n'augmentent pas artificiellement le nombre de jobs réussis.
9. Une restauration de test vérifie le contenu attendu.
10. Aucun secret réel ne paraît dans logs, rapports, commit ou notifications.

## Qualité envisagée

Pour Go : formatage, go vet, tests, détecteur de races et lint configuré. Pour Bash éventuellement ajouté : ShellCheck. Pour la documentation : lint Markdown, validation YAML des exemples selon leur statut, contrôle des liens relatifs et détection de secrets. La CI devra exécuter ces contrôles ; aucun résultat de lint n'est revendiqué actuellement.

## Passage éventuel en production

Exiger revue de sécurité, versionnement des contrats, compatibilité testée, migrations et rollback documentés, restaurations testées, observabilité, installation reproductible et procédures d'incident. La qualification production doit faire l'objet d'une décision explicite, jamais découler automatiquement de la présence de documentation.
