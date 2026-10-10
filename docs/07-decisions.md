# Registre des décisions

Révision : 2026-10-10, après validation du porteur du projet. Projet en conception, non prêt pour la production.

EXIGENCE : demandée par le porteur. ACCEPTÉ : explicitement validé. PROPOSÉ : non validé. REMPLACÉ : orientation initiale devenue incompatible. OUVERT : arbitrage restant.

Les détails normatifs révisés figurent dans [les spécifications révisées](09-specifications-revisees.md).

## Exigences

E01 à E08 restent applicables : Restic, agents/serveur REST, planification serveur, destinations et filesets, verrou local, signalement des jobs à vérifier, notifications 24 h, reporting 7 jours et avertissement non-production.

Nouvelles exigences : plusieurs profils par machine ; suspension/désactivation machine et profil ; pre/post-hooks ; vérification TLS configurable ; Go statique multi-OS ; lancement manuel local ; interface web avec OpenLDAP et rôles ; export serveur cohérent local ; rétention des snapshots configurée côté client ; réplication primaire puis copy.

## Orientations P

| ID | Statut | Décision |
|---|---|---|
| P01 | PROPOSÉ, AMENDÉ | Serveur autorité des échéances automatiques ; lancement manuel local explicitement autorisé. Mode autonome automatique non décidé. |
| P02 | ACCEPTÉ | Polling HTTPS sortant ; aucun port réseau entrant obligatoire sur l'agent. |
| P03 | ACCEPTÉ | Configurations immuables versionnées rattachées aux jobs. |
| P04 | PROPOSÉ | Secrets de dépôt résolus sur agent ; secrets de notifications sur serveur. |
| P05 | ACCEPTÉ | Outbox persistante, livraison au moins une fois et déduplication. |
| P06 | ACCEPTÉ | Séparer jobs, tentatives et résultats par destination. |
| P07 | REMPLACÉ | Backup primaire puis réplication par copy, plutôt que backups indépendants. Règle globale de succès encore à préciser. |
| P08 | PROPOSÉ | État partial distinct ; état d'observation distinct de l'exécution. |
| P09 | ACCEPTÉ | Dépassement de délai : alerte et vérification, sans arrêt forcé par défaut. |
| P10 | PROPOSÉ | Pas d'unlock automatique sur simple timeout. |
| P11 | ACCEPTÉ, ÉTENDU | Agent et serveur en Go, compilation statique et multi-OS ; anciennes restrictions Linux seul remplacées. |
| P12 | PARTIELLEMENT REMPLACÉ | Hooks désormais dans le périmètre. HA et restauration distante restent hors MVP proposé. |
| P13 | ACCEPTÉ | Incidents immédiats, synthèse quotidienne et notification de rétablissement. |
| P14 | PROPOSÉ | Rapports par échéance, retries séparés et métriques absentes signalées. |

## Arbitrages O

| ID | Statut | Décision ou question restante |
|---|---|---|
| O01 | OUVERT | Moteur de stockage serveur et persistance locale. |
| O02 | ACCEPTÉ | HTTPS/TLS avec token individuel ; mTLS optionnel. |
| O03 | OUVERT | Version minimale Restic et matrice de compatibilité. |
| O04 | ACCEPTÉ POUR LA CIBLE | Un an de jobs pour 300 machines ; profils, tentatives, événements et charges à dimensionner. RPO/RTO du serveur restent ouverts. |
| O05 | ACCEPTÉ POUR LA PLANIFICATION | Intervalles réguliers, 24 h par défaut, ancre timestamp stable ; affichage datetime avec TZ. Politique exacte de rattrapage reste à décider. |
| O06 | OUVERT | Agrégation primaire/copies, destinations facultatives et résultats incomplets. |
| O07 | ACCEPTÉ | Cohérence applicative hors scope ; hooks peuvent préparer des fichiers cohérents sans garantie applicative du produit. |
| O08 | ACCEPTÉ POUR LES SNAPSHOTS | Rétention des snapshots configurée côté client. Rétention détaillée des logs/événements/audit reste ouverte. |
| O09 | ACCEPTÉ POUR LE PÉRIMÈTRE | Web opérateur, OpenLDAP possible, rôles applicatifs ; export cohérent local planifié ou manuel web/CLI. Stack UI et premier provider restent ouverts. |
| O10 | OUVERT | Licence, distribution et mise à jour ; obligation Go statique multi-OS actée. |
| O11 | ACCEPTÉ POUR LA RÉPLICATION | Backup primaire puis copy ; mode autonome automatique toujours ouvert. |

## Historique et conséquences

Les validations P02, P03, P05, P06, P09, P11 et P13 proviennent explicitement du porteur du projet. Les autres propositions ne deviennent pas acceptées par simple publication.

Les hooks augmentent les privilèges et la surface d'exécution : prévoir commandes structurées, restrictions locales, délais et audit. Le mode TLS non vérifié est possible mais doit être clairement identifié comme dégradé. Le lancement local impose le même moteur de verrouillage et une réconciliation idempotente avec le serveur.

Une panne serveur bloque les nouveaux déclenchements centralisés mais ne doit pas empêcher un lancement manuel local sur configuration disponible. Une erreur de copy ne doit pas provoquer inutilement une nouvelle lecture des sources.

Toute décision ultérieure doit indiquer contexte, alternatives, responsable, date et conséquences ; conserver les décisions remplacées.
