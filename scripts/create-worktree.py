#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READY = {"CONTRACT_READY","IMPLEMENTATION","INTEGRATION","SECURITY_REVIEW","REVIEW","PR_READY"}


def run(*args, capture=False, check=True):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=capture, check=check)


def find_feature_branch(task_id):
    proc = run("git", "for-each-ref", "--format=%(refname:short)", f"refs/heads/feature/{task_id}-*", capture=True)
    branches = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
    if len(branches) != 1:
        raise SystemExit(f"Expected exactly one feature/{task_id}-* branch; found {branches or 'none'}. Run agentctl git prepare first.")
    return branches[0]


def task_from_branch(branch, task_id):
    path = f".ai/tasks/{task_id}/task.json"
    proc = run("git", "show", f"{branch}:{path}", capture=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"{path} is not committed on {branch}. Commit planning/contracts before creating worktrees.")
    return json.loads(proc.stdout)


def main():
    parser = argparse.ArgumentParser(description="Create a parallel Git worktree for an implementation agent.")
    parser.add_argument("task_id")
    parser.add_argument("role", choices=["backend","frontend"])
    parser.add_argument("--base")
    parser.add_argument("--dir", dest="target_dir")
    args = parser.parse_args()

    run("git", "rev-parse", "--show-toplevel", capture=True)
    base = args.base or find_feature_branch(args.task_id)
    if base in {"main","master"}:
        raise SystemExit("Implementation worktrees may not branch directly from main/master.")

    task = task_from_branch(base, args.task_id)
    if task.get("status") not in READY:
        raise SystemExit(f"Committed task status is {task.get('status')!r}; CONTRACT_READY is required before implementation worktrees.")

    branch = f"agent/{args.task_id}-{args.role}"
    target = Path(args.target_dir) if args.target_dir else ROOT.parent / f"{ROOT.name}-{args.task_id}-{args.role}"
    if target.exists():
        raise SystemExit(f"Target already exists: {target}")
    if run("git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode == 0:
        raise SystemExit(f"Branch already exists: {branch}")

    run("git", "worktree", "add", str(target), "-b", branch, base)
    print(f"Created {args.role} worktree: {target}")
    print(f"Base: {base}")


if __name__ == "__main__":
    main()
