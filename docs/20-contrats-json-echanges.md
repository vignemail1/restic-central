# Contrats JSON d’échange — inventaire v1

> **Portée réelle.** Ce document explique les messages et règles métier, sans être la source normative des schémas. Les sources normatives sont les fichiers Draft 2020-12 de `../contracts/schemas/v1/`, avec définitions communes dans `_shared.schema.json`; les exemples sont dans `../contracts/exemples/v1/`. Les anciens fichiers JSON de `docs/` sont historiques et ne doivent pas être utilisés par une implémentation ou la CI.

## 1. Enveloppe commune

La source normative est exclusivement constituée des schémas Draft 2020-12 présents dans `../contracts/schemas/v1/`, avec définitions communes dans `_shared.schema.json`; les exemples sont dans `../contracts/exemples/v1/`. Ce document est explicatif et ne doit pas être utilisé comme schéma d’exécution. Valider localement avec `python3 scripts/validate-contracts.py`; le validateur construit un registre par `$id`, résout uniquement les références présentes dans le dépôt et échoue sur toute référence absente. Aucun accès réseau n’est autorisé.

## 2. Exemples conformes

Les exemples ci-dessous sont minimaux pour illustrer les flux ajoutés ; ils complètent `../contracts/exemples/v1/attempt.result.json` (résultat terminal). Ils ne promettent pas une implémentation.
