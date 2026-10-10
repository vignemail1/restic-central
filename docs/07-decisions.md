# Registre des décisions

Statut initial : 2026-10-10.

EXIGENCE signifie exprimé par le porteur du projet. PROPOSÉ signifie orientation recommandée, non encore validée. OUVERT signifie arbitrage nécessaire. Une approbation de publication ne transforme pas les propositions en décisions acceptées.

| ID | Statut | Sujet et orientation |
|---|---|---|
| E01 | EXIGENCE | Restic est le moteur ; architecture client et serveur REST. |
| E02 | EXIGENCE | Serveur chargé de la planification et des remontées. |
| E03 | EXIGENCE | Plusieurs dépôts, sources et exclusions configurables. |
| E04 | EXIGENCE | Verrou client empêchant deux sauvegardes simultanées. |
| E05 | EXIGENCE | Délai configurable signalant un job à vérifier manuellement. |
| E06 | EXIGENCE | Notifications multicanaux ; fenêtre d'erreurs 24 h par défaut. |
| E07 | EXIGENCE | Rapports durée/volumétrie sur 7 jours par défaut. |
| E08 | EXIGENCE | Documentation seule ; avertissement non-production visible. |
| P01 | PROPOSÉ | Scheduler serveur seul au MVP ; pas de déclenchement local indépendant. |
| P02 | PROPOSÉ | Polling HTTPS sortant des agents ; pas de port entrant obligatoire. |
| P03 | PROPOSÉ | Configurations immuables versionnées attachées aux jobs. |
| P04 | PROPOSÉ | Secrets de dépôt résolus sur agents ; notifications sur serveur. |
| P05 | PROPOSÉ | Outbox locale persistante, livraison au moins une fois et déduplication. |
| P06 | PROPOSÉ | Jobs, tentatives et résultats par destination séparés. |
| P07 | PROPOSÉ | Backups indépendants séquentiels ; succès si tous les dépôts obligatoires réussissent. |
| P08 | PROPOSÉ | État partial distinct ; observation réseau séparée de l'exécution. |
| P09 | PROPOSÉ | Timeout : alerte et vérification manuelle, sans arrêt forcé par défaut. |
| P10 | PROPOSÉ | Aucun unlock automatique sur simple dépassement de délai. |
| P11 | PROPOSÉ | Agent et serveur en Go ; Linux initial, macOS à valider. |
| P12 | PROPOSÉ | Pas de hooks arbitraires, HA ou restauration distante au MVP. |
| P13 | PROPOSÉ | Incidents immédiats, synthèse quotidienne et notification de rétablissement. |
| P14 | PROPOSÉ | Rapport par échéance, retries séparés, métriques absentes explicitement indisponibles. |

## Raisons et conséquences

P01/P02 simplifient l'autorité de déclenchement et le réseau, mais une panne serveur empêche les nouveaux départs. Un mode autonome nécessite un nouveau protocole explicite.

P03/P06 garantissent une lecture historique cohérente, mais demandent un modèle de données et des migrations rigoureux.

P04 réduit la centralisation des secrets ; ne protège pas contre une configuration malveillante issue d'un serveur compromis. Ajouter contrôles locaux et audit.

P05 évite la perte de résultat pendant une coupure ; impose quotas, reprise et déduplication. Pas de garantie exactement une fois pour toutes les opérations.

P07 réduit la concurrence mais augmente la durée globale et ne garantit pas une vue source identique entre destinations. Backup puis copy reste une évolution.

P08/P09 évitent de confondre absence de réseau et blocage ; exigent réconciliation et interventions explicites.

## Arbitrages ouverts

- O01 : moteur de base serveur et stockage local agent.
- O02 : authentification mTLS ou tokens ; enrôlement et rotation.
- O03 : version minimale de Restic et matrice de compatibilité.
- O04 : limites de dimensionnement et objectifs RPO/RTO du serveur.
- O05 : grammaire de planification, DST, rattrapage et valeurs de délais.
- O06 : règle exacte d'agrégation des résultats facultatifs et incomplets.
- O07 : cohérence applicative, hooks et tests de restauration.
- O08 : rétention des snapshots, événements, audit et logs.
- O09 : interface web, export et canal initial de notification.
- O10 : licence, packaging, distribution et mise à jour.
- O11 : mode autonome et stratégie de réplication par copy.

## Procédure de décision

Pour accepter une orientation, enregistrer date, responsable, contexte, alternatives, décision et conséquences. Conserver l'historique ; une décision remplacée est marquée superseded, pas supprimée. Utiliser ultérieurement des ADR séparés si nécessaire.
