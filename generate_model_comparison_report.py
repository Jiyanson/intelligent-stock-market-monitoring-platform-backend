#!/usr/bin/env python3
"""
Model Comparison HTML Report Generator
Creates beautiful visual comparison of DeepSeek R1 vs LLaMA 3.3
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def generate_comparison_html(comparison_data: dict, output_path: str = "ai-reports/model_comparison.html"):
    """Generate comprehensive HTML comparison report."""

    individual_results = comparison_data.get("individual_results", {})
    comparison_metrics = comparison_data.get("comparison_metrics", {})
    winner = comparison_data.get("winner", "N/A")
    recommendation = comparison_data.get("recommendation", "No recommendation available")

    # Get data for both models
    deepseek = individual_results.get("deepseek", {})
    llama = individual_results.get("llama", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Model Comparison Report - DeepSeek R1 vs LLaMA 3.3</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1a202c;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header .subtitle {{
            font-size: 18px;
            opacity: 0.9;
        }}

        .winner-banner {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }}

        .winner-banner .trophy {{
            font-size: 48px;
            margin-bottom: 10px;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h2 {{
            color: #2d3748;
            font-size: 24px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
            padding-left: 15px;
        }}

        .model-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .model-card {{
            background: #f7fafc;
            border-radius: 15px;
            padding: 25px;
            border: 3px solid #e2e8f0;
            transition: all 0.3s ease;
        }}

        .model-card.winner {{
            border-color: #48bb78;
            background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
            box-shadow: 0 10px 30px rgba(72, 187, 120, 0.3);
        }}

        .model-card h3 {{
            font-size: 22px;
            margin-bottom: 15px;
            color: #2d3748;
        }}

        .model-card .badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin-bottom: 15px;
            font-weight: 600;
        }}

        .model-card.winner .badge {{
            background: #48bb78;
        }}

        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }}

        .metric-row:last-child {{
            border-bottom: none;
        }}

        .metric-label {{
            color: #4a5568;
            font-weight: 500;
        }}

        .metric-value {{
            color: #2d3748;
            font-weight: 700;
        }}

        .metric-value.high {{
            color: #48bb78;
        }}

        .metric-value.medium {{
            color: #ed8936;
        }}

        .metric-value.low {{
            color: #f56565;
        }}

        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e2e8f0;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
            position: relative;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .comparison-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .comparison-table td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .comparison-table tr:hover {{
            background: #f7fafc;
        }}

        .recommendation-box {{
            background: linear-gradient(135deg, #fef5e7 0%, #fdebd0 100%);
            border-left: 5px solid #f39c12;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
        }}

        .recommendation-box h3 {{
            color: #e67e22;
            margin-bottom: 10px;
            font-size: 20px;
        }}

        .recommendation-box p {{
            color: #34495e;
            font-size: 16px;
            line-height: 1.8;
        }}

        .chart-container {{
            margin: 30px 0;
        }}

        .bar-chart {{
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            height: 300px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 10px;
        }}

        .bar {{
            width: 80px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px 10px 0 0;
            position: relative;
            transition: all 0.5s ease;
        }}

        .bar:hover {{
            transform: scaleY(1.05);
        }}

        .bar-label {{
            text-align: center;
            margin-top: 10px;
            font-weight: 600;
            color: #2d3748;
        }}

        .bar-value {{
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            background: #2d3748;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
        }}

        .footer {{
            background: #2d3748;
            color: white;
            text-align: center;
            padding: 30px;
            font-size: 14px;
        }}

        @media (max-width: 768px) {{
            .model-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Model Comparison Report</h1>
            <div class="subtitle">DeepSeek R1 vs LLaMA 3.3 70B for Security Policy Generation</div>
            <div style="margin-top: 15px; opacity: 0.8;">
                Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
            </div>
        </div>

        <div class="winner-banner">
            <div class="trophy">🏆</div>
            <div>Winner: {individual_results.get(winner, {}).get('model_name', 'N/A')}</div>
            <div style="font-size: 16px; margin-top: 10px; opacity: 0.9;">
                Quality Score: {individual_results.get(winner, {}).get('quality_score', 0):.1f}/100
            </div>
        </div>

        <div class="content">
            <!-- Executive Summary -->
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="recommendation-box">
                    <h3>💡 Recommendation</h3>
                    <p>{recommendation}</p>
                </div>
            </div>

            <!-- Model Comparison -->
            <div class="section">
                <h2>🔬 Detailed Model Comparison</h2>
                <div class="model-grid">
                    <div class="model-card {'winner' if winner == 'deepseek' else ''}">
                        <div class="badge">{'🏆 WINNER' if winner == 'deepseek' else 'CHALLENGER'}</div>
                        <h3>DeepSeek R1</h3>
                        <p style="color: #718096; margin-bottom: 20px;">Reasoning-optimized model (8B parameters)</p>

                        <div class="metric-row">
                            <span class="metric-label">Overall Quality</span>
                            <span class="metric-value high">{deepseek.get('quality_score', 0):.1f}/100</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Response Time</span>
                            <span class="metric-value">{deepseek.get('response_time', 0):.2f}s</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Policies Generated</span>
                            <span class="metric-value">{deepseek.get('policy_count', 0)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Recommendations</span>
                            <span class="metric-value">{deepseek.get('recommendation_count', 0)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Specificity</span>
                            <span class="metric-value">{deepseek.get('specificity_score', 0):.1f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Relevance</span>
                            <span class="metric-value">{deepseek.get('relevance_score', 0):.1f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Completeness</span>
                            <span class="metric-value">{deepseek.get('completeness_score', 0):.1f}%</span>
                        </div>
                    </div>

                    <div class="model-card {'winner' if winner == 'llama' else ''}">
                        <div class="badge">{'🏆 WINNER' if winner == 'llama' else 'CHALLENGER'}</div>
                        <h3>LLaMA 3.3 70B</h3>
                        <p style="color: #718096; margin-bottom: 20px;">Instruction-tuned model (70B parameters)</p>

                        <div class="metric-row">
                            <span class="metric-label">Overall Quality</span>
                            <span class="metric-value high">{llama.get('quality_score', 0):.1f}/100</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Response Time</span>
                            <span class="metric-value">{llama.get('response_time', 0):.2f}s</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Policies Generated</span>
                            <span class="metric-value">{llama.get('policy_count', 0)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Recommendations</span>
                            <span class="metric-value">{llama.get('recommendation_count', 0)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Specificity</span>
                            <span class="metric-value">{llama.get('specificity_score', 0):.1f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Relevance</span>
                            <span class="metric-value">{llama.get('relevance_score', 0):.1f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Completeness</span>
                            <span class="metric-value">{llama.get('completeness_score', 0):.1f}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quality Metrics Visualization -->
            <div class="section">
                <h2>📈 Quality Metrics Breakdown</h2>

                <div style="margin: 20px 0;">
                    <h4 style="margin-bottom: 10px;">Overall Quality Score</h4>
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: bold; margin-bottom: 5px;">DeepSeek R1</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {deepseek.get('quality_score', 0)}%">
                                {deepseek.get('quality_score', 0):.1f}%
                            </div>
                        </div>
                    </div>
                    <div>
                        <div style="font-weight: bold; margin-bottom: 5px;">LLaMA 3.3 70B</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {llama.get('quality_score', 0)}%; background: linear-gradient(90deg, #48bb78 0%, #38a169 100%)">
                                {llama.get('quality_score', 0):.1f}%
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Detailed Comparison Table -->
            <div class="section">
                <h2>📋 Detailed Metrics Comparison</h2>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>DeepSeek R1</th>
                            <th>LLaMA 3.3 70B</th>
                            <th>Better Model</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Quality Score</strong></td>
                            <td>{deepseek.get('quality_score', 0):.1f}/100</td>
                            <td>{llama.get('quality_score', 0):.1f}/100</td>
                            <td>{'DeepSeek R1' if deepseek.get('quality_score', 0) > llama.get('quality_score', 0) else 'LLaMA 3.3'}</td>
                        </tr>
                        <tr>
                            <td><strong>Response Time</strong></td>
                            <td>{deepseek.get('response_time', 0):.2f}s</td>
                            <td>{llama.get('response_time', 0):.2f}s</td>
                            <td>{'DeepSeek R1' if deepseek.get('response_time', 999) < llama.get('response_time', 999) else 'LLaMA 3.3'}</td>
                        </tr>
                        <tr>
                            <td><strong>Specificity</strong></td>
                            <td>{deepseek.get('specificity_score', 0):.1f}%</td>
                            <td>{llama.get('specificity_score', 0):.1f}%</td>
                            <td>{'DeepSeek R1' if deepseek.get('specificity_score', 0) > llama.get('specificity_score', 0) else 'LLaMA 3.3'}</td>
                        </tr>
                        <tr>
                            <td><strong>Relevance</strong></td>
                            <td>{deepseek.get('relevance_score', 0):.1f}%</td>
                            <td>{llama.get('relevance_score', 0):.1f}%</td>
                            <td>{'DeepSeek R1' if deepseek.get('relevance_score', 0) > llama.get('relevance_score', 0) else 'LLaMA 3.3'}</td>
                        </tr>
                        <tr>
                            <td><strong>Completeness</strong></td>
                            <td>{deepseek.get('completeness_score', 0):.1f}%</td>
                            <td>{llama.get('completeness_score', 0):.1f}%</td>
                            <td>{'DeepSeek R1' if deepseek.get('completeness_score', 0) > llama.get('completeness_score', 0) else 'LLaMA 3.3'}</td>
                        </tr>
                        <tr>
                            <td><strong>Policies Generated</strong></td>
                            <td>{deepseek.get('policy_count', 0)}</td>
                            <td>{llama.get('policy_count', 0)}</td>
                            <td>{'DeepSeek R1' if deepseek.get('policy_count', 0) > llama.get('policy_count', 0) else 'LLaMA 3.3'}</td>
                        </tr>
                        <tr>
                            <td><strong>Recommendations</strong></td>
                            <td>{deepseek.get('recommendation_count', 0)}</td>
                            <td>{llama.get('recommendation_count', 0)}</td>
                            <td>{'DeepSeek R1' if deepseek.get('recommendation_count', 0) > llama.get('recommendation_count', 0) else 'LLaMA 3.3'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Key Insights -->
            <div class="section">
                <h2>🔍 Key Insights</h2>
                <div style="background: #f7fafc; padding: 20px; border-radius: 10px;">
                    <ul style="list-style: none; padding: 0;">
                        <li style="padding: 10px 0; border-bottom: 1px solid #e2e8f0;">
                            <strong>🎯 Quality Difference:</strong> {comparison_metrics.get('quality_difference', 0):.1f} points ({comparison_metrics.get('quality_gap_percentage', 0):.1f}% gap)
                        </li>
                        <li style="padding: 10px 0; border-bottom: 1px solid #e2e8f0;">
                            <strong>⚡ Speed Difference:</strong> {comparison_metrics.get('speed_difference', 0):.2f} seconds
                        </li>
                        <li style="padding: 10px 0; border-bottom: 1px solid #e2e8f0;">
                            <strong>🏆 Quality Leader:</strong> {individual_results.get(comparison_metrics.get('better_quality', 'N/A'), {}).get('model_name', 'N/A')}
                        </li>
                        <li style="padding: 10px 0;">
                            <strong>🚀 Faster Model:</strong> {individual_results.get(comparison_metrics.get('faster_model', 'N/A'), {}).get('model_name', 'N/A')}
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Intelligent Stock Market Monitoring Platform</strong></p>
            <p style="margin-top: 10px; opacity: 0.8;">AI-Powered Security Analysis © {datetime.now().year}</p>
            <p style="margin-top: 10px; font-size: 12px;">
                This report was generated automatically using dual-model comparison methodology
            </p>
        </div>
    </div>
</body>
</html>"""

    # Save HTML file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✅ Model comparison HTML report saved to: {output_file}")
    return output_file


def main():
    """Main execution."""
    # Load comparison data
    comparison_file = Path("ai-policies/model_comparison_report.json")

    if not comparison_file.exists():
        print(f"❌ Comparison report not found: {comparison_file}")
        print("   Please run dual_model_policy_generator.py first")
        return 1

    with open(comparison_file, 'r') as f:
        comparison_data = json.load(f)

    # Generate HTML report
    generate_comparison_html(comparison_data)

    print("✅ Model comparison report generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
