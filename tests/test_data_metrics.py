"""Regression test untuk data mart, filter, KPI, RFM, cohort, dan ekspor."""

from __future__ import annotations

import io

import pandas as pd
import pytest

import app

EXPECTED_ROWS = {
    "customers": 99_441,
    "sellers": 3_095,
    "payments": 103_886,
    "translation": 71,
    "products": 32_951,
    "geolocation": 1_000_163,
    "reviews": 104_719,
    "items": 112_650,
    "orders": 99_441,
}


@pytest.mark.slow
def test_source_rows_and_data_model_grain(data_bundle: dict[str, object]) -> None:
    datasets = data_bundle["datasets"]
    model = data_bundle["model"]

    assert {key: len(frame) for key, frame in datasets.items()} == EXPECTED_ROWS
    assert len(model["fact"]) == EXPECTED_ROWS["items"]
    assert len(model["payments"]) == EXPECTED_ROWS["payments"]
    assert set(model) == {"fact", "payments", "quality"}


@pytest.mark.slow
def test_default_kpi_regression(data_bundle: dict[str, object]) -> None:
    model = data_bundle["model"]
    fact = model["fact"]

    start_date = fact["order_purchase_timestamp"].min().normalize()
    end_date = fact["order_purchase_timestamp"].max().normalize()
    filtered = app.apply_filters(
        fact,
        start_date,
        end_date,
        customer_states=[],
        categories=[],
        statuses=["delivered"],
        seller_states=[],
    )
    order_view = filtered.drop_duplicates("order_id")

    assert len(filtered) == 110_197
    assert filtered["order_id"].nunique() == 96_478
    assert filtered["customer_unique_id"].nunique() == 93_358
    assert float(filtered["gmv"].sum()) == pytest.approx(13_221_498.11, abs=0.01)
    assert float(filtered["order_value"].sum()) == pytest.approx(
        15_419_773.75, abs=0.01
    )
    assert float(filtered["order_value"].sum() / filtered["order_id"].nunique()) == (
        pytest.approx(159.82683876116835, abs=1e-10)
    )
    assert float(order_view["review_score"].mean()) == pytest.approx(
        4.156186520855942, abs=1e-12
    )


@pytest.mark.slow
def test_customer_value_regression(data_bundle: dict[str, object]) -> None:
    model = data_bundle["model"]
    fact = model["fact"]

    filtered = app.apply_filters(
        fact,
        fact["order_purchase_timestamp"].min().normalize(),
        fact["order_purchase_timestamp"].max().normalize(),
        customer_states=[],
        categories=[],
        statuses=["delivered"],
        seller_states=[],
    )
    customer_value = app.build_customer_value_analysis(
        filtered.drop_duplicates("order_id"),
        model["payments"],
    )

    assert customer_value is not None
    assert customer_value["repeat_customer_rate"] == pytest.approx(
        0.03000278497825575, abs=1e-15
    )
    assert customer_value["month1_retention"] == pytest.approx(
        0.004827206641135597, abs=1e-15
    )
    assert customer_value["month3_retention"] == pytest.approx(
        0.0025468582116279993, abs=1e-15
    )

    summary = customer_value["segment_summary"].set_index("segment")
    assert summary.index[0] == "High-Value One-Time"
    assert int(summary.loc["High-Value One-Time", "customers"]) == 8_466
    assert float(summary.loc["High-Value One-Time", "payment_share"]) == (
        pytest.approx(0.3488799979045109, abs=1e-12)
    )
    assert list(customer_value["cohort_view"].columns) == list(range(7))
    assert len(customer_value["cohort_view"]) == 14


@pytest.mark.slow
def test_filters_empty_state_and_export(data_bundle: dict[str, object]) -> None:
    model = data_bundle["model"]
    fact = model["fact"]

    # Hari pertama dataset hanya berisi order berstatus shipped. Dengan default
    # delivered, hasil harus kosong dan memicu empty-state aplikasi.
    empty = app.apply_filters(
        fact,
        pd.Timestamp("2016-09-04"),
        pd.Timestamp("2016-09-04"),
        customer_states=[],
        categories=[],
        statuses=["delivered"],
        seller_states=[],
    )
    assert empty.empty
    assert app.build_customer_value_analysis(
        empty.drop_duplicates("order_id"),
        model["payments"],
    ) is None
    assert app.create_order_export(empty) == b""

    sample = app.apply_filters(
        fact,
        pd.Timestamp("2018-01-01"),
        pd.Timestamp("2018-01-31"),
        customer_states=["SP"],
        categories=[],
        statuses=["delivered"],
        seller_states=[],
    )
    assert not sample.empty
    assert sample["customer_state"].astype(str).eq("SP").all()
    assert sample["order_status"].astype(str).eq("delivered").all()
    assert sample["order_purchase_timestamp"].between(
        "2018-01-01", "2018-01-31 23:59:59.999999"
    ).all()

    payload = app.create_order_export(sample)
    exported = pd.read_csv(io.BytesIO(payload), encoding="utf-8-sig")
    assert len(exported) == sample["order_id"].nunique()
    assert {
        "order_id",
        "item_count",
        "product_gmv",
        "freight_value",
        "order_value",
        "categories",
    }.issubset(exported.columns)
