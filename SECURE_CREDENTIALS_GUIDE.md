# Secure Credentials Management Guide

## Overview
This guide explains how to securely manage sensitive credentials (HuggingFace tokens, API keys) without exposing them in version control.

---

## 🔐 Security Best Practices

### ✅ DO:
- Store secrets in Jenkins credentials store
- Use environment variables for local development
- Keep `.env` file in `.gitignore`
- Use credential reference syntax in code
- Rotate tokens regularly (every 90 days)
- Use read-only tokens when possible
- Document where secrets are used (but not the values)

### ❌ DON'T:
- Hardcode secrets in source code
- Commit `.env` files with real tokens
- Share tokens in Slack/Email
- Use production tokens in development
- Store tokens in public repositories
- Use tokens with more permissions than needed

---

## 📝 Secure Syntax Patterns

### Jenkins Credential Reference (Recommended)
```groovy
// In Jenkinsfile environment block:
environment {
    HF_TOKEN_CREDENTIALS_ID = 'huggingface-token'
}

// In stages:
withCredentials([string(credentialsId: HF_TOKEN_CREDENTIALS_ID, variable: 'HF_TOKEN')]) {
    sh """
        docker run --rm -e HF_TOKEN=\${HF_TOKEN} ...
    """
}
```

### Environment Variable (Local Development)
```bash
# In ~/.bashrc or ~/.zshrc (NOT in git):
export HF_TOKEN="<your-token-here>"

# Or use a .env file:
cp .env.example .env
# Edit .env and add your token
# Make sure .env is in .gitignore
```

### Docker Compose with Secrets
```yaml
# docker-compose.yml
services:
  web:
    environment:
      - HF_TOKEN=${HF_TOKEN:-}  # From host environment
    env_file:
      - .env  # File not committed to git
```

### Python Code
```python
# Good: Read from environment
import os
hf_token = os.environ.get('HF_TOKEN')
if not hf_token:
    raise ValueError("HF_TOKEN environment variable not set")

# Bad: Hardcoded
hf_token = "hf_abc123..."  # ❌ NEVER DO THIS
```

---

## 🔑 HuggingFace Token Management

### Creating a Token

1. **Visit Token Page:**
   ```
   https://huggingface.co/settings/tokens
   ```

2. **Create New Token:**
   - Click **New token**
   - **Name:** `Jenkins AI Security Pipeline - <environment>`
   - **Type:** **Read** (for inference API only)
   - **Permissions:** Inference endpoints
   - Click **Generate**

3. **Copy Token:**
   - Token format: `hf_...` (44 characters)
   - Copy immediately (won't be shown again)

4. **Store Securely:**
   - Jenkins: Add as Secret Text credential
   - Local: Add to `.env` file (not committed)
   - Password Manager: Store backup copy

### Token Rotation

Rotate tokens every 90 days:

1. Create new token (keep old one active)
2. Update Jenkins credential with new token
3. Test pipeline with new token
4. Deactivate old token on HuggingFace
5. Update local `.env` file

---

## 🚀 Setup for Different Environments

### Production (Jenkins)

```groovy
// Jenkinsfile
environment {
    HF_TOKEN_CREDENTIALS_ID = 'huggingface-token-prod'
}

stages {
    stage('AI Analysis') {
        steps {
            withCredentials([string(credentialsId: HF_TOKEN_CREDENTIALS_ID, variable: 'HF_TOKEN')]) {
                sh 'python3 real_llm_integration.py'
            }
        }
    }
}
```

**Jenkins Credential:**
- ID: `huggingface-token-prod`
- Type: Secret text
- Scope: Global

### Staging (Jenkins)

```groovy
environment {
    HF_TOKEN_CREDENTIALS_ID = 'huggingface-token-staging'
}
```

**Jenkins Credential:**
- ID: `huggingface-token-staging`
- Type: Secret text
- Scope: Global

### Local Development

```bash
# Method 1: Export in terminal session
export HF_TOKEN="hf_your_dev_token_here"
python3 real_llm_integration.py

# Method 2: Use .env file
cp .env.example .env
# Edit .env and add: HF_TOKEN=hf_your_dev_token_here
docker-compose up -d

# Method 3: Pass directly to command
HF_TOKEN="hf_your_dev_token_here" python3 real_llm_integration.py
```

---

## 📁 File Security

### .gitignore Configuration

Ensure these files are NEVER committed:

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Credentials
CREDENTIALS_PRIVATE.txt
**/secrets/
**/credentials/

# Token files
*.token
.hf_token
hf_token.txt

# IDE settings with secrets
.vscode/settings.json
.idea/workspace.xml
```

### Safe Files to Commit

```
✅ .env.example          (with placeholder values)
✅ .gitignore           (excludes sensitive files)
✅ Jenkinsfile          (uses credential references)
✅ Documentation        (with <placeholder> syntax)
```

---

## 🔍 Checking for Exposed Secrets

### Before Committing

```bash
# Check for hardcoded tokens
git diff | grep -i "hf_"
git diff | grep -i "token"

# Scan with gitleaks
docker run --rm -v $(pwd):/workspace \
    zricethezav/gitleaks:latest \
    detect --source /workspace --no-git
```

### If You Accidentally Commit a Secret

1. **Immediately Revoke the Token:**
   - Go to https://huggingface.co/settings/tokens
   - Click **Revoke** on the exposed token

2. **Remove from Git History:**
   ```bash
   # Use BFG Repo Cleaner or git filter-branch
   git filter-branch --force --index-filter \
       "git rm --cached --ignore-unmatch .env" \
       --prune-empty --tag-name-filter cat -- --all

   # Force push (⚠️ WARNING: rewrites history)
   git push origin --force --all
   ```

3. **Create New Token:**
   - Generate a new token
   - Update Jenkins credentials
   - Test the pipeline

---

## 📋 Credential Inventory

Keep track of where credentials are used:

| Credential | Type | Location | Rotation Date | Owner |
|------------|------|----------|---------------|-------|
| HuggingFace Token (Prod) | Secret Text | Jenkins: `huggingface-token` | 2025-02-01 | DevOps Team |
| HuggingFace Token (Dev) | Environment | Developer machines `.env` | 2025-02-01 | Developers |
| Docker Hub | Username/Password | Jenkins: `docker-credentials` | 2025-03-01 | DevOps Team |
| Grafana API Key | Secret Text | Jenkins: `grafana-api-key` | 2025-03-01 | DevOps Team |

---

## 🛡️ Security Checklist

Before pushing code to Git:

- [ ] No hardcoded tokens in source files
- [ ] `.env` file is in `.gitignore`
- [ ] `.env.example` has placeholder values only
- [ ] Documentation uses `<placeholder>` syntax
- [ ] Jenkinsfile uses `credentials()` or `withCredentials()`
- [ ] Run `git diff` and check for secrets
- [ ] Run gitleaks scan locally

Before deploying to production:

- [ ] Jenkins credentials configured with correct IDs
- [ ] Token has minimum required permissions (Read only)
- [ ] Token rotation schedule documented
- [ ] Backup token stored in password manager
- [ ] Team members know how to access credentials
- [ ] Incident response plan for leaked secrets

---

## 📞 Support

### If You Need Help With:

**Token Issues:**
- HuggingFace Support: https://huggingface.co/support
- Token Documentation: https://huggingface.co/docs/hub/security-tokens

**Jenkins Credentials:**
- Jenkins Credentials Plugin: https://plugins.jenkins.io/credentials/
- Jenkins Docs: https://www.jenkins.io/doc/book/using/using-credentials/

**Security Incidents:**
- Immediately revoke exposed credentials
- Contact security team
- Follow incident response procedure

---

## 🔄 Quick Reference

### Get Token from Environment
```bash
# Bash/Zsh
echo $HF_TOKEN

# Check if set
[ -z "$HF_TOKEN" ] && echo "HF_TOKEN not set" || echo "HF_TOKEN is set"
```

### Test Token Validity
```bash
curl -H "Authorization: Bearer $HF_TOKEN" \
     https://huggingface.co/api/whoami
```

### Jenkins Credential Syntax
```groovy
// Method 1: withCredentials block (recommended)
withCredentials([string(credentialsId: 'huggingface-token', variable: 'HF_TOKEN')]) {
    sh 'echo "Token is available as $HF_TOKEN"'
}

// Method 2: credentials() function
environment {
    HF_TOKEN = credentials('huggingface-token')
}

// Method 3: usernamePassword
withCredentials([usernamePassword(
    credentialsId: 'docker-credentials',
    usernameVariable: 'DOCKER_USER',
    passwordVariable: 'DOCKER_PASS'
)]) {
    sh 'docker login -u $DOCKER_USER -p $DOCKER_PASS'
}
```

---

**Last Updated:** 2025-11-09
**Version:** 1.0.0
