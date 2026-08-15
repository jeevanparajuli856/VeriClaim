"""Validated public and model-boundary schemas for the local demo."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


FactValue = str | float | bool
RuleId = Literal["REF-001", "DATE-001", "REPEAT-001", "AMOUNT-001", "OUTLIER-001"]
GeminiFailureStatus = Literal[
    "configuration_error", "timeout", "provider_error", "invalid_output", "invalid_evidence"
]


class SourceFile(StrictModel):
    alias: Literal["patient", "coverage", "eob"]
    path: Literal[
        "dataset/patient_bbuser29999.json",
        "dataset/coverage_bundle_bbuser29999.json",
        "dataset/eob_bundle_bbuser29999.json",
    ]
    sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    size_bytes: Annotated[int, Field(ge=1, le=1_048_576)]


class ResourceCounts(StrictModel):
    Patient: Annotated[int, Field(ge=0)]
    Coverage: Annotated[int, Field(ge=0)]
    ExplanationOfBenefit: Annotated[int, Field(ge=0)]


class SourceMetadata(StrictModel):
    dataset_name: Literal["cms-blue-button-local-sample"] = "cms-blue-button-local-sample"
    synthetic: Literal[True] = True
    files: Annotated[list[SourceFile], Field(min_length=3, max_length=3)]
    resource_counts: ResourceCounts


class ObservedFact(StrictModel):
    evidence_id: Annotated[str, Field(pattern=r"^ev:(patient|coverage|eob):/.*$", max_length=640)]
    source_alias: Literal["patient", "coverage", "eob"]
    json_pointer: Annotated[str, Field(pattern=r"^/", max_length=512)]
    fact_type: Literal[
        "resource_id",
        "coverage_status",
        "beneficiary_reference",
        "coverage_period_start",
        "coverage_period_end",
        "patient_reference",
        "coverage_reference",
        "billable_period_start",
        "billable_period_end",
        "service_date",
        "product_service_system",
        "product_service_code",
        "adjudication_value",
        "adjudication_currency",
    ]
    value: FactValue


class DeterministicSignal(StrictModel):
    evidence_id: Annotated[
        str,
        Field(pattern=r"^sig:(REF-001|DATE-001|REPEAT-001|AMOUNT-001|OUTLIER-001):[0-9]{4}$", max_length=64),
    ]
    rule_id: RuleId
    signal_type: Annotated[str, Field(min_length=1, max_length=160)]
    priority: Literal["information", "review"]
    message: Annotated[str, Field(min_length=1, max_length=500)]
    evidence_refs: Annotated[list[str], Field(min_length=1, max_length=20)]
    limitations: Annotated[list[str], Field(min_length=1, max_length=10)]

    @field_validator("evidence_refs", "limitations")
    @classmethod
    def unique_values(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("values must be unique")
        return value


class RuleResult(StrictModel):
    rule_id: RuleId
    name: Annotated[str, Field(min_length=1, max_length=160)]
    status: Literal["completed", "insufficient_evidence"]
    description: Annotated[str, Field(min_length=1, max_length=500)]
    formula: Annotated[str, Field(min_length=1, max_length=500)]
    parameters: dict[str, str | float | int | bool]
    signals: Annotated[list[DeterministicSignal], Field(max_length=500)]
    missing_evidence: Annotated[list[str], Field(max_length=500)]
    limitations: Annotated[list[str], Field(min_length=1, max_length=20)]

    @field_validator("missing_evidence", "limitations")
    @classmethod
    def unique_rule_text(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("values must be unique")
        return value


class EvidenceRecord(StrictModel):
    evidence_id: Annotated[
        str,
        Field(
            pattern=r"^(ev:(patient|coverage|eob):/.*|sig:(REF-001|DATE-001|REPEAT-001|AMOUNT-001|OUTLIER-001):[0-9]{4})$",
            max_length=640,
        ),
    ]
    kind: Literal["fact", "signal"]
    summary: Annotated[str, Field(min_length=1, max_length=500)]
    source_refs: Annotated[list[str], Field(max_length=20)]


class CandidateFinding(StrictModel):
    title: Annotated[str, Field(min_length=1, max_length=160)]
    explanation: Annotated[str, Field(min_length=1, max_length=1000)]
    evidence_refs: Annotated[list[str], Field(min_length=1, max_length=10)]

    @field_validator("evidence_refs")
    @classmethod
    def unique_evidence(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("evidence references must be unique")
        return value


class GeminiOutput(StrictModel):
    """The exact structured content requested from Gemini."""

    summary: Annotated[str, Field(min_length=1, max_length=2000)]
    candidate_findings: Annotated[list[CandidateFinding], Field(max_length=5)]
    missing_evidence: Annotated[list[Annotated[str, Field(min_length=1, max_length=500)]], Field(max_length=10)]
    limitations: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=500)]], Field(min_length=1, max_length=10)
    ]

    @field_validator("missing_evidence", "limitations")
    @classmethod
    def unique_model_text(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("values must be unique")
        return value


class GeminiSuccess(GeminiOutput):
    status: Literal["success"] = "success"


class GeminiFailure(StrictModel):
    status: GeminiFailureStatus
    message: Annotated[str, Field(min_length=1, max_length=500)]
    candidate_findings: list[CandidateFinding] = Field(default_factory=list, max_length=0)
    missing_evidence: Annotated[list[str], Field(max_length=10)] = Field(default_factory=list)
    limitations: Annotated[list[str], Field(min_length=1, max_length=10)]


class ModelMetadata(StrictModel):
    provider: Literal["vertex-ai"] = "vertex-ai"
    sdk: Literal["google-genai"] = "google-genai"
    model: Annotated[str | None, Field(max_length=160)]
    prompt_version: Annotated[str, Field(min_length=1, max_length=64)] = "demo-001-v1"
    response_schema_version: Annotated[str, Field(min_length=1, max_length=64)] = "demo-001-v1"
    invoked: bool
    call_count: Annotated[int, Field(ge=0, le=1)]
    output_validated: bool
    latency_ms: Annotated[int | None, Field(ge=0)] = None
    input_tokens: Annotated[int | None, Field(ge=0)] = None
    output_tokens: Annotated[int | None, Field(ge=0)] = None


class AnalysisResponse(StrictModel):
    analysis_id: Annotated[str, Field(min_length=1, max_length=128)]
    source: SourceMetadata
    observed_facts: Annotated[list[ObservedFact], Field(max_length=2000)]
    rule_results: Annotated[list[RuleResult], Field(min_length=5, max_length=5)]
    evidence_index: Annotated[list[EvidenceRecord], Field(max_length=2500)]
    gemini: GeminiSuccess | GeminiFailure
    model_metadata: ModelMetadata
    limitations: Annotated[list[str], Field(min_length=1, max_length=20)]


class DeterministicPipelineError(StrictModel):
    code: Literal[
        "SOURCE_UNAVAILABLE",
        "SOURCE_TOO_LARGE",
        "SOURCE_INVALID_JSON",
        "SOURCE_SHAPE_UNSUPPORTED",
        "EXTRACTION_LIMIT_EXCEEDED",
    ]
    message: Annotated[str, Field(min_length=1, max_length=500)]
    model_called: Literal[False] = False


class DeterministicPipelineErrorResponse(StrictModel):
    error: DeterministicPipelineError
