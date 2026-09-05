import os

print("1. Updating globals.css with 3D animations...")
css_path = 'apps/web/app/globals.css'
with open(css_path, 'r') as f:
    css_content = f.read()

animation_css = '''
/* ── Razorpay 3D Scroll Animations ── */
.animate-3d {
  opacity: 0;
  transform: perspective(1000px) rotateX(-8deg) translateY(40px) scale(0.96);
  transition: opacity 0.7s cubic-bezier(0.2, 0.8, 0.2, 1), transform 0.7s cubic-bezier(0.2, 0.8, 0.2, 1);
  will-change: opacity, transform;
}
.animate-3d.in-view {
  opacity: 1;
  transform: perspective(1000px) rotateX(0) translateY(0) scale(1);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
'''
if '.animate-3d' not in css_content:
    with open(css_path, 'a') as f:
        f.write(animation_css)

print("2. Rewriting LayoutBody.tsx for Top Navigation...")
layout = """\
"use client";
import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import TopNav from "@/components/TopNav";

const navGroups = [
  {
    title: "Finance",
    items: [
      { href: "/dashboard", label: "Overview", icon: "⬡" },
      { href: "/reconciliation", label: "Reconciliation", icon: "⚡" },
      { href: "/settlements", label: "Settlements", icon: "₹" },
      { href: "/exceptions", label: "Exceptions", icon: "⚠" },
      { href: "/period-close", label: "Period Close", icon: "🔒" },
      { href: "/audit", label: "Audit Trail", icon: "🔐" },
    ]
  },
  {
    title: "Operations",
    items: [
      { href: "/controls", label: "Control Checks", icon: "☑" },
      { href: "/transactions", label: "Transactions", icon: "⇄" },
      { href: "/data-quality", label: "Data Quality", icon: "◎" },
      { href: "/ai-control-room", label: "AI Control Room", icon: "✦" },
    ]
  },
  {
    title: "Analytics",
    items: [
      { href: "/query-lab", label: "Query Lab", icon: "🔍" },
      { href: "/reports", label: "Reports", icon: "📄" },
      { href: "/evaluation", label: "Evaluation Lab", icon: "◈" },
      { href: "/settings", label: "Settings", icon: "⚙" },
    ]
  }
];

function NavDropdown({ group }: { group: any }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  
  const isActive = group.items.some((i: any) => pathname.startsWith(i.href) && i.href !== "/") || 
                   (pathname === "/" && group.items.some((i: any) => i.href === "/"));

  return (
    <div 
      onMouseEnter={() => setOpen(true)} 
      onMouseLeave={() => setOpen(false)} 
      style={{ position: 'relative', height: '100%', display: 'flex', alignItems: 'center' }}
    >
      <div style={{ 
        cursor: 'pointer', padding: '8px 16px', fontWeight: 600, fontSize: 14, 
        color: isActive ? '#2D68FE' : '#475569',
        transition: 'color 0.2s ease',
        display: 'flex', alignItems: 'center', gap: 6
      }}>
        {group.title}
        <span style={{ fontSize: 10, transform: open ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}>▼</span>
      </div>
      
      {open && (
        <div style={{ 
          position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', 
          background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12, padding: 12, 
          width: 280, boxShadow: '0 10px 40px -10px rgba(0,0,0,0.1), 0 0 20px rgba(45, 104, 254, 0.05)', 
          zIndex: 100,
          animation: 'fadeInUp 0.2s ease'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
             {group.items.map((item: any) => (
                <Link href={item.href} key={item.href} style={{ textDecoration: 'none' }}>
                  <div style={{ 
                    display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', borderRadius: 8, 
                    color: pathname === item.href ? '#2D68FE' : '#475569',
                    background: pathname === item.href ? '#EFF6FF' : 'transparent',
                    transition: 'all 0.15s ease' 
                  }}
                       onMouseEnter={e => { e.currentTarget.style.background = '#F8FAFC'; e.currentTarget.style.color = '#0F172A'; }}
                       onMouseLeave={e => { e.currentTarget.style.background = pathname === item.href ? '#EFF6FF' : 'transparent'; e.currentTarget.style.color = pathname === item.href ? '#2D68FE' : '#475569'; }}>
                    <span style={{ color: pathname === item.href ? '#2D68FE' : '#94A3B8', fontSize: 16, width: 20, textAlign: 'center' }}>{item.icon}</span>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{item.label}</span>
                  </div>
                </Link>
             ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function LayoutBody({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLanding = pathname === "/";

  // 3D Scroll Intersection Observer
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
        }
      });
    }, { threshold: 0.05, rootMargin: '0px 0px -50px 0px' });

    // Give React a tick to render elements
    const timer = setTimeout(() => {
      const elements = document.querySelectorAll('.animate-3d');
      elements.forEach(el => observer.observe(el));
    }, 100);

    return () => {
      clearTimeout(timer);
      observer.disconnect();
    };
  }, [pathname]);

  if (isLanding) return <body className="landing-mode"><TopNav /><main>{children}</main></body>;

  return (
    <body className="dashboard-mode" style={{ background: '#F8FAFC', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Mega Menu Top Nav */}
      <header style={{ 
        height: 72, background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)',
        borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
        padding: '0 40px', position: 'sticky', top: 0, zIndex: 100 
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 48, height: '100%' }}>
          {/* Logo */}
          <Link href="/dashboard" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #2D68FE, #1E4FD8)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 800, color: '#fff', boxShadow: '0 2px 8px rgba(45, 104, 254, 0.3)' }}>R</div>
            <div>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', lineHeight: 1.2 }}>ReconIQ</div>
            </div>
          </Link>
          
          {/* Nav Items */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: 16, height: '100%' }}>
            {navGroups.map((group) => (
              <NavDropdown key={group.title} group={group} />
            ))}
          </nav>
        </div>
        
        {/* Right side actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 12px', background: '#F1F5F9', borderRadius: 99, border: '1px solid transparent', transition: 'border 0.2s' }}>
             <span style={{ fontSize: 14 }}>🔍</span>
             <input type="text" placeholder="Search PAY, UTR..." style={{ border: 'none', background: 'transparent', outline: 'none', width: 140, fontSize: 13, color: '#0F172A' }} />
             <span style={{ fontSize: 11, color: '#94A3B8', fontWeight: 600, background: '#fff', padding: '2px 6px', borderRadius: 4, border: '1px solid #E2E8F0' }}>⌘K</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px rgba(16,185,129,0.3)' }} />
            <span style={{ fontSize: 11, fontWeight: 700, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Live</span>
          </div>
          <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#2D68FE', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: '#fff', cursor: 'pointer', boxShadow: '0 2px 8px rgba(45,104,254,0.3)' }}>A</div>
        </div>
      </header>

      {/* Main content - centered and max-width like Razorpay */}
      <main style={{ flex: 1, padding: '48px 40px', maxWidth: 1360, margin: '0 auto', width: '100%' }}>
        {children}
      </main>
    </body>
  );
}
"""
with open('apps/web/components/LayoutBody.tsx', 'w') as f:
    f.write(layout)

print("3. Injecting animate-3d classes into all cards and elements...")
replacements = {
    'className="card"': 'className="card animate-3d"',
    'className="kpi-card"': 'className="kpi-card animate-3d"',
    'className="table-wrapper"': 'className="table-wrapper animate-3d"',
    'className="data-table"': 'className="data-table animate-3d"',
    'className="card ': 'className="card animate-3d ',
    'className="kpi-card ': 'className="kpi-card animate-3d ',
    # We can also add it to header blocks to make titles pop in
    '<div style={{ marginBottom: 32 }}>': '<div className="animate-3d" style={{ marginBottom: 32 }}>',
    '<div style={{ marginBottom: 28 }}>': '<div className="animate-3d" style={{ marginBottom: 28 }}>',
}

folders = [
    'dashboard', 'reconciliation', 'exceptions', 'query-lab', 'ai-control-room',
    'audit', 'controls', 'data-quality', 'evaluation', 'ledger', 'reports', 'settings', 'settlements', 'transactions'
]

for folder in folders:
    path = f'apps/web/app/{folder}/page.tsx'
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        
        # Avoid double inject
        if 'animate-3d' not in content:
            for k, v in replacements.items():
                content = content.replace(k, v)
            with open(path, 'w') as f:
                f.write(content)

print("4. Cleaning up Sidebar file...")
if os.path.exists('apps/web/components/Sidebar.tsx'):
    os.remove('apps/web/components/Sidebar.tsx')

print("Done! Architecture shifted to Top Nav + 3D Scroll Animations.")
