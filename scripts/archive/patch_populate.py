import re

with open("apps/api/routers/transactions.py", "r") as f:
    content = f.read()

new_pop = """def _populate_transactions_if_empty(db):
    import time
    t0 = time.time()
    first = db.query(Transaction).first()
    t1 = time.time()
    print(f"DEBUG_POPULATE: first() took {t1-t0:.4f}s, first={first}")
    if first is not None:
        return
"""

content = re.sub(
    r'def _populate_transactions_if_empty\(db\):\n    if db\.query\(Transaction\)\.first\(\) is not None:\n        return\n',
    new_pop,
    content
)

with open("apps/api/routers/transactions.py", "w") as f:
    f.write(content)
