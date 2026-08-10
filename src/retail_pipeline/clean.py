"""Normalize raw POS rows into typed, trustworthy records."""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def clean_sales(raw: DataFrame) -> DataFrame:
    """One raw sales extract in, cleaned rows out.

    - trims whitespace on identifiers
    - parses currency strings like "$1,234.56" into DECIMAL(10,2)
    - casts quantity to int and both timestamps to timestamp
    - derives business_date from sale_ts
    - drops rows with no transaction_id (unusable)
    """
    return (
        raw
        .withColumn("transaction_id", F.trim(F.col("transaction_id")))
        .withColumn("store_id", F.trim(F.col("store_id")))
        .withColumn("product_id", F.trim(F.col("product_id")))
        .filter(F.col("transaction_id").isNotNull() & (F.col("transaction_id") != ""))
        .withColumn("quantity", F.col("quantity").cast("int"))
        .withColumn(
            "unit_price",
            F.regexp_replace(F.trim(F.col("unit_price")), "[$,]", "").cast("decimal(10,2)"),
        )
        .withColumn("sale_ts", F.to_timestamp(F.col("sale_ts")))
        .withColumn("ingested_at", F.to_timestamp(F.col("ingested_at")))
        .withColumn("business_date", F.to_date(F.col("sale_ts")))
    )
