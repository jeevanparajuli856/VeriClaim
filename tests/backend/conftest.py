from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from backend.app.extractor import ExtractedDataset, extract_supported_dataset
from backend.app.loader import SOURCE_PATHS, default_project_root, load_approved_sources


@pytest.fixture
def extracted() -> ExtractedDataset:
    return extract_supported_dataset(load_approved_sources())


def source_hashes() -> dict[str, str]:
    root = default_project_root()
    return {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for _, relative in SOURCE_PATHS
    }
