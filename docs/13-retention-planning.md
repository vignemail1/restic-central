# Rétention et planification mises en cache par les clients

Date : 2026-10-10. Projet en conception — NON PRÊT POUR LA PRODUCTION.

Ce document complète les décisions existantes et remplace les dispositions incompatibles sur le déclenchement. **EXIGENCE** reprend la demande du porteur ; **PROPOSITION** identifie les précisions restant à valider.

## 1. Règles de conservation et déclencheurs

**EXIGENCE :** la purge est un type de job. Deux critères de conservation sont proposés : `keep-last=X` conserve les X derniers jobs réussis ; `keep-after=DATE_SPEC` conserve les snapshots réussis après la date indiquée. DATE_SPEC accepte une date/heure absolue complète ou une durée relative, par exemple `8w` = `now` moins huit semaines.

Ces critères définissent ce qui doit être conservé ; ils ne définissent pas quand le job `forget` démarre. La planification du job `forget` doit donc être configurée séparément : intervalle ou heure quotidienne, et éventuellement déclenchement manuel. Une dépendance après backup/copy est