import re

with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

# Define the ProfileDropdown component
profile_dropdown_code = """
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
            <span style={{ fontSize: 14, fontWeight: 700, color: '#0F172A' }}>Aarush Singh</span>
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
"""

# Insert the component definition before LayoutBody
content = content.replace('export default function LayoutBody(', profile_dropdown_code + '\nexport default function LayoutBody(')

# Replace the static avatar div with the ProfileDropdown component
static_avatar_regex = r"<div style={{ width: 36, height: 36, borderRadius: '50%', background: '#2D68FE', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: '#fff', cursor: 'pointer', boxShadow: '0 2px 8px rgba\(45,104,254,0\.3\)' }}>A</div>"

content = re.sub(static_avatar_regex, "<ProfileDropdown />", content)

with open("apps/web/components/LayoutBody.tsx", "w") as f:
    f.write(content)

print("Patched LayoutBody to include an interactive ProfileDropdown.")
