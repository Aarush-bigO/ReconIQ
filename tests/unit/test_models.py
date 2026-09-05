"""
Unit tests for database models.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from datetime import datetime, timezone
from database.models import (
    Transaction, Settlement, ExceptionRecord, Match, AuditEvent,
    ReconciliationRun, JournalEntryDB, JournalLineDB,
    Organization, Entity, PeriodClose, WebhookEvent,
)


class TestTransactionModel:
    def test_create_transaction(self, db_session):
        tx = Transaction(
            canonical_id="tx_model_test_001",
            source="Razorpay",
            source_record_id="pay_001",
            amount_minor=50000,
            event_time=datetime(2026, 8, 15, tzinfo=timezone.utc),
            event_type="PAYMENT",
            direction="CREDIT",
            status="SETTLED",
        )
        db_session.add(tx)
        db_session.commit()
        result = db_session.query(Transaction).filter_by(canonical_id="tx_model_test_001").first()
        assert result is not None
        assert result.amount_minor == 50000
        assert result.source == "Razorpay"

    def test_transaction_repr(self, db_session):
        tx = Transaction(
            canonical_id="tx_repr_test",
            source="HDFC",
            source_record_id="stmt_001",
            amount_minor=100000,
            event_time=datetime(2026, 8, 15, tzinfo=timezone.utc),
            event_type="CREDIT",
            direction="CREDIT",
            status="SETTLED",
        )
        assert "tx_repr_test" in repr(tx)
        assert "HDFC" in repr(tx)

    def test_amount_is_integer(self, db_session):
        tx = Transaction(
            canonical_id="tx_int_test",
            source="Razorpay",
            source_record_id="pay_int",
            amount_minor=999999,
            event_time=datetime(2026, 8, 15, tzinfo=timezone.utc),
            event_type="PAYMENT",
            direction="CREDIT",
            status="SETTLED",
        )
        db_session.add(tx)
        db_session.commit()
        result = db_session.query(Transaction).filter_by(canonical_id="tx_int_test").first()
        assert isinstance(result.amount_minor, int)


class TestSettlementModel:
    def test_create_settlement(self, db_session):
        s = Settlement(
            settlement_id="SET_MODEL_001",
            settlement_date=datetime(2026, 8, 15, tzinfo=timezone.utc),
            gross_minor=1000000,
            fees_minor=20000,
            tax_minor=3600,
            net_minor=976400,
            bank_credit_minor=976400,
            variance_minor=0,
            status="SETTLED",
        )
        db_session.add(s)
        db_session.commit()
        result = db_session.query(Settlement).filter_by(settlement_id="SET_MODEL_001").first()
        assert result is not None
        assert result.gross_minor - result.fees_minor - result.tax_minor == result.net_minor

    def test_settlement_conservation(self, db_session):
        """Verify gross - fees - tax = net (financial conservation law)."""
        gross = 5000000
        fees = int(gross * 0.02)
        tax = int(fees * 0.18)
        net = gross - fees - tax
        s = Settlement(
            settlement_id="SET_CONSERVATION",
            settlement_date=datetime(2026, 8, 15, tzinfo=timezone.utc),
            gross_minor=gross,
            fees_minor=fees,
            tax_minor=tax,
            net_minor=net,
            bank_credit_minor=net,
            variance_minor=0,
            status="SETTLED",
        )
        db_session.add(s)
        db_session.commit()
        result = db_session.query(Settlement).filter_by(settlement_id="SET_CONSERVATION").first()
        assert result.gross_minor - result.fees_minor - result.tax_minor == result.net_minor
        assert result.variance_minor == 0


class TestExceptionModel:
    def test_create_exception(self, db_session):
        # Need a run first for FK
        run = ReconciliationRun(
            run_id="TEST_RUN_EXC", threshold=0.95,
            records_processed=10, auto_matched=8, manual_review=1, unresolved=1,
            match_rate=90.0, status="COMPLETED",
        )
        db_session.add(run)
        tx = Transaction(
            canonical_id="tx_exc_test", source="Razorpay", source_record_id="pay_exc",
            amount_minor=50000, event_time=datetime(2026, 8, 15, tzinfo=timezone.utc),
            event_type="PAYMENT", direction="CREDIT", status="SETTLED",
        )
        db_session.add(tx)
        db_session.commit()

        exc = ExceptionRecord(
            exception_id="EXC_MODEL_001",
            run_id="TEST_RUN_EXC",
            transaction_id="tx_exc_test",
            reason_code="AMOUNT_MISMATCH",
            severity="HIGH",
            status="OPEN",
        )
        db_session.add(exc)
        db_session.commit()
        result = db_session.query(ExceptionRecord).filter_by(exception_id="EXC_MODEL_001").first()
        assert result is not None
        assert result.severity == "HIGH"
        assert result.status == "OPEN"


class TestAuditEventModel:
    def test_create_audit_event(self, db_session):
        evt = AuditEvent(
            event_id="aud_model_test",
            run_id="TEST_RUN_001",
            record_id="tx_test_0000",
            action="INGESTED",
            payload={"test": True},
            previous_hash="0" * 64,
            current_hash="a" * 64,
            hmac_signature="b" * 64,
            nonce="c" * 32,
            sequence=0,
        )
        db_session.add(evt)
        db_session.commit()
        result = db_session.query(AuditEvent).filter_by(event_id="aud_model_test").first()
        assert result is not None
        assert result.sequence == 0


class TestJournalEntryModel:
    def test_balanced_entry(self, db_session):
        entry = JournalEntryDB(
            entry_id="je_balanced_test",
            description="Test balanced entry",
            reference="ref_001",
        )
        db_session.add(entry)
        line1 = JournalLineDB(
            entry_id="je_balanced_test",
            account="assets:cash_in_transit",
            debit_minor=250000,
            credit_minor=0,
        )
        line2 = JournalLineDB(
            entry_id="je_balanced_test",
            account="income:revenue",
            debit_minor=0,
            credit_minor=250000,
        )
        db_session.add_all([line1, line2])
        db_session.commit()

        lines = db_session.query(JournalLineDB).filter_by(entry_id="je_balanced_test").all()
        total_debit = sum(l.debit_minor for l in lines)
        total_credit = sum(l.credit_minor for l in lines)
        assert total_debit == total_credit
        assert total_debit == 250000


class TestOrganizationModel:
    def test_create_org_with_entities(self, db_session):
        org = Organization(org_id="ORG_TEST", name="Test Corp")
        db_session.add(org)
        entity = Entity(entity_id="ENT_TEST", org_id="ORG_TEST", name="Test India", currency="INR")
        db_session.add(entity)
        db_session.commit()

        result = db_session.query(Organization).filter_by(org_id="ORG_TEST").first()
        assert result is not None
        assert len(result.entities) == 1
        assert result.entities[0].currency == "INR"
