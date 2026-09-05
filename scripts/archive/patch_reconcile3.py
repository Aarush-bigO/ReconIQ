import re

with open("apps/api/routers/reconcile.py", "r") as f:
    content = f.read()

content = content.replace('match_metadata={"splink_score": m.probability}', 'evidence={"splink_score": m.probability}')

with open("apps/api/routers/reconcile.py", "w") as f:
    f.write(content)
