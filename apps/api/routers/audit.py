"""
ReconIQ Enterprise — Audit Trail Router
=========================================
Hardened with OpenFang-inspired HMAC signing and chain export/verification.
"""
from datetime import datetime

from fastapi import APIRouter

from audit.audit_log import get_chain, AuditChain
from database.session import SyncSessionLocal

router = APIRouter()


@router.get("")
async def get_audit_trail(limit: int = 100):
    """Get recent audit events with chain integrity status."""
    db = SyncSessionLocal()
    chain = AuditChain(db_session=db)
    events = chain.get_events()
    is_valid, broken_at = chain.verify()
    db.close()

    return {
        "total": chain.event_count(),
        "events": events[-limit:],
        "last_hash": chain.last_hash()[:32] + "...",
        "chain_valid": is_valid,
        "broken_at_index": broken_at,
    }


@router.get("/verify")
async def verify_audit_chain():
    """Verify the complete audit chain integrity (hash chain + HMAC)."""
    db = SyncSessionLocal()
    chain = AuditChain(db_session=db)
    is_valid, broken_at = chain.verify()
    db.close()
    return {
        "status": "VERIFIED" if is_valid else "TAMPERED",
        "valid": is_valid,
        "event_count": chain.event_count(),
        "broken_at_index": broken_at,
        "verified_at": datetime.utcnow().isoformat(),
        "message": "Audit chain integrity verified. All hash chains and HMAC signatures valid." if is_valid
                   else f"⚠️ CRITICAL: Chain tampered at event index {broken_at}. Do not treat affected records as trusted.",
    }


@router.get("/export")
async def export_audit_chain():
    """Export the entire audit chain as JSON-LD for external verification."""
    db = SyncSessionLocal()
    chain = AuditChain(db_session=db)
    res = chain.export_chain()
    db.close()
    return res


@router.get("/statistics")
async def audit_statistics():
    """Get audit chain statistics including action distribution."""
    db = SyncSessionLocal()
    chain = AuditChain(db_session=db)
    res = chain.statistics()
    db.close()
    return res
