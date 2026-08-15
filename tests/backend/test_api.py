from __future__ import annotations

import hashlib
import asyncio

import httpx

from backend.app.gemini import GeminiResult
from backend.app.loader import SOURCE_PATHS, default_project_root
from backend.app.loader import PipelineError
from backend.app.main import app, get_analysis_service
from backend.app.models import GeminiFailure, GeminiSuccess, ModelMetadata
from backend.app.service import AnalysisService


def source_hashes() -> dict[str, str]:
    root = default_project_root()
    return {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for _, relative in SOURCE_PATHS
    }


def post_demo() -> httpx.Response:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/api/v1/analyze-demo")

    return asyncio.run(request())


class FixedSummarizer:
    def __init__(self, success: bool = False) -> None:
        self.calls = 0
        self.success = success

    def summarize(self, payload, allowed_evidence):
        self.calls += 1
        evidence_ref = next(iter(allowed_evidence))
        if self.success:
            gemini = GeminiSuccess(
                summary="Bounded candidate summary.",
                candidate_findings=[
                    {
                        "title": "Candidate review item",
                        "explanation": "A supplied synthetic fact may be reviewed.",
                        "evidence_refs": [evidence_ref],
                    }
                ],
                missing_evidence=[],
                limitations=["Candidate model text is non-authoritative."],
            )
            valid = True
        else:
            gemini = GeminiFailure(
                status="provider_error",
                message="The Vertex AI provider request failed.",
                limitations=["No model findings are available because the single provider call failed."],
            )
            valid = False
        return GeminiResult(
            gemini=gemini,
            metadata=ModelMetadata(
                model="fake-model", invoked=True, call_count=1, output_validated=valid, latency_ms=1
            ),
        )


def test_endpoint_returns_contract_sections_and_model_success() -> None:
    fake = FixedSummarizer(success=True)
    async def override_service():
        return AnalysisService(fake)

    app.dependency_overrides[get_analysis_service] = override_service
    try:
        response = post_demo()
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "analysis_id",
        "source",
        "observed_facts",
        "rule_results",
        "evidence_index",
        "gemini",
        "model_metadata",
        "limitations",
    }
    assert body["gemini"]["status"] == "success"
    assert body["gemini"]["candidate_findings"][0]["evidence_refs"][0] in {
        record["evidence_id"] for record in body["evidence_index"]
    }
    assert fake.calls == 1


def test_model_failure_keeps_deterministic_report_and_source_is_immutable() -> None:
    before = source_hashes()
    fake = FixedSummarizer(success=False)
    async def override_service():
        return AnalysisService(fake)

    app.dependency_overrides[get_analysis_service] = override_service
    try:
        response = post_demo()
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert len(body["rule_results"]) == 5
    assert body["observed_facts"]
    assert body["gemini"]["status"] == "provider_error"
    assert body["gemini"]["candidate_findings"] == []
    assert fake.calls == 1
    assert source_hashes() == before


def test_openapi_exposes_bodyless_demo_operation() -> None:
    operation = app.openapi()["paths"]["/api/v1/analyze-demo"]["post"]
    assert "requestBody" not in operation
    assert set(operation["responses"]) >= {"200", "500"}


def test_deterministic_pipeline_failure_is_typed_sanitized_500() -> None:
    class BrokenService:
        def analyze(self):
            raise PipelineError("SOURCE_INVALID_JSON", "An approved synthetic source is not valid UTF-8 JSON.")

    async def override_service():
        return BrokenService()

    app.dependency_overrides[get_analysis_service] = override_service
    try:
        response = post_demo()
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "SOURCE_INVALID_JSON",
            "message": "An approved synthetic source is not valid UTF-8 JSON.",
            "model_called": False,
        }
    }
