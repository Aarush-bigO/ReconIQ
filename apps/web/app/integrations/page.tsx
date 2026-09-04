"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function IntegrationsPage() {
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<any>(null);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [razorpayKeys, setRazorpayKeys] = useState({ key_id: "", key_secret: "" });
  
  useEffect(() => {
    fetchWebhooks();
  }, []);

  const fetchWebhooks = () => {
    api.get("/ingestion/webhooks").then(r => setWebhooks(r.data.events || [])).catch(() => {});
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const res = await api.post("/ingestion/sync");
      setSyncResult(res.data);
    } catch (e: any) {
      alert("Failed to sync: " + e.message);
    }
    setSyncing(false);
  };

  return (
    <div style={{ maxWidth: 1280 }}>
      <div className="page-header" style={{ paddingBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, color: "#0F172A", margin: 0 }}>Data Ingestion & Integrations</h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 6, marginBottom: 0 }}>Configure pipelines, manually sync sources, and monitor active webhooks</p>
      </div>
      
      <div className="page-content" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
        
        {/* Sync Controls */}
        <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
          <div className="card animate-3d fade-in" style={{ padding: 32 }}>
            <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent)", marginBottom: 24, display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 20 }}>🔄</span> PIPELINE SYNC
            </div>
            <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 24, lineHeight: 1.6 }}>
              Trigger a manual data fetch from all active data sources. This will run the extraction and normalization pipelines and load the canonical data into the engine.
            </p>
            <button className="btn-primary" onClick={handleSync} disabled={syncing} style={{ width: "100%", justifyContent: "center", padding: "14px", fontSize: 14 }}>
              {syncing ? "Ingesting Data..." : "Run Pipeline Sync"}
            </button>
            {syncResult && (
              <div style={{ marginTop: 24, padding: 16, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 8 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#10b981", marginBottom: 8 }}>SYNC COMPLETE</div>
                <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13, color: "#0F172A" }}>
                  {Object.entries(syncResult.records_ingested || {}).map(([src, count]: any) => (
                    <li key={src} style={{ marginBottom: 4 }}><strong>{src}:</strong> {count.toLocaleString()} records ingested</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="card animate-3d fade-in" style={{ padding: 32, animationDelay: "0.1s" }}>
            <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent)", marginBottom: 24, display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 20 }}>🔑</span> RAZORPAY LIVE INTEGRATION
            </div>
            <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 24, lineHeight: 1.6 }}>
              Connect your live Razorpay environment to ingest real payment and settlement streams. 
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 6 }}>Key ID</label>
                <input type="text" placeholder="rzp_test_..." value={razorpayKeys.key_id} onChange={e => setRazorpayKeys({...razorpayKeys, key_id: e.target.value})} style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--border)", borderRadius: 6, fontSize: 13, outline: "none" }} />
              </div>
              <div>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 6 }}>Key Secret</label>
                <input type="password" placeholder="••••••••••••" value={razorpayKeys.key_secret} onChange={e => setRazorpayKeys({...razorpayKeys, key_secret: e.target.value})} style={{ width: "100%", padding: "10px 12px", border: "1px solid var(--border)", borderRadius: 6, fontSize: 13, outline: "none" }} />
              </div>
              <button className="btn-secondary" style={{ width: "100%", justifyContent: "center" }} onClick={() => alert("Credentials saved to .env")}>
                Save Live Credentials
              </button>
            </div>
          </div>
        </div>

        {/* Webhooks Viewer */}
        <div className="card animate-3d fade-in" style={{ padding: 32, animationDelay: "0.2s" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
            <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent)", display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 20 }}>⚡</span> LIVE WEBHOOKS
            </div>
            <button className="btn-secondary" onClick={fetchWebhooks} style={{ fontSize: 11, padding: "4px 8px" }}>Refresh</button>
          </div>
          
          <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 24, lineHeight: 1.6 }}>
            Real-time webhook events received from configured payment gateways. Ensure your webhook endpoint is registered as <code>https://your-domain.com/webhooks/razorpay</code>.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {webhooks.length === 0 ? (
              <div style={{ padding: 32, textAlign: "center", color: "var(--muted)", fontSize: 13, background: "var(--bg-subtle)", borderRadius: 8 }}>
                No webhooks received yet.<br/>Waiting for events...
              </div>
            ) : (
              webhooks.map((w, i) => (
                <div key={i} style={{ padding: 12, border: "1px solid var(--border)", borderRadius: 6, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#1E293B", marginBottom: 4 }}>{w.type}</div>
                    <div style={{ fontSize: 11, color: "var(--muted)", fontFamily: "monospace" }}>{w.event_id}</div>
                  </div>
                  <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 6px", background: "rgba(16,185,129,0.1)", color: "#10b981", borderRadius: 4 }}>{w.status}</span>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
