"""Independent acceptance tests for the integrated DEMO-001 revision."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from jsonschema import Draft202012Validator

from backend.app.extractor import AmountComponent, ExtractedDataset, ReferenceValue
from backend.app.gemini import MAX_PROMPT_BYTES, MAX_RESPONSE_BYTES, GeminiSummarizer
from backend.app.loader import MAX_FILE_BYTES, PipelineError, SOURCE_PATHS, default_project_root, load_approved_sources
from backend.app.rules import coverage_date_bounds, observed_amount_relationship, reference_integrity, sample_relative_high_amount
from backend.app.service import AnalysisService


EXPECTED_SOURCE_HASHES = {
    "dataset/patient_bbuser29999.json": "6fb43e72120e3a3cfb7bc756d0661eebcc0925a2bc994f60ecbf573813e3f58a",
    "dataset/coverage_bundle_bbuser29999.json": "fef088d7c6df3fb33bc02a1e32be53a67db0815046b1e2d998d44cb1536ec33c",
    "dataset/eob_bundle_bbuser29999.json": "d48c12a8d94e331c786f3876ea94df4356209c216c54392346dae87f84fc34f0",
}


def _source_hashes() -> dict[str, str]:
    root = default_project_root()
    return {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for _, relative in SOURCE_PATHS
    }


@pytest.fixture(scope="module", autouse=True)
def approved_sources_remain_byte_identical():
    assert _source_hashes() == EXPECTED_SOURCE_HASHES
    yield
    assert _source_hashes() == EXPECTED_SOURCE_HASHES


def _write_minimal_source_set(root: Path) -> None:
    dataset = root / "dataset"
    dataset.mkdir()
    documents = {
        "patient_bbuser29999.json": {"resourceType": "Patient", "id": "p"},
        "coverage_bundle_bbuser29999.json": {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Coverage",
                        "id": "c",
                        "beneficiary": {"reference": "Patient/p"},
                    }
                }
            ],
        },
        "eob_bundle_bbuser29999.json": {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "ExplanationOfBenefit",
                        "id": "e",
                        "patient": {"reference": "Patient/p"},
                        "insurance": [{"coverage": {"reference": "Coverage/c"}}],
                        "item": [],
                    }
                }
            ],
        },
    }
    for name, document in documents.items():
        (dataset / name).write_text(json.dumps(document), encoding="utf-8")


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("missing", "SOURCE_UNAVAILABLE"),
        ("oversize", "SOURCE_TOO_LARGE"),
        ("invalid_json", "SOURCE_INVALID_JSON"),
        ("non_object", "SOURCE_SHAPE_UNSUPPORTED"),
    ],
)
def test_fixed_loader_classifies_source_failures(tmp_path: Path, mutation: str, expected_code: str) -> None:
    _write_minimal_source_set(tmp_path)
    patient = tmp_path / "dataset" / "patient_bbuser29999.json"
    if mutation == "missing":
        patient.unlink()
    elif mutation == "oversize":
        patient.write_bytes(b"x" * (MAX_FILE_BYTES + 1))
    elif mutation == "invalid_json":
        patient.write_text("{", encoding="utf-8")
    else:
        patient.write_text("[]", encoding="utf-8")

    with pytest.raises(PipelineError) as captured:
        load_approved_sources(tmp_path)

    assert captured.value.code == expected_code


def test_real_pipeline_requires_no_live_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "VERTEX_GEMINI_MODEL",
        "GOOGLE_GENAI_USE_VERTEXAI",
    ):
        monkeypatch.delenv(name, raising=False)

    response = AnalysisService().analyze()

    assert response.gemini.status == "configuration_error"
    assert response.model_metadata.model is None
    assert response.model_metadata.invoked is False
    assert response.model_metadata.call_count == 0
    assert [result.rule_id for result in response.rule_results] == [
        "REF-001",
        "DATE-001",
        "REPEAT-001",
        "AMOUNT-001",
        "OUTLIER-001",
    ]
    evidence_ids = [record.evidence_id for record in response.evidence_index]
    assert len(evidence_ids) == len(set(evidence_ids))
    assert all(
        reference in evidence_ids
        for result in response.rule_results
        for signal in result.signals
        for reference in signal.evidence_refs
    )


def test_pipeline_failure_occurs_before_the_model_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    class RecordingSummarizer:
        calls = 0

        def summarize(self, payload, allowed_evidence):
            self.calls += 1
            raise AssertionError("model boundary must not be reached")

    summarizer = RecordingSummarizer()

    def fail_loading():
        raise PipelineError("SOURCE_UNAVAILABLE", "An approved synthetic source is unavailable.")

    monkeypatch.setattr("backend.app.service.load_approved_sources", fail_loading)
    with pytest.raises(PipelineError, match="approved synthetic source"):
        AnalysisService(summarizer).analyze()  # type: ignore[arg-type]
    assert summarizer.calls == 0


@pytest.mark.parametrize(
    ("reference", "expected_type"),
    [
        (ReferenceValue(None, None, "ev:eob:/entry/0/resource/id"), "missing_reference"),
        (
            ReferenceValue("https://example.invalid/Patient/p", "ev:eob:/entry/0/resource/patient/reference", "ev:eob:/entry/0/resource/id"),
            "malformed_reference",
        ),
        (
            ReferenceValue("Coverage/c", "ev:eob:/entry/0/resource/patient/reference", "ev:eob:/entry/0/resource/id"),
            "wrong_reference_type",
        ),
        (
            ReferenceValue("Patient/absent", "ev:eob:/entry/0/resource/patient/reference", "ev:eob:/entry/0/resource/id"),
            "unresolved_reference",
        ),
    ],
)
def test_reference_rule_distinguishes_failure_modes(
    extracted: ExtractedDataset, reference: ReferenceValue, expected_type: str
) -> None:
    eob = extracted.eobs[0]
    changed = replace(extracted, eobs=[replace(eob, patient=reference)])
    result = reference_integrity(changed)
    assert [(signal.evidence_id, signal.signal_type) for signal in result.signals] == [
        ("sig:REF-001:0001", expected_type)
    ]


def test_reference_rule_preserves_ambiguous_identity_evidence(extracted: ExtractedDataset) -> None:
    eob = extracted.eobs[0]
    patient_id = eob.patient.value.removeprefix("Patient/")  # type: ignore[union-attr]
    identity_index = {key: list(values) for key, values in extracted.identity_index.items()}
    identity_index[("Patient", patient_id)].append("ev:patient:/duplicate/id")
    changed = replace(extracted, eobs=[eob], identity_index=identity_index)

    result = reference_integrity(changed)

    assert [signal.signal_type for signal in result.signals] == ["ambiguous_reference"] * 5
    assert all("ev:patient:/duplicate/id" in signal.evidence_refs for signal in result.signals)


def test_date_rule_is_inclusive_and_uses_only_present_bounds(extracted: ExtractedDataset) -> None:
    eob = extracted.eobs[0]
    item = eob.items[0]
    coverage = extracted.coverages[3]
    bounded = replace(
        coverage,
        start=item.service_date,
        start_evidence_id=coverage.identity_evidence_id,
        end=None,
        end_evidence_id=None,
    )
    one_item = replace(extracted, coverages=[*extracted.coverages[:3], bounded], eobs=[replace(eob, items=(item,))])
    inclusive = coverage_date_bounds(one_item)
    assert inclusive.status == "completed"
    assert inclusive.parameters["comparisons"] == 1
    assert inclusive.signals == []

    outside = replace(
        one_item,
        coverages=[*extracted.coverages[:3], replace(bounded, start=item.service_date + timedelta(days=1))],
    )
    assert [signal.signal_type for signal in coverage_date_bounds(outside).signals] == [
        "service_date_outside_present_coverage_bounds"
    ]


def _with_drugcost_delta(extracted: ExtractedDataset, delta: Decimal, currency: str = "USD") -> ExtractedDataset:
    eob = extracted.eobs[0]
    item = eob.items[0]
    by_code = {component.code: component for component in item.adjudications}
    target = by_code["benefit"].value + by_code["paidbypatient"].value + delta
    adjudications = tuple(
        replace(component, value=target, currency=currency) if component.code == "drugcost" else component
        for component in item.adjudications
    )
    return replace(extracted, eobs=[replace(eob, items=(replace(item, adjudications=adjudications),))])


def test_amount_rule_uses_decimal_strictly_greater_than_tolerance(extracted: ExtractedDataset) -> None:
    boundary = observed_amount_relationship(_with_drugcost_delta(extracted, Decimal("0.01")))
    above = observed_amount_relationship(_with_drugcost_delta(extracted, Decimal("0.0101")))
    mismatch = observed_amount_relationship(_with_drugcost_delta(extracted, Decimal("0"), "EUR"))

    assert boundary.status == "completed" and boundary.signals == []
    assert [signal.signal_type for signal in above.signals] == ["observed_amount_components_do_not_reconcile"]
    assert mismatch.status == "insufficient_evidence" and mismatch.signals == []
    assert "currencies do not match exactly" in mismatch.missing_evidence[0]


def test_sample_relative_rule_exposes_frozen_tukey_math(extracted: ExtractedDataset) -> None:
    result = sample_relative_high_amount(extracted)
    assert result.parameters == {
        "multiplier": 1.5,
        "minimum_group_size": 4,
        "currency_conversion": False,
        "evaluated_groups": 1,
        "group_statistics": "USD:n=10,q1=0.0,q3=20.0,iqr=20.0,threshold=50.00",
    }
    assert len(result.signals) == 1
    assert "100.0 USD is strictly above Tukey threshold 50.00" in result.signals[0].message


class RecordingModels:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def test_model_prompt_limit_makes_zero_calls() -> None:
    models = RecordingModels(SimpleNamespace(text="{}", parsed=None, usage_metadata=None))
    client = SimpleNamespace(models=models)
    payload = {"bounded": "x" * MAX_PROMPT_BYTES}

    result = GeminiSummarizer(client, "test-model").summarize(payload, set())

    assert result.gemini.status == "configuration_error"
    assert result.metadata.invoked is False
    assert result.metadata.call_count == 0
    assert models.calls == []


def test_model_rejects_oversize_or_schema_invalid_output_without_retry() -> None:
    for response in (
        SimpleNamespace(text="x" * (MAX_RESPONSE_BYTES + 1), parsed=None, usage_metadata=None),
        SimpleNamespace(
            text=json.dumps(
                {
                    "summary": "candidate",
                    "candidate_findings": [
                        {"title": "candidate", "explanation": "candidate", "evidence_refs": []}
                    ],
                    "missing_evidence": [],
                    "limitations": ["synthetic only"],
                }
            ),
            parsed=None,
            usage_metadata=None,
        ),
    ):
        models = RecordingModels(response)
        result = GeminiSummarizer(SimpleNamespace(models=models), "test-model").summarize({}, set())
        assert result.gemini.status == "invalid_output"
        assert result.gemini.candidate_findings == []
        assert result.metadata.call_count == 1
        assert len(models.calls) == 1


def test_static_openapi_validates_real_configuration_failure_response(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "VERTEX_GEMINI_MODEL",
        "GOOGLE_GENAI_USE_VERTEXAI",
    ):
        monkeypatch.delenv(name, raising=False)
    response = AnalysisService().analyze().model_dump(mode="json")
    contract = yaml.safe_load((default_project_root() / "contracts" / "openapi.yaml").read_text(encoding="utf-8"))
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/components/schemas/AnalysisResponse",
        "components": contract["components"],
    }
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(response)
