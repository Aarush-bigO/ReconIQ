"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ControlsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/controls/run")
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to run controls", err);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: 32, maxWidth: 1000, margin: "0 auto" }}>
      <div className="animate-3d" style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8, color: "#0F172A" }}>Control Center</h1>
        <p style={{ color: "var(--text-secondary)" }}>Continuous evaluation of enterprise financial invariants.</p>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: 60, color: "var(--text-secondary)" }}>
          <div className="pulse-dot" style={{ background: "var(--accent)", width: 12, height: 12, borderRadius: "50%", margin: "0 auto 16px" }} />
          Running Invariant Checks...
        </div>
      ) : data ? (
        <div>
          <div style={{
            padding: 24, borderRadius: 12, marginBottom: 32,
            background: data.status === "PASS" ? "rgba(16,185,129,0.05)" : "rgba(239,68,68,0.05)",
            border: `1px solid ${data.status === "PASS" ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)"}`
          }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, color: data.status === "PASS" ? "#34d399" : "#f87171", marginBottom: 8 }}>
              {data.status === "PASS" ? "✓ All Controls Passing" : "⚠ Controls Failed"}
            </h2>
            <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
              These checks verify mathematical constraints and logical assertions against the immutable financial event log.
            </p>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {data.controls.map((control: any, idx: number) => (
              <div key={idx} style={{
                background: "var(--surface)", border: "1px solid var(--border)",
                borderRadius: 12, padding: 24, display: "flex", justifyContent: "space-between", alignItems: "center"
              }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                    <div style={{
                      width: 28, height: 28, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                      background: control.status === "PASS" ? "rgba(16,185,129,0.1)" : "rgba(239,68,68,0.1)",
                      color: control.status === "PASS" ? "#10b981" : "#ef4444",
                      fontSize: 14, fontWeight: 700
                    }}>
                      {control.status === "PASS" ? "✓" : "!"}
                    </div>
                    <h3 style={{ fontSize: 16, fontWeight: 600, color: "#0F172A" }}>{control.name}</h3>
                  </div>
                  <p style={{ color: "var(--text-secondary)", fontSize: 14, marginLeft: 40 }}>{control.message}</p>
                </div>
                
                {control.status === "FAIL" && (
                  <button style={{
                    padding: "8px 16px", borderRadius: 6, background: "rgba(239,68,68,0.1)",
                    color: "#f87171", border: "1px solid rgba(239,68,68,0.2)", cursor: "pointer",
                    fontSize: 13, fontWeight: 600
                  }}>
                    View Evidence
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div style={{ color: "var(--text-secondary)" }}>Failed to load control data.</div>
      )}
    </div>
  );
}
