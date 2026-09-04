"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function LedgerPage() {
  const [trialBalance, setTrialBalance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/ledger/trial-balance")
      .then(res => {
        setTrialBalance(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load trial balance", err);
        setLoading(false);
      });
  }, []);

  const totalDebits = trialBalance.reduce((sum, row) => sum + row.debit_minor, 0) / 100;
  const totalCredits = trialBalance.reduce((sum, row) => sum + row.credit_minor, 0) / 100;

  return (
    <div style={{ padding: 32, maxWidth: 1000, margin: "0 auto" }}>
      <div className="animate-3d" style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8, color: "#0F172A" }}>Continuous Ledger</h1>
        <p style={{ color: "var(--text-secondary)" }}>Real-time Double-Entry Trial Balance (CQRS pattern).</p>
      </div>

      {loading ? (
        <div style={{ color: "var(--text-secondary)" }}>Loading continuous accounting state...</div>
      ) : (
        <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 12, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead>
              <tr style={{ background: "#F8FAFC", borderBottom: "1px solid var(--border)" }}>
                <th style={{ padding: "16px 24px", color: "var(--text-secondary)", fontWeight: 500, fontSize: 13 }}>ACCOUNT</th>
                <th style={{ padding: "16px 24px", color: "var(--text-secondary)", fontWeight: 500, fontSize: 13, textAlign: "right" }}>DEBITS (INR)</th>
                <th style={{ padding: "16px 24px", color: "var(--text-secondary)", fontWeight: 500, fontSize: 13, textAlign: "right" }}>CREDITS (INR)</th>
                <th style={{ padding: "16px 24px", color: "var(--text-secondary)", fontWeight: 500, fontSize: 13, textAlign: "right" }}>NET BALANCE (INR)</th>
              </tr>
            </thead>
            <tbody>
              {trialBalance.length > 0 ? trialBalance.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "16px 24px", color: "#0F172A", fontWeight: 500, fontSize: 14 }}>
                    {row.account}
                  </td>
                  <td style={{ padding: "16px 24px", color: "#0F172A", fontSize: 14, textAlign: "right" }}>
                    {(row.debit_minor / 100).toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                  </td>
                  <td style={{ padding: "16px 24px", color: "#0F172A", fontSize: 14, textAlign: "right" }}>
                    {(row.credit_minor / 100).toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                  </td>
                  <td style={{ padding: "16px 24px", color: "#0F172A", fontSize: 14, textAlign: "right" }}>
                    {(row.balance_minor / 100).toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={4} style={{ padding: "32px 24px", color: "var(--text-secondary)", textAlign: "center" }}>
                    No journal entries posted yet. (Import transactions to populate the ledger).
                  </td>
                </tr>
              )}
            </tbody>
            <tfoot>
              <tr style={{ background: "#F8FAFC" }}>
                <td style={{ padding: "16px 24px", color: "#0F172A", fontWeight: 600, fontSize: 14 }}>TOTALS</td>
                <td style={{ padding: "16px 24px", color: "#34d399", fontWeight: 600, fontSize: 14, textAlign: "right" }}>
                  {totalDebits.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                </td>
                <td style={{ padding: "16px 24px", color: "#34d399", fontWeight: 600, fontSize: 14, textAlign: "right" }}>
                  {totalCredits.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                </td>
                <td style={{ padding: "16px 24px", color: (totalDebits - totalCredits) === 0 ? "#34d399" : "#f87171", fontWeight: 600, fontSize: 14, textAlign: "right" }}>
                  {((totalDebits - totalCredits)).toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}
