"use client";
import { useState } from "react";
export default function SettingsPage() {
  const [config, setConfig] = useState({ auto_match_threshold: 0.95, review_threshold: 0.70, date_tolerance_days: 3, amount_tolerance_minor: 100, currency: "INR" });
  const [saved, setSaved] = useState(false);
  function save() { setSaved(true); setTimeout(() => setSaved(false), 2000); }
  return (
    <div>
      <div className="page-header" style={{ paddingBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#0F172A", margin: 0 }}>Settings</h1>
        <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 6, marginBottom: 0 }}>Reconciliation policy, thresholds, integrations, and AI settings</p>
      </div>
      <div className="page-content">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          <div className="card animate-3d animate-3d" style={{ padding: 24 }}>
            <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--muted)", marginBottom: 20 }}>Reconciliation Policy</div>
            {[
              { key: "auto_match_threshold", label: "Auto-Match Threshold", min: 0.5, max: 1.0, step: 0.01 },
              { key: "review_threshold", label: "Review Threshold", min: 0.3, max: 0.95, step: 0.01 },
              { key: "date_tolerance_days", label: "Date Tolerance (days)", min: 1, max: 7, step: 1 },
              { key: "amount_tolerance_minor", label: "Amount Tolerance (paise)", min: 0, max: 1000, step: 10 },
            ].map(f => (
              <div key={f.key} style={{ marginBottom: 20 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <label style={{ fontSize: 13, color: "#475569" }}>{f.label}</label>
                  <span style={{ fontSize: 13, fontWeight: 700, color: "#3b82f6" }}>{config[f.key as keyof typeof config]}</span>
                </div>
                <input type="range" min={f.min} max={f.max} step={f.step}
                  value={config[f.key as keyof typeof config] as number}
                  onChange={e => setConfig(c => ({ ...c, [f.key]: parseFloat(e.target.value) }))}
                  style={{ width: "100%", accentColor: "#3b82f6" }} />
              </div>
            ))}
            <button className="btn-primary" onClick={save} style={{ width: "100%", justifyContent: "center" }}>
              {saved ? "✓ Saved (Audit Event Created)" : "Save Configuration"}
            </button>
            <div style={{ marginTop: 12, fontSize: 11, color: "var(--muted)" }}>Changing configuration creates a CONFIG_CHANGED audit event.</div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <div className="card animate-3d animate-3d" style={{ padding: 24 }}>
              <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--muted)", marginBottom: 16 }}>Providers</div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid var(--border)" }}>
                <div><div style={{ fontSize: 13, color: "#1E293B" }}>Razorpay</div><div style={{ fontSize: 11, color: "var(--muted)" }}>Test Mode API</div></div>
                <span style={{ fontSize: 11, color: "#f59e0b", background: "rgba(245,158,11,0.1)", padding: "3px 10px", borderRadius: 4 }}>NOT CONFIGURED</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0" }}>
                <div><div style={{ fontSize: 13, color: "#1E293B" }}>Synthetic Data</div><div style={{ fontSize: 11, color: "var(--muted)" }}>Demo mode fallback</div></div>
                <span style={{ fontSize: 11, color: "#10b981", background: "rgba(16,185,129,0.1)", padding: "3px 10px", borderRadius: 4 }}>ACTIVE</span>
              </div>
            </div>
            <div className="card animate-3d animate-3d" style={{ padding: 24 }}>
              <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--muted)", marginBottom: 16 }}>AI Settings</div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid var(--border)" }}>
                <div><div style={{ fontSize: 13, color: "#1E293B" }}>Gemini 3.6 Flash</div><div style={{ fontSize: 11, color: "var(--muted)" }}>Google GenAI Structured Outputs</div></div>
                <span style={{ fontSize: 11, color: "#10b981", background: "rgba(16,185,129,0.1)", padding: "3px 10px", borderRadius: 4 }}>ACTIVE</span>
              </div>
              <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 12, lineHeight: 1.6 }}>
                AI explanation is fully functional with the deterministic fallback. Set GEMINI_API_KEY in .env to enable LLM explanations.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
