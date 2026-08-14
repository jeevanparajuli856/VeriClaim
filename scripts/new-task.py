#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / ".ai" / "templates"
TASK_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_-]*-[0-9]+$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def deep_replace(value, old, new):
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [deep_replace(v, old, new) for v in value]
    if isinstance(value, dict):
        return {k: deep_replace(v, old, new) for k, v in value.items()}
    return value


def from_template(name, task_id):
    data = deepcopy(load_json(TEMPLATES / name))
    return deep_replace(data, "AUTH-001", task_id)


def require_project_ready(allow_unconfigured=False):
    path = ROOT / ".ai" / "project.json"
    if not path.exists():
        raise SystemExit("Missing .ai/project.json. Run project inception first.")
    project = load_json(path)
    if allow_unconfigured:
        return
    validation = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate-project.py")], cwd=ROOT)
    if validation.returncode != 0:
        raise SystemExit("Project operational configuration is invalid. Complete project inception before creating implementation tasks.")
    if project.get("status") != "INCEPTION_READY":
        raise SystemExit(
            "Project is not INCEPTION_READY. Complete project inception and update .ai/project.json before creating implementation tasks."
        )


def create_feature_spec(task_id, title):
    return f"""# {task_id} — {title}

## Goal

Describe the desired user/business outcome.

## In scope

-

## Out of scope

-

## Architecture impact

-

## Contract impact

-

## Security considerations

-

## Dependencies

-

## Acceptance criteria

-
"""


def main():
    parser = argparse.ArgumentParser(description="Create a complete agentic development task workspace.")
    parser.add_argument("task_id")
    parser.add_argument("title")
    parser.add_argument("--type", default="feature", choices=["feature","bug","refactor","security","infra","research"])
    parser.add_argument("--priority", default="medium", choices=["low","medium","high","critical"])
    parser.add_argument("--allow-unconfigured", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    require_project_ready(args.allow_unconfigured)

    if not TASK_ID_PATTERN.fullmatch(args.task_id):
        raise SystemExit("Invalid task ID. Use a format such as AUTH-001, PROFILE-003, or SEC-12.")

    task_dir = ROOT / ".ai" / "tasks" / args.task_id
    spec_path = ROOT / "docs" / "features" / f"{args.task_id}.md"
    if task_dir.exists() or spec_path.exists():
        raise SystemExit(f"Task or spec already exists for {args.task_id}")

    task = from_template("task.template.json", args.task_id)
    task.update({"title": args.title, "type": args.type, "priority": args.priority, "status": "PROPOSED"})

    task_dir.mkdir(parents=True)
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(task_dir / "task.json", task)
    spec_path.write_text(create_feature_spec(args.task_id, args.title), encoding="utf-8")

    templates = {
        "architecture-report.json": "architecture-report.template.json",
        "database-report.json": "database-report.template.json",
        "backend-report.json": "backend-report.template.json",
        "frontend-report.json": "frontend-report.template.json",
        "test-report.json": "test-report.template.json",
        "verification-report.json": "verification-report.template.json",
        "security-report.json": "security-report.template.json",
        "review-report.json": "review-report.template.json",
    }
    for output_name, template_name in templates.items():
        write_json(task_dir / output_name, from_template(template_name, args.task_id))

    print(f"Created task workspace: {args.task_id}")
    print(f"Next: python scripts/agentctl.py git prepare {args.task_id}")
    print(f"Then: python scripts/agentctl.py task advance {args.task_id}")


if __name__ == "__main__":
    main()
