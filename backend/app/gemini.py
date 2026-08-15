"""One-call, no-tools Google Gen AI SDK boundary for Vertex AI Gemini."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .models import GeminiFailure, GeminiOutput, GeminiSuccess, ModelMetadata

PROMPT_VERSION = "demo-001-v1"
SCHEMA_VERSION = "demo-001-v1"
MAX_PROMPT_BYTES = 128 * 1024
MAX_RESPONSE_BYTES = 64 * 1024
MAX_OUTPUT_TOKENS = 2_048
TIMEOUT_MS = 30_000

SYSTEM_INSTRUCTION = """You are a bounded investigation summarizer for a local synthetic-data demonstration.
Use only the JSON data supplied below. Explain deterministic signals, correlate supplied facts, identify missing
evidence, and state limitations. Every candidate finding must cite one or more supplied evidence IDs. Findings
are non-authoritative candidates. Do not determine fraud; approve or deny claims; make payment, coverage,
coding, medical-necessity, diagnostic, or clinical decisions; request external facts; use tools; or modify data.
Return only JSON matching the supplied response schema."""
USER_CONTENT_LABEL = "SUPPLIED_SYNTHETIC_DATA_JSON:\n"


@dataclass(frozen=True)
class GeminiResult:
    gemini: GeminiSuccess | GeminiFailure
    metadata: ModelMetadata


class GeminiSummarizer:
    """Owns exactly zero or one SDK invocation for a single summarize call."""

    def __init__(self, client: Any | None, model: str | None, configuration_message: str | None = None) -> None:
        self._client = client
        self._model = model
        self._configuration_message = configuration_message

    @classmethod
    def from_environment(cls) -> "GeminiSummarizer":
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        model = os.getenv("VERTEX_GEMINI_MODEL")
        use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
        if not (project and location and model and use_vertex) or len(model) > 160:
            return cls(None, model if model and len(model) <= 160 else None, "Vertex AI model configuration is unavailable.")
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(
                vertexai=True,
                project=project,
                location=location,
                http_options=types.HttpOptions(timeout=TIMEOUT_MS),
            )
        except Exception:
            return cls(None, model, "The Google Gen AI SDK could not be initialized.")
        return cls(client, model)

    def summarize(self, payload: dict[str, Any], allowed_evidence: set[str]) -> GeminiResult:
        if self._client is None or self._model is None:
            return self._failure(
                "configuration_error",
                self._configuration_message or "Vertex AI model configuration is unavailable.",
                invoked=False,
                call_count=0,
            )
        prompt_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        contents = f"{USER_CONTENT_LABEL}{prompt_json}"
        request_bytes = len(SYSTEM_INSTRUCTION.encode("utf-8")) + len(contents.encode("utf-8"))
        if request_bytes > MAX_PROMPT_BYTES:
            return self._failure(
                "configuration_error",
                "The minimized model request exceeds the configured prompt limit.",
                invoked=False,
                call_count=0,
            )
        started = time.monotonic()
        try:
            from google.genai import types

            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_json_schema=GeminiOutput.model_json_schema(),
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    temperature=0.1,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=0,
                        include_thoughts=False,
                    ),
                ),
            )
        except Exception as exc:
            latency = round((time.monotonic() - started) * 1000)
            is_timeout = isinstance(exc, TimeoutError) or "timeout" in type(exc).__name__.lower()
            return self._failure(
                "timeout" if is_timeout else "provider_error",
                "The Vertex AI request timed out." if is_timeout else "The Vertex AI provider request failed.",
                invoked=True,
                call_count=1,
                latency_ms=latency,
            )
        latency = round((time.monotonic() - started) * 1000)
        raw_text = getattr(response, "text", None)
        if raw_text is not None and (
            not isinstance(raw_text, str) or len(raw_text.encode("utf-8")) > MAX_RESPONSE_BYTES
        ):
            return self._failure(
                "invalid_output",
                "Gemini returned structured content outside the accepted output boundary.",
                invoked=True,
                call_count=1,
                latency_ms=latency,
                usage=response,
            )
        try:
            parsed = getattr(response, "parsed", None)
            if isinstance(parsed, GeminiOutput):
                output = parsed
            elif isinstance(parsed, dict):
                output = GeminiOutput.model_validate(parsed)
            elif isinstance(raw_text, str):
                output = GeminiOutput.model_validate_json(raw_text)
            else:
                raise ValueError("structured response missing")
        except (ValidationError, ValueError, TypeError, json.JSONDecodeError):
            return self._failure(
                "invalid_output",
                "Gemini returned content that did not match the required structured schema.",
                invoked=True,
                call_count=1,
                latency_ms=latency,
                usage=response,
            )
        cited = {ref for finding in output.candidate_findings for ref in finding.evidence_refs}
        if not cited.issubset(allowed_evidence):
            return self._failure(
                "invalid_evidence",
                "Gemini cited evidence that was not supplied for this analysis.",
                invoked=True,
                call_count=1,
                latency_ms=latency,
                usage=response,
            )
        return GeminiResult(
            gemini=GeminiSuccess(status="success", **output.model_dump()),
            metadata=self._metadata(
                invoked=True,
                call_count=1,
                output_validated=True,
                latency_ms=latency,
                usage=response,
            ),
        )

    def _failure(
        self,
        status: str,
        message: str,
        *,
        invoked: bool,
        call_count: int,
        latency_ms: int | None = None,
        usage: Any | None = None,
    ) -> GeminiResult:
        limitation = {
            "configuration_error": "No model findings are available because model configuration was unavailable.",
            "timeout": "No model findings are available because the single model call timed out.",
            "provider_error": "No model findings are available because the single provider call failed.",
            "invalid_output": "No model findings are available because the complete model output was rejected.",
            "invalid_evidence": "No model findings are available because model citations did not resolve.",
        }[status]
        return GeminiResult(
            gemini=GeminiFailure(status=status, message=message, limitations=[limitation]),  # type: ignore[arg-type]
            metadata=self._metadata(
                invoked=invoked,
                call_count=call_count,
                output_validated=False,
                latency_ms=latency_ms,
                usage=usage,
            ),
        )

    def _metadata(
        self,
        *,
        invoked: bool,
        call_count: int,
        output_validated: bool,
        latency_ms: int | None,
        usage: Any | None,
    ) -> ModelMetadata:
        usage_metadata = getattr(usage, "usage_metadata", None) if usage is not None else None
        input_tokens = getattr(usage_metadata, "prompt_token_count", None)
        output_tokens = getattr(usage_metadata, "candidates_token_count", None)
        return ModelMetadata(
            model=self._model,
            invoked=invoked,
            call_count=call_count,
            output_validated=output_validated,
            latency_ms=latency_ms,
            input_tokens=input_tokens if isinstance(input_tokens, int) and input_tokens >= 0 else None,
            output_tokens=output_tokens if isinstance(output_tokens, int) and output_tokens >= 0 else None,
        )
