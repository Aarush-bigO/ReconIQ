"use client";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, formatMinorAmount } from "@/lib/api";

const SOURCES = ["All", "razorpay", "ledger", "bank"];

function SourceBadge({ source }: { source: string }) {
  const colors: Record<string, { bg: string; color: string }> = {
    razorpay: { bg: "rgba(59,130,246,0.12)", color: "#3b82f6" },
    ledger:   { bg: "rgba(139,92,246,0.12)", color: "#8b5cf6" },
    bank:     { bg: "rgba(16,185,129,0.12)", color: "#10b981" },
  };
  const c = colors[source] || { bg: "rgba(255,255,255,0.08)", color: "#475569" };
  return (
    <span style={{ padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600, background: c.bg, color: c.color }}>
      {source.toUpperCase()}
    </span>
  );
}

export default function TransactionsPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [source, setSource] = useState("All");
  const [search, setSearch] = useState("");
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      setSearch(params.get("search") || "");
    }
  }, []);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    setLoading(true);
    api.listTransactions({ source: source === "All" ? "" : source, search })
      .then(r => { setRecords(r.records || []); setTotal(r.total || 0); })
      .catch(() => setRecords([]))
      .finally(() => setLoading(false));
  }, [source, search]);

  return (
    <div>
      <div className="page-header" style={{ paddingBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: "#0F172A", margin: 0 }}>Transactions</h1>
            <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 6, marginBottom: 0 }}>
              {total} canonical records across all sources {search && `(searching: "${search}")`}
            </p>
            {search && (
              <button onClick={() => { setSearch(""); window.history.replaceState({}, '', '/transactions'); }} style={{ marginTop: 8, padding: "4px 8px", fontSize: 11, background: "rgba(239,68,68,0.1)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 4, cursor: "pointer" }}>
                Clear Search ✕
              </button>
            )}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {SOURCES.map(s => (
              <button key={s} onClick={() => setSource(s)}
                style={{
                  padding: "7px 14px", borderRadius: 6, fontSize: 12, fontWeight: 500, cursor: "pointer",
                  background: source === s ? "rgba(59,130,246,0.15)" : "rgba(255,255,255,0.04)",
                  border: source === s ? "1px solid rgba(59,130,246,0.3)" : "1px solid var(--border)",
                  color: source === s ? "#3b82f6" : "#94a3b8",
                  transition: "all 0.15s ease",
                }}>
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="page-content" style={{ display: "grid", gridTemplateColumns: selected ? "1fr 420px" : "1fr", gap: 24 }}>
        {/* Table */}
        <div className="table-wrapper animate-3d">
          {loading ? (
            <div style={{ padding: 48, textAlign: "center", color: "var(--muted)" }}>
              <div className="skeleton" style={{ height: 16, width: "60%", margin: "0 auto 12px" }} />
              <div className="skeleton" style={{ height: 16, width: "40%", margin: "0 auto" }} />
            </div>
          ) : (
            <table className="data-table animate-3d">
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Record ID</th>
                  <th>Reference</th>
                  <th>Ref Core</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r: any) => (
                  <tr key={r.canonical_id} onClick={() => setSelected(r)} style={{ cursor: "pointer" }}>
                    <td><SourceBadge source={r.source} /></td>
                    <td className="mono" style={{ color: "#475569" }}>{r.source_record_id}</td>
                    <td className="mono" style={{ color: "#475569" }}>{r.source_reference}</td>
                    <td className="mono" style={{ color: "#3b82f6", fontWeight: 600 }}>{r.reference_core}</td>
                    <td style={{ fontWeight: 600 }}>{formatMinorAmount(r.amount_minor)}</td>
                    <td>
                      <span style={{
                        padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600,
                        background: r.status === "captured" || r.status === "credited" || r.status === "posted"
                          ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
                        color: r.status === "captured" || r.status === "credited" || r.status === "posted"
                          ? "#10b981" : "#f59e0b",
                      }}>{r.status}</span>
                    </td>
                    <td style={{ color: "var(--muted)", fontSize: 12 }}>{r.event_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* 360° Detail Panel */}
        {selected && (
          <div className="card animate-3d fade-in" style={{ padding: 24, alignSelf: "start", position: "sticky", top: 24, background: "var(--card)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-main)" }}>360° Transaction View</div>
              <button onClick={() => setSelected(null)} style={{ background: "none", border: "none", color: "var(--muted)", cursor: "pointer", fontSize: 18 }}>×</button>
            </div>

            <div style={{ textAlign: "center", padding: "20px 0 24px", borderBottom: "1px solid var(--border)", marginBottom: 20 }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--text-main)" }}>{formatMinorAmount(selected.amount_minor)}</div>
              <div className="mono" style={{ color: "var(--muted)", marginTop: 4 }}>{selected.source_record_id}</div>
              <SourceBadge source={selected.source} />
            </div>

            {Object.entries({
              "Source Reference": selected.source_reference,
              "Reference Core": selected.reference_core,
              "Currency": selected.currency,
              "Type": selected.transaction_type,
              "Status": selected.status,
              "Event Date": selected.event_date,
              "Payment ID": selected.payment_id || "—",
              "Order ID": selected.order_id || "—",
              "Settlement ID": selected.settlement_id || "—",
              "UTR": selected.utr || "—",
              "Fee": selected.fee_minor ? formatMinorAmount(selected.fee_minor) : "—",
              "Tax": selected.tax_minor ? formatMinorAmount(selected.tax_minor) : "—",
            }).map(([k, v]) => (
              <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                <span style={{ fontSize: 12, color: "var(--muted)" }}>{k}</span>
                <span className="mono" style={{ fontSize: 12, color: "var(--text-main)", textAlign: "right", maxWidth: "60%" }}>{String(v)}</span>
              </div>
            ))}

            {selected.normalization_trace && (
              <div style={{ marginTop: 16, padding: 12, background: "rgba(59,130,246,0.06)", borderRadius: 8, border: "1px solid rgba(59,130,246,0.15)" }}>
                <div style={{ fontSize: 11, color: "var(--accent)", fontWeight: 600, marginBottom: 8 }}>Normalization Trace</div>
                <div className="mono" style={{ fontSize: 11, color: "var(--muted)" }}>
                  <div>Raw: {selected.normalization_trace.raw}</div>
                  <div>Normalizer: {selected.normalization_trace.normalizer}</div>
                  <div>Core: <span style={{ color: "var(--accent)" }}>{selected.normalization_trace.normalized}</span></div>
                </div>
              </div>
            )}

            <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid var(--border)", textAlign: "center" }}>
              <button 
                onClick={() => {
                  api.getTransaction360(selected.canonical_id)
                    .then(res => {
                      if (res.match_evidence) {
                        alert(`Match Decision: ${res.match_evidence.decision}\nConfidence: ${(res.match_evidence.probability * 100).toFixed(1)}%\nReason: ${res.match_evidence.reason_code}`);
                      } else {
                        alert("No match decision trace available for this record yet.");
                      }
                    })
                    .catch(() => alert("Failed to fetch decision trace."));
                }}
                style={{ fontSize: 13, fontWeight: 600, color: "var(--accent)", textDecoration: "none", background: "none", border: "none", cursor: "pointer" }}
              >
                View Decision Trace →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
