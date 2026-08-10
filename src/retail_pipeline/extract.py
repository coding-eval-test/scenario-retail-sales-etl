"""Read the raw feed files. Schemas are enforced, never inferred."""
from pyspark.sql import DataFrame, SparkSession

from retail_pipeline.schemas import PRODUCTS_SCHEMA, RAW_SALES_SCHEMA, STORES_SCHEMA


def read_sales_feed(spark: SparkSession, path: str) -> DataFrame:
    """All raw sales files matching *path* (a file or a glob), as delivered."""
    return spark.read.csv(path, header=True, schema=RAW_SALES_SCHEMA)


def read_products(spark: SparkSession, path: str) -> DataFrame:
    return spark.read.csv(path, header=True, schema=PRODUCTS_SCHEMA)


def read_stores(spark: SparkSession, path: str) -> DataFrame:
    return spark.read.csv(path, header=True, schema=STORES_SCHEMA)
