"""Networkless DATA-001 reference validator used only by independent tests.

This intentionally implements the project compatibility boundary, not full FHIR or
CARIN validation.  Source values are never dereferenced or semantically interpreted.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Callable, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = REPO_ROOT / "contracts/fhir/data-001"
LAYER_NAMES = (
    "source",
    "json",
    "support",
    "required-fields",
    "references",
    "content-isolation",
)
ZERO_COUNTS = {"fatal": 0, "error": 0, "warning": 0, "information": 0}
FHIR_ID = re.compile(r"^[A-Za-z0-9\-.]{1,64}$")
RELATIVE_REFERENCE = re.compile(r"^([A-Z][A-Za-z0-9]+)/([A-Za-z0-9\-.]{1,64})$")


class StrictJsonError(ValueError):
    """A deliberately detail-free strict JSON parsing failure."""


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJsonError("duplicate-key")
        result[key] = value
    return result


def strict_json_loads(raw: bytes) -> Any:
    try:
        text = raw.decode("utf-8", errors="strict")
        return json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except StrictJsonError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StrictJsonError("invalid-json") from exc


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _walk(value: Any, pointer: str = "") -> Iterable[tuple[str, Any]]:
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f"{pointer}/{_pointer_token(key)}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{pointer}/{index}")


@dataclass(frozen=True)
class SourceDocument:
    path: str
    role: str
    raw: bytes
    expected_bytes: int
    expected_sha256: str
    parse_as_fhir: bool = True


@dataclass(frozen=True)
class SourceSet:
    classification: str
    documents: tuple[SourceDocument, ...]
    expected_digest: str

    def document(self, role: str) -> SourceDocument:
        matches = [item for item in self.documents if item.role == role]
        if len(matches) != 1:
            raise KeyError(role)
        return matches[0]

    def replace_document(
        self,
        role: str,
        raw: bytes,
        *,
        update_identity: bool = True,
    ) -> "SourceSet":
        replaced = []
        for item in self.documents:
            if item.role == role:
                replaced.append(
                    replace(
                        item,
                        raw=raw,
                        expected_bytes=len(raw) if update_identity else item.expected_bytes,
                        expected_sha256=sha256_bytes(raw) if update_identity else item.expected_sha256,
                    )
                )
            else:
                replaced.append(item)
        digest = source_set_digest(replaced) if update_identity else self.expected_digest
        return replace(self, documents=tuple(replaced), expected_digest=digest)


def source_set_digest(documents: Iterable[SourceDocument]) -> str:
    records = []
    for item in sorted(documents, key=lambda document: document.path):
        records.append(
            f"{item.path}\0{item.expected_bytes}\0{item.expected_sha256}\n"
        )
    return sha256_bytes("".join(records).encode("utf-8"))


def load_seed_source_set(repo_root: Path = REPO_ROOT) -> SourceSet:
    manifest = strict_json_loads(
        (repo_root / "contracts/fhir/data-001/source-manifest.json").read_bytes()
    )
    documents = []
    for record in manifest["files"]:
        documents.append(
            SourceDocument(
                path=record["path"],
                role=record["role"],
                raw=(repo_root / record["path"]).read_bytes(),
                expected_bytes=record["bytes"],
                expected_sha256=record["sha256"],
                parse_as_fhir=record.get("parse_as_fhir", True),
            )
        )
    return SourceSet(
        classification=manifest["classification"],
        documents=tuple(documents),
        expected_digest=manifest["source_set_digest"]["sha256"],
    )


def project_fixture_from_seed(case_id: str) -> SourceSet:
    """Create a deterministic in-memory fixture with project-authored paths."""
    seed = load_seed_source_set()
    filenames = {
        "patient": "patient.json",
        "coverage-searchset": "coverage.json",
        "pharmacy-eob-searchset": "eob.json",
        "provenance-readme": "readme.txt",
    }
    documents = tuple(
        replace(
            item,
            path=f"tests/fixtures/fhir/data-001/generated/{case_id}/{filenames[item.role]}",
        )
        for item in seed.documents
    )
    return SourceSet(
        classification="project-authored-synthetic",
        documents=documents,
        expected_digest=source_set_digest(documents),
    )


class ReferenceValidator:
    """Small executable interpretation of the versioned DATA-001 contract."""

    def __init__(self, repo_root: Path = REPO_ROOT) -> None:
        self.repo_root = repo_root
        self.boundary_raw = (CONTRACT_DIR / "boundary.json").read_bytes()
        self.package_lock_raw = (CONTRACT_DIR / "packages.lock.json").read_bytes()
        self.boundary = strict_json_loads(self.boundary_raw)
        self.package_lock = strict_json_loads(self.package_lock_raw)

    def validate(
        self,
        source_set: SourceSet | None = None,
        *,
        carin_available: bool = True,
    ) -> dict[str, Any]:
        source_set = source_set or load_seed_source_set(self.repo_root)
        parsed: dict[str, tuple[SourceDocument, Any]] = {}
        resources: list[tuple[SourceDocument, str, Any]] = []
        statuses = {name: "not-run" for name in LAYER_NAMES}

        failure = self._validate_source(source_set)
        if failure:
            statuses["source"] = "failed"
            return self._rejected(source_set, statuses, failure)
        statuses["source"] = "passed"

        for document in source_set.documents:
            if not document.parse_as_fhir:
                continue
            try:
                value = strict_json_loads(document.raw)
            except StrictJsonError:
                statuses["json"] = "failed"
                return self._rejected(
                    source_set,
                    statuses,
                    self._finding(
                        "JSON-SYNTAX-001",
                        "INVALID_JSON",
                        "Input is not strict UTF-8 JSON with unique object keys.",
                        document.path,
                    ),
                )
            if not isinstance(value, dict):
                statuses["json"] = "failed"
                return self._rejected(
                    source_set,
                    statuses,
                    self._finding(
                        "JSON-SYNTAX-001",
                        "TOP_LEVEL_NOT_OBJECT",
                        "FHIR JSON input must have an object at the top level.",
                        document.path,
                    ),
                )
            parsed[document.role] = (document, value)
        statuses["json"] = "passed"

        failure, resources = self._validate_support(parsed)
        if failure:
            statuses["support"] = "failed"
            return self._rejected(source_set, statuses, failure)
        statuses["support"] = "passed"

        failure = self._validate_required(resources, parsed)
        if failure:
            statuses["required-fields"] = "failed"
            return self._rejected(source_set, statuses, failure)
        statuses["required-fields"] = "passed"

        failure = self._validate_references(resources)
        if failure:
            statuses["references"] = "failed"
            return self._rejected(source_set, statuses, failure)
        statuses["references"] = "passed"

        failure = self._validate_content(resources, parsed)
        if failure:
            statuses["content-isolation"] = "failed"
            return self._rejected(source_set, statuses, failure)
        statuses["content-isolation"] = "passed"

        return self._accepted(source_set, statuses, resources, carin_available)

    def _validate_source(self, source_set: SourceSet) -> dict[str, Any] | None:
        accepted = self.boundary["source_set"]["accepted_classifications"]
        if source_set.classification not in accepted:
            return self._finding(
                "DATA-CLASS-001",
                "CLASSIFICATION_NOT_ACCEPTED",
                "Source classification is not approved for this synthetic-only boundary.",
                source_set.documents[0].path if source_set.documents else "dataset/readme.txt",
            )
        required_roles = set(self.boundary["source_set"]["required_roles"])
        roles = [item.role for item in source_set.documents]
        if set(roles) != required_roles or len(roles) != len(required_roles):
            return self._finding(
                "SOURCE-MANIFEST-001",
                "SOURCE_ROLE_SET_INVALID",
                "Declared source roles are missing, duplicated, or unsupported.",
                source_set.documents[0].path if source_set.documents else "dataset/readme.txt",
            )
        paths = [item.path for item in source_set.documents]
        for path in paths:
            pure = PurePosixPath(path)
            if pure.is_absolute() or ".." in pure.parts or str(pure) != path:
                return self._finding(
                    "SOURCE-MANIFEST-001",
                    "SOURCE_PATH_INVALID",
                    "A source path is not a normalized repository-relative path.",
                    "dataset/readme.txt",
                )
        if len(paths) != len(set(paths)):
            return self._finding(
                "SOURCE-MANIFEST-001",
                "SOURCE_PATH_DUPLICATE",
                "Declared source paths must be unique.",
                source_set.documents[0].path,
            )
        for item in source_set.documents:
            if len(item.raw) != item.expected_bytes or sha256_bytes(item.raw) != item.expected_sha256:
                return self._finding(
                    "SOURCE-MANIFEST-001",
                    "SOURCE_IDENTITY_MISMATCH",
                    "A source byte length or digest does not match its declaration.",
                    item.path,
                )
        if source_set_digest(source_set.documents) != source_set.expected_digest:
            return self._finding(
                "SOURCE-MANIFEST-001",
                "SOURCE_SET_DIGEST_MISMATCH",
                "The declared source-set digest does not match its member identities.",
                source_set.documents[0].path,
            )
        return None

    def _validate_support(
        self, parsed: dict[str, tuple[SourceDocument, Any]]
    ) -> tuple[dict[str, Any] | None, list[tuple[SourceDocument, str, Any]]]:
        resources: list[tuple[SourceDocument, str, Any]] = []
        patient_document, patient = parsed["patient"]
        if patient.get("resourceType") != "Patient":
            return (
                self._finding(
                    "FHIR-COMPAT-RESOURCE-001",
                    "UNSUPPORTED_STANDALONE_RESOURCE",
                    "The standalone document is not a supported Patient resource.",
                    patient_document.path,
                ),
                resources,
            )
        resources.append((patient_document, "", patient))

        for role, expected_type in (
            ("coverage-searchset", "Coverage"),
            ("pharmacy-eob-searchset", "ExplanationOfBenefit"),
        ):
            document, bundle = parsed[role]
            if bundle.get("resourceType") != "Bundle" or bundle.get("type") != "searchset":
                return (
                    self._finding(
                        "FHIR-COMPAT-ENVELOPE-001",
                        "UNSUPPORTED_BUNDLE_ENVELOPE",
                        "Only the declared FHIR searchset Bundle envelope is supported.",
                        document.path,
                    ),
                    resources,
                )
            entries = bundle.get("entry")
            if not isinstance(entries, list) or not entries:
                return (
                    self._finding(
                        "FHIR-COMPAT-ENVELOPE-001",
                        "EMPTY_OR_INVALID_BUNDLE",
                        "A supported searchset Bundle must contain a non-empty entry array.",
                        document.path,
                        "/entry",
                    ),
                    resources,
                )
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict) or not isinstance(entry.get("resource"), dict):
                    return (
                        self._finding(
                            "FHIR-COMPAT-ENVELOPE-001",
                            "INVALID_BUNDLE_ENTRY",
                            "Every Bundle entry must contain one resource object.",
                            document.path,
                            f"/entry/{index}",
                        ),
                        resources,
                    )
                resource = entry["resource"]
                if resource.get("resourceType") != expected_type:
                    return (
                        self._finding(
                            "FHIR-COMPAT-RESOURCE-001",
                            "MIXED_OR_UNSUPPORTED_BUNDLE_RESOURCE",
                            "Bundle entries must be homogeneous supported resources.",
                            document.path,
                            f"/entry/{index}/resource",
                        ),
                        resources,
                    )
                resources.append((document, f"/entry/{index}/resource", resource))

        for document, pointer, resource in resources:
            resource_type = resource["resourceType"]
            meta = resource.get("meta")
            profiles = meta.get("profile") if isinstance(meta, dict) else None
            if profiles is None:
                continue
            if (
                not isinstance(profiles, list)
                or len(profiles) != 1
                or profiles[0] not in self.boundary["profile_markers"][resource_type]
            ):
                return (
                    self._finding(
                        "FHIR-COMPAT-PROFILE-MARKER-001",
                        "UNSUPPORTED_PROFILE_MARKER",
                        "The resource profile marker is not an exact supported routing marker.",
                        document.path,
                        f"{pointer}/meta/profile",
                    ),
                    resources,
                )
        return None, resources

    def _validate_required(
        self,
        resources: list[tuple[SourceDocument, str, Any]],
        parsed: dict[str, tuple[SourceDocument, Any]],
    ) -> dict[str, Any] | None:
        for role in ("coverage-searchset", "pharmacy-eob-searchset"):
            document, bundle = parsed[role]
            if not self._nonempty_string(bundle.get("id")):
                return self._required_finding(document.path, "/id")
            total = bundle.get("total")
            if total is not None and (
                isinstance(total, bool)
                or not isinstance(total, int)
                or total < len(bundle["entry"])
            ):
                return self._required_finding(document.path, "/total")

        for document, pointer, resource in resources:
            resource_type = resource["resourceType"]
            if not self._nonempty_string(resource.get("id")) or not FHIR_ID.fullmatch(resource["id"]):
                return self._required_finding(document.path, f"{pointer}/id")
            meta = resource.get("meta")
            if not isinstance(meta, dict) or not isinstance(meta.get("profile"), list) or not meta["profile"]:
                return self._required_finding(document.path, f"{pointer}/meta/profile")
            if resource_type == "Patient":
                if not self._nonempty_list(resource.get("identifier")):
                    return self._required_finding(document.path, f"{pointer}/identifier")
                if not self._nonempty_list(resource.get("name")):
                    return self._required_finding(document.path, f"{pointer}/name")
            elif resource_type == "Coverage":
                if not self._nonempty_string(resource.get("status")):
                    return self._required_finding(document.path, f"{pointer}/status")
                if not self._nonempty_dict(resource.get("type")):
                    return self._required_finding(document.path, f"{pointer}/type")
                beneficiary = resource.get("beneficiary")
                if not isinstance(beneficiary, dict) or not self._nonempty_string(beneficiary.get("reference")):
                    return self._required_finding(document.path, f"{pointer}/beneficiary/reference")
            else:
                for key in ("status", "use"):
                    if not self._nonempty_string(resource.get(key)):
                        return self._required_finding(document.path, f"{pointer}/{key}")
                if not self._nonempty_dict(resource.get("type")):
                    return self._required_finding(document.path, f"{pointer}/type")
                patient = resource.get("patient")
                if not isinstance(patient, dict) or not self._nonempty_string(patient.get("reference")):
                    return self._required_finding(document.path, f"{pointer}/patient/reference")
                if not self._nonempty_list(resource.get("insurance")):
                    return self._required_finding(document.path, f"{pointer}/insurance")
                if not self._nonempty_list(resource.get("item")):
                    return self._required_finding(document.path, f"{pointer}/item")
                for index, insurance in enumerate(resource["insurance"]):
                    coverage = insurance.get("coverage") if isinstance(insurance, dict) else None
                    if not isinstance(coverage, dict) or not self._nonempty_string(coverage.get("reference")):
                        return self._required_finding(
                            document.path,
                            f"{pointer}/insurance/{index}/coverage/reference",
                        )
        return None

    def _validate_references(
        self, resources: list[tuple[SourceDocument, str, Any]]
    ) -> dict[str, Any] | None:
        identities: dict[tuple[str, str], list[tuple[SourceDocument, str]]] = {}
        for document, pointer, resource in resources:
            identity = (resource["resourceType"], resource["id"])
            identities.setdefault(identity, []).append((document, pointer))
        duplicates = [identity for identity, found in identities.items() if len(found) != 1]
        if duplicates:
            document, pointer = identities[duplicates[0]][0]
            return self._finding(
                "FHIR-COMPAT-ID-001",
                "DUPLICATE_RESOURCE_IDENTITY",
                "Each resource type and id identity must occur exactly once.",
                document.path,
                f"{pointer}/id",
            )

        for document, pointer, resource in resources:
            reference_paths: list[tuple[str, str, str]] = []
            if resource["resourceType"] == "Coverage":
                reference_paths.append((
                    f"{pointer}/beneficiary/reference",
                    resource["beneficiary"]["reference"],
                    "Patient",
                ))
            elif resource["resourceType"] == "ExplanationOfBenefit":
                reference_paths.append((
                    f"{pointer}/patient/reference",
                    resource["patient"]["reference"],
                    "Patient",
                ))
                for index, insurance in enumerate(resource["insurance"]):
                    reference_paths.append((
                        f"{pointer}/insurance/{index}/coverage/reference",
                        insurance["coverage"]["reference"],
                        "Coverage",
                    ))
            for reference_pointer, reference, expected_type in reference_paths:
                matched = RELATIVE_REFERENCE.fullmatch(reference)
                if matched is None or matched.group(1) != expected_type:
                    return self._finding(
                        "FHIR-COMPAT-REF-001",
                        "INVALID_REQUIRED_REFERENCE",
                        "A required reference is not a same-source-set relative reference of the expected type.",
                        document.path,
                        reference_pointer,
                    )
                if len(identities.get((matched.group(1), matched.group(2)), [])) != 1:
                    return self._finding(
                        "FHIR-COMPAT-REF-001",
                        "UNRESOLVED_REQUIRED_REFERENCE",
                        "A required reference does not resolve exactly once in the declared source set.",
                        document.path,
                        reference_pointer,
                    )
        return None

    def _validate_content(
        self,
        resources: list[tuple[SourceDocument, str, Any]],
        parsed: dict[str, tuple[SourceDocument, Any]],
    ) -> dict[str, Any] | None:
        rejected_keys = set(self.boundary["rejected_content_keys_any_depth"])
        for document, pointer, resource in resources:
            allowed = set(self.boundary["resources"][resource["resourceType"]]["allowed_top_level_fields"])
            if not set(resource).issubset(allowed):
                return self._content_finding(document.path, pointer)
            for child_pointer, value in _walk(resource, pointer):
                if isinstance(value, dict) and rejected_keys.intersection(value):
                    return self._content_finding(document.path, child_pointer)

        for role in ("coverage-searchset", "pharmacy-eob-searchset"):
            document, bundle = parsed[role]
            if not set(bundle).issubset(set(self.boundary["bundle"]["allowed_top_level_fields"])):
                return self._content_finding(document.path, "")
            for index, entry in enumerate(bundle["entry"]):
                if not set(entry).issubset(set(self.boundary["bundle"]["entry_allowed_fields"])):
                    return self._content_finding(document.path, f"/entry/{index}")

        extension_uris: set[str] = set()
        systems: set[str] = set()
        for _, _, resource in resources:
            self._collect_registries(resource, extension_uris, systems)
        for name, values in (("extension_uris", extension_uris), ("system_uris", systems)):
            expected = self.boundary["registries"][name]
            digest = sha256_bytes(("\n".join(sorted(values)) + "\n").encode("utf-8"))
            if len(values) != expected["count"] or digest != expected["sha256"]:
                return self._content_finding(resources[0][0].path, "")
        return None

    def _accepted(
        self,
        source_set: SourceSet,
        statuses: dict[str, str],
        resources: list[tuple[SourceDocument, str, Any]],
        carin_available: bool,
    ) -> dict[str, Any]:
        terminology = self._terminology(resources)
        if carin_available:
            carin = self._carin_evidence()
            carin_state = "carin-nonconformant"
        else:
            carin = {
                "status": "diagnostic-unavailable",
                "acceptance_authority": False,
                "tool": "HL7 FHIR Validator CLI#6.10.2",
                "package": "hl7.fhir.us.carin-bb#2.2.0",
                "counts": dict(ZERO_COUNTS),
                "findings": [
                    self._finding(
                        "CARIN-DIAGNOSTIC-001",
                        "PINNED_DIAGNOSTIC_UNAVAILABLE",
                        "Pinned offline CARIN diagnostic evidence is unavailable.",
                        source_set.documents[0].path,
                        source="carin",
                    )
                ],
                "availability_error": "Pinned offline diagnostic evidence unavailable",
            }
            carin_state = "carin-diagnostic-unavailable"
        states = ["minimal-profile-valid", carin_state]
        if terminology["status"] == "unverified":
            states.append("terminology-unverified")
        return self._base_outcome(
            source_set,
            "accepted",
            states,
            statuses,
            [],
            carin,
            terminology,
        )

    def _rejected(
        self,
        source_set: SourceSet,
        statuses: dict[str, str],
        failure: dict[str, Any],
    ) -> dict[str, Any]:
        return self._base_outcome(
            source_set,
            "rejected",
            ["rejected"],
            statuses,
            [failure],
            {
                "status": "not-run-rejected",
                "acceptance_authority": False,
                "tool": "HL7 FHIR Validator CLI#6.10.2",
                "package": "hl7.fhir.us.carin-bb#2.2.0",
                "counts": dict(ZERO_COUNTS),
                "findings": [],
            },
            {
                "status": "not-evaluated-rejected",
                "acceptance_authority": False,
                "membership_asserted": False,
                "opaque_values": [],
            },
        )

    def _base_outcome(
        self,
        source_set: SourceSet,
        decision: str,
        states: list[str],
        statuses: dict[str, str],
        project_findings: list[dict[str, Any]],
        carin: dict[str, Any],
        terminology: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "contract_id": self.boundary["contract_id"],
            "contract_version": self.boundary["contract_version"],
            "decision": decision,
            "states": states,
            "source_set_sha256": source_set_digest(source_set.documents),
            "boundary_sha256": sha256_bytes(self.boundary_raw),
            "package_lock_sha256": sha256_bytes(self.package_lock_raw),
            "layers": [{"name": name, "status": statuses[name]} for name in LAYER_NAMES],
            "project_findings": project_findings,
            "carin": carin,
            "terminology": terminology,
        }

    def _carin_evidence(self) -> dict[str, Any]:
        evidence = self.package_lock["compatibility_evidence"]
        counts = evidence["counts"]
        findings = []
        ordinal = 0
        for path in (
            "dataset/patient_bbuser29999.json",
            "dataset/coverage_bundle_bbuser29999.json",
            "dataset/eob_bundle_bbuser29999.json",
        ):
            for severity in ("fatal", "error", "warning", "information"):
                for _ in range(counts[path][severity]):
                    ordinal += 1
                    findings.append(
                        self._finding(
                            "CARIN-DIAGNOSTIC-001",
                            f"PINNED_RAW_FINDING_{ordinal:06d}",
                            "Pinned CARIN diagnostic finding retained in digest-addressed untrusted evidence.",
                            path,
                            source="carin",
                            severity=severity,
                        )
                    )
        return {
            "status": "nonconformant",
            "acceptance_authority": False,
            "tool": "HL7 FHIR Validator CLI#6.10.2",
            "package": "hl7.fhir.us.carin-bb#2.2.0",
            "counts": dict(counts["total"]),
            "raw_evidence": {
                "sha256": evidence["raw_operation_outcome"]["sha256"],
                "format": "FHIR-R4-Bundle-of-OperationOutcome",
                "trusted_content": False,
            },
            "findings": findings,
        }

    def _terminology(
        self, resources: list[tuple[SourceDocument, str, Any]]
    ) -> dict[str, Any]:
        opaque = []
        for document, base_pointer, resource in resources:
            for pointer, value in _walk(resource, base_pointer):
                if isinstance(value, dict) and self._nonempty_string(value.get("system")):
                    opaque.append(
                        {
                            "source_path": document.path,
                            "json_pointer": f"{pointer}/system",
                            "system": value["system"],
                            "code_present": self._nonempty_string(value.get("code")),
                        }
                    )
        return {
            "status": "unverified" if opaque else "verified",
            "acceptance_authority": False,
            "membership_asserted": False,
            "opaque_values": opaque,
        }

    @staticmethod
    def _collect_registries(value: Any, extensions: set[str], systems: set[str]) -> None:
        if isinstance(value, dict):
            extension = value.get("extension")
            if isinstance(extension, list):
                for item in extension:
                    if isinstance(item, dict) and isinstance(item.get("url"), str):
                        extensions.add(item["url"])
            if isinstance(value.get("system"), str):
                systems.add(value["system"])
            for child in value.values():
                ReferenceValidator._collect_registries(child, extensions, systems)
        elif isinstance(value, list):
            for child in value:
                ReferenceValidator._collect_registries(child, extensions, systems)

    @staticmethod
    def _nonempty_string(value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())

    @staticmethod
    def _nonempty_list(value: Any) -> bool:
        return isinstance(value, list) and bool(value)

    @staticmethod
    def _nonempty_dict(value: Any) -> bool:
        return isinstance(value, dict) and bool(value)

    def _required_finding(self, source_path: str, pointer: str) -> dict[str, Any]:
        return self._finding(
            "FHIR-COMPAT-REQUIRED-001",
            "REQUIRED_ANCHOR_INVALID",
            "A project-required FHIR anchor is missing, empty, or structurally invalid.",
            source_path,
            pointer,
        )

    def _content_finding(self, source_path: str, pointer: str) -> dict[str, Any]:
        return self._finding(
            "FHIR-COMPAT-CONTENT-001",
            "UNSUPPORTED_OR_ACTIVE_CONTENT",
            "Input contains content outside the exact passive compatibility registry.",
            source_path,
            pointer,
        )

    @staticmethod
    def _finding(
        rule_id: str,
        machine_code: str,
        message: str,
        source_path: str,
        json_pointer: str = "",
        *,
        source: str = "project",
        severity: str = "error",
    ) -> dict[str, Any]:
        return {
            "rule_id": rule_id,
            "source": source,
            "severity": severity,
            "machine_code": machine_code,
            "message": message,
            "source_path": source_path,
            "json_pointer": json_pointer,
        }


def mutate_json_document(
    source_set: SourceSet,
    role: str,
    mutator: Callable[[dict[str, Any]], None],
) -> SourceSet:
    value = strict_json_loads(source_set.document(role).raw)
    mutator(value)
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return source_set.replace_document(role, raw)
