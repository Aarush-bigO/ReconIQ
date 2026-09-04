import re

with open("apps/web/app/transactions/page.tsx", "r") as f:
    content = f.read()

# Replace the useState
old_state = 'const [search, setSearch] = useState(typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("search") || "" : "");'
new_state = 'const [search, setSearch] = useState("");\n  useEffect(() => {\n    if (typeof window !== "undefined") {\n      const params = new URLSearchParams(window.location.search);\n      setSearch(params.get("search") || "");\n    }\n  }, []);'

content = content.replace(old_state, new_state)

with open("apps/web/app/transactions/page.tsx", "w") as f:
    f.write(content)
