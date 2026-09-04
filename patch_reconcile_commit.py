import re

with open("apps/api/routers/reconcile.py", "r") as f:
    content = f.read()

new_block = """        db_run = ReconciliationRun(
            run_id=run_id,
            started_at=output.started_at,
            completed_at=output.completed_at,
            threshold=req.auto_match_threshold,
            records_processed=output.records_processed,
            auto_matched=output.auto_matched,
            manual_review=output.manual_review_count,
            unresolved=output.unresolved_count,
            match_rate=output.match_rate,
            reconciled_value_minor=reconciled_value,
            processing_ms=output.processing_ms,
            status="COMPLETED"
        )
        db.add(db_run)
        db.commit()  # Commit the run summary first!

        # Now try to insert the matches. If it fails due to FK/Unique, ignore.
        existing_matches = db.query(Match.left_transaction_id, Match.right_transaction_id).all()
        existing_set = set((m[0], m[1]) for m in existing_matches)

        for m in output.matches:
            if (m.left_id, m.right_id) in existing_set:
                continue
                
            db.add(
                Match(
                    run_id=run_id,
                    left_transaction_id=m.left_id,
                    right_transaction_id=m.right_id,
                    decision=m.decision,
                    probability=m.probability,
                    reason_code=m.reason_code,
                    match_metadata={"splink_score": m.probability}
                )
            )
            
        try:
            db.commit()
        except Exception as e:
            db.rollback()
"""

content = re.sub(r'        db_run = ReconciliationRun\([\s\S]*?db\.commit\(\)', new_block, content)

with open("apps/api/routers/reconcile.py", "w") as f:
    f.write(content)
