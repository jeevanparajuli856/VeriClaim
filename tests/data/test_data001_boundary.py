from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import replace
import json
import os
import socket
import urllib.request

from jsonschema import Draft202012Validator
import pytest

from reference_validator import (
    CONTRACT_DIR,
    REPO_ROOT,
    ReferenceValidator,
    load_seed_source_set,
    mutate_json_document,
    project_fixture_from_seed,
    sha256_bytes,
    strict_json_loads,
)


CATALOG_PATH = REPO_ROOT / "tests/fixtures/fhir/data-001/fixture-catalog.json"
DUPLICATE_KEY_PATH = REPO_ROOT / "tests/fixtures/fhir/data-001/duplicate-key-patient.json"
SEED_HASHES = {
    "dataset/patient_bbuser29999.json": "6fb43e72120e3a3cfb7bc756d0661eebcc0925a2bc994f60ecbf573813e3f58a",
    "dataset/coverage_bundle_bbuser29999.json": "fef088d7c6df3fb33bc02a1e32be53a67db0815046b1e2d998d44cb1536ec33c",
    "dataset/eob_bundle_bbuser29999.json": "d48c12a8d94e331c786f3876ea94df4356209c216c54392346dae87f84fc34f0",
    "dataset/readme.txt": "5c5c7641a7dbb1c5c21864e429390f7021d303fef5ad8eabacd01b805e205fe8",
}
EXPECTED_COUNTS = {
    "dataset/patient_bbuser29999.json": {"fatal": 0, "error": 16, "warning": 5, "information": 0},
    "dataset/coverage_bundle_bbuser29999.json": {"fatal": 0, "error": 216, "warning": 12, "information": 0},
    "dataset/eob_bundle_bbuser29999.json": {"fatal": 0, "error": 218, "warning": 428, "information": 0},
}
EXPECTED_TOTAL = {"fatal": 0, "error": 450, "warning": 445, "information": 0}
EXPECTED_RAW_DIGEST = "2eb1271891b41794b665b639aa2f63138ed597cace33fbd2e3ce45673dcf7d15"


def file_hashes() -> dict[str, str]:
    return {path: sha256_bytes((REPO_ROOT / path).read_bytes()) for path in SEED_HASHES}


@pytest.fixture(scope="module", autouse=True)
def seed_immutability_guard():
    before = file_hashes()
    assert before == SEED_HASHES
    yield
    assert file_hashes() == before == SEED_HASHES


@pytest.fixture(scope="module")
def validator() -> ReferenceValidator:
    return ReferenceValidator()


@pytest.fixture(scope="module")
def outcome_schema_validator() -> Draft202012Validator:
    schema = strict_json_loads((CONTRACT_DIR / "validation-outcome.schema.json").read_bytes())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture(scope="module")
def accepted_seed(validator: ReferenceValidator) -> dict:
    return validator.validate()


def assert_schema_valid(schema_validator: Draft202012Validator, outcome: dict) -> None:
    errors = sorted(schema_validator.iter_errors(outcome), key=lambda error: list(error.path))
    assert not errors, " | ".join(error.message for error in errors)


def assert_schema_invalid(schema_validator: Draft202012Validator, outcome: dict) -> None:
    assert list(schema_validator.iter_errors(outcome))


def _set_first_system(value: object) -> bool:
    if isinstance(value, dict):
        if isinstance(value.get("system"), str):
            value["system"] = "https://unregistered.invalid/system"
            return True
        return any(_set_first_system(child) for child in value.values())
    if isinstance(value, list):
        return any(_set_first_system(child) for child in value)
    return False


def _set_nested(resource: dict, path: tuple[object, ...], value: object = None, delete: bool = False) -> None:
    current = resource
    for key in path[:-1]:
        current = current[key]
    if delete:
        del current[path[-1]]
    else:
        current[path[-1]] = value


def build_case(case_id: str):
    fixture = project_fixture_from_seed(case_id)
    if case_id == "duplicate-key":
        return fixture.replace_document("patient", DUPLICATE_KEY_PATH.read_bytes())
    if case_id == "malformed-json":
        return fixture.replace_document("patient", b'{"resourceType":"Patient"')
    if case_id == "top-level-array":
        return fixture.replace_document("patient", b"[]")
    if case_id == "prohibited-class":
        return replace(fixture, classification="prohibited-real-phi")
    if case_id == "hash-mismatch":
        patient = fixture.document("patient")
        return fixture.replace_document("patient", patient.raw + b" ", update_identity=False)
    if case_id == "source-path-traversal":
        documents = tuple(
            replace(item, path="tests/fixtures/fhir/data-001/../escape/patient.json")
            if item.role == "patient"
            else item
            for item in fixture.documents
        )
        return replace(fixture, documents=documents)

    mutations = {
        "unsupported-resource": ("patient", lambda value: value.__setitem__("resourceType", "Practitioner")),
        "unsupported-profile": ("patient", lambda value: _set_nested(value, ("meta", "profile"), ["https://unregistered.invalid/Profile"])),
        "unsupported-bundle-type": ("coverage-searchset", lambda value: value.__setitem__("type", "collection")),
        "empty-bundle": ("coverage-searchset", lambda value: value.__setitem__("entry", [])),
        "mixed-bundle": ("coverage-searchset", lambda value: _set_nested(value, ("entry", 0, "resource", "resourceType"), "Patient")),
        "missing-patient-identifier": ("patient", lambda value: value.pop("identifier")),
        "missing-coverage-status": ("coverage-searchset", lambda value: _set_nested(value, ("entry", 0, "resource", "status"), delete=True)),
        "missing-eob-item": ("pharmacy-eob-searchset", lambda value: _set_nested(value, ("entry", 0, "resource", "item"), delete=True)),
        "invalid-bundle-total": ("coverage-searchset", lambda value: value.__setitem__("total", "4")),
        "duplicate-id": ("coverage-searchset", lambda value: _set_nested(value, ("entry", 1, "resource", "id"), value["entry"][0]["resource"]["id"])),
        "broken-ref": ("coverage-searchset", lambda value: _set_nested(value, ("entry", 0, "resource", "beneficiary", "reference"), "Patient/absent")),
        "cross-type-ref": ("coverage-searchset", lambda value: _set_nested(value, ("entry", 0, "resource", "beneficiary", "reference"), "Coverage/part-a--20140000010000")),
        "absolute-ref": ("coverage-searchset", lambda value: _set_nested(value, ("entry", 0, "resource", "beneficiary", "reference"), "https://evil.invalid/Patient/EVIL_MARKER")),
        "unknown-resource-field": ("patient", lambda value: value.__setitem__("EVIL_MARKER<script>", "https://evil.invalid/secret\nINJECT")),
        "unknown-bundle-field": ("coverage-searchset", lambda value: value.__setitem__("instruction", {"run": "EVIL_MARKER"})),
        "extension-registry-change": ("patient", lambda value: _set_nested(value, ("extension", 0, "url"), "https://unregistered.invalid/extension")),
        "system-registry-change": ("patient", lambda value: _set_first_system(value)),
        "modifier-extension": ("patient", lambda value: value.__setitem__("modifierExtension", [{"url": "https://evil.invalid/modifier"}])),
        "contained": ("patient", lambda value: value.__setitem__("contained", [{"resourceType": "Patient", "id": "nested"}])),
        "narrative-text": ("patient", lambda value: value.__setitem__("text", {"status": "generated", "div": "<script>EVIL_MARKER</script>"})),
        "attachment": ("patient", lambda value: value.__setitem__("attachment", {"data": "RVZJTF9NQVJLRVI="})),
        "bundle-request": ("coverage-searchset", lambda value: value["entry"][0].__setitem__("request", {"method": "POST", "url": "https://evil.invalid"})),
        "bundle-response": ("coverage-searchset", lambda value: value["entry"][0].__setitem__("response", {"status": "200"})),
    }
    role, mutation = mutations[case_id]
    return mutate_json_document(fixture, role, mutation)


def test_fixture_catalog_has_durable_synthetic_lineage_and_expected_results():
    catalog = strict_json_loads(CATALOG_PATH.read_bytes())
    assert catalog["classification"] == "project-authored-synthetic"
    assert catalog["recipe_version"] == "1.0.0"
    assert catalog["parent_hashes"] == SEED_HASHES
    assert catalog["author_state"] == "project-authored-by-independent-tester"
    assert catalog["reviewer_state"] == "pending-independent-review"
    assert catalog["intended_use"]
    assert catalog["limitations"]
    fixtures = catalog["fixtures"]
    assert len({fixture["id"] for fixture in fixtures}) == len(fixtures)
    for fixture in fixtures:
        assert fixture["recipe"]
        assert fixture["expected_decision"] == "rejected"
        assert fixture["expected_states"] == ["rejected"]
        assert fixture["expected_rule_id"]
        build_case(fixture["id"])


def test_unchanged_seed_passes_minimal_boundary_with_ordered_advisory_states(
    accepted_seed: dict,
    outcome_schema_validator: Draft202012Validator,
):
    assert accepted_seed["decision"] == "accepted"
    assert accepted_seed["states"] == [
        "minimal-profile-valid",
        "carin-nonconformant",
        "terminology-unverified",
    ]
    assert accepted_seed["project_findings"] == []
    assert accepted_seed["layers"] == [
        {"name": name, "status": "passed"}
        for name in ("source", "json", "support", "required-fields", "references", "content-isolation")
    ]
    assert_schema_valid(outcome_schema_validator, accepted_seed)
    assert file_hashes() == SEED_HASHES

    coverage = strict_json_loads((REPO_ROOT / "dataset/coverage_bundle_bbuser29999.json").read_bytes())
    eob = strict_json_loads((REPO_ROOT / "dataset/eob_bundle_bbuser29999.json").read_bytes())
    assert all("fullUrl" not in entry for entry in coverage["entry"] + eob["entry"])
    assert accepted_seed["decision"] == "accepted"


def test_carin_errors_are_complete_structured_diagnostics_not_acceptance(
    accepted_seed: dict,
):
    carin = accepted_seed["carin"]
    assert carin["status"] == "nonconformant"
    assert carin["acceptance_authority"] is False
    assert carin["counts"] == EXPECTED_TOTAL
    assert carin["raw_evidence"] == {
        "sha256": EXPECTED_RAW_DIGEST,
        "format": "FHIR-R4-Bundle-of-OperationOutcome",
        "trusted_content": False,
    }
    observed = Counter((item["source_path"], item["severity"]) for item in carin["findings"])
    for source_path, counts in EXPECTED_COUNTS.items():
        for severity, count in counts.items():
            assert observed[(source_path, severity)] == count
    assert len(carin["findings"]) == 895
    serialized = json.dumps(accepted_seed, sort_keys=True).lower()
    assert "carin-conformant" not in serialized
    assert '"acceptance_authority": true' not in serialized


def test_raw_carin_evidence_digest_is_independently_confirmed_when_materialized():
    evidence_path = CONTRACT_DIR / ".offline/evidence/seed-carin-operationoutcomes.json"
    if os.environ.get("DATA001_REQUIRE_OFFLINE") == "1":
        assert evidence_path.is_file(), "required raw CARIN diagnostic evidence is unavailable"
    if evidence_path.exists():
        raw = evidence_path.read_bytes()
        assert sha256_bytes(raw) == EXPECTED_RAW_DIGEST
        evidence = strict_json_loads(raw)
        observed = [
            Counter(issue["severity"] for issue in entry["resource"]["issue"])
            for entry in evidence["entry"]
        ]
        assert observed == [
            Counter({"error": 16, "warning": 5}),
            Counter({"error": 216, "warning": 12}),
            Counter({"error": 218, "warning": 428}),
        ]


def test_exact_validator_jre_and_carin_archives_match_lock_when_materialized():
    package_lock = strict_json_loads((CONTRACT_DIR / "packages.lock.json").read_bytes())
    validator_tool, jre_tool = package_lock["tooling"]
    carin_package = next(
        package for package in package_lock["packages"]
        if package["name"] == "hl7.fhir.us.carin-bb" and package["version"] == "2.2.0"
    )
    materialized = [
        (CONTRACT_DIR / ".offline/tooling/validator_cli-6.10.2.jar", validator_tool),
        (CONTRACT_DIR / ".offline/tooling/OpenJDK21U-jre_x64_linux_hotspot_21.0.12_8.tar.gz", jre_tool),
        (CONTRACT_DIR / ".offline/packages/hl7.fhir.us.carin-bb#2.2.0.tgz", carin_package),
    ]
    for path, lock_entry in materialized:
        if os.environ.get("DATA001_REQUIRE_OFFLINE") == "1":
            assert path.is_file(), f"required offline artifact is unavailable: {path.name}"
        if path.exists():
            raw = path.read_bytes()
            assert sha256_bytes(raw) == lock_entry["sha256"]
            if "bytes" in lock_entry:
                assert len(raw) == lock_entry["bytes"]


def test_opaque_ncpdp_systems_and_codes_remain_unverified_without_semantics(
    accepted_seed: dict,
):
    package_lock = strict_json_loads((CONTRACT_DIR / "packages.lock.json").read_bytes())
    ncpdp_systems = set(package_lock["official_package_example_evidence"]["unavailable_terminology"]["systems"])
    opaque = accepted_seed["terminology"]
    assert opaque["status"] == "unverified"
    assert opaque["acceptance_authority"] is False
    assert opaque["membership_asserted"] is False
    observed = {item["system"] for item in opaque["opaque_values"] if item["code_present"]}
    opaque_source_systems = {
        "https://bluebutton.cms.gov/resources/variables/brnd_gnrc_cd",
        "https://bluebutton.cms.gov/resources/variables/daw_prod_slctn_cd",
        "https://bluebutton.cms.gov/resources/variables/rx_orgn_cd",
    }
    assert opaque_source_systems.issubset(observed)
    # The unavailable licensed systems are not present in the source and must not
    # be substituted for the byte-preserved source systems.
    assert ncpdp_systems.isdisjoint(observed)
    assert all(set(item) == {"source_path", "json_pointer", "system", "code_present"} for item in opaque["opaque_values"])
    boundary = strict_json_loads((CONTRACT_DIR / "boundary.json").read_bytes())
    assert boundary["terminology"]["prohibited_independent_conclusions"] == [
        "coverage", "payment", "coding", "fraud", "clinical", "policy"
    ]


def test_validation_is_networkless_even_with_source_uris(
    monkeypatch: pytest.MonkeyPatch,
    validator: ReferenceValidator,
):
    def deny_network(*_args, **_kwargs):
        raise AssertionError("network access is forbidden")

    monkeypatch.setattr(socket, "create_connection", deny_network)
    monkeypatch.setattr(urllib.request, "urlopen", deny_network)
    result = validator.validate()
    assert result["decision"] == "accepted"


@pytest.mark.parametrize(
    "case_id, expected_rule",
    [
        ("duplicate-key", "JSON-SYNTAX-001"),
        ("malformed-json", "JSON-SYNTAX-001"),
        ("top-level-array", "JSON-SYNTAX-001"),
        ("prohibited-class", "DATA-CLASS-001"),
        ("hash-mismatch", "SOURCE-MANIFEST-001"),
        ("source-path-traversal", "SOURCE-MANIFEST-001"),
        ("unsupported-resource", "FHIR-COMPAT-RESOURCE-001"),
        ("unsupported-profile", "FHIR-COMPAT-PROFILE-MARKER-001"),
        ("unsupported-bundle-type", "FHIR-COMPAT-ENVELOPE-001"),
        ("empty-bundle", "FHIR-COMPAT-ENVELOPE-001"),
        ("mixed-bundle", "FHIR-COMPAT-RESOURCE-001"),
        ("missing-patient-identifier", "FHIR-COMPAT-REQUIRED-001"),
        ("missing-coverage-status", "FHIR-COMPAT-REQUIRED-001"),
        ("missing-eob-item", "FHIR-COMPAT-REQUIRED-001"),
        ("invalid-bundle-total", "FHIR-COMPAT-REQUIRED-001"),
        ("duplicate-id", "FHIR-COMPAT-ID-001"),
        ("broken-ref", "FHIR-COMPAT-REF-001"),
        ("cross-type-ref", "FHIR-COMPAT-REF-001"),
        ("absolute-ref", "FHIR-COMPAT-REF-001"),
        ("unknown-resource-field", "FHIR-COMPAT-CONTENT-001"),
        ("unknown-bundle-field", "FHIR-COMPAT-CONTENT-001"),
        ("extension-registry-change", "FHIR-COMPAT-CONTENT-001"),
        ("system-registry-change", "FHIR-COMPAT-CONTENT-001"),
        ("modifier-extension", "FHIR-COMPAT-CONTENT-001"),
        ("contained", "FHIR-COMPAT-CONTENT-001"),
        ("narrative-text", "FHIR-COMPAT-CONTENT-001"),
        ("attachment", "FHIR-COMPAT-CONTENT-001"),
        ("bundle-request", "FHIR-COMPAT-CONTENT-001"),
        ("bundle-response", "FHIR-COMPAT-CONTENT-001"),
    ],
)
def test_project_authored_invalid_and_unsupported_input_fails_closed(
    case_id: str,
    expected_rule: str,
    validator: ReferenceValidator,
    outcome_schema_validator: Draft202012Validator,
):
    result = validator.validate(build_case(case_id))
    assert result["decision"] == "rejected"
    assert result["states"] == ["rejected"]
    assert result["project_findings"][0]["rule_id"] == expected_rule
    assert any(layer["status"] == "failed" for layer in result["layers"])
    assert result["carin"]["status"] == "not-run-rejected"
    assert result["carin"]["findings"] == []
    assert result["terminology"]["status"] == "not-evaluated-rejected"
    assert result["terminology"]["opaque_values"] == []
    assert_schema_valid(outcome_schema_validator, result)


def test_rejection_messages_are_sanitized_and_do_not_echo_untrusted_values(
    validator: ReferenceValidator,
):
    for case_id in ("absolute-ref", "unknown-resource-field", "narrative-text", "bundle-request"):
        result = validator.validate(build_case(case_id))
        findings = json.dumps(result["project_findings"], sort_keys=True)
        assert "EVIL_MARKER" not in findings
        assert "evil.invalid" not in findings
        assert "<script>" not in findings
        assert "\nINJECT" not in findings


def test_diagnostic_unavailability_is_distinct_and_does_not_reject_minimal_input(
    validator: ReferenceValidator,
    outcome_schema_validator: Draft202012Validator,
):
    result = validator.validate(carin_available=False)
    assert result["decision"] == "accepted"
    assert result["states"] == [
        "minimal-profile-valid",
        "carin-diagnostic-unavailable",
        "terminology-unverified",
    ]
    assert result["carin"]["status"] == "diagnostic-unavailable"
    assert result["carin"]["acceptance_authority"] is False
    assert_schema_valid(outcome_schema_validator, result)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["layers"].__setitem__(0, {"name": "source", "status": "failed"}),
        lambda value: value.__setitem__("states", ["carin-nonconformant", "minimal-profile-valid", "terminology-unverified"]),
        lambda value: value.__setitem__("states", ["minimal-profile-valid", "carin-nonconformant", "terminology-unverified", "rejected"]),
        lambda value: value.__setitem__("states", ["minimal-profile-valid", "carin-no-errors-reported", "terminology-unverified"]),
        lambda value: value.__setitem__("states", ["minimal-profile-valid", "carin-nonconformant"]),
    ],
)
def test_schema_rejects_inconsistent_accepted_layer_state_and_diagnostic_combinations(
    mutation,
    accepted_seed: dict,
    outcome_schema_validator: Draft202012Validator,
):
    invalid = deepcopy(accepted_seed)
    mutation(invalid)
    assert_schema_invalid(outcome_schema_validator, invalid)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.__setitem__("project_findings", []),
        lambda value: [layer.__setitem__("status", "passed") for layer in value["layers"]],
        lambda value: value["carin"].__setitem__("status", "nonconformant"),
        lambda value: value["terminology"].__setitem__("status", "unverified"),
    ],
)
def test_schema_rejects_inconsistent_rejected_evidence(
    mutation,
    validator: ReferenceValidator,
    outcome_schema_validator: Draft202012Validator,
):
    rejected = validator.validate(build_case("missing-patient-identifier"))
    mutation(rejected)
    assert_schema_invalid(outcome_schema_validator, rejected)
