"""Smoke test kelima bagian dashboard melalui API testing resmi Streamlit."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"

pytestmark = [pytest.mark.slow, pytest.mark.streamlit]


def _assert_no_runtime_error(app_test: AppTest) -> None:
    assert not app_test.exception
    assert not app_test.error


def test_all_sections_filters_empty_state_and_export_button() -> None:
    app_test = AppTest.from_file(APP_PATH, default_timeout=240).run(timeout=240)
    _assert_no_runtime_error(app_test)

    assert app_test.button_group(key="dashboard_section").value == "Ringkasan"
    assert app_test.multiselect[2].value == ["delivered"]
    assert any(button.label == "Siapkan file CSV" for button in app_test.button)

    expected_markers = {
        "Ringkasan": "Komposisi status",
        "Customer & Peta": "Profil wilayah",
        "Customer Value": "Cohort retention bulanan",
        "Produk & Seller": "Matriks portofolio kategori",
        "Layanan & Pembayaran": "Distribusi rating",
    }

    for section, marker in expected_markers.items():
        app_test.button_group(key="dashboard_section").set_value(section)
        app_test.run(timeout=240)
        _assert_no_runtime_error(app_test)
        assert app_test.button_group(key="dashboard_section").value == section
        assert any(marker in markdown.value for markdown in app_test.markdown)

    # 4 September 2016 tidak memiliki delivered order. Ini mengunci empty-state
    # dari kombinasi filter yang valid, bukan dengan nilai widget buatan.
    app_test.date_input[0].set_value((date(2016, 9, 4), date(2016, 9, 4)))
    app_test.run(timeout=240)
    assert not app_test.exception
    assert any(
        "Tidak ada data yang cocok" in warning.value
        for warning in app_test.warning
    )
