import re

with open("apps/web/components/LayoutBody.tsx", "r") as f:
    content = f.read()

# Replace the {isLanding ? ( <TopNav /> ) : ( <header> ... )} part
# We will just render nothing for header if isLanding is true.

new_logic = """      {isLanding ? null : (
        <header style={{ 
          height: 72, background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)',
          borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
          padding: '0 40px', position: 'sticky', top: 0, zIndex: 100 
        }}>"""

content = re.sub(r'\{\s*isLanding\s*\?\s*\(\s*<TopNav />\s*\)\s*:\s*\(\s*<header style=\{\{\s*height: 72, background: \'rgba\(255, 255, 255, 0\.95\)\', backdropFilter: \'blur\(10px\)\',\s*borderBottom: \'1px solid #E2E8F0\', display: \'flex\', alignItems: \'center\', justifyContent: \'space-between\', \s*padding: \'0 40px\', position: \'sticky\', top: 0, zIndex: 100 \s*\}\}>', new_logic, content)

with open("apps/web/components/LayoutBody.tsx", "w") as f:
    f.write(content)

