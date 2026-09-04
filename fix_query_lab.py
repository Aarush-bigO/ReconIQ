import re

with open("apps/web/app/query-lab/page.tsx", "r") as f:
    content = f.read()

# Replace animate-3d with empty or a simpler animation
content = content.replace('className="card animate-3d animate-3d"', 'className="card"')
content = content.replace('className="data-table animate-3d"', 'className="data-table"')

# Also, the loading state
content = content.replace('className="card animate-3d"', 'className="card"')

with open("apps/web/app/query-lab/page.tsx", "w") as f:
    f.write(content)
