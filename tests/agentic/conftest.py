from pathlib import Path
import shutil
import json
import subprocess
import sys
import pytest

SOURCE = Path(__file__).resolve().parents[2]

@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    for rel in [".ai", "scripts", "contracts", "docs/features"]:
        src = SOURCE / rel
        dst = root / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    project_path = root / ".ai" / "project.json"
    project = json.loads(project_path.read_text())
    project["status"] = "INCEPTION_READY"
    project["components"]["backend"]["enabled"] = True
    project["components"]["backend"]["technology"] = "test"
    project["components"]["frontend"]["enabled"] = True
    project["components"]["frontend"]["technology"] = "test"
    project["components"]["database"]["enabled"] = False
    project["components"]["database"]["provider"] = None
    project_path.write_text(json.dumps(project, indent=2) + "\n")
    return root


def run(root, *args, check=True):
    return subprocess.run([sys.executable, *args], cwd=root, text=True, capture_output=True, check=check)
