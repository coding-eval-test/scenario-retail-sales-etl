"""Run the pipeline over data/raw and print the results. A viewing harness —
not graded, and it never writes anything through Spark."""
import os
import sys
from pathlib import Path

from pyspark.sql import SparkSession

from retail_pipeline import clean, extract, transforms

os.environ.setdefault("PYSPARK_PYTHON", sys.executable)


def main() -> None:
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("retail-sales-etl")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"

    sales = clean.clean_sales(extract.read_sales_feed(spark, str(raw_dir / "sales_*.csv")))
    deduped = transforms.dedupe_sales(sales)
    print(f"cleaned rows: {sales.count()}  after dedupe: {deduped.count()}")
    deduped.orderBy("transaction_id", "ingested_at").show(truncate=False)

    products = extract.read_products(spark, str(raw_dir / "products.csv"))
    for name, build in [
        ("daily store sales", lambda: transforms.build_daily_store_sales(deduped)),
        ("category revenue", lambda: transforms.build_category_revenue(
            transforms.enrich_with_products(deduped, products))),
    ]:
        print(f"--- {name} ---")
        try:
            build().show(truncate=False)
        except NotImplementedError as todo:
            print(f"not implemented yet: {todo}")

    spark.stop()


if __name__ == "__main__":
    main()
