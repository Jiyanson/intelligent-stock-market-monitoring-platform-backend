#!/usr/bin/env python3
"""
Main Orchestration Script for AI-Powered Security Vulnerability Analysis
Integrates: Normalization -> LLM Analysis -> HTML Report Generation

This script:
1. Loads normalized vulnerability data
2. Generates AI-powered security insights using DeepSeek R1 and Llama
3. Creates comprehensive HTML reports for technical teams and leadership
4. Saves artifacts to ai-policies directory
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from llm_integration import SecurityAnalysisLLM
from html_report_generator import HTMLReportGenerator


class SecurityReportOrchestrator:
    """Orchestrates the complete security analysis and reporting workflow."""

    def __init__(
        self,
        hf_token: str,
        normalized_data_path: str = "processed/normalized_vulnerabilities.json",
        output_dir: str = "ai-policies",
        reports_dir: str = "reports"
    ):
        self.hf_token = hf_token
        self.normalized_data_path = Path(normalized_data_path)
        self.output_dir = Path(output_dir)
        self.reports_dir = Path(reports_dir)

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        print("🤖 Initializing AI Security Analysis System...")
        print(f"   Using DeepSeek R1 and Llama models via HuggingFace")

        self.llm = SecurityAnalysisLLM(hf_token, preferred_model="deepseek")
        self.html_generator = HTMLReportGenerator()

        self.vulnerability_data = None
        self.ai_insights = {}

    def load_vulnerability_data(self) -> bool:
        """Load normalized vulnerability data."""
        try:
            if not self.normalized_data_path.exists():
                print(f"❌ Normalized data not found: {self.normalized_data_path}")
                return False

            with open(self.normalized_data_path, 'r') as f:
                self.vulnerability_data = json.load(f)

            total_vulns = self.vulnerability_data.get('risk_metrics', {}).get('total', 0)
            print(f"✅ Loaded {total_vulns} vulnerabilities from normalized data")
            return True

        except Exception as e:
            print(f"❌ Error loading vulnerability data: {e}")
            return False

    def generate_ai_insights(self) -> bool:
        """Generate AI-powered security insights."""
        if not self.vulnerability_data:
            print("❌ No vulnerability data loaded")
            return False

        try:
            print("\n" + "="*70)
            print("🤖 Generating AI-Powered Security Insights")
            print("="*70)

            # 1. Executive Summary
            print("\n📊 Generating Executive Summary (for C-level)...")
            self.ai_insights['executive_summary'] = self.llm.generate_executive_summary(
                self.vulnerability_data
            )
            print("   ✅ Executive summary generated")

            # 2. Remediation Policy
            print("\n📋 Generating Remediation Policy...")
            self.ai_insights['remediation_policy'] = self.llm.generate_remediation_policy(
                self.vulnerability_data
            )
            print("   ✅ Remediation policy generated")

            # 3. Technical Playbook
            print("\n🛠️  Generating Technical Remediation Playbook...")
            self.ai_insights['technical_playbook'] = self.llm.generate_technical_playbook(
                self.vulnerability_data
            )
            print("   ✅ Technical playbook generated")

            # 4. Risk Assessment
            print("\n⚠️  Performing Risk Assessment...")
            self.ai_insights['risk_assessment'] = self.llm.generate_risk_assessment(
                self.vulnerability_data
            )
            print("   ✅ Risk assessment completed")

            # 5. Compliance Mapping
            print("\n✅ Generating Compliance Traceability Mapping...")
            self.ai_insights['compliance_mapping'] = self.llm.generate_compliance_mapping(
                self.vulnerability_data
            )
            print("   ✅ Compliance mapping generated")

            print("\n" + "="*70)
            print("✅ All AI insights generated successfully")
            print("="*70)

            return True

        except Exception as e:
            print(f"❌ Error generating AI insights: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_ai_insights(self):
        """Save AI insights to JSON file."""
        try:
            # Prepare output data
            output_data = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "llm_model": "DeepSeek R1 & Llama",
                    "pipeline_version": "1.0.0",
                    "vulnerability_count": self.vulnerability_data.get('risk_metrics', {}).get('total', 0),
                    "risk_level": self.vulnerability_data.get('risk_metrics', {}).get('risk_level', 'UNKNOWN')
                },
                "insights": self.ai_insights,
                "vulnerability_summary": self.vulnerability_data.get('risk_metrics', {}),
                "compliance_frameworks": self.vulnerability_data.get('compliance_mapping', {})
            }

            # Save to JSON
            output_file = self.output_dir / "llm_generated_policy.json"
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"\n💾 AI insights saved to: {output_file}")
            return output_file

        except Exception as e:
            print(f"❌ Error saving AI insights: {e}")
            return None

    def generate_html_reports(self):
        """Generate comprehensive HTML reports."""
        try:
            print("\n" + "="*70)
            print("📄 Generating HTML Reports")
            print("="*70)

            # 1. Comprehensive Report (for technical teams & leadership)
            print("\n📊 Creating comprehensive security report...")
            comprehensive_html = self.html_generator.generate_full_report(
                self.vulnerability_data,
                self.ai_insights
            )

            comprehensive_path = self.reports_dir / "comprehensive_security_report.html"
            self.html_generator.save_report(comprehensive_html, str(comprehensive_path))
            print(f"   ✅ Comprehensive report: {comprehensive_path}")

            # 2. Executive Summary Report (simplified for leadership)
            print("\n📈 Creating executive summary report...")
            executive_html = self._generate_executive_report()
            executive_path = self.reports_dir / "executive_summary_report.html"
            self.html_generator.save_report(executive_html, str(executive_path))
            print(f"   ✅ Executive report: {executive_path}")

            # 3. Technical Playbook Report (for DevOps/Security teams)
            print("\n🔧 Creating technical playbook report...")
            technical_html = self._generate_technical_report()
            technical_path = self.reports_dir / "technical_playbook_report.html"
            self.html_generator.save_report(technical_html, str(technical_path))
            print(f"   ✅ Technical playbook: {technical_path}")

            print("\n" + "="*70)
            print("✅ All HTML reports generated successfully")
            print("="*70)

            return {
                'comprehensive': comprehensive_path,
                'executive': executive_path,
                'technical': technical_path
            }

        except Exception as e:
            print(f"❌ Error generating HTML reports: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_executive_report(self) -> str:
        """Generate simplified executive report."""
        risk_metrics = self.vulnerability_data.get('risk_metrics', {})
        exec_summary = self.ai_insights.get('executive_summary', 'Not available')
        risk_assessment = self.ai_insights.get('risk_assessment', {})

        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Security Summary</title>
    {self.html_generator.report_css}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Executive Security Summary</h1>
            <div class="subtitle">Leadership Briefing - Security Posture Assessment</div>
            <div class="metadata">
                Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
                <span class="ai-badge">🤖 AI-Enhanced</span>
            </div>
        </div>

        <div class="section">
            <h2>📊 Security Posture at a Glance</h2>
            {self.html_generator.generate_risk_summary_cards(risk_metrics)}

            <div style="margin: 20px 0;">
                <h3>Overall Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}</h3>
                <h3>Business Impact: {risk_assessment.get('business_impact', 'UNKNOWN')}</h3>
            </div>
        </div>

        <div class="section">
            <h2>📋 Executive Summary</h2>
            <div class="executive-summary">
                {self.html_generator._format_text_content(exec_summary)}
            </div>
        </div>

        <div class="section">
            <h2>⚠️ Business Risk Assessment</h2>
            <div class="executive-summary">
                {self.html_generator._format_text_content(risk_assessment.get('analysis', 'Not available'))}
            </div>
        </div>

        <div class="section">
            <h2>💡 Immediate Action Items</h2>
            {self.html_generator._generate_recommendations(risk_metrics, self.vulnerability_data.get('vulnerabilities', []))}
        </div>

        <div class="footer">
            <p>For detailed technical information, please refer to the Comprehensive Security Report</p>
            <p>© {datetime.now().year} | Intelligent Stock Market Monitoring Platform</p>
        </div>
    </div>
</body>
</html>
        '''
        return html

    def _generate_technical_report(self) -> str:
        """Generate technical playbook report."""
        playbook = self.ai_insights.get('technical_playbook', 'Not available')
        remediation = self.ai_insights.get('remediation_policy', 'Not available')
        vulnerabilities = self.vulnerability_data.get('vulnerabilities', [])

        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Technical Remediation Playbook</title>
    {self.html_generator.report_css}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ Technical Remediation Playbook</h1>
            <div class="subtitle">DevOps & Security Team Action Guide</div>
            <div class="metadata">
                Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
                <span class="ai-badge">🤖 AI-Enhanced</span>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Remediation Strategy</h2>
            <div class="executive-summary">
                {self.html_generator._format_text_content(remediation)}
            </div>
        </div>

        <div class="section">
            <h2>🔧 Technical Implementation Guide</h2>
            <div class="executive-summary">
                {self.html_generator._format_text_content(playbook)}
            </div>
        </div>

        <div class="section">
            <h2>📋 Detailed Vulnerability List</h2>
            {self.html_generator.generate_vulnerability_table(vulnerabilities, limit=50)}
        </div>

        <div class="section">
            <h2>✅ Compliance Mapping</h2>
            <div class="executive-summary">
                {self.html_generator._format_text_content(self.ai_insights.get('compliance_mapping', 'Not available'))}
            </div>
        </div>

        <div class="footer">
            <p>For executive summary, please refer to the Executive Security Summary Report</p>
            <p>© {datetime.now().year} | Intelligent Stock Market Monitoring Platform</p>
        </div>
    </div>
</body>
</html>
        '''
        return html

    def run_complete_analysis(self):
        """Run the complete security analysis workflow."""
        print("\n" + "="*70)
        print("🚀 Starting AI-Powered Security Vulnerability Analysis")
        print("="*70)

        # Step 1: Load data
        print("\n📂 Step 1: Loading normalized vulnerability data...")
        if not self.load_vulnerability_data():
            print("❌ Failed to load vulnerability data. Exiting.")
            return False

        # Step 2: Generate AI insights
        print("\n🤖 Step 2: Generating AI-powered security insights...")
        if not self.generate_ai_insights():
            print("⚠️  Warning: AI insights generation failed. Continuing with available data...")

        # Step 3: Save AI insights
        print("\n💾 Step 3: Saving AI insights...")
        self.save_ai_insights()

        # Step 4: Generate HTML reports
        print("\n📄 Step 4: Generating HTML reports...")
        reports = self.generate_html_reports()

        # Summary
        print("\n" + "="*70)
        print("✅ SECURITY ANALYSIS COMPLETE")
        print("="*70)

        if reports:
            print("\n📊 Generated Reports:")
            for report_type, path in reports.items():
                print(f"   • {report_type.capitalize()}: {path}")

        print(f"\n📁 All artifacts saved to:")
        print(f"   • AI Policies: {self.output_dir}")
        print(f"   • HTML Reports: {self.reports_dir}")

        print("\n" + "="*70)
        print("🎉 Analysis pipeline completed successfully!")
        print("="*70)

        return True


def main():
    """Main entry point for the script."""
    # Get HuggingFace token from environment
    hf_token = os.environ.get('HF_TOKEN')

    if not hf_token:
        print("❌ Error: HF_TOKEN environment variable not set")
        print("   Please set your HuggingFace API token:")
        print("   export HF_TOKEN='your_token_here'")
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = SecurityReportOrchestrator(
        hf_token=hf_token,
        normalized_data_path="processed/normalized_vulnerabilities.json",
        output_dir="ai-policies",
        reports_dir="reports"
    )

    # Run complete analysis
    success = orchestrator.run_complete_analysis()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
