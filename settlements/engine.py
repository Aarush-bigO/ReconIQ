"""
ReconIQ Enterprise — Settlement Engine
========================================
Inspired by Blnk's open-source ledger architecture.

Every Razorpay settlement is modeled as a double-entry batch:
  - Gross payment captured (debit: Razorpay Receivable)
  - Gateway fee deducted (credit: Fee Expense)
  - GST on fee deducted (credit: Tax Payable)
  - Net amount settled to bank (credit: Bank Account)

All amounts are in integer minor units (paise). Never float.

Settlement Batch Lifecycle:
  PENDING → MATCHED → RECONCILED → CLOSED
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    MATCHED = "MATCHED"
    RECONCILED = "RECONCILED"
    CLOSED = "CLOSED"
    DISPUTED = "DISPUTED"


class EntryType(str, Enum):
    GROSS_PAYMENT = "GROSS_PAYMENT"
    GATEWAY_FEE = "GATEWAY_FEE"
    GST_ON_FEE = "GST_ON_FEE"
    NET_SETTLEMENT = "NET_SETTLEMENT"
    REFUND = "REFUND"
    CHARGEBACK = "CHARGEBACK"
    ADJUSTMENT = "ADJUSTMENT"


@dataclass(frozen=True)
class SettlementEntry:
    """
    A single line item in a settlement batch.
    Inspired by Blnk's transaction model — every entry has a
    source account and destination account (double-entry).

    All amounts are in integer minor units (paise for INR).
    """
    entry_id: str
    entry_type: EntryType
    amount_minor: int  # Always positive. Direction is determined by entry_type.
    currency: str = "INR"
    source_account: str = ""  # e.g., "razorpay_receivable"
    destination_account: str = ""  # e.g., "bank_account"
    reference: str = ""  # UTR, payment_id, etc.
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.amount_minor < 0:
            raise ValueError(
                f"SettlementEntry amount_minor must be >= 0, got {self.amount_minor}. "
                "Use entry_type to indicate direction, not sign."
            )


@dataclass
class SettlementBatch:
    """
    A settlement batch groups all entries for a single Razorpay settlement cycle.

    Invariant: gross_amount == fees + taxes + net_amount + adjustments
    This invariant is verified by validate().
    """
    batch_id: str
    settlement_id: str
    utr: str
    settlement_date: str  # ISO date
    currency: str = "INR"
    status: SettlementStatus = SettlementStatus.PENDING
    entries: list[SettlementEntry] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def gross_amount(self) -> int:
        """Total gross payment amount (sum of GROSS_PAYMENT entries)."""
        return sum(
            e.amount_minor for e in self.entries
            if e.entry_type == EntryType.GROSS_PAYMENT
        )

    @property
    def total_fees(self) -> int:
        """Total gateway fees."""
        return sum(
            e.amount_minor for e in self.entries
            if e.entry_type == EntryType.GATEWAY_FEE
        )

    @property
    def total_taxes(self) -> int:
        """Total taxes (GST on fees)."""
        return sum(
            e.amount_minor for e in self.entries
            if e.entry_type == EntryType.GST_ON_FEE
        )

    @property
    def total_refunds(self) -> int:
        """Total refunds in this batch."""
        return sum(
            e.amount_minor for e in self.entries
            if e.entry_type == EntryType.REFUND
        )

    @property
    def total_chargebacks(self) -> int:
        """Total chargebacks in this batch."""
        return sum(
            e.amount_minor for e in self.entries
            if e.entry_type == EntryType.CHARGEBACK
        )

    @property
    def total_adjustments(self) -> int:
        """Total adjustments."""
        return sum(
            e.amount_minor for e in self.entries
            if e.entry_type == EntryType.ADJUSTMENT
        )

    @property
    def net_amount(self) -> int:
        """Net settlement amount (sum of NET_SETTLEMENT entries)."""
        return sum(
            e.amount_minor for e in self.entries
            if e.entry_type == EntryType.NET_SETTLEMENT
        )

    @property
    def computed_net(self) -> int:
        """
        Computed net = gross - fees - taxes - refunds - chargebacks ± adjustments.
        This should match net_amount if the batch is balanced.
        """
        return (
            self.gross_amount
            - self.total_fees
            - self.total_taxes
            - self.total_refunds
            - self.total_chargebacks
            - self.total_adjustments
        )

    def validate(self) -> tuple[bool, str]:
        """
        Verify the settlement batch balance invariant.
        Returns (is_valid, message).
        """
        if not self.entries:
            return False, "Settlement batch has no entries"

        computed = self.computed_net
        declared = self.net_amount

        if computed != declared:
            delta = computed - declared
            return False, (
                f"Settlement imbalance: computed_net={computed} != declared_net={declared}, "
                f"delta={delta} minor units ({delta / 100:.2f} {self.currency})"
            )

        return True, "Settlement batch is balanced"

    def to_breakdown(self) -> dict[str, Any]:
        """Export a human-readable settlement breakdown."""
        return {
            "batch_id": self.batch_id,
            "settlement_id": self.settlement_id,
            "utr": self.utr,
            "settlement_date": self.settlement_date,
            "currency": self.currency,
            "status": self.status.value,
            "gross_amount_minor": self.gross_amount,
            "gross_amount": self.gross_amount / 100,
            "total_fees_minor": self.total_fees,
            "total_fees": self.total_fees / 100,
            "total_taxes_minor": self.total_taxes,
            "total_taxes": self.total_taxes / 100,
            "total_refunds_minor": self.total_refunds,
            "total_refunds": self.total_refunds / 100,
            "total_chargebacks_minor": self.total_chargebacks,
            "total_chargebacks": self.total_chargebacks / 100,
            "net_amount_minor": self.net_amount,
            "net_amount": self.net_amount / 100,
            "computed_net_minor": self.computed_net,
            "computed_net": self.computed_net / 100,
            "is_balanced": self.computed_net == self.net_amount,
            "entry_count": len(self.entries),
        }


def compute_settlement_breakdown(
    payments: list[dict[str, Any]],
    fee_rate_bps: int = 200,  # 2.00% default Razorpay rate
    gst_rate_bps: int = 1800,  # 18% GST on fees
) -> SettlementBatch:
    """
    Build a SettlementBatch from a list of payment records.

    Args:
        payments: List of canonical payment dicts with amount_minor, payment_id, etc.
        fee_rate_bps: Gateway fee rate in basis points (200 = 2.00%)
        gst_rate_bps: GST rate on fees in basis points (1800 = 18%)

    Returns:
        A fully populated SettlementBatch with all entries.
    """
    batch_id = f"stl_{uuid.uuid4().hex[:8]}"
    settlement_id = payments[0].get("settlement_id", f"setl_{uuid.uuid4().hex[:6]}") if payments else ""
    utr = payments[0].get("utr", "") if payments else ""
    settlement_date = payments[0].get("event_date", datetime.utcnow().strftime("%Y-%m-%d")) if payments else ""

    entries: list[SettlementEntry] = []
    total_gross = 0
    total_fee = 0
    total_tax = 0

    for payment in payments:
        amount = int(payment.get("amount_minor", 0))
        if amount <= 0:
            continue

        pid = payment.get("payment_id", payment.get("canonical_id", ""))

        # Gross payment entry
        entries.append(SettlementEntry(
            entry_id=f"ent_{uuid.uuid4().hex[:8]}",
            entry_type=EntryType.GROSS_PAYMENT,
            amount_minor=amount,
            currency=payment.get("currency", "INR"),
            source_account="customer",
            destination_account="razorpay_receivable",
            reference=pid,
            description=f"Payment capture: {pid}",
        ))
        total_gross += amount

        # Fee calculation (integer arithmetic only — no floats)
        fee = (amount * fee_rate_bps) // 10000
        entries.append(SettlementEntry(
            entry_id=f"ent_{uuid.uuid4().hex[:8]}",
            entry_type=EntryType.GATEWAY_FEE,
            amount_minor=fee,
            currency=payment.get("currency", "INR"),
            source_account="razorpay_receivable",
            destination_account="fee_expense",
            reference=pid,
            description=f"Gateway fee @ {fee_rate_bps}bps: {pid}",
        ))
        total_fee += fee

        # GST on fee (integer arithmetic only)
        tax = (fee * gst_rate_bps) // 10000
        entries.append(SettlementEntry(
            entry_id=f"ent_{uuid.uuid4().hex[:8]}",
            entry_type=EntryType.GST_ON_FEE,
            amount_minor=tax,
            currency=payment.get("currency", "INR"),
            source_account="razorpay_receivable",
            destination_account="tax_payable",
            reference=pid,
            description=f"GST on fee @ {gst_rate_bps}bps: {pid}",
        ))
        total_tax += tax

    # Net settlement entry
    net = total_gross - total_fee - total_tax
    entries.append(SettlementEntry(
        entry_id=f"ent_{uuid.uuid4().hex[:8]}",
        entry_type=EntryType.NET_SETTLEMENT,
        amount_minor=net,
        currency=payments[0].get("currency", "INR") if payments else "INR",
        source_account="razorpay_receivable",
        destination_account="bank_account",
        reference=utr,
        description=f"Net settlement to bank: {utr}",
    ))

    return SettlementBatch(
        batch_id=batch_id,
        settlement_id=settlement_id,
        utr=utr,
        settlement_date=settlement_date,
        entries=entries,
    )
