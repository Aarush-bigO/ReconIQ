"use client";
import React, { useRef, useMemo } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Code2, Database, Zap, Sparkles, Mail } from 'lucide-react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// ── 3D COMPONENTS (ReconIQ Data Streams & Financial Ledger) ──

function FinancialLedger3D() {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const GRID_SIZE = 40;
  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame((state) => {
    if (!meshRef.current) return;
    let i = 0;
    const time = state.clock.elapsedTime;
    for (let x = 0; x < GRID_SIZE; x++) {
      for (let z = 0; z < GRID_SIZE; z++) {
        const posX = (x - GRID_SIZE / 2) * 0.8;
        const posZ = (z - GRID_SIZE / 2) * 0.8;
        const posY = Math.sin(posX * 0.15 + time) * Math.cos(posZ * 0.15 + time) * 2.0;
        dummy.position.set(posX, posY - 8, posZ - 10);
        const scaleY = 1 + Math.max(0, posY * 1.5);
        dummy.scale.set(1, scaleY, 1);
        dummy.updateMatrix();
        meshRef.current.setMatrixAt(i++, dummy.matrix);
      }
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
    meshRef.current.rotation.y = time * 0.03;
  });

  return (
    <instancedMesh ref={meshRef} args={[null as any, null as any, GRID_SIZE * GRID_SIZE]}>
      <boxGeometry args={[0.15, 1, 0.15]} />
      <meshBasicMaterial color="#2563EB" wireframe={true} transparent opacity={0.15} />
    </instancedMesh>
  );
}

function DataStreams() {
  const groupRef = useRef<THREE.Group>(null);
  const packets = useMemo(() => {
    return Array.from({ length: 150 }).map(() => ({
      x: (Math.random() - 0.5) * 40,
      y: (Math.random() - 0.5) * 20,
      z: (Math.random() - 0.5) * 50,
      speed: 0.2 + Math.random() * 0.4,
      isAnomaly: Math.random() > 0.95
    }));
  }, []);

  useFrame(() => {
    if (!groupRef.current) return;
    groupRef.current.children.forEach((child, i) => {
      child.position.z += packets[i].speed;
      if (child.position.z > 10) {
        child.position.z = -40;
      }
    });
  });

  return (
    <group ref={groupRef}>
      {packets.map((p, i) => (
        <mesh key={i} position={[p.x, p.y, p.z]}>
          <boxGeometry args={[0.02, 0.02, 1.5]} />
          <meshBasicMaterial 
            color={p.isAnomaly ? "#EF4444" : "#3B82F6"} 
            transparent 
            opacity={p.isAnomaly ? 0.8 : 0.3} 
          />
        </mesh>
      ))}
    </group>
  );
}

function Background3D() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none bg-[#06080F]">
      <Canvas camera={{ position: [0, 0, 10], fov: 60 }} gl={{ antialias: false }}>
        <fog attach="fog" args={['#06080F', 10, 35]} />
        <FinancialLedger3D />
        <DataStreams />
      </Canvas>
      <div className="absolute inset-0 dot-grid opacity-30 dot-grid-mask"></div>
      <div className="absolute inset-0 hero-glow"></div>
    </div>
  );
}

export default function RazorpayBuildathonInspired() {
  return (
    <div className="w-full min-h-screen text-white overflow-x-hidden selection:bg-blue-500/30" style={{ fontFamily: "'Satoshi', sans-serif" }}>
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://api.fontshare.com/v2/css?f[]=satoshi@900,700,500,400&display=swap');
        
        .hero-glow { background: radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.25) 0%, rgba(6, 8, 15, 0) 60%); }
        .dot-grid { background-image: radial-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px); background-size: 24px 24px; }
        .dot-grid-mask { mask-image: linear-gradient(to bottom, black 0%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, black 0%, transparent 100%); }
        .rzp-button { background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%); box-shadow: 0px 1px 2px rgba(255, 255, 255, 0.3) inset, 0px 4px 12px rgba(37, 99, 235, 0.4); }
        .glass-card { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); }
      `}} />

      <Background3D />

      {/* ── HEADER ── */}
      <header className="relative z-50 flex items-center justify-center h-[80px] border-b border-white/5 bg-[#06080F]/60 backdrop-blur-md">
         <div className="w-full max-w-7xl mx-auto flex items-center justify-between px-[32px] md:px-[64px]">
           <motion.div whileHover={{ scale: 1.05 }} className="flex items-center gap-[12px] cursor-pointer">
              <motion.div whileHover={{ rotate: 90 }} transition={{ type: "spring" }} className="w-[32px] h-[32px] rounded-[6px] bg-blue-600 flex items-center justify-center font-black text-[18px]">
                 R
              </motion.div>
              <motion.span whileHover={{ color: "#60A5FA", letterSpacing: "1px" }} transition={{ duration: 0.2 }} className="font-bold text-[20px] tracking-tight text-white">
                 ReconIQ
              </motion.span>
           </motion.div>
           
           <nav className="hidden md:flex items-center gap-[32px] text-[15px] font-medium text-gray-400">
              {[
                { label: 'Platform', href: '/dashboard' },
                { label: 'APIs', href: '/docs' },
                { label: 'Documentation', href: '/docs' }
              ].map((item) => (
                <motion.div key={item.label} whileHover={{ y: -2, color: "#fff", textShadow: "0px 0px 8px rgba(255,255,255,0.8)" }}>
                  <Link href={item.href} className="transition-colors">{item.label}</Link>
                </motion.div>
              ))}
           </nav>
           
           <motion.div whileHover={{ scale: 1.05, boxShadow: "0 0 20px rgba(59,130,246,0.6)" }} whileTap={{ scale: 0.95 }} className="rounded-[6px]">
             <Link href="/dashboard" className="rzp-button text-white text-[14px] font-bold rounded-[6px] block" style={{ padding: '10px 24px' }}>
                Get Started
             </Link>
           </motion.div>
         </div>
      </header>

      {/* ── HERO SECTION ── */}
      <main className="relative z-10 w-full flex flex-col items-center justify-center pt-[100px] pb-[80px] px-[24px]" style={{ gap: '64px' }}>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col items-center text-center max-w-[800px]"
          style={{ gap: '24px' }}
        >
          {/* Badge */}
          <motion.div 
            whileHover={{ scale: 1.05, backgroundColor: "rgba(59,130,246,0.2)", borderColor: "rgba(59,130,246,0.6)" }}
            className="inline-flex items-center gap-[8px] rounded-[999px] border border-blue-500/30 bg-blue-500/10 text-[13px] font-bold text-blue-400 backdrop-blur-md cursor-pointer transition-colors"
            style={{ padding: '8px 16px' }}
          >
             <motion.div animate={{ rotate: 360 }} transition={{ duration: 4, repeat: Infinity, ease: "linear" }}>
               <Sparkles className="w-[14px] h-[14px]" />
             </motion.div>
             <motion.span whileHover={{ letterSpacing: "1px" }}>RECONIQ AI PLATFORM V4</motion.span>
          </motion.div>
          
          {/* Main Title */}
          <motion.h1 
            whileHover={{ scale: 1.02, textShadow: "0px 10px 40px rgba(59,130,246,0.4)" }}
            className="text-[56px] sm:text-[72px] md:text-[96px] font-black tracking-tighter leading-[1.05] text-white cursor-default"
          >
            <motion.span whileHover={{ color: "#93C5FD" }} transition={{ duration: 0.2 }}>Build.</motion.span>{" "}
            <motion.span whileHover={{ color: "#93C5FD" }} transition={{ duration: 0.2 }}>Resolve.</motion.span> <br/>
            <motion.span 
              whileHover={{ letterSpacing: "0.05em", filter: "hue-rotate(45deg)" }}
              transition={{ type: "spring", stiffness: 300 }}
              className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300 inline-block"
            >
              Scale.
            </motion.span>
          </motion.h1>
          
          {/* Description */}
          <motion.p 
            whileHover={{ scale: 1.02, color: "#ffffff" }}
            className="text-gray-400 text-[18px] md:text-[22px] max-w-[600px] font-medium leading-relaxed cursor-default transition-colors"
          >
            The ultimate AI-native reconciliation engine. Drop the manual spreadsheets—build pipelines worth talking about.
          </motion.p>
          
          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center w-full sm:w-auto" style={{ gap: '16px' }}>
             <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="w-full sm:w-auto">
               <Link href="/dashboard" className="w-full sm:w-auto rzp-button text-white text-[16px] font-bold rounded-[8px] flex items-center justify-center group" style={{ padding: '18px 32px', gap: '8px' }}>
                  <motion.span whileHover={{ letterSpacing: "1px" }}>Start Building Now</motion.span>
                  <ArrowRight className="w-[18px] h-[18px] group-hover:translate-x-[4px] transition-transform" />
               </Link>
             </motion.div>
             <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="w-full sm:w-auto">
               <Link href="/docs" className="w-full sm:w-auto bg-white/5 hover:bg-white/10 transition-colors text-white text-[16px] font-bold rounded-[8px] border border-white/10 flex items-center justify-center backdrop-blur-md" style={{ padding: '18px 32px' }}>
                  Read the Docs
               </Link>
             </motion.div>
          </div>
        </motion.div>

        {/* ── MOCKUP WINDOW ── */}
        <motion.div 
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          whileHover={{ y: -10, boxShadow: "0 30px 100px rgba(59,130,246,0.3)" }}
          className="w-full max-w-[1000px] cursor-crosshair"
        >
          <div className="rounded-[16px] border border-white/10 bg-[#0A0D14]/80 backdrop-blur-xl overflow-hidden relative">
            <div className="h-[48px] border-b border-white/10 bg-white/[0.02] flex items-center px-[20px] gap-[8px]">
              <div className="w-[12px] h-[12px] rounded-full bg-red-500/80"></div>
              <div className="w-[12px] h-[12px] rounded-full bg-yellow-500/80"></div>
              <div className="w-[12px] h-[12px] rounded-full bg-green-500/80"></div>
              <motion.div whileHover={{ color: "#fff", letterSpacing: "1px" }} className="ml-auto text-[13px] text-gray-500 font-mono transition-colors">pipeline.py</motion.div>
            </div>
            
            <div className="p-[32px] font-mono text-[14px] leading-loose overflow-x-auto">
              {[
                { type: 'comment', text: '# 1. Initialize ReconIQ Engine' },
                { type: 'code', html: '<span class="text-purple-400">import</span> <span class="text-white">recon_iq</span>' },
                { type: 'comment', text: '# 2. Connect high-volume data streams' },
                { type: 'code', html: '<span class="text-white">gateway_data = recon_iq.</span><span class="text-blue-400">stream</span><span class="text-white">("razorpay_api")</span>' },
                { type: 'code', html: '<span class="text-white">bank_data = recon_iq.</span><span class="text-blue-400">stream</span><span class="text-white">("hdfc_core")</span>' },
                { type: 'comment', text: '# 3. Resolve using AI probabilistic matching' },
                { type: 'code', html: '<span class="text-white">results = recon_iq.</span><span class="text-blue-400">match</span><span class="text-white">(</span>' },
                { type: 'code', html: '<span class="ml-[24px] text-white">source_a=gateway_data,</span>' },
                { type: 'code', html: '<span class="ml-[24px] text-white">source_b=bank_data,</span>' },
                { type: 'code', html: '<span class="ml-[24px] text-white">strategy=<span class="text-green-400">"ai_fuzzy_logic"</span></span>' },
                { type: 'code', html: '<span class="text-white">)</span>' },
                { type: 'comment', text: '# → Output: 99.9% match rate. <span class="text-red-400">14 anomalies detected.</span>' }
              ].map((line, i) => (
                <motion.div 
                  key={i}
                  whileHover={{ x: 15, backgroundColor: "rgba(255,255,255,0.05)" }}
                  className={`px-[8px] rounded-[4px] transition-colors ${line.type === 'comment' ? 'text-gray-400 mt-[16px]' : ''}`}
                  dangerouslySetInnerHTML={{ __html: line.html || line.text }}
                />
              ))}
            </div>
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[300px] h-[2px] bg-gradient-to-r from-transparent via-blue-500 to-transparent shadow-[0_0_20px_rgba(59,130,246,0.8)]"></div>
          </div>
        </motion.div>

      </main>

      {/* ── FEATURES GRID ── */}
      <section className="relative z-10 w-full max-w-7xl mx-auto" style={{ padding: '100px 24px' }}>
        
        <div className="flex flex-col" style={{ gap: '16px', marginBottom: '64px' }}>
           <motion.h2 whileHover={{ scale: 1.02, x: 10, color: "#60A5FA" }} className="text-[36px] md:text-[48px] font-black text-white origin-left cursor-default transition-colors leading-none">
             Engineered for scale.
           </motion.h2>
           <motion.p whileHover={{ x: 10, color: "#F8FAFC" }} className="text-gray-400 text-[18px] max-w-[600px] cursor-default transition-colors">
             Everything you need to automate millions of rows in sub-seconds.
           </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3" style={{ gap: '24px' }}>
          
          {[
            { 
              icon: Database, title: "Petabyte Ready", desc: "Built on DuckDB. Ingest millions of transactions locally and match them instantly without cloud roundtrips.", 
              colors: { bg: "bg-blue-500/10", border: "border-blue-500/20", text: "text-blue-400" } 
            },
            { 
              icon: Code2, title: "Developer First", desc: "Fully extensible API. Write custom Python reconciliation rules and deploy them securely into the engine.", 
              colors: { bg: "bg-purple-500/10", border: "border-purple-500/20", text: "text-purple-400" } 
            },
            { 
              icon: Zap, title: "Sub-second AI", desc: "Anomalies are passed to a local LLM agent network that auto-resolves mismatches in milliseconds.", 
              colors: { bg: "bg-cyan-500/10", border: "border-cyan-500/20", text: "text-cyan-400" } 
            }
          ].map((feature, i) => (
            <motion.div 
              key={i}
              whileHover={{ y: -10, backgroundColor: "rgba(255,255,255,0.05)", borderColor: `rgba(255,255,255,0.15)` }}
              className="glass-card rounded-[16px] flex flex-col group transition-colors cursor-pointer"
              style={{ padding: '32px', gap: '20px' }}
            >
               <motion.div whileHover={{ rotate: 15, scale: 1.1 }} className={`w-[48px] h-[48px] rounded-[12px] ${feature.colors.bg} border ${feature.colors.border} flex items-center justify-center ${feature.colors.text}`}>
                  <feature.icon className="w-[24px] h-[24px]" />
               </motion.div>
               <div className="flex flex-col" style={{ gap: '8px' }}>
                 <motion.h3 whileHover={{ x: 5, color: "#fff" }} className="text-[20px] font-bold text-white transition-colors">{feature.title}</motion.h3>
                 <motion.p whileHover={{ color: "#E2E8F0" }} className="text-gray-400 text-[15px] leading-relaxed transition-colors">
                   {feature.desc}
                 </motion.p>
               </div>
            </motion.div>
          ))}

        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="relative z-10 border-t border-white/10 py-[80px] px-[24px] mt-[80px] flex flex-col items-center gap-[40px]">
         <motion.div whileHover={{ scale: 1.1 }} className="flex items-center gap-[12px] cursor-pointer">
            <motion.div whileHover={{ rotate: 180 }} transition={{ duration: 0.5 }} className="w-[24px] h-[24px] rounded-[6px] bg-blue-600 flex items-center justify-center font-black text-[12px]">R</motion.div>
            <span className="font-bold text-[18px] tracking-tight text-white/70 hover:text-white transition-colors">ReconIQ</span>
         </motion.div>
         
         <div className="flex items-center gap-[40px]">
            <motion.a whileHover={{ y: -4, color: "#fff", scale: 1.1 }} className="text-gray-500 transition-colors" href="https://github.com/Aarush-bigO" target="_blank" rel="noopener noreferrer">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
            </motion.a>
            <motion.a whileHover={{ y: -4, color: "#fff", scale: 1.1 }} className="text-gray-500 transition-colors" href="https://www.linkedin.com/in/aarush-bharti-667a43324/" target="_blank" rel="noopener noreferrer">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            </motion.a>
            <motion.a whileHover={{ y: -4, color: "#fff", scale: 1.1 }} className="text-gray-500 transition-colors" href="https://x.com/Aarush52410944" target="_blank" rel="noopener noreferrer">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 24 24"><path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/></svg>
            </motion.a>
            <motion.a whileHover={{ y: -4, color: "#fff", scale: 1.1 }} className="text-gray-500 transition-colors" href="mailto:aarushbharti2005@gmail.com">
              <Mail className="w-[24px] h-[24px]" />
            </motion.a>
         </div>

         <motion.p whileHover={{ letterSpacing: "1px", color: "#94A3B8" }} className="text-gray-500 text-[15px] cursor-pointer transition-all text-center max-w-sm leading-relaxed">
           © 2026 ReconIQ Inc. Buildathon Edition. <br /> Crafted with precision by Aarush.
         </motion.p>
      </footer>
    </div>
  );
}
