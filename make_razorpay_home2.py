page_content = """\
"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState("Accept Payments");

  return (
    <div className="w-full bg-white text-[#0b1222] font-sans selection:bg-[#3366FF] selection:text-white">
      
      {/* ── TOP BANNER ── */}
      <div className="w-full bg-[#0a1835] text-white py-3 px-4 flex justify-between items-center text-sm font-medium">
        <div className="flex items-center gap-6 max-w-7xl mx-auto w-full">
          <span className="opacity-90">Accept International Payments</span>
          <div className="flex items-center gap-2 bg-white/10 px-3 py-1 rounded-full text-xs">
            <span>🇮🇹 Italy</span>
          </div>
          <span className="opacity-90">Global cards, Apple Pay, Google Pay at lower fee.</span>
          <button className="bg-[#1f2b48] hover:bg-[#2a385a] transition px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider ml-2">
            Know More
          </button>
          
          <div className="flex gap-1 ml-auto">
            <span className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-[10px] font-bold">A$</span>
            <span className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-[10px] font-bold">C$</span>
            <span className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-[10px] font-bold">CHF</span>
            <span className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-[10px] font-bold">S$</span>
          </div>
        </div>
      </div>

      {/* ── MAIN NAVBAR ── */}
      <nav className="w-full bg-white border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-20 flex items-center justify-between">
          
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 text-2xl font-bold text-[#0b1222] tracking-tight">
              <span className="text-[#3366FF] italic font-serif text-3xl">R</span> Razorpay
            </Link>
            
            <div className="hidden lg:flex items-center gap-6 text-[15px] font-medium text-gray-700">
              <span className="hover:text-[#3366FF] cursor-pointer transition">Agentic Stack</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Payments</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Banking+</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Payroll</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Engage</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Partners</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Startups</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Resources</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Pricing</span>
            </div>
          </div>

          <div className="flex items-center gap-5">
            <span className="cursor-pointer opacity-70 hover:opacity-100">🎧</span>
            <div className="flex items-center gap-1 cursor-pointer">
              <span>🇮🇳</span>
              <span className="text-xs">▼</span>
            </div>
            <Link href="/dashboard" className="text-[#3366FF] font-bold px-4 py-2 border border-[#3366FF] rounded hover:bg-blue-50 transition">
              Login
            </Link>
            <Link href="/dashboard" className="bg-[#3366FF] hover:bg-[#2855d8] transition text-white font-bold px-6 py-2.5 rounded shadow-lg shadow-blue-500/30 flex items-center gap-2">
              Sign Up →
            </Link>
          </div>
        </div>
      </nav>

      {/* ── HERO SECTION ── */}
      <section className="relative w-full overflow-hidden bg-white min-h-[600px] flex items-center">
        {/* Huge angled background */}
        <div className="absolute top-0 right-0 w-[55%] h-[120%] bg-gradient-to-bl from-[#eef4ff] to-[#f4f7fc] transform origin-top-left -skew-x-12 z-0"></div>
        
        <div className="max-w-7xl mx-auto px-4 w-full relative z-10 flex flex-col md:flex-row items-center pt-10 pb-20">
          
          <div className="md:w-1/2 pt-10">
            <h1 className="text-[3.8rem] leading-[1.1] font-bold mb-6 tracking-tight">
              <span className="text-[#3366FF]">International Payments</span><br />
              <span className="text-[#0b1222]">for founders defying all odds</span>
            </h1>
            <p className="text-gray-500 text-lg mb-10 max-w-lg font-medium">
              Accept cards, bank transfers and Apple Pay from 180+ countries
            </p>
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="bg-[#3366FF] hover:bg-[#2855d8] transition text-white px-8 py-3.5 rounded font-bold shadow-lg shadow-blue-500/30 text-[15px]">
                Sign Up Now
              </Link>
              <button className="text-[#3366FF] hover:text-[#2855d8] px-4 py-3 font-bold transition text-[15px]">
                Know More
              </button>
            </div>
          </div>

          <div className="md:w-1/2 relative h-[500px] flex justify-center items-center mt-10 md:mt-0">
             {/* Simulated Vinay Dube Photo Element */}
             <div className="relative w-[340px] h-[450px] bg-gradient-to-t from-[#3366FF]/20 to-transparent rounded-t-full flex items-end justify-center border-b border-[#3366FF]/30">
                <div className="absolute top-10 right-[-60px] bg-white/90 backdrop-blur-sm shadow-xl p-4 rounded-xl border border-blue-100 flex flex-col items-center animate-bounce" style={{animationDuration: '4s'}}>
                   <span className="text-blue-500 font-bold mb-1">✈ Akasa Air</span>
                   <span className="text-[9px] text-gray-400 font-bold tracking-widest">POWERED BY</span>
                   <span className="text-[9px] text-gray-400 font-bold tracking-widest text-center">RAZORPAY<br/>INTERNATIONAL PAYMENTS</span>
                </div>
                <div className="absolute top-32 right-[-80px] bg-white shadow-lg px-4 py-2 rounded-full border border-gray-100 font-bold text-sm text-gray-700">
                   135 Currencies
                </div>
                <div className="absolute top-48 right-[-100px] bg-white shadow-lg px-4 py-2 rounded-full border border-gray-100 font-bold text-sm text-gray-700">
                   Higher Success Rates
                </div>
                <div className="absolute top-64 right-[-60px] bg-white shadow-lg px-4 py-2 rounded-full border border-gray-100 font-bold text-sm text-gray-700 flex items-center gap-2">
                    Apple Pay
                </div>
                
                <div className="bg-[#3366FF]/90 backdrop-blur text-white px-6 py-2 rounded-t-xl text-sm font-bold absolute bottom-0">
                  Vinay Dube Co-Founder & CEO ↗
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* ── SEARCH TABS ── */}
      <div className="max-w-[1100px] mx-auto relative z-20 -mt-10 px-4">
        <div className="bg-white rounded-lg shadow-[0_10px_40px_rgba(0,0,0,0.08)] border border-gray-100 p-2 flex flex-wrap md:flex-nowrap items-center gap-2 overflow-x-auto hide-scrollbar">
          <div className="flex items-center gap-2 px-4 py-2 text-[13px] font-bold text-[#0b1222] border-r border-gray-100 whitespace-nowrap">
            <span className="text-blue-500 text-lg">⌘</span> Start your search
          </div>
          <button className="px-4 py-2 text-[13px] font-bold text-[#3366FF] bg-blue-50 rounded whitespace-nowrap flex items-center gap-2">
            💳 Accept Payments
          </button>
          <button className="px-4 py-2 text-[13px] font-bold text-gray-500 hover:bg-gray-50 rounded whitespace-nowrap flex items-center gap-2 transition">
            💸 Make Payouts
          </button>
          <button className="px-4 py-2 text-[13px] font-bold text-gray-500 hover:bg-gray-50 rounded whitespace-nowrap flex items-center gap-2 transition">
            🏦 Start Business Banking
          </button>
          <button className="px-4 py-2 text-[13px] font-bold text-gray-500 hover:bg-gray-50 rounded whitespace-nowrap flex items-center gap-2 transition">
            📊 Get Credit
          </button>
          <button className="px-4 py-2 text-[13px] font-bold text-gray-500 hover:bg-gray-50 rounded whitespace-nowrap flex items-center gap-2 transition">
            ⚙ Automate Payroll
          </button>
          <button className="px-4 py-2 text-[13px] font-bold text-[#3366FF] hover:bg-gray-50 rounded whitespace-nowrap flex items-center gap-2 transition ml-auto">
            ✎ Something else?
          </button>
        </div>
      </div>

      {/* ── LOGO MARQUEE ── */}
      <section className="py-16">
         <div className="max-w-7xl mx-auto px-4 overflow-hidden flex items-center justify-between opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
           {['Blinkit', 'Zomato', 'Swiggy', 'Lenskart', 'Urban Company', 'Nykaa', 'Zerodha'].map((brand, i) => (
             <div key={i} className="text-2xl font-black tracking-tighter text-gray-800">{brand}</div>
           ))}
         </div>
      </section>

      {/* ── VULCAN DARK SECTION ── */}
      <section className="bg-[#050914] text-white py-24 relative overflow-hidden flex justify-center">
        {/* Complex radial grid background */}
        <div className="absolute inset-0 opacity-30 flex items-center justify-center">
          <div className="w-[800px] h-[800px] rounded-full border border-gray-700"></div>
          <div className="absolute w-[600px] h-[600px] rounded-full border border-gray-600"></div>
          <div className="absolute w-[400px] h-[400px] rounded-full border border-gray-500 border-dashed animate-[spin_60s_linear_infinite]"></div>
          <div className="absolute w-[200px] h-[200px] rounded-full border-2 border-blue-500 blur-[2px] animate-pulse"></div>
        </div>
        
        <div className="max-w-[1000px] mx-auto px-6 relative z-10 text-center flex flex-col items-center">
          <div className="text-gray-400 text-xs tracking-[0.2em] font-bold mb-6 border border-gray-700 w-fit px-3 py-1 rounded">RAZORPAY VULCAN</div>
          <h2 className="text-4xl md:text-[3.5rem] leading-tight font-serif mb-10 text-white max-w-2xl">
            We built India's First AI<br />Payments Foundation Model
          </h2>
          <Link href="/ai-control-room" className="inline-block bg-[#3366FF] hover:bg-[#2855d8] transition text-white px-8 py-3.5 rounded font-bold shadow-lg">
            Discover Now
          </Link>
        </div>
      </section>

      {/* ── THE ALL IN ONE FINANCE PLATFORM ── */}
      <section className="pt-32 pb-24 max-w-7xl mx-auto px-4">
        <h2 className="text-[3.5rem] leading-[1.1] font-bold text-[#0b1222] mb-12 tracking-tight">
          The all in one <span className="text-[#00d289]">finance platform</span><br />
          you've been looking for
        </h2>
        
        <div className="flex gap-8 border-b border-gray-200 mb-12 text-[15px] overflow-x-auto hide-scrollbar font-bold">
           {['Build AI Native', 'Accept Payments', 'Make Payouts', 'Start Business Banking', 'Automate Payroll', 'Get Credit & Loans'].map(tab => (
             <button 
               key={tab} 
               onClick={() => setActiveTab(tab)}
               className={`pb-4 whitespace-nowrap transition-colors ${activeTab === tab ? "border-b-[3px] border-[#3366FF] text-[#0b1222]" : "text-gray-400 hover:text-[#0b1222]"}`}
             >
               {tab}
             </button>
           ))}
        </div>

        {/* Dynamic Grid: Accept Payments (Since user screenshot shows Accept Payments) */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="col-span-1 border border-gray-200 rounded-xl p-6 bg-white shadow-sm hover:shadow-lg transition cursor-pointer flex flex-col">
            <div className="h-40 bg-[#f4f8f7] rounded-lg mb-6 flex items-center justify-center text-4xl">💳</div>
            <h3 className="font-bold text-xl mb-2 text-[#0b1222]">Payment Gateway</h3>
            <p className="text-gray-500 text-sm">Accept payments on your website or app via cards, UPI, netbanking & more.</p>
          </div>
          
          <div className="col-span-1 border border-gray-200 rounded-xl p-6 bg-white shadow-sm hover:shadow-lg transition cursor-pointer flex flex-col">
            <div className="h-40 bg-[#eff2ff] rounded-lg mb-6 flex flex-col items-center justify-center relative overflow-hidden">
               <div className="bg-white/80 backdrop-blur px-3 py-1 rounded text-xs font-bold text-gray-500 absolute top-3 right-3 shadow-sm border border-gray-100">NO CODE</div>
               <div className="text-4xl">📱</div>
            </div>
            <h3 className="font-bold text-xl mb-2 text-[#0b1222]">Payment Links</h3>
            <p className="text-gray-500 text-sm">Share payment links via email, SMS, WhatsApp & social media.</p>
          </div>

          <div className="col-span-1 border border-gray-200 rounded-xl p-6 bg-white shadow-sm hover:shadow-lg transition cursor-pointer flex flex-col">
            <div className="h-40 bg-[#fef6f0] rounded-lg mb-6 flex flex-col items-center justify-center relative overflow-hidden">
               <div className="bg-white/80 backdrop-blur px-3 py-1 rounded text-xs font-bold text-gray-500 absolute top-3 right-3 shadow-sm border border-gray-100">NO CODE</div>
               <div className="text-4xl">🪴</div>
            </div>
            <h3 className="font-bold text-xl mb-2 text-[#0b1222]">Payment Pages</h3>
            <p className="text-gray-500 text-sm">Build custom payment pages for your business with zero coding.</p>
          </div>

          <div className="col-span-1 border border-gray-200 rounded-xl p-6 bg-white shadow-sm hover:shadow-lg transition cursor-pointer flex flex-col relative overflow-hidden">
            <div className="h-40 bg-[#eef7ff] rounded-lg mb-6 flex items-center justify-center relative">
               <div className="w-24 h-32 bg-white rounded-lg shadow-xl border border-gray-100 flex flex-col items-center justify-between p-2 transform rotate-3">
                 <div className="w-full h-8 bg-blue-500 rounded text-[8px] text-white flex items-center justify-center font-bold">Razorpay</div>
                 <div className="w-full grid grid-cols-3 gap-1">
                   {[...Array(9)].map((_, i) => <div key={i} className="h-2 bg-gray-100 rounded"></div>)}
                 </div>
               </div>
            </div>
            <h3 className="font-bold text-xl mb-2 text-[#0b1222]">Razorpay POS</h3>
            <p className="text-gray-500 text-sm">Seamless In-Store Payments for your retail outlets.</p>
          </div>
        </div>
      </section>

      {/* ── POWERING ALL DISRUPTORS ── */}
      <section className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-4">
           <h2 className="text-[3rem] font-bold text-[#0b1222] mb-10 tracking-tight">Powering all disruptors.</h2>
           
           <div className="flex gap-8 mb-10 text-[15px] font-bold border-b border-gray-200">
             <button className="text-[#00d289] border-b-[3px] border-[#00d289] pb-4">E-Commerce</button>
             <button className="text-gray-400 hover:text-[#0b1222] transition pb-4">Education</button>
             <button className="text-gray-400 hover:text-[#0b1222] transition pb-4">BFSI</button>
             <button className="text-gray-400 hover:text-[#0b1222] transition pb-4">SaaS</button>
             <button className="text-gray-400 hover:text-[#0b1222] transition pb-4">Freelancer</button>
           </div>

           <div className="flex flex-col md:flex-row bg-[#0b1222] rounded-3xl overflow-hidden shadow-2xl">
             <div className="md:w-[45%] bg-white p-16 flex flex-col justify-center m-1 rounded-3xl">
                <h3 className="text-3xl font-bold text-[#0b1222] mb-4 leading-snug">Empower your<br/><span className="text-[#00d289]">e-commerce business</span></h3>
                <p className="text-gray-500 mb-8 leading-relaxed font-medium">
                  Streamline payment management with a unified dashboard, enabling both online and in-person payment collection while enhancing conversion rates and minimizing fraud.
                </p>
                <div className="flex items-center gap-4 text-sm font-black text-gray-500 mb-10 opacity-70">
                  <span>NYKAA</span>
                  <span>DECATHLON</span>
                  <span>ZOMATO</span>
                  <span>Flipkart</span>
                  <span className="text-gray-400 font-medium text-xs">+ 70,000 others</span>
                </div>
                <button className="bg-[#3366FF] hover:bg-[#2855d8] transition text-white px-8 py-3.5 rounded font-bold w-fit shadow-lg shadow-blue-500/20">
                  See Solutions →
                </button>
             </div>
             <div className="md:w-[55%] relative min-h-[400px]">
                {/* Photo Placeholder mimicking the guy packing boxes */}
                <div className="absolute inset-0 bg-[#16213e] flex items-center justify-center overflow-hidden">
                   <div className="absolute inset-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center"></div>
                   <div className="relative z-10 text-white opacity-20 text-9xl font-bold">IMAGE</div>
                </div>
             </div>
           </div>
        </div>
      </section>

      {/* ── BUILT FOR DEVELOPERS ── */}
      <section className="bg-[#0b1222] py-32 text-white relative border-t-[8px] border-[#00d289]">
         <div className="max-w-7xl mx-auto px-4 relative z-10 flex flex-col md:flex-row gap-16 items-center">
            
            <div className="md:w-1/2">
              <h2 className="text-[3rem] font-bold mb-6 text-white leading-tight tracking-tight">
                Razorpay is built<br/>
                <span className="text-[#00d289] font-mono text-4xl">&lt;for developers by developers&gt;</span>
              </h2>
              
              <div className="grid grid-cols-2 gap-12 mt-16">
                <div>
                  <div className="text-2xl mb-4 text-[#3366FF]">📄</div>
                  <h4 className="font-bold mb-3 text-lg">Integrations</h4>
                  <p className="text-[15px] text-gray-400 mb-4 leading-relaxed">Find all popular platform SDKs, plugins, server integrations in our integration stack.</p>
                  <Link href="#" className="text-white font-bold hover:text-[#00d289] transition">View Docs →</Link>
                </div>
                <div>
                  <div className="text-2xl mb-4 text-[#3366FF]">⚡</div>
                  <h4 className="font-bold mb-3 text-lg">API Reference</h4>
                  <p className="text-[15px] text-gray-400 mb-4 leading-relaxed">Comprehensive documentation to build powerful payment solutions.</p>
                  <Link href="#" className="text-white font-bold hover:text-[#00d289] transition">View Docs →</Link>
                </div>
              </div>
            </div>

            <div className="md:w-1/2 w-full mt-10 md:mt-0">
              <div className="flex gap-4 text-xs font-bold text-[#00d289] font-mono mb-4 tracking-widest">
                <span className="cursor-pointer">PYTHON •</span>
                <span className="opacity-50 hover:opacity-100 cursor-pointer transition">PHP •</span>
                <span className="opacity-50 hover:opacity-100 cursor-pointer transition">NODE JS •</span>
                <span className="opacity-50 hover:opacity-100 cursor-pointer transition">CURL •</span>
                <span className="opacity-50 hover:opacity-100 cursor-pointer transition">JAVA •</span>
              </div>
              
              <div className="bg-[#050914] rounded-xl border border-gray-800 shadow-2xl overflow-hidden font-mono text-sm">
                <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between bg-[#0b1222]">
                  <span className="text-gray-400">Try it out</span>
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-gray-700"></div>
                    <div className="w-3 h-3 rounded-full bg-gray-700"></div>
                    <div className="w-3 h-3 rounded-full bg-gray-700"></div>
                  </div>
                </div>
                <div className="p-8 text-gray-300 whitespace-pre overflow-x-auto leading-loose text-[15px]">
                  <span className="text-[#ff5e5e]">import</span> razorpay<br/><br/>
                  client = razorpay.Client(auth=(<span className="text-[#00d289]">"YOUR_ID"</span>, <span className="text-[#00d289]">"YOUR_SECRET"</span>))<br/><br/>
                  <span className="text-gray-600"># Create a payment link</span><br/>
                  client.payment_link.create({<br/>
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-[#3366FF]">"amount"</span>: <span className="text-yellow-500">5000</span>,<br/>
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-[#3366FF]">"currency"</span>: <span className="text-[#00d289]">"INR"</span>,<br/>
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-[#3366FF]">"accept_partial"</span>: <span className="text-[#ff5e5e]">True</span>,<br/>
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-[#3366FF]">"description"</span>: <span className="text-[#00d289]">"For XYZ purpose"</span><br/>
                  })
                </div>
              </div>
            </div>

         </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="bg-white py-16 px-4 border-t border-gray-100">
        <div className="max-w-7xl mx-auto flex flex-wrap gap-12 justify-between">
          <div className="w-full md:w-1/4">
             <div className="flex items-center gap-2 text-2xl font-bold text-[#0b1222] tracking-tight mb-6">
                <span className="text-[#3366FF] italic font-serif text-3xl">R</span> Razorpay
             </div>
             <p className="text-gray-500 text-sm leading-relaxed mb-6">
               Razorpay is the only payments solution in India that allows businesses to accept, process and disburse payments with its product suite.
             </p>
             <div className="flex gap-4 opacity-50">
               <span className="text-2xl">📱</span>
               <span className="text-2xl">✉</span>
               <span className="text-2xl">🌐</span>
             </div>
          </div>
          <div>
            <h4 className="font-bold text-[#0b1222] mb-6">ACCEPT PAYMENTS</h4>
            <div className="flex flex-col gap-4 text-sm text-gray-500 font-medium">
              <span className="hover:text-[#3366FF] cursor-pointer transition">Payment Gateway</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Payment Pages</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Payment Links</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Razorpay POS</span>
            </div>
          </div>
          <div>
            <h4 className="font-bold text-[#0b1222] mb-6">BANKING PLUS</h4>
            <div className="flex flex-col gap-4 text-sm text-gray-500 font-medium">
              <span className="hover:text-[#3366FF] cursor-pointer transition">RazorpayX</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Source to pay</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Current Accounts</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Payouts</span>
            </div>
          </div>
          <div>
            <h4 className="font-bold text-[#0b1222] mb-6">COMPANY</h4>
            <div className="flex flex-col gap-4 text-sm text-gray-500 font-medium">
              <span className="hover:text-[#3366FF] cursor-pointer transition">About Us</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Careers</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Terms of Use</span>
              <span className="hover:text-[#3366FF] cursor-pointer transition">Privacy Policy</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
"""

with open("apps/web/app/page.tsx", "w") as f:
    f.write(page_content)
