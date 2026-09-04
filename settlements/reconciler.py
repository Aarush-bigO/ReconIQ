"""
ReconIQ Enterprise — Settlement Reconciler
============================================
Three-way settlement matching inspired by Blnk + Financial Transaction Reconciliation.

Matches across three sources:
  1. Razorpay payments (gross amounts)
  2. Ledger entries (expected settlements)
  3. Bank statement credits (actual deposits)

Settlement reconciliation flow:
  1. Group payments by settlement_id/UTR
  2. Build SettlementBatch with fee/tax breakdown
  3. Match computed net against bank credit amount
  4. Classify: MATCHED / FEE_DISCREPANCY / PARTIAL / MISSING_BANK_CREDIT
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from enum import Enum

from settlements.engine import (
    SettlementBatch,
    SettlementStatus,
    compute_settlement_breakdown,
)


class SettlementMatchResult(str, Enum):
    EXACT_MATCH = "EXACT_MATCH"
    FEE_DISCREPANCY = "FEE_DISCREPANCY"
    PARTIAL_SETTLEMENT = "PARTIAL_SETTLEMENT"
    MISSING_BANK_CREDIT = "MISSING_BANK_CREDIT"
    OVERPAYMENT = "OVERPAYMENT"
    UNMATCHED = "UNMATCHED"


@dataclass
class SettlementReconciliationResult:
    """Result of reconciling a settlement batch against bank data."""
    batch: SettlementBatch
    match_result: SettlementMatchResult
    bank_credit_amount_minor: int = 0
    variance_minor: int = 0
    variance_pct: float = 0.0
    explanation: str = ""
    bank_reference: str = ""
    reconciled_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        breakdown = self.batch.to_breakdown()
        return {
            **breakdown,
            "match_result": self.match_result.value,
            "bank_credit_amount_minor": self.bank_credit_amount_minor,
            "bank_credit_amount": self.bank_credit_amount_minor / 100,
            "variance_minor": self.variance_minor,
            "variance": self.variance_minor / 100,
            "variance_pct": round(self.variance_pct, 4),
            "explanation": self.explanation,
            "bank_reference": self.bank_reference,
            "reconciled_at": self.reconciled_at,
        }


def reconcile_settlement(
    batch: SettlementBatch,
    bank_credits: list[dict[str, Any]],
    tolerance_minor: int = 100,  # ₹1.00 tolerance for rounding
) -> SettlementReconciliationResult:
    """
    Reconcile a SettlementBatch against bank credit records.

    Args:
        batch: The settlement batch to reconcile
        bank_credits: List of bank credit records with amount_minor and utr fields
        tolerance_minor: Acceptable variance in minor units

    Returns:
        SettlementReconciliationResult with match classification
    """
    expected_net = batch.net_amount

    # Find matching bank credit by UTR
    matching_credit = None
    for credit in bank_credits:
        credit_utr = str(credit.get("utr", "")).strip()
        if credit_utr and credit_utr == batch.utr:
            matching_credit = credit
            break

    # If no UTR match, try matching by settlement_id
    if matching_credit is None:
        for credit in bank_credits:
            credit_settlement = str(credit.get("settlement_id", "")).strip()
            if credit_settlement and credit_settlement == batch.settlement_id:
                matching_credit = credit
                break

    # No bank credit found
    if matching_credit is None:
        batch.status = SettlementStatus.PENDING
        return SettlementReconciliationResult(
            batch=batch,
            match_result=SettlementMatchResult.MISSING_BANK_CREDIT,
            explanation=(
                f"No bank credit found for settlement {batch.settlement_id} "
                f"(UTR: {batch.utr}). Expected net: ₹{expected_net / 100:.2f}"
            ),
        )

    bank_amount = int(matching_credit.get("amount_minor", 0))
    variance = expected_net - bank_amount
    abs_variance = abs(variance)

    # Calculate variance percentage (avoid division by zero)
    variance_pct = (abs_variance / expected_net * 100) if expected_net > 0 else 0.0

    bank_ref = matching_credit.get("bank_reference", matching_credit.get("reference_core", ""))

    # Exact match (within tolerance)
    if abs_variance <= tolerance_minor:
        batch.status = SettlementStatus.RECONCILED
        return SettlementReconciliationResult(
            batch=batch,
            match_result=SettlementMatchResult.EXACT_MATCH,
            bank_credit_amount_minor=bank_amount,
            variance_minor=variance,
            variance_pct=variance_pct,
            bank_reference=bank_ref,
            explanation=(
                f"Settlement matched. Expected ₹{expected_net / 100:.2f}, "
                f"received ₹{bank_amount / 100:.2f}. "
                f"Variance ₹{variance / 100:.2f} within tolerance."
            ),
        )

    # Fee discrepancy (small variance, likely fee rounding)
    if abs_variance <= 5000:  # ₹50 — typical fee rounding range
        batch.status = SettlementStatus.MATCHED
        return SettlementReconciliationResult(
            batch=batch,
            match_result=SettlementMatchResult.FEE_DISCREPANCY,
            bank_credit_amount_minor=bank_amount,
            variance_minor=variance,
            variance_pct=variance_pct,
            bank_reference=bank_ref,
            explanation=(
                f"Fee discrepancy detected. Expected ₹{expected_net / 100:.2f}, "
                f"received ₹{bank_amount / 100:.2f}. "
                f"Variance ₹{variance / 100:.2f} may be due to fee/tax rounding."
            ),
        )

    # Partial settlement (bank received less than expected)
    if bank_amount < expected_net and bank_amount > 0:
        batch.status = SettlementStatus.DISPUTED
        return SettlementReconciliationResult(
            batch=batch,
            match_result=SettlementMatchResult.PARTIAL_SETTLEMENT,
            bank_credit_amount_minor=bank_amount,
            variance_minor=variance,
            variance_pct=variance_pct,
            bank_reference=bank_ref,
            explanation=(
                f"Partial settlement. Expected ₹{expected_net / 100:.2f}, "
                f"received ₹{bank_amount / 100:.2f}. "
                f"Shortfall ₹{variance / 100:.2f} ({variance_pct:.2f}%). "
                f"May indicate split settlement across multiple batches."
            ),
        )

    # Overpayment
    if bank_amount > expected_net:
        batch.status = SettlementStatus.DISPUTED
        return SettlementReconciliationResult(
            batch=batch,
            match_result=SettlementMatchResult.OVERPAYMENT,
            bank_credit_amount_minor=bank_amount,
            variance_minor=variance,
            variance_pct=variance_pct,
            bank_reference=bank_ref,
            explanation=(
                f"Overpayment detected. Expected ₹{expected_net / 100:.2f}, "
                f"received ₹{bank_amount / 100:.2f}. "
                f"Excess ₹{abs_variance / 100:.2f}. Investigate source."
            ),
        )

    # Fallback
    return SettlementReconciliationResult(
        batch=batch,
        match_result=SettlementMatchResult.UNMATCHED,
        bank_credit_amount_minor=bank_amount,
        variance_minor=variance,
        variance_pct=variance_pct,
        bank_reference=bank_ref,
        explanation="Unable to classify settlement match result.",
    )


def reconcile_all_settlements(
    payments_by_settlement: dict[str, list[dict[str, Any]]],
    bank_credits: list[dict[str, Any]],
    fee_rate_bps: int = 200,
    gst_rate_bps: int = 1800,
) -> list[SettlementReconciliationResult]:
    """
    Reconcile all settlement batches against bank credits.

    Args:
        payments_by_settlement: Payments grouped by settlement_id
        bank_credits: All bank credit records
        fee_rate_bps: Gateway fee rate in basis points
        gst_rate_bps: GST rate on fees in basis points

    Returns:
        List of reconciliation results, one per settlement batch
    """
    results = []

    for settlement_id, payments in payments_by_settlement.items():
        if not payments:
            continue

        batch = compute_settlement_breakdown(
            payments,
            fee_rate_bps=fee_rate_bps,
            gst_rate_bps=gst_rate_bps,
        )

        result = reconcile_settlement(batch, bank_credits)
        results.append(result)

    return results
