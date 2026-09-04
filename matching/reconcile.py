"""
ReconIQ Enterprise — Reconciliation Decision Engine
====================================================
Converts Splink probabilities into deterministic financial decisions.

Three-stage policy:
  probability >= AUTO_MATCH_THRESHOLD  → AUTO_MATCH
  REVIEW_THRESHOLD <= prob < auto      → MANUAL_REVIEW
  probability < REVIEW_THRESHOLD       → UNRESOLVED

No black-box decisions. Every match exposes full evidence.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import pandas as pd

from ingestion.schemas import FinancialEvent, ReconciliationRunConfig


# ── Decision constants ────────────────────────────────────────────────────────

class Decision:
    AUTO_MATCH = "AUTO_MATCH"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    UNRESOLVED = "UNRESOLVED"


# ── Match result with full evidence ──────────────────────────────────────────

@dataclass
class MatchResult:
    left_id: str
    right_id: str
    decision: str
    probability: float
    threshold_applied: float
    evidence: dict[str, Any] = field(default_factory=dict)
    reason_code: str = ""


@dataclass
class ReconciliationOutput:
    run_id: str
    config: ReconciliationRunConfig
    matches: list[MatchResult]
    manual_review: list[MatchResult]
    unresolved_ids: list[str]
    all_ids: list[str]
    started_at: datetime
    completed_at: datetime

    @property
    def auto_matched(self) -> int:
        return len(self.matches)

    @property
    def manual_review_count(self) -> int:
        return len(self.manual_review)

    @property
    def unresolved_count(self) -> int:
        return len(self.unresolved_ids)

    @property
    def records_processed(self) -> int:
        return len(self.all_ids)

    @property
    def match_rate(self) -> float:
        if not self.all_ids:
            return 0.0
        return round(self.auto_matched / len(self.all_ids), 4)

    @property
    def processing_ms(self) -> int:
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() * 1000)


def _build_evidence(row: pd.Series, left_records: dict, right_records: dict) -> dict[str, Any]:
    """Extract match evidence from Splink prediction row."""
    evidence: dict[str, Any] = {}

    # Probability
    evidence["match_probability"] = float(row.get("match_probability", 0.0))

    # Extract Splink comparison scores where available
    for col in row.index:
        if col.startswith("bf_") or col.startswith("gamma_") or "level" in col.lower():
            evidence[col] = row[col]

    # Enrich with canonical record data
    l_id = str(row.get("canonical_id_l", ""))
    r_id = str(row.get("canonical_id_r", ""))

    left_rec = left_records.get(l_id, {})
    right_rec = right_records.get(r_id, {})

    evidence["left_amount"] = left_rec.get("amount_minor", 0)
    evidence["right_amount"] = right_rec.get("amount_minor", 0)
    evidence["amount_delta"] = abs(evidence["left_amount"] - evidence["right_amount"])

    evidence["left_reference_core"] = left_rec.get("reference_core", "")
    evidence["right_reference_core"] = right_rec.get("reference_core", "")
    evidence["reference_core_match"] = evidence["left_reference_core"] == evidence["right_reference_core"]

    evidence["left_date"] = left_rec.get("event_date", "")
    evidence["right_date"] = right_rec.get("event_date", "")

    evidence["left_source"] = left_rec.get("source", "")
    evidence["right_source"] = right_rec.get("source", "")

    evidence["left_payment_id"] = left_rec.get("payment_id", "")
    evidence["right_payment_id"] = right_rec.get("payment_id", "")
    evidence["payment_id_match"] = (
        bool(evidence["left_payment_id"])
        and evidence["left_payment_id"] == evidence["right_payment_id"]
    )

    return evidence


def apply_reconciliation_policy(
    predictions: pd.DataFrame,
    left_records: list[dict],
    right_records: list[dict],
    config: ReconciliationRunConfig,
) -> tuple[list[MatchResult], list[MatchResult]]:
    """
    Apply the three-stage reconciliation policy to Splink predictions.

    Returns (auto_matches, manual_reviews)
    """
    # Build lookup maps
    left_map = {r["canonical_id"]: r for r in left_records}
    right_map = {r["canonical_id"]: r for r in right_records}

    auto_matches = []
    manual_reviews = []

    # Deduplicate: one left record should match at most one right record
    # (take the highest probability candidate)
    if not predictions.empty and "match_probability" in predictions.columns:
        predictions = predictions.sort_values("match_probability", ascending=False)

        used_left = set()
        used_right = set()

        for _, row in predictions.iterrows():
            l_id = str(row.get("canonical_id_l", ""))
            r_id = str(row.get("canonical_id_r", ""))
            prob = float(row.get("match_probability", 0.0))

            if l_id in used_left or r_id in used_right:
                continue

            evidence = _build_evidence(row, left_map, right_map)

            # ── Hard contradiction checks ─────────────────────────────────
            # Don't auto-match if currency differs
            l_currency = left_map.get(l_id, {}).get("currency", "INR")
            r_currency = right_map.get(r_id, {}).get("currency", "INR")
            has_contradiction = l_currency != r_currency

            # ── Apply policy ──────────────────────────────────────────────
            if prob >= config.auto_match_threshold and not has_contradiction:
                decision = Decision.AUTO_MATCH
                used_left.add(l_id)
                used_right.add(r_id)
                result = MatchResult(
                    left_id=l_id,
                    right_id=r_id,
                    decision=decision,
                    probability=prob,
                    threshold_applied=config.auto_match_threshold,
                    evidence=evidence,
                    reason_code="AMOUNT_DATE_REFERENCE",
                )
                auto_matches.append(result)

            elif prob >= config.review_threshold:
                decision = Decision.MANUAL_REVIEW
                used_left.add(l_id)
                used_right.add(r_id)
                result = MatchResult(
                    left_id=l_id,
                    right_id=r_id,
                    decision=decision,
                    probability=prob,
                    threshold_applied=config.review_threshold,
                    evidence=evidence,
                    reason_code="BELOW_AUTO_THRESHOLD",
                )
                manual_reviews.append(result)

    return auto_matches, manual_reviews


def reconcile(
    sources: dict[str, list[dict]],
    predictions: pd.DataFrame,
    config: ReconciliationRunConfig | None = None,
) -> ReconciliationOutput:
    """
    Main reconciliation entry point.
    
    Takes multi-source canonical records and Splink predictions,
    applies policy, and returns full ReconciliationOutput.
    """
    if config is None:
        config = ReconciliationRunConfig()

    run_id = f"recon_{uuid.uuid4().hex[:8]}"
    started_at = datetime.utcnow()

    # Flatten all records for ID tracking
    all_ids = []
    all_records_map = {}
    for source_name, records in sources.items():
        for r in records:
            cid = r["canonical_id"]
            all_ids.append(cid)
            all_records_map[cid] = r

    # For linkage we use ledger as the "left" source (the anchor)
    left_records = sources.get("ledger", [])
    # Combine razorpay + bank as right sources
    right_records = sources.get("razorpay", []) + sources.get("bank", [])

    auto_matches, manual_reviews = apply_reconciliation_policy(
        predictions, left_records, right_records, config
    )

    # Determine unresolved
    matched_left_ids = {m.left_id for m in auto_matches + manual_reviews}
    unresolved_ids = [
        r["canonical_id"]
        for r in left_records
        if r["canonical_id"] not in matched_left_ids
    ]

    completed_at = datetime.utcnow()

    return ReconciliationOutput(
        run_id=run_id,
        config=config,
        matches=auto_matches,
        manual_review=manual_reviews,
        unresolved_ids=unresolved_ids,
        all_ids=all_ids,
        started_at=started_at,
        completed_at=completed_at,
    )
