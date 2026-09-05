"""
ReconIQ Enterprise — FastAPI Application
=========================================
Main entry point for the ReconIQ backend API.
"""
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.config import get_settings
from apps.api.routers import (
    ingestion,
    health,
    reconcile,
    transactions,
    exceptions_router,
    settlements,
    audit,
    reports,
    webhooks,
    evaluation,
    controls,
    period_close,
    query_lab,
    ledger,
    copilot,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    from ingestion.loaders import get_payment_provider
    from exceptions.manager import get_exception_queue, ExceptionRecord as MemExceptionRecord, ExceptionSeverity
    from database.session import SyncSessionLocal
    from database.models import ExceptionRecord as DBExceptionRecord, Settlement as DBSettlement
    from apps.api.routers.settlements import set_settlements, set_settlement_batches, set_settlement_recon_results
    
    provider = get_payment_provider()
    
    print("🚀 ReconIQ Enterprise starting up...")
    print(f"   Environment: {settings.app_env}")
    print(f"   Provider: {provider.get_provider_name()}")
    print(f"   AI Explanation: {'Gemini' if settings.gemini_api_key else 'Deterministic fallback'}")
    
    # ── God Mode Data Auto-Loader ──
    try:
        session = SyncSessionLocal()
        
        # Load Exceptions
        db_exceptions = session.query(DBExceptionRecord).all()
        if db_exceptions:
            print(f"🔥 God Mode: Auto-loading {len(db_exceptions)} exceptions into memory queue...")
            queue = get_exception_queue()
            for db_ex in db_exceptions:
                try:
                    severity = ExceptionSeverity(db_ex.severity)
                except:
                    severity = ExceptionSeverity.MEDIUM
                
                amount = 10000
                
                queue.add(MemExceptionRecord(
                    exception_id=db_ex.exception_id,
                    run_id=db_ex.run_id,
                    record_id=db_ex.transaction_id,
                    reason_code=db_ex.reason_code,
                    severity=severity,
                    amount_minor=amount,
                    currency="INR",
                    evidence_json=db_ex.evidence_json or {},
                    explanation=db_ex.ai_explanation or "",
                    recommended_action=db_ex.recommended_action or ""
                ))
                
        # Load Settlements
        db_settlements = session.query(DBSettlement).all()
        if db_settlements:
            print(f"🔥 God Mode: Auto-loading {len(db_settlements)} settlements into memory...")
            s_list = []
            recon_results = []
            for s in db_settlements:
                s_dict = {
                    "settlement_id": s.settlement_id,
                    "date": s.settlement_date.isoformat(),
                    "gross_minor": s.gross_minor,
                    "fees_minor": s.fees_minor,
                    "tax_minor": s.tax_minor,
                    "net_minor": s.net_minor,
                    "bank_credit_minor": s.bank_credit_minor,
                    "variance_minor": s.variance_minor,
                    "status": s.status,
                    "utr": s.utr
                }
                s_list.append(s_dict)
                recon_results.append({
                    "settlement_id": s.settlement_id,
                    "date": s.settlement_date.isoformat(),
                    "match_result": "EXACT_MATCH" if s.variance_minor == 0 else "FEE_DISCREPANCY",
                    "variance_minor": s.variance_minor
                })
            set_settlements(s_list)
            set_settlement_batches(s_list) # Just dual-load for UI compatibility
            set_settlement_recon_results(recon_results)
            
        session.close()
    except Exception as e:
        print(f"God Mode Loader failed: {e}")
        
    yield
    print("👋 ReconIQ Enterprise shutting down...")


app = FastAPI(
    title="ReconIQ Enterprise API",
    description="""
## AI Finance Control Center

ReconIQ Enterprise reconciles payment, settlement, ledger and bank records 
using probabilistic record linkage and deterministic financial policies.

**Core principle:** Deterministic systems decide. AI explains.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "message": "No financial state was modified.",
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["System"])
app.include_router(reconcile.router, prefix="/reconcile", tags=["Reconciliation"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(exceptions_router.router, prefix="/exceptions", tags=["Exceptions"])
app.include_router(settlements.router, prefix="/settlements", tags=["Settlements"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(controls.router, prefix="/controls", tags=["Controls"])
app.include_router(period_close.router, prefix="/period-close", tags=["Period Close"])
app.include_router(query_lab.router, prefix="/query-lab", tags=["Query Lab"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(evaluation.router, prefix="/evaluation", tags=["Evaluation"])
app.include_router(ledger.router, prefix="/ledger", tags=["Ledger"])
app.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])
app.include_router(copilot.router, prefix="/copilot", tags=["Copilot"])
