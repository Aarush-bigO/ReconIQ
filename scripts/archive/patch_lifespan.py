import re

with open("apps/api/main.py", "r") as f:
    content = f.read()

lifespan_code = """
@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Application startup/shutdown lifecycle.\"\"\"
    from ingestion.loaders import get_payment_provider
    from exceptions.manager import get_exception_queue, ExceptionRecord as MemExceptionRecord, ExceptionSeverity
    from database.session import SyncSessionLocal
    from database.models import ExceptionRecord as DBExceptionRecord
    
    provider = get_payment_provider()
    
    print("🚀 ReconIQ Enterprise starting up...")
    print(f"   Environment: {settings.app_env}")
    print(f"   Provider: {provider.get_provider_name()}")
    print(f"   AI Explanation: {'Gemini' if settings.gemini_api_key else 'Deterministic fallback'}")
    
    # ── God Mode Data Auto-Loader ──
    try:
        session = SyncSessionLocal()
        db_exceptions = session.query(DBExceptionRecord).all()
        if db_exceptions:
            print(f"🔥 God Mode: Auto-loading {len(db_exceptions)} exceptions into memory queue...")
            queue = get_exception_queue()
            for db_ex in db_exceptions:
                try:
                    severity = ExceptionSeverity(db_ex.severity)
                except:
                    severity = ExceptionSeverity.MEDIUM
                
                # Fetch amount from transaction if possible, or mock
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
        session.close()
    except Exception as e:
        print(f"God Mode Loader failed: {e}")
        
    yield
    print("👋 ReconIQ Enterprise shutting down...")
"""

# Replace the lifespan block
content = re.sub(
    r'@asynccontextmanager\nasync def lifespan\(app: FastAPI\):.*?yield\n    print\("👋 ReconIQ Enterprise shutting down..."\)',
    lifespan_code.strip(),
    content,
    flags=re.DOTALL
)

with open("apps/api/main.py", "w") as f:
    f.write(content)

print("Patched lifespan in main.py")
