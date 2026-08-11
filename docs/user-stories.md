# User stories

Story tests are already written (`tests/`). A story earns its points when its whole
category passes. The tests define the output contract exactly — column names, types,
values. How you build the DataFrames is your call: the DataFrame API and `spark.sql`
over temp views are both fine.

## S1 — Daily store sales summary (25 points)

The merchandising team wants one row per store per business date.

Implement `build_daily_store_sales` in `src/retail_pipeline/transforms.py`.

**Acceptance criteria**

- Input: cleaned, de-duplicated sales.
- Output columns: `store_id`, `business_date`, `total_revenue`, `units_sold`,
  `txn_count`.
- `total_revenue` sums `quantity × unit_price` for the group; `units_sold` sums
  `quantity`; `txn_count` counts transactions.
- Money stays decimal end to end.

## S2 — Product enrichment (25 points)

Category managers need sales broken down by product category — including sales of
products that are missing from the product master.

Implement `enrich_with_products` and `build_category_revenue` in
`src/retail_pipeline/transforms.py`.

**Acceptance criteria**

- `enrich_with_products`: every sales row gains `product_name` and `category`,
  matched on `product_id`.
- A sale whose `product_id` has no product row is **kept**, with `category` set to
  the literal `UNKNOWN` and `product_name` null. Enrichment never drops or
  duplicates a sales row.
- `build_category_revenue`: one row per `category` with `total_revenue`
  (sum of `quantity × unit_price`).
