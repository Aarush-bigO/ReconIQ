"""
ReconIQ Enterprise — Shared Test Fixtures
"""
import sys
import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.session import Base
from database.models import (
    Transaction, Settlement, ExceptionRecord, Match, AuditEvent,
    ReconciliationRun, JournalEntryDB, JournalLineDB, WebhookEvent,
    Organization, Entity, PeriodClose,
)


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite engine for tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def seeded_session(db_session):
    """A database session pre-populated with test data."""
    # Add a reconciliation run
    run = ReconciliationRun(
        run_id="TEST_RUN_001",
        started_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        completed_at=datetime(2026, 8, 1, 0, 5, tzinfo=timezone.utc),
        threshold=0.95,
        records_processed=100,
        auto_matched=90,
        manual_review=5,
        unresolved=5,
        match_rate=95.0,
        status="COMPLETED",
    )
    db_session.add(run)

    # Add transactions
    for i in range(20):
        db_session.add(Transaction(
            canonical_id=f"tx_test_{i:04d}",
            source="Razorpay" if i % 2 == 0 else "HDFC",
            source_record_id=f"src_{i:04d}",
            amount_minor=(i + 1) * 10000,
            event_time=datetime(2026, 8, 1, i % 24, tzinfo=timezone.utc),
            event_type="PAYMENT" if i % 2 == 0 else "CREDIT",
            direction="CREDIT",
            status="SETTLED",
            utr=f"UTR{90000 + i}",
        ))

    # Add matches
    for i in range(0, 20, 2):
        db_session.add(Match(
            run_id="TEST_RUN_001",
            left_transaction_id=f"tx_test_{i:04d}",
            right_transaction_id=f"tx_test_{i+1:04d}",
            probability=0.97,
            decision="AUTO_MATCH",
            reason_code="EXACT_MATCH",
        ))

    # Add settlements
    for i in range(5):
        gross = 1000000 * (i + 1)
        fees = int(gross * 0.02)
        tax = int(fees * 0.18)
        net = gross - fees - tax
        db_session.add(Settlement(
            settlement_id=f"SET_TEST_{i:03d}",
            settlement_date=datetime(2026, 8, i + 1, tzinfo=timezone.utc),
            gross_minor=gross,
            fees_minor=fees,
            tax_minor=tax,
            net_minor=net,
            bank_credit_minor=net,
            variance_minor=0,
            status="SETTLED",
            utr=f"UTR_TEST_{i:03d}",
        ))

    # Add exceptions
    for i in range(5):
        db_session.add(ExceptionRecord(
            exception_id=f"EXC_TEST_{i:03d}",
            run_id="TEST_RUN_001",
            transaction_id=f"tx_test_{i:04d}",
            reason_code=["AMOUNT_MISMATCH", "MISSING_IN_BANK", "FEE_DISCREPANCY", "DUPLICATE_PAYMENT", "STALE_TRANSACTION"][i],
            severity=["HIGH", "MEDIUM", "LOW", "CRITICAL", "MEDIUM"][i],
            status="OPEN",
            ai_explanation=f"Test explanation for exception {i}",
            recommended_action="POST_FEE_JOURNAL_ENTRY",
        ))

    # Add journal entries
    entry = JournalEntryDB(
        entry_id="je_test_001",
        description="Test payment capture",
        reference="tx_test_0000",
    )
    db_session.add(entry)
    db_session.add(JournalLineDB(
        entry_id="je_test_001",
        account="assets:cash_in_transit",
        debit_minor=100000,
        credit_minor=0,
    ))
    db_session.add(JournalLineDB(
        entry_id="je_test_001",
        account="income:revenue",
        debit_minor=0,
        credit_minor=100000,
    ))

    db_session.commit()
    return db_session
