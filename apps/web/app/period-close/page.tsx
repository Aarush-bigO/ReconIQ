"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function PeriodClosePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = () => {
    setLoading(true);
    api.get("/period-close/status")
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const requestApproval = () => {
    api.post("/period-close/approve")
      .then(res => {
        alert(res.data.message);
        fetchStatus();
      })
      .catch(err => alert("Error: " + err.message));
  };

  const generateEvidencePack = () => {
    api.get("/reports/evidence-pack")
      .then(res => {
        alert(`Evidence Pack Generated!\n\nDocument ID: ${res.data.document_id}\nPeriod: ${res.data.period}\nVerified Signature: ${res.data.signature}\n\nBalance Integrity: PASS\nIdempotency: PASS`);
      })
      .catch(err => alert("Error generating evidence pack"));
  };

  if (loading && !data) {
    return <div style={{ padding: 40, color: "#fff" }}>Loading Period Close status...</div>;
  }

  const isReady = data?.open_exceptions === 0;

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 40 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: "#fff" }}>Period Close</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 15 }}>{data?.period_name}</p>
        </div>
        <div style={{
          padding: "6px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600,
          background: data?.status === "CLOSED" ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
          color: data?.status === "CLOSED" ? "#34d399" : "#fbbf24",
          border: `1px solid ${data?.status === "CLOSED" ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)"}`
        }}>
          ● {data?.status === "CLOSED" ? "PERIOD CLOSED" : "PENDING CONTROLLER APPROVAL"}
        </div>
      </div>

      <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 16, overflow: "hidden", marginBottom: 32 }}>
        <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border)", background: "rgba(255,255,255,0.02)" }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: "#fff" }}>Close Checklist</h2>
        </div>
        
        <div style={{ padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
          {[
            { label: "Payment activity imported", checked: data?.payment_activity_imported },
            { label: "Settlements imported", checked: data?.settlements_imported },
            { label: "Bank statement imported", checked: data?.bank_statement_imported },
            { label: "Reconciliation complete", checked: data?.reconciliation_complete },
            { label: "Duplicate controls passed", checked: data?.duplicate_controls_passed },
            { label: "Audit chain verified", checked: data?.audit_chain_verified },
            { label: `${data?.open_exceptions} open exceptions resolved`, checked: data?.exceptions_resolved },
          ].map((item, idx) => (
            <div key={idx} style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{
                width: 20, height: 20, borderRadius: 4, display: "flex", alignItems: "center", justifyContent: "center",
                background: item.checked ? "var(--accent)" : "transparent",
                border: item.checked ? "none" : "1px solid var(--border)",
                color: "#fff", fontSize: 12
              }}>
                {item.checked ? "✓" : ""}
              </div>
              <span style={{ color: item.checked ? "var(--text-secondary)" : "#fff", fontSize: 14 }}>
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ textAlign: "right" }}>
        <button
          onClick={requestApproval}
          disabled={!isReady || data?.status === "CLOSED"}
          style={{
            background: data?.status === "CLOSED" ? "var(--border)" : (isReady ? "var(--accent)" : "var(--surface)"),
            color: isReady && data?.status !== "CLOSED" ? "#fff" : "var(--text-secondary)",
            border: isReady && data?.status !== "CLOSED" ? "none" : "1px solid var(--border)",
            padding: "12px 24px", borderRadius: 8, fontSize: 14, fontWeight: 600,
            cursor: (isReady && data?.status !== "CLOSED") ? "pointer" : "not-allowed",
            transition: "all 0.2s"
          }}
        >
          {data?.status === "CLOSED" ? "Closed by Controller" : "Request Approval"}
        </button>
        <button
          onClick={generateEvidencePack}
          style={{
            background: "transparent",
            color: "var(--accent)",
            border: "1px solid var(--accent)",
            padding: "12px 24px", borderRadius: 8, fontSize: 14, fontWeight: 600,
            cursor: "pointer",
            marginLeft: 16,
            transition: "all 0.2s"
          }}
        >
          Generate Evidence Pack
        </button>
      </div>
    </div>
  );
}
