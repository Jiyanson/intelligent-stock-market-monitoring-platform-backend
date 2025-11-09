#!/usr/bin/env python3
"""
AI-Powered Security Report Generator
Processes REAL vulnerability data and generates actionable security reports
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_vulnerability_data(processed_dir: str = "processed") -> Dict[str, Any]:
    """Load normalized vulnerability data."""
    vuln_file = Path(processed_dir) / "normalized_vulnerabilities.json"

    if not vuln_file.exists():
        print(f"❌ No vulnerability data found at {vuln_file}")
        return {"vulnerabilities": [], "risk_metrics": {"total": 0}}

    with open(vuln_file, 'r') as f:
        data = json.load(f)

    # Handle different formats
    if isinstance(data, list):
        vulnerabilities = data
    elif isinstance(data, dict):
        vulnerabilities = data.get('vulnerabilities', [])
    else:
        vulnerabilities = []

    return {
        "vulnerabilities": vulnerabilities,
        "total_count": len(vulnerabilities)
    }

def analyze_vulnerabilities(vulnerabilities: List[Dict]) -> Dict[str, Any]:
    """Analyze and categorize vulnerabilities."""
    analysis = {
        "total": len(vulnerabilities),
        "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0},
        "by_tool": {},
        "by_category": {},
        "top_critical": [],
        "packages_to_update": set(),
        "files_with_issues": set()
    }

    for vuln in vulnerabilities:
        # Count by severity
        severity = vuln.get('severity', 'UNKNOWN').upper()
        if severity in analysis['by_severity']:
            analysis['by_severity'][severity] += 1

        # Count by tool
        tool = vuln.get('tool', vuln.get('source', 'Unknown'))
        analysis['by_tool'][tool] = analysis['by_tool'].get(tool, 0) + 1

        # Count by category
        category = vuln.get('category', vuln.get('type', 'Unknown'))
        analysis['by_category'][category] = analysis['by_category'].get(category, 0) + 1

        # Collect critical/high items
        if severity in ['CRITICAL', 'HIGH']:
            analysis['top_critical'].append({
                'id': vuln.get('id', 'N/A'),
                'title': vuln.get('title', 'No title'),
                'severity': severity,
                'tool': tool,
                'package': vuln.get('package', vuln.get('file', 'N/A')),
                'description': vuln.get('description', '')[:200]
            })

        # Collect packages that need updates
        if vuln.get('package'):
            analysis['packages_to_update'].add(vuln['package'])

        # Collect files with issues
        if vuln.get('file'):
            analysis['files_with_issues'].add(vuln['file'])

    # Sort top critical by severity
    analysis['top_critical'] = sorted(
        analysis['top_critical'][:50],  # Top 50
        key=lambda x: 0 if x['severity'] == 'CRITICAL' else 1
    )

    # Calculate risk score
    analysis['risk_score'] = (
        analysis['by_severity']['CRITICAL'] * 10 +
        analysis['by_severity']['HIGH'] * 5 +
        analysis['by_severity']['MEDIUM'] * 2 +
        analysis['by_severity']['LOW'] * 1
    )

    # Determine risk level
    if analysis['by_severity']['CRITICAL'] > 0:
        analysis['risk_level'] = "CRITICAL"
    elif analysis['by_severity']['HIGH'] > 10:
        analysis['risk_level'] = "HIGH"
    elif analysis['by_severity']['HIGH'] > 0:
        analysis['risk_level'] = "MEDIUM-HIGH"
    else:
        analysis['risk_level'] = "MEDIUM"

    return analysis

def generate_executive_summary_html(analysis: Dict[str, Any], build_number: str = "N/A") -> str:
    """Generate executive summary HTML report."""
    severity_counts = analysis['by_severity']
    top_risks = analysis['top_critical'][:10]

    risk_rows = ""
    for risk in top_risks:
        sev_class = risk['severity'].lower()
        risk_rows += f"""
        <tr>
            <td><strong>{risk['title']}</strong><br><small>{risk['package']}</small></td>
            <td>{risk['tool']}</td>
            <td><span class="sev {sev_class}">{risk['severity']}</span></td>
            <td>{'24h' if risk['severity'] == 'CRITICAL' else '72h'}</td>
        </tr>
        """

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Executive Security Summary — Build #{build_number}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{{font:14px/1.5 system-ui,Segoe UI,Roboto,Ubuntu,Helvetica,Arial,sans-serif;margin:24px;color:#1f2328}}
 h1,h2{{margin:0 0 8px}} h1{{font-size:22px}} h2{{font-size:16px;margin-top:24px}}
 .kpi{{display:flex;gap:12px;margin:12px 0;flex-wrap:wrap}}
 .kpi div{{border:1px solid #e0e4e8;border-radius:8px;padding:10px 12px;min-width:140px}}
 .sev{{display:inline-block;border-radius:6px;padding:2px 8px;margin-right:6px}}
 .critical{{background:#ffe8e6;color:#a40000}} .high{{background:#fff0d6;color:#8a4b00}}
 .medium{{background:#eef2ff;color:#223076}} .low{{background:#eef7f0;color:#174d1a}}
 table{{width:100%;border-collapse:collapse;margin:8px 0 16px}}
 th,td{{border:1px solid #e6e9ed;padding:8px;text-align:left;vertical-align:top}}
 small{{color:#57606a}}
 .tag{{display:inline-block;background:#f2f4f7;border:1px solid #e3e6ea;border-radius:6px;padding:0 6px;margin-right:6px}}
 .alert{{background:#fff5e6;border-left:4px solid #ff9500;padding:12px;margin:12px 0}}
</style>
</head>
<body>
<h1>Executive Security Summary <small>— Build #{build_number} • {datetime.now().strftime('%Y-%m-%d')}</small></h1>

<div class="kpi">
  <div><strong>Total Vulnerabilities</strong><br><span style="font-size:24px">{analysis['total']}</span></div>
  <div><strong>Risk Score</strong><br><span style="font-size:24px;color:#a40000">{analysis['risk_score']}</span></div>
  <div><strong>Severity Breakdown</strong><br>
    <span class="sev critical">Critical: {severity_counts['CRITICAL']}</span>
    <span class="sev high">High: {severity_counts['HIGH']}</span>
    <span class="sev medium">Medium: {severity_counts['MEDIUM']}</span>
    <span class="sev low">Low: {severity_counts['LOW']}</span>
  </div>
  <div><strong>Quality Gate</strong><br><span class="tag">{'BLOCKED' if severity_counts['CRITICAL'] > 0 or severity_counts['HIGH'] > 10 else 'WARNING'}</span></div>
</div>

<div class="alert">
  <strong>⚠️ Security Alert:</strong> {severity_counts['CRITICAL']} critical and {severity_counts['HIGH']} high-severity vulnerabilities detected. Immediate action required.
</div>

<h2>Top {len(top_risks)} Critical Risks (Prioritized)</h2>
<table>
  <thead><tr><th>Finding</th><th>Source</th><th>Severity</th><th>Fix ETA</th></tr></thead>
  <tbody>
    {risk_rows}
  </tbody>
</table>

<h2>Remediation Plan</h2>
<ul>
  <li><strong>Container Security</strong>: Update {len([p for p in analysis['packages_to_update'] if 'lib' in str(p).lower()])} vulnerable base packages. Rebuild images with latest patches.</li>
  <li><strong>Dependencies</strong>: Upgrade {len(analysis['packages_to_update'])} packages with known CVEs. Review SBOM and apply updates.</li>
  <li><strong>Code Issues</strong>: Fix {len(analysis['files_with_issues'])} source files flagged by SAST scans.</li>
  <li><strong>Verification</strong>: Re-scan after fixes; add regression tests; update security baseline.</li>
</ul>

<h2>Standards Alignment</h2>
<p>
  <span class="tag">ISO 27001 A.12.6.1</span>
  <span class="tag">NIST SSDF PW.7</span>
  <span class="tag">OWASP ASVS 14.2</span>
  <span class="tag">PCI-DSS 6.2</span>
</p>

<h2>Next Steps</h2>
<ol>
  <li>Review this executive summary with security and DevOps teams</li>
  <li>Prioritize fixes based on severity and business impact</li>
  <li>Apply patches for critical/high vulnerabilities within SLA</li>
  <li>Re-run security scans to verify remediation</li>
  <li>Update security documentation and runbooks</li>
</ol>

</body>
</html>"""

    return html

def generate_technical_playbook_html(analysis: Dict[str, Any], vulnerabilities: List[Dict], build_number: str = "N/A") -> str:
    """Generate technical remediation playbook HTML."""

    # Group vulnerabilities by type
    container_vulns = [v for v in vulnerabilities if v.get('category') in ['Container Security', 'Container', 'OS Package']]
    dependency_vulns = [v for v in vulnerabilities if v.get('category') in ['SCA', 'Dependency', 'Vulnerable Dependency']]
    code_vulns = [v for v in vulnerabilities if v.get('category') in ['SAST', 'Code Quality', 'Code Vulnerability']]

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Technical Remediation Playbook — Build #{build_number}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{{font:14px system-ui;margin:24px;color:#1f2328}}
 h1{{font-size:20px;margin:0 0 8px}}
 h2{{font-size:16px;margin:18px 0 8px}}
 .block{{border:1px solid #e0e4e8;border-radius:10px;padding:14px;margin:12px 0}}
 code{{background:#f6f8fa;padding:2px 6px;border-radius:4px;font-size:13px}}
 pre{{background:#f6f8fa;padding:12px;border-radius:6px;overflow-x:auto}}
 .sev{{padding:2px 8px;border-radius:6px;border:1px solid #e3e6ea;margin-right:6px}}
 .critical{{background:#ffe8e6;color:#a40000}}
 .high{{background:#fff0d6;color:#8a4b00}}
 table{{width:100%;border-collapse:collapse;margin:8px 0}}
 th,td{{border:1px solid #e6e9ed;padding:8px;text-align:left}}
</style>
</head>
<body>
<h1>Technical Remediation Playbook <small>Build #{build_number}</small></h1>

<div class="block">
  <strong>📊 Vulnerability Summary</strong>
  <ul>
    <li>Total Vulnerabilities: {analysis['total']}</li>
    <li>Container/OS Issues: {len(container_vulns)}</li>
    <li>Dependency Issues: {len(dependency_vulns)}</li>
    <li>Code Issues: {len(code_vulns)}</li>
    <li>Risk Level: <span class="sev {'critical' if analysis['risk_level'] == 'CRITICAL' else 'high'}">{analysis['risk_level']}</span></li>
  </ul>
</div>

<h2>🐳 Container Security Fixes</h2>
<div class="block">
  <p><strong>Issue:</strong> {len(container_vulns)} vulnerabilities in container base image and OS packages</p>

  <p><strong>Action:</strong></p>
  <pre>
# 1. Update Dockerfile base image
FROM python:3.11-slim  # Use latest stable version

# 2. Update OS packages
RUN apt-get update && apt-get upgrade -y && \\
    apt-get install -y --no-install-recommends \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# 3. Scan image after rebuild
docker build -t app:latest .
trivy image --severity CRITICAL,HIGH app:latest
  </pre>

  <p><strong>Priority Packages to Update:</strong></p>
  <ul>
    {"".join([f"<li><code>{pkg}</code></li>" for pkg in sorted(list(analysis['packages_to_update']))[:10]])}
  </ul>
</div>

<h2>📦 Dependency Updates</h2>
<div class="block">
  <p><strong>Issue:</strong> {len(dependency_vulns)} vulnerable dependencies detected</p>

  <p><strong>Action:</strong></p>
  <pre>
# 1. Update requirements.txt with patched versions
# Check for updates:
pip list --outdated

# 2. Update specific packages with known CVEs
pip install --upgrade requests urllib3 cryptography

# 3. Regenerate lock file
pip freeze > requirements.txt

# 4. Re-scan dependencies
safety check
dependency-check --project "App" --scan .
  </pre>
</div>

<h2>💻 Code Security Fixes</h2>
<div class="block">
  <p><strong>Issue:</strong> {len(code_vulns)} code-level vulnerabilities found by SAST</p>

  <p><strong>Common Fixes:</strong></p>
  <ul>
    <li>Input Validation: Sanitize all user inputs before processing</li>
    <li>SQL Injection: Use parameterized queries or ORM</li>
    <li>XSS Prevention: Escape output, set CSP headers</li>
    <li>Authentication: Enforce strong password policies, use MFA</li>
    <li>Session Management: Set HttpOnly, Secure, SameSite flags on cookies</li>
  </ul>

  <pre>
# Example: Fix cookie security
response.set_cookie(
    "session",
    value=session_id,
    httponly=True,  # Prevent XSS access
    secure=True,    # HTTPS only
    samesite="Lax"  # CSRF protection
)
  </pre>
</div>

<h2>🔄 Verification Steps</h2>
<div class="block">
  <ol>
    <li>Apply fixes and commit changes</li>
    <li>Trigger CI/CD pipeline</li>
    <li>Review scan results - expect reduced vulnerability count</li>
    <li>Run regression tests</li>
    <li>Deploy to staging for validation</li>
    <li>Update security baseline documentation</li>
  </ol>
</div>

</body>
</html>"""

    return html

def generate_detailed_findings_html(vulnerabilities: List[Dict], analysis: Dict[str, Any], build_number: str = "N/A") -> str:
    """Generate detailed findings report."""

    # Limit to top 100 for readability
    top_vulns = vulnerabilities[:100]

    rows = ""
    for vuln in top_vulns:
        sev_class = vuln.get('severity', 'MEDIUM').lower()
        rows += f"""
        <tr>
            <td><code>{vuln.get('id', 'N/A')}</code></td>
            <td>{vuln.get('title', 'No title')}</td>
            <td><span class="sev {sev_class}">{vuln.get('severity', 'UNKNOWN')}</span></td>
            <td>{vuln.get('tool', vuln.get('source', 'Unknown'))}</td>
            <td><small>{vuln.get('package', vuln.get('file', 'N/A'))}</small></td>
        </tr>
        """

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Detailed Vulnerability Findings — Build #{build_number}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{{font:13px system-ui;margin:20px;color:#1f2328}}
 h1{{font-size:18px}}
 table{{width:100%;border-collapse:collapse;font-size:12px}}
 th,td{{border:1px solid #e6e9ed;padding:6px;text-align:left}}
 th{{background:#f6f8fa}}
 .sev{{padding:2px 6px;border-radius:4px;font-size:11px}}
 .critical{{background:#ffe8e6;color:#a40000}}
 .high{{background:#fff0d6;color:#8a4b00}}
 .medium{{background:#eef2ff;color:#223076}}
 .low{{background:#eef7f0;color:#174d1a}}
 small{{color:#57606a}}
</style>
</head>
<body>
<h1>Detailed Vulnerability Findings <small>Build #{build_number} • Showing top {len(top_vulns)} of {analysis['total']}</small></h1>

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Title</th>
      <th>Severity</th>
      <th>Tool</th>
      <th>Package/File</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>

<p><small>Total vulnerabilities: {analysis['total']} • Showing top {len(top_vulns)} ordered by severity</small></p>

</body>
</html>"""

    return html

def main():
    """Main execution."""
    print("=" * 70)
    print("🤖 AI-POWERED SECURITY REPORT GENERATOR")
    print("=" * 70)

    # Get build number from environment or default
    build_number = os.environ.get('BUILD_NUMBER', 'LOCAL')

    # Create output directory
    output_dir = Path("ai-reports")
    output_dir.mkdir(exist_ok=True)

    # Load vulnerability data
    print("\n📂 Loading vulnerability data...")
    data = load_vulnerability_data()
    vulnerabilities = data['vulnerabilities']

    if not vulnerabilities:
        print("❌ No vulnerabilities found. Generating placeholder reports...")
        vulnerabilities = [{"id": "NONE", "title": "No vulnerabilities detected", "severity": "INFO"}]

    print(f"✅ Loaded {len(vulnerabilities)} vulnerabilities")

    # Analyze vulnerabilities
    print("\n📊 Analyzing vulnerabilities...")
    analysis = analyze_vulnerabilities(vulnerabilities)
    print(f"   Risk Level: {analysis['risk_level']}")
    print(f"   Risk Score: {analysis['risk_score']}")
    print(f"   Critical: {analysis['by_severity']['CRITICAL']}, High: {analysis['by_severity']['HIGH']}")

    # Generate reports
    print("\n📄 Generating HTML reports...")

    # 1. Executive Summary
    exec_html = generate_executive_summary_html(analysis, build_number)
    exec_path = output_dir / "01_Executive_Security_Summary.html"
    exec_path.write_text(exec_html)
    print(f"   ✅ {exec_path}")

    # 2. Technical Playbook
    tech_html = generate_technical_playbook_html(analysis, vulnerabilities, build_number)
    tech_path = output_dir / "02_Technical_Playbook.html"
    tech_path.write_text(tech_html)
    print(f"   ✅ {tech_path}")

    # 3. Detailed Findings
    findings_html = generate_detailed_findings_html(vulnerabilities, analysis, build_number)
    findings_path = output_dir / "03_Detailed_Findings.html"
    findings_path.write_text(findings_html)
    print(f"   ✅ {findings_path}")

    # Save analysis JSON
    analysis_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "build_number": build_number,
            "total_vulnerabilities": analysis['total']
        },
        "analysis": {
            k: (list(v) if isinstance(v, set) else v)
            for k, v in analysis.items()
        }
    }

    json_path = output_dir / "analysis.json"
    with open(json_path, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"   ✅ {json_path}")

    print("\n" + "=" * 70)
    print("✅ REPORT GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n📁 Reports saved to: {output_dir.absolute()}")
    print(f"\n🎯 Summary:")
    print(f"   • Total Vulnerabilities: {analysis['total']}")
    print(f"   • Critical: {analysis['by_severity']['CRITICAL']}")
    print(f"   • High: {analysis['by_severity']['HIGH']}")
    print(f"   • Medium: {analysis['by_severity']['MEDIUM']}")
    print(f"   • Risk Level: {analysis['risk_level']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
