import re

with open("apps/api/routers/query_lab.py", "r") as f:
    content = f.read()

# Replace synchronous call with async call
content = content.replace(
    'response = client.models.generate_content(',
    'response = await client.aio.models.generate_content('
)

with open("apps/api/routers/query_lab.py", "w") as f:
    f.write(content)
