import re

with open("apps/api/routers/transactions.py", "r") as f:
    content = f.read()

# Fix get_transaction
new_get = """@router.get("/{canonical_id}")
async def get_transaction(canonical_id: str):
    db = SyncSessionLocal()
    try:
        _populate_transactions_if_empty(db)
        tx = db.query(Transaction).filter(Transaction.canonical_id == canonical_id).first()
        if tx:
            return tx.metadata_
        raise HTTPException(status_code=404, detail=f"Transaction {canonical_id} not found")
    finally:
        db.close()"""
content = re.sub(r'@router\.get\("/\{canonical_id\}"\)\nasync def get_transaction.*?\n    raise HTTPException.*?not found"\)', new_get, content, flags=re.DOTALL)


# Fix get_transaction_360
new_360 = """@router.get("/{canonical_id}/360")
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
        db.close()"""
content = re.sub(r'@router\.get\("/\{canonical_id\}/360"\)\nasync def get_transaction_360.*?\n    return \{\n        "base_record": tx\.metadata_,\n        "counterparts": counterparts,\n        "match_evidence": match_evidence\n    \}', new_360, content, flags=re.DOTALL)

with open("apps/api/routers/transactions.py", "w") as f:
    f.write(content)
