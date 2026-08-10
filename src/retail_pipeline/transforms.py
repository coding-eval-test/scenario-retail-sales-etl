"""The business tables. This is where the work items live — see docs/user-stories.md
and docs/bug-reports.md. Tests in tests/ define each output contract exactly."""
from pyspark.sql import DataFrame


def dedupe_sales(sales: DataFrame) -> DataFrame:
    """One row per transaction, even when a feed file was re-sent."""
    # Re-sent feed files repeat transactions; dropDuplicates removes the repeats.
    return sales.dropDuplicates()


def build_daily_store_sales(sales: DataFrame) -> DataFrame:
    """One row per store per business date: total_revenue, units_sold, txn_count."""
    raise NotImplementedError("S1 — see docs/user-stories.md")


def enrich_with_products(sales: DataFrame, products: DataFrame) -> DataFrame:
    """Sales rows enriched with product_name and category from the product master."""
    raise NotImplementedError("S2 — see docs/user-stories.md")


def build_category_revenue(enriched: DataFrame) -> DataFrame:
    """One row per category: total_revenue."""
    raise NotImplementedError("S2 — see docs/user-stories.md")
