"""Explicit schemas for every table the pipeline touches. Nothing is inferred."""
from pyspark.sql.types import (
    DateType,
    DecimalType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

RAW_SALES_SCHEMA = StructType([
    StructField("transaction_id", StringType()),
    StructField("store_id", StringType()),
    StructField("product_id", StringType()),
    StructField("quantity", StringType()),
    StructField("unit_price", StringType()),
    StructField("sale_ts", StringType()),
    StructField("ingested_at", StringType()),
])

CLEAN_SALES_SCHEMA = StructType([
    StructField("transaction_id", StringType()),
    StructField("store_id", StringType()),
    StructField("product_id", StringType()),
    StructField("quantity", IntegerType()),
    StructField("unit_price", DecimalType(10, 2)),
    StructField("sale_ts", TimestampType()),
    StructField("ingested_at", TimestampType()),
    StructField("business_date", DateType()),
])

PRODUCTS_SCHEMA = StructType([
    StructField("product_id", StringType()),
    StructField("product_name", StringType()),
    StructField("category", StringType()),
    StructField("unit_cost", DecimalType(10, 2)),
])

STORES_SCHEMA = StructType([
    StructField("store_id", StringType()),
    StructField("store_name", StringType()),
    StructField("region", StringType()),
])
