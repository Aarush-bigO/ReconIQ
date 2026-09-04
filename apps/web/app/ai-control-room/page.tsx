"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { api, formatMinorAmount } from "@/lib/api";

export default function AIControlRoomPage() {
  const [exceptions, setExceptions] = useState<any[]>([]);
  const [explaining, setExplaining] = useState<string | null>(null);

  useEffect(() => {
    api.listExceptions().then(r => setExceptions(r.exceptions || [])).catch(() => {});
  }, []);

  const highPriority = exceptions.filter(e => e.severity === "HIGH").length;
  const mediumPriority = exceptions.filter(e => e.severity === "MEDIUM").length;
  const explained = exceptions.filter(e => e.explanation).length;

  async function explainAll() {
    const toExplain = exceptions.filter(e => !e.explanation && e.severity === "HIGH").slice(0, 3);
    for (const exc of toExplain) {
      setExplaining(exc.exception_id);
      try {
        const result = await api.explainException(exc.exception_id);
        setExceptions(prev => prev.map(e => e.exception_id === exc.exception_id ? { ...e, ...result } : e));
      } catch (e) {}
    }
    setExplaining(null);
  }

  return (
    <div style={{ maxWidth: 1280 }}>

      {/* Header */}
      <div className="animate-3d" style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg, rgba(30,79,216,0.3), rgba(45,104,254,0.2))", border: "1px solid rgba(30,79,216,0.4)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, color: "var(--purple)" }}>✦</div>
          <span style={{ fontSize: 11, fontWeight: 700, color: "var(--purple)", textTransform: "uppercase", letterSpacing: "0.12em" }}>Gemini AI Powered</span>
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: "#0F172A", letterSpacing: "-0.03em", margin: 0 }}>AI Control Room</h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 6 }}>
          AI explains deterministic findings — never makes financial decisions
        </p>
      </div>

      {/* Safety boundary */}
      <div style={{ padding: 20, marginBottom: 28, background: "rgba(30,79,216,0.06)", borderRadius: 12, border: "1px solid rgba(30,79,216,0.2)", display: "flex", gap: 16, alignItems: "flex-start" }}>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: "rgba(30,79,216,0.15)", border: "1px solid rgba(30,79,216,0.3)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>🔒</div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--purple)", marginBottom: 4 }}>Strict AI Safety Boundary</div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.7 }}>
            Gemini AI receives only structured evidence (JSON schema). It can only produce <code style={{ color: "var(--purple)", background: "rgba(30,79,216,0.1)", padding: "1px 5px", borderRadius: 4 }}>explanation</code> and <code style={{ color: "var(--purple)", background: "rgba(30,79,216,0.1)", padding: "1px 5px", borderRadius: 4 }}>recommended_action</code> fields.
            It cannot change amounts, confidence scores, create matches, or write to any financial state. All decisions are deterministic.
          </div>
        </div>
      </div>

      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
        {[
          { label: "Total Exceptions", value: exceptions.length, color: "#f59e0b", icon: "⚠" },
          { label: "High Priority", value: highPriority, color: "#ef4444", icon: "🔴" },
          { label: "AI Explained", value: explained, color: "#10b981", icon: "✦" },
          { label: "Auto-Resolved", value: "0", color: "var(--muted)", icon: "🔒", note: "AI never auto-resolves" },
        ].map(k => (
          <div key={k.label} className="card animate-3d animate-3d" style={{ padding: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em" }}>{k.label}</span>
              <span style={{ fontSize: 16 }}>{k.icon}</span>
            </div>
            <div style={{ fontSize: 28, fontWeight: 800, color: k.color }}>{k.value}</div>
            {(k as any).note && <div style={{ fontSize: 10, color: "var(--muted)", marginTop: 4, fontStyle: "italic" }}>{(k as any).note}</div>}
          </div>
        ))}
      </div>

      {/* Main content */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>

        {/* Exception queue */}
        <div className="card animate-3d animate-3d" style={{ padding: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em" }}>Exception Queue</div>
            <button className="btn-secondary" style={{ fontSize: 11, padding: "6px 12px" }} onClick={explainAll} disabled={!!explaining}>
              {explaining ? "Explaining..." : `✦ Explain HIGH Priority`}
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {exceptions.slice(0, 6).map((exc: any) => (
              <div key={exc.exception_id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 14px", background: "#F8FAFC", borderRadius: 10, border: "1px solid #E2E8F0", transition: "border-color 0.2s" }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", flexShrink: 0, background: exc.severity === "HIGH" ? "#ef4444" : exc.severity === "MEDIUM" ? "#f59e0b" : "#10b981", boxShadow: `0 0 6px ${exc.severity === "HIGH" ? "rgba(239,68,68,0.5)" : exc.severity === "MEDIUM" ? "rgba(245,158,11,0.5)" : "rgba(16,185,129,0.5)"}` }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#1E293B", marginBottom: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {exc.reason_code?.replace(/_/g, " ")} · {formatMinorAmount(exc.amount_minor || 0)}
                  </div>
                  <div style={{ fontSize: 10, color: "var(--muted)", fontFamily: "monospace" }}>{exc.exception_id?.slice(0, 24)}...</div>
                </div>
                <div style={{ flexShrink: 0, display: "flex", alignItems: "center", gap: 6 }}>
                  {exc.explanation ? (
                    <span style={{ fontSize: 10, color: "#10b981", fontWeight: 700, background: "rgba(16,185,129,0.1)", padding: "2px 7px", borderRadius: 99, border: "1px solid rgba(16,185,129,0.2)" }}>✦ Explained</span>
                  ) : explaining === exc.exception_id ? (
                    <span style={{ fontSize: 10, color: "var(--purple)" }}>Generating...</span>
                  ) : null}
                </div>
              </div>
            ))}
            {exceptions.length === 0 && (
              <div style={{ textAlign: "center", padding: "32px 0", color: "var(--muted)", fontSize: 13 }}>No exceptions · Run reconciliation first</div>
            )}
          </div>
          <Link href="/exceptions" className="btn-secondary" style={{ marginTop: 16, display: "flex", justifyContent: "center", fontSize: 12, padding: "8px" }}>
            Open Exception Workbench →
          </Link>
        </div>

        {/* AI features */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {[
            {
              icon: "🔍",
              color: "var(--accent)",
              title: "Query Lab",
              desc: "Ask any financial question in natural language. Gemini AI parses intent, generates read-only SQL, and returns structured results.",
              link: "/query-lab",
              cta: "Open Query Lab →",
            },
            {
              icon: "⚠",
              color: "#f59e0b",
              title: "Exception Explainer",
              desc: "Select any exception in the workbench and click 'Explain with Gemini'. AI produces a plain-English analysis + resolution path.",
              link: "/exceptions",
              cta: "Open Exceptions →",
            },
            {
              icon: "◈",
              color: "var(--purple)",
              title: "Evaluation Lab",
              desc: "Sweep Splink matching thresholds from 0.80→0.99 and compare precision/recall/F1 against ground truth.",
              link: "/evaluation",
              cta: "Open Evaluation Lab →",
            },
          ].map(f => (
            <div key={f.title} className="card animate-3d animate-3d" style={{ padding: 20, borderColor: `${f.color}15` }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: `${f.color}15`, border: `1px solid ${f.color}30`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, flexShrink: 0 }}>{f.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "#1E293B", marginBottom: 6 }}>{f.title}</div>
                  <div style={{ fontSize: 12, color: "var(--muted)", lineHeight: 1.6, marginBottom: 12 }}>{f.desc}</div>
                  <Link href={f.link} style={{ fontSize: 12, fontWeight: 600, color: f.color, textDecoration: "none" }}>{f.cta}</Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
