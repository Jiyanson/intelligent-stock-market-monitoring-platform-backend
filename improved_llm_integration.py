#!/usr/bin/env python3
"""
IMPROVED LLM Integration Module for Security Analysis
Fixes the vulnerability counting and LLM prompt generation issues

Key improvements:
1. Processes ALL vulnerabilities, not just first 10-15
2. Generates detailed statistics by package, severity, and CVE
3. Includes specific HIGH/CRITICAL vulnerabilities with package names
4. Properly handles large datasets (e.g., 705 vulnerabilities)
5. Adds comprehensive error handling
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import requests


class LLMProvider:
    """Base class for LLM providers."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api-inference.huggingface.co/models/"

    def query(self, model_id: str, payload: Dict[str, Any], max_retries: int = 3) -> Optional[str]:
        """Query the HuggingFace Inference API."""
        headers = {"Authorization": f"Bearer {self.api_token}"}
        url = f"{self.base_url}{model_id}"

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=120)

                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', '')
                    elif isinstance(result, dict):
                        return result.get('generated_text', '')
                    return str(result)

                elif response.status_code == 503:
                    wait_time = min(20 * (attempt + 1), 60)
                    print(f"Model loading... waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue

                else:
                    print(f"Error: HTTP {response.status_code} - {response.text}")
                    return None

            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)

        return None


class DeepSeekR1:
    """DeepSeek R1 model integration."""

    def __init__(self, api_token: str):
        self.provider = LLMProvider(api_token)
        self.model_id = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"

    def generate(self, prompt: str, max_length: int = 2000, temperature: float = 0.7) -> Optional[str]:
        """Generate response from DeepSeek R1."""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": temperature,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False
            }
        }
        return self.provider.query(self.model_id, payload)


class LlamaModel:
    """Llama model integration."""

    def __init__(self, api_token: str, model_variant: str = "meta-llama/Llama-3.2-3B-Instruct"):
        self.provider = LLMProvider(api_token)
        self.model_id = model_variant

    def generate(self, prompt: str, max_length: int = 2000, temperature: float = 0.7) -> Optional[str]:
        """Generate response from Llama."""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": temperature,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False
            }
        }
        return self.provider.query(self.model_id, payload)


class VulnerabilityAnalyzer:
    """Analyzes and categorizes vulnerability data for LLM prompts."""

    @staticmethod
    def analyze_vulnerabilities(vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive analysis of all vulnerabilities.
        Returns detailed statistics for LLM prompt generation.
        """
        if not vulnerabilities:
            return {
                "total_count": 0,
                "by_severity": {},
                "by_tool": {},
                "by_package": {},
                "by_category": {},
                "critical_high_details": [],
                "package_summary": {}
            }

        # Count by severity
        by_severity = Counter(v.get('severity', 'UNKNOWN').upper() for v in vulnerabilities)

        # Count by tool
        by_tool = Counter(v.get('tool', 'Unknown') for v in vulnerabilities)

        # Count by category
        by_category = Counter(v.get('category', 'Unknown') for v in vulnerabilities)

        # Detailed package analysis
        package_vulns = defaultdict(lambda: {'count': 0, 'critical': 0, 'high': 0, 'cves': []})
        for v in vulnerabilities:
            pkg = v.get('package', v.get('file', 'Unknown'))
            severity = v.get('severity', 'MEDIUM').upper()
            package_vulns[pkg]['count'] += 1
            if severity == 'CRITICAL':
                package_vulns[pkg]['critical'] += 1
            elif severity == 'HIGH':
                package_vulns[pkg]['high'] += 1
            if v.get('id', '').startswith('CVE'):
                package_vulns[pkg]['cves'].append(v.get('id'))

        # Sort packages by severity (critical + high count)
        sorted_packages = sorted(
            package_vulns.items(),
            key=lambda x: (x[1]['critical'] + x[1]['high'], x[1]['count']),
            reverse=True
        )

        # Get top CRITICAL and HIGH vulnerabilities with details
        critical_high = [
            v for v in vulnerabilities
            if v.get('severity', '').upper() in ['CRITICAL', 'HIGH']
        ]
        critical_high.sort(key=lambda x: (
            0 if x.get('severity', '').upper() == 'CRITICAL' else 1,
            x.get('severity_score', 0)
        ), reverse=True)

        # Extract detailed information for top 50 CRITICAL/HIGH
        critical_high_details = [
            {
                'id': v.get('id', 'UNKNOWN'),
                'title': v.get('title', 'No title'),
                'severity': v.get('severity', 'UNKNOWN'),
                'package': v.get('package', v.get('file', 'Unknown')),
                'installed_version': v.get('installed_version', 'N/A'),
                'fixed_version': v.get('fixed_version', 'N/A'),
                'tool': v.get('tool', 'Unknown'),
                'category': v.get('category', 'Unknown')
            }
            for v in critical_high[:50]  # Top 50 critical/high
        ]

        return {
            "total_count": len(vulnerabilities),
            "by_severity": dict(by_severity),
            "by_tool": dict(by_tool),
            "by_category": dict(by_category),
            "by_package": dict(sorted_packages[:20]),  # Top 20 packages
            "critical_high_details": critical_high_details,
            "critical_count": by_severity.get('CRITICAL', 0),
            "high_count": by_severity.get('HIGH', 0),
            "medium_count": by_severity.get('MEDIUM', 0),
            "low_count": by_severity.get('LOW', 0)
        }


class SecurityAnalysisLLM:
    """Improved high-level interface for security analysis using LLMs."""

    def __init__(self, api_token: str, preferred_model: str = "deepseek"):
        self.api_token = api_token
        self.preferred_model = preferred_model.lower()
        self.analyzer = VulnerabilityAnalyzer()

        # Initialize both models
        self.deepseek = DeepSeekR1(api_token)
        self.llama = LlamaModel(api_token)

    def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> Optional[str]:
        """Generate response using specified or preferred model."""
        model_to_use = model or self.preferred_model

        if model_to_use == "deepseek":
            return self.deepseek.generate(prompt, **kwargs)
        elif model_to_use == "llama":
            return self.llama.generate(prompt, **kwargs)
        else:
            print(f"Unknown model: {model_to_use}, defaulting to DeepSeek")
            return self.deepseek.generate(prompt, **kwargs)

    def generate_executive_summary(self, vulnerability_data: Dict[str, Any]) -> str:
        """
        Generate executive summary with ACCURATE vulnerability counts.
        Fixes the issue where only 1 vulnerability was reported instead of 705.
        """
        risk_metrics = vulnerability_data.get('risk_metrics', {})
        tool_summary = vulnerability_data.get('tool_summary', {})
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])

        # COMPREHENSIVE ANALYSIS OF ALL VULNERABILITIES
        analysis = self.analyzer.analyze_vulnerabilities(vulnerabilities)

        # Build detailed tool breakdown
        tool_details = []
        for tool, info in tool_summary.items():
            count = info.get('count', 0)
            tool_details.append(f"  • {tool}: {count} findings")

        tool_breakdown = "\n".join(tool_details) if tool_details else "  • No tools processed"

        # Package-specific details
        package_details = []
        for pkg, stats in list(analysis['by_package'].items())[:10]:
            critical = stats['critical']
            high = stats['high']
            total = stats['count']
            cve_list = ', '.join(stats['cves'][:5]) if stats['cves'] else 'N/A'
            package_details.append(
                f"  • {pkg}: {total} vulnerabilities ({critical} CRITICAL, {high} HIGH)\n    CVEs: {cve_list}"
            )

        package_breakdown = "\n".join(package_details) if package_details else "  • No package data"

        # Top critical/high vulnerabilities
        top_vulns = []
        for v in analysis['critical_high_details'][:15]:
            top_vulns.append(
                f"  • [{v['severity']}] {v['id']} in {v['package']} "
                f"(installed: {v['installed_version']}, fixed: {v['fixed_version']})"
            )

        top_vulns_text = "\n".join(top_vulns) if top_vulns else "  • None"

        prompt = f"""You are a cybersecurity expert tasked with creating an executive summary for leadership.

CRITICAL SECURITY SCAN RESULTS:

OVERALL STATISTICS:
- Total Vulnerabilities Found: {analysis['total_count']}
- Critical Severity: {analysis['critical_count']}
- High Severity: {analysis['high_count']}
- Medium Severity: {analysis['medium_count']}
- Low Severity: {analysis['low_count']}
- Overall Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}
- Risk Score: {risk_metrics.get('risk_score', 0)}/100

FINDINGS BY SECURITY TOOL:
{tool_breakdown}

FINDINGS BY CATEGORY:
{json.dumps(analysis['by_category'], indent=2)}

TOP AFFECTED PACKAGES (Sorted by Critical + High Count):
{package_breakdown}

TOP 15 CRITICAL/HIGH VULNERABILITIES:
{top_vulns_text}

IMPORTANT CONTEXT:
- This scan identified {analysis['total_count']} total vulnerabilities across the application
- Container/OS vulnerabilities ({analysis['by_category'].get('Container Security', 0)}) are a major concern
- The package '{list(analysis['by_package'].items())[0][0] if analysis['by_package'] else 'N/A'}' has {list(analysis['by_package'].items())[0][1]['count'] if analysis['by_package'] else 0} vulnerabilities

Create a concise executive summary (300-500 words) that:
1. Highlights the overall security posture (emphasize the {analysis['total_count']} total vulnerabilities)
2. Identifies the most critical risks (focus on {analysis['critical_count']} CRITICAL and {analysis['high_count']} HIGH severity issues)
3. Provides business impact assessment
4. Recommends immediate actions (specifically mention updating vulnerable packages like those listed above)
5. Uses non-technical language suitable for C-level executives

IMPORTANT: Your summary MUST accurately reflect that {analysis['total_count']} vulnerabilities were found, NOT just 1 or a handful.

Executive Summary:"""

        return self.generate(prompt, max_length=1500, temperature=0.7) or "Summary generation failed."

    def generate_technical_playbook(self, vulnerability_data: Dict[str, Any]) -> str:
        """
        Generate technical remediation playbook with SPECIFIC package and CVE details.
        Fixes the issue where generic advice was given instead of specific fixes.
        """
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])
        risk_metrics = vulnerability_data.get('risk_metrics', {})

        # COMPREHENSIVE ANALYSIS OF ALL VULNERABILITIES
        analysis = self.analyzer.analyze_vulnerabilities(vulnerabilities)

        # Build detailed package remediation list
        package_remediations = []
        for pkg, stats in list(analysis['by_package'].items())[:20]:
            if stats['critical'] > 0 or stats['high'] > 0:
                # Find a sample vulnerability for this package to get version info
                sample_vuln = next(
                    (v for v in vulnerabilities if v.get('package', v.get('file')) == pkg),
                    {}
                )
                package_remediations.append({
                    'package': pkg,
                    'count': stats['count'],
                    'critical': stats['critical'],
                    'high': stats['high'],
                    'installed_version': sample_vuln.get('installed_version', 'unknown'),
                    'fixed_version': sample_vuln.get('fixed_version', 'latest'),
                    'cves': stats['cves'][:10]  # Top 10 CVEs
                })

        # Format package remediation details
        remediation_details = []
        for pkg_info in package_remediations[:15]:
            cve_list = ', '.join(pkg_info['cves']) if pkg_info['cves'] else 'Multiple CVEs'
            remediation_details.append(
                f"  • {pkg_info['package']}: {pkg_info['count']} vulnerabilities "
                f"({pkg_info['critical']} CRITICAL, {pkg_info['high']} HIGH)\n"
                f"    Installed: {pkg_info['installed_version']} → Fixed: {pkg_info['fixed_version']}\n"
                f"    CVEs: {cve_list}"
            )

        remediation_text = "\n".join(remediation_details) if remediation_details else "  • No package updates needed"

        # Categorize vulnerabilities
        container_vulns = [v for v in vulnerabilities if v.get('category') == 'Container Security']
        code_vulns = [v for v in vulnerabilities if v.get('category') in ['SAST', 'Code Quality']]
        dependency_vulns = [v for v in vulnerabilities if v.get('category') == 'SCA']
        secrets_vulns = [v for v in vulnerabilities if v.get('category') == 'Secrets']

        prompt = f"""You are a DevSecOps engineer creating a technical remediation playbook.

COMPLETE VULNERABILITY LANDSCAPE:
- Total Vulnerabilities: {analysis['total_count']}
- Critical: {analysis['critical_count']}
- High: {analysis['high_count']}
- Medium: {analysis['medium_count']}
- Low: {analysis['low_count']}

VULNERABILITY BREAKDOWN BY TYPE:
- Container/OS Issues: {len(container_vulns)}
- Code Issues (SAST): {len(code_vulns)}
- Dependency Issues: {len(dependency_vulns)}
- Secrets Exposed: {len(secrets_vulns)}
- Other: {analysis['total_count'] - len(container_vulns) - len(code_vulns) - len(dependency_vulns) - len(secrets_vulns)}

TOP PACKAGES REQUIRING UPDATES (by Critical + High severity):
{remediation_text}

SPECIFIC CRITICAL/HIGH VULNERABILITIES TO ADDRESS:
{json.dumps(analysis['critical_high_details'][:20], indent=2)}

Create a detailed technical playbook with:

1. CONTAINER/OS PACKAGE UPDATES (Priority: CRITICAL)
   - Specific commands to update the {len(package_remediations)} vulnerable packages
   - Focus on {list(analysis['by_package'].items())[0][0] if analysis['by_package'] else 'top packages'} with {list(analysis['by_package'].items())[0][1]['count'] if analysis['by_package'] else 0} vulnerabilities
   - Include Dockerfile changes or base image updates
   - Provide update commands for each major package

2. SECRETS MANAGEMENT ({len(secrets_vulns)} secrets found)
   - How to remove secrets from git history
   - Secret rotation procedures
   - Secrets management tools to implement

3. CODE FIXES ({len(code_vulns)} code issues)
   - Specific code changes needed
   - Secure coding patterns
   - Code review checklist

4. DEPENDENCY UPDATES ({len(dependency_vulns)} dependencies)
   - Package update commands
   - Compatibility testing steps
   - Rollback procedures

5. VERIFICATION
   - How to verify all {analysis['total_count']} vulnerabilities are addressed
   - Re-scan procedures
   - Acceptance criteria

CRITICAL: Your playbook MUST provide SPECIFIC remediation steps for the {analysis['high_count']} HIGH severity and {analysis['critical_count']} CRITICAL vulnerabilities, especially for packages like {', '.join(list(analysis['by_package'].keys())[:5])}.

Include actual commands like:
- apt-get update && apt-get install --only-upgrade <package>=<version>
- Docker base image updates
- Package manager commands

Technical Playbook:"""

        return self.generate(prompt, max_length=3500, temperature=0.5) or "Playbook generation failed."

    def generate_remediation_policy(self, vulnerability_data: Dict[str, Any]) -> str:
        """Generate detailed remediation policy with accurate counts."""
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])
        risk_metrics = vulnerability_data.get('risk_metrics', {})

        # Comprehensive analysis
        analysis = self.analyzer.analyze_vulnerabilities(vulnerabilities)

        prompt = f"""You are a security architect creating a comprehensive remediation policy.

COMPLETE VULNERABILITY LANDSCAPE:
- Total Issues: {analysis['total_count']}
- Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}
- Critical: {analysis['critical_count']}
- High: {analysis['high_count']}
- Medium: {analysis['medium_count']}
- Low: {analysis['low_count']}

VULNERABILITY CATEGORIES:
{json.dumps(analysis['by_category'], indent=2)}

TOP AFFECTED COMPONENTS:
{json.dumps(dict(list(analysis['by_package'].items())[:10]), indent=2)}

Create a structured remediation policy that includes:

1. IMMEDIATE ACTIONS (0-7 days)
   - All {analysis['critical_count']} CRITICAL vulnerabilities
   - Top {min(analysis['high_count'], 20)} HIGH severity vulnerabilities
   - Emergency response procedures

2. SHORT-TERM ACTIONS (1-4 weeks)
   - Remaining HIGH severity vulnerabilities ({max(0, analysis['high_count'] - 20)} items)
   - Quick wins and low-hanging fruit

3. MEDIUM-TERM ACTIONS (1-3 months)
   - All {analysis['medium_count']} MEDIUM severity vulnerabilities
   - Process improvements

4. LONG-TERM ACTIONS (3-6 months)
   - {analysis['low_count']} LOW severity vulnerabilities
   - Strategic security improvements

5. PREVENTIVE MEASURES
   - Security controls to prevent recurrence of these {analysis['total_count']} vulnerabilities
   - Training and awareness requirements

6. VERIFICATION AND TESTING
   - How to verify fixes for all {analysis['total_count']} issues
   - Regression testing requirements

Format as a clear, actionable policy document.

Remediation Policy:"""

        return self.generate(prompt, max_length=3000, temperature=0.6) or "Policy generation failed."

    def generate_compliance_mapping(self, vulnerability_data: Dict[str, Any]) -> str:
        """Generate compliance traceability mapping."""
        compliance_data = vulnerability_data.get('compliance_mapping', {})
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])

        analysis = self.analyzer.analyze_vulnerabilities(vulnerabilities)

        prompt = f"""You are a compliance officer creating a traceability matrix.

VULNERABILITY STATISTICS:
- Total Vulnerabilities: {analysis['total_count']}
- Critical: {analysis['critical_count']}
- High: {analysis['high_count']}

COMPLIANCE FRAMEWORKS AFFECTED:
{json.dumps(compliance_data, indent=2)}

Create a compliance traceability document that:

1. ISO/IEC 27001 MAPPING
   - Which controls are affected by these {analysis['total_count']} vulnerabilities
   - Gap analysis
   - Remediation requirements

2. PCI-DSS MAPPING
   - Relevant requirements
   - Compliance impact
   - Remediation priority

3. OWASP TOP 10 MAPPING
   - Which OWASP categories are violated
   - Risk assessment
   - Mitigation strategies

4. CWE/SANS TOP 25 MAPPING
   - Common weakness enumeration
   - Industry standards alignment
   - Best practice recommendations

5. AUDIT TRAIL
   - What evidence to collect for {analysis['total_count']} vulnerabilities
   - Documentation requirements
   - Verification procedures

6. RISK ACCEPTANCE MATRIX
   - Which risks can be accepted
   - Risk transfer options
   - Residual risk management

Format as a compliance traceability matrix.

Compliance Mapping:"""

        return self.generate(prompt, max_length=3000, temperature=0.6) or "Compliance mapping failed."

    def generate_risk_assessment(self, vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment with accurate statistics."""
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])
        risk_metrics = vulnerability_data.get('risk_metrics', {})

        analysis = self.analyzer.analyze_vulnerabilities(vulnerabilities)

        # Calculate business impact
        critical_count = analysis['critical_count']
        high_count = analysis['high_count']

        business_impact = "SEVERE" if critical_count > 0 else "HIGH" if high_count > 5 else "MEDIUM"

        prompt = f"""You are a risk management expert performing a security risk assessment.

CURRENT SECURITY STATE:
- Total Vulnerabilities: {analysis['total_count']}
- Critical: {critical_count}
- High: {high_count}
- Risk Score: {risk_metrics.get('risk_score', 0)}
- Business Impact: {business_impact}

VULNERABILITY DISTRIBUTION:
- By Tool: {json.dumps(analysis['by_tool'], indent=2)}
- By Category: {json.dumps(analysis['by_category'], indent=2)}

TOP VULNERABLE COMPONENTS:
{json.dumps(dict(list(analysis['by_package'].items())[:5]), indent=2)}

Analyze and provide:

1. LIKELIHOOD OF EXPLOITATION
   - Attack surface analysis for {analysis['total_count']} vulnerabilities
   - Threat actor capabilities
   - Exploitation difficulty

2. BUSINESS IMPACT
   - Data breach potential
   - Financial impact (considering {critical_count} CRITICAL + {high_count} HIGH severity issues)
   - Reputational damage
   - Regulatory consequences

3. RISK PRIORITIZATION
   - Which of the {analysis['total_count']} vulnerabilities to fix first
   - Risk treatment strategy
   - Resource allocation

4. THREAT SCENARIOS
   - Most likely attack paths
   - Worst-case scenarios
   - Mitigation priorities

Provide concise, actionable risk analysis that addresses the scale of {analysis['total_count']} vulnerabilities.

Risk Assessment:"""

        analysis_text = self.generate(prompt, max_length=2500, temperature=0.7)

        return {
            "business_impact": business_impact,
            "risk_level": risk_metrics.get('risk_level', 'UNKNOWN'),
            "analysis": analysis_text or "Risk assessment failed.",
            "metrics": risk_metrics,
            "detailed_stats": {
                "total": analysis['total_count'],
                "critical": critical_count,
                "high": high_count,
                "by_tool": analysis['by_tool'],
                "by_category": analysis['by_category'],
                "top_packages": dict(list(analysis['by_package'].items())[:10])
            }
        }


def validate_vulnerability_data(data_path: str) -> Dict[str, Any]:
    """
    Validates and loads vulnerability data with comprehensive error handling.

    Returns:
        Dictionary with validation results and loaded data
    """
    result = {
        "valid": False,
        "data": None,
        "errors": [],
        "warnings": [],
        "stats": {}
    }

    try:
        # Check file exists
        if not os.path.exists(data_path):
            result["errors"].append(f"File not found: {data_path}")
            return result

        # Load JSON
        with open(data_path, 'r') as f:
            data = json.load(f)

        result["data"] = data

        # Validate structure
        if 'vulnerabilities' not in data:
            result["errors"].append("Missing 'vulnerabilities' key in data")
            return result

        if 'risk_metrics' not in data:
            result["warnings"].append("Missing 'risk_metrics' key")

        # Count vulnerabilities
        vuln_count = len(data.get('vulnerabilities', []))
        risk_total = data.get('risk_metrics', {}).get('total', 0)

        result["stats"] = {
            "vulnerability_array_length": vuln_count,
            "risk_metrics_total": risk_total,
            "match": vuln_count == risk_total
        }

        if vuln_count != risk_total:
            result["warnings"].append(
                f"Mismatch: vulnerabilities array has {vuln_count} items but "
                f"risk_metrics.total reports {risk_total}"
            )

        if vuln_count == 0:
            result["warnings"].append("No vulnerabilities found in data")

        result["valid"] = len(result["errors"]) == 0

    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON: {e}")
    except Exception as e:
        result["errors"].append(f"Unexpected error: {e}")

    return result


if __name__ == "__main__":
    # Test the improved LLM integration
    print("="*70)
    print("IMPROVED LLM INTEGRATION - VALIDATION TEST")
    print("="*70)

    # Validate data
    data_path = "processed/normalized_vulnerabilities.json"
    print(f"\nValidating data from: {data_path}")
    validation = validate_vulnerability_data(data_path)

    if validation["errors"]:
        print("\n❌ ERRORS:")
        for error in validation["errors"]:
            print(f"  • {error}")

    if validation["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in validation["warnings"]:
            print(f"  • {warning}")

    if validation["valid"]:
        print("\n✅ Data validation passed")
        print(f"\nData Statistics:")
        print(f"  • Vulnerabilities in array: {validation['stats']['vulnerability_array_length']}")
        print(f"  • Total in risk_metrics: {validation['stats']['risk_metrics_total']}")
        print(f"  • Counts match: {validation['stats']['match']}")

        # Test analysis
        print("\n" + "="*70)
        print("TESTING VULNERABILITY ANALYZER")
        print("="*70)

        analyzer = VulnerabilityAnalyzer()
        analysis = analyzer.analyze_vulnerabilities(validation["data"]["vulnerabilities"])

        print(f"\nTotal Vulnerabilities: {analysis['total_count']}")
        print(f"By Severity: {analysis['by_severity']}")
        print(f"By Tool: {analysis['by_tool']}")
        print(f"By Category: {analysis['by_category']}")
        print(f"\nTop 5 Affected Packages:")
        for pkg, stats in list(analysis['by_package'].items())[:5]:
            print(f"  • {pkg}: {stats['count']} total ({stats['critical']} CRITICAL, {stats['high']} HIGH)")

        print(f"\nCritical/High Vulnerabilities: {len(analysis['critical_high_details'])}")

        # Test LLM integration
        token = os.environ.get('HF_TOKEN')
        if token:
            print("\n" + "="*70)
            print("TESTING LLM INTEGRATION")
            print("="*70)

            llm = SecurityAnalysisLLM(token, preferred_model="deepseek")
            print("\n✅ LLM initialized successfully")
            print("\nTo generate reports, run: python3 real_llm_integration.py")
        else:
            print("\n⚠️  HF_TOKEN not set - skipping LLM test")

    else:
        print("\n❌ Data validation failed - cannot proceed with testing")

    print("\n" + "="*70)
