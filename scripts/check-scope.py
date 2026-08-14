#!/usr/bin/env python3
import argparse
import fnmatch
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLE_ALIASES = {
    "architect": "architecture",
    "reviewer": "review",
}


def run_git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check)


def matches(path, patterns):
    path = path.replace("\\", "/")
    return any(fnmatch.fnmatchcase(path, p.replace("\\", "/")) for p in patterns)


def find_feature_branch(task_id):
    proc = run_git("for-each-ref", "--format=%(refname:short)", f"refs/heads/feature/{task_id}-*")
    branches = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
    if len(branches) != 1:
        raise SystemExit(f"Cannot infer feature base for {task_id}; found {branches or 'none'}.")
    return branches[0]


def changed_files(base):
    files = set()
    for args in [("diff","--name-only",f"{base}...HEAD"),("diff","--name-only"),("diff","--cached","--name-only"),("ls-files","--others","--exclude-standard")]:
        proc = run_git(*args)
        files.update(x.strip().replace("\\", "/") for x in proc.stdout.splitlines() if x.strip())
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="Check worker Git changes against task path permissions.")
    parser.add_argument("task_id")
    parser.add_argument("role")
    parser.add_argument("--base")
    args = parser.parse_args()

    role = ROLE_ALIASES.get(args.role, args.role)
    task_path = ROOT / ".ai" / "tasks" / args.task_id / "task.json"
    task = json.loads(task_path.read_text(encoding="utf-8"))
    block = task.get("permissions", {}).get(role)
    if not block:
        known = sorted(task.get("permissions", {}))
        raise SystemExit(f"Unknown/unconfigured role: {args.role}. Known roles: {known}")

    base = args.base or find_feature_branch(args.task_id)
    allowed = block["allowed_write_paths"]
    forbidden = block["forbidden_paths"]
    violations = []
    files = changed_files(base)
    for path in files:
        if matches(path, forbidden):
            violations.append(f"FORBIDDEN: {path}")
        elif not matches(path, allowed):
            violations.append(f"OUTSIDE_ALLOWED_SCOPE: {path}")

    if violations:
        print(f"[FAIL] scope check for {args.task_id}/{args.role} ({role}) against {base}")
        for v in violations:
            print(f"  - {v}")
        raise SystemExit(1)
    print(f"[OK] scope check for {args.task_id}/{args.role} ({role}) ({len(files)} changed files)")


if __name__ == "__main__":
    main()
