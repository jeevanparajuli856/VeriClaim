"""In-memory deterministic analysis and response assembly."""

from __future__ import annotations

import hashlib
from typing import Any

from .extractor import extract_supported_dataset
from .gemini import GeminiSummarizer
from .loader import load_approved_sources
from .models import AnalysisResponse, EvidenceRecord
from .rules import run_all_rules

GLOBAL_LIMITATIONS = [
    "This local demonstration uses a small synthetic sample and does not establish healthcare validity or generalizability.",
    "Signals and Gemini text are investigation aids only; they do not determine fraud or make claim, payment, coverage, coding, medical-necessity, diagnostic, or clinical decisions.",
    "The extractor supports a narrow FHIR-shaped subset and does not claim base FHIR, profile, terminology, or CARIN conformance.",
]
MAX_EVIDENCE_SUMMARY = 500


class AnalysisService:
    def __init__(self, summarizer: GeminiSummarizer | None = None) -> None:
        self._summarizer = summarizer

    def analyze(self) -> AnalysisResponse:
        sources = load_approved_sources()
        dataset = extract_supported_dataset(sources)
        rule_results = run_all_rules(dataset)
        evidence_index = self._evidence_index(dataset.facts, rule_results)
        model_payload = {
            "observed_facts": [
                {
                    "evidence_id": fact.evidence_id,
                    "fact_type": fact.fact_type,
                    "value": fact.value,
                }
                for fact in dataset.facts
            ],
            "deterministic_rules": [
                {
                    "rule_id": rule.rule_id,
                    "status": rule.status,
                    "formula": rule.formula,
                    "signals": [
                        {
                            "evidence_id": signal.evidence_id,
                            "signal_type": signal.signal_type,
                            "message": signal.message,
                            "evidence_refs": signal.evidence_refs,
                        }
                        for signal in rule.signals
                    ],
                    "missing_evidence": rule.missing_evidence,
                    "limitations": rule.limitations,
                }
                for rule in rule_results
            ],
            "limitations": GLOBAL_LIMITATIONS,
        }
        allowed_evidence = {record.evidence_id for record in evidence_index}
        summarizer = self._summarizer or GeminiSummarizer.from_environment()
        model_result = summarizer.summarize(model_payload, allowed_evidence)
        analysis_digest = hashlib.sha256(
            "|".join(source.metadata.sha256 for source in sources.values()).encode("ascii")
        ).hexdigest()[:24]
        return AnalysisResponse(
            analysis_id=f"demo-{analysis_digest}",
            source=dataset.source,
            observed_facts=dataset.facts,
            rule_results=rule_results,
            evidence_index=evidence_index,
            gemini=model_result.gemini,
            model_metadata=model_result.metadata,
            limitations=GLOBAL_LIMITATIONS,
        )

    @staticmethod
    def _evidence_index(facts: list[Any], rules: list[Any]) -> list[EvidenceRecord]:
        def fact_summary(fact: Any) -> str:
            prefix = f"{fact.fact_type}: "
            value = str(fact.value)
            remaining = MAX_EVIDENCE_SUMMARY - len(prefix)
            if len(value) > remaining:
                value = f"{value[: remaining - 1]}…"
            return f"{prefix}{value}"

        records = [
            EvidenceRecord(
                evidence_id=fact.evidence_id,
                kind="fact",
                summary=fact_summary(fact),
                source_refs=[fact.evidence_id],
            )
            for fact in facts
        ]
        for rule in rules:
            records.extend(
                EvidenceRecord(
                    evidence_id=signal.evidence_id,
                    kind="signal",
                    summary=signal.message,
                    source_refs=signal.evidence_refs,
                )
                for signal in rule.signals
            )
        return records
