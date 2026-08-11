"""S1 — daily store sales summary. See docs/user-stories.md."""
from datetime import date, datetime
from decimal import Decimal

import pytest

from helpers import sorted_rows
from retail_pipeline.schemas import CLEAN_SALES_SCHEMA
from retail_pipeline.transforms import build_daily_store_sales

pytestmark = pytest.mark.S1

ROWS = [
    ("T-1", "S-01", "P-100", 2, Decimal("4.50"), datetime(2026, 3, 13, 9, 0), datetime(2026, 3, 13, 23, 0), date(2026, 3, 13)),
    ("T-2", "S-01", "P-102", 1, Decimal("15.00"), datetime(2026, 3, 13, 11, 0), datetime(2026, 3, 13, 23, 0), date(2026, 3, 13)),
    ("T-3", "S-01", "P-100", 1, Decimal("4.50"), datetime(2026, 3, 14, 10, 0), datetime(2026, 3, 14, 23, 0), date(2026, 3, 14)),
    ("T-4", "S-02", "P-101", 1, Decimal("1299.00"), datetime(2026, 3, 13, 12, 0), datetime(2026, 3, 13, 23, 0), date(2026, 3, 13)),
]


def summary(spark):
    return build_daily_store_sales(spark.createDataFrame(ROWS, schema=CLEAN_SALES_SCHEMA))


def test_output_columns(spark):
    assert set(summary(spark).columns) == {"store_id", "business_date", "total_revenue", "units_sold", "txn_count"}


def test_one_row_per_store_per_day(spark):
    keys = sorted_rows(summary(spark).select("store_id", "business_date"))
    assert keys == [
        ("S-01", date(2026, 3, 13)),
        ("S-01", date(2026, 3, 14)),
        ("S-02", date(2026, 3, 13)),
    ]


def test_revenue_units_and_count_aggregate_correctly(spark):
    rows = sorted_rows(summary(spark).select("store_id", "business_date", "total_revenue", "units_sold", "txn_count"))
    assert rows == [
        ("S-01", date(2026, 3, 13), Decimal("24.00"), 3, 2),
        ("S-01", date(2026, 3, 14), Decimal("4.50"), 1, 1),
        ("S-02", date(2026, 3, 13), Decimal("1299.00"), 1, 1),
    ]
