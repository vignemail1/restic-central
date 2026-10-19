# Décision : isolation des repositories par machine

Date : 2026-10-10. Statut : EXIGENCE exprimée par le porteur du projet.

> Projet en conception — NON PRÊT POUR LA PRODUCTION. Aucun contrôle d’isolation ou procédure de restauration n’est implémenté ou validé.

## 1. Principe

Un repository appartient exclusivement à une machine cliente. Il ne contient pas les sauvegardes de plusieurs machines. Une machine ne doit pas accéder aux dépôts d’une autre machine.

Cette exigence remplace les hypothèses antérieures de repositories partagés entre machines dans les documents de conception. Elle vaut pour les repositories primaires et pour les destinations de réplication par copy.

Une machine peut posséder plusieurs repositories. **PROPOSITION :** plusieurs profiles de cette même machine peuvent utiliser son repository ou des repositories distincts ; cela ne constitue pas un partage inter-machines. La séparation des profiles dans un même dépôt reste une séparation fonctionnelle, pas une frontière de sécurité indépendante.

## 2. Propriété et autorisations

Associer chaque Repository à un owner_machine_id stable. Tous les profiles et jobs qui le ciblent doivent appartenir à cette machine. Une copy ne peut relier que des repositories du même propriétaire. Rejeter une configuration ou un job qui enfreint cette règle.

Ne pas utiliser le hostname seul comme identité de propriété : prévoir une identité machine stable et une procédure explicite de remplacement de machine ou de réenrôlement.

Les credentials de stockage et secrets de chiffrement ne sont pas partagés entre machines. **PROPOSITION :** secrets distincts par repository, références locales et rotation documentée. Ne pas distribuer de credentials globaux donnant accès à tous les dépôts.

L’isolation doit être appliquée côté stockage par des permissions appropriées, pas seulement par convention de nommage ou préfixe. Les identités de stockage d’une machine doivent être refusées sur les dépôts des autres, même si leurs emplacements sont connus. La définition exacte des ACL dépend du backend et sera testée.

Le serveur central conserve les métadonnées et relations de propriété. **PROPOSITION :** par défaut, il ne conserve pas les secrets permettant de lire ou restaurer tous les dépôts. Toute conservation centrale nécessiterait une décision de sécurité distincte.

## 3. Maintenance

**PROPOSITION :** l’agent propriétaire exécute backup, copy, forget, prune, check et stats sur ses repositories. Aucun agent de maintenance central avec accès global n’est prévu par défaut.

Le serveur coordonne les échéances et opérations par repository_id ; le lock local machine reste applicable. Les opérations de plusieurs profiles d’une même machine pouvant cibler un dépôt, la maintenance doit être coordonnée avec leurs backups et copies. Les locks natifs Restic restent nécessaires, notamment lors d’un lancement local.

La rétention reste configurée côté client. Si plusieurs profiles partagent un dépôt de cette machine, les sélections de snapshots doivent préserver leurs policies respectives. Chaque replica possède sa propre maintenance et ses propres résultats.

Si la machine propriétaire est arrêtée ou en maintenance planifiée, différer les opérations selon une policy explicite et afficher l’ancienneté des contrôles. Un exécuteur de remplacement demande une autorisation de récupération limitée à cette machine ; aucun basculement automatique avec credentials globaux.

## 4. Restauration

**EXIGENCE :** les restaurations sont effectuées depuis le repository de la machine concernée avec ses credentials.

Documenter les éléments de récupération : emplacement et backend, credentials d’accès au stockage, secret de déchiffrement Restic, éventuels certificats/CA et références du dépôt. Le token REST de reporting de l’agent n’est pas un credential de restauration du repository.

**PROPOSITION :** rendre ces éléments récupérables via un coffre ou une procédure indépendante de la machine sauvegardée ; ne pas en conserver l’unique copie sur la machine qui peut être perdue. L’emplacement du coffre et sa gestion restent à décider.

Une machine ou un environnement de restauration autorisé peut recevoir temporairement les credentials de la machine sinistrée. Cette exception est explicite, limitée et auditée ; elle ne donne pas un accès permanent aux dépôts d’autres machines.

La restauration pilotée par restic-central reste hors MVP proposé. Documenter une procédure opérateur et tester la récupération depuis une machine neuve, sans dépendre de la disponibilité du serveur central.

## 5. Reporting et validations

Les statistiques et opérations de chaque repository sont rattachées à son propriétaire. Les profiles restent identifiés séparément. Les dépôts primaires et répliqués sont distingués pour éviter de présenter leurs volumes comme des données source différentes.

Tester : rejet des configurations inter-machines, copy vers un dépôt d’un autre propriétaire, refus des credentials A sur le dépôt B, droits de maintenance, rotation, suppression/réenrôlement d’agent, remplacement de machine et restauration après perte complète du client.

## 6. Questions restantes

Repositories par profile ou mutualisés entre profiles d’une même machine ; provisioning des ACL selon backend ; coffre de récupération ; rotation des secrets ; transferts de propriété ; procédures de remplacement d’agent ; exécution de maintenance pendant une indisponibilité prolongée.

Cette publication ne valide ni ne publie automatiquement les amendements encore en attente, notamment les options Restic/statistiques et le processus détaillé de maintenance.
