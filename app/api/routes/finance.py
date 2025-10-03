# app/api/routes/finance.py - Enhanced version with clearer stock name search

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List
from app.services.finance_api import FinanceAPIService, FinanceAPIError
from app.core.fastapi_users import current_active_user
from app.db.models.user import User

router = APIRouter()

@router.get("/quote/{symbol}")
async def get_stock_quote(
    symbol: str,
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get current stock quote"""
    try:
        data = FinanceAPIService.get_stock_quote(symbol)
        return {"symbol": symbol.upper(), "data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query(default="1mo", description="Period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"),
    interval: str = Query(default="1d", description="Interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get historical stock data"""
    try:
        data = FinanceAPIService.get_historical_data(symbol, period, interval)
        return {"symbol": symbol.upper(), "period": period, "interval": interval, "data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search/stocks")
async def search_stocks_by_name(
    company_name: str = Query(..., min_length=2, description="Company name to search (e.g., 'Apple', 'Microsoft', 'Tesla')"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results (1-50)"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """
    Search for stocks by company name
    
    This endpoint allows you to find stocks by searching for company names.
    Examples:
    - Search "Apple" to find AAPL
    - Search "Microsoft" to find MSFT  
    - Search "Tesla" to find TSLA
    """
    try:
        data = FinanceAPIService.search_symbols(company_name, limit)
        
        # Enhanced response with clearer messaging
        response = {
            "search_query": company_name,
            "limit": limit,
            "total_results": data.get("count", 0),
            "stocks": data.get("results", []),
            "provider": data.get("provider", "Alpha Vantage"),
            "search_tip": "Use company names like 'Apple', 'Google', 'Amazon' for best results"
        }
        
        # If no results found, provide helpful message
        if response["total_results"] == 0:
            response["message"] = f"No stocks found for company name '{company_name}'. Try different keywords or check spelling."
        
        return response
        
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search")
async def search_symbols(
    query: str = Query(..., description="Search query - can be company name or symbol"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results (1-50)"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Search for stock symbols (legacy endpoint - use /search/stocks for better experience)"""
    try:
        data = FinanceAPIService.search_symbols(query, limit)
        return {"query": query, "limit": limit, "data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/movers")
async def get_market_movers(
    market_type: str = Query(default="gainers", regex="^(gainers|losers|most_active)$", description="Type of movers"),
    count: int = Query(default=10, ge=1, le=100, description="Number of results (1-100)"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get market movers (gainers, losers, most active)"""
    try:
        data = FinanceAPIService.get_market_movers(market_type, count)
        return {"market_type": market_type, "count": count, "data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/company/{symbol}")
async def get_company_info(
    symbol: str,
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get detailed company information"""
    try:
        data = FinanceAPIService.get_company_info(symbol)
        return {"symbol": symbol.upper(), "data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/news")
async def get_market_news(
    symbol: str = Query(None, description="Stock symbol to filter news (optional)"),
    limit: int = Query(default=10, ge=1, le=50, description="Max news items (1-50)"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get market news"""
    try:
        data = FinanceAPIService.get_market_news(symbol, limit)
        return {"symbol": symbol, "limit": limit, "data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market-status")
async def get_market_status(
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get current market status"""
    try:
        data = FinanceAPIService.get_market_status()
        return {"data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/quotes/multiple")
async def get_multiple_quotes(
    symbols: List[str],
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get quotes for multiple symbols"""
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
    if len(symbols) > 100:
        raise HTTPException(status_code=400, detail="Too many symbols (max 100)")
    
    try:
        data = FinanceAPIService.get_multiple_quotes(symbols)
        return {"symbols": [s.upper() for s in symbols], "data": data}
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def finance_health():
    """Check finance service health (public endpoint)"""
    try:
        # Simple health check
        FinanceAPIService.get_stock_quote("AAPL")
        return {"status": "healthy", "provider": "alpha_vantage"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}