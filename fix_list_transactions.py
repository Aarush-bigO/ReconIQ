import re

with open("apps/api/routers/transactions.py", "r") as f:
    content = f.read()

new_list = """@router.get("")
async def list_transactions(
    source: str = "",
    status: str = "",
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
        db.close()"""

content = re.sub(r'@router\.get\(""\)\nasync def list_transactions\(.*?\n        "records": res,\n    \}', new_list, content, flags=re.DOTALL)

with open("apps/api/routers/transactions.py", "w") as f:
    f.write(content)
