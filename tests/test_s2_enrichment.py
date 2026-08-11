"""S2 — product enrichment and category revenue. See docs/user-stories.md."""
from datetime import date, datetime
from decimal import Decimal

import pytest

from helpers import sorted_rows
from retail_pipeline.schemas import CLEAN_SALES_SCHEMA, PRODUCTS_SCHEMA
from retail_pipeline.transforms import build_category_revenue, enrich_with_products

pytestmark = pytest.mark.S2

SALES = [
    ("T-1", "S-01", "P-100", 2, Decimal("4.50"), datetime(2026, 3, 13, 9, 0), datetime(2026, 3, 13, 23, 0), date(2026, 3, 13)),
    ("T-2", "S-01", "P-102", 1, Decimal("15.00"), datetime(2026, 3, 13, 11, 0), datetime(2026, 3, 13, 23, 0), date(2026, 3, 13)),
    ("T-3", "S-02", "P-999", 1, Decimal("25.00"), datetime(2026, 3, 13, 14, 30), datetime(2026, 3, 13, 23, 0), date(2026, 3, 13)),
]
PRODUCTS = [
    ("P-100", "Wireless Mouse", "Electronics", Decimal("2.10")),
    ("P-102", "Desk Lamp", "Home", Decimal("6.75")),
]


def enriched(spark):
    return enrich_with_products(
        spark.createDataFrame(SALES, schema=CLEAN_SALES_SCHEMA),
        spark.createDataFrame(PRODUCTS, schema=PRODUCTS_SCHEMA),
    )


def test_known_products_gain_name_and_category(spark):
    rows = sorted_rows(enriched(spark).select("transaction_id", "product_name", "category"))
    assert ("T-1", "Wireless Mouse", "Electronics") in rows
    assert ("T-2", "Desk Lamp", "Home") in rows


def test_unknown_products_are_kept_with_category_unknown(spark):
    rows = {r["transaction_id"]: r for r in enriched(spark).collect()}
    assert rows["T-3"]["category"] == "UNKNOWN"
    assert rows["T-3"]["product_name"] is None
    assert len(rows) == 3


def test_no_sales_rows_are_lost_or_duplicated(spark):
    assert enriched(spark).count() == 3


def test_category_revenue_rolls_up(spark):
    rows = sorted_rows(build_category_revenue(enriched(spark)).select("category", "total_revenue"))
    assert rows == [
        ("Electronics", Decimal("9.00")),
        ("Home", Decimal("15.00")),
        ("UNKNOWN", Decimal("25.00")),
    ]
