import os

print("1. Rewriting CustomCursor.tsx with framer-motion...")
cursor_code = """\
"use client";
import { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
import { usePathname } from "next/navigation";

export default function CustomCursor() {
  const [isHovering, setIsHovering] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const pathname = usePathname();

  const mouseX = useMotionValue(-100);
  const mouseY = useMotionValue(-100);

  // Rolls-Royce signature smooth spring physics
  const springConfig = { damping: 45, stiffness: 400, mass: 0.1 };
  const cursorX = useSpring(mouseX, springConfig);
  const cursorY = useSpring(mouseY, springConfig);

  useEffect(() => {
    const moveCursor = (e: MouseEvent) => {
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
      if (!isVisible) setIsVisible(true);
    };

    window.addEventListener("mousemove", moveCursor);

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName.toLowerCase() === "a" ||
        target.tagName.toLowerCase() === "button" ||
        target.closest("a") ||
        target.closest("button") ||
        target.closest(".cursor-pointer") ||
        target.closest("input")
      ) {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };

    window.addEventListener("mouseover", handleMouseOver);
    setIsHovering(false);

    return () => {
      window.removeEventListener("mousemove", moveCursor);
      window.removeEventListener("mouseover", handleMouseOver);
    };
  }, [mouseX, mouseY, isVisible, pathname]);

  return (
    <>
      <motion.div
        className="luxury-cursor-ring"
        style={{
          x: cursorX,
          y: cursorY,
          opacity: isVisible ? 1 : 0,
        }}
        animate={{
          scale: isHovering ? 1.6 : 1,
          borderWidth: isHovering ? "0px" : "1px",
          backgroundColor: isHovering ? "rgba(255, 255, 255, 1)" : "rgba(255, 255, 255, 0)",
        }}
        transition={{ type: "tween", ease: "easeOut", duration: 0.2 }}
      />
      <motion.div
        className="luxury-cursor-dot"
        style={{
          x: mouseX,
          y: mouseY,
          opacity: isVisible ? (isHovering ? 0 : 1) : 0,
        }}
        transition={{ type: "tween", ease: "easeOut", duration: 0.15 }}
      />
    </>
  );
}
"""
with open("apps/web/components/CustomCursor.tsx", "w") as f:
    f.write(cursor_code)

print("2. Cleaning old cursor CSS and applying new ones...")
css_path = 'apps/web/app/globals.css'
with open(css_path, 'r') as f:
    css_content = f.read()

# Strip out old cursor CSS
if "/* ── Rolls-Royce Luxury Custom Cursor ── */" in css_content:
    css_content = css_content.split("/* ── Rolls-Royce Luxury Custom Cursor ── */")[0]

new_css = """
/* ── Rolls-Royce Luxury Custom Cursor ── */
@media (pointer: fine) {
  body, a, button, div, span, p, h1, h2, h3, h4, h5, h6, input, textarea {
    cursor: none !important;
  }
}

.luxury-cursor-ring {
  position: fixed;
  top: -20px;
  left: -20px;
  width: 40px;
  height: 40px;
  border: 1px solid #ffffff;
  border-radius: 50%;
  pointer-events: none;
  z-index: 999999;
  mix-blend-mode: difference;
}

.luxury-cursor-dot {
  position: fixed;
  top: -3px;
  left: -3px;
  width: 6px;
  height: 6px;
  background-color: #ffffff;
  border-radius: 50%;
  pointer-events: none;
  z-index: 999999;
  mix-blend-mode: difference;
}
"""

with open(css_path, 'w') as f:
    f.write(css_content + new_css)

print("Done upgrading cursor.")
