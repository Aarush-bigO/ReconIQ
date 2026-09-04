import re

with open("apps/api/routers/reconcile.py", "r") as f:
    content = f.read()

content = content.replace("async def run_reconciliation(", "def run_reconciliation(")

with open("apps/api/routers/reconcile.py", "w") as f:
    f.write(content)
