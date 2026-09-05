"""
ReconIQ Enterprise — Double-Entry Ledger Service
Provides continuous accounting logic (CQRS) and journal posting validation.
"""
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from database.models import JournalEntryDB, JournalLineDB

# For sync contexts (ingestion/loaders)
def post_journal_entry_sync(db: Session, description: str, reference: str, lines: List[Dict[str, Any]]):
    """Post a balanced journal entry synchronously."""
    total_debit = sum(line.get("debit_minor", 0) for line in lines)
    total_credit = sum(line.get("credit_minor", 0) for line in lines)

    if total_debit != total_credit:
        raise ValueError(f"Double-entry violation: Debits ({total_debit}) do not equal Credits ({total_credit}).")

    if total_debit == 0:
        return None # No-op

    entry_id = f"je_{uuid.uuid4().hex[:12]}"
    
    entry = JournalEntryDB(
        entry_id=entry_id,
        description=description,
        reference=reference,
        metadata_={"lines_count": len(lines)}
    )
    db.add(entry)

    for line in lines:
        db.add(JournalLineDB(
            entry_id=entry_id,
            account=line["account"],
            debit_minor=line.get("debit_minor", 0),
            credit_minor=line.get("credit_minor", 0),
            memo=line.get("memo", "")
        ))

    db.commit()
    return entry_id


def process_financial_event_sync(db: Session, event_type: str, direction: str, amount_minor: int, reference: str, description: str):
    """
    Standardizes accounting rules for ReconIQ financial events.
    These map to specific T-Accounts.
    """
    lines = []
    
    # Simple standardized rules engine
    if event_type == "PAYMENT" and direction == "CREDIT":
        # Payment received: Debit Cash in Transit, Credit Revenue
        lines.append({"account": "assets:cash_in_transit", "debit_minor": amount_minor, "credit_minor": 0})
        lines.append({"account": "income:revenue", "debit_minor": 0, "credit_minor": amount_minor})
        
    elif event_type == "REFUND" and direction == "DEBIT":
        # Refund issued: Debit Revenue (or Refunds), Credit Cash in Transit
        lines.append({"account": "income:refunds", "debit_minor": amount_minor, "credit_minor": 0})
        lines.append({"account": "assets:cash_in_transit", "debit_minor": 0, "credit_minor": amount_minor})
        
    elif event_type == "FEE" and direction == "DEBIT":
        # Processor Fee: Debit Expenses, Credit Cash in Transit
        lines.append({"account": "expenses:processor_fees", "debit_minor": amount_minor, "credit_minor": 0})
        lines.append({"account": "assets:cash_in_transit", "debit_minor": 0, "credit_minor": amount_minor})
        
    elif event_type == "SETTLEMENT" and direction == "CREDIT":
        # Settlement to Bank: Debit Bank Account, Credit Cash in Transit
        lines.append({"account": "assets:bank", "debit_minor": amount_minor, "credit_minor": 0})
        lines.append({"account": "assets:cash_in_transit", "debit_minor": 0, "credit_minor": amount_minor})
        
    elif event_type == "PAYOUT" and direction == "DEBIT":
        # Payout to merchant: Debit Payables, Credit Bank
        lines.append({"account": "liabilities:payouts", "debit_minor": amount_minor, "credit_minor": 0})
        lines.append({"account": "assets:bank", "debit_minor": 0, "credit_minor": amount_minor})

    if not lines:
        # Fallback or unmapped event
        return None

    return post_journal_entry_sync(db, description, reference, lines)


async def get_account_balance(db: AsyncSession, account: str) -> int:
    """Calculate the balance of an account directly from the journal lines (CQRS)."""
    debits_res = await db.execute(select(func.sum(JournalLineDB.debit_minor)).where(JournalLineDB.account == account))
    credits_res = await db.execute(select(func.sum(JournalLineDB.credit_minor)).where(JournalLineDB.account == account))
    
    total_debit = debits_res.scalar() or 0
    total_credit = credits_res.scalar() or 0
    
    # Asset/Expense = Debit normal. Returning net debit balance. 
    return total_debit - total_credit

async def get_trial_balance(db: AsyncSession) -> List[Dict[str, Any]]:
    """Generates a trial balance of all accounts."""
    query = select(
        JournalLineDB.account, 
        func.sum(JournalLineDB.debit_minor).label("debits"), 
        func.sum(JournalLineDB.credit_minor).label("credits")
    ).group_by(JournalLineDB.account).order_by(JournalLineDB.account)
    
    res = await db.execute(query)
    
    tb = []
    for row in res.all():
        net = row.debits - row.credits
        tb.append({
            "account": row.account,
            "debit_minor": row.debits,
            "credit_minor": row.credits,
            "balance_minor": net
        })
        
    return tb


def draft_deduction_journal_entry_sync(session: Session, exception: Any, diff_amount: int) -> JournalEntryDB:
    """Draft a deduction journal entry based on exception category."""
    category_map = {
        "BANK_FEE": "expenses:bank_fees",
        "DISCOUNT": "expenses:discounts",
        "TAX": "expenses:taxes",
    }
    
    cat = getattr(exception, "deduction_category", None) or "BANK_FEE"
    expense_account = category_map.get(cat, "expenses:other")
    suspense_account = "reconciliation:suspense"
    
    entry_id = f"je_draft_{uuid.uuid4().hex[:12]}"
    
    entry = JournalEntryDB(
        entry_id=entry_id,
        description=f"Draft deduction for exception {exception.exception_id}",
        reference=exception.exception_id,
        status="DRAFT",
        metadata_={"lines_count": 2, "deduction_category": cat, "drafted": True}
    )
    session.add(entry)

    # Debit expense, Credit suspense
    line_debit = JournalLineDB(
        entry_id=entry_id,
        account=expense_account,
        debit_minor=diff_amount,
        credit_minor=0,
        memo=f"Exception {exception.exception_id} deduction"
    )
    line_credit = JournalLineDB(
        entry_id=entry_id,
        account=suspense_account,
        debit_minor=0,
        credit_minor=diff_amount,
        memo=f"Exception {exception.exception_id} suspense offset"
    )
    session.add(line_debit)
    session.add(line_credit)

    session.commit()
    session.refresh(entry)
    return entry

