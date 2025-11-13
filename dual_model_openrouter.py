#!/usr/bin/env python3
"""
Dual-Model Security Policy Generator via OpenRouter
Compares DeepSeek R1 and LLaMA 3.3 for generating security policies
"""

import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests


class DualModelPolicyGenerator:
    """Generates and compares security policies using multiple models via OpenRouter."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        # Model configurations
        self.models = {
            "deepseek": {
                "id": "deepseek/deepseek-r1",
                "name": "DeepSeek R1",
                "type": "Reasoning Model"
            },
            "llama": {
                "id": "meta-llama/llama-3.3-70b-instruct",
                "name": "LLaMA 3.3 70B",
                "type": "Instruction-Tuned Model"
            }
        }

    def call_model(self, model_key: str, prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Call a specific model via OpenRouter and return response with metadata."""
        model_config = self.models[model_key]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/devsecops-pipeline",
            "X-Title": "DevSecOps Security Policy Generator"
        }

        payload = {
            "model": model_config["id"],
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
                print(f"   Calling {model_config['name']} (attempt {attempt + 1}/{max_retries})...")

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
                        "model": model_key,
                        "model_name": model_config["name"],
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
            "model": model_key,
            "model_name": model_config["name"],
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
            "policies": policies[:10],
            "recommendations": recommendations[:15],
            "raw_response": response_text
        }

    def evaluate_response_quality(self, model_key: str, parsed_response: Dict[str, Any],
                                  vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the quality of model response."""
        policies = parsed_response.get("policies", [])
        recommendations = parsed_response.get("recommendations", [])
        raw_response = parsed_response.get("raw_response", "")

        # Metrics
        metrics = {
            "policy_count": len(policies),
            "recommendation_count": len(recommendations),
            "total_response_length": len(raw_response),
            "avg_policy_length": sum(len(str(p)) for p in policies) / max(len(policies), 1),
            "avg_recommendation_length": sum(len(r) for r in recommendations) / max(len(recommendations), 1),
            "structured_output": isinstance(policies, list) and len(policies) > 0,
            "actionable_items": len(policies) + len(recommendations),
        }

        # Specificity: Check if policies mention specific technologies/CVEs
        specific_keywords = ['CVE', 'Python', 'Docker', 'dependency', 'version', 'patch', 'update', 'upgrade']
        specificity_count = sum(1 for keyword in specific_keywords if keyword.lower() in raw_response.lower())
        metrics["specificity_score"] = min(specificity_count / len(specific_keywords), 1.0) * 100

        # Relevance: Check if response addresses vulnerability data
        relevance_keywords = ['critical', 'vulnerability', 'security', 'risk', 'remediation', 'fix']
        relevance_count = sum(1 for keyword in relevance_keywords if keyword.lower() in raw_response.lower())
        metrics["relevance_score"] = min(relevance_count / len(relevance_keywords), 1.0) * 100

        # Completeness: Check if covers multiple aspects
        completeness_aspects = {
            "immediate_actions": any(word in raw_response.lower() for word in ['immediate', '24 hours', 'urgent', 'critical']),
            "remediation_steps": any(word in raw_response.lower() for word in ['update', 'patch', 'fix', 'remediate']),
            "prevention": any(word in raw_response.lower() for word in ['prevent', 'avoid', 'monitoring', 'scanning']),
            "compliance": any(word in raw_response.lower() for word in ['compliance', 'iso', 'nist', 'pci', 'gdpr']),
            "prioritization": any(word in raw_response.lower() for word in ['priority', 'critical', 'high', 'medium'])
        }
        metrics["completeness_score"] = (sum(completeness_aspects.values()) / len(completeness_aspects)) * 100

        # Overall quality score (weighted average)
        metrics["overall_quality_score"] = (
            metrics["specificity_score"] * 0.3 +
            metrics["relevance_score"] * 0.4 +
            metrics["completeness_score"] * 0.3
        )

        return metrics

    def generate_policies_with_both_models(self, vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security policies using both models and compare."""

        print("\n" + "="*70)
        print("DUAL-MODEL SECURITY POLICY GENERATION (via OpenRouter)")
        print("DeepSeek R1 vs LLaMA 3.3 70B")
        print("="*70)

        # Create prompt
        risk_metrics = vuln_data.get("risk_metrics", {})
        vulnerabilities = vuln_data.get("vulnerabilities", [])[:20]

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

        results = {}

        # Call both models
        for model_key in ["deepseek", "llama"]:
            print(f"\n🤖 Generating policies with {self.models[model_key]['name']}...")

            response_data = self.call_model(model_key, prompt)

            if response_data["success"]:
                print(f"   ✅ Response received in {response_data['response_time']:.2f}s")

                # Parse response
                parsed = self.parse_policy_response(response_data["response"])

                # Evaluate quality
                metrics = self.evaluate_response_quality(model_key, parsed, vuln_data)

                results[model_key] = {
                    "model_info": self.models[model_key],
                    "response_data": response_data,
                    "parsed_output": parsed,
                    "quality_metrics": metrics
                }

                print(f"   📊 Quality Score: {metrics['overall_quality_score']:.1f}/100")
                print(f"   📝 Generated {metrics['policy_count']} policies, {metrics['recommendation_count']} recommendations")
            else:
                print(f"   ❌ Failed: {response_data.get('error')}")
                results[model_key] = {
                    "model_info": self.models[model_key],
                    "response_data": response_data,
                    "error": response_data.get("error")
                }

        return results

    def generate_comparison_report(self, results: Dict[str, Any], vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed comparison report."""

        print("\n" + "="*70)
        print("MODEL COMPARISON ANALYSIS")
        print("="*70)

        comparison = {
            "timestamp": datetime.utcnow().isoformat(),
            "vulnerability_context": vuln_data.get("risk_metrics", {}),
            "models_compared": list(results.keys()),
            "individual_results": {},
            "comparison_metrics": {},
            "winner": None,
            "recommendation": ""
        }

        # Collect metrics from both models
        for model_key, result in results.items():
            if "quality_metrics" in result:
                metrics = result["quality_metrics"]
                response_time = result["response_data"]["response_time"]

                comparison["individual_results"][model_key] = {
                    "model_name": result["model_info"]["name"],
                    "quality_score": metrics["overall_quality_score"],
                    "response_time": response_time,
                    "policy_count": metrics["policy_count"],
                    "recommendation_count": metrics["recommendation_count"],
                    "specificity_score": metrics["specificity_score"],
                    "relevance_score": metrics["relevance_score"],
                    "completeness_score": metrics["completeness_score"],
                    "structured_output": metrics["structured_output"]
                }

        # Compare models
        if len(comparison["individual_results"]) >= 2:
            deepseek_score = comparison["individual_results"].get("deepseek", {}).get("quality_score", 0)
            llama_score = comparison["individual_results"].get("llama", {}).get("quality_score", 0)

            deepseek_time = comparison["individual_results"].get("deepseek", {}).get("response_time", 999)
            llama_time = comparison["individual_results"].get("llama", {}).get("response_time", 999)

            comparison["comparison_metrics"] = {
                "quality_difference": abs(deepseek_score - llama_score),
                "speed_difference": abs(deepseek_time - llama_time),
                "better_quality": "deepseek" if deepseek_score > llama_score else "llama",
                "faster_model": "deepseek" if deepseek_time < llama_time else "llama",
                "quality_gap_percentage": abs(deepseek_score - llama_score) / max(deepseek_score, llama_score, 1) * 100
            }

            # Determine winner (weighted: 70% quality, 30% speed)
            deepseek_weighted = (deepseek_score * 0.7) + ((100 - min(deepseek_time, 100)) * 0.3)
            llama_weighted = (llama_score * 0.7) + ((100 - min(llama_time, 100)) * 0.3)

            comparison["winner"] = "deepseek" if deepseek_weighted > llama_weighted else "llama"
            winner_name = self.models[comparison["winner"]]["name"]

            # Generate recommendation
            if comparison["comparison_metrics"]["quality_gap_percentage"] < 10:
                comparison["recommendation"] = f"Both models perform similarly (quality difference < 10%). Using {winner_name} based on slight performance edge."
            elif comparison["winner"] == comparison["comparison_metrics"]["better_quality"]:
                comparison["recommendation"] = f"{winner_name} is recommended for superior quality ({comparison['individual_results'][comparison['winner']]['quality_score']:.1f}/100) and comprehensive policy generation."
            else:
                comparison["recommendation"] = f"{winner_name} offers the best balance of quality and performance for this use case."

        # Print summary
        print("\n📊 Comparison Results:")
        for model_key, metrics in comparison["individual_results"].items():
            print(f"\n{metrics['model_name']}:")
            print(f"   Quality Score: {metrics['quality_score']:.1f}/100")
            print(f"   Response Time: {metrics['response_time']:.2f}s")
            print(f"   Policies: {metrics['policy_count']}, Recommendations: {metrics['recommendation_count']}")
            print(f"   Specificity: {metrics['specificity_score']:.1f}%, Relevance: {metrics['relevance_score']:.1f}%")

        if comparison["winner"]:
            print(f"\n🏆 Winner: {self.models[comparison['winner']]['name']}")
            print(f"   {comparison['recommendation']}")

        return comparison

    def save_results(self, results: Dict[str, Any], comparison: Dict[str, Any],
                    output_dir: str = "ai-policies"):
        """Save all results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save individual model outputs
        for model_key, result in results.items():
            if "parsed_output" in result:
                model_output = {
                    "metadata": {
                        "model": result["model_info"]["name"],
                        "model_id": result["model_info"]["id"],
                        "generated_at": result["response_data"]["timestamp"],
                        "response_time": result["response_data"]["response_time"],
                        "quality_score": result["quality_metrics"]["overall_quality_score"]
                    },
                    "policies": result["parsed_output"]["policies"],
                    "recommendations": result["parsed_output"]["recommendations"],
                    "quality_metrics": result["quality_metrics"]
                }

                filename = f"{model_key}_generated_policy.json"
                with open(output_path / filename, 'w') as f:
                    json.dump(model_output, f, indent=2)
                print(f"   ✅ Saved: {filename}")

        # Save comparison report
        comparison_file = output_path / "model_comparison_report.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        print(f"   ✅ Saved: model_comparison_report.json")

        # Save best model output as primary policy file
        if comparison["winner"] and comparison["winner"] in results:
            best_result = results[comparison["winner"]]
            if "parsed_output" in best_result:
                primary_output = {
                    "generated_at": datetime.utcnow().isoformat(),
                    "model": best_result["model_info"]["name"],
                    "model_id": best_result["model_info"]["id"],
                    "generation_method": "dual-model-comparison",
                    "winner_reason": comparison["recommendation"],
                    "quality_score": best_result["quality_metrics"]["overall_quality_score"],
                    "policies": best_result["parsed_output"]["policies"],
                    "recommendations": best_result["parsed_output"]["recommendations"]
                }

                with open(output_path / "security-policies.json", 'w') as f:
                    json.dump(primary_output, f, indent=2)
                print(f"   ✅ Saved: security-policies.json (best model output)")


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
    print("DUAL-MODEL SECURITY POLICY GENERATOR (via OpenRouter)")
    print("DeepSeek R1 vs LLaMA 3.3 70B")
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
    generator = DualModelPolicyGenerator(api_key)

    # Generate policies with both models
    results = generator.generate_policies_with_both_models(vuln_data)

    # Generate comparison report
    comparison = generator.generate_comparison_report(results, vuln_data)

    # Save all results
    print("\n💾 Saving results...")
    generator.save_results(results, comparison)

    print("\n" + "="*70)
    print("✅ DUAL-MODEL ANALYSIS COMPLETE")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
