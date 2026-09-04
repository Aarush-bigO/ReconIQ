from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from apps.api.services.ledger import get_trial_balance

router = APIRouter()

@router.get("/trial-balance")
async def trial_balance(db: AsyncSession = Depends(get_db)):
    """Returns the continuous trial balance (sum of debits vs credits)."""
    return await get_trial_balance(db)
