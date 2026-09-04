"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function AuditPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [verification, setVerification] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    Promise.all([api.getAuditTrail(), api.verifyAuditChain()])
      .then(([trail, verify]) => { setEvents(trail.events || []); setVerification(verify); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function verify() {
    setVerifying(true);
    try { const r = await api.verifyAuditChain(); setVerification(r); }
    catch (e) {} finally { setVerifying(false); }
  }

  const actionColor: Record<string, string> = {
    INGESTED: "#3b82f6",
    NORMALIZED: "#8b5cf6",
    MATCH_CONFIRMED: "#10b981",
    EXCEPTION_CREATED: "#ef4444",
    EXCEPTION_REVIEWED: "#f59e0b",
    EXPLANATION_GENERATED: "#8b5cf6",
    RECONCILIATION_COMPLETED: "#10b981",
    RECONCILIATION_STARTED: "#3b82f6",
  };

  return (
    <div>
      <div className="page-header" style={{ paddingBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "#0F172A", margin: 0 }}>Audit Trail</h1>
          <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 6, marginBottom: 0 }}>
            Tamper-evident SHA-256 hash-chained event log
          </p>
        </div>
        <button className="btn-primary" onClick={verify} disabled={verifying}>
          {verifying ? "Verifying..." : "🔐 Verify Chain"}
        </button>
      </div>

      <div className="page-content">
        {/* Chain verification status */}
        {verification && (
          <div className="fade-in" style={{
            padding: 20, borderRadius: 12, marginBottom: 24,
            background: verification.valid ? "rgba(16,185,129,0.06)" : "rgba(239,68,68,0.1)",
            border: `1px solid ${verification.valid ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.3)"}`,
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ fontSize: 32 }}>{verification.valid ? "✓" : "⚠"}</div>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: verification.valid ? "#10b981" : "#ef4444" }}>
                    AUDIT CHAIN {verification.status}
                  </div>
                  <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>{verification.message}</div>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#0F172A" }}>{verification.event_count}</div>
                <div style={{ fontSize: 12, color: "var(--muted)" }}>events verified</div>
              </div>
            </div>
          </div>
        )}

        {/* Events table */}
        <div className="table-wrapper animate-3d">
          {loading ? (
            <div style={{ padding: 48, textAlign: "center", color: "var(--muted)" }}>Loading audit events...</div>
          ) : events.length === 0 ? (
            <div style={{ padding: 48, textAlign: "center", color: "var(--muted)" }}>
              No audit events. Run a reconciliation to generate events.
            </div>
          ) : (
            <table className="data-table animate-3d">
              <thead>
                <tr>
                  <th>Event ID</th>
                  <th>Action</th>
                  <th>Record</th>
                  <th>Decision</th>
                  <th>Confidence</th>
                  <th>Timestamp</th>
                  <th>Hash</th>
                </tr>
              </thead>
              <tbody>
                {[...events].reverse().map((evt: any) => (
                  <tr key={evt.event_id}>
                    <td className="mono" style={{ color: "#475569", fontSize: 11 }}>{evt.event_id}</td>
                    <td>
                      <span style={{
                        fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 4,
                        color: actionColor[evt.action] || "#94a3b8",
                        background: `${actionColor[evt.action] || "#94a3b8"}15`,
                      }}>{evt.action}</span>
                    </td>
                    <td className="mono" style={{ fontSize: 11, color: "var(--muted)" }}>
                      {evt.record_id?.slice(0, 20)}...
                    </td>
                    <td style={{ fontSize: 12, color: "#475569" }}>{evt.decision || "—"}</td>
                    <td style={{ fontSize: 12, color: evt.confidence > 0.9 ? "#10b981" : "var(--muted)" }}>
                      {evt.confidence > 0 ? `${(evt.confidence * 100).toFixed(1)}%` : "—"}
                    </td>
                    <td style={{ fontSize: 11, color: "var(--muted)" }}>
                      {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : "—"}
                    </td>
                    <td className="mono" style={{ fontSize: 10, color: "#3b82f6" }}>
                      {evt.current_hash?.slice(0, 12)}...
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={{ marginTop: 16, padding: 16, background: "#F8FAFC", borderRadius: 8, border: "1px solid var(--border)", fontSize: 12, color: "var(--muted)", lineHeight: 1.6 }}>
          <strong style={{ color: "#1E293B" }}>SHA-256 Hash Chain:</strong> Each event's hash is computed from its payload + the previous event's hash.
          Any modification to any event will produce a different hash, breaking the chain verification. This is tamper-evident audit logging — not blockchain.
        </div>
      </div>
    </div>
  );
}
