#!/usr/bin/env python3
"""
AI-Powered Security Report Generator with LLM-Generated Remediation
Uses dual-model OpenRouter approach for dynamic remediation and playbooks
"""

import os
import json
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class LLMReportGenerator:
    """Generates security reports with LLM-powered remediation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        self.models = {
            "deepseek": "deepseek/deepseek-r1",
            "llama": "meta-llama/llama-3.3-70b-instruct"
        }

    def call_llm(self, model_key: str, prompt: str, max_tokens: int = 1500) -> Optional[str]:
        """Call LLM via OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/devsecops-pipeline",
            "X-Title": "DevSecOps Report Generator"
        }

        payload = {
            "model": self.models[model_key],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ LLM call failed ({model_key}): HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error calling {model_key}: {e}")

        return None

    def generate_remediation_plan(self, vulnerabilities: List[Dict], model_key: str = "deepseek") -> str:
        """Generate remediation plan using LLM."""

        # Prepare vulnerability summary
        critical = [v for v in vulnerabilities if v.get('severity') == 'CRITICAL']
        high = [v for v in vulnerabilities if v.get('severity') == 'HIGH']

        vuln_summary = f"Found {len(critical)} CRITICAL and {len(high)} HIGH severity vulnerabilities.\n\n"
        vuln_summary += "Top Critical Issues:\n"

        for i, v in enumerate(critical[:5] + high[:5], 1):
            vuln_summary += f"{i}. {v.get('title', 'Unknown')} - {v.get('package', v.get('file', 'N/A'))}\n"

        prompt = f"""You are a cybersecurity remediation expert. Based on these vulnerability scan results, create a concise, actionable remediation plan.

{vuln_summary}

Generate a remediation plan with:
1. **Immediate Actions** (24-48 hours) - Critical fixes
2. **Short-term Actions** (1-2 weeks) - High priority fixes
3. **Medium-term Actions** (1 month) - Medium priority improvements
4. **Long-term Actions** (Ongoing) - Security posture improvements

For each action, provide:
- Specific steps to take
- Commands or code changes needed
- Expected impact

Keep it concise and technical. Format as markdown with bullet points."""

        print(f"   🤖 Generating remediation plan with {model_key}...")
        response = self.call_llm(model_key, prompt)

        if response:
            print(f"   ✅ Remediation plan generated ({len(response)} chars)")
            return response
        else:
            return self._fallback_remediation(vulnerabilities)

    def generate_technical_playbook(self, vulnerabilities: List[Dict], analysis: Dict, model_key: str = "llama") -> str:
        """Generate technical playbook using LLM."""

        # Categorize vulnerabilities
        categories = {}
        for v in vulnerabilities:
            cat = v.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + 1

        prompt = f"""You are a DevSecOps engineer writing a technical remediation playbook.

**Vulnerability Breakdown:**
- Total: {len(vulnerabilities)}
- Critical: {analysis['by_severity']['CRITICAL']}
- High: {analysis['by_severity']['HIGH']}
- Categories: {', '.join([f"{k}: {v}" for k, v in categories.items()])}

**Top 10 Critical Vulnerabilities:**
{chr(10).join([f"- {v.get('title', 'Unknown')} in {v.get('package', v.get('file', 'N/A'))}" for v in vulnerabilities[:10]])}

Create a technical playbook with:

1. **Container Security Fixes**
   - Specific Dockerfile changes
   - Base image updates
   - Package updates needed

2. **Dependency Updates**
   - Exact commands to update vulnerable packages
   - Version constraints
   - Testing steps

3. **Code Security Fixes**
   - Common vulnerability patterns found
   - Code examples of fixes
   - Secure coding practices

4. **Verification Steps**
   - Commands to verify fixes
   - Testing checklist
   - Regression prevention

Provide ACTUAL commands, code snippets, and file names where applicable. Be specific and actionable.
Format as markdown."""

        print(f"   🤖 Generating technical playbook with {model_key}...")
        response = self.call_llm(model_key, prompt, max_tokens=2000)

        if response:
            print(f"   ✅ Technical playbook generated ({len(response)} chars)")
            return response
        else:
            return self._fallback_playbook(vulnerabilities)

    def _fallback_remediation(self, vulnerabilities: List[Dict]) -> str:
        """Fallback remediation if LLM fails."""
        critical_count = len([v for v in vulnerabilities if v.get('severity') == 'CRITICAL'])
        high_count = len([v for v in vulnerabilities if v.get('severity') == 'HIGH'])

        return f"""## Immediate Actions (24-48 hours)
- Address {critical_count} critical vulnerabilities
- Update vulnerable packages identified in scan
- Rebuild and redeploy affected containers

## Short-term Actions (1-2 weeks)
- Fix {high_count} high-severity issues
- Implement automated security scanning in CI/CD
- Update security baseline

## Medium-term Actions (1 month)
- Conduct security code review
- Update security documentation
- Train team on secure coding practices

## Long-term Actions (Ongoing)
- Implement continuous monitoring
- Regular security audits
- Maintain security tooling"""

    def _fallback_playbook(self, vulnerabilities: List[Dict]) -> str:
        """Fallback playbook if LLM fails."""
        return """## Container Security Fixes
```bash
# Update Dockerfile base image
FROM python:3.11-slim

# Update OS packages
RUN apt-get update && apt-get upgrade -y
```

## Dependency Updates
```bash
# Update vulnerable packages
pip install --upgrade $(pip list --outdated --format=json | jq -r '.[].name')
```

## Verification
```bash
# Re-scan after fixes
trivy image app:latest
safety check
```"""


def load_vulnerability_data(processed_dir: str = "processed") -> Dict[str, Any]:
    """Load normalized vulnerability data."""
    vuln_file = Path(processed_dir) / "normalized_vulnerabilities.json"

    if not vuln_file.exists():
        return {"vulnerabilities": [], "risk_metrics": {"total": 0}}

    with open(vuln_file, 'r') as f:
        data = json.load(f)

    vulnerabilities = data.get('vulnerabilities', [])
    risk_metrics = data.get('risk_metrics', {
        'total': len(vulnerabilities),
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'risk_score': 0,
        'risk_level': 'UNKNOWN'
    })

    return {
        "vulnerabilities": vulnerabilities,
        "risk_metrics": risk_metrics
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
        severity = vuln.get('severity', 'UNKNOWN').upper()
        if severity in analysis['by_severity']:
            analysis['by_severity'][severity] += 1

        tool = vuln.get('tool', 'Unknown')
        analysis['by_tool'][tool] = analysis['by_tool'].get(tool, 0) + 1

        category = vuln.get('category', 'Unknown')
        analysis['by_category'][category] = analysis['by_category'].get(category, 0) + 1

        if severity in ['CRITICAL', 'HIGH']:
            analysis['top_critical'].append({
                'id': vuln.get('id', 'N/A'),
                'title': vuln.get('title', 'No title'),
                'severity': severity,
                'tool': tool,
                'package': vuln.get('package', vuln.get('file', 'N/A')),
                'description': vuln.get('description', '')[:200]
            })

        if vuln.get('package'):
            analysis['packages_to_update'].add(vuln['package'])

        if vuln.get('file'):
            analysis['files_with_issues'].add(vuln['file'])

    analysis['top_critical'] = sorted(
        analysis['top_critical'][:50],
        key=lambda x: 0 if x['severity'] == 'CRITICAL' else 1
    )

    analysis['risk_score'] = (
        analysis['by_severity']['CRITICAL'] * 10 +
        analysis['by_severity']['HIGH'] * 5 +
        analysis['by_severity']['MEDIUM'] * 2 +
        analysis['by_severity']['LOW'] * 1
    )

    if analysis['by_severity']['CRITICAL'] > 0:
        analysis['risk_level'] = "CRITICAL"
    elif analysis['by_severity']['HIGH'] > 10:
        analysis['risk_level'] = "HIGH"
    else:
        analysis['risk_level'] = "MEDIUM"

    return analysis


def markdown_to_html(markdown_text: str) -> str:
    """Convert simple markdown to HTML."""
    html = markdown_text

    # Headers
    html = html.replace('## ', '<h2>').replace('\n#', '</h2>\n<h')

    # Bold
    html = html.replace('**', '<strong>', 1)
    while '**' in html:
        html = html.replace('**', '</strong>', 1)
        if '**' in html:
            html = html.replace('**', '<strong>', 1)

    # Code blocks
    html = html.replace('```bash\n', '<pre><code class="language-bash">')
    html = html.replace('```\n', '</code></pre>')
    html = html.replace('```', '</code></pre>')

    # Lists
    lines = html.split('\n')
    in_list = False
    result = []
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f"<li>{line.strip()[2:]}</li>")
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)

    if in_list:
        result.append('</ul>')

    return '\n'.join(result)


def generate_executive_summary_html(analysis: Dict, remediation_plan: str, build_number: str = "N/A") -> str:
    """Generate executive summary with AI-generated remediation."""

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
        </tr>"""

    remediation_html = markdown_to_html(remediation_plan)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Executive Security Summary — Build #{build_number}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{{font:14px/1.6 system-ui,sans-serif;margin:24px;color:#1f2328;max-width:1200px}}
 h1,h2{{margin:16px 0 8px}} h1{{font-size:24px}} h2{{font-size:18px}}
 .kpi{{display:flex;gap:12px;margin:16px 0;flex-wrap:wrap}}
 .kpi div{{border:1px solid #e0e4e8;border-radius:8px;padding:14px;min-width:150px}}
 .sev{{display:inline-block;border-radius:6px;padding:3px 10px;font-weight:500}}
 .critical{{background:#ffe8e6;color:#a40000}} .high{{background:#fff0d6;color:#8a4b00}}
 .medium{{background:#eef2ff;color:#223076}} .low{{background:#eef7f0;color:#174d1a}}
 table{{width:100%;border-collapse:collapse;margin:12px 0}}
 th,td{{border:1px solid#e6e9ed;padding:10px;text-align:left}}
 th{{background:#f6f8fa;font-weight:600}}
 small{{color:#57606a}}
 .alert{{background:#fff5e6;border-left:4px solid #ff9500;padding:14px;margin:16px 0;border-radius:6px}}
 .ai-badge{{background:#e7f5ff;color:#0969da;padding:2px 8px;border-radius:4px;font-size:12px;margin-left:8px}}
 pre{{background:#f6f8fa;padding:14px;border-radius:6px;overflow-x:auto}}
 code{{background:#f6f8fa;padding:2px 6px;border-radius:4px;font-size:13px}}
 ul{{line-height:1.8}}
</style>
</head>
<body>
<h1>🛡️ Executive Security Summary <small>Build #{build_number} • {datetime.now().strftime('%Y-%m-%d')}</small></h1>

<div class="kpi">
  <div><strong>Total Vulnerabilities</strong><br><span style="font-size:28px">{analysis['total']}</span></div>
  <div><strong>Risk Score</strong><br><span style="font-size:28px;color:#a40000">{analysis['risk_score']}</span></div>
  <div><strong>Severity Breakdown</strong><br>
    <span class="sev critical">Critical: {severity_counts['CRITICAL']}</span>
    <span class="sev high">High: {severity_counts['HIGH']}</span><br>
    <span class="sev medium">Medium: {severity_counts['MEDIUM']}</span>
    <span class="sev low">Low: {severity_counts['LOW']}</span>
  </div>
  <div><strong>Risk Level</strong><br><span class="sev {'critical' if analysis['risk_level'] == 'CRITICAL' else 'high'}">{analysis['risk_level']}</span></div>
</div>

<div class="alert">
  <strong>⚠️ Security Alert:</strong> {severity_counts['CRITICAL']} critical and {severity_counts['HIGH']} high-severity vulnerabilities detected. Immediate action required.
</div>

<h2>Top {len(top_risks)} Critical Risks</h2>
<table>
  <thead><tr><th>Finding</th><th>Source</th><th>Severity</th></tr></thead>
  <tbody>{risk_rows}</tbody>
</table>

<h2>🤖 AI-Generated Remediation Plan <span class="ai-badge">Generated by DeepSeek R1</span></h2>
<div style="border:1px solid #e0e4e8;border-radius:8px;padding:16px;background:#fafbfc">
{remediation_html}
</div>

<h2>📋 Next Steps</h2>
<ol style="line-height:1.8">
  <li>Review remediation plan with security and DevOps teams</li>
  <li>Assign owners for critical and high-severity fixes</li>
  <li>Track remediation progress in project management tool</li>
  <li>Re-scan after fixes to verify remediation</li>
  <li>Update security runbooks and documentation</li>
</ol>

<hr style="margin:24px 0;border:none;border-top:1px solid #e0e4e8">
<p style="color:#57606a;font-size:13px">
  <strong>Standards Alignment:</strong> ISO 27001 A.12.6.1 • NIST SSDF PW.7 • OWASP ASVS 14.2 • PCI-DSS 6.2<br>
  <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} by AI-Powered Security Pipeline
</p>

</body>
</html>"""

    return html


def generate_technical_playbook_html(analysis: Dict, playbook_content: str, build_number: str = "N/A") -> str:
    """Generate technical playbook with AI-generated content."""

    playbook_html = markdown_to_html(playbook_content)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Technical Remediation Playbook — Build #{build_number}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{{font:14px/1.6 system-ui,sans-serif;margin:24px;color:#1f2328;max-width:1200px}}
 h1,h2{{margin:16px 0 8px}} h1{{font-size:22px}} h2{{font-size:18px}}
 .block{{border:1px solid #e0e4e8;border-radius:8px;padding:16px;margin:16px 0;background:#fafbfc}}
 code{{background:#f6f8fa;padding:3px 8px;border-radius:4px;font-size:13px;font-family:monospace}}
 pre{{background:#f6f8fa;padding:16px;border-radius:6px;overflow-x:auto;border:1px solid #e0e4e8}}
 pre code{{background:none;padding:0}}
 .sev{{padding:3px 10px;border-radius:6px;font-weight:500}}
 .critical{{background:#ffe8e6;color:#a40000}} .high{{background:#fff0d6;color:#8a4b00}}
 ul,ol{{line-height:1.8}}
 .ai-badge{{background:#e7f5ff;color:#0969da;padding:2px 8px;border-radius:4px;font-size:12px;margin-left:8px}}
 table{{width:100%;border-collapse:collapse;margin:12px 0}}
 th,td{{border:1px solid #e6e9ed;padding:10px;text-align:left}}
 th{{background:#f6f8fa}}
</style>
</head>
<body>
<h1>⚙️ Technical Remediation Playbook <small>Build #{build_number}</small></h1>

<div class="block">
  <strong>📊 Vulnerability Summary</strong>
  <ul>
    <li>Total Vulnerabilities: {analysis['total']}</li>
    <li>Risk Level: <span class="sev {'critical' if analysis['risk_level'] == 'CRITICAL' else 'high'}">{analysis['risk_level']}</span></li>
    <li>Critical: {analysis['by_severity']['CRITICAL']} • High: {analysis['by_severity']['HIGH']} • Medium: {analysis['by_severity']['MEDIUM']}</li>
  </ul>
</div>

<h2>🤖 AI-Generated Technical Playbook <span class="ai-badge">Generated by LLaMA 3.3 70B</span></h2>
<div style="border:1px solid #e0e4e8;border-radius:8px;padding:16px">
{playbook_html}
</div>

<hr style="margin:24px 0;border:none;border-top:1px solid #e0e4e8">
<p style="color:#57606a;font-size:13px">
  <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} by AI-Powered DevSecOps Pipeline<br>
  <strong>Models Used:</strong> DeepSeek R1 (remediation strategy) + LLaMA 3.3 70B (technical playbook)
</p>

</body>
</html>"""

    return html


def generate_detailed_findings_html(vulnerabilities: List[Dict], analysis: Dict, build_number: str = "N/A") -> str:
    """Generate detailed findings report."""

    vuln_rows = ""
    for v in vulnerabilities[:100]:  # Top 100
        sev_class = v.get('severity', 'unknown').lower()
        vuln_rows += f"""
        <tr>
            <td><span class="sev {sev_class}">{v.get('severity', 'N/A')}</span></td>
            <td><strong>{v.get('id', 'N/A')}</strong><br>{v.get('title', 'No title')[:80]}</td>
            <td>{v.get('tool', 'N/A')}</td>
            <td><code>{v.get('package', v.get('file', 'N/A'))[:40]}</code></td>
            <td><small>{v.get('description', '')[:100]}...</small></td>
        </tr>"""

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Detailed Findings — Build #{build_number}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{{font:13px system-ui,sans-serif;margin:20px;color:#1f2328}}
 h1{{font-size:20px;margin:0 0 16px}}
 .sev{{display:inline-block;padding:3px 8px;border-radius:4px;font-weight:500;font-size:11px}}
 .critical{{background:#ffe8e6;color:#a40000}} .high{{background:#fff0d6;color:#8a4b00}}
 .medium{{background:#eef2ff;color:#223076}} .low{{background:#eef7f0;color:#174d1a}}
 table{{width:100%;border-collapse:collapse;font-size:12px}}
 th,td{{border:1px solid #e6e9ed;padding:8px;text-align:left;vertical-align:top}}
 th{{background:#f6f8fa;position:sticky;top:0}}
 code{{background:#f6f8fa;padding:2px 6px;border-radius:3px;font-size:11px}}
 small{{color:#57606a}}
</style>
</head>
<body>
<h1>📋 Detailed Findings Report <small>Build #{build_number} • {datetime.now().strftime('%Y-%m-%d')}</small></h1>

<p><strong>Total Findings:</strong> {len(vulnerabilities)} • <strong>Showing:</strong> Top 100</p>

<table>
  <thead>
    <tr>
      <th>Severity</th>
      <th>Finding</th>
      <th>Tool</th>
      <th>Location</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    {vuln_rows}
  </tbody>
</table>

</body>
</html>"""

    return html


def main():
    """Main execution."""
    print("="*70)
    print("🤖 AI-POWERED SECURITY REPORT GENERATOR (Enhanced)")
    print("="*70)

    # Get API key
    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    if not api_key or len(api_key) < 10:
        print("❌ Error: OPENROUTER_API_KEY required for AI-generated content")
        print("   Falling back to static reports...")
        api_key = None

    # Load vulnerability data
    print("\n📂 Loading vulnerability data...")
    data = load_vulnerability_data()
    vulnerabilities = data['vulnerabilities']
    risk_metrics = data['risk_metrics']

    print(f"   ✅ Loaded {len(vulnerabilities)} vulnerabilities")
    print(f"   Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}")
    print(f"   Critical: {risk_metrics.get('critical', 0)}, High: {risk_metrics.get('high', 0)}")

    # Analyze vulnerabilities
    print("\n📊 Analyzing vulnerabilities...")
    analysis = analyze_vulnerabilities(vulnerabilities)

    # Generate AI-powered content if API key available
    remediation_plan = ""
    technical_playbook = ""

    if api_key and len(vulnerabilities) > 0:
        print("\n🤖 Generating AI-powered remediation content...")
        llm_generator = LLMReportGenerator(api_key)

        # Generate remediation plan with DeepSeek
        remediation_plan = llm_generator.generate_remediation_plan(vulnerabilities, "deepseek")

        # Generate technical playbook with LLaMA
        technical_playbook = llm_generator.generate_technical_playbook(vulnerabilities, analysis, "llama")
    else:
        print("\n⚠️ Skipping AI generation (no API key or no vulnerabilities)")
        remediation_plan = "No API key configured. Using fallback remediation plan."
        technical_playbook = "No API key configured. Using fallback playbook."

    # Generate HTML reports
    print("\n📄 Generating HTML reports...")
    output_dir = Path("ai-reports")
    output_dir.mkdir(exist_ok=True)

    build_number = os.environ.get('BUILD_NUMBER', 'N/A')

    # Executive Summary
    exec_html = generate_executive_summary_html(analysis, remediation_plan, build_number)
    with open(output_dir / "01_Executive_Security_Summary.html", 'w') as f:
        f.write(exec_html)
    print("   ✅ 01_Executive_Security_Summary.html")

    # Technical Playbook
    playbook_html = generate_technical_playbook_html(analysis, technical_playbook, build_number)
    with open(output_dir / "02_Technical_Playbook.html", 'w') as f:
        f.write(playbook_html)
    print("   ✅ 02_Technical_Playbook.html")

    # Detailed Findings
    findings_html = generate_detailed_findings_html(vulnerabilities, analysis, build_number)
    with open(output_dir / "03_Detailed_Findings.html", 'w') as f:
        f.write(findings_html)
    print("   ✅ 03_Detailed_Findings.html")

    # Save analysis JSON
    analysis_data = {
        "generated_at": datetime.now().isoformat(),
        "build_number": build_number,
        "total_vulnerabilities": len(vulnerabilities),
        "risk_metrics": risk_metrics,
        "analysis": {
            "by_severity": analysis['by_severity'],
            "by_tool": analysis['by_tool'],
            "by_category": analysis['by_category'],
            "risk_score": analysis['risk_score'],
            "risk_level": analysis['risk_level']
        },
        "ai_generated": api_key is not None
    }

    with open(output_dir / "analysis.json", 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print("   ✅ analysis.json")

    print("\n" + "="*70)
    print("✅ REPORT GENERATION COMPLETE")
    print("="*70)
    print(f"📁 Reports saved to: {output_dir.absolute()}")
    print(f"🎯 Summary:")
    print(f"   • Total Vulnerabilities: {len(vulnerabilities)}")
    print(f"   • Critical: {analysis['by_severity']['CRITICAL']}")
    print(f"   • High: {analysis['by_severity']['HIGH']}")
    print(f"   • Risk Level: {analysis['risk_level']}")
    print(f"   • AI-Generated Content: {'Yes' if api_key else 'No'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
