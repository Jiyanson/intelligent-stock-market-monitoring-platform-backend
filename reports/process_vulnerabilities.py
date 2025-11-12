#!/usr/bin/env python3
"""
Vulnerability Report Normalization Script
Processes and normalizes security scan reports from multiple tools:
- Gitleaks (Secrets scanning)
- Semgrep (SAST)
- Dependency-Check (SCA)
- Trivy (Container scanning)
- OWASP ZAP (DAST)

Outputs a unified JSON schema for downstream AI processing.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class VulnerabilityNormalizer:
    """Normalizes vulnerability reports from multiple security tools."""

    def __init__(self, reports_dir: str = ".", output_dir: str = "../processed"):
        self.reports_dir = Path(reports_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Severity mapping to standardized levels
        self.severity_map = {
            "CRITICAL": 10,
            "HIGH": 8,
            "MEDIUM": 5,
            "LOW": 3,
            "INFO": 1,
            "INFORMATIONAL": 1,
            "NEGLIGIBLE": 1
        }

    def normalize_gitleaks(self, report_path: Path) -> List[Dict[str, Any]]:
        """Normalize Gitleaks secrets scanning report."""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)

            vulnerabilities = []
            findings = data if isinstance(data, list) else data.get('findings', [])

            for finding in findings:
                vuln = {
                    "id": f"GITLEAKS-{finding.get('Commit', finding.get('File', 'unknown'))[:8]}",
                    "tool": "Gitleaks",
                    "category": "Secrets",
                    "type": "Secret Exposure",
                    "title": f"Secret detected: {finding.get('RuleID', 'Unknown')}",
                    "description": finding.get('Description', finding.get('Match', 'Secret found in repository')),
                    "severity": "CRITICAL",
                    "severity_score": 10,
                    "file": finding.get('File', 'unknown'),
                    "line": finding.get('StartLine', 0),
                    "commit": finding.get('Commit', 'N/A'),
                    "rule": finding.get('RuleID', 'unknown'),
                    "remediation": "Remove the secret from version control and rotate credentials immediately.",
                    "cwe": ["CWE-798"],
                    "owasp": ["A02:2021-Cryptographic Failures"],
                    "compliance": ["ISO 27001: A.9.4.3", "PCI-DSS: 6.5.3"]
                }
                vulnerabilities.append(vuln)

            return vulnerabilities
        except Exception as e:
            print(f"Error processing Gitleaks report: {e}")
            return []

    def normalize_semgrep(self, report_path: Path) -> List[Dict[str, Any]]:
        """Normalize Semgrep SAST report."""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)

            vulnerabilities = []
            results = data.get('results', [])

            for result in results:
                severity = result.get('extra', {}).get('severity', 'MEDIUM').upper()

                vuln = {
                    "id": result.get('check_id', 'SEMGREP-UNKNOWN'),
                    "tool": "Semgrep",
                    "category": "SAST",
                    "type": result.get('extra', {}).get('metadata', {}).get('category', 'Code Quality'),
                    "title": result.get('extra', {}).get('message', 'Security issue detected'),
                    "description": result.get('extra', {}).get('metadata', {}).get('source', result.get('extra', {}).get('message', '')),
                    "severity": severity,
                    "severity_score": self.severity_map.get(severity, 5),
                    "file": result.get('path', 'unknown'),
                    "line": result.get('start', {}).get('line', 0),
                    "code_snippet": result.get('extra', {}).get('lines', ''),
                    "rule": result.get('check_id', 'unknown'),
                    "remediation": result.get('extra', {}).get('metadata', {}).get('fix', 'Review and fix the security issue'),
                    "cwe": result.get('extra', {}).get('metadata', {}).get('cwe', []),
                    "owasp": result.get('extra', {}).get('metadata', {}).get('owasp', []),
                    "references": result.get('extra', {}).get('metadata', {}).get('references', [])
                }
                vulnerabilities.append(vuln)

            return vulnerabilities
        except Exception as e:
            print(f"Error processing Semgrep report: {e}")
            return []

    def normalize_dependency_check(self, report_path: Path) -> List[Dict[str, Any]]:
        """Normalize OWASP Dependency-Check SCA report."""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)

            vulnerabilities = []
            dependencies = data.get('dependencies', [])

            for dep in dependencies:
                if 'vulnerabilities' not in dep:
                    continue

                for vuln_data in dep.get('vulnerabilities', []):
                    severity = vuln_data.get('severity', 'MEDIUM').upper()

                    vuln = {
                        "id": vuln_data.get('name', 'CVE-UNKNOWN'),
                        "tool": "Dependency-Check",
                        "category": "SCA",
                        "type": "Vulnerable Dependency",
                        "title": f"{vuln_data.get('name')} in {dep.get('fileName', 'unknown')}",
                        "description": vuln_data.get('description', 'Known vulnerability in dependency'),
                        "severity": severity,
                        "severity_score": vuln_data.get('cvssv3', {}).get('baseScore', self.severity_map.get(severity, 5)),
                        "file": dep.get('fileName', 'unknown'),
                        "package": dep.get('fileName', 'unknown'),
                        "cvss_score": vuln_data.get('cvssv3', {}).get('baseScore', 0),
                        "cvss_vector": vuln_data.get('cvssv3', {}).get('attackVector', 'NETWORK'),
                        "cwe": [vuln_data.get('cwe', 'CWE-1035')],
                        "remediation": f"Update {dep.get('fileName')} to a patched version",
                        "references": [ref.get('url') for ref in vuln_data.get('references', [])],
                        "compliance": ["ISO 27001: A.12.6.1", "PCI-DSS: 6.2"]
                    }
                    vulnerabilities.append(vuln)

            return vulnerabilities
        except Exception as e:
            print(f"Error processing Dependency-Check report: {e}")
            return []

    def normalize_trivy(self, report_path: Path) -> List[Dict[str, Any]]:
        """Normalize Trivy container image scan report."""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)

            vulnerabilities = []
            results = data.get('Results', [])

            for result in results:
                target = result.get('Target', 'unknown')

                for vuln_data in result.get('Vulnerabilities', []):
                    severity = vuln_data.get('Severity', 'MEDIUM').upper()

                    vuln = {
                        "id": vuln_data.get('VulnerabilityID', 'TRIVY-UNKNOWN'),
                        "tool": "Trivy",
                        "category": "Container Security",
                        "type": result.get('Type', 'OS Package'),
                        "title": f"{vuln_data.get('VulnerabilityID')} in {vuln_data.get('PkgName', 'unknown')}",
                        "description": vuln_data.get('Description', vuln_data.get('Title', 'Container vulnerability')),
                        "severity": severity,
                        "severity_score": self.severity_map.get(severity, 5),
                        "package": vuln_data.get('PkgName', 'unknown'),
                        "installed_version": vuln_data.get('InstalledVersion', 'unknown'),
                        "fixed_version": vuln_data.get('FixedVersion', 'Not available'),
                        "target": target,
                        "cvss_score": vuln_data.get('CVSS', {}).get('nvd', {}).get('V3Score', 0),
                        "remediation": f"Update {vuln_data.get('PkgName')} from {vuln_data.get('InstalledVersion')} to {vuln_data.get('FixedVersion', 'latest')}",
                        "references": vuln_data.get('References', []),
                        "compliance": ["ISO 27001: A.12.6.1", "CIS Docker Benchmark"]
                    }
                    vulnerabilities.append(vuln)

            return vulnerabilities
        except Exception as e:
            print(f"Error processing Trivy report: {e}")
            return []

    def normalize_zap(self, report_path: Path) -> List[Dict[str, Any]]:
        """Normalize OWASP ZAP DAST report."""
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)

            vulnerabilities = []
            site = data.get('site', [{}])[0] if data.get('site') else {}
            alerts = site.get('alerts', [])

            for alert in alerts:
                risk = alert.get('riskdesc', 'Medium').split()[0].upper()

                vuln = {
                    "id": f"ZAP-{alert.get('pluginid', 'UNKNOWN')}",
                    "tool": "OWASP ZAP",
                    "category": "DAST",
                    "type": "Web Application Vulnerability",
                    "title": alert.get('name', 'Security issue detected'),
                    "description": alert.get('desc', 'Web application vulnerability'),
                    "severity": risk,
                    "severity_score": self.severity_map.get(risk, 5),
                    "url": alert.get('instances', [{}])[0].get('uri', 'unknown'),
                    "method": alert.get('instances', [{}])[0].get('method', 'GET'),
                    "parameter": alert.get('instances', [{}])[0].get('param', ''),
                    "attack": alert.get('instances', [{}])[0].get('attack', ''),
                    "evidence": alert.get('instances', [{}])[0].get('evidence', ''),
                    "solution": alert.get('solution', 'Review and remediate'),
                    "remediation": alert.get('solution', 'Review security best practices'),
                    "cwe": [f"CWE-{alert.get('cweid', '0')}"],
                    "owasp": [alert.get('wascid', 'OWASP-Unknown')],
                    "references": alert.get('reference', '').split('\n'),
                    "compliance": ["ISO 27001: A.14.2.1", "OWASP Top 10"]
                }
                vulnerabilities.append(vuln)

            return vulnerabilities
        except Exception as e:
            print(f"Error processing ZAP report: {e}")
            return []

    def calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk metrics."""
        if not vulnerabilities:
            return {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "risk_score": 0,
                "risk_level": "LOW"
            }

        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0
        }

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'MEDIUM').upper()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Calculate weighted risk score
        risk_score = (
            severity_counts["CRITICAL"] * 10 +
            severity_counts["HIGH"] * 5 +
            severity_counts["MEDIUM"] * 2 +
            severity_counts["LOW"] * 1
        )

        # Determine risk level
        if severity_counts["CRITICAL"] > 0:
            risk_level = "CRITICAL"
        elif severity_counts["HIGH"] > 5:
            risk_level = "HIGH"
        elif severity_counts["HIGH"] > 0:
            risk_level = "MEDIUM-HIGH"
        elif severity_counts["MEDIUM"] > 10:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "total": len(vulnerabilities),
            "critical": severity_counts["CRITICAL"],
            "high": severity_counts["HIGH"],
            "medium": severity_counts["MEDIUM"],
            "low": severity_counts["LOW"],
            "info": severity_counts["INFO"],
            "risk_score": risk_score,
            "risk_level": risk_level
        }

    def process_all_reports(self) -> Dict[str, Any]:
        """Process all security reports and create normalized output."""
        all_vulnerabilities = []
        tool_summary = {}

        # Process each tool's report
        reports = {
            'gitleaks-report.json': self.normalize_gitleaks,
            'semgrep-report.json': self.normalize_semgrep,
            'dependency-check-report.json': self.normalize_trivy,  # Trivy SCA scan (named as dependency-check for compatibility)
            'trivy-dependencies.json': self.normalize_trivy,  # Fast Trivy SCA scan
            'trivy-image-scan.json': self.normalize_trivy,    # Container image scan
            'trivy-report.json': self.normalize_trivy,         # Legacy/fallback
            'zap-report.json': self.normalize_zap
        }

        for report_file, normalizer_func in reports.items():
            report_path = self.reports_dir / report_file
            if report_path.exists():
                print(f"Processing {report_file}...")
                vulns = normalizer_func(report_path)
                all_vulnerabilities.extend(vulns)
                tool_summary[report_file.replace('-report.json', '')] = {
                    'count': len(vulns),
                    'file': str(report_file)
                }
            else:
                print(f"Report not found: {report_file}")
                tool_summary[report_file.replace('-report.json', '')] = {
                    'count': 0,
                    'file': str(report_file),
                    'status': 'not_found'
                }

        # Sort by severity score (highest first)
        all_vulnerabilities.sort(key=lambda x: x.get('severity_score', 0), reverse=True)

        # Calculate risk metrics
        risk_metrics = self.calculate_risk_score(all_vulnerabilities)

        # Create normalized output
        normalized_data = {
            "metadata": {
                "scan_date": datetime.utcnow().isoformat(),
                "total_tools": len(reports),
                "processed_tools": sum(1 for t in tool_summary.values() if t.get('status') != 'not_found'),
                "pipeline_version": "1.0.0"
            },
            "risk_metrics": risk_metrics,
            "tool_summary": tool_summary,
            "vulnerabilities": all_vulnerabilities,
            "compliance_mapping": self.generate_compliance_mapping(all_vulnerabilities)
        }

        # Write normalized output
        output_file = self.output_dir / "normalized_vulnerabilities.json"
        with open(output_file, 'w') as f:
            json.dump(normalized_data, f, indent=2)

        print(f"\nNormalized {len(all_vulnerabilities)} vulnerabilities")
        print(f"Risk Level: {risk_metrics['risk_level']}")
        print(f"Output written to: {output_file}")

        return normalized_data

    def generate_compliance_mapping(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Map vulnerabilities to compliance frameworks."""
        compliance_map = {
            "ISO_27001": [],
            "PCI_DSS": [],
            "OWASP_Top_10": [],
            "CWE_Top_25": [],
            "NIST_CSF": []
        }

        for vuln in vulnerabilities:
            # ISO 27001
            if any('ISO 27001' in str(c) for c in vuln.get('compliance', [])):
                compliance_map["ISO_27001"].append(vuln['id'])

            # PCI-DSS
            if any('PCI-DSS' in str(c) for c in vuln.get('compliance', [])):
                compliance_map["PCI_DSS"].append(vuln['id'])

            # OWASP
            if vuln.get('owasp'):
                compliance_map["OWASP_Top_10"].append(vuln['id'])

            # CWE
            if vuln.get('cwe'):
                compliance_map["CWE_Top_25"].append(vuln['id'])

        return {
            framework: {
                "count": len(vulns),
                "vulnerability_ids": list(set(vulns))[:10]  # Top 10
            }
            for framework, vulns in compliance_map.items()
        }


if __name__ == "__main__":
    normalizer = VulnerabilityNormalizer()
    normalized_data = normalizer.process_all_reports()

    print("\n" + "="*60)
    print("Vulnerability Normalization Complete")
    print("="*60)
    print(f"Total Vulnerabilities: {normalized_data['risk_metrics']['total']}")
    print(f"  Critical: {normalized_data['risk_metrics']['critical']}")
    print(f"  High: {normalized_data['risk_metrics']['high']}")
    print(f"  Medium: {normalized_data['risk_metrics']['medium']}")
    print(f"  Low: {normalized_data['risk_metrics']['low']}")
    print(f"\nOverall Risk Score: {normalized_data['risk_metrics']['risk_score']}")
    print(f"Risk Level: {normalized_data['risk_metrics']['risk_level']}")
