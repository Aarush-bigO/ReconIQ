"""
ReconIQ Enterprise — Health & System Status Router
"""
from datetime import datetime
from fastapi import APIRouter
from apps.api.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@router.get("/system/status")
async def system_status():
    return {
        "api": {"status": "HEALTHY"},
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
