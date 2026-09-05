import sys
import os
import random
import uuid
import json
import secrets
import hmac
import hashlib
from datetime import datetime, timezone, timedelta

# 1. Insert path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.session import SyncSessionLocal, sync_engine, Base
from database.models import (
    Transaction, Match, ExceptionRecord, Settlement, PeriodClose,
    AuditEvent, ReconciliationRun, WebhookEvent, JournalEntryDB,
    JournalLineDB, Organization, Entity, MatchCandidate, BenchmarkRun,
    AgenticCommunication
)

# Constants
START_DATE = datetime(2026, 6, 7, tzinfo=timezone.utc)
HMAC_SECRET = b"reconiq-audit-secret-2026"
GENESIS_HASH = "GENESIS_HASH_00000000000000000000000000000000000000000000000000000000"

def generate_hmac(current_hash: str) -> str:
    return hmac.new(HMAC_SECRET, current_hash.encode(), hashlib.sha256).hexdigest()

def generate_sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def chunked_save(session, objects, chunk_size=5000):
    """Save objects in chunks using bulk_save_objects for performance"""
    for i in range(0, len(objects), chunk_size):
        session.bulk_save_objects(objects[i:i+chunk_size])
        session.commit()

def clear_database(session):
    print("Clearing existing data...")
    tables = [
        JournalLineDB, JournalEntryDB, MatchCandidate, Match, AgenticCommunication, ExceptionRecord,
        Transaction, WebhookEvent, AuditEvent, Settlement, PeriodClose,
        ReconciliationRun, BenchmarkRun, Entity, Organization
    ]
    for table in tables:
        session.execute(table.__table__.delete())
    session.commit()

def main():
    print("Initializing Database Seeder...")
    Base.metadata.create_all(bind=sync_engine)
    session = SyncSessionLocal()

    try:
        clear_database(session)

        # ---------------------------------------------------------
        # Organization & Entities
        # ---------------------------------------------------------
        print("Seeding Organization and Entities...")
        org = Organization(org_id="ORG_RECONIQ", name="ReconIQ Demo Corp")
        ent_in = Entity(entity_id="ENT_INDIA", org_id="ORG_RECONIQ", name="ReconIQ India Pvt Ltd", currency="INR")
        ent_gl = Entity(entity_id="ENT_GLOBAL", org_id="ORG_RECONIQ", name="ReconIQ Global Inc", currency="USD")
        session.add_all([org, ent_in, ent_gl])
        session.commit()

        # ---------------------------------------------------------
        # Reconciliation Runs (5 historical)
        # ---------------------------------------------------------
        print("Seeding Reconciliation Runs...")
        runs = []
        run_ids = []
        metrics = [
            (92.1, 8, 8000), (94.8, 10, 12000), (96.3, 11, 18000),
            (97.5, 13, 25000), (98.2, 15, 35000)
        ]
        
        for i in range(5):
            run_date = START_DATE + timedelta(days=i*15)
            run_id = f"RUN_{run_date.strftime('%Y%m%d')}_{str(i+1).zfill(3)}"
            run_ids.append(run_id)
            match_rate, duration, records = metrics[i]
            
            run = ReconciliationRun(
                run_id=run_id,
                status="COMPLETED",
                started_at=run_date,
                completed_at=run_date + timedelta(seconds=duration),
                threshold=0.95,
                records_processed=records,
                auto_matched=int(records * match_rate / 100),
                manual_review=int(records * 0.02),
                unresolved=int(records * (100 - match_rate) / 100),
                match_rate=match_rate,
                reconciled_value_minor=records * 250000,
                processing_ms=duration * 1000,
            )
            runs.append(run)
        
        session.add_all(runs)
        session.commit()
        last_run_id = run_ids[-1]

        # ---------------------------------------------------------
        # Transactions and Matches (24,000 matches = 48,000 txns)
        # ---------------------------------------------------------
        print("Seeding Transactions and Matches...")
        transactions = []
        matches = []
        
        for i in range(24000):
            # Razorpay Txn
            rzp_id = f"txn_{uuid.uuid4().hex}"
            amount = random.randint(5000, 20000000) # 50 to 200,000 INR
            date = START_DATE + timedelta(days=random.randint(0, 90), seconds=random.randint(0, 86400))
            
            order_id = f"order_{uuid.uuid4().hex[:8]}"
            pay_id = f"pay_RPZ_{uuid.uuid4().hex[:8]}"
            
            va_id = None
            cust_id = None
            if i % 10 == 0:
                va_id = f"va_RPZ_{uuid.uuid4().hex[:6]}"
                cust_id = f"cust_{uuid.uuid4().hex[:6]}"

            rzp_txn = Transaction(
                canonical_id=rzp_id,
                source="Razorpay",
                source_record_id=pay_id,
                reference_core=order_id,
                amount_minor=amount,
                currency="INR",
                event_time=date,
                event_type="PAYMENT",
                direction="CREDIT",
                status="SETTLED",
                payment_id=pay_id,
                order_id=order_id,
                virtual_account_id=va_id,
                customer_id=cust_id,
                metadata_={"entity_id": "ENT_INDIA"}
            )
            
            # HDFC Txn
            bank_id = f"txn_{uuid.uuid4().hex}"
            bank_date = date + timedelta(days=1, seconds=random.randint(0, 3600))
            utr_types = [
                f"HDFC{str(random.randint(10000000000, 99999999999))}",
                f"UTRCITI{str(random.randint(10000000, 99999999))}",
                f"NEFT{str(random.randint(1000000000, 9999999999))}"
            ]
            utr = random.choice(utr_types)
            
            bank_txn = Transaction(
                canonical_id=bank_id,
                source="HDFC",
                source_record_id=utr,
                reference_core=utr,
                amount_minor=amount,
                currency="INR",
                event_time=bank_date,
                event_type="CREDIT",
                direction="CREDIT",
                status="SETTLED",
                utr=utr,
                virtual_account_id=va_id,
                metadata_={"entity_id": "ENT_INDIA"}
            )
            
            transactions.extend([rzp_txn, bank_txn])
            
            # Match
            if va_id:
                prob = 1.0
                match_type = "SMART_COLLECT_MATCH"
                reason = "VIRTUAL_ACCOUNT"
            else:
                match_prob_rand = random.random()
                if match_prob_rand < 0.80:
                    prob = random.uniform(0.97, 0.99)
                    match_type = "EXACT_MATCH"
                    reason = "EXACT_MATCH"
                elif match_prob_rand < 0.95:
                    prob = random.uniform(0.95, 0.97)
                    match_type = "AUTO_MATCH"
                    reason = random.choice(["REFERENCE_MATCH", "AMOUNT_AND_DATE_MATCH"])
                else:
                    prob = random.uniform(0.90, 0.95)
                    match_type = "AUTO_MATCH"
                    reason = "AMOUNT_AND_DATE_MATCH"
                
            match = Match(
                run_id=last_run_id,
                left_transaction_id=rzp_id,
                right_transaction_id=bank_id,
                decision=match_type,
                probability=prob,
                reason_code=reason,
                evidence={"status": "CONFIRMED", "review_status": "APPROVED" if va_id else "PENDING"},
                created_at=bank_date + timedelta(hours=1)
            )
            matches.append(match)
            
        chunked_save(session, transactions)
        chunked_save(session, matches)

        # ---------------------------------------------------------
        # Exceptions (500)
        # ---------------------------------------------------------
        print("Seeding Exceptions...")
        exceptions = []
        exception_txns = []
        
        exception_types = [
            ("AMOUNT_MISMATCH", "HIGH", "POST_FEE_JOURNAL_ENTRY", 100),
            ("MISSING_IN_BANK", "MEDIUM", "MARK_AS_PENDING_SETTLEMENT", 80),
            ("FEE_DISCREPANCY", "LOW", "AUTO_ADJUST_FEE", 70),
            ("DUPLICATE_PAYMENT", "CRITICAL", "ESCALATE_TO_FINANCE", 50),
            ("PARTIAL_SETTLEMENT", "HIGH", "LINK_PARTIAL_SETTLEMENTS", 50),
            ("STALE_TRANSACTION", "MEDIUM", "MANUAL_INVESTIGATION", 50),
            ("REFERENCE_MISMATCH", "MEDIUM", "VERIFY_UTR_WITH_BANK", 50),
            ("CURRENCY_MISMATCH", "CRITICAL", "ESCALATE_TO_TREASURY", 50)
        ]
        
        for category, severity, action, count in exception_types:
            for i in range(count):
                date = START_DATE + timedelta(days=random.randint(0, 90))
                base_amount = random.randint(5000, 20000000)
                
                pay_id = f"pay_RPZ_{uuid.uuid4().hex[:8]}"
                order_id = f"order_{uuid.uuid4().hex[:8]}"
                rzp_id = f"txn_{uuid.uuid4().hex}"
                
                rzp_txn = Transaction(
                    canonical_id=rzp_id,
                    source="Razorpay",
                    source_record_id=pay_id,
                    reference_core=order_id,
                    amount_minor=base_amount,
                    currency="INR",
                    event_time=date,
                    event_type="PAYMENT",
                    direction="CREDIT",
                    status="SETTLED",
                    payment_id=pay_id,
                    order_id=order_id,
                    metadata_={"entity_id": "ENT_INDIA"}
                )
                exception_txns.append(rzp_txn)
                
                ext_tx_id = None
                description = f"{category} Exception generated."
                
                if category == "AMOUNT_MISMATCH":
                    diff = random.randint(1800, 50000) # 18 to 500 INR difference
                    ext_tx_id = f"txn_{uuid.uuid4().hex}"
                    utr = f"NEFT{random.randint(1000000000, 9999999999)}"
                    bank_txn = Transaction(
                        canonical_id=ext_tx_id, source="HDFC", source_record_id=utr, reference_core=utr,
                        amount_minor=base_amount - diff, currency="INR", event_time=date+timedelta(days=1), event_type="CREDIT", direction="CREDIT",
                        status="SETTLED", utr=utr, metadata_={"entity_id": "ENT_INDIA"}
                    )
                    exception_txns.append(bank_txn)
                    description = f"The payment gateway recorded ₹{base_amount/100:.2f} but the bank statement shows ₹{(base_amount-diff)/100:.2f} — a difference of ₹{diff/100:.2f} which corresponds exactly to the GST component (18%) of the processing fee."
                
                elif category == "MISSING_IN_BANK":
                    description = f"Transaction on {date.strftime('%Y-%m-%d')} has no bank counterpart. T+1 settlement expected on {(date+timedelta(days=1)).strftime('%Y-%m-%d')} did not arrive. Investigate possible weekend or holiday delays."
                    
                elif category == "FEE_DISCREPANCY":
                    diff = random.randint(100, 5000)
                    ext_tx_id = f"txn_{uuid.uuid4().hex}"
                    utr = f"NEFT{random.randint(1000000000, 9999999999)}"
                    bank_txn = Transaction(
                        canonical_id=ext_tx_id, source="HDFC", source_record_id=utr, reference_core=utr,
                        amount_minor=base_amount - diff, currency="INR", event_time=date+timedelta(days=1), event_type="CREDIT", direction="CREDIT",
                        status="SETTLED", utr=utr, metadata_={"entity_id": "ENT_INDIA"}
                    )
                    exception_txns.append(bank_txn)
                    description = f"Fee calculation difference of ₹{diff/100:.2f} detected on transaction. Expected standard 2% plus 18% GST rounding variance."
                
                elif category == "DUPLICATE_PAYMENT":
                    ext_tx_id = f"txn_{uuid.uuid4().hex}"
                    pay_id_dup = f"pay_RPZ_{uuid.uuid4().hex[:8]}"
                    dup_txn = Transaction(
                        canonical_id=ext_tx_id, source="Razorpay", source_record_id=pay_id_dup, reference_core=order_id,
                        amount_minor=base_amount, currency="INR", event_time=date+timedelta(minutes=5), event_type="PAYMENT", direction="CREDIT",
                        status="SETTLED", payment_id=pay_id_dup, order_id=order_id, metadata_={"entity_id": "ENT_INDIA"}
                    )
                    exception_txns.append(dup_txn)
                    description = f"Identical amounts (₹{base_amount/100:.2f}) processed within 5 minutes. High probability of webhook replay or idempotency key failure."
                
                elif category == "PARTIAL_SETTLEMENT":
                    description = f"Payment of ₹{base_amount/100:.2f} is partially settled. Corresponding bank credits only cover a portion of the total amount."
                    
                elif category == "STALE_TRANSACTION":
                    description = f"Transaction from {date.strftime('%Y-%m-%d')} is over 15 days old with no matching bank credit. Requires manual investigation."
                    
                elif category == "REFERENCE_MISMATCH":
                    ext_tx_id = f"txn_{uuid.uuid4().hex}"
                    utr = f"UTX{random.randint(100000, 999999)}"
                    bank_txn = Transaction(
                        canonical_id=ext_tx_id, source="HDFC", source_record_id=utr, reference_core=utr,
                        amount_minor=base_amount, currency="INR", event_time=date+timedelta(days=1), event_type="CREDIT", direction="CREDIT",
                        status="SETTLED", utr=utr, metadata_={"entity_id": "ENT_INDIA"}
                    )
                    exception_txns.append(bank_txn)
                    description = f"Similar UTR numbers detected with exact amount match (₹{base_amount/100:.2f}) but differing prefixes or minor typos."
                    
                elif category == "CURRENCY_MISMATCH":
                    description = f"Transaction reported in INR but corresponding ledger entry reflects USD equivalent. Verify cross-border payment routing."
                
                exc = ExceptionRecord(
                    exception_id=f"exc_{uuid.uuid4().hex}",
                    run_id=random.choice(run_ids),
                    transaction_id=rzp_id,
                    reason_code=category,
                    severity=severity,
                    status="OPEN",
                    ai_explanation=description,
                    recommended_action=action,
                    created_at=date + timedelta(days=2)
                )
                exceptions.append(exc)
        
        chunked_save(session, exception_txns)
        chunked_save(session, exceptions)

        # ---------------------------------------------------------
        # Agentic Communications (Mock data for open exceptions)
        # ---------------------------------------------------------
        print("Seeding Agentic Communications...")
        communications = []
        for exc in random.sample(exceptions, min(20, len(exceptions))):
            comm = AgenticCommunication(
                exception_id=exc.exception_id,
                message_content=f"[Slack Outreach] Hey team, could you provide more context on the {exc.reason_code} exception? ID: {exc.exception_id}",
                status="AWAITING_REPLY"
            )
            communications.append(comm)
        chunked_save(session, communications)

        # ---------------------------------------------------------
        # Settlements (365 daily)
        # ---------------------------------------------------------
        print("Seeding Settlements...")
        settlements = []
        settle_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for i in range(365):
            date = settle_start + timedelta(days=i)
            gross = random.randint(10000000, 150000000) # 1L to 15L INR
            fees = int(gross * 0.02)
            tax = int(fees * 0.18)
            net = gross - fees - tax
            
            variance = 0
            status = "SETTLED"
            if i % 30 == 0:
                variance = random.choice([-25000, -10000, 10000, 25000])
                status = "PARTIAL"
                
            bank_credit = net + variance
            utr = f"UTR{random.randint(10000, 99999)}" if random.choice([True, False]) else f"NEFT{random.randint(1000000000, 9999999999)}"
            
            settle = Settlement(
                settlement_id=f"set_{uuid.uuid4().hex}",
                settlement_date=date,
                gross_minor=gross,
                fees_minor=fees,
                tax_minor=tax,
                adjustments_minor=0,
                net_minor=net,
                bank_credit_minor=bank_credit,
                variance_minor=variance,
                status=status,
                utr=utr
            )
            settlements.append(settle)
            
        chunked_save(session, settlements)

        # ---------------------------------------------------------
        # Journal Entries (100)
        # ---------------------------------------------------------
        print("Seeding Journal Entries...")
        journals = []
        journal_lines = []
        
        for i in range(100):
            je_id = f"je_{uuid.uuid4().hex[:12]}"
            amount = random.randint(5000, 100000)
            date = START_DATE + timedelta(days=random.randint(0, 90))
            
            je = JournalEntryDB(
                entry_id=je_id,
                posted_at=date,
                description="Daily Revenue Recognition",
                reference=random.choice(run_ids),
                metadata_={"status": "POSTED", "entity_id": "ENT_INDIA"}
            )
            journals.append(je)
            
            line1 = JournalLineDB(
                entry_id=je_id, account="assets:cash_in_transit",
                debit_minor=amount, credit_minor=0, memo="Debit"
            )
            line2 = JournalLineDB(
                entry_id=je_id, account="income:revenue",
                debit_minor=0, credit_minor=amount, memo="Credit"
            )
            journal_lines.extend([line1, line2])
            
        chunked_save(session, journals)
        chunked_save(session, journal_lines)

        # ---------------------------------------------------------
        # Webhook Events (50)
        # ---------------------------------------------------------
        print("Seeding Webhook Events...")
        webhooks = []
        event_types = ["payment.captured", "payment.failed", "settlement.processed", "refund.created", "order.paid"]
        
        for i in range(50):
            status = "PROCESSED" if random.random() < 0.9 else "PENDING"
            ev_type = random.choice(event_types)
            payload = {"event": ev_type, "contains": ["payment"], "payload": {"payment": {"entity": {"id": f"pay_{uuid.uuid4().hex[:8]}"}}}}
            
            wh = WebhookEvent(
                event_id=f"wh_{uuid.uuid4().hex}",
                provider="Razorpay",
                event_type=ev_type,
                payload=payload,
                processing_status=status,
                received_at=START_DATE + timedelta(days=random.randint(0, 90))
            )
            webhooks.append(wh)
            
        chunked_save(session, webhooks)

        # ---------------------------------------------------------
        # Audit Events (1000)
        # ---------------------------------------------------------
        print("Seeding Audit Events...")
        from audit.audit_log import AuditChain
        audits = []
        chain = AuditChain(hmac_secret="reconiq-audit-secret-2026")
        actions = ["INGESTED", "MATCH_CONFIRMED", "EXCEPTION_CREATED", "SETTLEMENT_RECONCILED", "JOURNAL_ENTRY_POSTED"]
        
        for i in range(1000):
            run = random.choice(run_ids)
            record = f"rec_{uuid.uuid4().hex[:8]}"
            action = random.choice(actions)
            
            # Use the actual AuditChain logic so hashes and HMACs are valid!
            event_dict = chain.record(run_id=run, record_id=record, action=action)
            
            ae = AuditEvent(
                event_id=event_dict["event_id"],
                sequence=event_dict["sequence"],
                action=event_dict["action"],
                record_id=event_dict["record_id"],
                run_id=event_dict["run_id"],
                previous_hash=event_dict["previous_hash"],
                current_hash=event_dict["current_hash"],
                hmac_signature=event_dict["hmac_signature"],
                nonce=event_dict["nonce"],
                payload={k: v for k, v in event_dict.items() if k not in ["previous_hash", "current_hash", "hmac_signature", "envelope_version", "schema_version", "nonce", "sequence"]},
            )
            audits.append(ae)
            
        chunked_save(session, audits)

        # ---------------------------------------------------------
        # Period Closes (3)
        # ---------------------------------------------------------
        print("Seeding Period Closes...")
        p1 = PeriodClose(
            period_id="PRD_2026_Q1", period_name="Q1 2026", status="CLOSED",
            payment_activity_imported=True, settlements_imported=True,
            bank_statement_imported=True, reconciliation_complete=True,
            duplicate_controls_passed=True, variances_reviewed=True,
            audit_chain_verified=True, exceptions_resolved=True,
            open_exceptions=0, total_variance_minor=0,
            closed_at=datetime(2026, 3, 31, tzinfo=timezone.utc), approved_by="Controller",
        )
        p2 = PeriodClose(
            period_id="PRD_2026_Q2", period_name="Q2 2026", status="CLOSED",
            payment_activity_imported=True, settlements_imported=True,
            bank_statement_imported=True, reconciliation_complete=True,
            duplicate_controls_passed=True, variances_reviewed=True,
            audit_chain_verified=True, exceptions_resolved=True,
            open_exceptions=0, total_variance_minor=0,
            closed_at=datetime(2026, 6, 30, tzinfo=timezone.utc), approved_by="Controller",
        )
        p3 = PeriodClose(
            period_id="PRD_2026_Q3", period_name="Q3 2026", status="OPEN",
            payment_activity_imported=True, settlements_imported=True,
            bank_statement_imported=False, reconciliation_complete=False,
            duplicate_controls_passed=False, variances_reviewed=False,
            audit_chain_verified=False, exceptions_resolved=False,
            open_exceptions=500, total_variance_minor=0,
        )
        
        session.add_all([p1, p2, p3])
        session.commit()

        # ---------------------------------------------------------
        # Summary
        # ---------------------------------------------------------
        print(f"""
✅ ReconIQ Production Database Seeded Successfully
╔══════════════════════════════╦══════════╗
║ Entity                       ║ Count    ║
╠══════════════════════════════╬══════════╣
║ Reconciliation Runs          ║ 5        ║
║ Transactions                 ║ {len(transactions) + len(exception_txns):<8} ║
║ Matches                      ║ {len(matches):<8} ║
║ Exceptions                   ║ {len(exceptions):<8} ║
║ Settlements                  ║ {len(settlements):<8} ║
║ Audit Events                 ║ {len(audits):<8} ║
║ Journal Entries              ║ {len(journals):<8} ║
║ Webhook Events               ║ {len(webhooks):<8} ║
║ Period Closes                ║ 3        ║
║ Agentic Communications       ║ {len(communications):<8} ║
╚══════════════════════════════╩══════════╝
        """)

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
