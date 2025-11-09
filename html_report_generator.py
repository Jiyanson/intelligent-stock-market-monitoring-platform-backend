#!/usr/bin/env python3
"""
HTML Report Generator for Security Vulnerability Analysis
Creates professional, printable HTML reports with AI-generated insights
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class HTMLReportGenerator:
    """Generates comprehensive HTML security reports."""

    def __init__(self):
        self.report_css = self._get_css_styles()

    def _get_css_styles(self) -> str:
        """Return CSS styles for professional reports."""
        return """
        <style>
            @page {
                size: A4;
                margin: 2cm;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }

            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            .header .subtitle {
                font-size: 1.2em;
                opacity: 0.9;
            }

            .header .metadata {
                margin-top: 20px;
                font-size: 0.9em;
                opacity: 0.8;
            }

            .section {
                padding: 30px 40px;
                border-bottom: 1px solid #e0e0e0;
            }

            .section:last-child {
                border-bottom: none;
            }

            .section h2 {
                color: #667eea;
                font-size: 1.8em;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
            }

            .section h3 {
                color: #764ba2;
                font-size: 1.4em;
                margin: 20px 0 10px 0;
            }

            .section h4 {
                color: #555;
                font-size: 1.1em;
                margin: 15px 0 8px 0;
            }

            .risk-summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .risk-card {
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            .risk-card.critical {
                background: #fee;
                border-left: 4px solid #dc3545;
            }

            .risk-card.high {
                background: #fff3e0;
                border-left: 4px solid #ff9800;
            }

            .risk-card.medium {
                background: #fff8e1;
                border-left: 4px solid #ffc107;
            }

            .risk-card.low {
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
            }

            .risk-card .count {
                font-size: 3em;
                font-weight: bold;
                margin: 10px 0;
            }

            .risk-card .label {
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .vulnerability-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 0.9em;
            }

            .vulnerability-table th {
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }

            .vulnerability-table td {
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
            }

            .vulnerability-table tr:hover {
                background: #f5f5f5;
            }

            .severity-badge {
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: bold;
                text-transform: uppercase;
                display: inline-block;
            }

            .severity-critical {
                background: #dc3545;
                color: white;
            }

            .severity-high {
                background: #ff9800;
                color: white;
            }

            .severity-medium {
                background: #ffc107;
                color: #333;
            }

            .severity-low {
                background: #4caf50;
                color: white;
            }

            .severity-info {
                background: #2196f3;
                color: white;
            }

            .executive-summary {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }

            .executive-summary p {
                margin: 10px 0;
                text-align: justify;
            }

            .chart-container {
                margin: 30px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
            }

            .progress-bar {
                height: 30px;
                background: #e0e0e0;
                border-radius: 15px;
                overflow: hidden;
                margin: 10px 0;
            }

            .progress-fill {
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 0.85em;
            }

            .tool-summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }

            .tool-card {
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }

            .tool-card h4 {
                color: #667eea;
                margin: 0 0 10px 0;
            }

            .compliance-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }

            .compliance-card {
                padding: 20px;
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }

            .compliance-card h4 {
                color: #667eea;
                margin-bottom: 15px;
            }

            .remediation-section {
                margin: 20px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
            }

            .priority-high {
                border-left: 4px solid #dc3545;
            }

            .priority-medium {
                border-left: 4px solid #ffc107;
            }

            .priority-low {
                border-left: 4px solid #4caf50;
            }

            .code-block {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                margin: 10px 0;
            }

            .footer {
                background: #333;
                color: white;
                padding: 20px 40px;
                text-align: center;
                font-size: 0.9em;
            }

            .footer a {
                color: #667eea;
                text-decoration: none;
            }

            .ai-badge {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 0.85em;
                margin-left: 10px;
            }

            ul, ol {
                margin: 10px 0 10px 30px;
            }

            li {
                margin: 5px 0;
            }

            @media print {
                body {
                    background: white;
                    padding: 0;
                }

                .container {
                    box-shadow: none;
                }

                .section {
                    page-break-inside: avoid;
                }

                .vulnerability-table {
                    font-size: 0.8em;
                }
            }
        </style>
        """

    def generate_severity_badge(self, severity: str) -> str:
        """Generate HTML for severity badge."""
        severity_clean = severity.upper()
        return f'<span class="severity-badge severity-{severity.lower()}">{severity_clean}</span>'

    def generate_risk_summary_cards(self, risk_metrics: Dict[str, Any]) -> str:
        """Generate risk summary cards HTML."""
        cards_html = '<div class="risk-summary">'

        cards = [
            ("critical", "Critical", risk_metrics.get('critical', 0)),
            ("high", "High", risk_metrics.get('high', 0)),
            ("medium", "Medium", risk_metrics.get('medium', 0)),
            ("low", "Low", risk_metrics.get('low', 0))
        ]

        for level, label, count in cards:
            cards_html += f'''
            <div class="risk-card {level}">
                <div class="label">{label}</div>
                <div class="count">{count}</div>
            </div>
            '''

        cards_html += '</div>'
        return cards_html

    def generate_vulnerability_table(self, vulnerabilities: List[Dict[str, Any]], limit: int = 20) -> str:
        """Generate vulnerability table HTML."""
        if not vulnerabilities:
            return '<p>No vulnerabilities found.</p>'

        table_html = '''
        <table class="vulnerability-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Severity</th>
                    <th>Tool</th>
                    <th>Category</th>
                    <th>Location</th>
                </tr>
            </thead>
            <tbody>
        '''

        for vuln in vulnerabilities[:limit]:
            location = vuln.get('file', vuln.get('package', vuln.get('url', 'N/A')))
            if len(location) > 50:
                location = '...' + location[-47:]

            table_html += f'''
            <tr>
                <td><code>{vuln.get('id', 'N/A')}</code></td>
                <td>{vuln.get('title', 'No title')}</td>
                <td>{self.generate_severity_badge(vuln.get('severity', 'MEDIUM'))}</td>
                <td>{vuln.get('tool', 'Unknown')}</td>
                <td>{vuln.get('category', 'N/A')}</td>
                <td><small>{location}</small></td>
            </tr>
            '''

        table_html += '</tbody></table>'
        return table_html

    def generate_tool_summary(self, tool_summary: Dict[str, Any]) -> str:
        """Generate tool summary cards."""
        html = '<div class="tool-summary">'

        for tool_name, tool_data in tool_summary.items():
            count = tool_data.get('count', 0)
            status = tool_data.get('status', 'completed')

            html += f'''
            <div class="tool-card">
                <h4>{tool_name.upper()}</h4>
                <p><strong>Findings:</strong> {count}</p>
                <p><strong>Status:</strong> {status}</p>
            </div>
            '''

        html += '</div>'
        return html

    def generate_compliance_section(self, compliance_mapping: Dict[str, Any]) -> str:
        """Generate compliance mapping section."""
        html = '<div class="compliance-grid">'

        frameworks = {
            "ISO_27001": "ISO/IEC 27001",
            "PCI_DSS": "PCI-DSS",
            "OWASP_Top_10": "OWASP Top 10",
            "CWE_Top_25": "CWE/SANS Top 25",
            "NIST_CSF": "NIST Cybersecurity Framework"
        }

        for key, name in frameworks.items():
            data = compliance_mapping.get(key, {})
            count = data.get('count', 0)
            vuln_ids = data.get('vulnerability_ids', [])

            html += f'''
            <div class="compliance-card">
                <h4>{name}</h4>
                <p><strong>Affected Controls:</strong> {count}</p>
                <p><strong>Sample IDs:</strong></p>
                <ul>
            '''

            for vid in vuln_ids[:5]:
                html += f'<li><code>{vid}</code></li>'

            html += '</ul></div>'

        html += '</div>'
        return html

    def generate_full_report(
        self,
        vulnerability_data: Dict[str, Any],
        ai_insights: Dict[str, Any]
    ) -> str:
        """Generate complete HTML report."""
        metadata = vulnerability_data.get('metadata', {})
        risk_metrics = vulnerability_data.get('risk_metrics', {})
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])
        tool_summary = vulnerability_data.get('tool_summary', {})
        compliance_mapping = vulnerability_data.get('compliance_mapping', {})

        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Vulnerability Assessment Report</title>
    {self.report_css}
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🛡️ Security Vulnerability Assessment Report</h1>
            <div class="subtitle">Comprehensive DevSecOps Security Analysis</div>
            <div class="metadata">
                Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}<br>
                Scan Date: {metadata.get('scan_date', 'N/A')}<br>
                Pipeline Version: {metadata.get('pipeline_version', '1.0.0')}
                <span class="ai-badge">🤖 AI-Enhanced</span>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="executive-summary">
                {self._format_text_content(ai_insights.get('executive_summary', 'No executive summary available.'))}
            </div>

            <h3>Overall Security Posture</h3>
            {self.generate_risk_summary_cards(risk_metrics)}

            <div style="margin: 20px 0;">
                <h4>Risk Score: {risk_metrics.get('risk_score', 0)} / 100</h4>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(risk_metrics.get('risk_score', 0), 100)}%; background: {self._get_risk_color(risk_metrics.get('risk_level', 'LOW'))};">
                        {risk_metrics.get('risk_level', 'UNKNOWN')}
                    </div>
                </div>
            </div>
        </div>

        <!-- Tools Summary -->
        <div class="section">
            <h2>🔧 Security Tools Utilized</h2>
            <p>Total Tools: {metadata.get('total_tools', 0)} | Processed: {metadata.get('processed_tools', 0)}</p>
            {self.generate_tool_summary(tool_summary)}
        </div>

        <!-- Vulnerability Details -->
        <div class="section">
            <h2>🔍 Vulnerability Details</h2>
            <h3>Top {min(20, len(vulnerabilities))} Critical Findings</h3>
            {self.generate_vulnerability_table(vulnerabilities, limit=20)}

            <h3>Vulnerability Distribution by Category</h3>
            {self._generate_category_distribution(vulnerabilities)}
        </div>

        <!-- AI-Generated Remediation Policy -->
        <div class="section">
            <h2>📋 Remediation Policy <span class="ai-badge">AI-Generated</span></h2>
            <div class="executive-summary">
                {self._format_text_content(ai_insights.get('remediation_policy', 'No remediation policy available.'))}
            </div>
        </div>

        <!-- Technical Playbook -->
        <div class="section">
            <h2>🛠️ Technical Remediation Playbook <span class="ai-badge">AI-Generated</span></h2>
            <div class="executive-summary">
                {self._format_text_content(ai_insights.get('technical_playbook', 'No technical playbook available.'))}
            </div>
        </div>

        <!-- Risk Assessment -->
        <div class="section">
            <h2>⚠️ Risk Assessment <span class="ai-badge">AI-Generated</span></h2>
            <div class="executive-summary">
                <h3>Business Impact: {ai_insights.get('risk_assessment', {}).get('business_impact', 'UNKNOWN')}</h3>
                {self._format_text_content(ai_insights.get('risk_assessment', {}).get('analysis', 'No risk assessment available.'))}
            </div>
        </div>

        <!-- Compliance Mapping -->
        <div class="section">
            <h2>✅ Compliance & Standards Mapping</h2>
            {self.generate_compliance_section(compliance_mapping)}

            <h3>Detailed Compliance Analysis <span class="ai-badge">AI-Generated</span></h3>
            <div class="executive-summary">
                {self._format_text_content(ai_insights.get('compliance_mapping', 'No compliance mapping available.'))}
            </div>
        </div>

        <!-- Recommendations -->
        <div class="section">
            <h2>💡 Key Recommendations</h2>
            {self._generate_recommendations(risk_metrics, vulnerabilities)}
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Generated by Intelligent Stock Market Monitoring Platform - DevSecOps Pipeline</p>
            <p>Powered by DeepSeek R1 & Llama AI Models via HuggingFace</p>
            <p>© {datetime.now().year} | <a href="https://github.com/Jiyanson/intelligent-stock-market-monitoring-platform-backend">GitHub Repository</a></p>
        </div>
    </div>
</body>
</html>
        '''

        return html

    def _format_text_content(self, text: str) -> str:
        """Format plain text content for HTML display."""
        if not text:
            return '<p>No content available.</p>'

        # Convert markdown-style headers to HTML
        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Headers
            if line.startswith('###'):
                formatted_lines.append(f'<h4>{line[3:].strip()}</h4>')
            elif line.startswith('##'):
                formatted_lines.append(f'<h3>{line[2:].strip()}</h3>')
            elif line.startswith('#'):
                formatted_lines.append(f'<h3>{line[1:].strip()}</h3>')
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                formatted_lines.append(f'<li>{line[2:].strip()}</li>')
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                formatted_lines.append(f'<li>{line[2:].strip()}</li>')
            # Code blocks
            elif line.startswith('```'):
                continue
            # Regular paragraphs
            else:
                formatted_lines.append(f'<p>{line}</p>')

        return '\n'.join(formatted_lines)

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color based on risk level."""
        colors = {
            "CRITICAL": "#dc3545",
            "HIGH": "#ff9800",
            "MEDIUM-HIGH": "#ff9800",
            "MEDIUM": "#ffc107",
            "LOW": "#4caf50"
        }
        return colors.get(risk_level.upper(), "#2196f3")

    def _generate_category_distribution(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Generate category distribution visualization."""
        categories = {}
        for vuln in vulnerabilities:
            cat = vuln.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + 1

        html = '<div class="chart-container">'
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(vulnerabilities)) * 100 if vulnerabilities else 0
            html += f'''
            <h4>{category}: {count} ({percentage:.1f}%)</h4>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {percentage}%; background: #667eea;">
                    {count}
                </div>
            </div>
            '''

        html += '</div>'
        return html

    def _generate_recommendations(self, risk_metrics: Dict[str, Any], vulnerabilities: List[Dict[str, Any]]) -> str:
        """Generate key recommendations."""
        recommendations = []

        if risk_metrics.get('critical', 0) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Address Critical Vulnerabilities Immediately',
                'description': f"Found {risk_metrics.get('critical')} critical vulnerabilities that require immediate attention within 24-48 hours."
            })

        if any(v.get('category') == 'Secrets' for v in vulnerabilities):
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Rotate Exposed Credentials',
                'description': 'Secrets have been detected in the codebase. Rotate all exposed credentials and implement secrets management.'
            })

        if any(v.get('category') == 'SCA' for v in vulnerabilities):
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Update Vulnerable Dependencies',
                'description': 'Multiple vulnerable dependencies detected. Implement automated dependency scanning and update processes.'
            })

        if any(v.get('category') == 'DAST' for v in vulnerabilities):
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Strengthen Web Application Security',
                'description': 'Web application vulnerabilities detected. Implement WAF, input validation, and security headers.'
            })

        recommendations.append({
            'priority': 'LOW',
            'title': 'Continuous Security Monitoring',
            'description': 'Implement continuous security monitoring and automated remediation workflows.'
        })

        html = ''
        for rec in recommendations:
            html += f'''
            <div class="remediation-section priority-{rec['priority'].lower()}">
                <h3>🎯 {rec['title']}</h3>
                <p><strong>Priority:</strong> {rec['priority']}</p>
                <p>{rec['description']}</p>
            </div>
            '''

        return html

    def save_report(self, html_content: str, output_path: str):
        """Save HTML report to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Report saved to: {output_file}")


if __name__ == "__main__":
    # Test HTML report generation
    generator = HTMLReportGenerator()

    sample_data = {
        "metadata": {
            "scan_date": datetime.utcnow().isoformat(),
            "total_tools": 5,
            "processed_tools": 5
        },
        "risk_metrics": {
            "total": 25,
            "critical": 3,
            "high": 8,
            "medium": 10,
            "low": 4,
            "risk_score": 76,
            "risk_level": "HIGH"
        },
        "vulnerabilities": [],
        "tool_summary": {},
        "compliance_mapping": {}
    }

    sample_insights = {
        "executive_summary": "Sample executive summary...",
        "remediation_policy": "Sample remediation policy...",
        "technical_playbook": "Sample playbook...",
        "risk_assessment": {"business_impact": "HIGH", "analysis": "Sample analysis..."},
        "compliance_mapping": "Sample compliance..."
    }

    html = generator.generate_full_report(sample_data, sample_insights)
    generator.save_report(html, "/tmp/test_report.html")
    print("Test report generated!")
