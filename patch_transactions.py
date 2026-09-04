import re

with open("apps/web/app/transactions/page.tsx", "r") as f:
    content = f.read()

# Add useSearchParams
content = content.replace('import { useState, useEffect } from "react";', 'import { useState, useEffect, Suspense } from "react";\nimport { useSearchParams } from "next/navigation";')

# We need to wrap it in a suspense boundary or just use a child component if we use useSearchParams
# Since it's a hackathon, we can just use `window.location.search` instead of `useSearchParams` to avoid Suspense issues in Next.js 13+ client components.
# Let's check what it uses. It's client-side, so we can just read URLSearchParams(window.location.search).
content = content.replace(
    'const [source, setSource] = useState("All");',
    'const [source, setSource] = useState("All");\n  const [search, setSearch] = useState(typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("search") || "" : "");'
)

content = content.replace(
    'api.listTransactions({ source: source === "All" ? "" : source })',
    'api.listTransactions({ source: source === "All" ? "" : source, search })'
)

content = content.replace(
    '}, [source]);',
    '}, [source, search]);'
)

with open("apps/web/app/transactions/page.tsx", "w") as f:
    f.write(content)
