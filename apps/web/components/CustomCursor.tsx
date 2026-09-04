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
          scale: isHovering ? 1.4 : 1,
          borderWidth: isHovering ? "2px" : "1px",
          backgroundColor: "transparent",
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
