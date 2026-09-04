with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

content = content.replace("window.location.href = `/transactions?search=${encodeURIComponent(searchQuery.trim())}`);", "window.location.href = `/transactions?search=${encodeURIComponent(searchQuery.trim())}`;")

with open("apps/web/components/LayoutBody.tsx", "w") as f:
    f.write(content)
