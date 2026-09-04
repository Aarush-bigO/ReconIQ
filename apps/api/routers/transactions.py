"""Transactions, Exceptions, Settlements, Audit, Reports, Webhooks, Evaluation routers."""
from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from apps.api.config import get_settings
from ingestion.loaders import load_all_sources, records_to_dict_list
from audit.audit_log import get_chain, AuditAction
from llm.explain import explain_exception
from exceptions.reason_codes import REASON_CODE_METADATA

settings = get_settings()

from database.session import SyncSessionLocal
from database.models import Transaction, Match
from apps.api.services.ledger import process_financial_event_sync

# ─────────────────────────────────────────────────────────────
# TRANSACTIONS
# ─────────────────────────────────────────────────────────────
router = APIRouter()

def _populate_transactions_if_empty(db):
    import time
    t0 = time.time()
    first = db.query(Transaction).first()
    t1 = time.time()
    print(f"DEBUG_POPULATE: first() took {t1-t0:.4f}s, first={first}")
    if first is not None:
        return
    sources = load_all_sources()
    for src, records in sources.items():
        dict_recs = records_to_dict_list(records)
        for r in dict_recs:
            dt = r.get("event_time") or r.get("settlement_date")
            try:
                dt_obj = datetime.fromisoformat(dt) if dt else datetime.utcnow()
            except:
                dt_obj = datetime.utcnow()
                
            tx = Transaction(
                canonical_id=r.get("canonical_id"),
                source=r.get("source", src),
                source_record_id=r.get("source_record_id") or r.get("canonical_id"),
                amount_minor=int(r.get("amount_minor", 0)),
                event_time=dt_obj,
                event_type=r.get("event_type") or "UNKNOWN",
                direction=r.get("direction") or "UNKNOWN",
                status=r.get("status") or "UNKNOWN",
                payment_id=r.get("payment_id"),
                order_id=r.get("order_id"),
                settlement_id=r.get("settlement_id"),
                utr=r.get("utr"),
                metadata_=r
            )
            db.add(tx)
            
            # Post to double-entry ledger
            process_financial_event_sync(
                db=db,
                event_type=tx.event_type,
                direction=tx.direction,
                amount_minor=tx.amount_minor,
                reference=tx.canonical_id,
                description=f"Transaction {tx.canonical_id}"
            )
    db.commit()

import time

@router.get("")
async def list_transactions(
    source: str = "",
    status: str = "",
    search: str = "",
    page: int = 1,
    page_size: int = 50,
):
    db = SyncSessionLocal()
    try:
        _populate_transactions_if_empty(db)
        
        query = db.query(Transaction)
        if source:
            query = query.filter(Transaction.source == source)
        if status:
            query = query.filter(Transaction.status == status)
        if search:
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Transaction.canonical_id.ilike(f"%{search}%"),
                    Transaction.payment_id.ilike(f"%{search}%"),
                    Transaction.order_id.ilike(f"%{search}%"),
                    Transaction.settlement_id.ilike(f"%{search}%"),
                    Transaction.utr.ilike(f"%{search}%")
                )
            )
            
        total = query.count()
        start = (page - 1) * page_size
        records = query.order_by(Transaction.event_time.desc()).offset(start).limit(page_size).all()
        
        res = []
        for r in records:
            d = {
                "canonical_id": r.canonical_id,
                "source": r.source,
                "source_record_id": r.source_record_id,
                "amount_minor": r.amount_minor,
                "currency": r.currency,
                "event_time": r.event_time.isoformat() if r.event_time else None,
                "event_type": r.event_type,
                "direction": r.direction,
                "status": r.status,
                "utr": r.utr
            }
            res.append(d)
            
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "records": res,
        }
    finally:
        db.close()

@router.get("/{canonical_id}")
async def get_transaction(canonical_id: str):
    db = SyncSessionLocal()
    try:
        _populate_transactions_if_empty(db)
        tx = db.query(Transaction).filter(Transaction.canonical_id == canonical_id).first()
        if tx:
            return tx.metadata_
        raise HTTPException(status_code=404, detail=f"Transaction {canonical_id} not found")
    finally:
        db.close()

@router.get("/{canonical_id}/360")
async def get_transaction_360(canonical_id: str):
    db = SyncSessionLocal()
    try:
        _populate_transactions_if_empty(db)
        tx = db.query(Transaction).filter(Transaction.canonical_id == canonical_id).first()
        if not tx:
            raise HTTPException(status_code=404, detail=f"Transaction {canonical_id} not found")
            
        matches = db.query(Match).filter(
            (Match.left_transaction_id == canonical_id) | (Match.right_transaction_id == canonical_id)
        ).all()
        
        counterparts = []
        match_evidence = None
        
        for m in matches:
            other_id = m.right_transaction_id if m.left_transaction_id == canonical_id else m.left_transaction_id
            other_tx = db.query(Transaction).filter(Transaction.canonical_id == other_id).first()
            if other_tx:
                counterparts.append(other_tx.metadata_)
            
            if not match_evidence or m.probability > match_evidence.get("probability", 0):
                match_evidence = {
                    "decision": m.decision,
                    "probability": m.probability,
                    "reason_code": m.reason_code,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                }
                
        return {
            "base_record": tx.metadata_,
            "counterparts": counterparts,
            "match_evidence": match_evidence
        }
    finally:
        db.close()
