import re

with open("apps/web/app/reports/page.tsx", "r") as f:
    content = f.read()

# Replace the alert button clicks with a function call
content = content.replace('onClick={() => alert("Downloading CSV...")}', 'onClick={() => downloadCSV(r.title)}')
content = content.replace('onClick={() => alert("Downloading JSON...")}', 'onClick={() => downloadJSON(r.title)}')

# Inject the download functions
download_funcs = """
  const downloadCSV = (reportName: string) => {
    const data = DATA_MAP[reportName];
    if (!data || data.length === 0) return;
    const headers = Object.keys(data[0]).join(",");
    const rows = data.map((r: any) => Object.values(r).map(v => `"${v}"`).join(",")).join("\\n");
    const blob = new Blob([`${headers}\\n${rows}`], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportName.replace(/ /g, "_").toLowerCase()}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadJSON = (reportName: string) => {
    const data = DATA_MAP[reportName];
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportName.replace(/ /g, "_").toLowerCase()}_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
"""

# Insert right after the useState
content = content.replace('const [activeReport, setActiveReport] = useState<string | null>(null);', 'const [activeReport, setActiveReport] = useState<string | null>(null);\n' + download_funcs)

with open("apps/web/app/reports/page.tsx", "w") as f:
    f.write(content)

print("Patched reports page to actually download CSV and JSON files.")
