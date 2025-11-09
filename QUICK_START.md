# Quick Start Guide - AI Security Pipeline

## Prerequisites

### Get Your HuggingFace Token
1. Visit: https://huggingface.co/settings/tokens
2. Click **New token**
3. Name: `Jenkins AI Security Pipeline`
4. Type: **Read**
5. Click **Generate**
6. **Copy the token** (starts with `hf_...`)

## 3-Step Jenkins Setup

### Step 1: Add Token to Jenkins (2 minutes)
1. Open Jenkins → `Manage Jenkins` → `Manage Credentials`
2. Click `(global)` → `Add Credentials`
3. Fill in:
   - **Kind:** Secret text
   - **Secret:** `<paste your HuggingFace token here>`
   - **ID:** `huggingface-token` (⚠️ must be exact)
4. Click **OK**

### Step 2: Push Code to Git
```bash
git add .
git commit -m "Add AI security analysis pipeline"
git push origin main
```

### Step 3: Run Pipeline
1. Go to your Jenkins job
2. Click **Build Now**
3. Wait 10-15 minutes
4. Download HTML reports from **Build Artifacts**

## Expected Output

After the build completes, you'll have:

### 📊 For Technical Teams:
- `comprehensive_security_report.html` - Complete analysis with all details

### 📈 For Leadership:
- `executive_summary_report.html` - Non-technical business summary

### 🔧 For DevOps:
- `technical_playbook_report.html` - Step-by-step remediation guide

### 🤖 For Automation:
- `llm_generated_policy.json` - Machine-readable AI insights

## Files Updated

✅ `Dockerfile` - Added security dependencies
✅ `docker-compose.yml` - Added volumes and HF_TOKEN
✅ `jenkinsfile` - Enhanced AI generation stage

## Docker Compose Usage

If you want to use the token locally:

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your HuggingFace token:
# HF_TOKEN=<your-token-here>

# Start services
export HF_TOKEN=<your-token-here>
docker-compose up -d
```

## Troubleshooting

### "HF_TOKEN not configured"
- Check credential ID is exactly: `huggingface-token`
- Verify token is valid (starts with `hf_`)
- Test token: Visit https://huggingface.co/settings/tokens and check status

### "AI scripts not found"
- Ensure these files exist:
  - `real_llm_integration.py`
  - `llm_integration.py`
  - `html_report_generator.py`
  - `requirements-security.txt`

### "Model loading timeout"
- Normal on first run
- Pipeline auto-retries
- Wait 30-60 seconds

## Need More Help?

- Detailed setup: See `JENKINS_SETUP.md`
- Full documentation: See `SECURITY_ANALYSIS_README.md`
- All changes: See `DEPLOYMENT_UPDATES_SUMMARY.md`

---

**Ready to deploy! 🚀**
