import os

print("1. Creating CustomCursor component...")
cursor_code = """\
"use client";
import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

export default function CustomCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const dotRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  useEffect(() => {
    const cursor = cursorRef.current;
    const dot = dotRef.current;
    if (!cursor || !dot) return;

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let cursorX = mouseX;
    let cursorY = mouseY;
    let isVisible = false;

    const onMouseMove = (e: MouseEvent) => {
      if (!isVisible) {
        cursor.style.opacity = "1";
        dot.style.opacity = "1";
        isVisible = true;
      }
      mouseX = e.clientX;
      mouseY = e.clientY;
      // Use requestAnimationFrame for the dot to prevent micro-stutters
      requestAnimationFrame(() => {
        if (dotRef.current) {
            dotRef.current.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
        }
      });
    };

    let animationFrame: number;
    const loop = () => {
      cursorX += (mouseX - cursorX) * 0.15;
      cursorY += (mouseY - cursorY) * 0.15;
      if (cursorRef.current) {
        cursorRef.current.style.transform = `translate3d(${cursorX}px, ${cursorY}px, 0)`;
      }
      animationFrame = requestAnimationFrame(loop);
    };

    window.addEventListener("mousemove", onMouseMove);
    animationFrame = requestAnimationFrame(loop);

    // Hover states
    const addHover = () => {
      if (cursorRef.current) cursorRef.current.classList.add("hovering");
      if (dotRef.current) dotRef.current.classList.add("hovering");
    };
    const removeHover = () => {
      if (cursorRef.current) cursorRef.current.classList.remove("hovering");
      if (dotRef.current) dotRef.current.classList.remove("hovering");
    };

    const attachHoverListeners = () => {
      const interactables = document.querySelectorAll("a, button, input, select, textarea, .cursor-pointer, [style*='cursor: pointer']");
      interactables.forEach((el) => {
        el.addEventListener("mouseenter", addHover);
        el.addEventListener("mouseleave", removeHover);
      });
    };

    attachHoverListeners();
    // Re-attach after a small delay to catch dynamically rendered elements
    const timeout = setTimeout(attachHoverListeners, 1000);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      cancelAnimationFrame(animationFrame);
      clearTimeout(timeout);
      const interactables = document.querySelectorAll("a, button, input, select, textarea, .cursor-pointer, [style*='cursor: pointer']");
      interactables.forEach((el) => {
        el.removeEventListener("mouseenter", addHover);
        el.removeEventListener("mouseleave", removeHover);
      });
    };
  }, [pathname]);

  return (
    <>
      <div ref={cursorRef} className="rr-cursor-ring" style={{ opacity: 0 }} />
      <div ref={dotRef} className="rr-cursor-dot" style={{ opacity: 0 }} />
    </>
  );
}
"""

with open("apps/web/components/CustomCursor.tsx", "w") as f:
    f.write(cursor_code)

print("2. Injecting CSS styles into globals.css...")
with open("apps/web/app/globals.css", "a") as f:
    f.write('''
/* ── Rolls-Royce Luxury Custom Cursor ── */
@media (pointer: fine) {
  body, a, button, div, span, p, h1, h2, h3, h4, h5, h6 {
    cursor: none !important;
  }
  input, textarea {
    cursor: none !important;
  }
}

.rr-cursor-ring {
  position: fixed;
  top: -16px;
  left: -16px;
  width: 32px;
  height: 32px;
  border: 1px solid #fff;
  border-radius: 50%;
  pointer-events: none;
  z-index: 99999;
  transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1), height 0.4s cubic-bezier(0.16, 1, 0.3, 1), top 0.4s cubic-bezier(0.16, 1, 0.3, 1), left 0.4s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.4s ease, opacity 0.5s ease;
  mix-blend-mode: difference;
}

.rr-cursor-dot {
  position: fixed;
  top: -3px;
  left: -3px;
  width: 6px;
  height: 6px;
  background-color: #fff;
  border-radius: 50%;
  pointer-events: none;
  z-index: 100000;
  mix-blend-mode: difference;
  transition: opacity 0.3s ease, transform 0.1s ease;
}

.rr-cursor-ring.hovering {
  width: 64px;
  height: 64px;
  top: -32px;
  left: -32px;
  background-color: #fff;
  border-color: transparent;
}

.rr-cursor-dot.hovering {
  opacity: 0;
}
''')

print("3. Injecting CustomCursor into LayoutBody.tsx...")
with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

if "CustomCursor" not in content:
    content = content.replace(
        'import TopNav from "@/components/TopNav";', 
        'import TopNav from "@/components/TopNav";\nimport CustomCursor from "@/components/CustomCursor";'
    )
    content = content.replace(
        '<body className="landing-mode">', 
        '<body className="landing-mode">\n      <CustomCursor />'
    )
    content = content.replace(
        '<body className="dashboard-mode" style={{ background: \'#F8FAFC\', minHeight: \'100vh\', display: \'flex\', flexDirection: \'column\' }}>', 
        '<body className="dashboard-mode" style={{ background: \'#F8FAFC\', minHeight: \'100vh\', display: \'flex\', flexDirection: \'column\' }}>\n      <CustomCursor />'
    )
    with open("apps/web/components/LayoutBody.tsx", "w") as f:
        f.write(content)

print("Rolls-Royce custom cursor successfully installed.")
