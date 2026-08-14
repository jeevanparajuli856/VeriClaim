#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "contracts" / "openapi.yaml"
    if not path.exists():
        raise SystemExit("[FAIL] missing contracts/openapi.yaml")

    # Use the package's documented CLI entry point instead of an internal Python
    # shortcut API. This keeps validation behavior aligned with the installed
    # openapi-spec-validator release and preserves file-based reference context.
    proc = subprocess.run(
        [sys.executable, "-m", "openapi_spec_validator", str(path)],
        cwd=ROOT,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit("[FAIL] contracts/openapi.yaml")
    print("[OK] contracts/openapi.yaml")


if __name__ == "__main__":
    main()
