import json
from jsonschema import Draft202012Validator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def validate(data_file, schema_file):
    data = json.loads((ROOT / data_file).read_text())
    schema = json.loads((ROOT / schema_file).read_text())
    errors = list(Draft202012Validator(schema).iter_errors(data))
    assert not errors, [e.message for e in errors]


def test_project_manifest_schema():
    validate('.ai/project.json', '.ai/schemas/project.schema.json')


def test_templates_match_schemas():
    mapping = {
        '.ai/templates/task.template.json': '.ai/schemas/task.schema.json',
        '.ai/templates/architecture-report.template.json': '.ai/schemas/architecture-report.schema.json',
        '.ai/templates/database-report.template.json': '.ai/schemas/agent-report.schema.json',
        '.ai/templates/backend-report.template.json': '.ai/schemas/agent-report.schema.json',
        '.ai/templates/frontend-report.template.json': '.ai/schemas/agent-report.schema.json',
        '.ai/templates/test-report.template.json': '.ai/schemas/agent-report.schema.json',
        '.ai/templates/verification-report.template.json': '.ai/schemas/verification-report.schema.json',
        '.ai/templates/security-report.template.json': '.ai/schemas/security-report.schema.json',
        '.ai/templates/review-report.template.json': '.ai/schemas/review.schema.json',
    }
    for data, schema in mapping.items():
        validate(data, schema)
