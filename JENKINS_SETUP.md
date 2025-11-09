# Jenkins Setup Guide for AI Security Pipeline

## Prerequisites
- Jenkins installed and running
- Docker installed on Jenkins agent
- Access to Jenkins credential management

## Step 1: Configure HuggingFace Token in Jenkins

### Option A: Via Jenkins UI (Recommended)

1. **Navigate to Jenkins Dashboard**
   - Go to `Manage Jenkins` → `Manage Credentials`

2. **Select Domain**
   - Click on `(global)` domain

3. **Add New Credential**
   - Click `Add Credentials`
   - **Kind:** Secret text
   - **Scope:** Global
   - **Secret:** `<paste-your-huggingface-token-here>`
   - **ID:** `huggingface-token` (⚠️ must match exactly)
   - **Description:** HuggingFace API Token for AI Security Analysis (DeepSeek R1)
   - Click **OK**

> **Where to get token:** Visit https://huggingface.co/settings/tokens and create a new **Read** token

### Option B: Via Jenkins CLI

```bash
# Create a credential XML file
cat > hf-token-credential.xml <<EOF
<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
  <scope>GLOBAL</scope>
  <id>huggingface-token</id>
  <description>HuggingFace API Token for AI Security Analysis</description>
  <username>hf_token</username>
  <password>\${HF_TOKEN}</password>
</com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
EOF

# Set your token first
export HF_TOKEN="<your-huggingface-token-here>"

# Import to Jenkins
java -jar jenkins-cli.jar -s http://localhost:8080/ create-credentials-by-xml system::system::jenkins _ < hf-token-credential.xml
```

### Option C: Environment Variable (Alternative)

If you prefer not to use Jenkins credentials, you can set an environment variable:

```groovy
// In jenkinsfile, add to environment block:
environment {
    HF_TOKEN = credentials('huggingface-token') // Recommended: use credential reference
    // OR (less secure):
    // HF_TOKEN = "${env.HF_TOKEN}" // from system environment variable
}
```

**⚠️ Warning:** Using environment variables is less secure. Always prefer Jenkins credentials.

---

## Step 2: Verify Other Required Credentials

### Docker Hub Credentials
- **ID:** `2709ba15-3bf5-42b4-a41e-e2ae435f4951` (already configured)
- **Type:** Username and Password
- **Username:** `michoc`
- **Password:** Your Docker Hub password

### Grafana API Key
- **ID:** `0acea52d-149d-4dce-affc-6e88b440471e` (already configured)
- **Type:** Secret text
- **Secret:** Your Grafana API key

### GitHub Credentials (optional)
- **ID:** `github-credentials`
- **Type:** Username and Password or Personal Access Token

---

## Step 3: Create Jenkins Pipeline Job

1. **New Item**
   - Name: `Stock-Market-Platform-Security-Pipeline`
   - Type: Pipeline
   - Click OK

2. **Configure Pipeline**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/Jiyanson/intelligent-stock-market-monitoring-platform-backend.git`
   - **Credentials:** Select your GitHub credentials
   - **Branch:** `*/main`
   - **Script Path:** `jenkinsfile`

3. **Save Configuration**

---

## Step 4: Run the Pipeline

1. **Build Now**
   - Click "Build Now" on the job page
   - Monitor the console output

2. **Expected Stages:**
   ```
   ✅ Checkout
   ✅ Prepare Directories
   ✅ Gitleaks - Secrets Scanning
   ✅ Semgrep - SAST
   ✅ Dependency-Check - SCA
   ✅ Build Docker Image
   ✅ Run Tests
   ✅ Code Quality Checks
   ✅ Trivy - Container Image Scan
   ✅ Push to Docker Hub
   ✅ Deploy with Docker Compose
   ✅ OWASP ZAP - DAST
   ✅ Normalize Reports
   ✅ AI Security Policy Generation ⬅️ NEW!
   ✅ Archive Reports
   ✅ Grafana Notification
   ```

3. **Access Reports**
   - After build completes, go to **Build Artifacts**
   - Download generated reports:
     - `reports/comprehensive_security_report.html`
     - `reports/executive_summary_report.html`
     - `reports/technical_playbook_report.html`
     - `ai-policies/llm_generated_policy.json`

---

## Step 5: Verify AI Security Analysis

### Check Console Output

Look for these messages in the build log:

```
🤖 Generating AI-based security policies and HTML reports...
✅ All AI security scripts found
🤖 Initializing AI Security Analysis System...
   Using DeepSeek R1 and Llama models via HuggingFace
📊 Generating Executive Summary (for C-level)...
📋 Generating Remediation Policy...
🛠️ Generating Technical Remediation Playbook...
⚠️ Performing Risk Assessment...
✅ Generating Compliance Traceability Mapping...
📄 Generating HTML Reports
✅ AI-powered security analysis complete!
```

### Verify Generated Artifacts

```bash
# From Jenkins workspace or build artifacts:
ls -lh reports/
# Expected files:
# - comprehensive_security_report.html
# - executive_summary_report.html
# - technical_playbook_report.html
# - gitleaks-report.json
# - semgrep-report.json
# - dependency-check-report.json
# - trivy-report.json
# - zap-report.json

ls -lh ai-policies/
# Expected file:
# - llm_generated_policy.json
```

---

## Troubleshooting

### Issue: HuggingFace Token Not Found

**Error Message:**
```
⚠️ HuggingFace token credential not configured. Skipping AI policy generation.
```

**Solution:**
- Verify credential ID is exactly: `huggingface-token`
- Check that the credential is in the Global domain
- Ensure the token is valid: https://huggingface.co/settings/tokens

### Issue: Model Loading Timeout

**Error Message:**
```
Error: HTTP 503 - Model is loading
```

**Solution:**
- This is normal for the first request to a model
- The pipeline will automatically retry (up to 3 times with backoff)
- Wait 20-60 seconds and the model will load

### Issue: AI Scripts Not Found

**Error Message:**
```
⚠️ AI integration scripts not found
```

**Solution:**
- Ensure these files are in your repository root:
  - `real_llm_integration.py`
  - `llm_integration.py`
  - `html_report_generator.py`
  - `requirements-security.txt`

### Issue: Empty Reports

**Solution:**
- Check that security scans are producing JSON output
- Verify `reports/process_vulnerabilities.py` exists
- Check Docker volume mounts in pipeline

---

## Security Best Practices

1. **Rotate Tokens Regularly**
   - Update HuggingFace token every 90 days
   - Use Jenkins credential rotation features

2. **Limit Token Permissions**
   - Use Read-only tokens when possible
   - HuggingFace tokens should only have inference permissions

3. **Audit Logs**
   - Monitor Jenkins logs for unauthorized credential access
   - Enable audit logging for credential usage

4. **Backup Credentials**
   - Export Jenkins credentials regularly
   - Store backups in secure vault (e.g., HashiCorp Vault)

---

## Additional Configuration

### Email Notifications (Optional)

Add to `post` section in jenkinsfile:

```groovy
post {
    success {
        emailext (
            subject: "✅ Security Pipeline Success - Build ${env.BUILD_NUMBER}",
            body: "AI security analysis completed. View reports: ${env.BUILD_URL}artifact/",
            to: "your-email@example.com"
        )
    }
}
```

### Slack Notifications (Optional)

```groovy
post {
    success {
        slackSend(
            color: 'good',
            message: "✅ Security pipeline completed\nReports: ${env.BUILD_URL}artifact/"
        )
    }
}
```

---

## Next Steps

1. ✅ Configure HuggingFace token credential
2. ✅ Run the pipeline
3. ✅ Review generated security reports
4. ✅ Share reports with your team
5. ✅ Set up automated scheduling (e.g., daily/weekly scans)
6. ✅ Integrate with your incident response workflow

---

**For more information, see:**
- [SECURITY_ANALYSIS_README.md](./SECURITY_ANALYSIS_README.md) - Complete security pipeline documentation
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
