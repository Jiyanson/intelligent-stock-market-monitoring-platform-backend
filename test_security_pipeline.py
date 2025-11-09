#!/usr/bin/env python3
"""
Test script for Security Analysis Pipeline
Validates installation and creates sample reports
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def check_environment():
    """Check if environment is properly configured."""
    print_header("🔍 Checking Environment")

    issues = []

    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version}")
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")

    # Check HuggingFace token
    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        issues.append("HF_TOKEN environment variable not set")
        print("❌ HF_TOKEN not configured")
    else:
        print(f"✅ HF_TOKEN configured (length: {len(hf_token)})")

    # Check required modules
    required_modules = ['json', 'requests', 'pathlib']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ Module '{module}' available")
        except ImportError:
            issues.append(f"Required module '{module}' not found")
            print(f"❌ Module '{module}' missing")

    # Check project files
    required_files = [
        'llm_integration.py',
        'html_report_generator.py',
        'real_llm_integration.py',
        'reports/process_vulnerabilities.py'
    ]
    for file in required_files:
        if Path(file).exists():
            print(f"✅ Found: {file}")
        else:
            issues.append(f"Required file '{file}' not found")
            print(f"❌ Missing: {file}")

    return issues


def create_sample_data():
    """Create sample vulnerability data for testing."""
    print_header("📝 Creating Sample Data")

    # Create directories
    for dir_name in ['reports', 'processed', 'ai-policies']:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

    # Sample vulnerability data
    sample_data = {
        "metadata": {
            "scan_date": datetime.utcnow().isoformat(),
            "total_tools": 5,
            "processed_tools": 5,
            "pipeline_version": "1.0.0"
        },
        "risk_metrics": {
            "total": 25,
            "critical": 3,
            "high": 8,
            "medium": 10,
            "low": 4,
            "info": 0,
            "risk_score": 76,
            "risk_level": "HIGH"
        },
        "tool_summary": {
            "gitleaks": {"count": 2, "file": "gitleaks-report.json"},
            "semgrep": {"count": 8, "file": "semgrep-report.json"},
            "dependency-check": {"count": 10, "file": "dependency-check-report.json"},
            "trivy": {"count": 3, "file": "trivy-report.json"},
            "zap": {"count": 2, "file": "zap-report.json"}
        },
        "vulnerabilities": [
            {
                "id": "CVE-2024-1234",
                "tool": "Trivy",
                "category": "Container Security",
                "type": "OS Package",
                "title": "Critical vulnerability in openssl",
                "description": "OpenSSL has a critical buffer overflow vulnerability",
                "severity": "CRITICAL",
                "severity_score": 10,
                "package": "openssl",
                "installed_version": "1.1.1",
                "fixed_version": "1.1.1w",
                "remediation": "Update openssl to version 1.1.1w or later",
                "cwe": ["CWE-119"],
                "owasp": ["A06:2021-Vulnerable Components"],
                "compliance": ["ISO 27001: A.12.6.1", "PCI-DSS: 6.2"]
            },
            {
                "id": "GITLEAKS-abc123",
                "tool": "Gitleaks",
                "category": "Secrets",
                "type": "Secret Exposure",
                "title": "Hardcoded AWS Access Key",
                "description": "AWS access key found in configuration file",
                "severity": "CRITICAL",
                "severity_score": 10,
                "file": "config/aws.py",
                "line": 15,
                "remediation": "Remove secret from git history and rotate credentials",
                "cwe": ["CWE-798"],
                "owasp": ["A02:2021-Cryptographic Failures"],
                "compliance": ["ISO 27001: A.9.4.3", "PCI-DSS: 6.5.3"]
            },
            {
                "id": "SEMGREP-sql-injection",
                "tool": "Semgrep",
                "category": "SAST",
                "type": "SQL Injection",
                "title": "SQL Injection vulnerability in user query",
                "description": "User input directly used in SQL query without sanitization",
                "severity": "HIGH",
                "severity_score": 8,
                "file": "app/database/queries.py",
                "line": 42,
                "remediation": "Use parameterized queries or ORM",
                "cwe": ["CWE-89"],
                "owasp": ["A03:2021-Injection"],
                "compliance": ["ISO 27001: A.14.2.1", "PCI-DSS: 6.5.1"]
            },
            {
                "id": "ZAP-10035",
                "tool": "OWASP ZAP",
                "category": "DAST",
                "type": "Web Application Vulnerability",
                "title": "Missing Anti-CSRF Tokens",
                "description": "Forms do not include CSRF protection",
                "severity": "MEDIUM",
                "severity_score": 5,
                "url": "http://localhost:8000/api/v1/users",
                "remediation": "Implement CSRF tokens for state-changing operations",
                "cwe": ["CWE-352"],
                "owasp": ["A01:2021-Broken Access Control"],
                "compliance": ["ISO 27001: A.14.2.1", "OWASP Top 10"]
            }
        ],
        "compliance_mapping": {
            "ISO_27001": {
                "count": 4,
                "vulnerability_ids": ["CVE-2024-1234", "GITLEAKS-abc123", "SEMGREP-sql-injection", "ZAP-10035"]
            },
            "PCI_DSS": {
                "count": 3,
                "vulnerability_ids": ["CVE-2024-1234", "GITLEAKS-abc123", "SEMGREP-sql-injection"]
            },
            "OWASP_Top_10": {
                "count": 4,
                "vulnerability_ids": ["GITLEAKS-abc123", "SEMGREP-sql-injection", "ZAP-10035", "CVE-2024-1234"]
            },
            "CWE_Top_25": {
                "count": 4,
                "vulnerability_ids": ["CWE-119", "CWE-798", "CWE-89", "CWE-352"]
            },
            "NIST_CSF": {
                "count": 0,
                "vulnerability_ids": []
            }
        }
    }

    # Save sample data
    output_file = Path("processed/normalized_vulnerabilities.json")
    with open(output_file, 'w') as f:
        json.dump(sample_data, f, indent=2)

    print(f"✅ Created sample data: {output_file}")
    print(f"   Total vulnerabilities: {sample_data['risk_metrics']['total']}")
    print(f"   Risk level: {sample_data['risk_metrics']['risk_level']}")

    return True


def test_llm_integration():
    """Test LLM integration with HuggingFace."""
    print_header("🤖 Testing LLM Integration")

    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        print("⚠️  Skipping LLM test (HF_TOKEN not set)")
        return False

    try:
        from llm_integration import SecurityAnalysisLLM

        print("✅ LLM module imported successfully")

        llm = SecurityAnalysisLLM(hf_token, preferred_model="deepseek")
        print("✅ LLM instance created")

        # Simple test prompt
        test_prompt = "Explain in one sentence what DevSecOps means."
        print(f"\n📝 Test prompt: '{test_prompt}'")
        print("🔄 Generating response (this may take 10-30 seconds)...")

        response = llm.generate(test_prompt, max_length=100, temperature=0.7)

        if response:
            print(f"\n✅ LLM Response received:")
            print(f"   {response[:200]}...")
            return True
        else:
            print("❌ LLM test failed - no response")
            return False

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


def test_html_generation():
    """Test HTML report generation."""
    print_header("📄 Testing HTML Report Generation")

    try:
        from html_report_generator import HTMLReportGenerator

        print("✅ HTML generator module imported")

        # Load sample data
        with open("processed/normalized_vulnerabilities.json", 'r') as f:
            vuln_data = json.load(f)

        print("✅ Sample data loaded")

        # Create sample AI insights
        sample_insights = {
            "executive_summary": "This is a test executive summary generated for validation purposes. "
                               "The system has detected 25 vulnerabilities across 5 security scanning tools. "
                               "Immediate action is required to address 3 critical vulnerabilities.",
            "remediation_policy": "## Immediate Actions\n- Rotate exposed AWS credentials\n- Patch OpenSSL vulnerability\n\n"
                                "## Short-term Actions\n- Fix SQL injection vulnerabilities\n- Implement CSRF protection",
            "technical_playbook": "### Secrets Management\n1. Remove credentials from git history\n2. Implement secrets manager\n\n"
                                "### Dependency Updates\n```bash\napt-get update && apt-get upgrade openssl\n```",
            "risk_assessment": {
                "business_impact": "HIGH",
                "analysis": "The exposed credentials present immediate risk of data breach. "
                          "Recommend 24-hour remediation window."
            },
            "compliance_mapping": "## ISO 27001\n- A.12.6.1: Vulnerability management\n- A.9.4.3: Password management"
        }

        generator = HTMLReportGenerator()
        print("✅ HTML generator initialized")

        # Generate comprehensive report
        html_content = generator.generate_full_report(vuln_data, sample_insights)
        print("✅ HTML report generated")

        # Save test report
        output_file = Path("reports/test_security_report.html")
        generator.save_report(html_content, str(output_file))

        print(f"\n✅ Test report saved: {output_file}")
        print(f"   Report size: {len(html_content)} bytes")
        print(f"   Open in browser: file://{output_file.absolute()}")

        return True

    except Exception as e:
        print(f"❌ HTML generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test execution."""
    print_header("🚀 Security Analysis Pipeline Test Suite")

    results = {
        "environment": False,
        "sample_data": False,
        "llm_integration": False,
        "html_generation": False
    }

    # Test 1: Environment
    issues = check_environment()
    if not issues:
        results["environment"] = True
        print("\n✅ Environment check passed")
    else:
        print(f"\n❌ Environment check failed:")
        for issue in issues:
            print(f"   - {issue}")

    # Test 2: Sample Data
    if create_sample_data():
        results["sample_data"] = True

    # Test 3: LLM Integration (optional)
    if os.environ.get('HF_TOKEN'):
        results["llm_integration"] = test_llm_integration()
    else:
        print_header("⚠️  Skipping LLM Test")
        print("Set HF_TOKEN to test AI integration:")
        print("export HF_TOKEN='your_huggingface_token'")

    # Test 4: HTML Generation
    results["html_generation"] = test_html_generation()

    # Summary
    print_header("📊 Test Summary")

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your pipeline is ready to use.")
        print("\nNext steps:")
        print("1. Set HF_TOKEN if not already set")
        print("2. Run real security scans")
        print("3. Execute: python3 real_llm_integration.py")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
