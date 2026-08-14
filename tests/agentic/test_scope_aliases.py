import json
import subprocess
from conftest import run


def _git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, text=True, capture_output=True, check=True)


def test_reviewer_alias_maps_to_review_permission_and_blocks_code_writes(repo):
    run(repo, 'scripts/new-task.py', 'SCOPE-001', 'Scope alias')
    _git(repo, 'init')
    _git(repo, 'config', 'user.email', 'agentic-test@example.invalid')
    _git(repo, 'config', 'user.name', 'Agentic Test')
    _git(repo, 'add', '.')
    _git(repo, 'commit', '-m', 'baseline')
    _git(repo, 'branch', 'feature/SCOPE-001-scope-alias')

    report_path = repo / '.ai/tasks/SCOPE-001/review-report.json'
    report = json.loads(report_path.read_text())
    report['summary'] = 'Review evidence only.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')

    ok = run(repo, 'scripts/check-scope.py', 'SCOPE-001', 'reviewer')
    assert ok.returncode == 0

    backend = repo / 'backend'
    backend.mkdir()
    (backend / 'oops.py').write_text('print("out of scope")\n')
    failed = run(repo, 'scripts/check-scope.py', 'SCOPE-001', 'reviewer', check=False)
    assert failed.returncode != 0
    assert 'backend/oops.py' in failed.stdout
