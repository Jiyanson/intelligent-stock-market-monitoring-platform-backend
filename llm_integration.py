#!/usr/bin/env python3
"""
LLM Integration Module for Security Analysis
Supports DeepSeek R1 and Llama models via HuggingFace Inference API
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
import requests


class LLMProvider:
    """Base class for LLM providers."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://router.huggingface.co/hf-inference/models/"

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
                    # Model is loading
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
        self.model_id = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"  # Using distilled version for faster inference

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


class SecurityAnalysisLLM:
    """High-level interface for security analysis using LLMs."""

    def __init__(self, api_token: str, preferred_model: str = "deepseek"):
        self.api_token = api_token
        self.preferred_model = preferred_model.lower()

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
        """Generate executive summary from vulnerability data."""
        risk_metrics = vulnerability_data.get('risk_metrics', {})
        tool_summary = vulnerability_data.get('tool_summary', {})
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])[:10]  # Top 10

        prompt = f"""You are a cybersecurity expert tasked with creating an executive summary for leadership.

VULNERABILITY SCAN RESULTS:
- Total Vulnerabilities: {risk_metrics.get('total', 0)}
- Critical: {risk_metrics.get('critical', 0)}
- High: {risk_metrics.get('high', 0)}
- Medium: {risk_metrics.get('medium', 0)}
- Low: {risk_metrics.get('low', 0)}
- Overall Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}
- Risk Score: {risk_metrics.get('risk_score', 0)}

TOOLS USED:
{json.dumps(tool_summary, indent=2)}

TOP CRITICAL FINDINGS:
{json.dumps([{{'id': v.get('id'), 'title': v.get('title'), 'severity': v.get('severity'), 'tool': v.get('tool')}} for v in vulnerabilities], indent=2)}

Create a concise executive summary (300-500 words) that:
1. Highlights the overall security posture
2. Identifies the most critical risks
3. Provides business impact assessment
4. Recommends immediate actions
5. Uses non-technical language suitable for C-level executives

Executive Summary:"""

        return self.generate(prompt, max_length=1000, temperature=0.7) or "Summary generation failed."

    def generate_remediation_policy(self, vulnerability_data: Dict[str, Any]) -> str:
        """Generate detailed remediation policy."""
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])
        risk_metrics = vulnerability_data.get('risk_metrics', {})

        # Group by category
        categories = {}
        for vuln in vulnerabilities:
            category = vuln.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(vuln)

        prompt = f"""You are a security architect creating a comprehensive remediation policy.

VULNERABILITY LANDSCAPE:
- Total Issues: {risk_metrics.get('total', 0)}
- Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}

VULNERABILITY CATEGORIES:
{json.dumps({cat: len(vulns) for cat, vulns in categories.items()}, indent=2)}

Create a structured remediation policy that includes:

1. IMMEDIATE ACTIONS (0-7 days)
   - Critical vulnerabilities requiring immediate attention
   - Emergency response procedures

2. SHORT-TERM ACTIONS (1-4 weeks)
   - High severity vulnerabilities
   - Quick wins and low-hanging fruit

3. MEDIUM-TERM ACTIONS (1-3 months)
   - Medium severity vulnerabilities
   - Process improvements

4. LONG-TERM ACTIONS (3-6 months)
   - Low severity vulnerabilities
   - Strategic security improvements

5. PREVENTIVE MEASURES
   - Security controls to prevent recurrence
   - Training and awareness requirements

6. VERIFICATION AND TESTING
   - How to verify fixes
   - Regression testing requirements

Format as a clear, actionable policy document.

Remediation Policy:"""

        return self.generate(prompt, max_length=2500, temperature=0.6) or "Policy generation failed."

    def generate_technical_playbook(self, vulnerability_data: Dict[str, Any]) -> str:
        """Generate technical remediation playbook."""
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])[:15]

        prompt = f"""You are a DevSecOps engineer creating a technical remediation playbook.

VULNERABILITIES TO ADDRESS:
{json.dumps([{{
    'id': v.get('id'),
    'title': v.get('title'),
    'severity': v.get('severity'),
    'tool': v.get('tool'),
    'category': v.get('category'),
    'file': v.get('file', v.get('package', 'N/A'))
}} for v in vulnerabilities], indent=2)}

Create a technical playbook with:

1. SECRETS MANAGEMENT
   - How to remove secrets from git history
   - Secret rotation procedures
   - Secrets management tools to implement

2. CODE FIXES
   - Specific code changes needed
   - Secure coding patterns
   - Code review checklist

3. DEPENDENCY UPDATES
   - Package update commands
   - Compatibility testing steps
   - Rollback procedures

4. CONTAINER SECURITY
   - Base image updates
   - Dockerfile hardening
   - Runtime security configurations

5. WEB APPLICATION SECURITY
   - Input validation fixes
   - Authentication improvements
   - Header security configurations

6. AUTOMATION
   - Pre-commit hooks
   - CI/CD integration
   - Automated testing

Include specific commands, code snippets, and configuration examples.

Technical Playbook:"""

        return self.generate(prompt, max_length=3000, temperature=0.5) or "Playbook generation failed."

    def generate_compliance_mapping(self, vulnerability_data: Dict[str, Any]) -> str:
        """Generate compliance traceability mapping."""
        compliance_data = vulnerability_data.get('compliance_mapping', {})
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])

        prompt = f"""You are a compliance officer creating a traceability matrix.

COMPLIANCE FRAMEWORKS:
{json.dumps(compliance_data, indent=2)}

Create a compliance traceability document that:

1. ISO/IEC 27001 MAPPING
   - Which controls are affected
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
   - What evidence to collect
   - Documentation requirements
   - Verification procedures

6. RISK ACCEPTANCE MATRIX
   - Which risks can be accepted
   - Risk transfer options
   - Residual risk management

Format as a compliance traceability matrix.

Compliance Mapping:"""

        return self.generate(prompt, max_length=2500, temperature=0.6) or "Compliance mapping failed."

    def generate_risk_assessment(self, vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        vulnerabilities = vulnerability_data.get('vulnerabilities', [])
        risk_metrics = vulnerability_data.get('risk_metrics', {})

        # Calculate business impact
        critical_count = risk_metrics.get('critical', 0)
        high_count = risk_metrics.get('high', 0)

        business_impact = "SEVERE" if critical_count > 0 else "HIGH" if high_count > 5 else "MEDIUM"

        prompt = f"""You are a risk management expert performing a security risk assessment.

CURRENT STATE:
- Total Vulnerabilities: {risk_metrics.get('total', 0)}
- Critical: {critical_count}
- High: {high_count}
- Risk Score: {risk_metrics.get('risk_score', 0)}
- Business Impact: {business_impact}

Analyze and provide:

1. LIKELIHOOD OF EXPLOITATION
   - Attack surface analysis
   - Threat actor capabilities
   - Exploitation difficulty

2. BUSINESS IMPACT
   - Data breach potential
   - Financial impact
   - Reputational damage
   - Regulatory consequences

3. RISK PRIORITIZATION
   - Which vulnerabilities to fix first
   - Risk treatment strategy
   - Resource allocation

4. THREAT SCENARIOS
   - Most likely attack paths
   - Worst-case scenarios
   - Mitigation priorities

Provide concise, actionable risk analysis.

Risk Assessment:"""

        analysis = self.generate(prompt, max_length=2000, temperature=0.7)

        return {
            "business_impact": business_impact,
            "risk_level": risk_metrics.get('risk_level', 'UNKNOWN'),
            "analysis": analysis or "Risk assessment failed.",
            "metrics": risk_metrics
        }


if __name__ == "__main__":
    # Test the LLM integration
    token = os.environ.get('HF_TOKEN')
    if not token:
        print("Error: HF_TOKEN environment variable not set")
        exit(1)

    llm = SecurityAnalysisLLM(token, preferred_model="deepseek")

    # Test with sample data
    sample_data = {
        "risk_metrics": {
            "total": 25,
            "critical": 3,
            "high": 8,
            "medium": 10,
            "low": 4,
            "risk_score": 76,
            "risk_level": "HIGH"
        },
        "vulnerabilities": [
            {"id": "CVE-2024-1234", "title": "SQL Injection", "severity": "CRITICAL", "tool": "OWASP ZAP"},
            {"id": "GITLEAKS-abc123", "title": "Hardcoded AWS Key", "severity": "CRITICAL", "tool": "Gitleaks"}
        ]
    }

    print("Testing Executive Summary Generation...")
    summary = llm.generate_executive_summary(sample_data)
    print(summary)
