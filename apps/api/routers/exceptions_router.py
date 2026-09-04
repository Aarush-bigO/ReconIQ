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
