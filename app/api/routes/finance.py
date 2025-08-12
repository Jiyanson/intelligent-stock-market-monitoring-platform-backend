# app/api/routes/finance.py
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

@router.get("/search")
async def search_symbols(
    query: str = Query(..., description="Search query"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results (1-50)"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Search for stock symbols"""
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

@router.get("/news/{symbol}")
async def get_company_news(
    symbol: str,
    limit: int = Query(default=10, ge=1, le=50, description="Max news items (1-50)"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get company news"""
    try:
        data = FinanceAPIService.get_company_news(symbol, limit)
        return {"symbol": symbol.upper(), "limit": limit, "data": data}
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
        return {"status": "healthy", "provider": "yfinance"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}