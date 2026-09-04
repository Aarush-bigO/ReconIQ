"""
ReconIQ Enterprise — Evaluation Metrics
========================================
Compares reconciliation predictions against ground truth.

Architecture (prevents benchmark leakage):

  RAW DATA ──► MATCHER ──► PREDICTIONS
  GROUND TRUTH ──────────► EVALUATOR
  PREDICTIONS + GROUND TRUTH ──► PRECISION / RECALL
"""
import json
from pathlib import Path
from typing import Any

from matching.reconcile import ReconciliationOutput


GROUND_TRUTH_PATH = Path(__file__).parent.parent / "data" / "ground_truth" / "matches.json"


def load_ground_truth(path: Path | None = None) -> list[dict]:
    """Load ground truth matches. Never pass this to the matcher."""
    p = path or GROUND_TRUTH_PATH
    with open(p) as f:
        data = json.load(f)
    return data.get("matches", [])


def build_true_positive_set(ground_truth: list[dict], source_records: dict[str, list[dict]]) -> set[tuple[str, str]]:
    """
    Build set of (left_canonical_id, right_canonical_id) pairs that are true matches.
    Looks up canonical IDs from source_record_id via ground_truth ledger_id → true_matches.
    """
    # Build a lookup: source_record_id → canonical_id
    record_id_to_canonical: dict[str, str] = {}
    for records in source_records.values():
        for r in records:
            record_id_to_canonical[r.get("source_record_id", "")] = r["canonical_id"]

    true_pairs = set()
    for gt in ground_truth:
        led_id = gt["ledger_id"]  # e.g. LED-1001
        true_matches = gt.get("true_matches", [])

        # Find canonical ID for the ledger record
        left_canonical = record_id_to_canonical.get(led_id)
        if not left_canonical:
            continue

        for match_id in true_matches:
            right_canonical = record_id_to_canonical.get(match_id)
            if right_canonical:
                true_pairs.add((left_canonical, right_canonical))

    return true_pairs


def compute_metrics(
    output: ReconciliationOutput,
    ground_truth: list[dict],
    source_records: dict[str, list[dict]],
) -> dict[str, Any]:
    """
    Compute precision, recall, F1, match_rate against ground truth.

    Returns:
    {
      "precision": float,
      "recall": float,
      "f1": float,
      "match_rate": float,
      "manual_review_rate": float,
      "true_positives": int,
      "false_positives": int,
      "false_negatives": int,
    }
    """
    true_pairs = build_true_positive_set(ground_truth, source_records)

    # Predicted AUTO_MATCH pairs
    predicted_pairs = {(m.left_id, m.right_id) for m in output.matches}

    tp = len(predicted_pairs & true_pairs)
    fp = len(predicted_pairs - true_pairs)
    fn = len(true_pairs - predicted_pairs)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    total = output.records_processed
    match_rate = output.auto_matched / max(1, len(source_records.get("ledger", [])))
    manual_rate = output.manual_review_count / max(1, len(source_records.get("ledger", [])))

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "match_rate": round(match_rate, 4),
        "manual_review_rate": round(manual_rate, 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "auto_matched": output.auto_matched,
        "manual_review": output.manual_review_count,
        "unresolved": output.unresolved_count,
        "records_processed": total,
        "processing_ms": output.processing_ms,
    }
