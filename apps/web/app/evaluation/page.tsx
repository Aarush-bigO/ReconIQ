"use client";
import { useState } from "react";
import { api } from "@/lib/api";

const THRESHOLDS = [0.80, 0.85, 0.90, 0.95, 0.97, 0.99];

export default function EvaluationPage() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runEval() {
    setLoading(true); setError("");
    try {
      const r = await api.runEvaluation();
      setResults(r.results || []);
    } catch (e: any) {
      setError(e.message || "Evaluation failed");
    } finally { setLoading(false); }
  }

  const best = results.find(r => r.threshold === 0.95);

  return (
    <div>
      <div className="page-header" style={{ paddingBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "#0F172A", margin: 0 }}>Evaluation Lab</h1>
          <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 6, marginBottom: 0 }}>
            Threshold sweep with real precision/recall vs hidden ground truth
          </p>
        </div>
        <button className="btn-primary" onClick={runEval} disabled={loading}>
          {loading ? "⟳ Running..." : "◈ Run Benchmark"}
        </button>
      </div>

      <div className="page-content">
        {error && (
          <div style={{ padding: 16, background: "rgba(239,68,68,0.1)", borderRadius: 8, border: "1px solid rgba(239,68,68,0.2)", color: "#ef4444", marginBottom: 24, fontSize: 13 }}>
            {error}
          </div>
        )}

        {loading && (
          <div className="card " style={{ padding: 48, textAlign: "center" }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>◈</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: "#1E293B", marginBottom: 8 }}>Running threshold sweep...</div>
            <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 24 }}>Running Splink + evaluating against ground truth at 6 thresholds</div>
            <div className="progress-bar" style={{ maxWidth: 400, margin: "0 auto" }}>
              <div className="progress-fill" style={{ width: "60%", animation: "none", background: "linear-gradient(90deg, #3b82f6, #8b5cf6)" }} />
            </div>
          </div>
        )}

        {!loading && results.length === 0 && (
          <div className="card " style={{ padding: 48, textAlign: "center", color: "var(--muted)" }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>◈</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: "#475569", marginBottom: 8 }}>No benchmark results yet</div>
            <div style={{ fontSize: 13 }}>Click Run Benchmark to evaluate across thresholds 0.80–0.99</div>
          </div>
        )}

        {results.length > 0 && (
          <div className="fade-in">
            {/* Recommended threshold */}
            {best && (
              <div style={{ padding: 20, marginBottom: 24, background: "rgba(59,130,246,0.06)", borderRadius: 12, border: "1px solid rgba(59,130,246,0.2)" }}>
                <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "#3b82f6", marginBottom: 12 }}>
                  Recommended Operating Point
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 16 }}>
                  {[
                    { label: "Threshold", value: best.threshold },
                    { label: "Precision", value: `${(best.precision * 100).toFixed(1)}%` },
                    { label: "Recall", value: `${(best.recall * 100).toFixed(1)}%` },
                    { label: "F1", value: `${(best.f1 * 100).toFixed(1)}%` },
                    { label: "Match Rate", value: `${(best.match_rate * 100).toFixed(1)}%` },
                  ].map(m => (
                    <div key={m.label} style={{ textAlign: "center" }}>
                      <div style={{ fontSize: 24, fontWeight: 700, color: "#3b82f6" }}>{m.value}</div>
                      <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>{m.label}</div>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 12, fontSize: 12, color: "var(--muted)" }}>
                  Reason: High precision with manageable manual-review volume.
                </div>
              </div>
            )}

            {/* Threshold table */}
            <div className="table-wrapper ">
              <table className="data-table ">
                <thead>
                  <tr>
                    <th>Threshold</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1</th>
                    <th>Match Rate</th>
                    <th>Auto-Matched</th>
                    <th>Manual Review</th>
                    <th>Unresolved</th>
                    <th>Time (s)</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r: any) => (
                    <tr key={r.threshold} style={{ background: r.threshold === 0.95 ? "rgba(59,130,246,0.06)" : undefined }}>
                      <td style={{ fontWeight: r.threshold === 0.95 ? 700 : 400, color: r.threshold === 0.95 ? "#3b82f6" : "#e2e8f0" }}>
                        {r.threshold.toFixed(2)} {r.threshold === 0.95 && "★"}
                      </td>
                      <td style={{ color: r.precision >= 0.95 ? "#10b981" : r.precision >= 0.8 ? "#f59e0b" : "#ef4444", fontWeight: 600 }}>
                        {(r.precision * 100).toFixed(1)}%
                      </td>
                      <td style={{ color: r.recall >= 0.85 ? "#10b981" : r.recall >= 0.7 ? "#f59e0b" : "#ef4444", fontWeight: 600 }}>
                        {(r.recall * 100).toFixed(1)}%
                      </td>
                      <td style={{ fontWeight: 600, color: "#1E293B" }}>{(r.f1 * 100).toFixed(1)}%</td>
                      <td>{(r.match_rate * 100).toFixed(1)}%</td>
                      <td style={{ color: "#10b981" }}>{r.auto_matched}</td>
                      <td style={{ color: "#f59e0b" }}>{r.manual_review}</td>
                      <td style={{ color: "#ef4444" }}>{r.unresolved}</td>
                      <td style={{ color: "var(--muted)", fontSize: 12 }}>{r.processing_seconds}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ marginTop: 16, fontSize: 12, color: "var(--muted)" }}>
              Dataset: {results[0]?.dataset_size} ledger records · Splink {results[0]?.splink_version} · Python {results[0]?.python_version}
              · All values from actual benchmark runs against hidden ground truth
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
