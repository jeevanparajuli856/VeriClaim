"""Read the fixed repository-owned synthetic inputs without mutation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .models import SourceFile

MAX_FILE_BYTES = 1_048_576

SOURCE_PATHS: tuple[tuple[Literal["patient", "coverage", "eob"], str], ...] = (
    ("patient", "dataset/patient_bbuser29999.json"),
    ("coverage", "dataset/coverage_bundle_bbuser29999.json"),
    ("eob", "dataset/eob_bundle_bbuser29999.json"),
)


class PipelineError(Exception):
    """Sanitized deterministic-pipeline failure."""

    def __init__(self, code: str, public_message: str) -> None:
        super().__init__(public_message)
        self.code = code
        self.public_message = public_message


@dataclass(frozen=True)
class LoadedSource:
    alias: Literal["patient", "coverage", "eob"]
    relative_path: str
    document: dict[str, Any]
    metadata: SourceFile


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_approved_sources(project_root: Path | None = None) -> dict[str, LoadedSource]:
    """Load only the compile-time allowlist; no caller-controlled file is accepted."""

    root = (project_root or default_project_root()).resolve()
    loaded: dict[str, LoadedSource] = {}
    for alias, relative_path in SOURCE_PATHS:
        path = (root / relative_path).resolve()
        expected_parent = (root / "dataset").resolve()
        if path.parent != expected_parent:
            raise PipelineError("SOURCE_UNAVAILABLE", "An approved synthetic source is unavailable.")
        try:
            size = path.stat().st_size
            if size > MAX_FILE_BYTES:
                raise PipelineError("SOURCE_TOO_LARGE", "An approved synthetic source exceeds the 1 MiB limit.")
            raw = path.read_bytes()
        except PipelineError:
            raise
        except (OSError, ValueError):
            raise PipelineError("SOURCE_UNAVAILABLE", "An approved synthetic source is unavailable.") from None
        if not raw:
            raise PipelineError("SOURCE_INVALID_JSON", "An approved synthetic source is not valid JSON.")
        try:
            decoded = raw.decode("utf-8")
            document = json.loads(decoded, parse_float=str, parse_int=str)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raise PipelineError("SOURCE_INVALID_JSON", "An approved synthetic source is not valid UTF-8 JSON.") from None
        if not isinstance(document, dict):
            raise PipelineError("SOURCE_SHAPE_UNSUPPORTED", "An approved synthetic source has an unsupported shape.")
        metadata = SourceFile(
            alias=alias,
            path=relative_path,
            sha256=hashlib.sha256(raw).hexdigest(),
            size_bytes=len(raw),
        )
        loaded[alias] = LoadedSource(alias, relative_path, document, metadata)
    return loaded
