import importlib.util
import json
import subprocess
import sys
from conftest import run


def _git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, text=True, capture_output=True, check=True)


def _load_agentctl(repo):
    path = repo / 'scripts/agentctl.py'
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location('agentctl_under_test', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous


def test_status_only_task_change_does_not_stale_verification_but_architecture_change_does(repo):
    run(repo, 'scripts/new-task.py', 'EVID-001', 'Evidence freshness')
    _git(repo, 'init')
    _git(repo, 'config', 'user.email', 'agentic-test@example.invalid')
    _git(repo, 'config', 'user.name', 'Agentic Test')
    _git(repo, 'add', '.')
    _git(repo, 'commit', '-m', 'baseline')
    reviewed = _git(repo, 'rev-parse', 'HEAD').stdout.strip()

    task_path = repo / '.ai/tasks/EVID-001/task.json'
    task = json.loads(task_path.read_text())
    task['status'] = 'PLANNING'
    task_path.write_text(json.dumps(task, indent=2) + '\n')

    agentctl = _load_agentctl(repo)
    ok, _ = agentctl.evidence_is_current('EVID-001', reviewed, 'verification-report.json')
    assert ok

    arch_path = repo / '.ai/tasks/EVID-001/architecture-report.json'
    arch = json.loads(arch_path.read_text())
    arch['summary'] = 'Changed after verification.'
    arch_path.write_text(json.dumps(arch, indent=2) + '\n')

    ok, reason = agentctl.evidence_is_current('EVID-001', reviewed, 'verification-report.json')
    assert not ok
    assert 'architecture-report.json' in reason
