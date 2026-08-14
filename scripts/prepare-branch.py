#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args, capture=False, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=capture, check=check)


def main():
    parser = argparse.ArgumentParser(description="Prepare the feature branch for a task.")
    parser.add_argument("task_id")
    parser.add_argument("--base", help="Explicit base branch; otherwise current branch")
    args = parser.parse_args()

    task_file = ROOT / ".ai" / "tasks" / args.task_id / "task.json"
    if not task_file.exists():
        raise SystemExit(f"Missing task: {args.task_id}")
    task = json.loads(task_file.read_text(encoding="utf-8"))

    git("rev-parse", "--show-toplevel", capture=True)
    current = git("branch", "--show-current", capture=True).stdout.strip()
    if current.startswith(f"feature/{args.task_id}-"):
        print(f"Feature branch already active: {current}")
        return

    base = args.base or current
    if not base:
        raise SystemExit("Detached HEAD. Pass --base explicitly.")
    if (current.startswith("feature/") or current.startswith("agent/")) and not args.base:
        raise SystemExit("Refusing to branch from another feature/agent branch. Pass --base deliberately.")

    slug = re.sub(r"[^a-z0-9]+", "-", task.get("title", "task").lower()).strip("-")[:48] or "task"
    feature = f"feature/{args.task_id}-{slug}"
    exists = git("show-ref", "--verify", "--quiet", f"refs/heads/{feature}", check=False)
    if exists.returncode == 0:
        if git("status", "--porcelain", capture=True).stdout.strip():
            raise SystemExit(f"Feature branch exists but working tree is dirty. Commit/stash before switching to {feature}.")
        git("switch", feature)
        print(f"Switched to existing feature branch: {feature}")
    else:
        git("switch", "-c", feature, base)
        print(f"Created feature branch: {feature}")


if __name__ == "__main__":
    main()
