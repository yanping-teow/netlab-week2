import os
import yaml
import sys
from datetime import datetime, timezone

import html
 
def links_section(spec):
    items = "\n".join(
        f"<li><code>{html.escape(a)}</code> ↔ <code>{html.escape(b)}</code></li>"
        for a, b in spec["links"]
    )
    return f"<ul>\n{items}\n</ul>"
 
def mermaid_diagram(spec):
    lines = ["graph LR"]
    for a, b in spec["links"]:
        lines.append(f"    {a} --- {b}")
    return "\n".join(lines)
 

def generate_html(topology_path="topology.yaml", page_path="page.yaml", output_dir="docs"):
    with open(topology_path, "r") as f:
        data = yaml.safe_load(f)

    page_data = {}
    if os.path.exists(page_path):
        with open(page_path, "r") as f:
            page_data = yaml.safe_load(f) or {}

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")

    network_name = data.get("network_name", "Programmable Network")
    description = data.get("description", "")
    
    switch_rows = "".join(
        f"<tr><td><code>{s['name']}</code></td><td>{s.get('role', '')}</td><td><code>{s.get('dpid', '')}</code></td></tr>"
        for s in data.get("switches", [])
    )
    
    host_rows = "".join(
        f"<tr><td><code>{h['name']}</code></td><td><code>{h.get('ip', '')}</code></td><td><code>{h.get('ipv6', '')}</code></td><td><code>{h.get('mac', '')}</code></td><td><code>{h['switch']}</code></td></tr>"
        for h in data.get("hosts", [])
    )

    answers = page_data.get("answers", {})
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <title>{network_name} — Network Documentation</title>
  <script type=\"module\">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
  </script>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #1e293b; line-height: 1.6; }}
    h1, h2 {{ color: #0f172a; }}
    .badge {{ background: #e2e8f0; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.9rem; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 0.6rem 0.8rem; text-align: left; }}
    th {{ background: #f8fafc; }}
    .diagram-box {{ background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1.5rem; text-align: center; }}
    footer {{ font-size: 0.85rem; color: #64748b; margin-top: 3rem; border-top: 1px solid #e2e8f0; padding-top: 1rem; }}
  </style>
</head>
<body>
  <h1>{network_name}</h1>
  <p>{description} · <span class=\"badge\">Student ID ending: {data.get('student_id_last4')}</span></p>

  <h2>Topology Diagram</h2>
  <div class=\"diagram-box\">
    <pre class=\"mermaid\">
{mermaid_diagram(data)}
    </pre>
  </div>

  <h2>Links Overview</h2>
  {links_section(data)}

  <h2>Switch Inventory</h2>
  <table>
    <thead><tr><th>Switch</th><th>Role</th><th>DPID</th></tr></thead>
    <tbody>{switch_rows}</tbody>
  </table>

  <h2>Host Addressing Inventory</h2>
  <table>
    <thead><tr><th>Host</th><th>IPv4 Address</th><th>IPv6 Address</th><th>MAC Address</th><th>Attached Switch</th></tr></thead>
    <tbody>{host_rows}</tbody>
  </table>

  <h2>Assignment Reflections</h2>
  <h3>1. Data Model vs. Serialisation</h3>
  <p>{answers.get('q1', 'No answer provided.')}</p>

  <h3>2. Static Validation vs. Runtime Checks (IPv4 vs. IPv6 DAD)</h3>
  <p>{answers.get('q2', 'No answer provided.')}</p>

  <h3>3. Value of Version Control (Git Diff)</h3>
  <p>{answers.get('q3', 'No answer provided.')}</p>

  <footer>Generated automatically from <code>topology.yaml</code> on {timestamp}</footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated documentation at {output_path}")

if __name__ == "__main__":
    generate_html()
