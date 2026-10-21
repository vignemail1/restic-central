#!/usr/bin/env python3
"""Tests ciblés du registre local : une ref absente doit échouer, sans réseau."""
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import validate_contracts  # noqa: E402

def test_missing_ref_is_reported():
    schema = {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"https://restic-central.invalid/schemas/v1/test.schema.json","type":"object","properties":{"child":{"$ref":"missing.schema.json"}}}
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test.schema.json"
        path.write_text(json.dumps(schema), encoding="utf-8")
        errors = validate_contracts.validate_paths([path], Path(directory))
        assert any("référence hors registre" in error for error in errors)

def test_local_ref_resolves_without_network():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        shared = {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"https://restic-central.invalid/schemas/v1/shared.schema.json","$defs":{"value":{"type":"string"}}}
        schema = {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"https://restic-central.invalid/schemas/v1/test.schema.json","type":"object","properties":{"value":{"$ref":"shared.schema.json#/$defs/value"}}}
        shared_path = root / "shared.schema.json"; test_path = root / "test.schema.json"
        shared_path.write_text(json.dumps(shared), encoding="utf-8"); test_path.write_text(json.dumps(schema), encoding="utf-8")
        (root / "shared.json").write_text("{}", encoding="utf-8"); (root / "test.json").write_text(json.dumps({"value":"ok"}), encoding="utf-8")
        errors = validate_contracts.validate_paths([shared_path, test_path], root)
        assert errors == [], errors

if __name__ == "__main__":
    test_missing_ref_is_reported(); test_local_ref_resolves_without_network(); print("OK: tests registre local/ref absente et ref locale")
