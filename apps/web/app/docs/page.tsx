"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, Code2, Database, Key, Terminal, ArrowLeft, Check, Copy } from 'lucide-react';

const CodeBlock = ({ code, language }: { code: string, language: string }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ borderRadius: '12px', overflow: 'hidden', background: '#0A0D14', border: '1px solid rgba(255,255,255,0.1)', marginTop: '24px', marginBottom: '40px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 16px', background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <span style={{ fontSize: '12px', fontFamily: 'monospace', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{language}</span>
        <button onClick={handleCopy} style={{ color: '#6B7280', background: 'transparent', border: 'none', cursor: 'pointer' }}>
          {copied ? <Check style={{ width: 16, height: 16, color: '#34D399' }} /> : <Copy style={{ width: 16, height: 16 }} />}
        </button>
      </div>
      <div style={{ padding: '20px', overflowX: 'auto' }}>
        <pre style={{ fontSize: '14px', fontFamily: 'monospace', lineHeight: '1.6', margin: 0 }} dangerouslySetInnerHTML={{ __html: code }} />
      </div>
    </div>
  );
};

export default function DocsPage() {
  const sections = [
    { id: 'intro', title: 'Introduction', icon: Terminal },
    { id: 'auth', title: 'Authentication', icon: Key },
    { id: 'streams', title: 'Streaming Data', icon: Database },
    { id: 'matching', title: 'AI Matching Engine', icon: Code2 },
  ];

  const [activeSection, setActiveSection] = useState('intro');

  return (
    <div style={{ minHeight: '100vh', background: '#06080F', color: '#fff', fontFamily: "'Satoshi', sans-serif", display: 'flex', flexDirection: 'column' }}>
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://api.fontshare.com/v2/css?f[]=satoshi@900,700,500,400&display=swap');
        * { box-sizing: border-box; }
        body { margin: 0; }
        a { text-decoration: none; }
      `}} />
      
      {/* ── HEADER ── */}
      <header style={{ position: 'sticky', top: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 32px', height: '72px', borderBottom: '1px solid rgba(255,255,255,0.1)', background: 'rgba(6,8,15,0.8)', backdropFilter: 'blur(16px)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '48px' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <motion.div whileHover={{ rotate: 180 }} transition={{ duration: 0.5 }} style={{ width: 32, height: 32, borderRadius: 6, background: '#2563EB', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 900, boxShadow: '0 0 15px rgba(37,99,235,0.4)', color: '#fff' }}>
               R
            </motion.div>
            <span style={{ fontWeight: 700, fontSize: '18px', letterSpacing: '-0.02em', color: '#fff' }}>ReconIQ Docs</span>
          </Link>
          <nav style={{ display: 'flex', gap: '24px', fontSize: '14px', fontWeight: 500, color: '#9CA3AF' }}>
            <Link href="/docs" style={{ color: '#fff' }}>API Reference</Link>
            <Link href="/docs" style={{ color: '#9CA3AF' }}>Guides</Link>
            <Link href="/docs" style={{ color: '#9CA3AF' }}>SDKs</Link>
          </nav>
        </div>
        <Link href="/dashboard" style={{ padding: '8px 20px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', fontSize: '14px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', color: '#fff' }}>
          <ArrowLeft style={{ width: 16, height: 16 }} /> Back to App
        </Link>
      </header>

      <div style={{ flex: 1, display: 'flex', maxWidth: '1440px', width: '100%', margin: '0 auto', position: 'relative' }}>
        {/* ── SIDEBAR ── */}
        <aside style={{ width: '280px', flexShrink: 0, borderRight: '1px solid rgba(255,255,255,0.1)', padding: '32px', position: 'sticky', top: '72px', height: 'calc(100vh - 72px)', overflowY: 'auto' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '24px' }}>Getting Started</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {sections.map(section => (
              <button 
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                style={{ 
                  display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 16px', borderRadius: '8px', fontSize: '14px', fontWeight: 500, textAlign: 'left', cursor: 'pointer', transition: 'all 0.2s ease',
                  ...(activeSection === section.id 
                    ? { background: 'rgba(59,130,246,0.1)', color: '#60A5FA', border: '1px solid rgba(59,130,246,0.2)' } 
                    : { background: 'rgba(0,0,0,0)', color: '#9CA3AF', border: '1px solid rgba(0,0,0,0)' })
                }}
              >
                <section.icon style={{ width: 16, height: 16 }} />
                {section.title}
              </button>
            ))}
          </div>
        </aside>

        {/* ── MAIN CONTENT ── */}
        <main style={{ flex: 1, padding: '48px 80px', maxWidth: '900px', paddingBottom: '128px' }}>
          
          <AnimatePresence mode="wait">
            {activeSection === 'intro' && (
              <motion.div key="intro" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 12px', borderRadius: '999px', border: '1px solid rgba(59,130,246,0.3)', background: 'rgba(59,130,246,0.1)', fontSize: '12px', fontWeight: 700, color: '#60A5FA', marginBottom: '24px' }}>
                  v4.0.0 (Latest)
                </div>
                <h1 style={{ fontSize: '48px', fontWeight: 900, letterSpacing: '-0.02em', margin: '0 0 24px 0' }}>Welcome to ReconIQ</h1>
                <p style={{ fontSize: '20px', color: '#9CA3AF', lineHeight: '1.6', margin: '0 0 32px 0' }}>
                  The ReconIQ API allows you to programmatically stream massive payment datasets, execute AI-driven fuzzy matching, and automatically resolve financial anomalies in milliseconds.
                </p>
                
                <h2 style={{ fontSize: '24px', fontWeight: 700, margin: '64px 0 24px 0', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>Installation</h2>
                <p style={{ color: '#9CA3AF', marginBottom: '16px' }}>Install the official Python SDK to interact with the matching engine.</p>
                <CodeBlock 
                  language="bash" 
                  code={`<span style="color:#fff">pip install</span> <span style="color:#60A5FA">reconiq-sdk</span>`} 
                />

                <h2 style={{ fontSize: '24px', fontWeight: 700, margin: '64px 0 24px 0', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>Quick Start</h2>
                <CodeBlock 
                  language="python" 
                  code={`<span style="color:#C084FC">import</span> recon_iq\n\n<span style="color:#6B7280"># 1. Initialize the engine</span>\nclient = recon_iq.Client(api_key=<span style="color:#34D399">"riq_live_xyz123"</span>)\n\n<span style="color:#6B7280"># 2. Check engine health</span>\nstatus = client.health.ping()\n<span style="color:#60A5FA">print</span>(status) <span style="color:#6B7280"># -> { "status": "online", "latency_ms": 12 }</span>`} 
                />
              </motion.div>
            )}

            {activeSection === 'auth' && (
              <motion.div key="auth" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <h1 style={{ fontSize: '48px', fontWeight: 900, letterSpacing: '-0.02em', margin: '0 0 24px 0' }}>Authentication</h1>
                <p style={{ fontSize: '20px', color: '#9CA3AF', lineHeight: '1.6', margin: '0 0 32px 0' }}>
                  The API uses Bearer tokens to authenticate requests. You can view and manage your API keys in the <Link href="/dashboard" style={{ color: '#60A5FA' }}>Developer Dashboard</Link>.
                </p>
                <div style={{ padding: '16px', borderRadius: '8px', background: 'rgba(249,115,22,0.1)', border: '1px solid rgba(249,115,22,0.3)', color: '#FB923C', marginBottom: '32px', display: 'flex', alignItems: 'flex-start', gap: '12px', fontSize: '14px' }}>
                  <Key style={{ width: 20, height: 20, flexShrink: 0, marginTop: 2 }} />
                  <p style={{ margin: 0, lineHeight: 1.5 }}><strong>Keep your keys secure.</strong> Do not hardcode your API keys directly into your client-side applications. Always use environment variables.</p>
                </div>
                
                <CodeBlock 
                  language="python" 
                  code={`<span style="color:#C084FC">import</span> os\n<span style="color:#C084FC">import</span> recon_iq\n\nclient = recon_iq.Client(\n    api_key=os.getenv(<span style="color:#34D399">"RECONIQ_API_KEY"</span>)\n)`} 
                />
              </motion.div>
            )}

            {activeSection === 'streams' && (
              <motion.div key="streams" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <h1 style={{ fontSize: '48px', fontWeight: 900, letterSpacing: '-0.02em', margin: '0 0 24px 0' }}>Streaming Data</h1>
                <p style={{ fontSize: '20px', color: '#9CA3AF', lineHeight: '1.6', margin: '0 0 32px 0' }}>
                  ReconIQ is built on DuckDB and can effortlessly stream millions of rows from payment gateways or internal bank ledgers in real-time.
                </p>
                <h2 style={{ fontSize: '24px', fontWeight: 700, margin: '48px 0 16px 0' }}>Supported Integrations</h2>
                <ul style={{ color: '#9CA3AF', margin: '0 0 32px 0', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <li><code style={{ color: '#60A5FA', background: 'rgba(96,165,250,0.1)', padding: '2px 6px', borderRadius: '4px' }}>razorpay_api</code> - Live Razorpay Settlements</li>
                  <li><code style={{ color: '#60A5FA', background: 'rgba(96,165,250,0.1)', padding: '2px 6px', borderRadius: '4px' }}>stripe_api</code> - Stripe Gateway Ledgers</li>
                  <li><code style={{ color: '#60A5FA', background: 'rgba(96,165,250,0.1)', padding: '2px 6px', borderRadius: '4px' }}>hdfs_core</code> - Raw HDFS Banking Dumps</li>
                </ul>
                <CodeBlock 
                  language="python" 
                  code={`<span style="color:#6B7280"># Stream live ledger datasets into memory</span>\npg_stream = client.stream(<span style="color:#34D399">"razorpay_api"</span>)\nbank_stream = client.stream(<span style="color:#34D399">"hdfc_core"</span>)`} 
                />
              </motion.div>
            )}

            {activeSection === 'matching' && (
              <motion.div key="matching" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <h1 style={{ fontSize: '48px', fontWeight: 900, letterSpacing: '-0.02em', margin: '0 0 24px 0' }}>AI Matching Engine</h1>
                <p style={{ fontSize: '20px', color: '#9CA3AF', lineHeight: '1.6', margin: '0 0 32px 0' }}>
                  Pass your streamed data into the core probabilistic matching engine to automatically resolve discrepancies that strict string-matching would miss.
                </p>
                <CodeBlock 
                  language="python" 
                  code={`<span style="color:#C084FC">from</span> recon_iq <span style="color:#C084FC">import</span> strategies\n\n<span style="color:#6B7280"># Execute AI fuzzy logic resolution</span>\nresults = client.match(\n    source_a=pg_stream,\n    source_b=bank_stream,\n    strategy=strategies.AI_FUZZY_LOGIC,\n    threshold=<span style="color:#FB923C">0.95</span>\n)\n\n<span style="color:#60A5FA">print</span>(<span style="color:#34D399">f"Auto-resolved {results.success_rate}% of records."</span>)`} 
                />
              </motion.div>
            )}
          </AnimatePresence>

        </main>
      </div>
    </div>
  );
}
