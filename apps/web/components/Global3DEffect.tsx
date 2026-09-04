"use client";
import { useEffect } from "react";

export default function Global3DEffect() {
  useEffect(() => {
    if (typeof window === "undefined" || window.matchMedia("(hover: none)").matches) return;

    // Apply to every major interactive/content container globally
    const SELECTORS = '.card, .kpi-card, .btn-primary, .btn-secondary, .metric-box, table tbody tr, .alert-box, .stat-box, .nav-item, .docs-sidebar a';

    const handleMouseMove = (e: MouseEvent) => {
      const el = e.currentTarget as HTMLElement;
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      // Calculate rotation (max 6 degrees for smooth elegance)
      const rotateX = ((y - centerY) / centerY) * -6;
      const rotateY = ((x - centerX) / centerX) * 6;
      
      el.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
      el.style.transition = 'transform 0.1s ease-out, box-shadow 0.1s ease-out';
      
      // Dynamic glowing drop shadow pointing away from mouse
      const shadowX = (x - centerX) / 10 * -1;
      const shadowY = (y - centerY) / 10 * -1;
      
      if (el.classList.contains('card') || el.classList.contains('kpi-card') || el.tagName === 'TR') {
          el.style.boxShadow = `${shadowX}px ${shadowY}px 40px rgba(45,104,254,0.15), 0 10px 20px rgba(0,0,0,0.05)`;
          el.style.zIndex = '50';
      }
    };

    const handleMouseLeave = (e: MouseEvent) => {
      const el = e.currentTarget as HTMLElement;
      el.style.transform = '';
      el.style.boxShadow = '';
      el.style.zIndex = '';
      el.style.transition = 'transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)';
    };

    const attachListeners = () => {
      document.querySelectorAll(SELECTORS).forEach((el: any) => {
        if (!el.dataset.has3dAttached) {
          el.addEventListener('mousemove', handleMouseMove);
          el.addEventListener('mouseleave', handleMouseLeave);
          el.dataset.has3dAttached = 'true';
          el.style.willChange = 'transform, box-shadow';
        }
      });
    };

    attachListeners();

    // Re-run observer when React modifies the DOM (like navigating pages or opening modals)
    const observer = new MutationObserver(() => attachListeners());
    observer.observe(document.body, { childList: true, subtree: true });

    return () => {
      observer.disconnect();
      document.querySelectorAll(SELECTORS).forEach((el: any) => {
        el.removeEventListener('mousemove', handleMouseMove);
        el.removeEventListener('mouseleave', handleMouseLeave);
        delete el.dataset.has3dAttached;
      });
    };
  }, []);

  return null;
}
