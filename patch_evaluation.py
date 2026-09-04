import re

with open("apps/api/routers/evaluation.py", "r") as f:
    content = f.read()

content = content.replace("async def run_evaluation():", "def run_evaluation():")

with open("apps/api/routers/evaluation.py", "w") as f:
    f.write(content)
