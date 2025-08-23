# Alpha Vantage Finance API - Quick Start Guide

---

## Prerequisites
- Finance API service running locally or accessible remotely (default URL: `http://localhost:8000`)  
- `curl` installed on your system  
- Access to a terminal/command prompt  
- Internet access if the service fetches live data from Alpha Vantage  
- Alpha Vantage API key configured in your service environment (usually via `.env` or settings)  

---

## Step-by-step Commands

### 1. Register a new user (run once)
```bash
# Create a new user account - run this only once
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com", "password": "testpassword123", "first_name": "Test", "last_name": "User"}'
```
*Note: If user already exists, you can ignore the error message.*

### 2. Login to get authentication token
```bash
# Login with your credentials to get access token
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@example.com&password=testpassword123"
```
*Copy the "access_token" value from the JSON response.*

### 3. Export your token for easy use
```bash
# Replace YOUR_TOKEN_HERE with the actual token string (without quotes)
export TOKEN="YOUR_TOKEN_HERE"

# Verify token is set correctly
echo "Token set: $TOKEN"
```

---

## API Endpoints

### Health Check (No Authentication Required)
```bash
# Check if the service is running
curl -X GET "http://localhost:8000/api/v1/finance/health"
```

### Stock Quotes

#### Get Single Stock Quote
```bash
# Get current quote for Apple (AAPL)
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/quote/AAPL"

# Get quote for Microsoft (MSFT)
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/quote/MSFT"

# Get quote for Google (GOOGL)
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/quote/GOOGL"
```

#### Get Multiple Stock Quotes
```bash
# Get quotes for multiple stocks at once (AAPL and MSFT)
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "http://localhost:8000/api/v1/finance/quotes/multiple" \
  -d '["AAPL", "MSFT"]'

# Get quotes for tech giants
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "http://localhost:8000/api/v1/finance/quotes/multiple" \
  -d '["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]'
```

### Symbol Search
```bash
# Search for symbols matching 'Apple' (limit to 3 results)
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/search?query=Apple&limit=3"

# Search for 'Microsoft' with more results
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/search?query=Microsoft&limit=5"

# Search for 'Tesla'
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/search?query=Tesla&limit=3"
```

### Company Information
```bash
# Get detailed company overview for Microsoft
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/company/MSFT"

# Get company info for Apple
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/company/AAPL"

# Get company info for Amazon
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/company/AMZN"
```

### Historical Data
```bash
# Get 1 month of daily data for Google
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/historical/GOOGL?period=1mo&interval=1d"

# Get 3 months of daily data for Apple
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/historical/AAPL?period=3mo&interval=1d"

# Get 1 year of weekly data for Tesla
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/historical/TSLA?period=1y&interval=1wk"
```

### Market News
```bash
# Get latest market news (limit to 3 articles)
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/news?limit=3"

# Get more news articles
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/news?limit=10"

# Get news with specific topics (if supported)
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/news?limit=5&topic=technology"
```

### Market Status
```bash
# Check current market status (open/closed)
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/market-status"
```

---

## Common Usage Patterns

### Quick Portfolio Check
```bash
# Check your portfolio stocks in one go
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "http://localhost:8000/api/v1/finance/quotes/multiple" \
  -d '["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]'
```

### Research New Stock
```bash
# Research workflow for a new stock (example: Netflix)
SYMBOL="NFLX"

# 1. Search to confirm symbol
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/search?query=Netflix&limit=3"

# 2. Get current quote
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/quote/$SYMBOL"

# 3. Get company details
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/company/$SYMBOL"

# 4. Get historical data
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/historical/$SYMBOL?period=6mo&interval=1d"
```

### Save Data to Files
```bash
# Save quotes to file for analysis
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "http://localhost:8000/api/v1/finance/quotes/multiple" \
  -d '["AAPL", "MSFT", "GOOGL"]' \
  -o portfolio_quotes.json

# Save historical data to file
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/historical/AAPL?period=1y&interval=1d" \
  -o aapl_historical.json

# Pretty print saved JSON
cat portfolio_quotes.json | python -m json.tool
```

---

## Troubleshooting

### Check Service Status
```bash
# Test if service is running
curl -I "http://localhost:8000/api/v1/finance/health"

# Get detailed health info
curl -X GET "http://localhost:8000/api/v1/finance/health"
```

### Authentication Issues
```bash
# Verify your token is set
echo "Current token: $TOKEN"

# Test token with simple request
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/market-status"

# If token expired, login again
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@example.com&password=testpassword123"
```

### Verbose Debugging
```bash
# Use -v flag for detailed request/response info
curl -v -H "Authorization: Bearer $TOKEN" \
  -X GET "http://localhost:8000/api/v1/finance/quote/AAPL"
```

---

## Environment Variables Setup

For easier management, create a script file:

### setup_env.sh
```bash
#!/bin/bash
# Alpha Vantage API Environment Setup

export API_BASE_URL="http://localhost:8000"
export API_EMAIL="testuser@example.com"
export API_PASSWORD="testpassword123"

# Login and get token
echo "Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$API_EMAIL&password=$API_PASSWORD")
S
# Extract token (requires jq)
export TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

echo "Token set: $TOKEN"
echo "Ready to use Alpha Vantage Finance API!"

# Test connection
curl -H "Authorization: Bearer $TOKEN" \
  -X GET "$API_BASE_URL/api/v1/finance/market-status"
```

Usage:
```bash
chmod +x setup_env.sh
source setup_env.sh
```

---

## API Response Examples

### Quote Response
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "change": 2.50,
  "change_percent": 1.69,
  "volume": 50123456,
  "timestamp": "2024-01-15T16:00:00Z"
}
```

### Historical Data Response
```json
{
  "symbol": "AAPL",
  "data": [
    {
      "date": "2024-01-15",
      "open": 148.50,
      "high": 152.00,
      "low": 147.25,
      "close": 150.25,
      "volume": 50123456
    }
  ]
}
```

---

## Notes

- **Service URL**: Default is `http://localhost:8000` - change if your service runs elsewhere
- **Token Expiry**: JWT tokens expire, re-login if you get 401 errors  
- **Rate Limits**: Alpha Vantage has API rate limits, the service may cache responses
- **Data Accuracy**: Market data may have delays based on your Alpha Vantage plan
- **Error Handling**: Check HTTP status codes and response messages for issues

---

