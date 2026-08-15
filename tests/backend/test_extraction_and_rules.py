from __future__ import annotations

from dataclasses import replace
from datetime import date

from backend.app.extractor import ExtractedDataset, ReferenceValue
from backend.app.rules import (
    coverage_date_bounds,
    duplicate_and_repetition,
    observed_amount_relationship,
    reference_integrity,
    sample_relative_high_amount,
)


def test_approved_sample_extracts_only_supported_bounded_facts(extracted: ExtractedDataset) -> None:
    assert extracted.source.resource_counts.model_dump() == {
        "Patient": 1,
        "Coverage": 4,
        "ExplanationOfBenefit": 10,
    }
    assert len(extracted.facts) == 155
    assert all(fact.evidence_id == f"ev:{fact.source_alias}:{fact.json_pointer}" for fact in extracted.facts)
    assert {fact.fact_type for fact in extracted.facts} <= {
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
    }
    serialized = " ".join(str(fact.value) for fact in extracted.facts)
    assert "Gabapentin" not in serialized
    assert "ATORVASTATIN" not in serialized


def test_reference_rule_no_signal_and_wrong_type_signal(extracted: ExtractedDataset) -> None:
    assert reference_integrity(extracted).signals == []
    eob = extracted.eobs[0]
    broken_patient = ReferenceValue("Coverage/not-a-patient", eob.patient.evidence_id, eob.identity_evidence_id)
    changed = replace(extracted, eobs=[replace(eob, patient=broken_patient), *extracted.eobs[1:]])
    result = reference_integrity(changed)
    assert [signal.signal_type for signal in result.signals] == ["wrong_reference_type"]
    assert result.signals[0].evidence_refs == [eob.patient.evidence_id]


def test_date_rule_reports_missing_bounds_and_detects_present_bound(extracted: ExtractedDataset) -> None:
    original = coverage_date_bounds(extracted)
    assert original.status == "insufficient_evidence"
    assert len(original.missing_evidence) == 10
    part_d = extracted.coverages[3]
    changed_coverage = replace(
        part_d,
        start=date(2017, 1, 1),
        start_evidence_id=part_d.identity_evidence_id,
    )
    changed = replace(extracted, coverages=[*extracted.coverages[:3], changed_coverage])
    result = coverage_date_bounds(changed)
    assert result.status == "completed"
    assert len(result.signals) == 10
    assert all(signal.signal_type == "service_date_outside_present_coverage_bounds" for signal in result.signals)


def test_repeat_rule_sample_signal_and_exact_duplicate(extracted: ExtractedDataset) -> None:
    sample = duplicate_and_repetition(extracted)
    assert [signal.signal_type for signal in sample.signals] == ["repeated_opaque_product_service_code"]
    eob = extracted.eobs[0]
    duplicate_item = replace(eob.items[0], path_key=f"{eob.items[0].path_key}-copy")
    changed = replace(extracted, eobs=[replace(eob, items=(*eob.items, duplicate_item)), *extracted.eobs[1:]])
    result = duplicate_and_repetition(changed)
    assert "exact_duplicate_items" in {signal.signal_type for signal in result.signals}
    assert [signal.evidence_id for signal in result.signals] == [
        f"sig:REPEAT-001:{index:04d}" for index in range(1, len(result.signals) + 1)
    ]


def test_amount_rule_signal_no_signal_and_missing_components(extracted: ExtractedDataset) -> None:
    sample = observed_amount_relationship(extracted)
    assert len(sample.signals) == 3
    first_eob_only = replace(extracted, eobs=[extracted.eobs[0]])
    assert observed_amount_relationship(first_eob_only).signals == []
    item = extracted.eobs[0].items[0]
    missing = replace(item, adjudications=tuple(component for component in item.adjudications if component.code != "drugcost"))
    changed = replace(extracted, eobs=[replace(extracted.eobs[0], items=(missing,))])
    result = observed_amount_relationship(changed)
    assert result.status == "insufficient_evidence"
    assert result.signals == []
    assert "not each present exactly once" in result.missing_evidence[0]


def test_outlier_rule_frozen_sample_math_no_signal_and_missing_evidence(extracted: ExtractedDataset) -> None:
    sample = sample_relative_high_amount(extracted)
    assert len(sample.signals) == 1
    assert "threshold 50" in sample.signals[0].message
    four_eobs = replace(extracted, eobs=extracted.eobs[:4])
    assert sample_relative_high_amount(four_eobs).signals == []
    missing_item = replace(extracted.eobs[0].items[0], adjudications=())
    missing = replace(extracted, eobs=[replace(extracted.eobs[0], items=(missing_item,))])
    result = sample_relative_high_amount(missing)
    assert result.status == "insufficient_evidence"
    assert any("drugcost is not present exactly once" in text for text in result.missing_evidence)
