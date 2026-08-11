# Domain — Retail Sales ETL

## The pipeline

Every night each store's point-of-sale system exports its transactions as a CSV feed
file, and an ingestion job drops the files into `data/raw/`. This pipeline turns those
files into clean, analysis-ready tables. Three stages:

1. **Extract** (`extract.py`) — read the raw files with explicit schemas. Nothing is
   inferred; a malformed value becomes a null, not a guess.
2. **Clean** (`clean.py`) — normalize raw rows into typed, trustworthy records (see
   the data dictionary below).
3. **Transform** (`transforms.py`) — the business tables: de-duplicated sales, daily
   summaries, product enrichment. The work items live here.

`run_pipeline.py` wires the stages together over `data/raw/` and prints the results —
run it any time with `python -m retail_pipeline.run_pipeline`. It is a viewing
harness, not part of the graded work.

## Feed behavior you can rely on

- A store-day's file may be **re-sent** after an upstream correction. A resend repeats
  the original file's transactions — usually identical, but a row may carry corrected
  values. Re-sent rows always have a later `ingested_at` than the originals.
- `transaction_id` uniquely identifies a sale. A repeated `transaction_id` is the same
  sale delivered again, never two different sales.
- Timestamps are UTC. `business_date` is the calendar date of `sale_ts`.

## Data dictionary

Raw sales feed (all columns arrive as text):

| Column | Meaning |
| --- | --- |
| `transaction_id` | Unique sale id (`T-…`). Rows without one are unusable. |
| `store_id` | Store code (`S-…`). |
| `product_id` | Product code (`P-…`). May not exist in `products.csv`. |
| `quantity` | Units sold. |
| `unit_price` | Price per unit — may arrive as `"$1,234.56"`, `"12.5"`, or padded with spaces. |
| `sale_ts` | When the sale happened. |
| `ingested_at` | When this row's file landed in `data/raw/`. |

Cleaned sales adds `business_date` and guarantees types: `quantity` int, `unit_price`
DECIMAL(10,2), timestamps as timestamps.

`products.csv`: `product_id`, `product_name`, `category`, `unit_cost`.
`stores.csv`: `store_id`, `store_name`, `region`.

## Ground rules

- **Money is DECIMAL(10,2), never float.** Floating-point revenue is a bug even when a
  test happens to pass.
- **Row order is never part of a table's contract.** Consumers sort when they need
  order; transforms must not depend on it.
- All data uses fixed March 2026 dates — nothing in this codebase reads the clock.
