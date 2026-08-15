from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from backend.app.gemini import GeminiSummarizer


class FakeModels:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.calls: list[dict] = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.models = FakeModels(response, error)


def response_for(evidence_ref: str):
    payload = {
        "summary": "One deterministic signal is available for human investigation.",
        "candidate_findings": [
            {
                "title": "Candidate relationship",
                "explanation": "The supplied deterministic signal merits review without implying a decision.",
                "evidence_refs": [evidence_ref],
            }
        ],
        "missing_evidence": ["No additional external evidence was supplied."],
        "limitations": ["This is candidate text for a synthetic demonstration."],
    }
    return SimpleNamespace(
        text=json.dumps(payload),
        parsed=None,
        usage_metadata=SimpleNamespace(prompt_token_count=100, candidates_token_count=50),
    )


def test_configuration_missing_makes_zero_calls() -> None:
    result = GeminiSummarizer(None, None).summarize({}, set())
    assert result.gemini.status == "configuration_error"
    assert result.metadata.call_count == 0
    assert result.metadata.invoked is False


def test_valid_structured_output_and_known_evidence_use_one_no_tools_call() -> None:
    evidence_ref = "sig:REF-001:0001"
    client = FakeClient(response_for(evidence_ref))
    result = GeminiSummarizer(client, "gemini-test").summarize(
        {"observed_facts": [], "deterministic_rules": []}, {evidence_ref}
    )
    assert result.gemini.status == "success"
    assert result.metadata.call_count == 1
    assert result.metadata.output_validated is True
    assert result.metadata.input_tokens == 100
    assert len(client.models.calls) == 1
    assert "tools" not in client.models.calls[0]["config"].model_dump(exclude_none=True)


@pytest.mark.parametrize(
    ("response", "error", "expected"),
    [
        (None, TimeoutError("private timeout detail"), "timeout"),
        (None, RuntimeError("private provider detail"), "provider_error"),
        (SimpleNamespace(text="not-json", parsed=None, usage_metadata=None), None, "invalid_output"),
    ],
)
def test_call_failures_are_sanitized_and_never_retried(response, error, expected: str) -> None:
    client = FakeClient(response, error)
    result = GeminiSummarizer(client, "gemini-test").summarize({}, set())
    assert result.gemini.status == expected
    assert result.gemini.candidate_findings == []
    assert "private" not in result.gemini.message
    assert result.metadata.call_count == 1
    assert len(client.models.calls) == 1


def test_unknown_evidence_rejects_entire_model_portion_without_retry() -> None:
    client = FakeClient(response_for("sig:REF-001:9999"))
    result = GeminiSummarizer(client, "gemini-test").summarize({}, {"sig:REF-001:0001"})
    assert result.gemini.status == "invalid_evidence"
    assert result.gemini.candidate_findings == []
    assert result.metadata.output_validated is False
    assert len(client.models.calls) == 1


def test_prompt_contains_minimized_data_and_not_environment_values(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "private-project-must-not-be-sent")
    client = FakeClient(response_for("ev:patient:/id"))
    result = GeminiSummarizer(client, "gemini-test").summarize(
        {"observed_facts": [{"evidence_id": "ev:patient:/id", "fact_type": "resource_id", "value": "synthetic"}]},
        {"ev:patient:/id"},
    )
    assert result.gemini.status == "success"
    sent = client.models.calls[0]["contents"]
    assert "private-project-must-not-be-sent" not in sent
    assert "SUPPLIED_SYNTHETIC_DATA_JSON" in sent
