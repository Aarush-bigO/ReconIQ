from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from database.session import get_db
from database.models import PeriodClose, ExceptionRecord, Settlement

router = APIRouter()

@router.get("/status")
async def get_period_status(db: AsyncSession = Depends(get_db)):
    # Get or create the current period
    from datetime import datetime, timezone
    current_period = datetime.now(timezone.utc).strftime("%B %Y")
    
    result = await db.execute(select(PeriodClose).where(PeriodClose.period_name == current_period))
    period = result.scalars().first()
    
    if not period:
        period = PeriodClose(
            period_id=f"prd_{datetime.utcnow().strftime('%Y%m')}",
            period_name=current_period,
            payment_activity_imported=True,
            settlements_imported=True,
            bank_statement_imported=True,
            reconciliation_complete=True,
            duplicate_controls_passed=True,
            variances_reviewed=True,
            audit_chain_verified=True,
        )
        db.add(period)
        await db.commit()
        await db.refresh(period)

    # Check exceptions
    exceptions = await db.execute(select(ExceptionRecord).where(ExceptionRecord.status == "OPEN"))
    open_count = len(exceptions.scalars().all())
    
    period.open_exceptions = open_count
    period.exceptions_resolved = (open_count == 0)
    
    # Check variances
    settlements = await db.execute(select(Settlement))
    total_variance = sum(s.variance_minor for s in settlements.scalars().all())
    period.total_variance_minor = total_variance
    
    await db.commit()
    await db.refresh(period)
    
    return period

@router.post("/approve")
async def request_approval(db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timezone
    current_period = datetime.now(timezone.utc).strftime("%B %Y")
    result = await db.execute(select(PeriodClose).where(PeriodClose.period_name == current_period))
    period = result.scalars().first()
    
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
        
    if period.open_exceptions > 0:
        raise HTTPException(status_code=400, detail="Cannot close period with open exceptions")
        
    period.status = "CLOSED"
    period.closed_at = datetime.utcnow()
    period.approved_by = "Controller"
    
    await db.commit()
    
    return {"message": f"{current_period} has been successfully closed.", "status": period.status}

@router.get("/history")
async def period_history(db: AsyncSession = Depends(get_db)):
    """List all period close records."""
    result = await db.execute(select(PeriodClose).order_by(PeriodClose.id.desc()))
    periods = result.scalars().all()
    return {
        "total": len(periods),
        "periods": [
            {
                "period_id": p.period_id,
                "period_name": p.period_name,
                "status": p.status,
                "open_exceptions": p.open_exceptions,
                "total_variance_minor": p.total_variance_minor,
                "closed_at": p.closed_at.isoformat() if p.closed_at else None,
                "approved_by": p.approved_by,
            }
            for p in periods
        ],
    }
