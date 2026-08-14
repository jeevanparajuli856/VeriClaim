#!/usr/bin/env python3
import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    raise SystemExit("Missing jsonschema. Install: python -m pip install -r requirements-agent.txt")

ROOT = Path(__file__).resolve().parents[1]


def semantic_errors(data):
    errors = []
    if data.get("status") != "INCEPTION_READY":
        return errors

    components = data.get("components", {})
    for name in ("backend", "frontend", "database"):
        enabled = components.get(name, {}).get("enabled")
        if not isinstance(enabled, bool):
            errors.append(f"components.{name}.enabled must be true/false when status is INCEPTION_READY")

    for name in ("backend", "frontend"):
        comp = components.get(name, {})
        if comp.get("enabled") is True:
            technology = comp.get("technology")
            if not isinstance(technology, str) or not technology.strip():
                errors.append(f"components.{name}.technology must be set when {name} is enabled")

    db = components.get("database", {})
    if db.get("enabled") is True:
        provider = db.get("provider")
        migration_path = db.get("migration_path")
        if not isinstance(provider, str) or not provider.strip():
            errors.append("components.database.provider must be set when database is enabled")
        if not isinstance(migration_path, str) or not migration_path.strip():
            errors.append("components.database.migration_path must be set when database is enabled")

    return errors


def main():
    data_path = ROOT / ".ai" / "project.json"
    schema_path = ROOT / ".ai" / "schemas" / "project.schema.json"
    if not data_path.exists():
        raise SystemExit("[FAIL] missing .ai/project.json")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.absolute_path))
    messages = []
    for e in errors:
        path = ".".join(str(x) for x in e.absolute_path) or "<root>"
        messages.append(f"{path}: {e.message}")
    messages.extend(semantic_errors(data))

    if messages:
        print("[FAIL] .ai/project.json")
        for message in messages:
            print(f"  - {message}")
        raise SystemExit(1)
    print("[OK] .ai/project.json")


if __name__ == "__main__":
    main()
