"use client";
import { useState, useEffect } from "react";
import { api, formatMinorAmount } from "@/lib/api";

export default function SettlementsPage() {
  const [settlements, setSettlements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSettlement, setSelectedSettlement] = useState<any>(null);

  useEffect(() => {
    api.listSettlements()
      .then(res => setSettlements(res.batches || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const statusColor: Record<string, string> = { RECONCILED: "#10b981", PARTIAL: "#f59e0b", PENDING: "#ef4444", VARIANCE: "#ef4444" };

  return (
    <div>
      <div className="page-header" style={{ paddingBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#0F172A", margin: 0 }}>Settlements</h1>
        <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 6, marginBottom: 0 }}>Settlement operations and bank reconciliation</p>
      </div>
      <div className="page-content">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
          {[
            { label: "Total Expected", value: "₹12.84L", color: "#0F172A" },
            { label: "Bank Received", value: "₹12.31L", color: "#10b981" },
            { label: "Variance", value: "₹53,420", color: "#f59e0b" },
            { label: "Reconciled", value: "95.8%", color: "#3b82f6" },
          ].map(k => (
            <div key={k.label} className="kpi-card animate-3d animate-3d">
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--muted)", marginBottom: 8 }}>{k.label}</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: k.color }}>{k.value}</div>
            </div>
          ))}
        </div>
        <div className="table-wrapper animate-3d">
          <table className="data-table animate-3d">
            <thead><tr><th>Settlement</th><th>Gross</th><th>Fees</th><th>Tax</th><th>Net</th><th>Bank Credit</th><th>Variance</th><th>Status</th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={8} style={{ textAlign: "center", color: "var(--muted)" }}>Loading settlements...</td></tr> :
              settlements.length === 0 ? <tr><td colSpan={8} style={{ textAlign: "center", color: "var(--muted)" }}>No settlements found</td></tr> :
              settlements.map(s => (
                <tr key={s.settlement_id} onClick={() => setSelectedSettlement(s)} style={{ cursor: "pointer" }}>
                  <td className="mono" style={{ color: "#3b82f6" }}>{s.settlement_id}</td>
                  <td style={{ fontWeight: 600 }}>{formatMinorAmount(s.total_gross_minor)}</td>
                  <td style={{ color: "var(--muted)" }}>{formatMinorAmount(s.total_fees_minor)}</td>
                  <td style={{ color: "var(--muted)" }}>{formatMinorAmount(s.total_tax_minor)}</td>
                  <td style={{ fontWeight: 600 }}>{formatMinorAmount(s.expected_net_minor)}</td>
                  <td>{s.actual_credit_minor ? formatMinorAmount(s.actual_credit_minor) : "Pending"}</td>
                  <td style={{ color: s.variance_minor === 0 ? "#10b981" : "#ef4444" }}>{formatMinorAmount(Math.abs(s.variance_minor || 0))}</td>
                  <td>
                    <span style={{ fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 4, color: statusColor[s.status || "PENDING"] || "#fff", background: `${statusColor[s.status || "PENDING"] || "#64748b"}15` }}>
                      {s.status || "PENDING"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Settlement Detail Timeline Modal */}
        {selectedSettlement && (
          <div className="modal-overlay" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 1000, padding: 24 }}>
            <div className="card animate-3d fade-in" style={{ width: "100%", maxWidth: 600, position: "relative", padding: 32 }}>
              <button onClick={() => setSelectedSettlement(null)} style={{ position: "absolute", top: 24, right: 24, background: "none", border: "none", color: "var(--muted)", fontSize: 24, cursor: "pointer" }}>×</button>
              <h2 style={{ margin: 0, marginBottom: 8 }}>Settlement Timeline</h2>
              <div className="mono" style={{ color: "var(--muted)", fontSize: 13, marginBottom: 24 }}>{selectedSettlement.settlement_id}</div>

              <div style={{ display: "grid", gap: 12, marginBottom: 24 }}>
                <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: 8 }}>
                  <span style={{ color: "var(--muted)" }}>Gross Expected</span>
                  <span>{formatMinorAmount(selectedSettlement.total_gross_minor)}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: 8 }}>
                  <span style={{ color: "var(--muted)" }}>Fees</span>
                  <span style={{ color: "#ef4444" }}>- {formatMinorAmount(selectedSettlement.total_fees_minor)}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: 8 }}>
                  <span style={{ color: "var(--muted)" }}>Tax</span>
                  <span style={{ color: "#ef4444" }}>- {formatMinorAmount(selectedSettlement.total_tax_minor)}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: 8 }}>
                  <span style={{ fontWeight: 600, color: "#0F172A" }}>Net Expected</span>
                  <span style={{ fontWeight: 600, color: "#0F172A" }}>{formatMinorAmount(selectedSettlement.expected_net_minor)}</span>
                </div>
              </div>

              <div style={{ padding: 16, background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)", borderRadius: 8 }}>
                <h3 style={{ margin: 0, marginBottom: 8, fontSize: 14, color: "#10b981" }}>Bank Received</h3>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 24, fontWeight: 700 }}>{selectedSettlement.actual_credit_minor ? formatMinorAmount(selectedSettlement.actual_credit_minor) : "Pending"}</span>
                  {selectedSettlement.variance_minor === 0 && <span style={{ color: "#10b981", fontWeight: 600 }}>✓ Reconciled</span>}
                </div>
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}
