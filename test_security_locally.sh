#!/bin/bash
###############################################################################
# Local Security Pipeline Test Script
# Tests the AI-powered security analysis pipeline on your local machine
###############################################################################

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Security Pipeline - Local Test${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if HF_TOKEN is set
if [ -z "$HF_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  HF_TOKEN not set${NC}"
    echo -e "${YELLOW}Please set: export HF_TOKEN='<your-token-from-YOUR_TOKEN.txt>'${NC}"
    echo -e "${YELLOW}Or check YOUR_TOKEN.txt file for your token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ HuggingFace Token: ${HF_TOKEN:0:10}...${NC}"

# Step 1: Create directories
echo -e "\n${BLUE}📁 Step 1: Creating directories...${NC}"
mkdir -p reports processed ai-policies
echo -e "${GREEN}✅ Directories created${NC}"

# Step 2: Run security scans (optional - skip if you want to use test data)
read -p "Run actual security scans? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}🔍 Step 2: Running security scans...${NC}"

    # Gitleaks
    echo -e "${YELLOW}Running Gitleaks...${NC}"
    docker run --rm -v $(pwd):/workspace \
        zricethezav/gitleaks:latest \
        detect --source /workspace \
        --report-path /workspace/reports/gitleaks-report.json \
        --report-format json --no-git || echo "Gitleaks completed"

    # Semgrep
    echo -e "${YELLOW}Running Semgrep...${NC}"
    docker run --rm -v $(pwd):/src \
        returntocorp/semgrep \
        scan --config=p/python \
        --json --output=/src/reports/semgrep-report.json /src || echo "Semgrep completed"

    echo -e "${GREEN}✅ Security scans completed${NC}"
else
    echo -e "${YELLOW}⏭️  Skipping security scans, using test data...${NC}"
    python3 test_security_pipeline.py
fi

# Step 3: Normalize reports
echo -e "\n${BLUE}📊 Step 3: Normalizing vulnerability reports...${NC}"
cd reports
python3 process_vulnerabilities.py
cd ..
echo -e "${GREEN}✅ Reports normalized${NC}"

# Step 4: Generate AI insights and HTML reports
echo -e "\n${BLUE}🤖 Step 4: Generating AI-powered security analysis...${NC}"
echo -e "${YELLOW}   This may take 1-3 minutes...${NC}"
python3 real_llm_integration.py

# Step 5: Display results
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Security Analysis Complete!${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${BLUE}📊 Generated Reports:${NC}"
if [ -f "reports/comprehensive_security_report.html" ]; then
    echo -e "${GREEN}✅ Comprehensive Report:${NC} reports/comprehensive_security_report.html"
    echo -e "   file://$(pwd)/reports/comprehensive_security_report.html"
fi

if [ -f "reports/executive_summary_report.html" ]; then
    echo -e "${GREEN}✅ Executive Summary:${NC} reports/executive_summary_report.html"
    echo -e "   file://$(pwd)/reports/executive_summary_report.html"
fi

if [ -f "reports/technical_playbook_report.html" ]; then
    echo -e "${GREEN}✅ Technical Playbook:${NC} reports/technical_playbook_report.html"
    echo -e "   file://$(pwd)/reports/technical_playbook_report.html"
fi

if [ -f "ai-policies/llm_generated_policy.json" ]; then
    echo -e "${GREEN}✅ AI Policy:${NC} ai-policies/llm_generated_policy.json"
fi

echo -e "\n${BLUE}📁 All artifacts saved to:${NC}"
echo -e "   • reports/     - Security scan reports and HTML reports"
echo -e "   • processed/   - Normalized vulnerability data"
echo -e "   • ai-policies/ - AI-generated policies and insights"

# Open reports in browser (optional)
echo -e "\n${YELLOW}Would you like to open the comprehensive report in your browser? (y/N):${NC}"
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "reports/comprehensive_security_report.html"
    elif command -v open &> /dev/null; then
        open "reports/comprehensive_security_report.html"
    else
        echo -e "${YELLOW}⚠️  Could not detect browser opener. Please open manually.${NC}"
    fi
fi

echo -e "\n${GREEN}🎉 Test complete!${NC}"
echo -e "${BLUE}========================================${NC}"
