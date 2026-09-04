import os

page_content = """\
"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState("Build AI Native");

  const productTabs = [
    "Build AI Native",
    "Accept Payments",
    "Make Payouts",
    "Start Business Banking",
    "Automate Payroll",
    "Credit & Loans",
  ];

  return (
    <div className="w-full bg-white text-[#02042b] font-sans selection:bg-[#2b64f9] selection:text-white pb-20">
      
      {/* 1. HERO SECTION */}
      <section className="relative w-full overflow-hidden pt-20 pb-32">
        {/* Angled background */}
        <div className="absolute top-0 right-0 w-3/5 h-full bg-gradient-to-bl from-[#eef2fa] to-[#f4f7fc] transform origin-top-left -skew-x-12 z-0 border-l border-white/50 shadow-sm"></div>
        
        <div className="max-w-[1200px] mx-auto px-6 relative z-10 flex flex-col md:flex-row items-center justify-between">
          
          <div className="md:w-1/2 pt-10">
            <h1 className="text-[3.4rem] leading-[1.1] font-bold text-[#02042b] mb-6 tracking-tight">
              Advanced Finance<br />
              <span className="text-[#2b64f9]">Operations Platform</span><br />
              for founders defying odds
            </h1>
            <p className="text-[#4f566b] text-lg mb-8 max-w-md font-medium">
              Accept payments, automate reconciliations, settle funds, and close your books faster with ReconIQ's AI-native stack.
            </p>
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="bg-[#2b64f9] hover:bg-[#1a4de0] transition-colors text-white px-7 py-3.5 rounded text-[15px] font-bold shadow-lg shadow-blue-500/30">
                Sign Up Now
              </Link>
              <button className="text-[#2b64f9] hover:text-[#1a4de0] px-4 py-3 text-[15px] font-bold transition-colors">
                Know More
              </button>
            </div>
          </div>

          {/* Hero Illustration / Dashboard Preview */}
          <div className="md:w-1/2 relative mt-16 md:mt-0 flex justify-end">
             <div className="relative w-[500px] h-[400px] bg-white rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.1)] border border-gray-100 p-6 z-10 transform hover:-translate-y-2 transition-transform duration-500">
                <div className="flex justify-between items-center mb-6">
                  <div className="h-4 w-24 bg-gray-200 rounded-full"></div>
                  <div className="h-4 w-8 bg-green-100 rounded-full"></div>
                </div>
                <div className="space-y-4">
                   <div className="h-16 w-full bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100/50 flex items-center px-4 gap-4">
                     <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs">AI</div>
                     <div className="flex-1 space-y-2">
                       <div className="h-2 w-1/3 bg-blue-200 rounded-full"></div>
                       <div className="h-2 w-1/2 bg-gray-200 rounded-full"></div>
                     </div>
                   </div>
                   <div className="h-16 w-full bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-100/50 flex items-center px-4 gap-4">
                     <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white text-xs">✓</div>
                     <div className="flex-1 space-y-2">
                       <div className="h-2 w-1/4 bg-green-200 rounded-full"></div>
                       <div className="h-2 w-2/3 bg-gray-200 rounded-full"></div>
                     </div>
                   </div>
                   <div className="h-16 w-full bg-gray-50 rounded-xl border border-gray-100 flex items-center px-4 gap-4">
                     <div className="w-8 h-8 rounded-full bg-gray-300"></div>
                     <div className="flex-1 space-y-2">
                       <div className="h-2 w-1/5 bg-gray-300 rounded-full"></div>
                       <div className="h-2 w-1/3 bg-gray-200 rounded-full"></div>
                     </div>
                   </div>
                </div>
                
                {/* Floating elements */}
                <div className="absolute -right-8 top-20 bg-white p-3 rounded-lg shadow-xl border border-gray-50 flex items-center gap-3 animate-bounce" style={{ animationDuration: '3s' }}>
                  <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">₹</div>
                  <div>
                    <div className="text-xs text-gray-400 font-bold">Payment Settled</div>
                    <div className="text-sm font-black text-[#02042b]">₹1,24,500</div>
                  </div>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* 2. FLOATING SEARCH TABS */}
      <div className="max-w-[1100px] mx-auto relative z-20 -mt-16 px-4">
        <div className="bg-white rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.08)] border border-gray-100 p-2 flex flex-wrap md:flex-nowrap items-center justify-between gap-2 overflow-x-auto hide-scrollbar">
          <div className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-[#02042b] border-r border-gray-100 whitespace-nowrap">
            <span className="text-blue-500">⌘</span> Start your search
          </div>
          <button className="px-4 py-2 text-[13px] font-semibold text-blue-600 bg-blue-50 rounded-lg whitespace-nowrap flex items-center gap-2">
            <span className="text-lg">💳</span> Accept Payments
          </button>
          <button className="px-4 py-2 text-[13px] font-semibold text-[#4f566b] hover:bg-gray-50 rounded-lg whitespace-nowrap transition-colors flex items-center gap-2">
            <span className="text-lg">💸</span> Make Payouts
          </button>
          <button className="px-4 py-2 text-[13px] font-semibold text-[#4f566b] hover:bg-gray-50 rounded-lg whitespace-nowrap transition-colors flex items-center gap-2">
            <span className="text-lg">🏦</span> Start Business Banking
          </button>
          <button className="px-4 py-2 text-[13px] font-semibold text-[#4f566b] hover:bg-gray-50 rounded-lg whitespace-nowrap transition-colors flex items-center gap-2">
            <span className="text-lg">📊</span> Get Credit
          </button>
          <button className="px-4 py-2 text-[13px] font-semibold text-[#4f566b] hover:bg-gray-50 rounded-lg whitespace-nowrap transition-colors flex items-center gap-2">
            <span className="text-lg">⚡</span> Automate Payroll
          </button>
        </div>
      </div>

      {/* 3. LOGO MARQUEE */}
      <section className="py-12 border-b border-gray-100 bg-gray-50/50">
         <div className="max-w-[1200px] mx-auto px-6 overflow-hidden flex items-center justify-between opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
           {['Swiggy', 'Zomato', 'Zerodha', 'Blinkit', 'Nykaa', 'Lenskart'].map((brand, i) => (
             <div key={i} className="text-xl font-black tracking-tighter text-gray-400">{brand.toUpperCase()}</div>
           ))}
         </div>
      </section>

      {/* 4. RECONIQ VULCAN (DARK AI SECTION) */}
      <section className="bg-[#0b0c10] text-white py-24 relative overflow-hidden">
        {/* Grid pattern background */}
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'linear-gradient(#1f2937 1px, transparent 1px), linear-gradient(90deg, #1f2937 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
        <div className="max-w-[1200px] mx-auto px-6 relative z-10 flex flex-col md:flex-row items-center justify-between gap-12">
          <div className="md:w-1/2">
            <div className="text-gray-400 text-xs tracking-[0.2em] font-bold mb-6 border border-gray-700 w-fit px-3 py-1 rounded">RECONIQ VULCAN</div>
            <h2 className="text-4xl md:text-5xl font-serif mb-8 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
              We built India's First AI<br />Payments Foundation Model
            </h2>
            <Link href="/ai-control-room" className="inline-block bg-[#2b64f9] hover:bg-[#1a4de0] transition-colors text-white px-7 py-3 rounded text-[15px] font-bold">
              Discover Now
            </Link>
          </div>
          <div className="md:w-1/2 flex justify-center">
            {/* Cool AI Graphic Mockup */}
            <div className="w-[300px] h-[300px] rounded-full border border-gray-700 relative flex items-center justify-center">
              <div className="w-[200px] h-[200px] rounded-full border border-blue-900 absolute animate-ping" style={{ animationDuration: '3s' }}></div>
              <div className="w-[100px] h-[100px] rounded-full bg-gradient-to-tr from-blue-600 to-cyan-400 blur-xl animate-pulse"></div>
              <div className="text-4xl relative z-10">🧠</div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. PRODUCT TABS (BUILD AI NATIVE, ACCEPT PAYMENTS...) */}
      <section className="py-24 max-w-[1200px] mx-auto px-6">
        <h2 className="text-3xl font-bold text-[#02042b] mb-12">
          The all in one <span className="text-green-500">finance platform</span><br />
          you've been looking for
        </h2>
        
        {/* Tabs Header */}
        <div className="flex gap-8 border-b border-gray-200 mb-12 overflow-x-auto hide-scrollbar">
          {productTabs.map(tab => (
            <button 
              key={tab} 
              onClick={() => setActiveTab(tab)}
              className={`pb-4 font-bold text-[15px] whitespace-nowrap transition-all ${
                activeTab === tab 
                  ? "border-b-2 border-[#2b64f9] text-[#2b64f9]" 
                  : "text-[#4f566b] hover:text-[#02042b]"
              }`}
            >
              {tab} {tab === "Build AI Native" && <span className="ml-2 bg-black text-white text-[10px] px-2 py-0.5 rounded-full uppercase">New</span>}
            </button>
          ))}
        </div>

        {/* Dynamic Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1 */}
          <div className="bg-white border border-gray-200 p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer group">
            <div className="h-40 bg-[#f4f7fc] rounded-lg mb-6 border border-gray-100 flex items-center justify-center relative overflow-hidden">
               <div className="absolute inset-0 bg-gradient-to-tr from-blue-100 to-transparent opacity-50 group-hover:opacity-100 transition-opacity"></div>
               <div className="text-5xl transform group-hover:scale-110 transition-transform">🤖</div>
            </div>
            <h3 className="font-bold text-xl text-[#02042b] mb-2">Agentic Payments</h3>
            <p className="text-[#4f566b] text-sm leading-relaxed">
              Turn every chat into a checkout with AI-native payment flows. Let agents negotiate and close sales.
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-white border border-gray-200 p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer group">
            <div className="h-40 bg-[#f4f7fc] rounded-lg mb-6 border border-gray-100 flex flex-col items-center justify-center gap-2 relative overflow-hidden">
               <div className="bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded-full w-fit">AGENT / AUTO-CAPTURE</div>
               <div className="bg-white text-gray-500 border border-gray-200 text-[10px] font-bold px-3 py-1 rounded-full w-fit">AGENT / DISPUTE RESPONDER</div>
               <div className="bg-white text-gray-500 border border-gray-200 text-[10px] font-bold px-3 py-1 rounded-full w-fit">AGENT / REVENUE DETECTOR</div>
            </div>
            <h3 className="font-bold text-xl text-[#02042b] mb-2">Agent Studio</h3>
            <p className="text-[#4f566b] text-sm leading-relaxed">
              Delegate operational work to agents that get things done automatically.
            </p>
            <Link href="/ai-control-room" className="inline-block mt-4 text-blue-600 font-bold text-sm hover:underline">Know More →</Link>
          </div>

          {/* Card 3 */}
          <div className="bg-white border border-gray-200 p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer group">
            <div className="h-40 bg-[#f4f7fc] rounded-lg mb-6 border border-gray-100 flex items-center justify-center gap-4 relative overflow-hidden">
               <div className="w-12 h-12 bg-white rounded-lg shadow flex items-center justify-center text-red-500 font-bold text-xs">n8n</div>
               <div className="w-12 h-12 bg-blue-600 rounded-lg shadow flex items-center justify-center text-white font-bold text-xs">⚡</div>
               <div className="w-12 h-12 bg-white rounded-lg shadow flex items-center justify-center text-orange-500 font-bold text-xs">replit</div>
            </div>
            <h3 className="font-bold text-xl text-[#02042b] mb-2">Payments for AI Builders</h3>
            <p className="text-[#4f566b] text-sm leading-relaxed">
              One-click payment nodes for n8n, Replit, and Vercel workflows.
            </p>
          </div>

        </div>
      </section>

      {/* 6. POWERING ALL DISRUPTORS (PHOTO + TEXT) */}
      <section className="bg-white py-24 border-t border-gray-100">
        <div className="max-w-[1200px] mx-auto px-6">
           <h2 className="text-3xl font-bold text-[#02042b] mb-10">Powering all disruptors.</h2>
           
           <div className="flex gap-6 mb-10 text-sm font-bold text-gray-500">
             <button className="text-[#02042b] border-b-2 border-green-500 pb-1">E-Commerce</button>
             <button className="hover:text-[#02042b] pb-1 transition-colors">Education</button>
             <button className="hover:text-[#02042b] pb-1 transition-colors">BFSI</button>
             <button className="hover:text-[#02042b] pb-1 transition-colors">SaaS</button>
           </div>

           <div className="flex flex-col md:flex-row bg-[#f8fafc] rounded-2xl overflow-hidden border border-gray-200">
             <div className="md:w-1/2 p-12 flex flex-col justify-center">
                <h3 className="text-3xl font-bold text-[#02042b] mb-4">Empower your<br/><span className="text-green-500">e-commerce business</span></h3>
                <p className="text-[#4f566b] mb-8 leading-relaxed">
                  Streamline payment management with a unified dashboard, enabling both online and in-person payment collection while enhancing conversion rates and minimizing fraud.
                </p>
                <div className="flex items-center gap-4 text-xs font-black text-gray-400 uppercase tracking-wider mb-8">
                  <span>NYKAA</span>
                  <span>DECATHLON</span>
                  <span>ZOMATO</span>
                  <span className="text-gray-300 normal-case font-medium text-sm">+ 70,000 others</span>
                </div>
                <button className="bg-[#2b64f9] hover:bg-[#1a4de0] transition-colors text-white px-6 py-3 rounded text-[15px] font-bold w-fit">
                  See Solutions →
                </button>
             </div>
             <div className="md:w-1/2 bg-gray-200 relative min-h-[300px]">
                {/* Photo Placeholder */}
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center"></div>
             </div>
           </div>
        </div>
      </section>

      {/* 7. BUILT FOR DEVELOPERS (TERMINAL SECTION) */}
      <section className="bg-[#0b132b] py-24 text-white relative">
         <div className="absolute top-0 right-10 flex gap-4 text-xs font-bold text-green-400 opacity-50 font-mono">
           <span>PYTHON •</span><span>PHP •</span><span>NODE JS •</span><span>CURL •</span><span>JAVA •</span>
         </div>
         <div className="max-w-[1200px] mx-auto px-6 relative z-10 flex flex-col md:flex-row gap-16 items-center">
            
            <div className="md:w-1/2">
              <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">ReconIQ is built<br/><span className="text-green-400">&lt;for developers by developers&gt;</span></h2>
              <p className="text-gray-400 mb-10 text-lg">Integrate our APIs in minutes and start reconciling payments across millions of rows with sub-second latency.</p>
              
              <div className="grid grid-cols-2 gap-8">
                <div>
                  <div className="text-2xl mb-2">⚡</div>
                  <h4 className="font-bold mb-2">Integrations</h4>
                  <p className="text-sm text-gray-400 mb-3">Find all popular platform SDKs, plugins, and server integrations.</p>
                  <Link href="#" className="text-blue-400 text-sm font-bold hover:underline">View Docs →</Link>
                </div>
                <div>
                  <div className="text-2xl mb-2">📖</div>
                  <h4 className="font-bold mb-2">API Reference</h4>
                  <p className="text-sm text-gray-400 mb-3">Comprehensive documentation to build powerful solutions.</p>
                  <Link href="#" className="text-blue-400 text-sm font-bold hover:underline">View Docs →</Link>
                </div>
              </div>
            </div>

            <div className="md:w-1/2 w-full">
              {/* Terminal Window Mockup */}
              <div className="bg-[#1a233a] rounded-xl border border-gray-700 shadow-2xl overflow-hidden font-mono text-sm">
                <div className="bg-[#0f172a] px-4 py-3 border-b border-gray-700 flex items-center justify-between text-gray-400 text-xs">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  </div>
                  <span>request.py</span>
                </div>
                <div className="p-6 text-gray-300 whitespace-pre overflow-x-auto">
                  <span className="text-pink-400">import</span> reconiq<br/><br/>
                  client = reconiq.Client(api_key=<span className="text-green-300">"rzp_live_..."</span>)<br/><br/>
                  <span className="text-gray-500"># Reconcile a massive dataset instantly</span><br/>
                  job = client.reconciliation.create(<br/>
                  &nbsp;&nbsp;&nbsp;&nbsp;internal_ledger=<span className="text-green-300">"db_ledgers.csv"</span>,<br/>
                  &nbsp;&nbsp;&nbsp;&nbsp;external_bank=<span className="text-green-300">"hdfc_statement.csv"</span>,<br/>
                  &nbsp;&nbsp;&nbsp;&nbsp;mode=<span className="text-green-300">"AI_PROBABILISTIC"</span><br/>
                  )<br/><br/>
                  <span className="text-pink-400">print</span>(<span className="text-green-300">f"Matched: {job.match_rate}%"</span>)
                </div>
              </div>
            </div>

         </div>
      </section>

      {/* 8. FOOTER SPACING (if needed) */}
      <footer className="bg-[#f4f7fc] py-12 text-center text-gray-500 text-sm font-medium">
        © 2026 ReconIQ Enterprise. Designed for the buildathon.
      </footer>

    </div>
  );
}
