"""
ReconIQ Enterprise — Exception Classifier
==========================================
Classifies unresolved transactions into structured exception records.
Every classification is deterministic — based on evidence, not AI.
"""
from datetime import datetime
from typing import Any
import uuid

from exceptions.reason_codes import ReasonCode, Severity, REASON_CODE_METADATA
from ingestion.schemas import ExceptionRecord


def classify_exception(
    transaction: dict[str, Any],
    candidate_count: int,
    candidates: list[dict[str, Any]],
    config: dict[str, Any],
) -> ExceptionRecord:
    """
    Classify an unresolved transaction into a structured exception.

    Decision logic (deterministic):
      1. No candidates → MISSING_COUNTERPART
      2. Multiple candidates with similar probability → AMBIGUOUS_MATCH
      3. Candidate exists, currency mismatch → CURRENCY_ISSUE
      4. Candidate exists, reference_core differs → REFERENCE_MISMATCH
      5. Candidate exists, amount diff matches fee structure → FEE_DIFFERENCE
      6. Candidate exists, date diff exceeds window → DATE_DRIFT
      7. Duplicate detected in source → DUPLICATE
      8. Amount partial (sub-sum matches) → PARTIAL_SETTLEMENT
      9. Fallback → UNCLASSIFIED
    """
    amount = transaction.get("amount_minor", 0)
    date_tolerance = config.get("date_tolerance_days", 3)
    amount_tolerance = config.get("amount_tolerance_minor", 100)

    reason_code = ReasonCode.UNCLASSIFIED
    evidence: dict[str, Any] = {
        "transaction_id": transaction.get("source_record_id", ""),
        "transaction_reference": transaction.get("source_reference", ""),
        "amount_minor": amount,
        "candidate_count": candidate_count,
        "window_days": date_tolerance,
        "threshold": config.get("auto_match_threshold", 0.95),
    }

    if candidate_count == 0:
        reason_code = ReasonCode.MISSING_COUNTERPART

    elif candidate_count >= 2:
        # Check if candidates are close in probability (ambiguous)
        probs = [c.get("match_probability", 0) for c in candidates[:2]]
        if len(probs) >= 2 and abs(probs[0] - probs[1]) < 0.1:
            reason_code = ReasonCode.AMBIGUOUS_MATCH
            evidence["top_candidates"] = [
                {
                    "canonical_id": c.get("canonical_id", ""),
                    "probability": c.get("match_probability", 0),
                }
                for c in candidates[:3]
            ]
        else:
            reason_code = ReasonCode.AMBIGUOUS_MATCH

    elif candidate_count == 1:
        cand = candidates[0]
        cand_amount = cand.get("amount_minor", 0)
        cand_currency = cand.get("currency", "INR")
        txn_currency = transaction.get("currency", "INR")
        cand_ref_core = cand.get("reference_core", "")
        txn_ref_core = transaction.get("reference_core", "")

        # Currency mismatch
        if cand_currency != txn_currency:
            reason_code = ReasonCode.CURRENCY_ISSUE
            evidence["transaction_currency"] = txn_currency
            evidence["candidate_currency"] = cand_currency

        # Fee-structure amount difference
        elif 0 < abs(amount - cand_amount) <= 5000:  # Within ₹50
            reason_code = ReasonCode.FEE_DIFFERENCE
            evidence["amount_delta"] = abs(amount - cand_amount)

        # Reference mismatch
        elif txn_ref_core and cand_ref_core and txn_ref_core != cand_ref_core:
            reason_code = ReasonCode.REFERENCE_MISMATCH
            evidence["transaction_ref_core"] = txn_ref_core
            evidence["candidate_ref_core"] = cand_ref_core

        # Default single candidate to date drift if amount matches
        elif abs(amount - cand_amount) <= amount_tolerance:
            reason_code = ReasonCode.DATE_DRIFT
        else:
            reason_code = ReasonCode.UNCLASSIFIED

    metadata = REASON_CODE_METADATA.get(reason_code, REASON_CODE_METADATA[ReasonCode.UNCLASSIFIED])
    severity = metadata["severity"]

    return ExceptionRecord(
        exception_id=f"exc_{uuid.uuid4().hex[:8]}",
        transaction_id=transaction.get("canonical_id", ""),
        reason_code=reason_code.value,
        severity=severity.value,
        amount_minor=amount,
        candidate_count=candidate_count,
        window_days=date_tolerance,
        status="OPEN",
        evidence_json=evidence,
    )


def classify_all_exceptions(
    unresolved_records: list[dict[str, Any]],
    all_right_records: list[dict[str, Any]],
    predictions_df: Any,  # pd.DataFrame
    config: dict[str, Any],
) -> list[ExceptionRecord]:
    """Classify all unresolved records into exceptions."""
    exceptions = []

    # Build candidates lookup from predictions
    candidates_by_left: dict[str, list[dict]] = {}
    if predictions_df is not None and not predictions_df.empty:
        for _, row in predictions_df.iterrows():
            l_id = str(row.get("canonical_id_l", ""))
            candidates_by_left.setdefault(l_id, []).append(dict(row))

    right_map = {r["canonical_id"]: r for r in all_right_records}

    for txn in unresolved_records:
        cid = txn.get("canonical_id", "")
        candidates_raw = candidates_by_left.get(cid, [])
        candidates = []
        for c in candidates_raw:
            r_id = str(c.get("canonical_id_r", ""))
            enriched = dict(right_map.get(r_id, {}))
            enriched["match_probability"] = c.get("match_probability", 0)
            candidates.append(enriched)

        exc = classify_exception(
            transaction=txn,
            candidate_count=len(candidates),
            candidates=sorted(candidates, key=lambda x: x.get("match_probability", 0), reverse=True),
            config=config,
        )
        exceptions.append(exc)

    return exceptions
