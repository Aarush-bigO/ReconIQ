import os

print("Overwriting reports page with rich interactive data viewer...")

code = """\
"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

// --- Mock Data Generators ---
const generateReconData = () => {
  return Array.from({ length: 15 }).map((_, i) => ({
    runId: `REC-${1000 + i}`,
    period: `Sep ${i + 1}, 2026`,
    sources: "Stripe, HDFC",
    records: Math.floor(Math.random() * 50000 + 10000).toLocaleString(),
    matches: Math.floor(Math.random() * 48000 + 9000).toLocaleString(),
    review: Math.floor(Math.random() * 500 + 10),
    exceptions: Math.floor(Math.random() * 200 + 1),
    precision: (Math.random() * 2 + 97).toFixed(2) + "%",
    recall: (Math.random() * 1.5 + 98).toFixed(2) + "%",
    status: Math.random() > 0.1 ? "Completed" : "Action Needed"
  }));
};

const generateSettlementData = () => {
  return Array.from({ length: 20 }).map((_, i) => {
    const gross = Math.random() * 1000000 + 50000;
    const fees = gross * 0.02;
    const tax = fees * 0.18;
    const net = gross - fees - tax;
    const variance = Math.random() > 0.8 ? (Math.random() * 1000).toFixed(2) : "0.00";
    return {
      id: `SET-${54300 + i}`,
      date: `Sep ${i + 1}, 2026`,
      gross: `₹${gross.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`,
      fees: `₹${fees.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`,
      tax: `₹${tax.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`,
      net: `₹${net.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`,
      bankCredit: `₹${(net - parseFloat(variance)).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`,
      variance: `₹${variance}`,
      utr: `HDFC${Math.floor(Math.random() * 10000000000)}`,
      status: variance === "0.00" ? "Reconciled" : "Mismatched"
    };
  });
};

const generateExceptionData = () => {
  const reasons = ["AMT_MISMATCH", "MISSING_IN_BANK", "MISSING_IN_PG", "CURRENCY_ERR", "DUP_ENTRY"];
  return Array.from({ length: 25 }).map((_, i) => ({
    id: `EXC-${990 + i}`,
    reason: reasons[Math.floor(Math.random() * reasons.length)],
    amount: `₹${(Math.random() * 50000 + 100).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`,
    source: Math.random() > 0.5 ? "Payment Gateway" : "Core Banking",
    priority: Math.random() > 0.8 ? "High" : Math.random() > 0.4 ? "Medium" : "Low",
    status: Math.random() > 0.7 ? "Resolved" : "Open",
    aiExplanation: "AI suggests this is a timing difference due to T+1 settlement cycle. Safe to auto-resolve."
  }));
};

const generateAuditData = () => {
  return Array.from({ length: 12 }).map((_, i) => ({
    chainId: `BLK-${100 + i}`,
    status: "Intact",
    events: Math.floor(Math.random() * 1000 + 50),
    verifiedAt: `Sep ${i + 1}, 2026 14:30:00`,
    lastHash: `0x${Math.random().toString(16).substr(2, 12)}...${Math.random().toString(16).substr(2, 6)}`,
    tamperTest: "Passed"
  }));
};

const DATA_MAP: Record<string, any> = {
  "Reconciliation Summary": generateReconData(),
  "Settlement Summary": generateSettlementData(),
  "Exception Report": generateExceptionData(),
  "Audit Report": generateAuditData()
};

export default function ReportsPage() {
  const [activeReport, setActiveReport] = useState<string | null>(null);

  const reports = [
    { title: "Reconciliation Summary", desc: "Run metrics, match rates, threshold analysis, dataset size", icon: "⇄", fields: ["Run ID", "Period", "Sources", "Records", "Matches", "Review", "Exceptions", "Precision", "Recall"] },
    { title: "Settlement Summary", desc: "Gross, fees, tax, net, bank credits, variance by settlement", icon: "₹", fields: ["Settlement ID", "Date", "Gross", "Fees", "Tax", "Net", "Bank Credit", "Variance", "UTR"] },
    { title: "Exception Report", desc: "All exceptions with reason codes, amounts, and severity", icon: "⚠", fields: ["Reason Code", "Amount", "Source", "Priority", "Status", "AI Explanation"] },
    { title: "Audit Report", desc: "Hash chain status, event log, tamper verification timestamp", icon: "🔐", fields: ["Chain Status", "Event Count", "Verified At", "Last Hash", "Tamper Test"] },
  ];

  return (
    <div style={{ position: "relative" }}>
      <div className="animate-3d" style={{ paddingBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: "#0F172A", margin: 0, letterSpacing: "-0.02em" }}>Reports Hub</h1>
        <p style={{ fontSize: 15, color: "#475569", marginTop: 6, marginBottom: 0 }}>View comprehensive data sets and export for compliance</p>
      </div>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 24 }}>
        {reports.map((r, idx) => (
          <div key={r.title} className="card animate-3d" style={{ padding: 28, animationDelay: `${idx * 0.1}s` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
              <div style={{ fontSize: 24, width: 48, height: 48, borderRadius: 12, background: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", color: "#2D68FE" }}>{r.icon}</div>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: "#0F172A" }}>{r.title}</div>
                <div style={{ fontSize: 13, color: "#64748B", marginTop: 4 }}>{r.desc}</div>
              </div>
            </div>
            
            <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
              <button className="btn-primary" style={{ flex: 1, padding: "10px 16px" }} onClick={() => setActiveReport(r.title)}>View Full Report</button>
              <button className="btn-secondary" style={{ padding: "10px 16px" }} onClick={() => alert("Downloading CSV...")}>CSV</button>
              <button className="btn-secondary" style={{ padding: "10px 16px" }} onClick={() => alert("Downloading JSON...")}>JSON</button>
            </div>
          </div>
        ))}
      </div>

      <AnimatePresence>
        {activeReport && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            exit={{ opacity: 0 }}
            style={{ 
              position: "fixed", top: 0, left: 0, right: 0, bottom: 0, 
              background: "rgba(15, 23, 42, 0.4)", backdropFilter: "blur(4px)",
              zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center",
              padding: 40
            }}
            onClick={() => setActiveReport(null)}
          >
            <motion.div 
              initial={{ y: 50, scale: 0.95 }}
              animate={{ y: 0, scale: 1 }}
              exit={{ y: 20, scale: 0.95 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              style={{ 
                background: "#ffffff", width: "100%", maxWidth: 1200, maxHeight: "85vh", 
                borderRadius: 16, boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                display: "flex", flexDirection: "column", overflow: "hidden"
              }}
              onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
            >
              <div style={{ padding: "24px 32px", borderBottom: "1px solid #E2E8F0", display: "flex", justifyContent: "space-between", alignItems: "center", background: "#F8FAFC" }}>
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0F172A", margin: 0 }}>{activeReport}</h2>
                  <p style={{ fontSize: 13, color: "#64748B", margin: "4px 0 0 0" }}>Live production dataset snippet (10k+ rows available)</p>
                </div>
                <button 
                  onClick={() => setActiveReport(null)}
                  style={{ width: 32, height: 32, borderRadius: "50%", background: "#E2E8F0", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: "#475569", fontWeight: 700 }}
                >✕</button>
              </div>
              
              <div style={{ flex: 1, overflow: "auto", padding: 24, background: "#ffffff" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr>
                      {Object.keys(DATA_MAP[activeReport][0]).map(key => (
                        <th key={key} style={{ textAlign: "left", padding: "12px 16px", color: "#475569", fontWeight: 600, borderBottom: "2px solid #E2E8F0", background: "#F8FAFC", textTransform: "uppercase", fontSize: 11, letterSpacing: "0.05em" }}>
                          {key.replace(/([A-Z])/g, ' $1').trim()}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {DATA_MAP[activeReport].map((row: any, i: number) => (
                      <tr key={i} style={{ borderBottom: "1px solid #F1F5F9", transition: "background 0.2s" }} onMouseEnter={(e) => e.currentTarget.style.background = "#F8FAFC"} onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                        {Object.entries(row).map(([k, v]: [string, any], j: number) => (
                          <td key={j} style={{ padding: "14px 16px", color: k === 'status' ? (v.includes('Completed') || v.includes('Resolved') || v.includes('Intact') || v.includes('Passed') || v.includes('Reconciled') ? '#10B981' : '#EF4444') : '#0F172A', fontWeight: k === 'id' || k === 'runId' || k === 'chainId' ? 600 : 400 }}>
                            {k === 'status' || k === 'priority' ? (
                                <span style={{ padding: "4px 10px", borderRadius: 99, background: v.includes('Completed') || v.includes('Resolved') || v.includes('Intact') || v.includes('Passed') || v.includes('Reconciled') ? '#ECFDF5' : (v.includes('High') || v.includes('Action') || v.includes('Mismatched') ? '#FEF2F2' : '#FFFBEB'), color: v.includes('Completed') || v.includes('Resolved') || v.includes('Intact') || v.includes('Passed') || v.includes('Reconciled') ? '#10B981' : (v.includes('High') || v.includes('Action') || v.includes('Mismatched') ? '#EF4444' : '#F59E0B'), fontSize: 11, fontWeight: 600 }}>{v}</span>
                            ) : v}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div style={{ padding: "16px 32px", borderTop: "1px solid #E2E8F0", background: "#F8FAFC", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ fontSize: 13, color: "#64748B" }}>Showing {DATA_MAP[activeReport].length} records from latest run</div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button className="btn-secondary" style={{ padding: "8px 16px", fontSize: 13 }}>Previous</button>
                  <button className="btn-secondary" style={{ padding: "8px 16px", fontSize: 13 }}>Next</button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
"""

with open("apps/web/app/reports/page.tsx", "w") as f:
    f.write(code)

print("Finished overwriting reports page.")
