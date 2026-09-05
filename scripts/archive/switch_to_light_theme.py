import os

print("Updating globals.css...")
css_path = 'apps/web/app/globals.css'
with open(css_path, 'r') as f:
    lines = f.readlines()
    
idx = 0
for i, line in enumerate(lines):
    if 'DASHBOARD MODE' in line:
        idx = i
        break
        
if idx > 0:
    new_css = lines[:idx-1]
    new_css.append('''
/* ═══════════════════════════════════════════════════════════════
   DASHBOARD MODE — Professional Light Theme (Razorpay Inspired)
   ═══════════════════════════════════════════════════════════════ */
:root {
  --bg-main: #F3F6F9;
  --card-bg: #FFFFFF;
  --text-main: #0F172A;
  --text-secondary: #475569;
  --muted: #64748B;
  --border: #E2E8F0;
  --surface: #FFFFFF;
  --accent: #2D68FE;
  --accent-hover: #1E4FD8;
  --cyan: #2D68FE;
  --purple: #1E4FD8;
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
}

.dashboard-mode {
  background: var(--bg-main);
  color: var(--text-main);
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

.card, .kpi-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 2px 6px rgba(0,0,0,0.03);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}
.card:hover, .kpi-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  border-color: #CBD5E1;
  transform: translateY(-2px);
}

.btn-primary {
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(45,104,254,0.2); }
.btn-primary:disabled { background: #94A3B8; cursor: not-allowed; box-shadow: none; transform: none; }

.btn-secondary {
  background: #FFFFFF;
  color: #334155;
  border: 1px solid #CBD5E1;
  border-radius: 6px;
  padding: 10px 20px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-secondary:hover { background: #F8FAFC; border-color: #94A3B8; }

.data-table { width: 100%; border-collapse: separate; border-spacing: 0; }
.data-table th {
  padding: 14px 20px;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--muted);
  border-bottom: 1px solid var(--border);
  background: #F8FAFC;
  white-space: nowrap;
}
.data-table td {
  padding: 14px 20px;
  font-size: 13px;
  border-bottom: 1px solid #F1F5F9;
  vertical-align: middle;
  color: var(--text-main);
}
.data-table tr:hover td { background: #F8FAFC; }

.page-header {
  padding: 0 0 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
  background: transparent;
}
.page-content { padding: 0; }
.table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--card-bg);
}

.badge-matched { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; font-size: 11px; padding: 4px 10px; border-radius: 99px; font-weight: 600; }
.badge-review { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; font-size: 11px; padding: 4px 10px; border-radius: 99px; font-weight: 600; }
.badge-unresolved { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; font-size: 11px; padding: 4px 10px; border-radius: 99px; font-weight: 600; }

.progress-bar, .confidence-bar { height: 6px; background: #E2E8F0; border-radius: 99px; overflow: hidden; }
.progress-fill, .confidence-fill { height: 100%; border-radius: 99px; transition: width 1.2s ease; background: var(--accent); }

.mono { font-family: var(--font-mono); font-size: 13px; }
.gradient-text { color: var(--text-main); }
.text-glow-cyan, .text-glow-white { text-shadow: none; color: var(--text-main); font-weight: 700; }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
''')
    with open(css_path, 'w') as f:
        f.write("".join(new_css))


print("Updating Sidebar.tsx...")
sidebar = """\
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navGroups = [
  {
    title: "Finance",
    items: [
      { href: "/dashboard", label: "Overview", icon: "⬡" },
      { href: "/reconciliation", label: "Reconciliation", icon: "⚡" },
      { href: "/settlements", label: "Settlements", icon: "₹" },
      { href: "/exceptions", label: "Exceptions", icon: "⚠" },
      { href: "/period-close", label: "Period Close", icon: "🔒" },
      { href: "/audit", label: "Audit Trail", icon: "🔐" },
    ]
  },
  {
    title: "Operations",
    items: [
      { href: "/controls", label: "Control Checks", icon: "☑" },
      { href: "/transactions", label: "Transactions", icon: "⇄" },
      { href: "/data-quality", label: "Data Quality", icon: "◎" },
      { href: "/ai-control-room", label: "AI Control Room", icon: "✦" },
    ]
  },
  {
    title: "Analytics",
    items: [
      { href: "/query-lab", label: "Query Lab", icon: "🔍" },
      { href: "/reports", label: "Reports", icon: "📄" },
      { href: "/evaluation", label: "Evaluation Lab", icon: "◈" },
      { href: "/settings", label: "Settings", icon: "⚙" },
    ]
  }
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside style={{ width: 260, background: "#ffffff", borderRight: "1px solid var(--border)", position: "fixed", top: 0, left: 0, bottom: 0, display: "flex", flexDirection: "column", zIndex: 50 }}>
      <div style={{ padding: "28px 24px 20px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #2D68FE, #1E4FD8)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 800, color: "#fff", boxShadow: "0 2px 8px rgba(45, 104, 254, 0.3)" }}>R</div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: "#0F172A", letterSpacing: "0.02em" }}>ReconIQ</div>
            <div style={{ fontSize: 10, color: "var(--accent)", letterSpacing: "0.08em", textTransform: "uppercase", fontWeight: 700 }}>Enterprise</div>
          </div>
        </div>
        <div style={{ marginTop: 20, padding: "8px 12px", background: "#F8FAFC", border: "1px solid var(--border)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" }}>
          <div>
            <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600 }}>Organization</div>
            <div style={{ fontSize: 13, color: "#0F172A", fontWeight: 600, marginTop: 2 }}>Acme Corp</div>
          </div>
          <div style={{ color: "var(--muted)", fontSize: 12 }}>▼</div>
        </div>
      </div>
      <div style={{ padding: "16px 16px 8px" }}>
        <div style={{ background: "#F1F5F9", border: "1px solid transparent", borderRadius: 8, padding: "8px 12px", display: "flex", alignItems: "center", gap: 8, color: "var(--muted)" }}>
          <span style={{ fontSize: 14 }}>🔍</span>
          <input type="text" placeholder="Search PAY, UTR..." style={{ background: "transparent", border: "none", color: "#0F172A", outline: "none", width: "100%", fontSize: 13 }} />
        </div>
      </div>
      <nav style={{ flex: 1, padding: "12px 16px", overflowY: "auto" }}>
        {navGroups.map((group, idx) => (
          <div key={idx} style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700, padding: "0 14px", marginBottom: 8 }}>{group.title}</div>
            {group.items.map(({ href, label, icon }) => {
              const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
              return (
                <Link key={href} href={href} style={{ textDecoration: "none" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 14px", borderRadius: 8, marginBottom: 2, background: isActive ? "#EFF6FF" : "transparent", color: isActive ? "var(--accent)" : "var(--text-secondary)", fontSize: 13, fontWeight: isActive ? 600 : 500, borderLeft: isActive ? "3px solid var(--accent)" : "3px solid transparent", transition: "all 0.15s ease" }} onMouseEnter={e => { if (!isActive) { e.currentTarget.style.background = "#F8FAFC"; e.currentTarget.style.color = "#0F172A"; } }} onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "var(--text-secondary)"; } }}>
                    <span style={{ fontSize: 16, width: 20, textAlign: "center", color: isActive ? "var(--accent)" : "var(--muted)" }}>{icon}</span>
                    <span>{label}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
      <div style={{ padding: "20px", borderTop: "1px solid var(--border)", background: "#F8FAFC" }}>
        <div style={{ fontSize: 11, color: "var(--muted)", lineHeight: 1.6 }}>
          <div style={{ fontWeight: 700, marginBottom: 4, color: "#0F172A", letterSpacing: "0.05em", textTransform: "uppercase" }}>Razorpay Buildathon</div>
          <div style={{ color: "var(--text-secondary)" }}>Track 04: AI Finance Controller</div>
        </div>
      </div>
    </aside>
  );
}
"""
with open('apps/web/components/Sidebar.tsx', 'w') as f: f.write(sidebar)

print("Updating LayoutBody.tsx...")
layout = """\
"use client";
import { usePathname } from "next/navigation";
import TopNav from "@/components/TopNav";
import Sidebar from "@/components/Sidebar";

export default function LayoutBody({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLanding = pathname === "/";
  if (isLanding) return <body className="landing-mode"><TopNav /><main>{children}</main></body>;

  return (
    <body className="dashboard-mode">
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <div style={{ flex: 1, marginLeft: 260, display: "flex", flexDirection: "column", minHeight: "100vh" }}>
          <header style={{ height: 56, borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 32px", background: "#ffffff", position: "sticky", top: 0, zIndex: 40 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", boxShadow: "0 0 8px rgba(16,185,129,0.3)" }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: "#10b981", textTransform: "uppercase", letterSpacing: "0.1em" }}>Live</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, background: "#F1F5F9", border: "1px solid transparent", borderRadius: 8, padding: "6px 12px" }}>
                <span style={{ fontSize: 12, color: "var(--muted)" }}>⌘K</span>
                <input type="text" placeholder="Search..." style={{ background: "transparent", border: "none", color: "#0F172A", outline: "none", fontSize: 13, width: 140 }} />
              </div>
              <div style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--accent)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: "#fff", cursor: "pointer" }}>A</div>
            </div>
          </header>
          <main style={{ flex: 1, padding: "32px 40px", minWidth: 0 }}>{children}</main>
        </div>
      </div>
    </body>
  );
}
"""
with open('apps/web/components/LayoutBody.tsx', 'w') as f: f.write(layout)

print("Running inline replacements on page components...")
replacements = {
    'color: "#f0f4ff"': 'color: "#0F172A"',
    'color: "#f1f5f9"': 'color: "#0F172A"',
    'color: "#e2e8f0"': 'color: "#1E293B"',
    'color: "#cbd5e1"': 'color: "#334155"',
    'color: "#fff"': 'color: "#0F172A"',
    'color: "#ffffff"': 'color: "#0F172A"',
    'background: "rgba(255,255,255,0.02)"': 'background: "#F8FAFC"',
    'background: "rgba(255,255,255,0.04)"': 'background: "#F1F5F9"',
    'background: "rgba(255,255,255,0.05)"': 'background: "#F1F5F9"',
    'background: "rgba(255,255,255,0.06)"': 'background: "#E2E8F0"',
    'background: "rgba(255,255,255,0.1)"': 'background: "#E2E8F0"',
    'background: "rgba(255,255,255,0.12)"': 'background: "#E2E8F0"',
    'border: "1px solid rgba(255,255,255,0.04)"': 'border: "1px solid #E2E8F0"',
    'border: "1px solid rgba(255,255,255,0.05)"': 'border: "1px solid #E2E8F0"',
    'border: "1px solid rgba(255,255,255,0.06)"': 'border: "1px solid #E2E8F0"',
    'borderBottom: "1px solid rgba(255,255,255,0.06)"': 'borderBottom: "1px solid #E2E8F0"',
    'borderBottom: "1px solid rgba(255,255,255,0.04)"': 'borderBottom: "1px solid #E2E8F0"',
    'borderBottom: "1px solid rgba(255,255,255,0.03)"': 'borderBottom: "1px solid #E2E8F0"',
    'background: "rgba(0,0,0,0.2)"': 'background: "#F8FAFC"',
    'background: "rgba(0,0,0,0.3)"': 'background: "#F1F5F9"',
    'background: "rgba(12,17,30,0.5)"': 'background: "#FFFFFF"',
    'background: "rgba(12,17,30,0.8)"': 'background: "#FFFFFF"',
    '"#22d3ee"': '"var(--accent)"',
    '"#a855f7"': '"var(--purple)"',
    'rgba(34,211,238,': 'rgba(45,104,254,',
    'rgba(168,85,247,': 'rgba(30,79,216,',
    'className="text-glow-white"': '',
    'className="text-glow-cyan"': '',
    'textShadow: "0 0 15px rgba(52,211,153,0.3)"': 'textShadow: "none"',
    'textShadow: "0 0 15px rgba(251,191,36,0.3)"': 'textShadow: "none"',
    'textShadow: "0 0 15px rgba(248,113,113,0.3)"': 'textShadow: "none"',
    'boxShadow: "0 0 8px rgba(16,185,129,0.6)"': 'boxShadow: "none"',
    'boxShadow: "0 0 8px rgba(34, 211, 238, 0.3)"': 'boxShadow: "none"',
    'boxShadow: "0 0 10px rgba(52,211,153,0.4)"': 'boxShadow: "none"',
    'boxShadow: "0 0 12px rgba(45,104,254,0.5)"': 'boxShadow: "none"',
    'boxShadow: "0 0 30px rgba(34,211,238,0.08)"': 'boxShadow: "none"',
    'border: "1px solid rgba(255,255,255,0.12)"': 'border: "1px solid #E2E8F0"',
    'background: "rgba(255,255,255,0.08)"': 'background: "#F1F5F9"',
    'background: "rgba(16,21,36,0.6)"': 'background: "#FFFFFF"',
    'color: "#64748b"': 'color: "#475569"',
    'color: "#94a3b8"': 'color: "#475569"',
}

folders = [
    'dashboard', 'reconciliation', 'exceptions', 'query-lab', 'ai-control-room',
    'audit', 'controls', 'data-quality', 'evaluation', 'ledger', 'reports', 'settings', 'settlements', 'transactions'
]

for folder in folders:
    path = f'apps/web/app/{folder}/page.tsx'
    if os.path.exists(path):
        with open(path, 'r') as f: content = f.read()
        for k, v in replacements.items():
            content = content.replace(k, v)
        with open(path, 'w') as f: f.write(content)

print("Done! Next.js will automatically hot reload.")
