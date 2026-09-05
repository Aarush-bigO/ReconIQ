"""
ReconIQ Enterprise — Health & System Status Router
"""
import time
from datetime import datetime, timezone
from fastapi import APIRouter
from apps.api.config import get_settings
from database.session import SyncSessionLocal
from database.models import Transaction, Settlement, ExceptionRecord, AuditEvent, Match

router = APIRouter()
settings = get_settings()
_startup_time = time.time()


@router.get("/health")
async def health():
    """Lightweight liveness probe."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": settings.app_env,
        "uptime_seconds": round(time.time() - _startup_time, 1),
    }


@router.get("/system/status")
async def system_status():
    """Detailed readiness probe with database connectivity and record counts."""
    db_status = "HEALTHY"
    record_counts = {}
    try:
        db = SyncSessionLocal()
        record_counts = {
            "transactions": db.query(Transaction).count(),
            "settlements": db.query(Settlement).count(),
            "exceptions": db.query(ExceptionRecord).count(),
            "matches": db.query(Match).count(),
            "audit_events": db.query(AuditEvent).count(),
        }
        db.close()
    except Exception as e:
        db_status = f"UNHEALTHY: {str(e)}"
        record_counts = {"error": str(e)}

    return {
        "api": {"status": "HEALTHY", "uptime_seconds": round(time.time() - _startup_time, 1)},
        "database": {"status": db_status, "record_counts": record_counts},
        "razorpay": {
            "status": "CONNECTED" if settings.razorpay_key_id else "NOT_CONFIGURED",
            "mode": "Test Mode" if settings.razorpay_key_id else "Demo Mode (synthetic data)",
        },
        "llm": {
            "status": "AVAILABLE" if settings.gemini_api_key else "FALLBACK",
            "mode": "Gemini" if settings.gemini_api_key else "Deterministic Fallback",
        },
        "thresholds": {
            "auto_match": settings.auto_match_threshold,
            "review": settings.review_threshold,
            "date_tolerance_days": settings.date_tolerance_days,
            "amount_tolerance_minor": settings.amount_tolerance_minor,
        },
    }
