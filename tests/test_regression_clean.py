"""The shipped cleaning behavior — must keep passing."""
from datetime import date, datetime
from decimal import Decimal

import pytest

from retail_pipeline.clean import clean_sales
from retail_pipeline.schemas import CLEAN_SALES_SCHEMA, RAW_SALES_SCHEMA

pytestmark = pytest.mark.Regression


def make_raw(spark, rows):
    return spark.createDataFrame(rows, schema=RAW_SALES_SCHEMA)


def test_currency_strings_parse_to_decimal(spark):
    raw = make_raw(spark, [
        ("T-1", "S-01", "P-100", "2", "$4.50", "2026-03-13T09:15:00", "2026-03-13T23:00:00"),
        ("T-2", "S-01", "P-101", "1", "1,299.00", "2026-03-13T10:02:00", "2026-03-13T23:00:00"),
        ("T-3", "S-02", "P-100", "3", " 4.50 ", "2026-03-13T11:45:00", "2026-03-13T23:00:00"),
    ])
    out = {row["transaction_id"]: row["unit_price"] for row in clean_sales(raw).collect()}
    assert out == {"T-1": Decimal("4.50"), "T-2": Decimal("1299.00"), "T-3": Decimal("4.50")}


def test_identifiers_are_trimmed(spark):
    raw = make_raw(spark, [(" T-1 ", " S-01", "P-100 ", "1", "4.50", "2026-03-13T09:15:00", "2026-03-13T23:00:00")])
    row = clean_sales(raw).collect()[0]
    assert (row["transaction_id"], row["store_id"], row["product_id"]) == ("T-1", "S-01", "P-100")


def test_rows_without_transaction_id_are_dropped(spark):
    raw = make_raw(spark, [
        (None, "S-01", "P-100", "1", "4.50", "2026-03-13T09:15:00", "2026-03-13T23:00:00"),
        ("", "S-01", "P-100", "1", "4.50", "2026-03-13T09:15:00", "2026-03-13T23:00:00"),
        ("T-1", "S-01", "P-100", "1", "4.50", "2026-03-13T09:15:00", "2026-03-13T23:00:00"),
    ])
    assert [r["transaction_id"] for r in clean_sales(raw).collect()] == ["T-1"]


def test_quantity_and_timestamps_are_typed(spark):
    raw = make_raw(spark, [("T-1", "S-01", "P-100", "3", "4.50", "2026-03-13T09:15:00", "2026-03-13T23:00:00")])
    row = clean_sales(raw).collect()[0]
    assert row["quantity"] == 3
    assert row["sale_ts"] == datetime(2026, 3, 13, 9, 15)
    assert row["ingested_at"] == datetime(2026, 3, 13, 23, 0)


def test_business_date_derives_from_sale_ts_not_ingestion(spark):
    raw = make_raw(spark, [("T-1", "S-01", "P-100", "1", "4.50", "2026-03-13T09:15:00", "2026-03-14T08:00:00")])
    assert clean_sales(raw).collect()[0]["business_date"] == date(2026, 3, 13)


def test_output_columns_and_types_match_the_clean_contract(spark):
    raw = make_raw(spark, [("T-1", "S-01", "P-100", "1", "4.50", "2026-03-13T09:15:00", "2026-03-13T23:00:00")])
    actual = [(f.name, f.dataType) for f in clean_sales(raw).schema.fields]
    expected = [(f.name, f.dataType) for f in CLEAN_SALES_SCHEMA.fields]
    assert actual == expected
