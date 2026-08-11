"""B1 — doubled revenue after a feed resend. See docs/bug-reports.md."""
from datetime import date, datetime
from decimal import Decimal

import pytest

from retail_pipeline.schemas import CLEAN_SALES_SCHEMA
from retail_pipeline.transforms import dedupe_sales

pytestmark = pytest.mark.B1

ORIGINAL = ("T-2001", "S-01", "P-100", 2, Decimal("4.50"),
            datetime(2026, 3, 14, 9, 5), datetime(2026, 3, 14, 23, 0), date(2026, 3, 14))
RESENT_CORRECTED = ("T-2001", "S-01", "P-100", 3, Decimal("4.50"),
                    datetime(2026, 3, 14, 9, 5), datetime(2026, 3, 15, 8, 0), date(2026, 3, 14))
UNIQUE = ("T-2002", "S-02", "P-101", 1, Decimal("1299.00"),
          datetime(2026, 3, 14, 13, 20), datetime(2026, 3, 14, 23, 0), date(2026, 3, 14))


def deduped(spark):
    frame = spark.createDataFrame([ORIGINAL, RESENT_CORRECTED, UNIQUE], schema=CLEAN_SALES_SCHEMA)
    return dedupe_sales(frame)


def test_one_row_per_transaction(spark):
    ids = sorted(r["transaction_id"] for r in deduped(spark).collect())
    assert ids == ["T-2001", "T-2002"]


def test_the_latest_resent_version_wins(spark):
    survivors = [tuple(r) for r in deduped(spark).collect() if r["transaction_id"] == "T-2001"]
    assert survivors == [RESENT_CORRECTED]
