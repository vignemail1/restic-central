# Contrats JSON v1

## Organisation et source de vérité

- `schemas/v1/<message>.schema.json` : un point d'entrée Draft 2020-12 par `message_type`.
- `schemas/v1/_shared.schema.json` : référence relative vers `../../.. /docs/20-exchanges-v1.schema.json` (sans l'espace : `../../../docs/20-exchanges-v1.schema.json`).
- `../docs/20-exchanges-v1.schema.json` : source de vérité des champs et contraintes v1, conservée sans duplication.
- `exemples/v1/<message>.json` : exemples illustratifs avec `schema_version: 1`.

Chaque schéma de message combine le contrat complet et une contrainte `const` sur `message_type`. Le contrat de référence applique ensuite les contraintes du payload correspondant : champs obligatoires, types, bornes et propriétés supplémentaires. Ce ne sont pas des schémas autonomes : distribuer aussi `_shared.schema.json` et le contrat de référence en conservant leurs chemins relatifs. Charger les schémas depuis leur URI de fichier, avec un résolveur Draft 2020-12 prenant en charge les références relatives. Activer explicitement la validation des formats UUID et date-time si le validateur ne la fait pas par défaut.

## Sorties Restic et provenance

Les exemples sont des données illustratives, non une preuve d'exécution de Restic. Le champ `restic_json` conserve une sortie Restic ; il ne transforme pas cette sortie en contrat API. Références : [Scripting — JSON output](https://restic.readthedocs.io/en/stable/075_scripting.html) et [Backing up](https://restic.readthedocs.io/en/stable/040_backup.html). Conserver la version de Restic observée et ne jamais assimiler une sortie inconnue à une réussite.

Le cadrage prévoit Restic `>=0.19.0`. Aucun binaire n'est validé par ces schémas. Ne pas inclure de véritables secrets dans les exemples.

## Compatibilité et validation

La négociation sélectionne la version commune maximale. Les champs inconnus doivent être préservés dans `extensions` avant validation du contrat strict, sans interprétation ni exécution. Les résultats sont idempotents via `message_id`/`idempotency_key` ; l'Outbox persiste avant envoi et l'ack suit la déduplication et le stockage.

La publication des points d'entrée ne constitue pas une validation automatisée des exemples ni des règles métier transversales (ordre temporel, négociation maximale, correspondance des identifiants, transitions d'état). Ces vérifications doivent être exécutées avant fusion.
