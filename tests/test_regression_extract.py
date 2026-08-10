"""The shipped extract behavior — must keep passing."""
from decimal import Decimal
from pathlib import Path

import pytest

from retail_pipeline.extract import read_products, read_sales_feed, read_stores
from retail_pipeline.schemas import PRODUCTS_SCHEMA, RAW_SALES_SCHEMA, STORES_SCHEMA

pytestmark = pytest.mark.Regression

RAW_DIR = str(Path(__file__).resolve().parents[1] / "data" / "raw")


def test_sales_feed_reads_all_files_with_the_raw_schema(spark):
    df = read_sales_feed(spark, f"{RAW_DIR}/sales_*.csv")
    assert df.schema == RAW_SALES_SCHEMA
    assert df.count() == 13


def test_products_read_typed(spark):
    df = read_products(spark, f"{RAW_DIR}/products.csv")
    assert df.schema == PRODUCTS_SCHEMA
    rows = {r["product_id"]: r for r in df.collect()}
    assert rows["P-100"]["unit_cost"] == Decimal("2.10")
    assert len(rows) == 4


def test_stores_read(spark):
    df = read_stores(spark, f"{RAW_DIR}/stores.csv")
    assert df.schema == STORES_SCHEMA
    assert df.count() == 2
