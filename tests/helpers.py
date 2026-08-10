"""Shared test helpers. Comparisons are order-independent by design —
Spark makes no row-order guarantees, so tests must never assert on them."""


def sorted_rows(df):
    """Collect a DataFrame as a sorted list of plain tuples.

    Select a unique leading column (e.g. transaction_id) before calling if a
    later column can be None — Python cannot order None against strings.
    """
    return sorted(tuple(row) for row in df.collect())
