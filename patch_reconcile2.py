import re

with open("apps/api/routers/reconcile.py", "r") as f:
    content = f.read()

content = content.replace("m.left_record_id", "m.left_id")
content = content.replace("m.right_record_id", "m.right_id")

with open("apps/api/routers/reconcile.py", "w") as f:
    f.write(content)
