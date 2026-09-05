import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import google.generativeai as genai

from database.session import get_db
from database.models import PeriodClose, Transaction, ExceptionRecord, Settlement

router = APIRouter(tags=["Copilot"])

@router.get("/period-summary/{period_id}")
async def get_period_summary(period_id: str, db: AsyncSession = Depends(get_db)):
    # Query period
    period_result = await db.execute(select(PeriodClose).filter(PeriodClose.period_id == period_id))
    period = period_result.scalar_one_or_none()
    
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
        
    # Query totals
    tx_count_res = await db.execute(select(func.count(Transaction.id)))
    tx_count = tx_count_res.scalar() or 0
    
    exc_count_res = await db.execute(select(func.count(ExceptionRecord.id)))
    exc_count = exc_count_res.scalar() or 0
    
    variance_res = await db.execute(select(func.sum(Settlement.variance_minor)))
    variance = variance_res.scalar() or 0
    
    prompt = f"Write a 3-paragraph executive summary for the {period.period_name} period close. We processed {tx_count} transactions, had {exc_count} exceptions, and ${variance / 100:.2f} in variances."
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(prompt)
            return {"summary": response.text}
        except Exception as e:
            return {"summary": f"[MOCKED - Error calling Gemini: {str(e)}] {prompt}"}
    else:
        return {"summary": f"[MOCKED] {prompt}"}
