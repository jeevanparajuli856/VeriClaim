#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    raise SystemExit("Missing jsonschema. Install: python -m pip install -r requirements-agent.txt")

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / ".ai" / "schemas"

REPORT_SCHEMAS = {
    "architecture-report.json": "architecture-report.schema.json",
    "database-report.json": "agent-report.schema.json",
    "backend-report.json": "agent-report.schema.json",
    "frontend-report.json": "agent-report.schema.json",
    "test-report.json": "agent-report.schema.json",
    "verification-report.json": "verification-report.schema.json",
    "security-report.json": "security-report.schema.json",
    "review-report.json": "review.schema.json",
}


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)


def schema_errors(data, schema_name):
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    return sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.absolute_path))


def fmt_error(error):
    path = ".".join(str(x) for x in error.absolute_path) or "<root>"
    return f"{path}: {error.message}"


def validate_task_file(task_file):
    errors = []
    data, err = load(task_file)
    if err:
        return [f"invalid task JSON: {err}"]

    for e in schema_errors(data, "task.schema.json"):
        errors.append(fmt_error(e))

    task_id = data.get("task_id")
    if task_file.parent.name != task_id:
        errors.append(f"task directory {task_file.parent.name!r} does not match task_id {task_id!r}")

    spec = data.get("spec")
    if spec and not (ROOT / spec).exists():
        errors.append(f"missing spec: {spec}")

    for contract in data.get("contracts", []):
        if not (ROOT / contract).exists():
            errors.append(f"missing contract: {contract}")

    for filename, schema_name in REPORT_SCHEMAS.items():
        path = task_file.parent / filename
        if not path.exists():
            errors.append(f"missing report: {path.relative_to(ROOT)}")
            continue
        report, report_err = load(path)
        if report_err:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {report_err}")
            continue
        for e in schema_errors(report, schema_name):
            errors.append(f"{path.relative_to(ROOT)}: {fmt_error(e)}")
        if report.get("task_id") != task_id:
            errors.append(f"{path.relative_to(ROOT)} task_id mismatch")

    project, project_err = load(ROOT / ".ai" / "project.json")
    if project_err:
        errors.append(f"invalid .ai/project.json: {project_err}")
    elif project.get("status") != "INCEPTION_READY":
        errors.append("project status must be INCEPTION_READY while tracked implementation tasks exist")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", nargs="?")
    args = parser.parse_args()

    files = ([ROOT / ".ai" / "tasks" / args.task_id / "task.json"] if args.task_id
             else sorted((ROOT / ".ai" / "tasks").glob("*/task.json")))
    if not files:
        print("No tasks found.")
        return

    ok = True
    for task_file in files:
        if not task_file.exists():
            print(f"[FAIL] missing {task_file}")
            ok = False
            continue
        errors = validate_task_file(task_file)
        if errors:
            ok = False
            print(f"[FAIL] {task_file.relative_to(ROOT)}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"[OK] {task_file.relative_to(ROOT)}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
