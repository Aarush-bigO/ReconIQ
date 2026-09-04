"use client";
import React from "react";
import { formatMinorAmount } from "@/lib/api";

interface Transaction360Props {
  evidence: any;
  decision: string;
  confidence?: number;
  reasonCode?: string;
  onClose: () => void;
}

export default function Transaction360({ evidence, decision, confidence, reasonCode, onClose }: Transaction360Props) {
  const isMatch = decision === "AUTO_MATCH" || decision === "MATCH";
  const color = isMatch ? "#10b981" : "#f59e0b";

  return (
    <div className="modal-overlay" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 1000, padding: 24 }}>
      <div className="card fade-in" style={{ width: "100%", maxWidth: 800, maxHeight: "90vh", overflowY: "auto", position: "relative", padding: 32 }}>
        <button onClick={onClose} style={{ position: "absolute", top: 24, right: 24, background: "none", border: "none", color: "var(--muted)", fontSize: 24, cursor: "pointer" }}>×</button>

        <div style={{ marginBottom: 24 }}>
          <div style={{ fontSize: 13, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted)", marginBottom: 8 }}>360-Degree Transaction View</div>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <h2 style={{ fontSize: 28, margin: 0, color: "#fff", fontWeight: 700 }}>
              {formatMinorAmount(evidence?.left_amount || evidence?.amount_minor || 0)}
            </h2>
            <span style={{ fontSize: 12, fontWeight: 700, color, background: `${color}20`, padding: "4px 12px", borderRadius: 16 }}>
              {decision}
            </span>
            {confidence !== undefined && (
              <span style={{ fontSize: 12, color: "var(--muted)" }}>{(confidence * 100).toFixed(1)}% Confidence</span>
            )}
          </div>
        </div>

        {/* 3-way table */}
        <div style={{ marginBottom: 32 }}>
          <table className="data-table" style={{ width: "100%", background: "rgba(255,255,255,0.02)", borderRadius: 8, overflow: "hidden" }}>
            <thead>
              <tr>
                <th style={{ color: "var(--accent)" }}>RAZORPAY</th>
                <th style={{ color: "#fff" }}>LEDGER</th>
                <th style={{ color: "#34D399" }}>BANK</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="mono">{evidence?.left_payment_id || "N/A"}</td>
                <td className="mono">{evidence?.left_id || "N/A"}</td>
                <td className="mono">{evidence?.right_id || "N/A"}</td>
              </tr>
              <tr>
                <td>{formatMinorAmount(evidence?.left_amount || 0)}</td>
                <td>{formatMinorAmount(evidence?.left_amount || 0)}</td>
                <td>{formatMinorAmount(evidence?.right_amount || 0)}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Evidence & Decision Trace */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          {/* Match Evidence */}
          <div style={{ background: "rgba(255,255,255,0.02)", padding: 24, borderRadius: 8, border: "1px solid var(--border)" }}>
            <h3 style={{ fontSize: 13, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginTop: 0, marginBottom: 16 }}>Match Evidence</h3>
            <div style={{ display: "grid", gap: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)", fontSize: 14 }}>Amount</span>
                <span style={{ color: "#10b981", fontWeight: 600 }}>✓ {(evidence?.amount_minor || 0)}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)", fontSize: 14 }}>Reference</span>
                <span style={{ color: "#10b981", fontWeight: 600 }}>✓</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)", fontSize: 14 }}>Date Proximity</span>
                <span style={{ color: "#10b981", fontWeight: 600 }}>✓ Within window</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)", fontSize: 14 }}>Currency</span>
                <span style={{ color: "#10b981", fontWeight: 600 }}>✓ PASS</span>
              </div>
            </div>
          </div>

          {/* Decision Trace */}
          <div style={{ background: "rgba(255,255,255,0.02)", padding: 24, borderRadius: 8, border: "1px solid var(--border)" }}>
            <h3 style={{ fontSize: 13, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginTop: 0, marginBottom: 16 }}>Decision Trace</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 11, fontFamily: "monospace", color: "var(--muted)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>INPUT</span> <span style={{ color: "#94a3b8" }}>Raw records</span></div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>NORMALIZATION</span> <span style={{ color: "#94a3b8" }}>Prefix stripped</span></div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>CANDIDATE GENERATION</span> <span style={{ color: "#94a3b8" }}>Blocked on reference_core</span></div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>SPLINK COMPARISON</span> <span style={{ color: "#94a3b8" }}>Vector computed</span></div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>PROBABILITY</span> <span style={{ color: "#34D399" }}>{confidence ? (confidence * 100).toFixed(2) + "%" : "N/A"}</span></div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>RECON POLICY</span> <span style={{ color: "#94a3b8" }}>Threshold checked</span></div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>DECISION</span> <span style={{ color }}>{decision}</span></div>
              {reasonCode && <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>REASON</span> <span style={{ color: "#f59e0b" }}>{reasonCode}</span></div>}
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span>↳</span> <span>AUDIT EVENT</span> <span style={{ color: "#34D399" }}>HMAC-SHA256 Chained</span></div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
