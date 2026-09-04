"""
ReconIQ Enterprise — Splink Probabilistic Matching Pipeline
===========================================================
Uses Splink 4.x for probabilistic record linkage.

Reference: https://github.com/moj-analytical-services/splink

Pipeline:
  1. Prepare DataFrames from canonical records
  2. Define comparison features
  3. Train Splink model
  4. Get match predictions with probabilities
  5. Return raw prediction table for reconcile.py to classify

IMPORTANT: This module returns probabilities only.
The financial decision (AUTO_MATCH / MANUAL_REVIEW / UNRESOLVED) is
made deterministically in reconcile.py — never here.
"""
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any

import splink
from splink import DuckDBAPI, Linker, SettingsCreator, block_on
import splink.comparison_library as cl
import splink.comparison_level_library as cll

from ingestion.loaders import records_to_dict_list
from ingestion.schemas import FinancialEvent


def _prepare_dataframe(records: list[dict]) -> pd.DataFrame:
    """Convert records to Pandas DataFrame for Splink."""
    df = pd.DataFrame(records)

    # Ensure unique_id column
    if "canonical_id" not in df.columns:
        df["canonical_id"] = [f"rec_{i}" for i in range(len(df))]

    # Parse event_date as string for Splink date comparison
    if "event_time" in df.columns:
        df["event_date"] = pd.to_datetime(df["event_time"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Fill NaN with empty string / 0
    str_cols = ["reference_core", "source_reference", "payment_id", "order_id", "settlement_id", "utr", "currency", "source"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    int_cols = ["amount_minor", "fee_minor", "tax_minor"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


def run_splink_linkage(
    left_records: list[dict],
    right_records: list[dict],
    source_left: str = "ledger",
    source_right: str = "razorpay",
) -> pd.DataFrame:
    """
    Run Splink probabilistic record linkage between two sets of canonical records.

    Returns a DataFrame with columns:
      canonical_id_l, canonical_id_r, match_probability, match_weight
    """
    if not left_records or not right_records:
        return pd.DataFrame(columns=["canonical_id_l", "canonical_id_r", "match_probability"])

    df_left = _prepare_dataframe(left_records)
    df_right = _prepare_dataframe(right_records)

    # ── Splink Settings ──────────────────────────────────────────────────────
    settings = SettingsCreator(
        link_type="link_only",
        unique_id_column_name="canonical_id",

        comparisons=[
            # Amount agreement — most important signal
            cl.CustomComparison(
                comparison_levels=[
                    cll.CustomLevel("amount_minor_l = amount_minor_r", label_for_charts="Exact amount"),
                    cll.CustomLevel("ABS(amount_minor_l - amount_minor_r) <= 500", label_for_charts="Within ₹5"),
                    cll.CustomLevel("ABS(amount_minor_l - amount_minor_r) <= 5000", label_for_charts="Within ₹50 (fee diff)"),
                    cll.ElseLevel(),
                ],
                output_column_name="amount_minor",
                comparison_description="amount_minor",
            ).configure(
                m_probabilities=[0.95, 0.03, 0.015, 0.005],
                u_probabilities=[0.001, 0.005, 0.01, 0.984],
            ),

            # Reference core — the normalization payoff
            cl.ExactMatch("reference_core").configure(
                m_probabilities=[0.85, 0.15],
                u_probabilities=[0.001, 0.999],
            ),

            # Date proximity — allows for settlement lag
            cl.AbsoluteDateDifferenceAtThresholds(
                "event_date",
                input_is_string=True,
                thresholds=[0, 1, 2, 3],
                metrics=["day", "day", "day", "day"],
            ),

            # Currency must agree
            cl.ExactMatch("currency").configure(
                m_probabilities=[0.99, 0.01],
                u_probabilities=[0.05, 0.95],
            ),

            # Payment ID (very strong signal when available)
            cl.CustomComparison(
                comparison_levels=[
                    cll.CustomLevel("(payment_id_l != '' AND payment_id_l = payment_id_r)", label_for_charts="Payment ID match"),
                    cll.ElseLevel(),
                ],
                output_column_name="payment_id",
                comparison_description="payment_id",
            ).configure(
                m_probabilities=[0.95, 0.05],
                u_probabilities=[0.0001, 0.9999],
            ),
        ],

        blocking_rules_to_generate_predictions=[
            block_on("reference_core"),
            block_on("payment_id"),
            block_on("settlement_id"),
            block_on("order_id"),
            block_on("currency", "amount_minor"),
        ],

        max_iterations=10,
        em_convergence=0.01,
        retain_intermediate_calculation_columns=True,
    )

    # ── Run linkage ──────────────────────────────────────────────────────────
    db_api = DuckDBAPI()
    linker = Linker([df_left, df_right], settings, db_api=db_api)

    try:
        linker.training.estimate_u_using_random_sampling(max_pairs=1e5)
    except Exception:
        pass  # Can fail if dataset is very small

    try:
        linker.training.estimate_parameters_using_expectation_maximisation(
            block_on("reference_core"),
            estimate_without_term_frequencies=True,
        )
    except Exception:
        pass

    try:
        linker.training.estimate_parameters_using_expectation_maximisation(
            block_on("currency", "amount_minor"),
            estimate_without_term_frequencies=True,
        )
    except Exception:
        pass

    predictions = linker.inference.predict(threshold_match_probability=0.3)
    df_pred = predictions.as_pandas_dataframe()

    # Normalize column names
    rename_map = {}
    for col in df_pred.columns:
        if "canonical_id_l" in col or col == "canonical_id_l":
            rename_map[col] = "canonical_id_l"
        elif "canonical_id_r" in col or col == "canonical_id_r":
            rename_map[col] = "canonical_id_r"

    if rename_map:
        df_pred = df_pred.rename(columns=rename_map)

    # Ensure we have the match probability column
    if "match_probability" not in df_pred.columns and "match_weight" in df_pred.columns:
        import numpy as np
        df_pred["match_probability"] = 1 / (1 + np.exp(-df_pred["match_weight"]))

    return df_pred


def run_multi_source_linkage(
    sources: dict[str, list[dict]],
) -> pd.DataFrame:
    """
    Run pairwise Splink linkage across all source combinations.
    Returns combined predictions DataFrame.
    """
    import pandas as pd

    all_predictions = []
    source_names = list(sources.keys())

    for i, left_source in enumerate(source_names):
        for right_source in source_names[i + 1:]:
            left_records = sources[left_source]
            right_records = sources[right_source]

            if not left_records or not right_records:
                continue

            try:
                preds = run_splink_linkage(
                    left_records,
                    right_records,
                    source_left=left_source,
                    source_right=right_source,
                )
                preds["source_pair"] = f"{left_source}↔{right_source}"
                all_predictions.append(preds)
            except Exception as e:
                print(f"[Splink] Linkage {left_source}↔{right_source} failed: {e}")

    if not all_predictions:
        return pd.DataFrame(columns=["canonical_id_l", "canonical_id_r", "match_probability"])

    return pd.concat(all_predictions, ignore_index=True)
