import json
from jsonschema import Draft202012Validator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _schema(name):
    return json.loads((ROOT / '.ai/schemas' / name).read_text())


def test_security_approved_cannot_contain_blocking_finding():
    report = json.loads((ROOT / '.ai/templates/security-report.template.json').read_text())
    report['status'] = 'APPROVED'
    report['reviewed_commit'] = 'abc123'
    report['findings'] = [{
        'severity': 'high',
        'category': 'authorization',
        'description': 'Broken authorization boundary',
        'impact': 'Unauthorized access',
        'remediation': 'Enforce ownership checks',
        'blocking': True,
    }]
    errors = list(Draft202012Validator(_schema('security-report.schema.json')).iter_errors(report))
    assert errors


def test_review_approved_cannot_contain_blocking_finding():
    report = json.loads((ROOT / '.ai/templates/review-report.template.json').read_text())
    report['status'] = 'APPROVED'
    report['reviewed_commit'] = 'abc123'
    report['findings'] = [{
        'severity': 'high',
        'category': 'correctness',
        'description': 'Release-blocking defect',
        'recommendation': 'Fix before merge',
        'blocking': True,
    }]
    errors = list(Draft202012Validator(_schema('review.schema.json')).iter_errors(report))
    assert errors
