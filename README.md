# restic-central

> **STATUT : IDÉE DE PROJET / PHASE DE CONCEPTION — NON PRÊT POUR LA PRODUCTION.**
> Aucun agent, serveur ou interface opérationnel n’est fourni. Les fonctionnalités décrites sont des objectifs non implémentés et non validés. Ne pas utiliser ce projet pour protéger des données réelles.

## Objectif

Concevoir un orchestrateur de sauvegardes Restic multi-machines : agents et serveur Go, binaires statiques multi-OS, API REST, supervision et interface web opérateur. Restic reste le moteur de sauvegarde ; le serveur central n’héberge pas les dépôts de sauvegarde.

## État du projet

Les décisions acceptées sont des engagements de conception, pas des fonctionnalités livrées. Les commandes, champs et endpoints restent illustratifs. Aucun résultat de test, lint, benchmark ou audit n’est revendiqué. La licence, les versions prises en charge et les modalités de distribution restent à définir.

## Documentation

### Autorité et statut

- [Spécifications révisées](docs/09-specifications-revisees.md) : référence normative actuelle pour les sujets qu’elles traitent. Elles remplacent les orientations initiales incompatibles.
- [Registre des décisions](docs/07-decisions.md) : statut des décisions (exigence, acceptée, proposée, remplacée ou ouverte) ; il ne remplace pas les spécifications détaillées. En cas d’écart, vérifier le statut dans ce registre et clarifier toute contradiction avant implémentation.
- Les documents 01–08 décrivent la conception initiale et restent utiles comme historique et contexte. Ne pas les interpréter comme exigences courantes lorsqu’ils contredisent les spécifications révisées.
- [Glossaire](docs/14-glossaire.md) : source unique des définitions des termes du domaine.
- [Modèles et relations](docs/15-modeles-relations.md) : propositions de cardinalités, relations et invariants ; ce n’est ni un schéma SQL livré ni une source alternative de définitions.
- Les documents 11–13 apportent des analyses complémentaires, sous réserve du statut indiqué dans chacun. Ils ne supplantent pas les spécifications révisées.
- [Décisions validées pour le développement](docs/16-decisions-for-development.md) : ordre de livraison et décisions de conception validées, sans présumer de leur implémentation.

### Parcours de lecture

1. [Spécifications révisées — référence normative](docs/09-specifications-revisees.md)
2. [Registre des décisions](docs/07-decisions.md) et [décisions validées pour le développement](docs/16-decisions-for-development.md)
3. [Vision initiale](docs/01-vision-exigences.md) et [architecture initiale](docs/02-architecture-modele.md)
4. Configuration/exécution, [API/fiabilité](docs/04-api-fiabilite.md), sécurité/exploitation et notifications : documents 03–06
5. [Plan de validation](docs/08-roadmap-validation.md)
6. Analyses complémentaires : documents 11–13, puis [glossaire](docs/14-glossaire.md) et [modèle conceptuel](docs/15-modeles-relations.md)

Les documents sont organisés par rôle : une définition se maintient dans le glossaire ; les documents thématiques décrivent les exigences et comportements ; le modèle conceptuel décrit les relations. Éviter de recopier une définition : ajouter plutôt un lien vers sa source canonique.

> **Note sur le document 10 :** `docs/10-options-statistiques.md` est publié, mais reste un document de conception **NON PRÊT POUR LA PRODUCTION**. Toute référence à son contenu doit être interprétée dans ce cadre.
