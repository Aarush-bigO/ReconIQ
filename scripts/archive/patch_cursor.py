import re

with open("apps/web/components/CustomCursor.tsx", "r") as f:
    content = f.read()

# Replace the animate block for the ring
new_animate = """animate={{
          scale: isHovering ? 1.4 : 1,
          borderWidth: isHovering ? "2px" : "1px",
          backgroundColor: "transparent",
        }}"""

content = re.sub(
    r'animate=\{\{\s*scale: isHovering \? [0-9\.]+ : 1,\s*borderWidth: isHovering \? "[^"]+" : "1px",\s*backgroundColor: isHovering \? "[^"]+" : "rgba\(255, 255, 255, 0\)",\s*\}\}',
    new_animate,
    content
)

with open("apps/web/components/CustomCursor.tsx", "w") as f:
    f.write(content)

print("Patched Custom Cursor")
