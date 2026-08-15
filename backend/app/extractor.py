"""Bounded extraction for the explicitly supported FHIR R4 subset."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from .loader import LoadedSource, PipelineError
from .models import ObservedFact, ResourceCounts, SourceMetadata

MAX_BUNDLE_ENTRIES = 100
MAX_EOB_ITEMS = 100
MAX_ADJUDICATIONS = 32
MAX_CODINGS = 16
MAX_STRING = 2_048
MAX_OBSERVED_FACTS = 2_000

BASE_ADJUDICATION = "http://terminology.hl7.org/CodeSystem/adjudication"
C4BB_ADJUDICATION = "http://hl7.org/fhir/us/carin-bb/CodeSystem/C4BBAdjudication"
SELECTED_CATEGORIES = {
    (BASE_ADJUDICATION, "benefit"),
    (C4BB_ADJUDICATION, "paidbypatient"),
    (C4BB_ADJUDICATION, "drugcost"),
}


@dataclass(frozen=True)
class ReferenceValue:
    value: str | None
    evidence_id: str | None
    owner_evidence_id: str


@dataclass(frozen=True)
class CoverageRecord:
    id: str
    identity_evidence_id: str
    beneficiary: ReferenceValue
    start: date | None
    start_evidence_id: str | None
    end: date | None
    end_evidence_id: str | None


@dataclass(frozen=True)
class AmountComponent:
    system: str
    code: str
    value: Decimal
    currency: str
    value_evidence_id: str
    currency_evidence_id: str


@dataclass(frozen=True)
class ItemRecord:
    path_key: str
    identity_evidence_id: str
    patient: ReferenceValue
    coverage_refs: tuple[ReferenceValue, ...]
    service_date: date | None
    service_date_text: str | None
    service_date_evidence_id: str | None
    products: tuple[tuple[str, str, str, str], ...]
    adjudications: tuple[AmountComponent, ...]


@dataclass(frozen=True)
class EobRecord:
    id: str
    identity_evidence_id: str
    patient: ReferenceValue
    coverage_refs: tuple[ReferenceValue, ...]
    items: tuple[ItemRecord, ...]


@dataclass
class ExtractedDataset:
    source: SourceMetadata
    facts: list[ObservedFact]
    patient_ids: list[tuple[str, str]]
    coverages: list[CoverageRecord]
    eobs: list[EobRecord]
    identity_index: dict[tuple[str, str], list[str]] = field(default_factory=dict)


def _pointer(alias: str, pointer: str) -> str:
    return f"ev:{alias}:{pointer}"


def _require_string(value: Any, label: str, *, required: bool = True) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value or len(value) > MAX_STRING:
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The supported {label} field has an unsupported shape.")
    return value


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The supported {label} field has an unsupported shape.")
    return value


def _bounded_list(value: Any, label: str, limit: int, *, required: bool = False) -> list[Any]:
    if value is None and not required:
        return []
    if not isinstance(value, list):
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The supported {label} field has an unsupported shape.")
    if len(value) > limit:
        raise PipelineError("EXTRACTION_LIMIT_EXCEEDED", f"The supported {label} collection exceeds its limit.")
    return value


def _parse_date(value: Any, label: str) -> tuple[str | None, date | None]:
    if value is None:
        return None, None
    text = _require_string(value, label)
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The supported {label} field is not a full ISO date.") from None
    return text, parsed


def _parse_decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The supported {label} field is not numeric.")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The supported {label} field is not numeric.") from None
    if not number.is_finite():
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The supported {label} field is not finite.")
    return number


def _add_fact(
    facts: list[ObservedFact], alias: str, pointer: str, fact_type: str, value: str | Decimal | bool
) -> str:
    if len(facts) >= MAX_OBSERVED_FACTS:
        raise PipelineError("EXTRACTION_LIMIT_EXCEEDED", "The supported observed-fact collection exceeds its limit.")
    evidence_id = _pointer(alias, pointer)
    public_value: str | float | bool = float(value) if isinstance(value, Decimal) else value
    facts.append(
        ObservedFact(
            evidence_id=evidence_id,
            source_alias=alias,
            json_pointer=pointer,
            fact_type=fact_type,
            value=public_value,
        )
    )
    return evidence_id


def _optional_reference(
    facts: list[ObservedFact], alias: str, container: Any, pointer: str, fact_type: str, owner_eid: str
) -> ReferenceValue:
    if container is None:
        return ReferenceValue(None, None, owner_eid)
    obj = _require_object(container, fact_type)
    raw = obj.get("reference")
    if raw is None:
        return ReferenceValue(None, None, owner_eid)
    value = _require_string(raw, fact_type)
    eid = _add_fact(facts, alias, f"{pointer}/reference", fact_type, value)
    return ReferenceValue(value, eid, owner_eid)


def extract_supported_dataset(sources: dict[str, LoadedSource]) -> ExtractedDataset:
    facts: list[ObservedFact] = []
    patient_ids: list[tuple[str, str]] = []
    coverages: list[CoverageRecord] = []
    eobs: list[EobRecord] = []
    identity_index: dict[tuple[str, str], list[str]] = {}

    patient = sources["patient"].document
    if patient.get("resourceType") != "Patient":
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", "The patient source is not a supported Patient object.")
    patient_id = _require_string(patient.get("id"), "Patient.id")
    patient_eid = _add_fact(facts, "patient", "/id", "resource_id", patient_id)
    patient_ids.append((patient_id, patient_eid))
    identity_index.setdefault(("Patient", patient_id), []).append(patient_eid)

    coverage_bundle = sources["coverage"].document
    coverage_entries = _bundle_entries(coverage_bundle, "Coverage")
    for entry_index, entry in enumerate(coverage_entries):
        resource = _require_object(_require_object(entry, "Coverage Bundle entry").get("resource"), "Coverage resource")
        base = f"/entry/{entry_index}/resource"
        coverage_id = _require_string(resource.get("id"), "Coverage.id")
        identity_eid = _add_fact(facts, "coverage", f"{base}/id", "resource_id", coverage_id)
        identity_index.setdefault(("Coverage", coverage_id), []).append(identity_eid)
        status = resource.get("status")
        if status is not None:
            _add_fact(facts, "coverage", f"{base}/status", "coverage_status", _require_string(status, "Coverage.status"))
        beneficiary = _optional_reference(
            facts, "coverage", resource.get("beneficiary"), f"{base}/beneficiary", "beneficiary_reference", identity_eid
        )
        period = resource.get("period")
        if period is not None:
            period = _require_object(period, "Coverage.period")
        else:
            period = {}
        start_text, start = _parse_date(period.get("start"), "Coverage.period.start")
        end_text, end = _parse_date(period.get("end"), "Coverage.period.end")
        start_eid = (
            _add_fact(facts, "coverage", f"{base}/period/start", "coverage_period_start", start_text)
            if start_text
            else None
        )
        end_eid = (
            _add_fact(facts, "coverage", f"{base}/period/end", "coverage_period_end", end_text) if end_text else None
        )
        coverages.append(
            CoverageRecord(coverage_id, identity_eid, beneficiary, start, start_eid, end, end_eid)
        )

    eob_bundle = sources["eob"].document
    eob_entries = _bundle_entries(eob_bundle, "ExplanationOfBenefit")
    for entry_index, entry in enumerate(eob_entries):
        resource = _require_object(_require_object(entry, "EOB Bundle entry").get("resource"), "EOB resource")
        base = f"/entry/{entry_index}/resource"
        eob_id = _require_string(resource.get("id"), "ExplanationOfBenefit.id")
        identity_eid = _add_fact(facts, "eob", f"{base}/id", "resource_id", eob_id)
        identity_index.setdefault(("ExplanationOfBenefit", eob_id), []).append(identity_eid)
        patient_ref = _optional_reference(
            facts, "eob", resource.get("patient"), f"{base}/patient", "patient_reference", identity_eid
        )
        insurance = _bounded_list(resource.get("insurance"), "ExplanationOfBenefit.insurance", MAX_BUNDLE_ENTRIES)
        coverage_refs: list[ReferenceValue] = []
        for insurance_index, insurance_value in enumerate(insurance):
            insurance_obj = _require_object(insurance_value, "ExplanationOfBenefit.insurance item")
            coverage_refs.append(
                _optional_reference(
                    facts,
                    "eob",
                    insurance_obj.get("coverage"),
                    f"{base}/insurance/{insurance_index}/coverage",
                    "coverage_reference",
                    identity_eid,
                )
            )
        billable = resource.get("billablePeriod")
        if billable is not None:
            billable = _require_object(billable, "ExplanationOfBenefit.billablePeriod")
            for key, fact_type in (("start", "billable_period_start"), ("end", "billable_period_end")):
                text, _ = _parse_date(billable.get(key), f"ExplanationOfBenefit.billablePeriod.{key}")
                if text:
                    _add_fact(facts, "eob", f"{base}/billablePeriod/{key}", fact_type, text)
        items: list[ItemRecord] = []
        for item_index, item_value in enumerate(
            _bounded_list(resource.get("item"), "ExplanationOfBenefit.item", MAX_EOB_ITEMS)
        ):
            item = _require_object(item_value, "ExplanationOfBenefit.item entry")
            item_base = f"{base}/item/{item_index}"
            service_text, service_date = _parse_date(item.get("servicedDate"), "item.servicedDate")
            service_eid = (
                _add_fact(facts, "eob", f"{item_base}/servicedDate", "service_date", service_text)
                if service_text
                else None
            )
            products: list[tuple[str, str, str, str]] = []
            product = item.get("productOrService")
            if product is not None:
                product_obj = _require_object(product, "item.productOrService")
                codings = _bounded_list(product_obj.get("coding"), "item.productOrService.coding", MAX_CODINGS)
                for coding_index, coding_value in enumerate(codings):
                    coding = _require_object(coding_value, "item.productOrService.coding entry")
                    system = coding.get("system")
                    code = coding.get("code")
                    if system is None or code is None:
                        continue
                    system = _require_string(system, "productOrService.system")
                    code = _require_string(code, "productOrService.code")
                    system_eid = _add_fact(
                        facts,
                        "eob",
                        f"{item_base}/productOrService/coding/{coding_index}/system",
                        "product_service_system",
                        system,
                    )
                    code_eid = _add_fact(
                        facts,
                        "eob",
                        f"{item_base}/productOrService/coding/{coding_index}/code",
                        "product_service_code",
                        code,
                    )
                    products.append((system, code, system_eid, code_eid))
            adjudications: list[AmountComponent] = []
            for adj_index, adj_value in enumerate(
                _bounded_list(item.get("adjudication"), "item.adjudication", MAX_ADJUDICATIONS)
            ):
                adj = _require_object(adj_value, "item.adjudication entry")
                category = adj.get("category")
                if category is None:
                    continue
                category_obj = _require_object(category, "adjudication.category")
                category_codings = _bounded_list(
                    category_obj.get("coding"), "adjudication.category.coding", MAX_CODINGS
                )
                selected: tuple[str, str] | None = None
                for coding_value in category_codings:
                    coding = _require_object(coding_value, "adjudication.category.coding entry")
                    pair = (coding.get("system"), coding.get("code"))
                    if pair in SELECTED_CATEGORIES:
                        selected = pair  # type: ignore[assignment]
                        break
                if selected is None:
                    continue
                amount = _require_object(adj.get("amount"), "selected adjudication.amount")
                value = _parse_decimal(amount.get("value"), "selected adjudication.amount.value")
                currency = _require_string(amount.get("currency"), "selected adjudication.amount.currency")
                value_eid = _add_fact(
                    facts,
                    "eob",
                    f"{item_base}/adjudication/{adj_index}/amount/value",
                    "adjudication_value",
                    value,
                )
                currency_eid = _add_fact(
                    facts,
                    "eob",
                    f"{item_base}/adjudication/{adj_index}/amount/currency",
                    "adjudication_currency",
                    currency,
                )
                adjudications.append(AmountComponent(*selected, value, currency, value_eid, currency_eid))
            items.append(
                ItemRecord(
                    item_base,
                    identity_eid,
                    patient_ref,
                    tuple(coverage_refs),
                    service_date,
                    service_text,
                    service_eid,
                    tuple(products),
                    tuple(adjudications),
                )
            )
        eobs.append(EobRecord(eob_id, identity_eid, patient_ref, tuple(coverage_refs), tuple(items)))

    source = SourceMetadata(
        files=[sources[key].metadata for key in ("patient", "coverage", "eob")],
        resource_counts=ResourceCounts(
            Patient=len(patient_ids), Coverage=len(coverages), ExplanationOfBenefit=len(eobs)
        ),
    )
    return ExtractedDataset(source, facts, patient_ids, coverages, eobs, identity_index)


def _bundle_entries(bundle: dict[str, Any], expected_type: str) -> list[Any]:
    if bundle.get("resourceType") != "Bundle" or bundle.get("type") != "searchset":
        raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The {expected_type} source is not a supported searchset Bundle.")
    entries = _bounded_list(bundle.get("entry"), f"{expected_type} Bundle.entry", MAX_BUNDLE_ENTRIES, required=True)
    for entry in entries:
        entry_obj = _require_object(entry, f"{expected_type} Bundle entry")
        resource = _require_object(entry_obj.get("resource"), f"{expected_type} resource")
        if resource.get("resourceType") != expected_type:
            raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", f"The {expected_type} Bundle is not homogeneous.")
    return entries
