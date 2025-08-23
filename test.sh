# Manual cURL Commands for Stock Search API
# Copy and paste these commands one by one in your terminal

# ===========================================
# STEP 1: Register a new user (run once only)
# ===========================================

curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'

# Expected response: User registration success or "user already exists" error (both are fine)

# ===========================================
# STEP 2: Login to get authentication token
# ===========================================

curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword123"

# Expected response: {"access_token":"eyJ0eXAiOiJKV1QiLCJhbGc...","token_type":"bearer"}
# COPY THE access_token VALUE (the long string after "access_token":")

# ===========================================
# STEP 3: Set your token as a variable (REPLACE WITH YOUR ACTUAL TOKEN)
# ===========================================

export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0ODgyODZiMC01M2RiLTQ3N2YtYTgwMy0wYzBjZTBlZDJmZTEiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc1NTk4ODQzMn0.3ofsmCDx0Hr5gDaFtmqK5JJxF2mjTrtWsevizWhpJcY"

# Alternative: Replace YOUR_ACTUAL_TOKEN_HERE with the token from step 2
# Example: export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# ===========================================
# STEP 4: Test stock search endpoints
# ===========================================

# Search for Apple
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/finance/search/stocks?company_name=Apple&limit=3"

# Search for Microsoft
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/finance/search/stocks?company_name=Microsoft&limit=3"

# Search for Tesla
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/finance/search/stocks?company_name=Tesla&limit=3"

# Search for Google
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/finance/search/stocks?company_name=Google&limit=3"

# ===========================================
# BONUS: Test other endpoints
# ===========================================

# Get stock quote for Apple
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/finance/quote/AAPL"

# Check market status
curl -H "Authorization: Bearer $TOKEN"