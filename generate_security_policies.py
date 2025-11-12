#!/usr/bin/env python3
"""
AI-Powered Security Policy Generator using DeepSeek R1
Generates dynamic security policies and recommendations based on actual vulnerability data
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import requests

def load_vulnerability_data(processed_dir: str = "processed") -> Dict[str, Any]:
    """Load normalized vulnerability data."""
    vuln_file = Path(processed_dir) / "normalized_vulnerabilities.json"

    if not vuln_file.exists():
        print(f"WARNING: No vulnerability data found at {vuln_file}")
        return {"vulnerabilities": [], "risk_metrics": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}}

    with open(vuln_file, 'r') as f:
        data = json.load(f)

    return data

def summarize_vulnerabilities(vuln_data: Dict[str, Any]) -> str:
    """Create a concise summary of vulnerabilities for LLM context."""
    risk_metrics = vuln_data.get("risk_metrics", {})
    vulnerabilities = vuln_data.get("vulnerabilities", [])

    # Get top critical/high vulnerabilities
    top_vulns = [v for v in vulnerabilities if v.get("severity") in ["CRITICAL", "HIGH"]][:10]

    summary = f"""Security Scan Results:
- Total Vulnerabilities: {risk_metrics.get('total', 0)}
- Critical: {risk_metrics.get('critical', 0)}
- High: {risk_metrics.get('high', 0)}
- Medium: {risk_metrics.get('medium', 0)}
- Low: {risk_metrics.get('low', 0)}
- Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}

Top Critical/High Issues:
"""

    for i, vuln in enumerate(top_vulns, 1):
        summary += f"\n{i}. [{vuln.get('severity')}] {vuln.get('title', 'N/A')}"
        if vuln.get('package'):
            summary += f" (Package: {vuln.get('package')})"
        if vuln.get('category'):
            summary += f" - Category: {vuln.get('category')}"

    if not top_vulns:
        summary += "\nNo critical or high severity vulnerabilities found."

    return summary

def call_huggingface_api(prompt: str, hf_token: str, model: str = "deepseek-ai/DeepSeek-R1") -> str:
    """Call HuggingFace Inference API with DeepSeek R1."""

    # HuggingFace Inference API endpoint
    api_url = f"https://router.huggingface.co/hf-inference/models/{model}"

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }

    try:
        print(f"Calling HuggingFace API with model: {model}...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)
        else:
            print(f"WARNING: API call failed with status {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"WARNING: Error calling HuggingFace API: {str(e)}")
        return None

def parse_llm_response(llm_response: str) -> Dict[str, Any]:
    """Parse LLM response to extract structured policies and recommendations."""

    # Try to extract JSON from response
    try:
        # Look for JSON content in the response
        start_idx = llm_response.find("{")
        end_idx = llm_response.rfind("}") + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = llm_response[start_idx:end_idx]
            return json.loads(json_str)
    except Exception as e:
        print(f"Could not parse LLM response as JSON: {e}")

    # Fallback: Extract structured content manually
    policies = []
    recommendations = []

    lines = llm_response.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()

        if 'policy' in line.lower() or 'remediation' in line.lower():
            current_section = 'policies'
        elif 'recommendation' in line.lower():
            current_section = 'recommendations'
        elif line.startswith(('-', '*', '•')) and current_section == 'recommendations':
            recommendations.append(line.lstrip('-*• '))
        elif line and current_section == 'policies':
            if any(keyword in line.lower() for keyword in ['critical', 'high', 'medium', 'update', 'patch', 'fix']):
                policies.append({
                    "title": line[:100],
                    "description": line,
                    "priority": "HIGH" if "critical" in line.lower() else "MEDIUM"
                })

    return {
        "policies": policies[:5] if policies else [],
        "recommendations": recommendations[:10] if recommendations else []
    }

def generate_fallback_policies(vuln_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate intelligent fallback policies based on vulnerability data."""

    risk_metrics = vuln_data.get("risk_metrics", {})
    vulnerabilities = vuln_data.get("vulnerabilities", [])

    critical_count = risk_metrics.get("critical", 0)
    high_count = risk_metrics.get("high", 0)

    # Analyze vulnerability types
    categories = {}
    for vuln in vulnerabilities:
        cat = vuln.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    policies = []
    recommendations = []

    # Policy 1: Critical Vulnerability Remediation
    if critical_count > 0:
        policies.append({
            "id": "POLICY-001",
            "title": "Immediate Critical Vulnerability Remediation",
            "description": f"Address all {critical_count} CRITICAL severity vulnerabilities within 24 hours to prevent potential security breaches",
            "priority": "CRITICAL",
            "actions": [
                "Review all CRITICAL findings with security team",
                "Create emergency remediation tickets with P0 priority",
                "Deploy security patches immediately",
                "Verify fixes with re-scan within 24 hours"
            ]
        })

    # Policy 2: High Severity Issues
    if high_count > 0:
        policies.append({
            "id": "POLICY-002",
            "title": "High Severity Vulnerability Management",
            "description": f"Remediate {high_count} HIGH severity vulnerabilities within 72 hours following security best practices",
            "priority": "HIGH",
            "actions": [
                "Prioritize HIGH vulnerabilities by exploitability",
                "Assign remediation tasks to development team",
                "Test patches in staging environment",
                "Deploy fixes within 72-hour SLA"
            ]
        })

    # Policy 3: Dependency Management
    if "SCA" in categories or "Dependency" in categories:
        dep_count = categories.get("SCA", 0) + categories.get("Dependency", 0)
        policies.append({
            "id": "POLICY-003",
            "title": "Dependency Security Update Strategy",
            "description": f"Update {dep_count} vulnerable dependencies to latest secure versions",
            "priority": "HIGH" if high_count > 5 else "MEDIUM",
            "actions": [
                "Enable automated dependency vulnerability scanning",
                "Update all packages with known CVEs",
                "Review and test dependency updates in staging",
                "Implement dependency pinning for stability"
            ]
        })

    # Policy 4: Container Security
    if "Container" in categories or "Container Security" in categories:
        policies.append({
            "id": "POLICY-004",
            "title": "Container Image Hardening",
            "description": "Implement container security best practices to reduce attack surface",
            "priority": "MEDIUM",
            "actions": [
                "Use minimal and updated base images (alpine or distroless)",
                "Run containers as non-root user",
                "Implement resource limits and security contexts",
                "Scan images before deployment with Trivy"
            ]
        })

    # Policy 5: Code Security
    if "SAST" in categories or "Code" in categories:
        policies.append({
            "id": "POLICY-005",
            "title": "Secure Code Development Practices",
            "description": "Address code-level vulnerabilities identified by SAST tools",
            "priority": "MEDIUM",
            "actions": [
                "Implement input validation and sanitization",
                "Use parameterized queries to prevent SQL injection",
                "Enable security linters in IDE and pre-commit hooks",
                "Conduct code security reviews for critical changes"
            ]
        })

    # Generate recommendations
    recommendations = [
        "Integrate security scanning in CI/CD pipeline as mandatory gates",
        "Implement security training program for development team",
        "Establish 24/7 security incident response procedures",
        "Schedule quarterly security audits and penetration testing",
        "Maintain comprehensive security documentation and runbooks",
        "Enable real-time security monitoring and alerting",
        "Implement security champions program within teams",
        "Regular security posture reviews with stakeholders"
    ]

    if critical_count > 0 or high_count > 10:
        recommendations.insert(0, "URGENT: Immediate security review required - Critical vulnerabilities detected")

    return {
        "policies": policies[:5],
        "recommendations": recommendations[:8]
    }

def generate_security_policies(hf_token: str = None) -> Dict[str, Any]:
    """Main function to generate security policies."""

    print("=" * 70)
    print("AI-POWERED SECURITY POLICY GENERATOR")
    print("=" * 70)

    # Load vulnerability data
    print("\nLoading vulnerability data...")
    vuln_data = load_vulnerability_data()

    total_vulns = vuln_data.get("risk_metrics", {}).get("total", 0)
    print(f"Loaded {total_vulns} vulnerabilities")

    # Create vulnerability summary
    vuln_summary = summarize_vulnerabilities(vuln_data)
    print("\nVulnerability Summary:")
    print(vuln_summary)

    policies_data = None

    # Try to use LLM if token is provided
    if hf_token and len(hf_token) > 10:
        print("\nAttempting to generate policies using DeepSeek R1 LLM...")

        prompt = f"""You are a security expert. Based on the following vulnerability scan results, generate 3-5 security policies and 5-8 actionable recommendations.

{vuln_summary}

Please provide:
1. Security policies (with id, title, description, priority, and actions)
2. Security recommendations (specific, actionable items)

Format your response as JSON with this structure:
{{
    "policies": [
        {{
            "id": "POLICY-001",
            "title": "Policy Title",
            "description": "Detailed description",
            "priority": "CRITICAL/HIGH/MEDIUM",
            "actions": ["action1", "action2", "action3"]
        }}
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ]
}}

Focus on practical, actionable items based on the severity and types of vulnerabilities found."""

        llm_response = call_huggingface_api(prompt, hf_token)

        if llm_response:
            print("LLM response received, parsing...")
            policies_data = parse_llm_response(llm_response)

            if policies_data and (policies_data.get("policies") or policies_data.get("recommendations")):
                print("Successfully generated policies using LLM!")
            else:
                print("LLM response could not be parsed, using fallback...")
                policies_data = None
        else:
            print("LLM call failed, using fallback policy generator...")
    else:
        print("\nNo HuggingFace token provided, using intelligent fallback...")

    # Use fallback if LLM failed or no token
    if not policies_data:
        policies_data = generate_fallback_policies(vuln_data)

    # Build final output
    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "model": os.getenv("HF_MODEL", "deepseek-ai/DeepSeek-R1"),
        "generation_method": "llm" if (policies_data and hf_token) else "intelligent-fallback",
        "total_vulnerabilities": total_vulns,
        "risk_metrics": vuln_data.get("risk_metrics", {}),
        "policies": policies_data.get("policies", []),
        "recommendations": policies_data.get("recommendations", [])
    }

    # Save to file
    output_dir = Path("ai-policies")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "security-policies.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nGenerated {len(output['policies'])} policies and {len(output['recommendations'])} recommendations")
    print(f"Saved to: {output_file}")
    print("\n" + "=" * 70)

    return output

def main():
    """Main execution."""
    # Get HuggingFace token from environment
    hf_token = os.environ.get('HF_TOKEN', '')

    try:
        result = generate_security_policies(hf_token)

        print("\nSUMMARY:")
        print(f"  Total Vulnerabilities: {result['total_vulnerabilities']}")
        print(f"  Risk Level: {result.get('risk_metrics', {}).get('risk_level', 'UNKNOWN')}")
        print(f"  Policies Generated: {len(result['policies'])}")
        print(f"  Recommendations: {len(result['recommendations'])}")
        print(f"  Generation Method: {result['generation_method']}")

        return 0
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
