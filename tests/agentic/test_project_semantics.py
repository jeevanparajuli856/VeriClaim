import json
from conftest import run


def test_inception_ready_requires_resolved_component_flags(repo):
    p = repo / '.ai/project.json'
    data = json.loads(p.read_text())
    data['components']['backend']['enabled'] = None
    p.write_text(json.dumps(data, indent=2) + '\n')

    result = run(repo, 'scripts/validate-project.py', check=False)
    assert result.returncode != 0
    assert 'components.backend.enabled must be true/false' in result.stdout


def test_enabled_component_requires_technology(repo):
    p = repo / '.ai/project.json'
    data = json.loads(p.read_text())
    data['components']['frontend']['enabled'] = True
    data['components']['frontend']['technology'] = None
    p.write_text(json.dumps(data, indent=2) + '\n')

    result = run(repo, 'scripts/validate-project.py', check=False)
    assert result.returncode != 0
    assert 'components.frontend.technology must be set' in result.stdout
