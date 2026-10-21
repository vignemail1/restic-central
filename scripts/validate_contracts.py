#!/usr/bin/env python3
"""Validation locale et déterministe des contrats JSON v1 (sans accès réseau)."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "contracts/schemas/v1"
EXAMPLE_DIR = ROOT / "contracts/exemples/v1"


def load(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def walk_refs(value):
    if isinstance(value, dict):
        if "$ref" in value:
            yield value["$ref"]
        for child in value.values():
            yield from walk_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_refs(child)


def build_registry(schemas: dict[Path, dict]) -> Registry:
    registry = Registry()
    for path, schema in schemas.items():
        schema_id = schema.get("$id")
        if not schema_id:
            raise ValueError(f"$id manquant: {path}")
        registry = registry.with_resource(schema_id, Resource.from_contents(schema))
    return registry


def validate_paths(schema_paths: list[Path], example_dir: Path) -> list[str]:
    schemas = {path: load(path) for path in schema_paths}
    errors: list[str] = []
    registry_ids: set[str] = set()
    for path, schema in schemas.items():
        schema_id = schema.get("$id")
        if not schema_id:
            errors.append(f"$id manquant: {path}")
            continue
        if schema_id in registry_ids:
            errors.append(f"$id dupliqué: {schema_id}")
        registry_ids.add(schema_id)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            errors.append(f"{path}: schéma invalide: {type(exc).__name__}: {exc}")
    if errors:
        return errors
    registry = build_registry(schemas)
    for path, schema in schemas.items():
        base = schema["$id"]
        for ref in walk_refs(schema):
            if ref.startswith("#"):
                continue
            resolved = urljoin(base, ref).split("#", 1)[0]
            if resolved not in registry_ids:
                errors.append(f"{path}: référence hors registre: {ref}")
        example_path = example_dir / path.name.replace(".schema.json", ".json")
        if path.name == "_shared.schema.json":
            continue
        if not example_path.exists():
            errors.append(f"{path}: exemple manquant: {example_path.name}")
            continue
        try:
            validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
            instance = load(example_path)
            errors.extend(f"{example_path}: {error.message}" for error in validator.iter_errors(instance))
        except Exception as exc:
            errors.append(f"{path}: {type(exc).__name__}: {exc}")
    return errors


def main() -> int:
    schema_paths = sorted(SCHEMA_DIR.glob("*.schema.json"))
    example_paths = sorted(EXAMPLE_DIR.glob("*.json"))
    if not schema_paths:
        raise SystemExit("Aucun schéma trouvé")
    errors = validate_paths(schema_paths, EXAMPLE_DIR)
    expected_examples = {p.name.replace(".schema.json", ".json") for p in schema_paths if p.name != "_shared.schema.json"}
    actual_examples = {p.name for p in example_paths}
    for missing in sorted(expected_examples - actual_examples):
        errors.append(f"exemple manquant: {missing}")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(schema_paths)} schémas, {len(example_paths)} exemples; Draft 2020-12 et refs hors ligne validés.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
