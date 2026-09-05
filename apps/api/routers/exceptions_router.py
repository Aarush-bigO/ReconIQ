"""
ReconIQ Enterprise — Exceptions Router
=========================================
Powered by the FTR-inspired exception management system.
Includes aging, SLA tracking, priority scoring, and operator assignment.
"""
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from apps.api.config import get_settings
from audit.audit_log import get_chain, AuditAction
from llm.explain import explain_exception
from exceptions.manager import (
    ExceptionRecord,
    ExceptionQueue,
    ExceptionSeverity,
    ExceptionStatus,
    ResolutionType,
    get_exception_queue,
)

router = APIRouter()
settings = get_settings()

# Legacy in-memory store (kept for backward compatibility)
from apps.api.services.ledger import draft_deduction_journal_entry_sync
from database.session import SyncSessionLocal
from database.models import AgenticCommunication

_exceptions: dict[str, Any] = {}


def set_exceptions(exceptions: list[dict]):
    """Populate both legacy store and new exception queue."""
    global _exceptions
    _exceptions = {e["exception_id"]: e for e in exceptions}

    # Also populate the new exception queue
    queue = get_exception_queue()
    for e in exceptions:
        severity_str = e.get("severity", "MEDIUM")
        try:
            severity = ExceptionSeverity(severity_str)
        except ValueError:
            severity = ExceptionSeverity.MEDIUM

        record = ExceptionRecord(
            exception_id=e["exception_id"],
            run_id=e.get("run_id", ""),
            record_id=e.get("record_id", e.get("transaction_id", "")),
            reason_code=e.get("reason_code", "UNCLASSIFIED"),
            severity=severity,
            amount_minor=int(e.get("amount_minor", 0)),
            currency=e.get("currency", "INR"),
            evidence_json=e.get("evidence_json", {}),
            explanation=e.get("explanation", ""),
            recommended_action=e.get("recommended_action", ""),
        )
        queue.add(record)

class ExceptionCreateRequest(BaseModel):
    exception_id: str
    run_id: str = ""
    record_id: str = ""
    reason_code: str
    severity: str = "MEDIUM"
    amount_minor: int = 0
    currency: str = "INR"
    evidence_json: dict = {}

@router.post("")
async def create_exception(req: ExceptionCreateRequest):
    queue = get_exception_queue()
    try:
        severity = ExceptionSeverity(req.severity)
    except ValueError:
        severity = ExceptionSeverity.MEDIUM

    record = ExceptionRecord(
        exception_id=req.exception_id,
        run_id=req.run_id,
        record_id=req.record_id,
        reason_code=req.reason_code,
        severity=severity,
        amount_minor=req.amount_minor,
        currency=req.currency,
        evidence_json=req.evidence_json,
    )

    if req.reason_code == "AMOUNT_MISMATCH" or req.amount_minor > 0:
        # If it's a short payment (amount > 0 often indicates short payment in this context)
        # or if reason code is AMOUNT_MISMATCH. The prompt says:
        # "if it's a short payment, automatically set deduction_category="BANK_FEE" (or randomly) and call draft_deduction_journal_entry_sync()"
        diff = req.evidence_json.get("difference", req.amount_minor)
        if diff > 0:
            record.deduction_category = "BANK_FEE"
            with SyncSessionLocal() as session:
                draft_deduction_journal_entry_sync(session, record, diff)

    queue.add(record)
    return record.to_dict()



@router.get("")
async def list_exceptions(
    status: str = "",
    severity: str = "",
    assigned_to: str = "",
    limit: int = 50,
    offset: int = 0,
):
    """List exceptions with filtering, sorted by priority."""
    queue = get_exception_queue()

    # Parse filters
    status_filter = None
    if status:
        try:
            status_filter = ExceptionStatus(status)
        except ValueError:
            pass

    severity_filter = None
    if severity:
        try:
            severity_filter = ExceptionSeverity(severity)
        except ValueError:
            pass

    items = queue.list_by_priority(
        status_filter=status_filter,
        severity_filter=severity_filter,
        assigned_to_filter=assigned_to or None,
        limit=limit,
        offset=offset,
    )

    return {
        "total": queue.count,
        "showing": len(items),
        "offset": offset,
        "exceptions": [e.to_dict() for e in items],
    }


@router.get("/summary")
async def exception_summary():
    """Get exception queue summary with SLA breach info."""
    queue = get_exception_queue()
    summary = queue.summary()
    breached = queue.sla_breached()
    summary["sla_breached_items"] = [e.to_dict() for e in breached[:10]]
    return summary


@router.get("/stats")
async def exception_stats():
    """Exception statistics from the database."""
    from database.session import SyncSessionLocal
    from database.models import ExceptionRecord as DBExceptionRecord
    from sqlalchemy import func
    db = SyncSessionLocal()
    try:
        total = db.query(DBExceptionRecord).count()
        by_severity = db.query(
            DBExceptionRecord.severity, func.count(DBExceptionRecord.id)
        ).group_by(DBExceptionRecord.severity).all()
        by_status = db.query(
            DBExceptionRecord.status, func.count(DBExceptionRecord.id)
        ).group_by(DBExceptionRecord.status).all()
        by_reason = db.query(
            DBExceptionRecord.reason_code, func.count(DBExceptionRecord.id)
        ).group_by(DBExceptionRecord.reason_code).all()
        return {
            "total_exceptions": total,
            "by_severity": {sev: count for sev, count in by_severity},
            "by_status": {status: count for status, count in by_status},
            "by_reason_code": {reason: count for reason, count in by_reason},
        }
    finally:
        db.close()


@router.get("/{exception_id}")
async def get_exception(exception_id: str):
    """Get a specific exception by ID."""
    queue = get_exception_queue()
    exc = queue.get(exception_id)
    if not exc:
        # Fallback to legacy store
        legacy = _exceptions.get(exception_id)
        if legacy:
            return legacy
        raise HTTPException(status_code=404, detail=f"Exception {exception_id} not found")
    return exc.to_dict()


class AssignRequest(BaseModel):
    assignee: str


@router.post("/{exception_id}/assign")
async def assign_exception(exception_id: str, req: AssignRequest):
    """Assign an exception to an operator."""
    queue = get_exception_queue()
    success = queue.assign(exception_id, req.assignee)
    if not success:
        raise HTTPException(status_code=404, detail=f"Exception {exception_id} not found")

    chain = get_chain()
    chain.record(
        run_id="", record_id=exception_id,
        action=AuditAction.EXCEPTION_REVIEWED,
        decision="ASSIGNED",
        extra={"assignee": req.assignee},
    )

    exc = queue.get(exception_id)
    return exc.to_dict() if exc else {"status": "assigned"}


class ReviewRequest(BaseModel):
    action: str  # resolve | escalate
    resolution_type: str = ""  # MANUAL_MATCH, FALSE_POSITIVE, etc.
    notes: str = ""
    resolved_by: str = ""


@router.post("/{exception_id}/review")
async def review_exception(exception_id: str, req: ReviewRequest):
    """Review an exception: resolve or escalate."""
    queue = get_exception_queue()
    exc = queue.get(exception_id)

    if not exc:
        raise HTTPException(status_code=404, detail=f"Exception {exception_id} not found")

    if req.action == "resolve":
        try:
            res_type = ResolutionType(req.resolution_type) if req.resolution_type else ResolutionType.OTHER
        except ValueError:
            res_type = ResolutionType.OTHER

        queue.resolve(
            exception_id,
            resolution_type=res_type,
            notes=req.notes,
            resolved_by=req.resolved_by,
        )
        audit_action = AuditAction.EXCEPTION_RESOLVED

    elif req.action == "escalate":
        exc.escalate(notes=req.notes)
        audit_action = AuditAction.EXCEPTION_ESCALATED

    else:
        exc.start_review()
        audit_action = AuditAction.EXCEPTION_REVIEWED

    chain = get_chain()
    chain.record(
        run_id=exc.run_id, record_id=exception_id,
        action=audit_action,
        decision=req.action,
        extra={"notes": req.notes},
    )

    return exc.to_dict()


@router.post("/{exception_id}/explain")
async def explain_exception_endpoint(exception_id: str):
    """Generate AI explanation for an exception."""
    queue = get_exception_queue()
    exc = queue.get(exception_id)

    if not exc:
        # Fallback to legacy
        legacy = _exceptions.get(exception_id)
        if not legacy:
            raise HTTPException(status_code=404, detail=f"Exception {exception_id} not found")

        output, source = explain_exception(legacy, api_key=settings.gemini_api_key, model=settings.gemini_model)
        return {
            "exception_id": exception_id,
            "explanation": output.explanation,
            "recommended_action": output.recommended_action,
            "source": source,
        }

    # Use the new exception record
    exc_dict = exc.to_dict()
    output, source = explain_exception(exc_dict, api_key=settings.gemini_api_key, model=settings.gemini_model)

    exc.explanation = output.explanation
    exc.recommended_action = output.recommended_action

    chain = get_chain()
    chain.record(
        run_id=exc.run_id, record_id=exception_id,
        action=AuditAction.EXPLANATION_GENERATED,
        extra={"source": source},
    )

    return {
        "exception_id": exception_id,
        "explanation": output.explanation,
        "recommended_action": output.recommended_action,
        "source": source,
    }

@router.post("/{exception_id}/outreach")
async def draft_outreach(exception_id: str):
    """Simulates Agentic AI drafting a Slack/Email message asking for info."""
    queue = get_exception_queue()
    exc = queue.get(exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    message_content = (
        f"Hi team,\n\n"
        f"We have an unresolved exception ({exception_id}) for amount {exc.amount_minor / 100} {exc.currency}. "
        f"Reason: {exc.reason_code}. Could you please provide context or missing details?\n\n"
        f"Thanks, ReconIQ AI"
    )

    with SyncSessionLocal() as session:
        comm = AgenticCommunication(
            exception_id=exception_id,
            message_content=message_content,
            status="PENDING"
        )
        session.add(comm)
        session.commit()
        session.refresh(comm)
        
        return {
            "status": "success",
            "communication_id": comm.id,
            "message": message_content
        }

class SimulateReplyRequest(BaseModel):
    reply: str

@router.post("/{exception_id}/simulate-reply")
async def simulate_reply(exception_id: str, req: SimulateReplyRequest):
    """A webhook where a human provides the requested info. Updates status to RESOLVED."""
    queue = get_exception_queue()
    exc = queue.get(exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    with SyncSessionLocal() as session:
        comm = session.query(AgenticCommunication).filter(
            AgenticCommunication.exception_id == exception_id,
            AgenticCommunication.status == "PENDING"
        ).first()
        
        if comm:
            comm.status = "RESOLVED"
            from datetime import timezone
            comm.resolved_at = datetime.now(timezone.utc)
            session.commit()
            
    # Parse reply and update ExceptionRecord
    exc.resolve(
        resolution_type=ResolutionType.MANUAL_MATCH, 
        notes=f"User reply: {req.reply}",
        resolved_by="Agentic AI via User"
    )
    
    return {"status": "success", "message": "Exception resolved based on user input."}

