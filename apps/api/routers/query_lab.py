from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Any
import json
import logging
from google import genai
from google.genai import types

from database.session import get_db
from database.models import Settlement, Transaction, ExceptionRecord
from apps.api.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    query: str

class Filter(BaseModel):
    field: str
    operator: str = Field(description="Must be one of: > < == !=")
    value: Any

class ParsedQuery(BaseModel):
    entity: str = Field(description="Must be one of: settlements, transactions, exceptions")
    filters: list[Filter]

@router.post("/execute")
async def execute_query(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key missing")
        
    client = genai.Client(api_key=settings.gemini_api_key)
    
    # Intent Parser
    prompt = f"""
    You are an AI-to-SQL intent parser for a financial system.
    Translate the user's natural language query into a strict JSON intent structure.
    
    Allowed entities: settlements, transactions, exceptions
    Allowed operators: >, <, ==, !=
    
    User Query: "{req.query}"
    """
    
    try:
        response = await client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ParsedQuery,
                temperature=0.0
            )
        )
        
        parsed_json = response.text
        intent = ParsedQuery.model_validate_json(parsed_json)
        
    except Exception as e:
        logger.error(f"Failed to parse query intent: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Could not parse query: {str(e)}")
        
    # Query Validator and Executor
    if intent.entity == "settlements":
        model = Settlement
    elif intent.entity == "transactions":
        model = Transaction
    elif intent.entity == "exceptions":
        model = ExceptionRecord
    else:
        raise HTTPException(status_code=400, detail="Disallowed entity requested")
        
    stmt = select(model)
    
    for f in intent.filters:
        if not hasattr(model, f.field):
            continue # Safe ignore
            
        column = getattr(model, f.field)
        if f.operator == ">":
            stmt = stmt.where(column > f.value)
        elif f.operator == "<":
            stmt = stmt.where(column < f.value)
        elif f.operator == "==":
            stmt = stmt.where(column == f.value)
        elif f.operator == "!=":
            stmt = stmt.where(column != f.value)
            
    # Limit for safety
    stmt = stmt.limit(100)
    
    result = await db.execute(stmt)
    records = result.scalars().all()
    
    # Return serializable dicts
    data = []
    for r in records:
        d = r.__dict__.copy()
        d.pop("_sa_instance_state", None)
        data.append(d)
        
    return {
        "intent": intent.model_dump(),
        "results": data
    }
