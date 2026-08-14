import json
from conftest import run


def test_architecture_gate_refuses_partial_report(repo):
    run(repo, 'scripts/new-task.py', 'GATE-001', 'Gate test')
    run(repo, 'scripts/agentctl.py', 'task', 'advance', 'GATE-001')
    failed = run(repo, 'scripts/agentctl.py', 'task', 'advance', 'GATE-001', check=False)
    assert failed.returncode != 0

    p = repo/'.ai/tasks/GATE-001/architecture-report.json'
    report = json.loads(p.read_text())
    report['status'] = 'COMPLETE'
    report['summary'] = 'Architecture complete.'
    for k in report['impacts']:
        report['impacts'][k] = False
    p.write_text(json.dumps(report, indent=2) + '\n')

    ok = run(repo, 'scripts/agentctl.py', 'task', 'advance', 'GATE-001')
    assert 'ARCHITECTURE_READY' in ok.stdout
