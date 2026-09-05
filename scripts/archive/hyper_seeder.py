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

def generate_hyper_data():
    print("Activating HYPER God Mode... Generating Enterprise-Scale Data")
    
    session = SyncSessionLocal()
    Base.metadata.create_all(bind=sync_engine)
    
    print("Clearing existing data...")
    session.execute(text("TRUNCATE TABLE exceptions, matches, settlements, transactions, period_closes, audit_events, reconciliation_runs CASCADE;"))
    session.commit()
    
    print("Generating Reconciliation Runs...")
    # Add 5 historical runs to make the dashboard look busy
    base_date = datetime.utcnow() - timedelta(days=90)
    
    runs = []
    run_ids = []
    for i in range(5):
        rid = f"RUN_{uuid.uuid4().hex[:8].upper()}"
        run_ids.append(rid)
        r = ReconciliationRun(
            run_id=rid,
            started_at=base_date + timedelta(days=i*15),
            completed_at=base_date + timedelta(days=i*15, minutes=12),
            threshold=0.95,
            records_processed=random.randint(45000, 55000),
            auto_matched=random.randint(40000, 44000),
            manual_review=random.randint(500, 2000),
            unresolved=random.randint(100, 500),
            match_rate=round(random.uniform(92.0, 98.5), 2),
            reconciled_value_minor=random.randint(1000000000, 5000000000),
            status="COMPLETED"
        )
        runs.append(r)
    session.bulk_save_objects(runs)
    session.commit()
    
    active_run = run_ids[-1]

    print("Generating 50,000 highly realistic transactions (25,000 matched pairs)...")
    transactions = []
    matches = []
    exceptions = []
    
    # 25,000 pairs = 50,000 transactions
    for i in range(25000):
        utr_val = f"HDFC{random.randint(10000000000, 99999999999)}"
        amount = random.randint(100, 150000) * 100
        t_date = base_date + timedelta(days=random.randint(0, 90), minutes=random.randint(0, 1440))
        
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
            run_id=active_run,
            left_transaction_id=tx_pg.canonical_id,
            right_transaction_id=tx_bank.canonical_id,
            probability=round(random.uniform(0.95, 0.99), 4),
            decision="AUTO_MATCH",
            reason_code="EXACT_MATCH"
        ))
        
        if i % 5000 == 0:
            print(f"  ... {i*2} transactions generated")

    print("Generating 1,000 precise exceptions for the AI Control Room...")
    for i in range(1000):
        amount = random.randint(100, 80000) * 100
        t_date = base_date + timedelta(days=random.randint(0, 90))
        
        exc_type = random.choice(["AMOUNT_MISMATCH", "MISSING_IN_BANK", "FEE_DISCREPANCY", "CURRENCY_MISMATCH"])
        
        if exc_type == "AMOUNT_MISMATCH":
            utr_val = f"HDFC{random.randint(10000000000, 99999999999)}"
            tx_pg = Transaction(
                canonical_id=f"pg_{uuid.uuid4()}", source="Razorpay", source_record_id=f"evt_{uuid.uuid4()}",
                reference_core=utr_val, amount_minor=amount, currency="INR", event_time=t_date,
                event_type="PAYMENT", direction="CREDIT", status="SETTLED", utr=utr_val
            )
            tx_bank = Transaction(
                canonical_id=f"bank_{uuid.uuid4()}", source="HDFC", source_record_id=f"stmt_{uuid.uuid4()}",
                reference_core=utr_val, amount_minor=amount - random.choice([5000, 1800, 12000]), 
                currency="INR", event_time=t_date, event_type="CREDIT", direction="CREDIT", status="SETTLED", utr=utr_val
            )
            transactions.extend([tx_pg, tx_bank])
            exceptions.append(ExceptionRecord(
                exception_id=f"EXC_{uuid.uuid4().hex[:12]}", run_id=active_run, transaction_id=tx_pg.canonical_id,
                reason_code="AMOUNT_MISMATCH", severity="HIGH", status="OPEN",
                ai_explanation="The bank statement shows an amount slightly less than the payment gateway. This is likely a fee deduction mismatch. Recommend automatically posting a journal entry for gateway fees.",
                recommended_action="POST_FEE_JOURNAL_ENTRY"
            ))
        elif exc_type == "MISSING_IN_BANK":
            tx_pg = Transaction(
                canonical_id=f"pg_{uuid.uuid4()}", source="Razorpay", source_record_id=f"evt_{uuid.uuid4()}",
                reference_core=f"ORDER_{random.randint(1000, 9999)}", amount_minor=amount, currency="INR", 
                event_time=t_date, event_type="PAYMENT", direction="CREDIT", status="SETTLED", utr=None
            )
            transactions.append(tx_pg)
            exceptions.append(ExceptionRecord(
                exception_id=f"EXC_{uuid.uuid4().hex[:12]}", run_id=active_run, transaction_id=tx_pg.canonical_id,
                reason_code="MISSING_IN_BANK", severity="MEDIUM", status="OPEN",
                ai_explanation="This transaction occurred near the end of the day or weekend. Standard T+1/T+2 settlement pushes this to the next business day. It should reconcile in the next run.",
                recommended_action="MARK_AS_PENDING_SETTLEMENT"
            ))
        else:
            tx_pg = Transaction(
                canonical_id=f"pg_{uuid.uuid4()}", source="Razorpay", source_record_id=f"evt_{uuid.uuid4()}",
                reference_core=f"ORDER_{random.randint(1000, 9999)}", amount_minor=amount, currency="INR", 
                event_time=t_date, event_type="REFUND", direction="DEBIT", status="FAILED", utr=None
            )
            transactions.append(tx_pg)
            exceptions.append(ExceptionRecord(
                exception_id=f"EXC_{uuid.uuid4().hex[:12]}", run_id=active_run, transaction_id=tx_pg.canonical_id,
                reason_code=exc_type, severity="CRITICAL", status="OPEN",
                ai_explanation="A critical mismatch or failure occurred on a refund. Manual intervention required to prevent customer escalation.",
                recommended_action="ESCALATE_TO_FINANCE"
            ))

    # Bulk insert
    print("Writing 51,000+ transactions to PostgreSQL...")
    chunk_size = 5000
    for i in range(0, len(transactions), chunk_size):
        session.bulk_save_objects(transactions[i:i+chunk_size])
    session.commit()
    
    print("Writing matches and exceptions...")
    for i in range(0, len(matches), chunk_size):
        session.bulk_save_objects(matches[i:i+chunk_size])
    session.bulk_save_objects(exceptions)
    session.commit()
    
    print("Generating 365 Daily Settlements (Full Year)...")
    settlements = []
    for i in range(365):
        gross = random.randint(1000000, 15000000) * 100
        fees = int(gross * 0.02)
        tax = int(fees * 0.18)
        net = gross - fees - tax
        
        # Introduce a few settlement variances for realism
        variance = 0
        if i % 45 == 0:
            variance = random.choice([10000, -5000, 25000])
            
        settlements.append(Settlement(
            settlement_id=f"SET_{uuid.uuid4().hex[:8]}",
            settlement_date=base_date + timedelta(days=i),
            gross_minor=gross,
            fees_minor=fees,
            tax_minor=tax,
            net_minor=net,
            bank_credit_minor=net + variance,
            variance_minor=variance,
            status="SETTLED" if variance == 0 else "PARTIAL",
            utr=f"UTR{random.randint(10000, 99999)}"
        ))
    session.bulk_save_objects(settlements)

    print("Populating Period Close...")
    for i in range(3):
        session.add(PeriodClose(
            period_id=f"PRD_2026_{i}",
            period_name=f"Q{i+1} 2026",
            status="CLOSED" if i < 2 else "OPEN",
            payment_activity_imported=True,
            settlements_imported=True,
            open_exceptions=0 if i < 2 else len(exceptions)
        ))
    
    session.commit()
    session.close()
    
    print("✅ HYPER God Mode Activated. 50,000+ records heavily inserted.")

if __name__ == "__main__":
    generate_hyper_data()
