import re

with open("apps/api/routers/reconcile.py", "r") as f:
    content = f.read()

new_logic = """        # Query existing matches to avoid UniqueViolation
        existing_matches = db.query(Match.left_transaction_id, Match.right_transaction_id).all()
        existing_set = set((m[0], m[1]) for m in existing_matches)

        for m in output.matches:
            if (m.left_record_id, m.right_record_id) in existing_set:
                continue"""

content = re.sub(r'        for m in output\.matches:', new_logic, content)

with open("apps/api/routers/reconcile.py", "w") as f:
    f.write(content)
