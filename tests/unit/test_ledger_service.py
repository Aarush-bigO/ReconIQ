"""
Unit tests for the double-entry ledger service.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from apps.api.services.ledger import post_journal_entry_sync, process_financial_event_sync
from database.models import JournalEntryDB, JournalLineDB


class TestPostJournalEntry:
    def test_balanced_entry_succeeds(self, db_session):
        entry_id = post_journal_entry_sync(
            db=db_session,
            description="Payment capture",
            reference="pay_001",
            lines=[
                {"account": "assets:cash_in_transit", "debit_minor": 100000, "credit_minor": 0},
                {"account": "income:revenue", "debit_minor": 0, "credit_minor": 100000},
            ],
        )
        assert entry_id is not None
        assert entry_id.startswith("je_")

    def test_unbalanced_entry_raises(self, db_session):
        with pytest.raises(ValueError, match="Double-entry violation"):
            post_journal_entry_sync(
                db=db_session,
                description="Bad entry",
                reference="bad_001",
                lines=[
                    {"account": "assets:cash_in_transit", "debit_minor": 100000, "credit_minor": 0},
                    {"account": "income:revenue", "debit_minor": 0, "credit_minor": 50000},
                ],
            )

    def test_zero_amount_returns_none(self, db_session):
        result = post_journal_entry_sync(
            db=db_session,
            description="Zero entry",
            reference="zero_001",
            lines=[
                {"account": "assets:cash_in_transit", "debit_minor": 0, "credit_minor": 0},
                {"account": "income:revenue", "debit_minor": 0, "credit_minor": 0},
            ],
        )
        assert result is None

    def test_entry_persists_lines(self, db_session):
        entry_id = post_journal_entry_sync(
            db=db_session,
            description="Multi-line entry",
            reference="multi_001",
            lines=[
                {"account": "assets:bank", "debit_minor": 500000, "credit_minor": 0, "memo": "Bank deposit"},
                {"account": "assets:cash_in_transit", "debit_minor": 0, "credit_minor": 500000, "memo": "Transit clear"},
            ],
        )
        lines = db_session.query(JournalLineDB).filter_by(entry_id=entry_id).all()
        assert len(lines) == 2
        assert lines[0].memo == "Bank deposit"


class TestProcessFinancialEvent:
    def test_payment_credit(self, db_session):
        entry_id = process_financial_event_sync(
            db=db_session,
            event_type="PAYMENT",
            direction="CREDIT",
            amount_minor=250000,
            reference="pay_test_001",
            description="Payment received",
        )
        assert entry_id is not None
        lines = db_session.query(JournalLineDB).filter_by(entry_id=entry_id).all()
        assert len(lines) == 2
        # Verify debit = credit
        total_debit = sum(l.debit_minor for l in lines)
        total_credit = sum(l.credit_minor for l in lines)
        assert total_debit == total_credit == 250000

    def test_refund_debit(self, db_session):
        entry_id = process_financial_event_sync(
            db=db_session,
            event_type="REFUND",
            direction="DEBIT",
            amount_minor=50000,
            reference="refund_test_001",
            description="Refund issued",
        )
        assert entry_id is not None

    def test_settlement_credit(self, db_session):
        entry_id = process_financial_event_sync(
            db=db_session,
            event_type="SETTLEMENT",
            direction="CREDIT",
            amount_minor=1000000,
            reference="settle_test_001",
            description="Settlement to bank",
        )
        assert entry_id is not None

    def test_unknown_event_returns_none(self, db_session):
        result = process_financial_event_sync(
            db=db_session,
            event_type="UNKNOWN_EVENT",
            direction="CREDIT",
            amount_minor=100000,
            reference="unknown_001",
            description="Unknown event",
        )
        assert result is None

    def test_all_events_maintain_balance(self, db_session):
        """Every financial event must produce balanced journal entries."""
        events = [
            ("PAYMENT", "CREDIT", 500000),
            ("REFUND", "DEBIT", 50000),
            ("FEE", "DEBIT", 10000),
            ("SETTLEMENT", "CREDIT", 440000),
            ("PAYOUT", "DEBIT", 440000),
        ]
        for event_type, direction, amount in events:
            entry_id = process_financial_event_sync(
                db=db_session,
                event_type=event_type,
                direction=direction,
                amount_minor=amount,
                reference=f"balance_test_{event_type.lower()}",
                description=f"Balance test: {event_type}",
            )
            if entry_id:
                lines = db_session.query(JournalLineDB).filter_by(entry_id=entry_id).all()
                total_debit = sum(l.debit_minor for l in lines)
                total_credit = sum(l.credit_minor for l in lines)
                assert total_debit == total_credit, f"Imbalance in {event_type}: D={total_debit}, C={total_credit}"
