"""Fixture bersama untuk quality gate v2.0.0."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import app  # noqa: E402


@pytest.fixture(scope="session")
def data_bundle() -> dict[str, object]:
    """Memuat sembilan CSV dan data mart satu kali per sesi pytest."""
    local_sources = app.discover_local_sources()
    assert set(local_sources) == set(app.REQUIRED_FILES)

    datasets, fingerprint, missing = app.load_sources(local_sources, [])
    assert not missing
    assert not app.validate_columns(datasets)
    assert not app.validate_dataset_completeness(datasets)

    return {
        "datasets": datasets,
        "fingerprint": fingerprint,
        "model": app.build_data_model(fingerprint, datasets),
    }
