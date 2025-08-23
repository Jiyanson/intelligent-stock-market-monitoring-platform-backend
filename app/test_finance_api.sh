#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"
EMAIL="test@example.com"
PASSWORD="testpassword123"

echo -e "${YELLOW}=== Testing Finance API ===${NC}\n"

# Check if server is running
echo -e "${BLUE}0. Checking if server is running...${NC}"
SERVER_CHECK=$(curl -s "$BASE_URL/" || echo "FAILED")
if [[ $SERVER_CHECK == "FAILED" ]]; then
    echo -e "${RED}❌ Server is not running at $BASE_URL${NC}"
    echo -e "${YELLOW}💡 Make sure to run: docker-compose up or uvicorn app.main:app --reload${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}\n"

# Step 1: Try registration (multiple formats)
echo -e "${BLUE}1. Attempting user registration...${NC}"

# Try minimal format first
echo -e "${YELLOW}   Trying minimal registration format...${NC}"
REG_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

echo -e "${YELLOW}   Registration response: $REG_RESPONSE${NC}"

# Check if registration was successful
if [[ $REG_RESPONSE == *"error"* ]] || [[ $REG_RESPONSE == *"detail"* ]]; then
    echo -e "${YELLOW}   Registration may have failed or user already exists. Proceeding with login...${NC}"
else
    echo -e "${GREEN}   ✅ Registration successful!${NC}"
fi

# Step 2: Try login (multiple formats)
echo -e "\n${BLUE}2. Attempting login...${NC}"

# Try JSON format first
echo -e "${YELLOW}   Trying JSON login format...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/jwt/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

echo -e "${YELLOW}   JSON Login response: $LOGIN_RESPONSE${NC}"

# Extract token from JSON response
TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'access_token' in data:
        print(data['access_token'])
    else:
        print('')
except:
    print('')
" 2>/dev/null)

# If JSON login failed, try form data
if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}   Trying form data login format...${NC}"
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/jwt/login" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=$EMAIL&password=$PASSWORD")
    
    echo -e "${YELLOW}   Form Login response: $LOGIN_RESPONSE${NC}"
    
    TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'access_token' in data:
        print(data['access_token'])
    else:
        print('')
except:
    print('')
" 2>/dev/null)
fi

# Check if we got a token
if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get authentication token${NC}"
    echo -e "${YELLOW}💡 Try accessing the API docs at: $BASE_URL/docs${NC}"
    echo -e "${YELLOW}💡 Or check your database and make sure the user table exists${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Login successful! Token obtained.${NC}\n"

# Step 3: Test finance endpoints
echo -e "${BLUE}3. Testing finance endpoints...${NC}\n"

# Health check (no auth required)
echo -e "${YELLOW}📊 Testing health endpoint:${NC}"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/v1/finance/health")
echo $HEALTH_RESPONSE | python3 -m json.tool 2>/dev/null || echo $HEALTH_RESPONSE
echo ""

# Stock quote
echo -e "${YELLOW}📈 Testing stock quote (AAPL):${NC}"
QUOTE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/finance/quote/AAPL")
echo $QUOTE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $QUOTE_RESPONSE
echo ""

# Symbol search
echo -e "${YELLOW}🔍 Testing symbol search:${NC}"
SEARCH_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/finance/search?query=Apple&limit=3")
echo $SEARCH_RESPONSE | python3 -m json.tool 2>/dev/null || echo $SEARCH_RESPONSE
echo ""

# Market movers
echo -e "${YELLOW}📊 Testing market movers:${NC}"
MOVERS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/finance/movers?market_type=gainers&count=3")
echo $MOVERS_RESPONSE | python3 -m json.tool 2>/dev/null || echo $MOVERS_RESPONSE
echo ""

# Multiple quotes
echo -e "${YELLOW}📈 Testing multiple quotes:${NC}"
MULTIPLE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/finance/quotes/multiple" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '["AAPL", "GOOGL"]')
echo $MULTIPLE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $MULTIPLE_RESPONSE
echo ""

echo -e "${GREEN}🎉 Testing Complete!${NC}"
echo -e "${BLUE}💡 Access the interactive API docs at: $BASE_URL/docs${NC}"