import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.session import SyncSessionLocal, sync_engine, Base
from database.models import Transaction, Match, ExceptionRecord, Settlement, PeriodClose, AuditEvent, ReconciliationRun

def generate_god_mode_data():
    print("Activating God Mode...")
    
    session = SyncSessionLocal()
    Base.metadata.create_all(bind=sync_engine)
    
    print("Clearing existing data...")
    tables = ["exceptions", "matches", "settlements", "transactions", "period_closes", "audit_events", "reconciliation_runs"]
    for t in tables:
        session.execute(text(f"DELETE FROM {t}"))
    session.commit()
    
    print("Generating Reconciliation Run...")
    run_id = f"RUN_{uuid.uuid4().hex[:8].upper()}"
    run = ReconciliationRun(
        run_id=run_id,
        started_at=datetime.utcnow() - timedelta(minutes=10),
        completed_at=datetime.utcnow(),
        threshold=0.95,
        records_processed=10000,
        auto_matched=9600,
        manual_review=200,
        unresolved=200,
        match_rate=98.0,
        status="COMPLETED"
    )
    session.add(run)
    session.commit()

    print("Generating 10,000 highly realistic transactions...")
    transactions = []
    matches = []
    exceptions = []
    
    base_date = datetime.utcnow() - timedelta(days=30)
    
    # Valid matched pairs
    for i in range(4800):
        utr_val = f"HDFC{random.randint(10000000000, 99999999999)}"
        amount = random.randint(100, 50000) * 100
        t_date = base_date + timedelta(days=random.randint(0, 30), minutes=random.randint(0, 1440))
        
        tx_pg = Transaction(
            canonical_id=f"pg_{uuid.uuid4()}",
            source="Stripe",
            source_record_id=f"evt_{uuid.uuid4()}",
            reference_core=utr_val,
            amount_minor=amount,
            currency="INR",
            event_time=t_date,
            event_type="PAYMENT",
            direction="CREDIT",
            status="SETTLED",
            utr=utr_val
        )
        
        tx_bank = Transaction(
            canonical_id=f"bank_{uuid.uuid4()}",
            source="HDFC",
            source_record_id=f"stmt_{uuid.uuid4()}",
            reference_core=utr_val,
            amount_minor=amount,
            currency="INR",
            event_time=t_date + timedelta(days=1),
            event_type="CREDIT",
            direction="CREDIT",
            status="SETTLED",
            utr=utr_val
        )
        transactions.extend([tx_pg, tx_bank])
        
        matches.append(Match(
            run_id=run_id,
            left_transaction_id=tx_pg.canonical_id,
            right_transaction_id=tx_bank.canonical_id,
            probability=0.99,
            decision="AUTO_MATCH",
            reason_code="EXACT_MATCH"
        ))

    print("Generating 200 precise exceptions for the AI Control Room...")
    for i in range(200):
        amount = random.randint(100, 50000) * 100
        t_date = base_date + timedelta(days=random.randint(0, 30))
        is_amount_mismatch = random.choice([True, False])
        
        if is_amount_mismatch:
            utr_val = f"HDFC{random.randint(10000000000, 99999999999)}"
            tx_pg = Transaction(
                canonical_id=f"pg_{uuid.uuid4()}",
                source="Razorpay",
                source_record_id=f"evt_{uuid.uuid4()}",
                reference_core=utr_val,
                amount_minor=amount,
                currency="INR",
                event_time=t_date,
                event_type="PAYMENT",
                direction="CREDIT",
                status="SETTLED",
                utr=utr_val
            )
            tx_bank = Transaction(
                canonical_id=f"bank_{uuid.uuid4()}",
                source="HDFC",
                source_record_id=f"stmt_{uuid.uuid4()}",
                reference_core=utr_val,
                amount_minor=amount - 5000,
                currency="INR",
                event_time=t_date,
                event_type="CREDIT",
                direction="CREDIT",
                status="SETTLED",
                utr=utr_val
            )
            transactions.extend([tx_pg, tx_bank])
            
            exceptions.append(ExceptionRecord(
                exception_id=f"EXC_{uuid.uuid4().hex[:12]}",
                run_id=run_id,
                transaction_id=tx_pg.canonical_id,
                reason_code="AMOUNT_MISMATCH",
                severity="HIGH",
                status="OPEN",
                ai_explanation="The bank statement shows an amount exactly ₹50.00 less than the payment gateway. This matches the standard gateway fee profile. Recommend automatically posting a journal entry for gateway fees to balance the books.",
                recommended_action="POST_FEE_JOURNAL_ENTRY"
            ))
        else:
            tx_pg = Transaction(
                canonical_id=f"pg_{uuid.uuid4()}",
                source="Razorpay",
                source_record_id=f"evt_{uuid.uuid4()}",
                reference_core=f"ORDER_{random.randint(1000, 9999)}",
                amount_minor=amount,
                currency="INR",
                event_time=t_date,
                event_type="PAYMENT",
                direction="CREDIT",
                status="SETTLED",
                utr=None
            )
            transactions.append(tx_pg)
            
            exceptions.append(ExceptionRecord(
                exception_id=f"EXC_{uuid.uuid4().hex[:12]}",
                run_id=run_id,
                transaction_id=tx_pg.canonical_id,
                reason_code="MISSING_IN_BANK",
                severity="MEDIUM",
                status="OPEN",
                ai_explanation="This transaction occurred near the end of the day on Friday. Standard T+1 settlement pushes this to Monday. No action required, it should reconcile in the next run.",
                recommended_action="MARK_AS_PENDING_SETTLEMENT"
            ))

    # Chunk the inserts so it doesn't crash sqlite/postgres
    chunk_size = 2000
    for i in range(0, len(transactions), chunk_size):
        session.bulk_save_objects(transactions[i:i+chunk_size])
    session.commit()
    
    session.bulk_save_objects(matches)
    session.bulk_save_objects(exceptions)
    session.commit()
    
    print("Generating Settlements...")
    settlements = []
    for i in range(30):
        gross = random.randint(1000000, 5000000) * 100
        fees = int(gross * 0.02)
        tax = int(fees * 0.18)
        net = gross - fees - tax
        
        settlements.append(Settlement(
            settlement_id=f"SET_{uuid.uuid4().hex[:8]}",
            settlement_date=base_date + timedelta(days=i),
            gross_minor=gross,
            fees_minor=fees,
            tax_minor=tax,
            net_minor=net,
            bank_credit_minor=net,
            variance_minor=0,
            status="SETTLED",
            utr=f"UTR{random.randint(10000, 99999)}"
        ))
    session.bulk_save_objects(settlements)

    print("Populating Period Close...")
    session.add(PeriodClose(
        period_id="PRD_SEP_2026",
        period_name="September 2026",
        status="OPEN",
        payment_activity_imported=True,
        settlements_imported=True,
        open_exceptions=len(exceptions)
    ))
    
    session.commit()
    session.close()
    
    print("✅ God Mode Activated. 10,000+ realistic records inserted into the database.")

if __name__ == "__main__":
    generate_god_mode_data()
