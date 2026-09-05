"""
ReconIQ Enterprise — Database Models
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, BigInteger, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship

from database.session import Base


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    threshold = Column(Float, nullable=False)
    records_processed = Column(Integer, default=0)
    auto_matched = Column(Integer, default=0)
    manual_review = Column(Integer, default=0)
    unresolved = Column(Integer, default=0)
    match_rate = Column(Float, default=0.0)
    reconciled_value_minor = Column(BigInteger, default=0)
    processing_ms = Column(Float, default=0.0)
    status = Column(String, default="RUNNING")

    def __repr__(self):
        return f"<ReconciliationRun(run_id={self.run_id!r}, status={self.status!r}, match_rate={self.match_rate})>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    canonical_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, index=True, nullable=False)
    source_record_id = Column(String, index=True, nullable=False)
    source_reference = Column(String, nullable=True)
    reference_core = Column(String, index=True, nullable=True)
    amount_minor = Column(BigInteger, nullable=False)
    currency = Column(String, default="INR")
    event_time = Column(DateTime, nullable=False)
    event_type = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    status = Column(String, nullable=False)
    payment_id = Column(String, index=True, nullable=True)
    order_id = Column(String, index=True, nullable=True)
    settlement_id = Column(String, index=True, nullable=True)
    utr = Column(String, index=True, nullable=True)
    fee_minor = Column(BigInteger, default=0)
    tax_minor = Column(BigInteger, default=0)
    adjustment_minor = Column(BigInteger, default=0)
    virtual_account_id = Column(String, index=True, nullable=True)
    customer_id = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('ix_transactions_source_event_time', 'source', 'event_time'),
    )

    def __repr__(self):
        return f"<Transaction(canonical_id={self.canonical_id!r}, source={self.source!r}, amount_minor={self.amount_minor})>"


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(String, unique=True, index=True, nullable=False)
    settlement_date = Column(DateTime, nullable=False)
    gross_minor = Column(BigInteger, default=0)
    fees_minor = Column(BigInteger, default=0)
    tax_minor = Column(BigInteger, default=0)
    adjustments_minor = Column(BigInteger, default=0)
    net_minor = Column(BigInteger, default=0)
    bank_credit_minor = Column(BigInteger, default=0)
    variance_minor = Column(BigInteger, default=0)
    status = Column(String, default="PENDING")
    utr = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Settlement(settlement_id={self.settlement_id!r}, status={self.status!r}, net_minor={self.net_minor})>"


class MatchCandidate(Base):
    __tablename__ = "match_candidates"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("reconciliation_runs.run_id"), nullable=False)
    left_transaction_id = Column(String, ForeignKey("transactions.canonical_id"), nullable=False)
    right_transaction_id = Column(String, ForeignKey("transactions.canonical_id"), nullable=False)
    probability = Column(Float, nullable=False)
    features = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("reconciliation_runs.run_id"), nullable=False)
    left_transaction_id = Column(String, ForeignKey("transactions.canonical_id"), nullable=False)
    right_transaction_id = Column(String, ForeignKey("transactions.canonical_id"), nullable=False)
    probability = Column(Float, nullable=False)
    decision = Column(String, nullable=False)  # AUTO_MATCH, MANUAL_REVIEW
    reason_code = Column(String, nullable=True)
    review_status = Column(String, default="PENDING")
    reviewer_id = Column(String, nullable=True)
    maker_id = Column(String, default="AI")
    evidence = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Match(left={self.left_transaction_id!r}, right={self.right_transaction_id!r}, decision={self.decision!r}, probability={self.probability})>"


class ExceptionRecord(Base):
    __tablename__ = "exceptions"

    id = Column(Integer, primary_key=True, index=True)
    exception_id = Column(String, unique=True, index=True, nullable=False)
    run_id = Column(String, ForeignKey("reconciliation_runs.run_id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.canonical_id"), nullable=False)
    reason_code = Column(String, nullable=False)
    severity = Column(String, default="HIGH")
    status = Column(String, default="OPEN")
    evidence_json = Column(JSON, default=dict)
    ai_explanation = Column(String, nullable=True)
    recommended_action = Column(String, nullable=True)
    deduction_category = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ExceptionRecord(exception_id={self.exception_id!r}, status={self.status!r}, reason_code={self.reason_code!r})>"


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    run_id = Column(String, index=True, nullable=False)
    record_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    decision = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    reason_code = Column(String, nullable=True)
    payload = Column(JSON, nullable=False)
    previous_hash = Column(String, nullable=False)
    current_hash = Column(String, unique=True, nullable=False)
    hmac_signature = Column(String, nullable=False)
    nonce = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditEvent(event_id={self.event_id!r}, action={self.action!r}, record_id={self.record_id!r})>"


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    payload = Column(JSON, nullable=False)
    processing_status = Column(String, default="PENDING")


class ExplanationRequest(Base):
    __tablename__ = "explanation_requests"

    id = Column(Integer, primary_key=True, index=True)
    exception_id = Column(String, ForeignKey("exceptions.exception_id"), nullable=False)
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=True)
    model = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AgenticCommunication(Base):
    __tablename__ = "agentic_communications"

    id = Column(Integer, primary_key=True, index=True)
    exception_id = Column(String, ForeignKey("exceptions.exception_id"), nullable=False)
    message_content = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_size = Column(Integer, nullable=False)
    seed = Column(Integer, nullable=False)
    threshold = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    match_rate = Column(Float, nullable=False)
    processing_seconds = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SourceConfig(Base):
    __tablename__ = "source_configs"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, unique=True, nullable=False)
    config = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# ── Django Ledger / Blnk Inspired Double-Entry Tables ─────────────────────────

class JournalEntryDB(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    reference = Column(String, index=True, nullable=True)
    status = Column(String, default="POSTED")
    posted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata_ = Column("metadata", JSON, default=dict)

    lines = relationship("JournalLineDB", back_populates="entry", cascade="all, delete-orphan")


class JournalLineDB(Base):
    __tablename__ = "journal_lines"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String, ForeignKey("journal_entries.entry_id"), nullable=False)
    account = Column(String, nullable=False)
    debit_minor = Column(BigInteger, default=0)
    credit_minor = Column(BigInteger, default=0)
    memo = Column(String, nullable=True)

    entry = relationship("JournalEntryDB", back_populates="lines")


# ── Enterprise Primitives ──────────────────────────────────────────────────────

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    entities = relationship("Entity", back_populates="organization")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String, unique=True, index=True, nullable=False)
    org_id = Column(String, ForeignKey("organizations.org_id"), nullable=False)
    name = Column(String, nullable=False)
    currency = Column(String, default="INR")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="entities")


class PeriodClose(Base):
    __tablename__ = "period_closes"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(String, unique=True, index=True, nullable=False)
    period_name = Column(String, nullable=False)  # e.g., "August 2026"
    status = Column(String, default="OPEN")       # OPEN | PENDING_APPROVAL | CLOSED
    
    # Checklist flags
    payment_activity_imported = Column(Boolean, default=False)
    settlements_imported = Column(Boolean, default=False)
    bank_statement_imported = Column(Boolean, default=False)
    reconciliation_complete = Column(Boolean, default=False)
    duplicate_controls_passed = Column(Boolean, default=False)
    variances_reviewed = Column(Boolean, default=False)
    audit_chain_verified = Column(Boolean, default=False)
    exceptions_resolved = Column(Boolean, default=False)
    
    # Summaries
    open_exceptions = Column(Integer, default=0)
    total_variance_minor = Column(BigInteger, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)


class DailyReconciliationSummary(Base):
    __tablename__ = "daily_reconciliation_summaries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True)
    total_transactions = Column(Integer, default=0)
    auto_matched = Column(Integer, default=0)
    manual_review = Column(Integer, default=0)
    unresolved = Column(Integer, default=0)
    match_rate = Column(Float, default=0.0)
    total_value_minor = Column(BigInteger, default=0)
    reconciled_value_minor = Column(BigInteger, default=0)
    open_exceptions = Column(Integer, default=0)
    resolved_exceptions = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
