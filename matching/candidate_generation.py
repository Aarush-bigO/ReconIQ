"""
ReconIQ Enterprise — Candidate Generation (Blocking)
======================================================
Reduces the comparison space before probabilistic linkage.

Blocking rules ensure we only compare records that could plausibly match,
dramatically reducing O(n²) comparisons.

Blocking does NOT create financial decisions — it only filters candidates.
"""
import polars as pl
from typing import Tuple
from ingestion.schemas import FinancialEvent


def generate_candidates(
    left_records: list[dict],
    right_records: list[dict],
    date_tolerance_days: int = 3,
    amount_tolerance_minor: int = 100,
) -> list[Tuple[str, str]]:
    """
    Generate candidate pairs from two sets of canonical records.
    Returns list of (left_canonical_id, right_canonical_id) pairs.

    Blocking constraints (ANY one must pass):
      1. Same reference_core (exact)
      2. Same payment_id or order_id
      3. Same settlement_id
      4. Same currency + amount within tolerance + date within window
    """
    left_df = pl.DataFrame(left_records)
    right_df = pl.DataFrame(right_records)

    if left_df.is_empty() or right_df.is_empty():
        return []

    candidates = set()

    # ── Block 1: reference_core match ────────────────────────────────────────
    if "reference_core" in left_df.columns and "reference_core" in right_df.columns:
        left_ref = left_df.filter(pl.col("reference_core") != "").select(
            ["canonical_id", "reference_core"]
        )
        right_ref = right_df.filter(pl.col("reference_core") != "").select(
            ["canonical_id", "reference_core"]
        )
        joined = left_ref.join(right_ref, on="reference_core", suffix="_right")
        for row in joined.iter_rows(named=True):
            candidates.add((row["canonical_id"], row["canonical_id_right"]))

    # ── Block 2: payment_id / order_id match ─────────────────────────────────
    for id_field in ["payment_id", "order_id", "settlement_id"]:
        if id_field in left_df.columns and id_field in right_df.columns:
            left_ids = left_df.filter(pl.col(id_field) != "").select(["canonical_id", id_field])
            right_ids = right_df.filter(pl.col(id_field) != "").select(["canonical_id", id_field])
            joined = left_ids.join(right_ids, on=id_field, suffix="_right")
            for row in joined.iter_rows(named=True):
                candidates.add((row["canonical_id"], row["canonical_id_right"]))

    # ── Block 3: amount + date proximity (for missing references) ────────────
    if "amount_minor" in left_df.columns and "amount_minor" in right_df.columns:
        # Cross-join a subset using DuckDB for efficiency
        import duckdb
        conn = duckdb.connect()
        conn.register("left_t", left_df)
        conn.register("right_t", right_df)

        query = f"""
        SELECT l.canonical_id as l_id, r.canonical_id as r_id
        FROM left_t l
        CROSS JOIN right_t r
        WHERE l.currency = r.currency
          AND ABS(l.amount_minor - r.amount_minor) <= {amount_tolerance_minor}
          AND ABS(DATEDIFF('day', 
                TRY_CAST(l.event_date AS DATE), 
                TRY_CAST(r.event_date AS DATE))) <= {date_tolerance_days}
        LIMIT 10000
        """
        try:
            result = conn.execute(query).fetchall()
            for l_id, r_id in result:
                candidates.add((l_id, r_id))
        except Exception:
            pass  # DuckDB may fail on some schemas — block 1/2 still runs

    return list(candidates)


def records_to_splink_df(records: list[dict], unique_id_col: str = "canonical_id") -> pl.DataFrame:
    """Convert canonical records to a Polars DataFrame suitable for Splink."""
    df = pl.DataFrame(records)
    # Ensure required columns exist
    for col in ["canonical_id", "source", "reference_core", "amount_minor", "event_date", "currency"]:
        if col not in df.columns:
            df = df.with_columns(pl.lit("").alias(col) if col != "amount_minor" else pl.lit(0).alias(col))
    return df
