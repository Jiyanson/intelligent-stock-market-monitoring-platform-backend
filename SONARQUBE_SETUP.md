# SonarQube Setup Guide

This guide explains how to set up SonarQube for code quality analysis in your DevSecOps pipeline.

## Current Status

⚠️ **SonarQube is currently OPTIONAL** - The pipeline will skip SonarQube analysis if it's not configured and continue with other security scans.

## Why Use SonarQube?

SonarQube provides:
- 🐛 Bug detection
- 🔒 Security vulnerability analysis
- 💩 Code smell identification
- 📊 Technical debt tracking
- 📈 Code coverage metrics
- 🎯 Code quality gates

## Quick Setup (Docker)

### Option 1: Run SonarQube Locally

```bash
# 1. Start SonarQube server
docker run -d --name sonarqube \
  -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
  sonarqube:latest

# 2. Wait for SonarQube to start (takes 1-2 minutes)
docker logs -f sonarqube

# 3. Access SonarQube at http://localhost:9000
# Default credentials: admin / admin (change on first login)

# 4. Generate authentication token:
#    - Login to SonarQube
#    - Go to: User > My Account > Security
#    - Generate Token (name: jenkins)
#    - Copy the token

# 5. Add token to Jenkins:
#    - Go to Jenkins > Credentials > System > Global credentials
#    - Click "Add Credentials"
#    - Kind: Secret text
#    - Secret: [paste your SonarQube token]
#    - ID: sonarqube-token
#    - Description: SonarQube authentication token
```

### Option 2: Run SonarQube with PostgreSQL (Production)

```bash
# Create docker-compose.yml for SonarQube
cat > docker-compose-sonar.yml << 'EOF'
version: "3.8"

services:
  sonarqube:
    image: sonarqube:community
    depends_on:
      - sonarqube-db
    environment:
      SONAR_JDBC_URL: jdbc:postgresql://sonarqube-db:5432/sonar
      SONAR_JDBC_USERNAME: sonar
      SONAR_JDBC_PASSWORD: sonar
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_extensions:/opt/sonarqube/extensions
      - sonarqube_logs:/opt/sonarqube/logs
    ports:
      - "9000:9000"

  sonarqube-db:
    image: postgres:15
    environment:
      POSTGRES_USER: sonar
      POSTGRES_PASSWORD: sonar
      POSTGRES_DB: sonar
    volumes:
      - sonarqube_db:/var/lib/postgresql/data

volumes:
  sonarqube_data:
  sonarqube_extensions:
  sonarqube_logs:
  sonarqube_db:
EOF

# Start SonarQube
docker-compose -f docker-compose-sonar.yml up -d

# Check logs
docker-compose -f docker-compose-sonar.yml logs -f sonarqube
```

## Configuration in Jenkins

### 1. Add SonarQube Token to Jenkins

```bash
# In Jenkins UI:
# - Navigate to: Manage Jenkins > Credentials > System > Global credentials
# - Click "Add Credentials"
# - Kind: Secret text
# - Secret: [Your SonarQube token]
# - ID: sonarqube-token
# - Description: SonarQube authentication token
# - Click "Create"
```

### 2. Update Jenkinsfile (if needed)

The Jenkinsfile is already configured! Just ensure these environment variables are set:

```groovy
// In jenkinsfile (already set):
SONAR_PROJECT_KEY = 'stock-market-platform'
SONAR_HOST_URL = 'http://localhost:9000'  // Or your SonarQube server URL
SONAR_LOGIN_ID = 'sonarqube-token'        // Credential ID in Jenkins
```

### 3. For Remote SonarQube Server

If SonarQube is running on a different server:

```groovy
// Update in jenkinsfile:
SONAR_HOST_URL = 'http://your-sonarqube-server:9000'
```

## Troubleshooting

### Issue: "Failed to connect to localhost"

**Cause:** Docker container can't reach `localhost:9000`

**Solution 1 - Use host network (Linux):**
```bash
# Already implemented in Jenkinsfile using --network host
```

**Solution 2 - Use host IP:**
```bash
# Update SONAR_HOST_URL to your machine's IP:
SONAR_HOST_URL = 'http://192.168.1.100:9000'  # Replace with your IP
```

**Solution 3 - Run SonarQube in same network:**
```bash
# Create Jenkins network
docker network create jenkins-network

# Run SonarQube on the network
docker run -d --name sonarqube \
  --network jenkins-network \
  -p 9000:9000 \
  sonarqube:latest

# Update Jenkinsfile:
SONAR_HOST_URL = 'http://sonarqube:9000'
```

### Issue: "Credentials not found"

**Cause:** Jenkins credential ID doesn't match

**Solution:**
1. Check credential ID in Jenkins matches `sonarqube-token`
2. Or update `SONAR_LOGIN_ID` in Jenkinsfile to match your credential ID

### Issue: SonarQube is slow to start

**Cause:** SonarQube takes time to initialize Elasticsearch

**Solution:**
```bash
# Wait for SonarQube to be ready (check logs)
docker logs -f sonarqube

# Look for: "SonarQube is operational"
```

### Issue: Want to disable SonarQube entirely

**Solution:**
The pipeline already handles this! If SonarQube is not configured or not reachable, it will:
- Skip the SonarQube scan
- Show a helpful message
- Continue with other security scans

No changes needed!

## Project Configuration in SonarQube

After SonarQube is running:

1. **Create Project:**
   ```
   - Login to SonarQube (http://localhost:9000)
   - Click "Create Project"
   - Project key: stock-market-platform
   - Display name: Stock Market Platform
   ```

2. **Configure Quality Gate (Optional):**
   ```
   - Go to: Quality Gates
   - Create custom gate for your requirements
   - Set thresholds (e.g., Code Coverage > 80%)
   ```

3. **View Results:**
   ```
   - After pipeline runs, view results at:
     http://localhost:9000/dashboard?id=stock-market-platform
   ```

## Analysis Scope

The pipeline analyzes:
- **Source Directory:** `app/` (Python application code)
- **Language:** Python
- **Coverage Reports:** `coverage.xml` (if available)

## Benefits When Enabled

✅ **Code Quality Metrics:**
- Bugs and vulnerabilities count
- Code smells and technical debt
- Security hotspots
- Code coverage percentage

✅ **Historical Trends:**
- Track quality over time
- See improvements/regressions
- Compare branches

✅ **Quality Gates:**
- Block deployments on quality issues
- Enforce minimum standards
- Automate code reviews

## Cost Considerations

- **SonarQube Community Edition:** FREE
- **Resource Usage:** ~2GB RAM (recommended)
- **Storage:** Grows with project history

## Alternative: SonarCloud (Cloud-Hosted)

If you don't want to self-host:

1. Sign up at https://sonarcloud.io
2. Connect your GitHub repository
3. Get organization key and token
4. Update Jenkinsfile:
   ```groovy
   SONAR_HOST_URL = 'https://sonarcloud.io'
   SONAR_ORGANIZATION = 'your-org-key'
   ```

## Current Pipeline Behavior

✅ **Without SonarQube:**
- Pipeline continues successfully
- Shows helpful setup instructions
- All other security scans run normally

✅ **With SonarQube:**
- Performs code quality analysis
- Reports bugs, vulnerabilities, code smells
- Adds quality metrics to pipeline
- No impact on pipeline success (warnings only)

---

**Note:** SonarQube is completely optional. The DevSecOps pipeline includes comprehensive security scanning (Trivy, Semgrep, Gitleaks, OWASP ZAP) and will function perfectly without SonarQube.
