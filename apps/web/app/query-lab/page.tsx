"use client";
import { useState } from "react";
import { api } from "@/lib/api";

const EXAMPLE_QUERIES = [
  "Show all HIGH severity exceptions",
  "Show settlements with variance greater than zero",
  "List the last 10 auto-matched transactions",
  "Show all open exceptions by amount descending",
  "What is the total reconciled value?",
  "Show unmatched bank transactions",
];

export default function QueryLabPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const executeQuery = (q?: string) => {
    const text = q || query;
    if (!text.trim()) return;
    if (q) setQuery(q);
    setLoading(true); setError(""); setResult(null);
    api.post("/query-lab/execute", { query: text })
      .then(res => { setResult(res.data); setLoading(false); })
      .catch(err => { setError(err.message || "Query failed"); setLoading(false); });
  };

  return (
    <div style={{ maxWidth: 1080 }}>

      {/* Header */}
      <div className="animate-3d" style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg, rgba(45,104,254,0.2), rgba(30,79,216,0.2))", border: "1px solid rgba(45,104,254,0.3)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, color: "var(--accent)" }}>✦</div>
          <span style={{ fontSize: 11, fontWeight: 700, color: "var(--accent)", textTransform: "uppercase", letterSpacing: "0.12em" }}>Gemini AI Powered</span>
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: "#0F172A", letterSpacing: "-0.03em", margin: 0 }}>Query Lab</h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 6 }}>
          Natural language → structured intent → deterministic read-only SQL. AI never writes to your books.
        </p>
      </div>

      {/* Search box */}
      <form onSubmit={e => { e.preventDefault(); executeQuery(); }} style={{ marginBottom: 24, position: "relative" }}>
        <div style={{
          display: "flex", alignItems: "center",
          background: "#FFFFFF", border: "1px solid rgba(45,104,254,0.3)",
          borderRadius: 14, padding: "4px 4px 4px 20px",
          boxShadow: "0 0 30px rgba(45,104,254,0.08)",
          transition: "all 0.3s ease",
        }}>
          <span style={{ fontSize: 16, color: "var(--accent)", marginRight: 12 }}>✦</span>
          <input
            type="text" value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder='Try: "Show HIGH severity exceptions" or "What is the match rate?"'
            style={{ flex: 1, background: "transparent", border: "none", color: "#0F172A", fontSize: 15, outline: "none", padding: "10px 0" }}
          />
          <button type="submit" disabled={loading || !query.trim()} className="btn-primary" style={{ borderRadius: 10, padding: "10px 24px", fontSize: 13 }}>
            {loading ? "Parsing..." : "Execute →"}
          </button>
        </div>
      </form>

      {/* Example queries */}
      {!result && !loading && (
        <div className="animate-3d" style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>Try an example</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {EXAMPLE_QUERIES.map(q => (
              <button key={q} onClick={() => executeQuery(q)} style={{
                padding: "7px 14px", borderRadius: 99, fontSize: 12, fontWeight: 500, cursor: "pointer",
                background: "rgba(45,104,254,0.05)", border: "1px solid rgba(45,104,254,0.15)",
                color: "#475569", transition: "all 0.15s ease",
              }}
                onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.background = "rgba(45,104,254,0.1)"; (e.currentTarget as HTMLButtonElement).style.color = "var(--accent)"; }}
                onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.background = "rgba(45,104,254,0.05)"; (e.currentTarget as HTMLButtonElement).style.color = "#94a3b8"; }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="card" style={{ padding: 48, textAlign: "center" }}>
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 16, marginBottom: 16 }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: "rgba(45,104,254,0.1)", border: "1px solid rgba(45,104,254,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: "var(--accent)", animation: "float 2s ease-in-out infinite" }}>✦</div>
          </div>
          <div style={{ fontSize: 14, color: "#1E293B", fontWeight: 600, marginBottom: 6 }}>Gemini is parsing your query...</div>
          <div style={{ fontSize: 12, color: "var(--muted)" }}>Natural language → structured intent → SQL execution</div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ padding: 16, background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 10, fontSize: 13, color: "#fca5a5" }}>
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          {/* Intent card */}
          <div className="card" style={{ padding: 20, borderColor: "rgba(30,79,216,0.2)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <span style={{ fontSize: 10, fontWeight: 700, color: "var(--purple)", textTransform: "uppercase", letterSpacing: "0.1em" }}>✦ Parsed Intent (Gemini AI)</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
              {result.intent && Object.entries(result.intent).map(([k, v]) => (
                <div key={k} style={{ padding: 10, background: "#F8FAFC", borderRadius: 8, border: "1px solid #E2E8F0" }}>
                  <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{k.replace(/_/g, " ")}</div>
                  <div style={{ fontSize: 12, color: "var(--purple)", fontFamily: "monospace" }}>{JSON.stringify(v)}</div>
                </div>
              ))}
            </div>

            {result.sql && (
              <div style={{ marginTop: 16, padding: 14, background: "#F1F5F9", borderRadius: 8, border: "1px solid #E2E8F0" }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>Generated SQL</div>
                <pre style={{ margin: 0, fontSize: 12, color: "var(--accent)", fontFamily: "monospace", overflowX: "auto", lineHeight: 1.6 }}>{result.sql}</pre>
              </div>
            )}
          </div>

          {/* Results table */}
          <div className="card" style={{ overflow: "hidden" }}>
            <div style={{ padding: "14px 20px", borderBottom: "1px solid #E2E8F0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: "#1E293B" }}>
                Query Results
              </span>
              <span className="badge-matched">{result.results?.length || 0} rows</span>
            </div>
            <div style={{ overflowX: "auto" }}>
              {result.results?.length > 0 ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      {Object.keys(result.results[0]).map(key => (
                        <th key={key}>{key.replace(/_/g, " ")}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.results.map((row: any, i: number) => (
                      <tr key={i}>
                        {Object.values(row).map((val: any, j: number) => (
                          <td key={j} style={{ fontFamily: typeof val === "string" && val.length > 20 ? "monospace" : undefined, fontSize: 12 }}>
                            {typeof val === "object" ? JSON.stringify(val) : String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div style={{ padding: 48, textAlign: "center", color: "var(--muted)", fontSize: 14 }}>
                  No results returned for this query.
                </div>
              )}
            </div>
          </div>

          {/* Disclaimer */}
          <div style={{ padding: "10px 14px", background: "rgba(30,79,216,0.04)", borderRadius: 8, border: "1px solid rgba(30,79,216,0.1)", fontSize: 11, color: "var(--muted)", display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ color: "var(--purple)" }}>✦</span>
            <span>Gemini AI translates natural language to <strong style={{ color: "var(--purple)" }}>read-only SQL</strong>. It never writes to, creates, or deletes financial records. Deterministic systems decide — AI only explains.</span>
          </div>
        </div>
      )}
    </div>
  );
}
