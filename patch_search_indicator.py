import re

with open("apps/web/app/transactions/page.tsx", "r") as f:
    content = f.read()

new_header = """      <div className="page-header" style={{ paddingBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: "#0F172A", margin: 0 }}>Transactions</h1>
            <p style={{ fontSize: 14, color: "var(--muted)", marginTop: 6, marginBottom: 0 }}>
              {total} canonical records across all sources {search && `(searching: "${search}")`}
            </p>
            {search && (
              <button onClick={() => { setSearch(""); window.history.replaceState({}, '', '/transactions'); }} style={{ marginTop: 8, padding: "4px 8px", fontSize: 11, background: "rgba(239,68,68,0.1)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 4, cursor: "pointer" }}>
                Clear Search ✕
              </button>
            )}
          </div>"""

content = re.sub(r'      <div className="page-header" style=\{\{ paddingBottom: 24 \}\}>[\s\S]*?</div>', new_header, content, count=1)

with open("apps/web/app/transactions/page.tsx", "w") as f:
    f.write(content)
