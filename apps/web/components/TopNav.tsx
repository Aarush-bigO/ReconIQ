"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react";

/* ── Dashboard navigation items ──────────────────────────── */
const primaryNav = [
  { href: "/dashboard", label: "Overview", icon: "⬡" },
  { href: "/reconciliation", label: "Reconciliation", icon: "⚡" },
  { href: "/transactions", label: "Transactions", icon: "⇄" },
  { href: "/ledger", label: "Ledger", icon: "📖" },
  { href: "/controls", label: "Controls", icon: "☑" },
];

const moreNav = [
  { href: "/settlements", label: "Settlements", icon: "₹" },
  { href: "/exceptions", label: "Exceptions", icon: "⚠" },
  { href: "/period-close", label: "Period Close", icon: "🔒" },
  { href: "/audit", label: "Audit Trail", icon: "🔐" },
  { href: "/data-quality", label: "Data Quality", icon: "◎" },
  { href: "/query-lab", label: "Query Lab", icon: "🔍" },
  { href: "/reports", label: "Reports", icon: "📄" },
  { href: "/evaluation", label: "Evaluation Lab", icon: "◈" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

/* ── Landing navigation items ────────────────────────────── */
const landingLinks = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How It Works" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/reconciliation", label: "Reconciliation" },
];

export default function TopNav() {
  const pathname = usePathname();
  const router = useRouter();
  const isLanding = pathname === "/";
  const [moreOpen, setMoreOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) {
        setMoreOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Track scroll for landing nav
  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handler, { passive: true });
    handler();
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const isMoreActive = moreNav.some(
    (item) => pathname.startsWith(item.href) && item.href !== "/"
  );

  /* ═══════════════════════════════════════════════════════════
     LANDING NAV — Clean white Razorpay-style
     ═══════════════════════════════════════════════════════════ */
  if (isLanding) {
    return (
      <nav className={`landing-nav ${scrolled ? "scrolled" : ""}`}>
        <div className="landing-nav-inner">
          {/* Logo */}
          <Link
            href="/"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              textDecoration: "none",
            }}
          >
            <div
              style={{
                width: 34,
                height: 34,
                borderRadius: 10,
                background: "linear-gradient(135deg, #0037ff, #00d67d)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 15,
                fontWeight: 800,
                color: "#fff",
                boxShadow: "0 2px 12px rgba(0, 55, 255, 0.25)",
              }}
            >
              R
            </div>
            <div>
              <div
                style={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: "#1a1a2e",
                  letterSpacing: "0.01em",
                  lineHeight: 1.1,
                }}
              >
                ReconIQ
              </div>
              <div
                style={{
                  fontSize: 8,
                  color: "#0037ff",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                }}
              >
                Enterprise
              </div>
            </div>
          </Link>

          {/* Center Links */}
          <div className="landing-nav-links">
            {landingLinks.map((item) => (
              <Link key={item.href} href={item.href} className="landing-nav-link">
                {item.label}
              </Link>
            ))}
          </div>

          {/* Right CTA */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Link
              href="/dashboard"
              style={{
                padding: "8px 18px",
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 500,
                color: "#575757",
                textDecoration: "none",
                border: "1px solid #e5e5e5",
                transition: "all 0.2s ease",
              }}
            >
              Login
            </Link>
            <Link href="/dashboard" className="btn-landing-primary" style={{ padding: "9px 22px", fontSize: 13 }}>
              Get Started
              <span style={{ fontSize: 14 }}>→</span>
            </Link>
          </div>
        </div>
      </nav>
    );
  }

  /* ═══════════════════════════════════════════════════════════
     DASHBOARD NAV — Dark glass (existing)
     ═══════════════════════════════════════════════════════════ */
  return (
    <nav
      className="glass-nav"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        boxShadow: "0 4px 30px rgba(0,0,0,0.4)",
      }}
    >
      <div
        style={{
          maxWidth: 1200,
          margin: "0 auto",
          padding: "0 32px",
          height: 64,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            textDecoration: "none",
          }}
        >
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 10,
              background: "linear-gradient(135deg, #22d3ee, #a855f7)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 15,
              fontWeight: 800,
              color: "#fff",
              boxShadow: "0 0 18px rgba(34, 211, 238, 0.4)",
            }}
          >
            R
          </div>
          <div>
            <div
              style={{
                fontSize: 14,
                fontWeight: 700,
                color: "#fff",
                letterSpacing: "0.02em",
                lineHeight: 1.1,
              }}
            >
              ReconIQ
            </div>
            <div
              style={{
                fontSize: 8,
                color: "#22d3ee",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
              }}
            >
              Enterprise
            </div>
          </div>
        </Link>

        {/* Navigation Links */}
        <div style={{ display: "flex", alignItems: "center", gap: 2 }}>
          {primaryNav.map((item) => {
            const isActive =
              item.href === "/dashboard"
                ? pathname === "/dashboard"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  position: "relative",
                  padding: "8px 14px",
                  borderRadius: 99,
                  fontSize: 13,
                  fontWeight: isActive ? 600 : 500,
                  textDecoration: "none",
                  transition: "all 0.3s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  color: isActive ? "#fff" : "#8b9cc0",
                  background: isActive ? "rgba(255,255,255,0.08)" : "transparent",
                  boxShadow: isActive
                    ? "inset 0 0 0 1px rgba(255,255,255,0.12)"
                    : "none",
                }}
              >
                <span style={{ fontSize: 14 }}>{item.icon}</span>
                <span>{item.label}</span>
                {isActive && (
                  <div
                    style={{
                      position: "absolute",
                      bottom: -1,
                      left: "50%",
                      transform: "translateX(-50%)",
                      width: 24,
                      height: 2,
                      background: "#22d3ee",
                      borderRadius: "2px 2px 0 0",
                      boxShadow: "0 -2px 10px rgba(34, 211, 238, 0.8)",
                    }}
                  />
                )}
              </Link>
            );
          })}

          {/* AI Control Room — highlighted */}
          <Link
            href="/ai-control-room"
            style={{
              position: "relative",
              padding: "8px 14px",
              borderRadius: 99,
              fontSize: 13,
              fontWeight: pathname === "/ai-control-room" ? 600 : 500,
              textDecoration: "none",
              transition: "all 0.3s ease",
              display: "flex",
              alignItems: "center",
              gap: 6,
              color:
                pathname === "/ai-control-room" ? "#fff" : "#22d3ee",
              background:
                pathname === "/ai-control-room"
                  ? "rgba(34, 211, 238, 0.1)"
                  : "transparent",
              filter: "drop-shadow(0 0 6px rgba(34, 211, 238, 0.3))",
            }}
          >
            <span style={{ fontSize: 14 }}>✦</span>
            <span>AI</span>
          </Link>

          {/* More Dropdown */}
          <div ref={moreRef} style={{ position: "relative" }}>
            <button
              onClick={() => setMoreOpen(!moreOpen)}
              style={{
                padding: "8px 14px",
                borderRadius: 99,
                fontSize: 13,
                fontWeight: 500,
                background: isMoreActive
                  ? "rgba(255,255,255,0.08)"
                  : "transparent",
                color: isMoreActive ? "#fff" : "#8b9cc0",
                border: "none",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 6,
                transition: "all 0.2s ease",
              }}
            >
              <span>More</span>
              <span
                style={{
                  fontSize: 10,
                  transition: "transform 0.2s ease",
                  transform: moreOpen ? "rotate(180deg)" : "rotate(0)",
                }}
              >
                ▼
              </span>
            </button>

            {moreOpen && (
              <div
                style={{
                  position: "absolute",
                  top: "calc(100% + 8px)",
                  right: 0,
                  width: 220,
                  background: "rgba(12, 17, 30, 0.95)",
                  backdropFilter: "blur(20px)",
                  WebkitBackdropFilter: "blur(20px)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 16,
                  padding: 8,
                  boxShadow:
                    "0 20px 60px -12px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.03)",
                  animation: "fadeIn 0.2s ease",
                }}
              >
                {moreNav.map((item) => {
                  const isActive =
                    pathname.startsWith(item.href) && item.href !== "/";
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMoreOpen(false)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: "10px 14px",
                        borderRadius: 10,
                        fontSize: 13,
                        fontWeight: isActive ? 600 : 400,
                        textDecoration: "none",
                        color: isActive ? "#fff" : "#8b9cc0",
                        background: isActive
                          ? "rgba(34, 211, 238, 0.1)"
                          : "transparent",
                        transition: "all 0.2s ease",
                      }}
                    >
                      <span
                        style={{
                          fontSize: 15,
                          width: 20,
                          textAlign: "center",
                        }}
                      >
                        {item.icon}
                      </span>
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Section */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {/* Search */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              background: "rgba(255,255,255,0.04)",
              border: `1px solid ${
                searchFocused
                  ? "rgba(34, 211, 238, 0.3)"
                  : "rgba(255,255,255,0.06)"
              }`,
              borderRadius: 99,
              padding: "6px 14px",
              transition: "all 0.3s ease",
              boxShadow: searchFocused
                ? "0 0 20px rgba(34, 211, 238, 0.1)"
                : "none",
            }}
          >
            <span style={{ fontSize: 13, color: "#4a5580", marginRight: 8 }}>
              🔍
            </span>
            <input
              type="text"
              placeholder="Search PAY, UTR..."
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  router.push(`/transactions?search=${encodeURIComponent(e.currentTarget.value)}`);
                }
              }}
              style={{
                background: "transparent",
                border: "none",
                outline: "none",
                fontSize: 12,
                color: "#fff",
                width: searchFocused ? 160 : 100,
                transition: "width 0.3s ease",
              }}
            />
          </div>

          {/* User */}
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "rgba(255,255,255,0.08)",
              border: "1px solid rgba(255,255,255,0.12)",
              cursor: "pointer",
              transition: "all 0.2s ease",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 12,
              fontWeight: 700,
              color: "#22d3ee",
              letterSpacing: "0.02em",
            }}
          >
            A
          </div>
        </div>
      </div>

      {/* Animated fadeIn for dropdown */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </nav>
  );
}
