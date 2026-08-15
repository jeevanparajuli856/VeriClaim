"""Five transparent, deterministic, terminology-agnostic anomaly checks."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from statistics import median

from .extractor import (
    AmountComponent,
    CoverageRecord,
    ExtractedDataset,
    ItemRecord,
    ReferenceValue,
)
from .models import DeterministicSignal, RuleResult

REFERENCE_RE = re.compile(r"^(Patient|Coverage)/([^/]+)$")
AMOUNT_TOLERANCE = Decimal("0.01")
COMMON_LIMITATION = "Signals are informational review aids for this small synthetic sample, not healthcare decisions."


@dataclass(frozen=True)
class PendingSignal:
    key: tuple[str, ...]
    signal_type: str
    priority: str
    message: str
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...]


def _finalize(rule_id: str, pending: list[PendingSignal]) -> list[DeterministicSignal]:
    ordered = sorted(pending, key=lambda signal: signal.key)
    return [
        DeterministicSignal(
            evidence_id=f"sig:{rule_id}:{index:04d}",
            rule_id=rule_id,
            signal_type=signal.signal_type,
            priority=signal.priority,
            message=signal.message,
            evidence_refs=list(dict.fromkeys(signal.evidence_refs))[:20],
            limitations=list(dict.fromkeys(signal.limitations)),
        )
        for index, signal in enumerate(ordered, start=1)
    ]


def _resolve(dataset: ExtractedDataset, reference: str | None, expected: str) -> list[str]:
    if not reference:
        return []
    match = REFERENCE_RE.fullmatch(reference)
    if not match or match.group(1) != expected:
        return []
    return dataset.identity_index.get((expected, match.group(2)), [])


def _reference_issue(
    dataset: ExtractedDataset, reference: ReferenceValue, expected: str, key_prefix: str
) -> PendingSignal | None:
    evidence = reference.evidence_id or reference.owner_evidence_id
    value = reference.value
    if value is None:
        return PendingSignal(
            (key_prefix, "missing"),
            "missing_reference",
            "review",
            f"A required local {expected} reference is missing.",
            (evidence,),
            ("Only the supplied local resource index was evaluated; no external lookup was attempted.",),
        )
    match = REFERENCE_RE.fullmatch(value)
    if not match:
        return PendingSignal(
            (key_prefix, "malformed", value),
            "malformed_reference",
            "review",
            f"The observed reference is not a local relative {expected}/<id> reference.",
            (evidence,),
            ("Reference syntax is checked narrowly; no general FHIR conformance is inferred.",),
        )
    if match.group(1) != expected:
        return PendingSignal(
            (key_prefix, "wrong_type", value),
            "wrong_reference_type",
            "review",
            f"The observed reference names {match.group(1)} where {expected} is required by this supported subset.",
            (evidence,),
            ("This is a supported-subset identity check, not comprehensive FHIR validation.",),
        )
    matches = dataset.identity_index.get((expected, match.group(2)), [])
    if not matches:
        return PendingSignal(
            (key_prefix, "unresolved", value),
            "unresolved_reference",
            "review",
            "The observed local reference does not resolve in the supplied source set.",
            (evidence,),
            ("Only the three approved synthetic files were searched.",),
        )
    if len(matches) > 1:
        return PendingSignal(
            (key_prefix, "ambiguous", value),
            "ambiguous_reference",
            "review",
            "The observed local reference resolves to more than one supplied resource identity.",
            tuple([evidence, *matches]),
            ("Duplicate resource identities are preserved rather than silently overwritten.",),
        )
    return None


def reference_integrity(dataset: ExtractedDataset) -> RuleResult:
    pending: list[PendingSignal] = []
    for coverage_index, coverage in enumerate(dataset.coverages):
        issue = _reference_issue(dataset, coverage.beneficiary, "Patient", f"coverage:{coverage_index:04d}")
        if issue:
            pending.append(issue)
    for eob_index, eob in enumerate(dataset.eobs):
        issue = _reference_issue(dataset, eob.patient, "Patient", f"eob:{eob_index:04d}:patient")
        if issue:
            pending.append(issue)
        if not eob.coverage_refs:
            pending.append(
                PendingSignal(
                    (f"eob:{eob_index:04d}:coverage", "missing"),
                    "missing_reference",
                    "review",
                    "The EOB has no insurance Coverage reference in the supported subset.",
                    (eob.identity_evidence_id,),
                    ("Only insurance.coverage.reference is evaluated.",),
                )
            )
        for reference_index, reference in enumerate(eob.coverage_refs):
            issue = _reference_issue(
                dataset, reference, "Coverage", f"eob:{eob_index:04d}:coverage:{reference_index:04d}"
            )
            if issue:
                pending.append(issue)
    return RuleResult(
        rule_id="REF-001",
        name="Local reference integrity",
        status="completed",
        description="Checks required Patient and Coverage references against the supplied one-to-many identity index.",
        formula="A local <expected-type>/<id> reference must resolve to exactly one supplied resource.",
        parameters={"external_lookup": False, "accepted_reference_form": "<expected-resourceType>/<id>"},
        signals=_finalize("REF-001", pending),
        missing_evidence=[],
        limitations=["No URL is dereferenced and no comprehensive FHIR reference validation is claimed."],
    )


def coverage_date_bounds(dataset: ExtractedDataset) -> RuleResult:
    pending: list[PendingSignal] = []
    missing: list[str] = []
    compared = 0
    coverage_by_evidence = {coverage.identity_evidence_id: coverage for coverage in dataset.coverages}
    for eob in dataset.eobs:
        for item in eob.items:
            if item.service_date is None or item.service_date_evidence_id is None:
                missing.append(f"{item.path_key}: item.servicedDate is absent; billablePeriod was not substituted.")
                continue
            if not item.coverage_refs:
                missing.append(f"{item.path_key}: no insurance Coverage reference is available for date comparison.")
                continue
            for reference in item.coverage_refs:
                matches = _resolve(dataset, reference.value, "Coverage")
                if len(matches) != 1:
                    missing.append(f"{item.path_key}: a Coverage reference did not resolve uniquely for date comparison.")
                    continue
                coverage = coverage_by_evidence[matches[0]]
                if coverage.start is None and coverage.end is None:
                    missing.append(f"{item.path_key}: resolved Coverage has no period bounds.")
                    continue
                compared += 1
                evidence = [item.service_date_evidence_id, reference.evidence_id or reference.owner_evidence_id]
                reasons: list[str] = []
                if coverage.start is not None:
                    evidence.append(coverage.start_evidence_id or coverage.identity_evidence_id)
                    if item.service_date < coverage.start:
                        reasons.append("before the present Coverage start")
                if coverage.end is not None:
                    evidence.append(coverage.end_evidence_id or coverage.identity_evidence_id)
                    if item.service_date > coverage.end:
                        reasons.append("after the present Coverage end")
                if reasons:
                    pending.append(
                        PendingSignal(
                            (item.path_key, coverage.id),
                            "service_date_outside_present_coverage_bounds",
                            "review",
                            f"Observed service date {item.service_date.isoformat()} is {' and '.join(reasons)}.",
                            tuple(evidence),
                            ("The comparison is inclusive and uses only bounds present in the supplied Coverage.",),
                        )
                    )
    return RuleResult(
        rule_id="DATE-001",
        name="Coverage date bounds",
        status="completed" if compared else "insufficient_evidence",
        description="Compares item.servicedDate inclusively with present bounds of uniquely resolved Coverages.",
        formula="signal when servicedDate < present start or servicedDate > present end",
        parameters={"inclusive": True, "billable_period_substitution": False, "comparisons": compared},
        signals=_finalize("DATE-001", pending),
        missing_evidence=sorted(set(missing)),
        limitations=["Observed dates alone do not establish coverage, payment, coding, or clinical conclusions."],
    )


def _selected(item: ItemRecord, system: str, code: str) -> list[AmountComponent]:
    return [component for component in item.adjudications if (component.system, component.code) == (system, code)]


def duplicate_and_repetition(dataset: ExtractedDataset) -> RuleResult:
    pending: list[PendingSignal] = []
    missing: list[str] = []
    signatures: dict[tuple[object, ...], list[tuple[ItemRecord, tuple[str, ...]]]] = defaultdict(list)
    repetitions: dict[tuple[str, str], list[tuple[ItemRecord, tuple[str, str]]]] = defaultdict(list)
    for eob in dataset.eobs:
        for item in eob.items:
            for system, code, system_eid, code_eid in item.products:
                repetitions[(system, code)].append((item, (system_eid, code_eid)))
            components: list[AmountComponent] = []
            for system, code in (
                ("http://terminology.hl7.org/CodeSystem/adjudication", "benefit"),
                ("http://hl7.org/fhir/us/carin-bb/CodeSystem/C4BBAdjudication", "paidbypatient"),
                ("http://hl7.org/fhir/us/carin-bb/CodeSystem/C4BBAdjudication", "drugcost"),
            ):
                found = _selected(item, system, code)
                if len(found) == 1:
                    components.append(found[0])
            usable_references = [reference.value for reference in item.coverage_refs if reference.value]
            if (
                not item.patient.value
                or not usable_references
                or item.service_date_text is None
                or len(item.products) != 1
                or len(components) != 3
            ):
                missing.append(f"{item.path_key}: exact-duplicate signature is incomplete or ambiguous.")
                continue
            system, code, system_eid, code_eid = item.products[0]
            amount_signature = tuple(
                sorted((component.code, str(component.value), component.currency) for component in components)
            )
            signature = (
                item.patient.value,
                tuple(sorted(usable_references)),
                item.service_date_text,
                system,
                code,
                amount_signature,
            )
            refs = [
                item.patient.evidence_id or item.patient.owner_evidence_id,
                *(reference.evidence_id or reference.owner_evidence_id for reference in item.coverage_refs),
                item.service_date_evidence_id or item.identity_evidence_id,
                system_eid,
                code_eid,
                *(eid for component in components for eid in (component.value_evidence_id, component.currency_evidence_id)),
            ]
            signatures[signature].append((item, tuple(refs)))
    for signature, members in signatures.items():
        distinct = {member.path_key for member, _ in members}
        if len(distinct) >= 2:
            pending.append(
                PendingSignal(
                    ("duplicate", repr(signature)),
                    "exact_duplicate_items",
                    "review",
                    f"{len(distinct)} distinct item source paths have the same exact supported-field signature.",
                    tuple(eid for _, refs in members for eid in refs),
                    ("Exact supported-field equality does not establish a duplicate claim or improper submission.",),
                )
            )
    for (system, code), members in repetitions.items():
        distinct = {member.path_key for member, _ in members}
        if len(distinct) >= 2:
            pending.append(
                PendingSignal(
                    ("repetition", system, code),
                    "repeated_opaque_product_service_code",
                    "information",
                    f"The exact opaque product/service system+code occurs on {len(distinct)} distinct sample items.",
                    tuple(eid for _, refs in members for eid in refs),
                    ("The code is not interpreted and repetition across this small sample is not generalized.",),
                )
            )
    return RuleResult(
        rule_id="REPEAT-001",
        name="Exact duplicate and opaque-code repetition",
        status="completed",
        description="Checks exact supported-field item signatures and exact system+code repetition across the sample.",
        formula="signal duplicate signatures or exact product/service system+code count >= 2",
        parameters={"minimum_count": 2, "near_match": False, "window": "entire supplied EOB sample"},
        signals=_finalize("REPEAT-001", pending),
        missing_evidence=sorted(set(missing)),
        limitations=["No code display, terminology membership, product meaning, or near-match semantics are inferred."],
    )


def observed_amount_relationship(dataset: ExtractedDataset) -> RuleResult:
    pending: list[PendingSignal] = []
    missing: list[str] = []
    evaluated = 0
    for eob in dataset.eobs:
        for item in eob.items:
            benefit = _selected(item, "http://terminology.hl7.org/CodeSystem/adjudication", "benefit")
            patient = _selected(
                item, "http://hl7.org/fhir/us/carin-bb/CodeSystem/C4BBAdjudication", "paidbypatient"
            )
            drugcost = _selected(item, "http://hl7.org/fhir/us/carin-bb/CodeSystem/C4BBAdjudication", "drugcost")
            if not (len(benefit) == len(patient) == len(drugcost) == 1):
                missing.append(f"{item.path_key}: benefit, paidbypatient, and drugcost are not each present exactly once.")
                continue
            components = (benefit[0], patient[0], drugcost[0])
            currencies = {component.currency for component in components}
            if len(currencies) != 1:
                missing.append(f"{item.path_key}: selected amount currencies do not match exactly.")
                continue
            evaluated += 1
            difference = abs(drugcost[0].value - (benefit[0].value + patient[0].value))
            if difference > AMOUNT_TOLERANCE:
                pending.append(
                    PendingSignal(
                        (item.path_key,),
                        "observed_amount_components_do_not_reconcile",
                        "review",
                        f"Observed drugcost differs from benefit + paidbypatient by {difference} {drugcost[0].currency}, exceeding 0.01.",
                        tuple(
                            eid
                            for component in components
                            for eid in (component.value_evidence_id, component.currency_evidence_id)
                        ),
                        ("Other components may exist and are intentionally not modeled by this narrow arithmetic check.",),
                    )
                )
    return RuleResult(
        rule_id="AMOUNT-001",
        name="Observed amount component relationship",
        status="completed" if evaluated else "insufficient_evidence",
        description="Compares three exactly selected, finite, same-currency adjudication components.",
        formula="abs(drugcost - (benefit + paidbypatient)) > 0.01",
        parameters={"tolerance": 0.01, "currency_conversion": False, "evaluated_items": evaluated},
        signals=_finalize("AMOUNT-001", pending),
        missing_evidence=sorted(set(missing)),
        limitations=["This narrow arithmetic relationship does not determine billed, allowed, paid, or correct amounts."],
    )


def _decimal_median(values: list[Decimal]) -> Decimal:
    return Decimal(str(median(values)))


def sample_relative_high_amount(dataset: ExtractedDataset) -> RuleResult:
    pending: list[PendingSignal] = []
    missing: list[str] = []
    groups: dict[str, list[tuple[Decimal, AmountComponent, ItemRecord]]] = defaultdict(list)
    for eob in dataset.eobs:
        for item in eob.items:
            components = _selected(
                item, "http://hl7.org/fhir/us/carin-bb/CodeSystem/C4BBAdjudication", "drugcost"
            )
            if len(components) != 1:
                missing.append(f"{item.path_key}: drugcost is not present exactly once for sample-relative analysis.")
                continue
            component = components[0]
            groups[component.currency].append((component.value, component, item))
    evaluated_groups = 0
    group_summaries: list[str] = []
    for currency, observations in sorted(groups.items()):
        if len(observations) < 4:
            missing.append(f"{currency}: fewer than four usable drugcost observations are available.")
            continue
        evaluated_groups += 1
        values = sorted(value for value, _, _ in observations)
        midpoint = len(values) // 2
        lower = values[:midpoint]
        upper = values[midpoint:] if len(values) % 2 == 0 else values[midpoint + 1 :]
        q1 = _decimal_median(lower)
        q3 = _decimal_median(upper)
        iqr = q3 - q1
        threshold = q3 + Decimal("1.5") * iqr
        group_summaries.append(
            f"{currency}:n={len(values)},q1={q1},q3={q3},iqr={iqr},threshold={threshold}"
        )
        for value, component, item in observations:
            if value > threshold:
                pending.append(
                    PendingSignal(
                        (currency, str(value), item.path_key),
                        "sample_relative_high_drugcost",
                        "information",
                        f"Observed drugcost {value} {currency} is strictly above Tukey threshold {threshold} (Q1={q1}, Q3={q3}, IQR={iqr}, n={len(values)}).",
                        (component.value_evidence_id, component.currency_evidence_id),
                        ("This threshold is relative only to the supplied small synthetic sample.",),
                    )
                )
    return RuleResult(
        rule_id="OUTLIER-001",
        name="Sample-relative high amount",
        status="completed" if evaluated_groups else "insufficient_evidence",
        description="Applies a frozen Tukey-hinge threshold independently to each exact-currency drugcost group.",
        formula="threshold = Q3 + 1.5 * (Q3 - Q1); signal when value > threshold; minimum n = 4",
        parameters={
            "multiplier": 1.5,
            "minimum_group_size": 4,
            "currency_conversion": False,
            "evaluated_groups": evaluated_groups,
            "group_statistics": "; ".join(group_summaries) or "none",
        },
        signals=_finalize("OUTLIER-001", pending),
        missing_evidence=sorted(set(missing)),
        limitations=["Small-sample quartiles are demonstrative and do not establish a population benchmark."],
    )


def run_all_rules(dataset: ExtractedDataset) -> list[RuleResult]:
    return [
        reference_integrity(dataset),
        coverage_date_bounds(dataset),
        duplicate_and_repetition(dataset),
        observed_amount_relationship(dataset),
        sample_relative_high_amount(dataset),
    ]
