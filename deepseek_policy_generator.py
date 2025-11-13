#!/usr/bin/env python3
"""
DeepSeek R1 Security Policy Generator
Generates security policies using DeepSeek R1 model via OpenRouter
"""

import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests


class DeepSeekPolicyGenerator:
    """Generates security policies using DeepSeek R1 via OpenRouter."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_id = "deepseek/deepseek-r1"
        self.model_name = "DeepSeek R1"
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def call_model(self, prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Call DeepSeek model via OpenRouter and return response with metadata."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/devsecops-pipeline",
            "X-Title": "DevSecOps Security Policy Generator"
        }

        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.95
        }

        start_time = time.time()

        for attempt in range(max_retries):
            try:
                print(f"   Calling {self.model_name} via OpenRouter (attempt {attempt + 1}/{max_retries})...")

                response = requests.post(self.base_url, headers=headers, json=payload, timeout=180)

                if response.status_code == 200:
                    result = response.json()
                    response_time = time.time() - start_time

                    # Extract content from OpenRouter response
                    generated_text = ""
                    if "choices" in result and len(result["choices"]) > 0:
                        message = result["choices"][0].get("message", {})
                        generated_text = message.get("content", "")

                    if not generated_text:
                        print(f"   ⚠️  Empty response from model")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                            continue

                    return {
                        "success": True,
                        "response": generated_text,
                        "response_time": response_time,
                        "timestamp": datetime.utcnow().isoformat(),
                        "token_count": len(generated_text.split()),
                        "usage": result.get("usage", {})
                    }

                elif response.status_code == 429:
                    wait_time = min(10 * (attempt + 1), 30)
                    print(f"   Rate limited... waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue

                elif response.status_code in [502, 503]:
                    wait_time = min(15 * (attempt + 1), 45)
                    print(f"   Service unavailable... waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue

                else:
                    print(f"   Error: HTTP {response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                    continue

            except Exception as e:
                print(f"   Request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)

        # Failed after all retries
        return {
            "success": False,
            "error": "Model call failed after retries",
            "response_time": time.time() - start_time
        }

    def parse_policy_response(self, response_text: str) -> Dict[str, Any]:
        """Parse model response to extract structured policies."""
        policies = []
        recommendations = []

        # Try to extract JSON
        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)

                policies = parsed.get("policies", [])
                recommendations = parsed.get("recommendations", [])
        except:
            pass

        # Fallback: Manual parsing
        if not policies and not recommendations:
            lines = response_text.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()

                if not line:
                    continue

                if any(word in line.lower() for word in ['policy', 'policies', 'remediation']):
                    current_section = 'policies'
                elif any(word in line.lower() for word in ['recommendation', 'suggest']):
                    current_section = 'recommendations'
                elif line.startswith(('-', '*', '•', '1.', '2.', '3.')):
                    content = line.lstrip('-*•0123456789. ')
                    if current_section == 'recommendations':
                        recommendations.append(content)
                    elif current_section == 'policies' and len(content) > 20:
                        policies.append({
                            "title": content[:100],
                            "description": content,
                            "priority": "HIGH" if any(word in content.lower() for word in ['critical', 'immediate', 'urgent']) else "MEDIUM"
                        })

        return {
            "policies": policies[:10],  # Top 10 policies
            "recommendations": recommendations[:15],  # Top 15 recommendations
            "raw_response": response_text
        }

    def generate_policies(self, vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security policies using DeepSeek."""

        print("\n" + "="*70)
        print("DEEPSEEK R1 SECURITY POLICY GENERATION")
        print("="*70)

        # Create prompt
        risk_metrics = vuln_data.get("risk_metrics", {})
        vulnerabilities = vuln_data.get("vulnerabilities", [])[:20]  # Top 20 for context

        prompt = f"""You are a cybersecurity expert. Based on the following vulnerability scan results, generate comprehensive security policies and recommendations.

**Vulnerability Summary:**
- Total Vulnerabilities: {risk_metrics.get('total', 0)}
- Critical: {risk_metrics.get('critical', 0)}
- High: {risk_metrics.get('high', 0)}
- Medium: {risk_metrics.get('medium', 0)}
- Risk Level: {risk_metrics.get('risk_level', 'UNKNOWN')}

**Top Vulnerabilities:**
"""

        for i, vuln in enumerate(vulnerabilities[:10], 1):
            prompt += f"\n{i}. [{vuln.get('severity')}] {vuln.get('title', 'N/A')}"
            if vuln.get('package'):
                prompt += f" (Package: {vuln.get('package')})"

        prompt += """

**Required Output (JSON format):**
{
    "policies": [
        {
            "id": "POLICY-001",
            "title": "Policy Title",
            "description": "Detailed description",
            "priority": "CRITICAL/HIGH/MEDIUM",
            "actions": ["action1", "action2", "action3"]
        }
    ],
    "recommendations": [
        "Specific, actionable recommendation 1",
        "Specific, actionable recommendation 2"
    ]
}

Generate 5-7 policies and 8-12 recommendations that are:
1. Specific to the vulnerabilities found
2. Actionable with clear steps
3. Prioritized by severity and business impact
4. Aligned with security best practices (NIST, ISO 27001, OWASP)
"""

        print(f"\n🤖 Generating policies with {self.model_name}...")

        response_data = self.call_model(prompt)

        if response_data["success"]:
            print(f"   ✅ Response received in {response_data['response_time']:.2f}s")

            # Parse response
            parsed = self.parse_policy_response(response_data["response"])

            print(f"   📝 Generated {len(parsed['policies'])} policies, {len(parsed['recommendations'])} recommendations")

            return {
                "success": True,
                "model_info": {
                    "name": self.model_name,
                    "id": self.model_id
                },
                "response_data": response_data,
                "parsed_output": parsed
            }
        else:
            print(f"   ❌ Failed: {response_data.get('error')}")
            return {
                "success": False,
                "error": response_data.get("error")
            }

    def save_results(self, result: Dict[str, Any], output_dir: str = "ai-policies"):
        """Save results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        if result.get("success") and "parsed_output" in result:
            # Save main policy file
            policy_output = {
                "generated_at": datetime.utcnow().isoformat(),
                "model": result["model_info"]["name"],
                "model_id": result["model_info"]["id"],
                "response_time": result["response_data"]["response_time"],
                "policies": result["parsed_output"]["policies"],
                "recommendations": result["parsed_output"]["recommendations"]
            }

            # Save as security-policies.json
            with open(output_path / "security-policies.json", 'w') as f:
                json.dump(policy_output, f, indent=2)
            print(f"   ✅ Saved: security-policies.json")

            # Save DeepSeek-specific output
            with open(output_path / "deepseek_generated_policy.json", 'w') as f:
                json.dump(policy_output, f, indent=2)
            print(f"   ✅ Saved: deepseek_generated_policy.json")

            return True
        else:
            print("   ⚠️  No policies generated to save")
            return False


def load_vulnerability_data(data_path: str = "processed/normalized_vulnerabilities.json") -> Dict[str, Any]:
    """Load normalized vulnerability data."""
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Could not load vulnerability data: {e}")
        return {
            "vulnerabilities": [],
            "risk_metrics": {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "risk_level": "UNKNOWN"
            }
        }


def main():
    """Main execution."""
    print("="*70)
    print("DEEPSEEK R1 SECURITY POLICY GENERATOR (via OpenRouter)")
    print("="*70)

    # Get OpenRouter API key
    api_key = os.environ.get('OPENROUTER_API_KEY', '')

    if not api_key or len(api_key) < 10:
        print("❌ Error: Valid OPENROUTER_API_KEY required")
        print("   Set environment variable: export OPENROUTER_API_KEY='your_key'")
        print("   Get your key at: https://openrouter.ai/keys")
        return 1

    # Load vulnerability data
    print("\n📂 Loading vulnerability data...")
    vuln_data = load_vulnerability_data()
    print(f"   Loaded {vuln_data['risk_metrics']['total']} vulnerabilities")
    print(f"   Risk Level: {vuln_data['risk_metrics']['risk_level']}")

    # Initialize generator
    generator = DeepSeekPolicyGenerator(api_key)

    # Generate policies
    result = generator.generate_policies(vuln_data)

    # Save results
    if result.get("success"):
        print("\n💾 Saving results...")
        generator.save_results(result)

        print("\n" + "="*70)
        print("✅ POLICY GENERATION COMPLETE")
        print("="*70)
        return 0
    else:
        print("\n" + "="*70)
        print("❌ POLICY GENERATION FAILED")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
