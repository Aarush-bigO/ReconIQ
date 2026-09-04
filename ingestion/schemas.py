"""
ReconIQ Enterprise — Canonical Data Model (Pydantic schemas)
Preserves source truth while creating controlled comparison semantics.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
import uuid


class FinancialEvent(BaseModel):
    """
    Every source record maps into this canonical schema.
    Monetary values are ALWAYS in integer minor units (paise for INR).
    Never use float for financial arithmetic.
    """
    canonical_id: str = Field(default_factory=lambda: f"txn_{uuid.uuid4().hex[:12]}")
    source: str                          # razorpay | ledger | bank
    source_record_id: str                # Original ID in source system
    source_reference: str                # Raw reference (preserved, never modified)
    reference_core: str = ""             # Normalized comparison key (derived)
    normalization_trace: Dict[str, Any] = Field(default_factory=dict)

    amount_minor: int                    # Amount in paise (integer only)
    currency: str = "INR"
    event_time: datetime
    event_type: str                      # PAYMENT | REFUND | FEE | TAX | SETTLEMENT | DISPUTE | PAYOUT
    direction: str                       # CREDIT | DEBIT
    status: str                          # captured | posted | credited | etc.

    payment_id: str = ""
    order_id: str = ""
    settlement_id: str = ""
    utr: str = ""

    fee_minor: int = 0
    tax_minor: int = 0
    adjustment_minor: int = 0

    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("amount_minor", "fee_minor", "tax_minor", "adjustment_minor", mode="before")
    @classmethod
    def coerce_to_int(cls, v: Any) -> int:
        if v is None or v == "":
            return 0
        return int(float(str(v)))

    @property
    def net_minor(self) -> int:
        return self.amount_minor - self.fee_minor - self.tax_minor - self.adjustment_minor

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class NormalizationTrace(BaseModel):
    raw: str
    normalizer: str
    normalized: str
    prefixes_stripped: List[str] = Field(default_factory=list)


class ReconciliationRunConfig(BaseModel):
    auto_match_threshold: float = 0.95
    review_threshold: float = 0.70
    date_tolerance_days: int = 3
    amount_tolerance_minor: int = 100
    currency: str = "INR"


class MatchEvidence(BaseModel):
    left_id: str
    right_id: str
    probability: float
    amount_score: float = 0.0
    date_score: float = 0.0
    reference_score: float = 0.0
    reference_core_match: bool = False
    currency_match: bool = True
    settlement_id_match: bool = False
    payment_id_match: bool = False


class MatchDecision(BaseModel):
    decision: str                        # AUTO_MATCH | MANUAL_REVIEW | UNRESOLVED
    probability: float
    evidence: MatchEvidence
    reason_code: str = ""
    threshold_applied: float = 0.95


class ExceptionRecord(BaseModel):
    exception_id: str = Field(default_factory=lambda: f"exc_{uuid.uuid4().hex[:8]}")
    transaction_id: str
    reason_code: str
    severity: str                        # HIGH | MEDIUM | LOW
    amount_minor: int
    candidate_count: int = 0
    window_days: int = 3
    status: str = "OPEN"                 # OPEN | REVIEWED | ESCALATED | RESOLVED
    evidence_json: Dict[str, Any] = Field(default_factory=dict)
    ai_explanation: Union[str, None] = None
    ai_recommended_action: Union[str, None] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Union[datetime, None] = None


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    run_id: str
    record_id: str
    action: str
    decision: str = ""
    confidence: float = 0.0
    reason_code: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)
    previous_hash: str = ""
    current_hash: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReconciliationResult(BaseModel):
    run_id: str
    started_at: datetime
    completed_at: datetime
    config: ReconciliationRunConfig
    records_processed: int
    auto_matched: int
    manual_review: int
    unresolved: int
    match_rate: float
    reconciled_value_minor: int
    exception_count: int
    processing_ms: int
    status: str = "COMPLETED"


class BenchmarkResult(BaseModel):
    dataset_size: int
    seed: int
    threshold: float
    splink_version: str
    python_version: str
    git_commit_sha: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    precision: float
    recall: float
    match_rate: float
    manual_review_rate: float
    exception_count: int
    reconciled_value_minor: int
    processing_seconds: float
