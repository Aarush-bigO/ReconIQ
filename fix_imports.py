with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

content = content.replace('import CustomCursor from "@/components/CustomCursor";\nimport Global3DEffect from "@/components/Global3DEffect"; from "@/components/CustomCursor";', 'import CustomCursor from "@/components/CustomCursor";\nimport Global3DEffect from "@/components/Global3DEffect";')

with open("apps/web/components/LayoutBody.tsx", "w") as f:
    f.write(content)
