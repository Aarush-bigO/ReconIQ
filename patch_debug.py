import re

with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

content = content.replace("const isLanding = pathname === \"/\";", "const isLanding = pathname === \"/\" || pathname === \"\";\n  console.log('LAYOUT PATHNAME:', pathname);")

with open("apps/web/components/LayoutBody.tsx", "w") as f:
    f.write(content)
