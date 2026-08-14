import json
from conftest import run


def test_new_task_creates_complete_workspace(repo):
    run(repo, 'scripts/new-task.py', 'TEST-001', 'Test feature')
    expected = {
        'task.json','architecture-report.json','database-report.json','backend-report.json',
        'frontend-report.json','test-report.json','verification-report.json','security-report.json','review-report.json'
    }
    created = {p.name for p in (repo/'.ai/tasks/TEST-001').iterdir()}
    assert expected <= created
    run(repo, 'scripts/validate-task.py', 'TEST-001')


def test_new_task_uses_template_permissions(repo):
    run(repo, 'scripts/new-task.py', 'TEST-002', 'Permission test')
    generated = json.loads((repo/'.ai/tasks/TEST-002/task.json').read_text())
    template = json.loads((repo/'.ai/templates/task.template.json').read_text())
    assert set(generated['permissions']) == set(template['permissions'])
    assert 'tester' in generated['owners']
