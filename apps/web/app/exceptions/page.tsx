"use client";
import { useState, useEffect } from "react";
import { api, formatMinorAmount } from "@/lib/api";

const SEV_COLOR: Record<string, string> = { HIGH: "#ef4444", MEDIUM: "#f59e0b", LOW: "#10b981" };
const SEV_BG: Record<string, string> = { HIGH: "rgba(239,68,68,0.1)", MEDIUM: "rgba(245,158,11,0.1)", LOW: "rgba(16,185,129,0.1)" };
const SEV_BORDER: Record<string, string> = { HIGH: "rgba(239,68,68,0.2)", MEDIUM: "rgba(245,158,11,0.2)", LOW: "rgba(16,185,129,0.2)" };

export default function ExceptionsPage() {
  const [exceptions, setExceptions] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [explaining, setExplaining] = useState(false);
  const [filter, setFilter] = useState("ALL");

  useEffect(() => {
    api.listExceptions()
      .then(r => setExceptions(r.exceptions || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function handleExplain(excId: string) {
    setExplaining(true);
    try {
      const result = await api.explainException(excId);
      setSelected((prev: any) => prev ? { ...prev, ...result } : prev);
      setExceptions(prev => prev.map(e => e.exception_id === excId ? { ...e, ...result } : e));
    } catch (e) {} finally { setExplaining(false); }
  }

  async function handleReview(excId: string, action: string) {
    try {
      await api.reviewException(excId, { action });
      const newStatus = action === "mark_reviewed" ? "REVIEWED" : "ESCALATED";
      setExceptions(prev => prev.map(e => e.exception_id === excId ? { ...e, status: newStatus } : e));
      if (selected?.exception_id === excId) setSelected((p: any) => ({ ...p, status: newStatus }));
    } catch (e) {}
  }

  const filtered = filter === "ALL" ? exceptions : exceptions.filter(e => e.severity === filter);

  return (
    <div style={{ maxWidth: 1280 }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: "#0F172A", letterSpacing: "-0.03em", margin: 0 }}>Exception Workbench</h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 6 }}>
          {exceptions.length} open exceptions · Review, assign, and triage with Gemini AI
        </p>
      </div>

      {/* Severity filter */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {["ALL", "HIGH", "MEDIUM", "LOW"].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            padding: "6px 14px", borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: "pointer",
            background: filter === f ? (f === "ALL" ? "rgba(45,104,254,0.15)" : SEV_BG[f]) : "rgba(255,255,255,0.04)",
            border: filter === f ? `1px solid ${f === "ALL" ? "rgba(45,104,254,0.3)" : SEV_BORDER[f]}` : "1px solid rgba(255,255,255,0.06)",
            color: filter === f ? (f === "ALL" ? "var(--accent)" : SEV_COLOR[f]) : "var(--text-secondary)",
            transition: "all 0.15s ease",
          }}>
            {f} {f !== "ALL" && `(${exceptions.filter(e => e.severity === f).length})`}
          </button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 20, alignItems: "start" }}>
        {/* Exception list */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {loading && (
            <div className="card animate-3d animate-3d" style={{ padding: 32, textAlign: "center", color: "var(--muted)", fontSize: 13 }}>Loading...</div>
          )}
          {!loading && filtered.length === 0 && (
            <div className="card animate-3d animate-3d" style={{ padding: 48, textAlign: "center" }}>
              <div style={{ fontSize: 36, marginBottom: 12, opacity: 0.5 }}>✓</div>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#10b981" }}>No exceptions</div>
              <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 6 }}>Run reconciliation to detect mismatches</div>
            </div>
          )}
          {filtered.map((exc: any) => (
            <div
              key={exc.exception_id}
              onClick={() => setSelected(exc)}
              style={{
                padding: "14px 16px", borderRadius: 12, cursor: "pointer",
                background: selected?.exception_id === exc.exception_id ? "rgba(45,104,254,0.06)" : "rgba(12,17,30,0.5)",
                border: selected?.exception_id === exc.exception_id ? "1px solid rgba(45,104,254,0.25)" : "1px solid rgba(255,255,255,0.06)",
                backdropFilter: "blur(12px)",
                transition: "all 0.15s ease",
              }}
              onMouseEnter={e => { if (selected?.exception_id !== exc.exception_id) (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.12)"; }}
              onMouseLeave={e => { if (selected?.exception_id !== exc.exception_id) (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.06)"; }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ fontSize: 10, fontWeight: 700, color: SEV_COLOR[exc.severity], background: SEV_BG[exc.severity], padding: "2px 8px", borderRadius: 99, border: `1px solid ${SEV_BORDER[exc.severity]}` }}>
                  {exc.severity}
                </span>
                <span style={{
                  fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 99,
                  background: exc.status === "OPEN" ? "rgba(245,158,11,0.1)" : exc.status === "REVIEWED" ? "rgba(16,185,129,0.1)" : "rgba(30,79,216,0.1)",
                  color: exc.status === "OPEN" ? "#f59e0b" : exc.status === "REVIEWED" ? "#10b981" : "var(--purple)",
                  border: `1px solid ${exc.status === "OPEN" ? "rgba(245,158,11,0.2)" : exc.status === "REVIEWED" ? "rgba(16,185,129,0.2)" : "rgba(30,79,216,0.2)"}`,
                }}>
                  {exc.status}
                </span>
              </div>
              <div style={{ fontSize: 15, fontWeight: 700, color: "#1E293B", marginBottom: 4 }}>{formatMinorAmount(exc.amount_minor || 0)}</div>
              <div style={{ fontSize: 11, color: "#3b82f6", fontFamily: "monospace", marginBottom: 2 }}>{exc.reason_code?.replace(/_/g, " ")}</div>
              <div style={{ fontSize: 10, color: "var(--muted)", fontFamily: "monospace" }}>{exc.exception_id?.slice(0, 24)}...</div>
            </div>
          ))}
        </div>

        {/* Detail panel */}
        {selected ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Main card */}
            <div className="card animate-3d animate-3d" style={{ padding: 28 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
                <div>
                  <div style={{ fontFamily: "monospace", fontSize: 11, color: "var(--muted)", marginBottom: 8 }}>{selected.exception_id}</div>
                  <div style={{ fontSize: 36, fontWeight: 900, color: "#0F172A", letterSpacing: "-0.03em" }}>{formatMinorAmount(selected.amount_minor || 0)}</div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: SEV_COLOR[selected.severity], background: SEV_BG[selected.severity], padding: "3px 10px", borderRadius: 99, border: `1px solid ${SEV_BORDER[selected.severity]}` }}>
                      {selected.severity}
                    </span>
                    <span style={{ fontFamily: "monospace", fontSize: 12, color: "#3b82f6", fontWeight: 600 }}>{selected.reason_code?.replace(/_/g, " ")}</span>
                  </div>
                </div>
                <span style={{
                  fontSize: 12, fontWeight: 700, padding: "6px 14px", borderRadius: 8,
                  background: selected.status === "OPEN" ? "rgba(245,158,11,0.1)" : "rgba(16,185,129,0.1)",
                  color: selected.status === "OPEN" ? "#f59e0b" : "#10b981",
                  border: `1px solid ${selected.status === "OPEN" ? "rgba(245,158,11,0.25)" : "rgba(16,185,129,0.25)"}`,
                }}>
                  {selected.status}
                </span>
              </div>

              {/* Evidence */}
              {selected.evidence_json && (
                <div style={{ padding: 16, background: "#F8FAFC", borderRadius: 10, border: "1px solid #E2E8F0", marginBottom: 20 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>Evidence Record</div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                    {Object.entries(selected.evidence_json)
                      .filter(([k]) => !["top_candidates"].includes(k))
                      .map(([k, v]) => (
                        <div key={k}>
                          <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>{k.replace(/_/g, " ")}</div>
                          <div style={{ fontFamily: "monospace", fontSize: 12, color: "#1E293B", marginTop: 2 }}>{String(v)}</div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <button className="btn-secondary" style={{ fontSize: 12, padding: "8px 14px" }} onClick={() => handleReview(selected.exception_id, "mark_reviewed")}>
                  ✓ Mark Reviewed
                </button>
                <button className="btn-secondary" style={{ fontSize: 12, padding: "8px 14px" }} onClick={() => handleReview(selected.exception_id, "escalate")}>
                  ⬆ Escalate
                </button>
                <button className="btn-secondary" style={{ fontSize: 12, padding: "8px 14px" }} onClick={() => alert("Assignment module: coming soon")}>
                  👤 Assign
                </button>
                {!selected.explanation && (
                  <button className="btn-primary" style={{ fontSize: 12, padding: "8px 16px", marginLeft: "auto" }} onClick={() => handleExplain(selected.exception_id)} disabled={explaining}>
                    {explaining ? "Generating..." : "✦ Explain with Gemini AI"}
                  </button>
                )}
              </div>
            </div>

            {/* AI Explanation */}
            {selected.explanation ? (
              <div className="card animate-3d animate-3d" style={{ padding: 24, borderColor: "rgba(139,92,246,0.2)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 8, background: "rgba(139,92,246,0.15)", border: "1px solid rgba(139,92,246,0.3)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>✦</div>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "var(--purple)" }}>Gemini AI Explanation</div>
                    <div style={{ fontSize: 10, color: "var(--muted)", fontStyle: "italic" }}>The AI explains. It never invents the books.</div>
                  </div>
                </div>
                <p style={{ fontSize: 14, color: "#334155", lineHeight: 1.7, marginBottom: 16 }}>{selected.explanation}</p>
                {selected.recommended_action && (
                  <div style={{ padding: 14, background: "rgba(139,92,246,0.06)", borderRadius: 8, border: "1px solid rgba(139,92,246,0.15)" }}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: "var(--purple)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>Recommended Action</div>
                    <p style={{ fontSize: 13, color: "#475569", lineHeight: 1.6, margin: 0 }}>{selected.recommended_action}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="card animate-3d animate-3d" style={{ padding: 32, textAlign: "center", borderStyle: "dashed" }}>
                <div style={{ fontSize: 28, marginBottom: 12, opacity: 0.3 }}>✦</div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#1E293B", marginBottom: 6 }}>No AI explanation yet</div>
                <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 16 }}>Gemini AI will analyze this exception and suggest a resolution path</div>
                <button className="btn-primary" style={{ fontSize: 13 }} onClick={() => handleExplain(selected.exception_id)} disabled={explaining}>
                  {explaining ? "Generating explanation..." : "✦ Generate Gemini Explanation"}
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="card animate-3d animate-3d" style={{ padding: 80, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 300 }}>
            <div style={{ fontSize: 48, marginBottom: 16, opacity: 0.2 }}>⚠</div>
            <div style={{ fontSize: 15, fontWeight: 600, color: "#475569" }}>Select an exception</div>
            <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 6 }}>Choose from the list to review details and get AI triage</div>
          </div>
        )}
      </div>
    </div>
  );
}
