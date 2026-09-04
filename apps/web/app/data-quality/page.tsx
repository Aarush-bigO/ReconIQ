"use client";
export default function DataQualityPage() {
  const sources = [
    { name: "RAZORPAY", icon: "💎", checks: [
      { label: "Schema Validation", status: "PASS", color: "#34D399" },
      { label: "Required Fields", status: "PASS", color: "#34D399" },
      { label: "Currency Consistency", status: "PASS", color: "#34D399" },
      { label: "Reference Formats", status: "WARN", detail: "7 format variants detected", color: "#FBBF24" },
      { label: "Amount Format", status: "PASS", color: "#34D399" },
    ]},
    { name: "BANK", icon: "🏦", checks: [
      { label: "Schema Validation", status: "PASS", color: "#34D399" },
      { label: "Required Fields", status: "PASS", color: "#34D399" },
      { label: "UTR Formatting", status: "WARN", detail: "12 format variants (NEFT, UTR, IMPS)", color: "#FBBF24" },
      { label: "Currency Consistency", status: "PASS", color: "#34D399" },
    ]},
    { name: "MERCHANT LEDGER", icon: "📓", checks: [
      { label: "Schema Validation", status: "PASS", color: "#34D399" },
      { label: "Required Fields", status: "PASS", color: "#34D399" },
      { label: "Duplicate Detection", status: "WARN", detail: "4 duplicate reference records", color: "#FBBF24" },
      { label: "Reference Formats", status: "WARN", detail: "Multiple prefix conventions", color: "#FBBF24" },
    ]},
  ];

  return (
    <div>
      <div className="page-header" style={{ paddingBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h1  style={{ fontSize: 28, fontWeight: 700, color: "#0F172A", margin: 0 }}>Data Quality Profiler</h1>
          <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 6, marginBottom: 0 }}>Per-source ingestion health and schema normalization checks</p>
        </div>
      </div>
      
      <div className="page-content">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 32 }}>
          {sources.map(src => (
            <div key={src.name} className="card animate-3d fade-in" style={{ padding: 32 }}>
              <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent)", marginBottom: 24, display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 20 }}>{src.icon}</span> {src.name}
              </div>
              {src.checks.map((check, i) => (
                <div key={check.label} style={{ 
                  display: "flex", justifyContent: "space-between", alignItems: "flex-start", 
                  padding: "16px 0", borderBottom: i === src.checks.length -1 ? "none" : "1px solid rgba(255,255,255,0.05)" 
                }}>
                  <div>
                    <div style={{ fontSize: 14, color: "#0F172A", fontWeight: 500, marginBottom: check.detail ? 4 : 0 }}>{check.label}</div>
                    {check.detail && <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{check.detail}</div>}
                  </div>
                  <span style={{ 
                    fontSize: 12, fontWeight: 800, color: check.color, flexShrink: 0, marginLeft: 16,
                    padding: "4px 8px", background: `${check.color}15`, borderRadius: 6, border: `1px solid ${check.color}30`,
                    boxShadow: `0 0 10px ${check.color}20`
                  }}>
                    {check.status === "PASS" ? "✓" : "⚠"} {check.status}
                  </span>
                </div>
              ))}
            </div>
          ))}
        </div>
        
        <div className="fade-in" style={{ 
          marginTop: 32, padding: 24, background: "rgba(45, 104, 254, 0.05)", borderRadius: 12, 
          border: "1px solid rgba(45, 104, 254, 0.2)", fontSize: 14, color: "var(--text-secondary)", 
          lineHeight: 1.7, display: "flex", gap: 16, alignItems: "flex-start" 
        }}>
          <div style={{ fontSize: 24 }}>💡</div>
          <div>
            <strong className="text-glow-blue" style={{ color: "var(--accent)", letterSpacing: "0.05em" }}>NORMALIZATION ARCHITECTURE:</strong> Multiple reference prefix conventions (PAY-, UTR-, NEFT, payment_, TXN-) are expected across sources.
            ReconIQ deterministically normalizes these to a canonical <code style={{ color: "#0F172A", background: "#E2E8F0", padding: "2px 8px", borderRadius: 4, fontSize: 13, border: "1px solid rgba(255,255,255,0.2)" }}>reference_core</code> field
            while preserving the original source reference to maintain the <span style={{ color: "#0F172A", fontWeight: 500 }}>immutable audit trail</span>.
          </div>
        </div>
      </div>
    </div>
  );
}
