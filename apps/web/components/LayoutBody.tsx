"use client";
import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import TopNav from "@/components/TopNav";
import CustomCursor from "@/components/CustomCursor";
import Global3DEffect from "@/components/Global3DEffect";

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
      { href: "/integrations", label: "Integrations", icon: "⚡" },
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
  },
  {
    title: "Developers",
    items: [
      { href: "/docs", label: "Documentation", icon: "📚" },
      { href: "/settings", label: "API Keys", icon: "🔑" },
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


function ProfileDropdown() {
  const [open, setOpen] = useState(false);

  return (
    <div 
      onMouseEnter={() => setOpen(true)} 
      onMouseLeave={() => setOpen(false)} 
      style={{ position: 'relative', display: 'flex', alignItems: 'center', height: '100%' }}
    >
      <div style={{ 
        width: 36, height: 36, borderRadius: '50%', background: '#2D68FE', 
        display: 'flex', alignItems: 'center', justifyContent: 'center', 
        fontSize: 14, fontWeight: 700, color: '#fff', cursor: 'pointer', 
        boxShadow: open ? '0 0 0 4px rgba(45,104,254,0.2)' : '0 2px 8px rgba(45,104,254,0.3)',
        transition: 'all 0.2s ease',
        transform: open ? 'scale(1.05)' : 'scale(1)'
      }}>
        A
      </div>
      
      {open && (
        <div style={{ 
          position: 'absolute', top: '100%', right: 0, marginTop: 8,
          background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12, padding: '8px 0', 
          width: 260, boxShadow: '0 20px 40px -10px rgba(0,0,0,0.1), 0 0 20px rgba(45, 104, 254, 0.05)', 
          zIndex: 200,
          animation: 'fadeInUp 0.2s ease',
          transformOrigin: 'top right'
        }}>
          {/* User Profile Header */}
          <div style={{ padding: '8px 16px', display: 'flex', flexDirection: 'column', gap: 2 }}>
            <span style={{ fontSize: 14, fontWeight: 700, color: '#0F172A' }}>Aarush Bharti</span>
            <span style={{ fontSize: 13, color: '#64748B' }}>aarush@reconiq.com</span>
            <div style={{ marginTop: 8, padding: '4px 8px', background: '#F1F5F9', borderRadius: 6, fontSize: 11, fontWeight: 600, color: '#475569', display: 'inline-block', width: 'fit-content' }}>
              Pro Workspace
            </div>
          </div>
          
          <div style={{ height: 1, background: '#E2E8F0', margin: '8px 0' }} />
          
          {/* Menu Items */}
          <div style={{ display: 'flex', flexDirection: 'column' }}>
             {[
               { icon: "⚙", label: "Account Settings", href: "/settings" },
               { icon: "👥", label: "Team Management", href: "/settings" },
               { icon: "💳", label: "Billing & Plans", href: "/settings" },
               { icon: "🔑", label: "Developer API Keys", href: "/settings" },
             ].map((item, i) => (
                <Link href={item.href} key={i} style={{ textDecoration: 'none' }}>
                  <div style={{ 
                    display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px', 
                    color: '#475569', transition: 'all 0.15s ease' 
                  }}
                       onMouseEnter={e => { e.currentTarget.style.background = '#F8FAFC'; e.currentTarget.style.color = '#0F172A'; }}
                       onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#475569'; }}>
                    <span style={{ fontSize: 16, width: 20, textAlign: 'center', opacity: 0.8 }}>{item.icon}</span>
                    <span style={{ fontWeight: 500, fontSize: 13 }}>{item.label}</span>
                  </div>
                </Link>
             ))}
          </div>
          
          <div style={{ height: 1, background: '#E2E8F0', margin: '8px 0' }} />
          
          {/* Logout */}
          <div 
            style={{ 
              display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px', 
              color: '#EF4444', cursor: 'pointer', transition: 'all 0.15s ease' 
            }}
            onMouseEnter={e => { e.currentTarget.style.background = '#FEF2F2'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            onClick={() => window.location.href = "/"}
          >
            <span style={{ fontSize: 16, width: 20, textAlign: 'center', opacity: 0.8 }}>🚪</span>
            <span style={{ fontWeight: 600, fontSize: 13 }}>Log out</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function LayoutBody({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLanding = pathname === "/" || pathname === "/docs";

  // Cmd+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const input = document.getElementById('global-search-input');
        if (input) input.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // 3D Scroll Intersection Observer
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
        }
      });
    }, { threshold: 0.05, rootMargin: '0px 0px -50px 0px' });

    const timer = setTimeout(() => {
      const elements = document.querySelectorAll('.animate-3d');
      elements.forEach(el => observer.observe(el));
    }, 100);

    return () => {
      clearTimeout(timer);
      observer.disconnect();
    };
  }, [pathname]);

  return (
    <body className={isLanding ? "landing-mode" : "dashboard-mode"} style={{ background: isLanding ? '#ffffff' : '#F8FAFC', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <CustomCursor />
      <Global3DEffect />
      
            {isLanding ? null : (
        <header style={{ 
          height: 72, background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)',
          borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
          padding: '0 40px', position: 'sticky', top: 0, zIndex: 100 
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 48, height: '100%' }}>
            <Link href="/dashboard" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #2D68FE, #1E4FD8)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 800, color: '#fff', boxShadow: '0 2px 8px rgba(45, 104, 254, 0.3)' }}>R</div>
              <div>
                <div style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', lineHeight: 1.2 }}>ReconIQ</div>
              </div>
            </Link>
            
            <nav style={{ display: 'flex', alignItems: 'center', gap: 16, height: '100%' }}>
              {navGroups.map((group) => (
                <NavDropdown key={group.title} group={group} />
              ))}
            </nav>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 12px', background: '#F1F5F9', borderRadius: 99, border: '1px solid transparent', transition: 'border 0.2s' }}>
               <span style={{ fontSize: 14 }}>🔍</span>
               <input 
                 id="global-search-input" type="text" 
                 placeholder="Search PAY, UTR..." 
                 onKeyDown={e => {
                   if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                     window.location.href = `/transactions?search=${encodeURIComponent(e.currentTarget.value.trim())}`;
                   }
                 }}
                 style={{ border: 'none', background: 'transparent', outline: 'none', width: 140, fontSize: 13, color: '#0F172A' }} 
               />
               <span style={{ fontSize: 11, color: '#94A3B8', fontWeight: 600, background: '#fff', padding: '2px 6px', borderRadius: 4, border: '1px solid #E2E8F0' }}>⌘K</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px rgba(16,185,129,0.3)' }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Live</span>
            </div>
            <ProfileDropdown />
          </div>
        </header>
      )}

      <main style={{ flex: 1, ...(isLanding ? {} : { padding: '48px 40px', maxWidth: 1360, margin: '0 auto', width: '100%' }) }}>
        {children}
      </main>
    </body>
  );
}
