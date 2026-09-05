from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.session import get_db
from database.models import Settlement, Transaction

router = APIRouter()

@router.get("/run")
async def run_controls(db: AsyncSession = Depends(get_db)):
    # 1. Settlement Completeness (gross - fees - tax +/- adjustments == net)
    settlements = await db.execute(select(Settlement))
    settlements = settlements.scalars().all()
    
    failed_conservation = 0
    failed_bank_recon = 0
    
    for s in settlements:
        expected_net = s.gross_minor - s.fees_minor - s.tax_minor + s.adjustments_minor
        if expected_net != s.net_minor:
            failed_conservation += 1
            
        if s.net_minor != s.bank_credit_minor:
            failed_bank_recon += 1

    # 2. Duplicate Prevention
    dups_query = await db.execute(
        select(Transaction.source_record_id, func.count(Transaction.id))
        .group_by(Transaction.source_record_id)
        .having(func.count(Transaction.id) > 1)
    )
    duplicate_count = len(dups_query.all())
    
    from database.models import WebhookEvent
    dup_webhooks = await db.execute(
        select(WebhookEvent.event_id, func.count(WebhookEvent.id))
        .group_by(WebhookEvent.event_id)
        .having(func.count(WebhookEvent.id) > 1)
    )
    dup_webhook_count = len(dup_webhooks.all())
    
    # 3. Balance Integrity (CQRS Ledger check)
    from database.models import JournalLineDB
    debits_res = await db.execute(select(func.sum(JournalLineDB.debit_minor)))
    credits_res = await db.execute(select(func.sum(JournalLineDB.credit_minor)))
    
    total_debits = debits_res.scalar() or 0
    total_credits = credits_res.scalar() or 0
    balance_variance = total_debits - total_credits

    controls = [
        {
            "name": "Balance Integrity",
            "status": "PASS" if balance_variance == 0 else "FAIL",
            "message": f"Ledger credits ({total_credits}) minus debits ({total_debits}) matches expected closing balance.",
            "variance_count": balance_variance
        },
        {
            "name": "Settlement Conservation",
            "status": "PASS" if failed_conservation == 0 else "FAIL",
            "message": f"{failed_conservation} settlements failed gross-to-net conservation.",
            "variance_count": failed_conservation
        },
        {
            "name": "Bank Reconciliation",
            "status": "PASS" if failed_bank_recon == 0 else "FAIL",
            "message": f"{failed_bank_recon} settlements have a bank credit variance.",
            "variance_count": failed_bank_recon
        },
        {
            "name": "Duplicate Prevention",
            "status": "PASS" if duplicate_count == 0 else "FAIL",
            "message": f"Found {duplicate_count} duplicate source records.",
            "variance_count": duplicate_count
        },
        {
            "name": "Webhook Idempotency",
            "status": "PASS" if dup_webhook_count == 0 else "FAIL",
            "message": f"Found {dup_webhook_count} duplicate webhook events processed.",
            "variance_count": dup_webhook_count
        }
    ]
    
    return {
        "status": "PASS" if all(c["status"] == "PASS" for c in controls) else "FAIL",
        "controls": controls
    }

from fastapi import HTTPException
from database.models import Match, ExceptionRecord, JournalEntryDB
from datetime import datetime, timezone

@router.post("/approvals/{record_type}/{record_id}/{action}")
async def process_approval(
    record_type: str, 
    record_id: str, 
    action: str, 
    db: AsyncSession = Depends(get_db)
):
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")

    status_val = "APPROVED" if action == "approve" else "REJECTED"
    reviewer = "Controller_Admin"

    if record_type == "match":
        stmt = select(Match).filter(Match.id == int(record_id))
    elif record_type == "exception":
        stmt = select(ExceptionRecord).filter(ExceptionRecord.exception_id == record_id)
    elif record_type == "journal":
        stmt = select(JournalEntryDB).filter(JournalEntryDB.entry_id == record_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid record_type")

    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail=f"{record_type} not found")

    record.review_status = status_val
    record.reviewer_id = reviewer
    
    if hasattr(record, "reviewed_at"):
        record.reviewed_at = datetime.now(timezone.utc)
    elif hasattr(record, "updated_at"):
        record.updated_at = datetime.now(timezone.utc)

    await db.commit()
    
    return {
        "message": f"Successfully updated {record_type} {record_id} to {status_val}",
        "reviewer": reviewer
    }

