#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_check(name, command, cwd, required=True):
    target = ROOT / cwd
    try:
        proc = subprocess.run(command, cwd=target)
        status = "PASSED" if proc.returncode == 0 else "FAILED"
        notes = "" if proc.returncode == 0 else f"exit code {proc.returncode}"
    except FileNotFoundError as exc:
        status = "FAILED" if required else "SKIPPED"
        notes = f"command unavailable: {exc.filename}"
    return {"name":name,"status":status,"required":required,"command":command,"notes":notes}


def current_commit():
    proc = subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, text=True, capture_output=True)
    return proc.stdout.strip() if proc.returncode == 0 else "UNCOMMITTED"


def baseline_security_check():
    proc = subprocess.run(["git","ls-files"], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        return {"name":"tracked-secret-file-baseline","status":"SKIPPED","required":False,"command":["git","ls-files"],"notes":"not a Git repository"}
    bad = []
    for rel in proc.stdout.splitlines():
        name = Path(rel).name.lower()
        if rel == ".env.example":
            continue
        if name == ".env" or name.startswith(".env.") or name == "credentials.json" or name.endswith(".pem") or name.endswith(".key"):
            bad.append(rel)
        if rel.startswith("supabase/.temp/") or rel.startswith("supabase/.branches/"):
            bad.append(rel)
    return {
        "name":"tracked-secret-file-baseline",
        "status":"FAILED" if bad else "PASSED",
        "required":True,
        "command":["git","ls-files"],
        "notes":("forbidden tracked files: " + ", ".join(sorted(set(bad)))) if bad else ""
    }


def write_report(task_id, checks):
    commit = current_commit()
    failed = any(c["status"] == "FAILED" or (c["required"] and c["status"] == "SKIPPED") for c in checks)
    report = {
        "schema_version":"1.0",
        "task_id":task_id,
        "commit":commit,
        "status":"FAILED" if failed else "PASSED",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "checks":checks,
    }
    path = ROOT / ".ai" / "tasks" / task_id / "verification-report.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Run repository verification.")
    parser.add_argument("task_id", nargs="?")
    parser.add_argument("--tests-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    args = parser.parse_args()
    if args.tests_only and args.security_only:
        raise SystemExit("Choose at most one of --tests-only or --security-only.")

    project_path = ROOT / ".ai" / "project.json"
    project = json.loads(project_path.read_text(encoding="utf-8"))
    checks = []

    if not args.security_only:
        checks.append(run_check("project-schema", [sys.executable,"scripts/validate-project.py"], ".", True))
        task_cmd = [sys.executable,"scripts/validate-task.py"] + ([args.task_id] if args.task_id else [])
        checks.append(run_check("task-schema-and-reports", task_cmd, ".", True))
        if not args.tests_only:
            checks.append(run_check("openapi-contract", [sys.executable,"scripts/validate-contracts.py"], ".", True))
        checks.append(run_check("agentic-framework-tests", [sys.executable,"-m","pytest","-q","tests/agentic"], ".", True))
        for item in project.get("verification", {}).get("checks", []):
            checks.append(run_check(item["name"], item["command"], item["cwd"], item["required"]))

    if not args.tests_only:
        checks.append(baseline_security_check())
        for item in project.get("security", {}).get("checks", []):
            checks.append(run_check(item["name"], item["command"], item["cwd"], item["required"]))

    failed = any(c["status"] == "FAILED" or (c["required"] and c["status"] == "SKIPPED") for c in checks)
    for c in checks:
        print(f"[{c['status']}] {c['name']}" + (f": {c['notes']}" if c['notes'] else ""))

    if args.task_id and not args.tests_only and not args.security_only:
        report = write_report(args.task_id, checks)
        print(f"verification-report.json: {report['status']} @ {report['commit']}")

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
