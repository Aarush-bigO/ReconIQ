import re

with open("apps/web/app/globals.css", "r") as f:
    content = f.read()

new_css = """@keyframes fadeInUp3D {
  from { opacity: 0; transform: perspective(1000px) rotateX(-8deg) translateY(40px) scale(0.96); }
  to { opacity: 1; transform: perspective(1000px) rotateX(0) translateY(0) scale(1); }
}

.animate-3d {
  animation: fadeInUp3D 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}
"""

content = re.sub(r'\.animate-3d \{[\s\S]*?\.animate-3d\.in-view \{[\s\S]*?\}', new_css, content)

with open("apps/web/app/globals.css", "w") as f:
    f.write(content)
