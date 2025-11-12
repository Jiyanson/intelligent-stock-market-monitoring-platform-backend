# AI-Powered Security Policy Generation Pipeline

## Overview

This project implements an intelligent stock market monitoring platform with a comprehensive security scanning and AI-driven policy generation system. The pipeline automatically scans the codebase for vulnerabilities, normalizes the findings, and generates actionable security policies using advanced AI models.

---

## Technology Stack

### Backend Framework
- **FastAPI** - Modern, high-performance Python web framework
- **Python 3.10+** - Core programming language
- **PostgreSQL** - Primary relational database
- **SQLAlchemy 2.0** - ORM with Pydantic support
- **Alembic** - Database migration tool
- **Celery + Redis** - Asynchronous task queue system

### Security Scanning Tools

#### 1. **Gitleaks** (Secrets Detection)
- **Purpose**: Detect hardcoded secrets, API keys, passwords, and credentials in source code
- **Output**: `reports/gitleaks-report.json`
- **Type**: Secrets scanning
- **Docker Image**: `zricethezav/gitleaks:latest`

#### 2. **Semgrep** (SAST - Static Application Security Testing)
- **Purpose**: Static code analysis to find security vulnerabilities and code quality issues
- **Output**: `reports/semgrep-report.json`
- **Type**: SAST (Static Application Security Testing)
- **Docker Image**: `returntocorp/semgrep`
- **Rules**: Python security ruleset (`p/python`)

#### 3. **OWASP Dependency-Check** (SCA - Software Composition Analysis)
- **Purpose**: Identify known vulnerabilities in project dependencies
- **Output**: `reports/dependency-check-report.json`
- **Type**: SCA (Software Composition Analysis)
- **Docker Image**: `owasp/dependency-check`
- **Scans**: Python packages and their known CVEs

#### 4. **Trivy** (Container Security)
- **Purpose**: Scan Docker images for OS vulnerabilities and misconfigurations
- **Output**: `reports/trivy-report.json`
- **Type**: Container security scanning
- **Docker Image**: `aquasec/trivy:latest`
- **Capabilities**: Scans for OS packages, library vulnerabilities, and IaC issues

#### 5. **OWASP ZAP** (DAST - Dynamic Application Security Testing)
- **Purpose**: Dynamic security testing of running web applications
- **Output**: `reports/zap-report.json`
- **Type**: DAST (Dynamic Application Security Testing)
- **Docker Image**: `zaproxy/zap-stable`
- **Tests**: SQL injection, XSS, CSRF, and other runtime vulnerabilities

### AI/ML Components

#### AI Models for Policy Generation

##### 1. **DeepSeek R1 Distill Llama 8B**
- **Model ID**: `deepseek-ai/DeepSeek-R1-Distill-Llama-8B`
- **Type**: Reasoning-optimized model
- **Purpose**: Generate intelligent security policies with deep reasoning
- **Strengths**: Complex reasoning, technical accuracy, structured outputs
- **Use Case**: Primary model for security policy generation

##### 2. **LLaMA 3.3 70B Instruct**
- **Model ID**: `meta-llama/Llama-3.3-70B-Instruct`
- **Type**: Instruction-tuned large language model
- **Purpose**: Alternative model for policy generation and comparison
- **Strengths**: Comprehensive responses, broad knowledge base
- **Use Case**: Comparative analysis and validation

#### AI Processing Tools
- **HuggingFace Inference API** - Model hosting and inference
- **Transformers** - ML model library
- **PyTorch** - Deep learning framework (in AI processor container)

### DevOps & CI/CD

#### Jenkins Pipeline
- **Jenkinsfile** - Declarative pipeline with 8 phases
- **Stages**:
  1. Initialization & Checkout
  2. Pre-commit Security Scanning
  3. Build (Docker images)
  4. Post-build Security (Container & dependency scanning)
  5. Quality Analysis (SonarQube)
  6. Vulnerability Normalization
  7. AI-Powered Security Policy Generation
  8. Deployment & Publishing

#### Docker
- **Main Application Image**: Built from `Dockerfile`
- **AI Processor Image**: Built from `Dockerfile.ai-processor` (cached in Docker Hub)
- **Docker Compose**: Multi-service orchestration (FastAPI, PostgreSQL, Redis, Celery)

#### Code Quality & Analysis
- **SonarQube** - Code quality and security analysis
- **Black** - Python code formatter
- **isort** - Import sorting
- **pytest** - Testing framework

#### Monitoring & Observability
- **Grafana Cloud** - Metrics visualization and dashboards
- **Prometheus** (optional) - Metrics collection

---

## AI Policy Generation Workflow

### Phase 1: Security Scanning (Tool Execution)

Each security tool runs independently and generates its own report:

```
├── reports/
│   ├── gitleaks-report.json       # Secrets scanning results
│   ├── semgrep-report.json        # SAST findings
│   ├── dependency-check-report.json  # SCA vulnerabilities
│   ├── trivy-report.json          # Container security issues
│   └── zap-report.json            # DAST results
```

**Example Raw Report Structure** (varies by tool):
- Gitleaks: List of detected secrets with file locations
- Semgrep: Security findings with rule IDs and severity
- Dependency-Check: CVE entries with CVSS scores
- Trivy: Vulnerability list with package details
- ZAP: Web application vulnerabilities with risk ratings

### Phase 2: Vulnerability Normalization

**Script**: `validate_vulnerability_pipeline.py`

**Purpose**: Consolidate all security findings into a standardized format

**Process**:
1. Read raw reports from all 5 tools
2. Parse different JSON formats
3. Normalize severity levels (CRITICAL, HIGH, MEDIUM, LOW, INFO)
4. Extract common fields: ID, title, description, severity, category, package, file
5. Calculate risk metrics and statistics
6. Generate unified vulnerability dataset

**Output File**: `processed/normalized_vulnerabilities.json`

**Required Structure**:
```json
{
  "scan_timestamp": "2025-11-12T00:00:00Z",
  "total_vulnerabilities": 156,
  "risk_metrics": {
    "total": 156,
    "critical": 5,
    "high": 23,
    "medium": 78,
    "low": 50,
    "risk_score": 289,
    "risk_level": "CRITICAL"
  },
  "by_tool": {
    "gitleaks": 3,
    "semgrep": 12,
    "dependency-check": 89,
    "trivy": 45,
    "zap": 7
  },
  "by_category": {
    "SCA": 89,
    "SAST": 12,
    "Secrets": 3,
    "Container Security": 45,
    "DAST": 7
  },
  "vulnerabilities": [
    {
      "id": "CVE-2024-12345",
      "title": "SQL Injection in Authentication Module",
      "description": "Detailed description of the vulnerability...",
      "severity": "CRITICAL",
      "category": "SAST",
      "tool": "semgrep",
      "package": "sqlalchemy",
      "file": "app/api/auth.py",
      "line": 42,
      "cvss_score": 9.8,
      "remediation": "Update to version X.Y.Z or apply patch",
      "references": [
        "https://nvd.nist.gov/vuln/detail/CVE-2024-12345"
      ]
    }
  ]
}
```

**Key Normalization Rules**:
- **Severity Mapping**: Convert all tools' severity levels to standard 5-level scale
- **Deduplication**: Merge duplicate findings from different tools
- **Categorization**: Group by vulnerability type (SCA, SAST, DAST, Secrets, Container)
- **Risk Calculation**: Weighted scoring based on severity distribution

### Phase 3: AI Report Generation

**Script**: `generate_ai_reports.py`

**Purpose**: Analyze normalized vulnerabilities and create human-readable reports

**Input**: `processed/normalized_vulnerabilities.json`

**Output**: `ai-reports/security-analysis-report.json`

**Process**:
1. Load normalized vulnerability data
2. Perform statistical analysis
3. Identify top critical issues
4. Extract actionable insights
5. Generate executive summary
6. Create detailed technical findings

**Report Contents**:
```json
{
  "generated_at": "2025-11-12T00:00:00Z",
  "summary": {
    "total_vulnerabilities": 156,
    "risk_level": "CRITICAL",
    "critical_count": 5,
    "high_count": 23,
    "packages_requiring_updates": 12,
    "files_with_issues": 34
  },
  "top_critical_issues": [
    {
      "rank": 1,
      "id": "CVE-2024-12345",
      "title": "SQL Injection in Authentication",
      "severity": "CRITICAL",
      "impact": "Remote code execution possible",
      "remediation": "Immediate patching required"
    }
  ],
  "analysis_by_category": {
    "SCA": "89 dependency vulnerabilities found...",
    "SAST": "12 code security issues detected..."
  },
  "recommended_actions": [
    "Update critical dependencies within 24 hours",
    "Review and fix SQL injection vulnerabilities",
    "Implement input validation across API endpoints"
  ]
}
```

### Phase 4: AI Security Policy Generation

#### Option A: Single Model Generation

**Script**: `generate_security_policies.py`

**Model**: DeepSeek R1 (default) or any HuggingFace model

**Input**: `processed/normalized_vulnerabilities.json`

**Output**: `ai-policies/security-policies.json`

**Process**:
1. Load normalized vulnerability data
2. Create vulnerability summary for LLM context
3. Call HuggingFace API with DeepSeek R1
4. Parse LLM response (JSON format preferred)
5. Generate fallback policies if LLM fails
6. Save structured security policies

**Environment Variables Required**:
```bash
export HF_TOKEN='your_huggingface_api_token'
export HF_MODEL='deepseek-ai/DeepSeek-R1'  # Optional, has default
```

#### Option B: Dual Model Comparison

**Script**: `dual_model_policy_generator.py`

**Models**: DeepSeek R1 vs LLaMA 3.3 70B

**Input**: `processed/normalized_vulnerabilities.json`

**Outputs**:
- `ai-policies/deepseek_generated_policy.json`
- `ai-policies/llama_generated_policy.json`
- `ai-policies/model_comparison_report.json`
- `ai-policies/security-policies.json` (best model output)

**Process**:
1. Load normalized vulnerabilities
2. Generate identical prompt for both models
3. Call DeepSeek R1 API
4. Call LLaMA 3.3 API
5. Parse both responses
6. Evaluate quality metrics:
   - Specificity score (mentions CVEs, packages, versions)
   - Relevance score (addresses actual vulnerabilities)
   - Completeness score (covers remediation, prevention, compliance)
   - Response time
7. Compare models and determine winner (70% quality, 30% speed)
8. Save individual outputs + comparison report
9. Export best model's policies as primary output

**Quality Evaluation Criteria**:
```json
{
  "quality_metrics": {
    "policy_count": 7,
    "recommendation_count": 12,
    "specificity_score": 85.5,
    "relevance_score": 92.3,
    "completeness_score": 88.7,
    "overall_quality_score": 89.2,
    "response_time": 12.4
  }
}
```

### Phase 5: Final Security Policy Output

**File**: `ai-policies/security-policies.json`

**Required Structure**:
```json
{
  "generated_at": "2025-11-12T00:00:00Z",
  "model": "DeepSeek R1",
  "model_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
  "generation_method": "dual-model-comparison",
  "quality_score": 89.2,
  "total_vulnerabilities": 156,
  "risk_metrics": {
    "total": 156,
    "critical": 5,
    "high": 23,
    "medium": 78,
    "low": 50,
    "risk_level": "CRITICAL"
  },
  "policies": [
    {
      "id": "POLICY-001",
      "title": "Immediate Critical Vulnerability Remediation",
      "description": "Address all 5 CRITICAL severity vulnerabilities within 24 hours to prevent potential security breaches",
      "priority": "CRITICAL",
      "actions": [
        "Review all CRITICAL findings with security team",
        "Create emergency remediation tickets with P0 priority",
        "Deploy security patches immediately",
        "Verify fixes with re-scan within 24 hours"
      ],
      "affected_components": ["authentication", "database", "api"],
      "compliance_frameworks": ["ISO 27001", "NIST CSF", "PCI DSS"],
      "sla": "24 hours"
    },
    {
      "id": "POLICY-002",
      "title": "High Severity Vulnerability Management",
      "description": "Remediate 23 HIGH severity vulnerabilities within 72 hours",
      "priority": "HIGH",
      "actions": [
        "Prioritize HIGH vulnerabilities by exploitability",
        "Assign remediation tasks to development team",
        "Test patches in staging environment",
        "Deploy fixes within 72-hour SLA"
      ],
      "sla": "72 hours"
    },
    {
      "id": "POLICY-003",
      "title": "Dependency Security Update Strategy",
      "description": "Update 89 vulnerable dependencies to latest secure versions",
      "priority": "HIGH",
      "actions": [
        "Enable automated dependency vulnerability scanning",
        "Update all packages with known CVEs to latest stable versions",
        "Review and test dependency updates in staging environment",
        "Implement dependency pinning for production stability",
        "Schedule weekly dependency security reviews"
      ],
      "affected_packages": [
        "sqlalchemy",
        "fastapi",
        "requests"
      ]
    },
    {
      "id": "POLICY-004",
      "title": "Container Image Hardening",
      "description": "Implement container security best practices to reduce attack surface",
      "priority": "MEDIUM",
      "actions": [
        "Use minimal base images (alpine or distroless)",
        "Run containers as non-root user",
        "Implement resource limits and security contexts",
        "Scan images before deployment with Trivy",
        "Enable Docker Content Trust for image signing"
      ]
    },
    {
      "id": "POLICY-005",
      "title": "Secure Code Development Practices",
      "description": "Address 12 code-level vulnerabilities identified by SAST tools",
      "priority": "MEDIUM",
      "actions": [
        "Implement input validation and sanitization across all API endpoints",
        "Use parameterized queries to prevent SQL injection",
        "Enable security linters (Semgrep) in IDE and pre-commit hooks",
        "Conduct mandatory code security reviews for critical changes",
        "Provide secure coding training for development team"
      ]
    }
  ],
  "recommendations": [
    "Integrate security scanning in CI/CD pipeline as mandatory quality gates",
    "Implement comprehensive security training program for development team",
    "Establish 24/7 security incident response procedures and runbooks",
    "Schedule quarterly security audits and penetration testing",
    "Maintain comprehensive security documentation and incident playbooks",
    "Enable real-time security monitoring and alerting with SIEM integration",
    "Implement security champions program within development teams",
    "Conduct regular security posture reviews with stakeholders",
    "Adopt Zero Trust security architecture principles",
    "Implement automated security testing in all deployment pipelines",
    "Establish bug bounty program for external security researchers",
    "Create security scorecard with KPIs and track improvement over time"
  ]
}
```

---

## File Requirements for AI Policy Generation

### Directory Structure

```
project-root/
├── reports/                           # Raw security scan outputs
│   ├── gitleaks-report.json
│   ├── semgrep-report.json
│   ├── dependency-check-report.json
│   ├── trivy-report.json
│   └── zap-report.json
│
├── processed/                         # Normalized data (REQUIRED)
│   └── normalized_vulnerabilities.json  # ✅ MUST EXIST for AI processing
│
├── ai-reports/                        # AI-generated analysis
│   └── security-analysis-report.json
│
├── ai-policies/                       # AI-generated policies (OUTPUT)
│   ├── security-policies.json         # Primary output
│   ├── deepseek_generated_policy.json # Dual-model output
│   ├── llama_generated_policy.json    # Dual-model output
│   └── model_comparison_report.json   # Model evaluation
│
└── (Python scripts for processing)
```

### Critical Files That Must Be Created

#### 1. **`processed/normalized_vulnerabilities.json`** ⭐ REQUIRED

**Purpose**: Unified vulnerability dataset from all security tools

**Created By**: Normalization script or manual consolidation

**Must Include**:
- `vulnerabilities` array with standardized vulnerability objects
- `risk_metrics` object with severity counts and risk scoring
- `scan_timestamp` for tracking
- `by_tool` breakdown showing contribution from each scanner
- `by_category` grouping (SCA, SAST, DAST, etc.)

**Minimum Required Fields per Vulnerability**:
```json
{
  "id": "string (CVE ID or tool-specific ID)",
  "title": "string (short description)",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
  "category": "string (SCA, SAST, DAST, Secrets, Container)",
  "tool": "string (source tool name)",
  "description": "string (detailed explanation)"
}
```

**Optional But Recommended Fields**:
```json
{
  "package": "string (affected package/dependency)",
  "file": "string (source code file path)",
  "line": "number (line number in file)",
  "cvss_score": "number (0-10 CVSS score)",
  "cwe_id": "string (CWE classification)",
  "remediation": "string (fix instructions)",
  "references": ["array of URLs"]
}
```

#### 2. **`.env` with HuggingFace Token**

```bash
# Required for AI policy generation
HF_TOKEN=hf_your_actual_huggingface_api_token_here

# Optional model override
HF_MODEL=deepseek-ai/DeepSeek-R1-Distill-Llama-8B
```

**How to Get HF_TOKEN**:
1. Create account at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create new token with "Read" permission
4. Copy token to `.env` file

---

## Running the AI Policy Generation Pipeline

### Prerequisites

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set HuggingFace Token**:
```bash
export HF_TOKEN='your_token_here'
```

3. **Ensure Required Directories Exist**:
```bash
mkdir -p reports processed ai-reports ai-policies
chmod 777 reports processed ai-reports ai-policies
```

### Step-by-Step Execution

#### Step 1: Run Security Scans (generates `reports/*.json`)

```bash
# Run via Jenkins pipeline, or manually:
docker run --rm -v ${PWD}:/workspace zricethezav/gitleaks:latest detect ...
docker run --rm -v ${PWD}:/src returntocorp/semgrep semgrep scan ...
# (see Jenkinsfile for complete commands)
```

#### Step 2: Normalize Vulnerability Data

```bash
python3 validate_vulnerability_pipeline.py
```

**Output**: `processed/normalized_vulnerabilities.json`

**Validation**: Script will report:
- Total vulnerabilities found
- Breakdown by severity
- Files and packages affected
- Data integrity checks passed/failed

#### Step 3: Generate AI Reports (Optional Analysis)

```bash
python3 generate_ai_reports.py
```

**Output**: `ai-reports/security-analysis-report.json`

#### Step 4: Generate Security Policies

**Option A: Single Model (Faster)**
```bash
python3 generate_security_policies.py
```

**Option B: Dual Model Comparison (More Comprehensive)**
```bash
python3 dual_model_policy_generator.py
```

**Output**: `ai-policies/security-policies.json`

**Expected Output Messages**:
```
======================================================================
AI-POWERED SECURITY POLICY GENERATOR
======================================================================

Loading vulnerability data...
Loaded 156 vulnerabilities

Vulnerability Summary:
Security Scan Results:
- Total Vulnerabilities: 156
- Critical: 5
- High: 23
- Medium: 78
- Low: 50
- Risk Level: CRITICAL

Attempting to generate policies using DeepSeek R1 LLM...
Calling HuggingFace API with model: deepseek-ai/DeepSeek-R1...
LLM response received, parsing...
Successfully generated policies using LLM!

Generated 7 policies and 12 recommendations
Saved to: ai-policies/security-policies.json

======================================================================
```

### Step 5: Review Generated Policies

```bash
cat ai-policies/security-policies.json | jq .
```

---

## Troubleshooting

### Issue: "No vulnerability data found"

**Cause**: `processed/normalized_vulnerabilities.json` doesn't exist

**Solution**:
1. Ensure security scans have run (check `reports/` directory)
2. Run normalization script: `python3 validate_vulnerability_pipeline.py`
3. Verify file exists: `ls -lh processed/normalized_vulnerabilities.json`

### Issue: "LLM call failed" or "API call failed with status 503"

**Cause**: HuggingFace API issue (model loading, rate limit, or invalid token)

**Solutions**:
1. **Check Token**: Verify `HF_TOKEN` is set correctly
2. **Model Loading**: Wait 30-60 seconds and retry (models need warm-up)
3. **Rate Limits**: Free tier has limits, wait or upgrade to Pro
4. **Fallback Mode**: Script will use intelligent rule-based policies if LLM fails

### Issue: Empty or poor quality policies generated

**Cause**: LLM response parsing failed or insufficient vulnerability data

**Solutions**:
1. Check `normalized_vulnerabilities.json` has meaningful data
2. Ensure vulnerabilities have `severity`, `category`, and `description` fields
3. Review LLM raw response in debug logs
4. Try dual-model comparison for better results

### Issue: "Permission denied" when writing files

**Solution**:
```bash
chmod -R 777 processed ai-reports ai-policies
```

---

## Integration with Jenkins Pipeline

The Jenkins pipeline (`Jenkinsfile`) automates this entire workflow:

### Phase 6: Normalization & Reporting
```groovy
stage('Generate AI Security Reports') {
    steps {
        sh 'python3 generate_ai_reports.py'
    }
}
```

### Phase 7: AI Policy Generation
```groovy
stage('AI Security Policy Generation') {
    steps {
        withCredentials([string(credentialsId: HF_TOKEN_CREDENTIALS_ID, variable: 'HF_TOKEN')]) {
            sh '''
                docker run --rm \
                  -v ${PWD}:/workspace \
                  -e HF_TOKEN=${HF_TOKEN} \
                  ${AI_PROCESSOR_IMAGE}:latest \
                  python3 /workspace/dual_model_policy_generator.py
            '''
        }
    }
}
```

**Pipeline automatically**:
1. Runs all security scans in parallel
2. Normalizes vulnerability data
3. Generates AI reports
4. Creates security policies using dual-model comparison
5. Archives all outputs as build artifacts
6. Pushes results to monitoring dashboards

---

## Best Practices

### Normalization
- ✅ Always validate input data format before normalization
- ✅ Implement deduplication logic (same CVE from multiple tools)
- ✅ Map all severity levels to standard 5-tier scale
- ✅ Include metadata (scan timestamp, tool versions)
- ✅ Calculate meaningful risk scores

### AI Policy Generation
- ✅ Use dual-model comparison for production deployments
- ✅ Validate LLM outputs (check for hallucinations)
- ✅ Always have intelligent fallback policies
- ✅ Log all LLM interactions for debugging
- ✅ Monitor API costs and rate limits
- ✅ Version control generated policies for tracking changes over time

### Security
- ✅ Never commit `HF_TOKEN` to version control
- ✅ Use Jenkins credentials management for tokens
- ✅ Rotate API tokens regularly
- ✅ Implement least-privilege access to AI APIs
- ✅ Sanitize vulnerability data before sending to external APIs

---

## Output Artifacts

After successful pipeline execution, you should have:

```
✅ reports/               (5 raw security scan reports)
✅ processed/             (1 normalized vulnerability dataset)
✅ ai-reports/            (1 AI-generated analysis report)
✅ ai-policies/           (3-4 policy files including comparison)
```

**Archived in Jenkins**:
- All JSON reports
- Generated policies
- Model comparison results
- HTML formatted reports (if HTML generator is used)

**Pushed to Grafana**:
- Vulnerability count metrics
- Risk score trends
- Policy compliance status
- Scan execution times

---

## References

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference)
- [DeepSeek R1 Model Card](https://huggingface.co/deepseek-ai/DeepSeek-R1)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Security Tools
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Semgrep](https://semgrep.dev/)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [Trivy](https://trivy.dev/)
- [OWASP ZAP](https://www.zaproxy.org/)

### Project Files
- `AI-PROCESSOR-SETUP.md` - AI container setup instructions
- `JENKINS_SETUP.md` - Jenkins configuration guide
- `SECURITY_ANALYSIS_README.md` - Security analysis details
- `QUICK_START.md` - Quick start guide

---

## Support

For issues or questions:
1. Check existing documentation in the project root
2. Review Jenkins pipeline logs
3. Validate input/output file formats
4. Check HuggingFace API status
5. Review security scan tool documentation

---

**Last Updated**: 2025-11-12
**Version**: 1.0
**Maintained By**: Security & DevOps Team
