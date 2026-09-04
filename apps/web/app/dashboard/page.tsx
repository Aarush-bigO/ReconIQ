"use client";
import { useState, useEffect } from "react";
import { api, formatMinorAmount } from "@/lib/api";
import Link from "next/link";

function StatCard({ label, value, sub, color = "var(--accent)", icon }: any) {
  return (
    <div className="kpi-card animate-3d animate-3d" style={{ padding: 24 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em" }}>{label}</span>
        <span style={{ fontSize: 18 }}>{icon}</span>
      </div>
      <div style={{ fontSize: 28, fontWeight: 800, color, letterSpacing: "-0.02em", lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 8 }}>{sub}</div>}
    </div>
  );
}

export default function DashboardPage() {
  const [report, setReport] = useState<any>(null);
  const [exceptions, setExceptions] = useState<any[]>([]);
  const [trialBalance, setTrialBalance] = useState<any[]>([]);
  const [controls, setControls] = useState<any>(null);

  useEffect(() => {
    api.getLatestReport().then(setReport).catch(() => {});
    api.listExceptions().then((res) => setExceptions(res.exceptions || [])).catch(() => {});
    api.get("/ledger/trial-balance").then(res => setTrialBalance(res.data || [])).catch(() => {});
    api.get("/controls/run").then(res => setControls(res.data)).catch(() => {});
  }, []);

  const matchRate = report?.summary?.match_rate || 0;
  const totalProcessed = report?.summary?.records_processed || 0;
  const highPriority = exceptions.filter(e => e.severity === "HIGH").length;
  const medPriority = exceptions.filter(e => e.severity === "MEDIUM").length;
  const exceptionsAmount = exceptions.reduce((s, e) => s + (e.amount_minor || 0), 0);

  return (
    <div style={{ maxWidth: 1280 }}>

      {/* Page title */}
      <div className="animate-3d" style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", boxShadow: "none" }} />
          <span style={{ fontSize: 11, color: "#10b981", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em" }}>All Systems Operational</span>
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: "#0F172A", letterSpacing: "-0.03em", margin: 0, lineHeight: 1.2 }}>
          Finance Control Center
        </h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 6, lineHeight: 1.5 }}>
          Probabilistic record linkage · Real-time settlement matching · AI-powered exception triage
        </p>
      </div>

      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
        <StatCard
          label="Match Rate"
          value={report ? `${(matchRate * 100).toFixed(1)}%` : "—"}
          sub={`${totalProcessed} records processed`}
          color="var(--accent)"
          icon="⚡"
        />
        <StatCard
          label="Reconciled Value"
          value={report ? formatMinorAmount(report.summary?.reconciled_value_minor || 0) : "—"}
          sub="this run"
          color="#10b981"
          icon="✓"
        />
        <StatCard
          label="Exceptions"
          value={exceptions.length || "—"}
          sub={`${highPriority} high · ${medPriority} medium`}
          color={exceptions.length > 5 ? "#f59e0b" : "#10b981"}
          icon="⚠"
        />
        <StatCard
          label="Exception Risk"
          value={exceptionsAmount > 0 ? formatMinorAmount(exceptionsAmount) : "₹0"}
          sub="under active review"
          color="var(--purple)"
          icon="₹"
        />
      </div>

      {/* Main grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 }}>

        {/* Reconciliation Health */}
        <div className="card animate-3d animate-3d" style={{ padding: 28 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 20 }}>
            Reconciliation Health
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 20 }}>
            <div style={{ fontSize: 52, fontWeight: 900, letterSpacing: "-0.04em", background: "linear-gradient(135deg, #22d3ee, #a855f7)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
              {report ? `${(matchRate * 100).toFixed(0)}%` : "—"}
            </div>
            <div style={{ fontSize: 14, color: "var(--text-secondary)" }}>match rate</div>
          </div>

          <div style={{ display: "flex", gap: 2, height: 6, marginBottom: 20 }}>
            {Array.from({ length: 40 }).map((_, i) => {
              const filled = i < Math.floor(matchRate * 40);
              return (
                <div key={i} style={{
                  flex: 1, borderRadius: 3,
                  background: filled ? "linear-gradient(135deg, #22d3ee, #a855f7)" : "rgba(255,255,255,0.04)",
                  boxShadow: filled ? "0 0 6px rgba(45,104,254,0.3)" : "none",
                  transition: `all 0.3s ease ${i * 0.01}s`,
                }} />
              );
            })}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
            {[
              { label: "Auto-Matched", value: report?.summary?.auto_matched ?? "—", color: "#10b981" },
              { label: "Manual Review", value: report?.summary?.manual_review ?? "—", color: "#f59e0b" },
              { label: "Unresolved", value: report?.summary?.unresolved ?? "—", color: "#ef4444" },
            ].map(item => (
              <div key={item.label} style={{ padding: 14, background: "#F8FAFC", borderRadius: 10, border: "1px solid #E2E8F0", textAlign: "center" }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: item.color }}>{item.value}</div>
                <div style={{ fontSize: 10, color: "var(--muted)", marginTop: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>{item.label}</div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
            <Link href="/reconciliation" className="btn-primary" style={{ flex: 1, justifyContent: "center", padding: "10px 16px", fontSize: 13 }}>
              Run Reconciliation ⚡
            </Link>
            <Link href="/evaluation" className="btn-secondary" style={{ fontSize: 13, padding: "10px 16px" }}>
              Evaluate →
            </Link>
          </div>
        </div>

        {/* Exception Risk Panel */}
        <div className="card animate-3d animate-3d" style={{ padding: 28 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 20 }}>
            Exception Risk Breakdown
          </div>

          <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
            {[
              { label: "HIGH", count: highPriority, bg: "rgba(239,68,68,0.08)", border: "rgba(239,68,68,0.2)", color: "#ef4444" },
              { label: "MEDIUM", count: medPriority, bg: "rgba(245,158,11,0.08)", border: "rgba(245,158,11,0.2)", color: "#f59e0b" },
              { label: "LOW", count: exceptions.filter(e => e.severity === "LOW").length, bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.2)", color: "#10b981" },
            ].map(s => (
              <div key={s.label} style={{ flex: 1, padding: "16px 12px", background: s.bg, border: `1px solid ${s.border}`, borderRadius: 12, textAlign: "center" }}>
                <div style={{ fontSize: 28, fontWeight: 800, color: s.color }}>{s.count}</div>
                <div style={{ fontSize: 10, color: s.color, marginTop: 4, fontWeight: 700, letterSpacing: "0.08em" }}>{s.label}</div>
              </div>
            ))}
          </div>

          <div style={{ flex: 1 }}>
            {exceptions.slice(0, 4).map((exc: any) => (
              <div key={exc.exception_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid #E2E8F0" }}>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#1E293B" }}>{exc.reason_code?.replace(/_/g, " ") || "Unknown"}</div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2 }}>{exc.source}</div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: "#1E293B" }}>{formatMinorAmount(exc.amount_minor || 0)}</span>
                  <span style={{ fontSize: 10, padding: "2px 7px", borderRadius: 99, fontWeight: 700,
                    background: exc.severity === "HIGH" ? "rgba(239,68,68,0.12)" : exc.severity === "MEDIUM" ? "rgba(245,158,11,0.12)" : "rgba(16,185,129,0.12)",
                    color: exc.severity === "HIGH" ? "#ef4444" : exc.severity === "MEDIUM" ? "#f59e0b" : "#10b981",
                  }}>{exc.severity}</span>
                </div>
              </div>
            ))}
          </div>

          <Link href="/exceptions" className="btn-secondary" style={{ marginTop: 16, display: "flex", justifyContent: "center", fontSize: 13, padding: "10px" }}>
            View All Exceptions →
          </Link>
        </div>
      </div>

      {/* Controls + Trial Balance */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: 20, marginBottom: 24 }}>

        {/* Invariant Controls */}
        <div className="card animate-3d animate-3d" style={{ padding: 28 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 20 }}>
            Invariant Controls
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {(controls?.controls || []).slice(0, 5).map((ctrl: any, i: number) => (
              <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", background: "#F8FAFC", borderRadius: 8, border: `1px solid ${ctrl.status === "PASS" ? "rgba(16,185,129,0.12)" : "rgba(239,68,68,0.12)"}` }}>
                <span style={{ fontSize: 12, fontWeight: 500, color: "#c8d4e8" }}>{ctrl.name}</span>
                <span style={{ fontSize: 13, fontWeight: 700, color: ctrl.status === "PASS" ? "#10b981" : "#ef4444" }}>
                  {ctrl.status === "PASS" ? "✓" : "✗"}
                </span>
              </div>
            ))}
            {!controls && (
              <div style={{ textAlign: "center", padding: "20px 0", color: "var(--muted)", fontSize: 13 }}>No control data · Run reconciliation first</div>
            )}
          </div>
          <Link href="/controls" className="btn-secondary" style={{ marginTop: 16, display: "flex", justifyContent: "center", fontSize: 13, padding: "10px" }}>
            Full Control Report →
          </Link>
        </div>

        {/* Trial Balance */}
        <div className="card animate-3d animate-3d" style={{ padding: 28 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em" }}>Trial Balance</div>
            <Link href="/ledger" style={{ fontSize: 12, color: "var(--accent)", fontWeight: 600, textDecoration: "none" }}>View Ledger →</Link>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                {["Account", "Debits", "Credits", "Net"].map(h => (
                  <th key={h} style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em", padding: "8px 0", textAlign: h === "Account" ? "left" : "right", borderBottom: "1px solid #E2E8F0" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {trialBalance.slice(0, 6).map((row: any, i: number) => (
                <tr key={i}>
                  <td style={{ padding: "10px 0", fontSize: 12, fontFamily: "monospace", color: "var(--accent)", borderBottom: "1px solid #E2E8F0" }}>{row.account}</td>
                  <td style={{ padding: "10px 0", fontSize: 12, fontFamily: "monospace", color: "#475569", textAlign: "right", borderBottom: "1px solid #E2E8F0" }}>{formatMinorAmount(row.debit_minor || 0)}</td>
                  <td style={{ padding: "10px 0", fontSize: 12, fontFamily: "monospace", color: "#475569", textAlign: "right", borderBottom: "1px solid #E2E8F0" }}>{formatMinorAmount(row.credit_minor || 0)}</td>
                  <td style={{ padding: "10px 0", fontSize: 12, fontFamily: "monospace", fontWeight: 700, color: (row.balance_minor || 0) >= 0 ? "#10b981" : "#ef4444", textAlign: "right", borderBottom: "1px solid #E2E8F0" }}>{formatMinorAmount(row.balance_minor || 0)}</td>
                </tr>
              ))}
              {trialBalance.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: "center", padding: "20px 0", fontSize: 13, color: "var(--muted)" }}>No ledger data · Run reconciliation first</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
        {[
          { href: "/ai-control-room", icon: "✦", title: "AI Control Room", desc: "Natural language queries over financial data", color: "var(--accent)" },
          { href: "/query-lab", icon: "🔍", title: "Query Lab", desc: "SQL via natural language — Gemini powered", color: "var(--purple)" },
          { href: "/period-close", icon: "🔒", title: "Period Close", desc: "Generate evidence packs, close the period", color: "#f59e0b" },
          { href: "/audit", icon: "🔐", title: "Audit Trail", desc: "SHA-256 hash chain · tamper-evident log", color: "#10b981" },
        ].map(item => (
          <Link key={item.href} href={item.href} style={{ textDecoration: "none" }}>
            <div className="card animate-3d animate-3d" style={{ padding: 20, cursor: "pointer", borderColor: `${item.color}15`, transition: "all 0.3s ease" }}
              onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.borderColor = `${item.color}30`; (e.currentTarget as HTMLDivElement).style.transform = "translateY(-2px)"; }}
              onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.borderColor = `${item.color}15`; (e.currentTarget as HTMLDivElement).style.transform = "translateY(0)"; }}
            >
              <div style={{ fontSize: 22, marginBottom: 12, color: item.color }}>{item.icon}</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#1E293B", marginBottom: 6 }}>{item.title}</div>
              <div style={{ fontSize: 11, color: "var(--muted)", lineHeight: 1.5 }}>{item.desc}</div>
            </div>
          </Link>
        ))}
      </div>

      {/* Footer */}
      <div style={{ marginTop: 40, paddingTop: 24, borderTop: "1px solid rgba(255,255,255,0.04)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em" }}>Razorpay Buildathon · Track 04: AI Finance Controller</span>
        <span style={{ fontSize: 11, color: "var(--muted)", fontStyle: "italic" }}>Deterministic systems decide. AI explains.</span>
      </div>
    </div>
  );
}
