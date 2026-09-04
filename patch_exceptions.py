import re

with open("apps/api/routers/exceptions_router.py", "r") as f:
    content = f.read()

# Make the explain endpoint run in a threadpool
new_endpoint = """@router.post("/{exception_id}/explain")
async def explain_exception_endpoint(exception_id: str):
    from fastapi.concurrency import run_in_threadpool
    db = SyncSessionLocal()
    try:
        if exception_id.startswith("EXC_"):
            db_exc = db.query(ExceptionRecord).filter(ExceptionRecord.exception_id == exception_id).first()
            if not db_exc:
                raise HTTPException(status_code=404, detail="Exception not found")
            exc_dict = {
                "exception_id": db_exc.exception_id,
                "reason_code": db_exc.reason_code,
                "severity": db_exc.severity,
                "record_id": db_exc.record_id,
                "evidence": db_exc.evidence
            }
            output, source = await run_in_threadpool(explain_exception, exc_dict, api_key=settings.gemini_api_key, model=settings.gemini_model)
            return {"explanation": output.explanation, "action_plan": output.action_plan, "source": source}
        
        # Legacy mock fallback
        import json
        with open(str(MOCK_EXCEPTIONS_FILE), "r") as f:
            data = json.load(f)
        legacy = next((e for e in data if e["id"] == exception_id), None)
        if not legacy:
            raise HTTPException(status_code=404, detail="Exception not found")
            
        output, source = await run_in_threadpool(explain_exception, legacy, api_key=settings.gemini_api_key, model=settings.gemini_model)
        return {"explanation": output.explanation, "action_plan": output.action_plan, "source": source}
    finally:
        db.close()
"""

# Replace the existing endpoint
content = re.sub(r'@router\.post\("/\{exception_id\}/explain"\)[\s\S]*?finally:\n\s*db\.close\(\)', new_endpoint, content)

with open("apps/api/routers/exceptions_router.py", "w") as f:
    f.write(content)
