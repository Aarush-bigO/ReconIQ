import re

with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

# Add useRouter and useState for search
content = content.replace('import { usePathname } from "next/navigation";', 'import { usePathname, useRouter } from "next/navigation";')

# Add state to LayoutBody
layout_body_match = re.search(r'export default function LayoutBody\(\{ children \}: \{ children: React\.ReactNode \}\) \{\n  const pathname = usePathname\(\);', content)
if layout_body_match:
    content = content.replace(
        'export default function LayoutBody({ children }: { children: React.ReactNode }) {\n  const pathname = usePathname();',
        'export default function LayoutBody({ children }: { children: React.ReactNode }) {\n  const pathname = usePathname();\n  const router = useRouter();\n  const [searchQuery, setSearchQuery] = useState("");'
    )

# Replace the input element
old_input = '<input type="text" placeholder="Search PAY, UTR..." style={{ border: \'none\', background: \'transparent\', outline: \'none\', width: 140, fontSize: 13, color: \'#0F172A\' }} />'
new_input = """<input 
               type="text" 
               placeholder="Search PAY, UTR..." 
               value={searchQuery}
               onChange={e => setSearchQuery(e.target.value)}
               onKeyDown={e => {
                 if (e.key === 'Enter' && searchQuery.trim()) {
                   router.push(`/transactions?search=${encodeURIComponent(searchQuery.trim())}`);
                 }
               }}
               style={{ border: 'none', background: 'transparent', outline: 'none', width: 140, fontSize: 13, color: '#0F172A' }} 
             />"""
content = content.replace(old_input, new_input)

# Add cmd+k support via useEffect
cmd_k_effect = """
  // 3D Scroll Intersection Observer
"""
new_cmd_k_effect = """
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
"""
content = content.replace(cmd_k_effect, new_cmd_k_effect)

# Add id to input
content = content.replace('type="text"', 'id="global-search-input" type="text"')

with open("apps/web/components/LayoutBody.tsx", "w") as f:
    f.write(content)
