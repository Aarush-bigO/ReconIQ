"use client";
import { useState } from "react";
import { api, formatMinorAmount } from "@/lib/api";
import Transaction360 from "@/components/Transaction360";

export default function ReconciliationPage() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [config, setConfig] = useState({ auto_match_threshold: 0.95, review_threshold: 0.70, date_tolerance_days: 3, amount_tolerance_minor: 100 });
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("");
  const [selectedMatch, setSelectedMatch] = useState<any>(null);

  async function handleRun() {
    setRunning(true); setError(""); setResult(null); setProgress(0);
    const stages = ["Loading canonical sources...", "Generating candidate pairs...", "Running Splink 4.x linkage...", "Applying deterministic policy...", "Classifying exceptions..."];
    let s = 0;
    setStage(stages[0]);
    const interval = setInterval(() => {
      setProgress(p => {
        const next = Math.min(p + 7, 90);
        const stageIdx = Math.min(Math.floor(next / 20), stages.length - 1);
        if (stageIdx !== s) { s = stageIdx; setStage(stages[stageIdx]); }
        return next;
      });
    }, 400);
    try {
      const r = await api.runReconciliation(config);
      clearInterval(interval); setProgress(100); setStage("Complete!");
      setTimeout(() => setResult(r), 400);
    } catch (e: any) {
      clearInterval(interval);
      setError(e.message || "Reconciliation failed.");
    } finally { setRunning(false); }
  }

  return (
    <div style={{ maxWidth: 1280 }}>
      {/* Header */}
      <div className="animate-3d" style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: "#0F172A", letterSpacing: "-0.03em", margin: 0 }}>
          Reconciliation Engine
        </h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 6 }}>
          Splink 4.x probabilistic record linkage across Razorpay · Ledger · Bank Statement
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 24 }}>

        {/* Config Panel */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card " style={{ padding: 24 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--accent)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
              <span>⚙</span> Linkage Policy
            </div>

            {[
              { key: "auto_match_threshold", label: "Auto-Match Threshold", min: 0.5, max: 1.0, step: 0.01 },
              { key: "review_threshold", label: "Review Threshold", min: 0.3, max: 0.95, step: 0.01 },
              { key: "date_tolerance_days", label: "Date Tolerance (days)", min: 1, max: 7, step: 1 },
            ].map(f => (
              <div key={f.key} style={{ marginBottom: 20 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <label style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 500 }}>{f.label}</label>
                  <span style={{ fontSize: 13, fontWeight: 800, color: "var(--accent)", fontFamily: "monospace" }}>
                    {config[f.key as keyof typeof config]}
                  </span>
                </div>
                <input type="range" min={f.min} max={f.max} step={f.step}
                  value={config[f.key as keyof typeof config] as number}
                  onChange={e => setConfig(c => ({ ...c, [f.key]: parseFloat(e.target.value) }))}
                  style={{ width: "100%", accentColor: "var(--accent)", height: 4 }}
                />
              </div>
            ))}

            <div style={{ padding: 12, background: "rgba(45,104,254,0.05)", borderRadius: 8, border: "1px solid rgba(45,104,254,0.1)", marginBottom: 20, fontSize: 11, color: "var(--muted)", lineHeight: 1.6 }}>
              Probabilistic record linkage via <strong style={{ color: "var(--accent)" }}>Splink 4.x</strong>. Comparisons use amount, date, reference, and payment ID features. Policy is deterministic — AI only explains.
            </div>

            <button className="btn-primary" onClick={handleRun} disabled={running} style={{ width: "100%", justifyContent: "center", padding: "13px" }}>
              {running ? "⟳ Reconciling..." : "⚡ Run Reconciliation"}
            </button>

            {running && (
              <div style={{ marginTop: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, fontSize: 11, color: "var(--text-secondary)" }}>
                  <span>{stage}</span>
                  <span style={{ color: "var(--accent)", fontWeight: 700 }}>{progress}%</span>
                </div>
                <div style={{ height: 4, background: "#E2E8F0", borderRadius: 99, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg, #22d3ee, #a855f7)", borderRadius: 99, transition: "width 0.4s ease", boxShadow: "0 0 8px rgba(45,104,254,0.5)" }} />
                </div>
              </div>
            )}

            {error && (
              <div style={{ marginTop: 16, padding: 14, background: "rgba(239,68,68,0.08)", borderRadius: 8, border: "1px solid rgba(239,68,68,0.2)", fontSize: 12, color: "#fca5a5", lineHeight: 1.5 }}>
                {error}
              </div>
            )}
          </div>

          {/* Source badges */}
          <div className="card " style={{ padding: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16 }}>Data Sources</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                { label: "Razorpay Payments", color: "#3b82f6", dot: "#3b82f6" },
                { label: "Internal Ledger", color: "#8b5cf6", dot: "#8b5cf6" },
                { label: "Bank Statement", color: "#10b981", dot: "#10b981" },
              ].map(s => (
                <div key={s.label} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", background: "#F8FAFC", borderRadius: 8 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.dot, boxShadow: `0 0 6px ${s.dot}80` }} />
                  <span style={{ fontSize: 12, color: "#c8d4e8", fontWeight: 500 }}>{s.label}</span>
                  <span style={{ marginLeft: "auto", fontSize: 10, color: "var(--muted)", fontWeight: 600 }}>READY</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Results Area */}
        <div>
          {!result && !running && !error && (
            <div className="card " style={{ padding: 80, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 400 }}>
              <div style={{ fontSize: 56, marginBottom: 20, opacity: 0.3 }}>⚡</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: "#1E293B", marginBottom: 8 }}>Ready to Reconcile</div>
              <div style={{ fontSize: 13, color: "var(--muted)", maxWidth: 300, lineHeight: 1.6 }}>
                Configure your Splink linkage policy on the left, then click Run to process all sources.
              </div>
            </div>
          )}

          {result && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

              {/* Summary KPIs */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                {[
                  { label: "Records Processed", value: result.summary.records_processed, color: "#1E293B" },
                  { label: "Auto-Matched", value: result.summary.auto_matched, color: "#10b981" },
                  { label: "Match Rate", value: `${(result.summary.match_rate * 100).toFixed(1)}%`, color: "var(--accent)" },
                  { label: "Exceptions", value: result.summary.exceptions, color: result.summary.exceptions > 10 ? "#ef4444" : "#f59e0b" },
                ].map(k => (
                  <div key={k.label} className="card " style={{ padding: 18, textAlign: "center" }}>
                    <div style={{ fontSize: 24, fontWeight: 800, color: k.color, marginBottom: 6 }}>{k.value}</div>
                    <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600 }}>{k.label}</div>
                  </div>
                ))}
              </div>

              {/* ML Metrics */}
              {result.metrics?.precision !== undefined && (
                <div className="card " style={{ padding: 24 }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 20 }}>
                    Benchmark Metrics vs Ground Truth
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
                    {[
                      { label: "Precision", value: result.metrics.precision },
                      { label: "Recall", value: result.metrics.recall },
                      { label: "F1 Score", value: result.metrics.f1 },
                    ].map(m => {
                      const pct = m.value * 100;
                      const color = pct >= 90 ? "#10b981" : pct >= 70 ? "#f59e0b" : "#ef4444";
                      return (
                        <div key={m.label} style={{ textAlign: "center" }}>
                          <div style={{ fontSize: 36, fontWeight: 900, color, letterSpacing: "-0.03em" }}>{pct.toFixed(1)}%</div>
                          <div style={{ height: 4, background: "#E2E8F0", borderRadius: 99, margin: "12px 0 8px", overflow: "hidden" }}>
                            <div style={{ height: "100%", width: `${pct}%`, background: color, borderRadius: 99 }} />
                          </div>
                          <div style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 500 }}>{m.label}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Match table */}
              {result.matches?.length > 0 && (
                <div className="card " style={{ overflow: "hidden" }}>
                  <div style={{ padding: "16px 24px", borderBottom: "1px solid #E2E8F0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: "#1E293B" }}>
                      Top Auto-Matched Pairs
                    </span>
                    <span className="badge-matched">{result.summary.auto_matched} total</span>
                  </div>
                  <div style={{ overflowX: "auto" }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Left Transaction</th>
                          <th>Right Transaction</th>
                          <th>Confidence</th>
                          <th>Decision</th>
                          <th>Reason</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.matches.slice(0, 10).map((m: any, i: number) => (
                          <tr key={i}>
                            <td className="mono" style={{ color: "#475569", fontSize: 11 }}>{m.left_id?.slice(0, 18)}...</td>
                            <td className="mono" style={{ color: "#475569", fontSize: 11 }}>{m.right_id?.slice(0, 18)}...</td>
                            <td>
                              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <div style={{ width: 64, height: 4, background: "#E2E8F0", borderRadius: 99, overflow: "hidden" }}>
                                  <div style={{ width: `${m.probability * 100}%`, height: "100%", background: "#10b981", borderRadius: 99 }} />
                                </div>
                                <span style={{ fontSize: 12, fontWeight: 700, color: "#10b981" }}>{(m.probability * 100).toFixed(1)}%</span>
                              </div>
                            </td>
                            <td><span className="badge-matched">{m.decision}</span></td>
                            <td style={{ fontSize: 11, color: "var(--muted)" }}>{m.reason_code?.replace(/_/g, " ")}</td>
                            <td>
                              <button className="btn-secondary" style={{ fontSize: 11, padding: "4px 10px" }} onClick={() => setSelectedMatch(m)}>
                                Explain
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Run metadata */}
              <div style={{ padding: "12px 16px", background: "#F8FAFC", borderRadius: 10, border: "1px solid #E2E8F0", display: "flex", gap: 20, fontSize: 12, color: "var(--muted)", flexWrap: "wrap" }}>
                <span>Run: <strong style={{ color: "#1E293B", fontFamily: "monospace" }}>{result.run_id}</strong></span>
                <span>·</span>
                <span>Processing: <strong style={{ color: "#1E293B" }}>{result.processing_ms}ms</strong></span>
                <span>·</span>
                <span style={{ color: result.audit?.chain_verified ? "#10b981" : "#ef4444", fontWeight: 700 }}>
                  {result.audit?.chain_verified ? "✓ Audit Chain Verified" : "⚠ Audit Chain Failed"}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {selectedMatch && (
        <Transaction360
          evidence={selectedMatch.evidence}
          decision={selectedMatch.decision}
          confidence={selectedMatch.probability}
          reasonCode={selectedMatch.reason_code}
          onClose={() => setSelectedMatch(null)}
        />
      )}
    </div>
  );
}
