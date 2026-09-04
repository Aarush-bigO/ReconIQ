import re

with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

# Find the start of LayoutBody
start_idx = content.find("export default function LayoutBody")

new_layout = """export default function LayoutBody({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLanding = pathname === "/";

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
      
      {isLanding ? (
        <TopNav />
      ) : (
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
"""

content = content[:start_idx] + new_layout

with open("apps/web/components/LayoutBody.tsx", "w") as f:
    f.write(content)
