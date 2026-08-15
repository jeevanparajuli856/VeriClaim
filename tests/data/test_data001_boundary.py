from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import socket
import urllib.request

from jsonschema import Draft202012Validator
import pytest

import reference_validator as reference_validator_module
from reference_validator import (
    CONTRACT_DIR,
    REPO_ROOT,
    ReferenceValidator,
    SAFE_REJECTED_SOURCE_PATH,
    declared_source_set_digest,
    load_seed_source_set,
    mutate_json_document,
    observed_source_set_digest,
    project_fixture_from_seed,
    sha256_bytes,
    source_set_digest,
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


def _deep_array(depth: int) -> list:
    value: object = 0
    for _ in range(depth):
        value = [value]
    return value


def _replace_source_path(source_set, role: str, path: str, *, new_role: str | None = None):
    documents = tuple(
        replace(item, path=path, role=new_role or item.role) if item.role == role else item
        for item in source_set.documents
    )
    return replace(
        source_set,
        documents=documents,
        expected_digest=source_set_digest(documents),
    )


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
    if case_id == "prohibited-class-malicious-path":
        fixture = _replace_source_path(
            fixture,
            "patient",
            "dataset/../../EVIL\nMARKER.json",
        )
        return replace(fixture, classification="prohibited-real-phi")
    if case_id == "invalid-role-malicious-path":
        return _replace_source_path(
            fixture,
            "patient",
            "tests/fixtures/fhir/data-001/../EVIL\nMARKER.json",
            new_role="unsupported-role",
        )
    if case_id.startswith("other-root-"):
        role = case_id.removeprefix("other-root-")
        filenames = {
            "patient": "patient.json",
            "coverage-searchset": "coverage.json",
            "pharmacy-eob-searchset": "eob.json",
            "provenance-readme": "readme.txt",
        }
        return _replace_source_path(fixture, role, f"other/{filenames[role]}")
    if case_id == "approved-classification-fixture-root":
        return replace(fixture, classification="approved-synthetic-local")
    if case_id == "project-classification-dataset-root":
        return replace(load_seed_source_set(), classification="project-authored-synthetic")
    if case_id.startswith("approved-renamed-"):
        role = case_id.removeprefix("approved-renamed-")
        seed = load_seed_source_set()
        return _replace_source_path(seed, role, f"dataset/renamed-{role}.json")
    if case_id in {"nonfinite-nan", "nonfinite-infinity", "nonfinite-negative-infinity"}:
        patient = strict_json_loads(fixture.document("patient").raw)
        constants = {
            "nonfinite-nan": float("nan"),
            "nonfinite-infinity": float("inf"),
            "nonfinite-negative-infinity": float("-inf"),
        }
        patient["gender"] = constants[case_id]
        raw = json.dumps(patient, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return fixture.replace_document("patient", raw)
    if case_id == "parser-recursion":
        raw = b'{"resourceType":"Patient","nested":' + b"[" * 2000 + b"0" + b"]" * 2000 + b"}"
        return fixture.replace_document("patient", raw)
    if case_id == "maximum-document-bytes":
        patient = fixture.document("patient")
        raw = patient.raw + b" " * (524289 - len(patient.raw))
        return fixture.replace_document("patient", raw)
    if case_id == "maximum-total-input-bytes":
        for role in ("patient", "coverage-searchset", "pharmacy-eob-searchset"):
            document = fixture.document(role)
            fixture = fixture.replace_document(role, document.raw + b" " * (400000 - len(document.raw)))
        return fixture
    if case_id == "maximum-source-files":
        patient = fixture.document("patient")
        extra = replace(
            patient,
            path="tests/fixtures/fhir/data-001/generated/maximum-source-files/extra.json",
            role="extra",
        )
        documents = fixture.documents + (extra,)
        return replace(fixture, documents=documents, expected_digest=source_set_digest(documents))

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
        "undeclared-nested-field": ("patient", lambda value: value["name"][0].__setitem__("instruction", "EVIL_MARKER")),
        "wrong-primitive-type": ("patient", lambda value: value.__setitem__("gender", {"value": "male"})),
        "maximum-nesting-depth": ("patient", lambda value: value["name"][0].__setitem__("instruction", _deep_array(40))),
        "maximum-array-items": ("patient", lambda value: value.__setitem__("name", [deepcopy(value["name"][0]) for _ in range(257)])),
        "maximum-object-members": ("patient", lambda value: value.__setitem__("name", [{f"member{i}": "x" for i in range(65)}])),
        "maximum-object-key-bytes": ("patient", lambda value: value["name"][0].__setitem__("k" * 129, "x")),
        "maximum-string-bytes": ("patient", lambda value: value.__setitem__("gender", "x" * 4097)),
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


def test_shape_registry_digest_types_and_limits_are_exact_contract_evidence(
    validator: ReferenceValidator,
):
    registry = validator.shape_registry
    records = sorted(
        (entry["role"], entry["json_pointer"], entry["type"])
        for entry in registry["entries"]
    )
    canonical = "".join(f"{role}\0{pointer}\0{item_type}\n" for role, pointer, item_type in records)
    assert len(records) == registry["canonical_registry"]["entry_count"] == 261
    assert sha256_bytes(canonical.encode("utf-8")) == registry["canonical_registry"]["sha256"]
    assert {item_type for _, _, item_type in records} == {"object", "array", "string", "number", "boolean"}
    assert registry["limits"] == {
        "maximum_source_files": 4,
        "maximum_total_input_bytes": 1048576,
        "maximum_document_bytes": 524288,
        "maximum_nesting_depth": 32,
        "maximum_array_items": 256,
        "maximum_object_members": 64,
        "maximum_object_key_utf8_bytes": 128,
        "maximum_string_utf8_bytes": 4096,
    }


@pytest.mark.parametrize("token", [b"NaN", b"Infinity", b"-Infinity"])
def test_strict_json_loader_rejects_every_non_finite_constant(token: bytes):
    with pytest.raises(ValueError):
        strict_json_loads(b'{"value":' + token + b"}")


def test_strict_json_loader_converts_parser_recursion_to_safe_rejection():
    raw = b"[" * 2000 + b"0" + b"]" * 2000
    with pytest.raises(ValueError):
        strict_json_loads(raw)


def test_nesting_limit_uses_iterative_fail_closed_traversal(
    monkeypatch: pytest.MonkeyPatch,
    validator: ReferenceValidator,
):
    entries = set()
    pointer = ""
    for _ in range(40):
        entries.add(("patient", pointer, "array"))
        pointer += "/[]"
    entries.add(("patient", pointer, "number"))
    monkeypatch.setattr(validator, "shape_entries", entries)
    failure = validator._validate_shape(
        "patient",
        "tests/fixtures/fhir/data-001/generated/maximum-nesting-depth/patient.json",
        _deep_array(40),
    )
    assert failure["machine_code"] == "NESTING_DEPTH_EXCEEDED"
    assert failure["rule_id"] == "FHIR-COMPAT-CONTENT-001"


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
    manifest = strict_json_loads((CONTRACT_DIR / "source-manifest.json").read_bytes())
    assert accepted_seed["declared_source_set_sha256"] == manifest["source_set_digest"]["sha256"]
    assert accepted_seed["observed_source_set_sha256"] == manifest["source_set_digest"]["sha256"]
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
        "bytes": 1556152,
        "issue_count": 895,
    }
    observed = Counter((item["source_path"], item["severity"]) for item in carin["findings"])
    for source_path, counts in EXPECTED_COUNTS.items():
        for severity, count in counts.items():
            assert observed[(source_path, severity)] == count
    assert len(carin["findings"]) == 895
    assert len(carin["verified_artifacts"]) == 32
    assert {item["kind"] for item in carin["verified_artifacts"]} == {"validator", "runtime", "package"}
    assert all(len(item["evidence_sha256"]) == 64 for item in carin["findings"])
    assert all(item["machine_code"].startswith("CARIN_") for item in carin["findings"])
    assert any(item["json_pointer"] == "/extension/0" for item in carin["findings"])
    assert any(item["json_pointer"].startswith("/entry/0/resource") for item in carin["findings"])
    serialized = json.dumps(accepted_seed, sort_keys=True).lower()
    assert "carin-conformant" not in serialized
    assert '"acceptance_authority": true' not in serialized


def test_each_carin_finding_digest_matches_the_complete_canonical_raw_issue(
    accepted_seed: dict,
):
    raw = strict_json_loads(
        (CONTRACT_DIR / ".offline/evidence/seed-carin-operationoutcomes.json").read_bytes()
    )
    canonical_digests = []
    for entry in raw["entry"]:
        for issue in entry["resource"]["issue"]:
            canonical = json.dumps(
                issue,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
            canonical_digests.append(sha256_bytes(canonical))
    assert [item["evidence_sha256"] for item in accepted_seed["carin"]["findings"]] == canonical_digests
    assert all(
        item["message"] == "Checksum-verified CARIN diagnostic issue retained by canonical issue digest."
        for item in accepted_seed["carin"]["findings"]
    )


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


@pytest.mark.parametrize("mode", ["missing", "changed"])
def test_missing_or_changed_raw_diagnostic_evidence_is_unavailable_not_synthesized(
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
    validator: ReferenceValidator,
    outcome_schema_validator: Draft202012Validator,
):
    target = validator.offline_dir / "evidence/seed-carin-operationoutcomes.json"
    original = Path.read_bytes

    def controlled_read(path: Path) -> bytes:
        if path == target:
            if mode == "missing":
                raise FileNotFoundError(path)
            return original(path) + b"changed"
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", controlled_read)
    result = validator.validate()
    assert result["decision"] == "accepted"
    assert result["states"][1] == "carin-diagnostic-unavailable"
    assert result["carin"]["status"] == "diagnostic-unavailable"
    assert result["carin"]["counts"] == {"fatal": 0, "error": 0, "warning": 0, "information": 0}
    assert result["carin"]["findings"] == []
    assert "raw_evidence" not in result["carin"]
    assert_schema_valid(outcome_schema_validator, result)


def test_missing_locked_package_makes_diagnostics_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    validator: ReferenceValidator,
):
    first_package = validator.package_lock["packages"][0]
    target = validator.offline_dir / "packages" / f"{first_package['name']}#{first_package['version']}.tgz"
    expected = {}
    for tool_path, tool in (
        (validator.offline_dir / "tooling/validator_cli-6.10.2.jar", validator.package_lock["tooling"][0]),
        (validator.offline_dir / "tooling/OpenJDK21U-jre_x64_linux_hotspot_21.0.12_8.tar.gz", validator.package_lock["tooling"][1]),
    ):
        expected[tool_path] = (tool["sha256"], tool["bytes"])
    for package in validator.package_lock["packages"]:
        path = validator.offline_dir / "packages" / f"{package['name']}#{package['version']}.tgz"
        expected[path] = (package["sha256"], 1)

    def controlled_digest(path: Path):
        if path == target:
            raise FileNotFoundError(path)
        return expected[path]

    monkeypatch.setattr(reference_validator_module, "sha256_path", controlled_digest)
    result = validator.validate()
    assert result["decision"] == "accepted"
    assert result["carin"]["status"] == "diagnostic-unavailable"
    assert result["carin"]["findings"] == []


def test_exact_validator_jre_and_every_locked_archive_are_verified(
    accepted_seed: dict,
):
    package_lock = strict_json_loads((CONTRACT_DIR / "packages.lock.json").read_bytes())
    validator_tool, jre_tool = package_lock["tooling"]
    expected = [
        ("validator", validator_tool),
        ("runtime", jre_tool),
    ]
    expected.extend(
        ("package", package)
        for package in package_lock["packages"]
    )
    verified = accepted_seed["carin"]["verified_artifacts"]
    assert len(expected) == len(verified) == 32
    for observed, (kind, lock_entry) in zip(verified, expected):
        assert observed["kind"] == kind
        assert observed["name"] == lock_entry["name"]
        assert observed["version"] == lock_entry["version"]
        assert observed["sha256"] == lock_entry["sha256"]
        assert observed["bytes"] > 0
        if "bytes" in lock_entry:
            assert observed["bytes"] == lock_entry["bytes"]


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
    accepted_seed: dict,
):
    def deny_network(*_args, **_kwargs):
        raise AssertionError("network access is forbidden")

    monkeypatch.setattr(socket, "create_connection", deny_network)
    monkeypatch.setattr(urllib.request, "urlopen", deny_network)
    monkeypatch.setattr(
        validator,
        "_verified_artifacts",
        lambda: deepcopy(accepted_seed["carin"]["verified_artifacts"]),
    )
    result = validator.validate()
    assert result["decision"] == "accepted"


def test_required_offline_project_verification_check_is_declared_and_enforced(
    accepted_seed: dict,
):
    project = strict_json_loads((REPO_ROOT / ".ai/project.json").read_bytes())
    checks = project["verification"]["checks"]
    check = next(item for item in checks if item["name"] == "DATA-001 required offline validation suite")
    assert check["required"] is True
    assert check["command"] == [
        "/usr/bin/env", "DATA001_REQUIRE_OFFLINE=1", "python3", "-m", "pytest", "-q", "tests/data"
    ]
    if os.environ.get("DATA001_REQUIRE_OFFLINE") == "1":
        assert accepted_seed["carin"]["status"] == "nonconformant"
        assert len(accepted_seed["carin"]["verified_artifacts"]) == 32


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
        ("undeclared-nested-field", "FHIR-COMPAT-CONTENT-001"),
        ("wrong-primitive-type", "FHIR-COMPAT-CONTENT-001"),
        ("nonfinite-nan", "JSON-SYNTAX-001"),
        ("nonfinite-infinity", "JSON-SYNTAX-001"),
        ("nonfinite-negative-infinity", "JSON-SYNTAX-001"),
        ("parser-recursion", "JSON-SYNTAX-001"),
        ("maximum-nesting-depth", "FHIR-COMPAT-CONTENT-001"),
        ("maximum-array-items", "FHIR-COMPAT-CONTENT-001"),
        ("maximum-object-members", "FHIR-COMPAT-CONTENT-001"),
        ("maximum-object-key-bytes", "FHIR-COMPAT-CONTENT-001"),
        ("maximum-string-bytes", "FHIR-COMPAT-CONTENT-001"),
        ("maximum-document-bytes", "SOURCE-MANIFEST-001"),
        ("maximum-total-input-bytes", "SOURCE-MANIFEST-001"),
        ("maximum-source-files", "SOURCE-MANIFEST-001"),
        ("prohibited-class-malicious-path", "SOURCE-MANIFEST-001"),
        ("invalid-role-malicious-path", "SOURCE-MANIFEST-001"),
        ("other-root-patient", "SOURCE-MANIFEST-001"),
        ("other-root-coverage-searchset", "SOURCE-MANIFEST-001"),
        ("other-root-pharmacy-eob-searchset", "SOURCE-MANIFEST-001"),
        ("other-root-provenance-readme", "SOURCE-MANIFEST-001"),
        ("approved-classification-fixture-root", "SOURCE-MANIFEST-001"),
        ("project-classification-dataset-root", "SOURCE-MANIFEST-001"),
        ("approved-renamed-patient", "SOURCE-MANIFEST-001"),
        ("approved-renamed-coverage-searchset", "SOURCE-MANIFEST-001"),
        ("approved-renamed-pharmacy-eob-searchset", "SOURCE-MANIFEST-001"),
        ("approved-renamed-provenance-readme", "SOURCE-MANIFEST-001"),
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


def test_path_validation_precedes_classification_role_and_identity_with_fixed_safe_evidence(
    validator: ReferenceValidator,
    outcome_schema_validator: Draft202012Validator,
):
    combined = build_case("prohibited-class-malicious-path")
    result = validator.validate(combined)
    assert result["project_findings"] == [
        {
            "rule_id": "SOURCE-MANIFEST-001",
            "source": "project",
            "severity": "error",
            "machine_code": "SOURCE_PATH_INVALID",
            "message": "A declared source path violates the normalized source-root policy.",
            "source_path": SAFE_REJECTED_SOURCE_PATH,
            "json_pointer": "",
        }
    ]
    assert result["observed_source_set_sha256"] == observed_source_set_digest(combined.documents)
    assert "EVIL" not in json.dumps(result)
    assert "MARKER" not in json.dumps(result)
    assert_schema_valid(outcome_schema_validator, result)

    invalid_role = validator.validate(build_case("invalid-role-malicious-path"))
    assert invalid_role["project_findings"][0]["machine_code"] == "SOURCE_PATH_INVALID"
    assert invalid_role["project_findings"][0]["source_path"] == SAFE_REJECTED_SOURCE_PATH
    assert_schema_valid(outcome_schema_validator, invalid_role)


@pytest.mark.parametrize(
    "case_id, machine_code",
    [
        ("other-root-patient", "SOURCE_ROOT_NOT_ALLOWED"),
        ("other-root-coverage-searchset", "SOURCE_ROOT_NOT_ALLOWED"),
        ("other-root-pharmacy-eob-searchset", "SOURCE_ROOT_NOT_ALLOWED"),
        ("other-root-provenance-readme", "SOURCE_ROOT_NOT_ALLOWED"),
        ("approved-classification-fixture-root", "CLASSIFICATION_SOURCE_ROOT_MISMATCH"),
        ("project-classification-dataset-root", "CLASSIFICATION_SOURCE_ROOT_MISMATCH"),
        ("approved-renamed-patient", "APPROVED_SOURCE_PATH_MISMATCH"),
        ("approved-renamed-coverage-searchset", "APPROVED_SOURCE_PATH_MISMATCH"),
        ("approved-renamed-pharmacy-eob-searchset", "APPROVED_SOURCE_PATH_MISMATCH"),
        ("approved-renamed-provenance-readme", "APPROVED_SOURCE_PATH_MISMATCH"),
    ],
)
def test_source_root_and_exact_approved_manifest_policy_rejects_with_schema_safe_path(
    case_id: str,
    machine_code: str,
    validator: ReferenceValidator,
    outcome_schema_validator: Draft202012Validator,
):
    source_set = build_case(case_id)
    result = validator.validate(source_set)
    assert result["decision"] == "rejected"
    assert result["states"] == ["rejected"]
    assert result["project_findings"][0]["machine_code"] == machine_code
    assert result["project_findings"][0]["source_path"] == SAFE_REJECTED_SOURCE_PATH
    assert result["observed_source_set_sha256"] == observed_source_set_digest(source_set.documents)
    assert_schema_valid(outcome_schema_validator, result)


def test_declared_and_observed_source_digests_distinguish_tampered_payloads(
    validator: ReferenceValidator,
    outcome_schema_validator: Draft202012Validator,
):
    base = project_fixture_from_seed("observed-provenance")
    patient = base.document("patient")
    first = base.replace_document("patient", patient.raw + b" A", update_identity=False)
    second = base.replace_document("patient", patient.raw + b" B", update_identity=False)
    first_result = validator.validate(first)
    second_result = validator.validate(second)
    assert first_result["decision"] == second_result["decision"] == "rejected"
    assert first_result["declared_source_set_sha256"] == second_result["declared_source_set_sha256"]
    assert first_result["declared_source_set_sha256"] == declared_source_set_digest(base.documents)
    assert first_result["observed_source_set_sha256"] == observed_source_set_digest(first.documents)
    assert second_result["observed_source_set_sha256"] == observed_source_set_digest(second.documents)
    assert first_result["observed_source_set_sha256"] != second_result["observed_source_set_sha256"]
    assert_schema_valid(outcome_schema_validator, first_result)
    assert_schema_valid(outcome_schema_validator, second_result)


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


@pytest.mark.parametrize("field", ["declared_source_set_sha256", "observed_source_set_sha256"])
def test_schema_requires_both_declared_and_observed_source_digests(
    field: str,
    accepted_seed: dict,
    outcome_schema_validator: Draft202012Validator,
):
    invalid = deepcopy(accepted_seed)
    invalid.pop(field)
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
