# app/api/routes/finance.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from app.services.finance_api import FinanceAPIService, FinanceAPIError
from app.core.fastapi_users import current_active_user
from app.db.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/quote/{symbol}")
async def get_stock_quote(
    symbol: str,
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get current stock quote for a symbol."""
    try:
        data = FinanceAPIService.get_stock_quote(symbol)
        return {
            "symbol": symbol.upper(),
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for symbol {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query(default="1mo", description="Period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"),
    interval: str = Query(default="1d", description="Interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get historical stock data."""
    try:
        data = FinanceAPIService.get_historical_data(symbol, period, interval)
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for historical data {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for historical data {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search")
async def search_symbols(
    query: str = Query(..., description="Search query for stock symbols"),
    limit: int = Query(default=10, description="Maximum number of results"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Search for stock symbols."""
    try:
        data = FinanceAPIService.search_symbols(query, limit)
        return {
            "query": query,
            "limit": limit,
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for symbol search {query}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for symbol search {query}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/movers")
async def get_market_movers(
    market_type: str = Query(default="gainers", description="Type: gainers, losers, most_active"),
    count: int = Query(default=10, description="Number of results"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get market movers (gainers, losers, most active)."""
    valid_types = ["gainers", "losers", "most_active"]
    if market_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid market_type. Must be one of: {', '.join(valid_types)}"
        )
    
    try:
        data = FinanceAPIService.get_market_movers(market_type, count)
        return {
            "market_type": market_type,
            "count": count,
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for market movers: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for market movers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/company/{symbol}")
async def get_company_info(
    symbol: str,
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get company information and profile."""
    try:
        data = FinanceAPIService.get_company_info(symbol)
        return {
            "symbol": symbol.upper(),
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for company info {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for company info {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/news")
async def get_market_news(
    symbol: Optional[str] = Query(default=None, description="Stock symbol to filter news (optional)"),
    limit: int = Query(default=10, description="Maximum number of news items"),
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get market news, optionally filtered by symbol."""
    try:
        data = FinanceAPIService.get_market_news(symbol, limit)
        return {
            "symbol": symbol,
            "limit": limit,
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for news: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for news: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market-status")
async def get_market_status(
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get current market status (open/closed)."""
    try:
        data = FinanceAPIService.get_market_status()
        return {
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for market status: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for market status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Public endpoint (no authentication required)
@router.post("/quotes/multiple")
async def get_multiple_quotes(
    symbols: List[str],
    user: User = Depends(current_active_user)
) -> Dict[str, Any]:
    """Get quotes for multiple symbols at once."""
    if not symbols or len(symbols) == 0:
        raise HTTPException(status_code=400, detail="No symbols provided")
    
    if len(symbols) > 100:  # Reasonable limit
        raise HTTPException(status_code=400, detail="Too many symbols (max 100)")
    
    try:
        data = FinanceAPIService.get_multiple_quotes(symbols)
        return {
            "symbols": symbols,
            "data": data,
            "requested_by": user.email
        }
    except FinanceAPIError as e:
        logger.error(f"Finance API error for multiple quotes: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for multiple quotes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def finance_service_health() -> Dict[str, Any]:
    """Check finance service health."""
    try:
        # Simple health check - try to get market status
        FinanceAPIService.get_market_status()
        return {
            "status": "healthy",
            "provider": "yfinance",
            "message": "Finance API service is operational"
        }
    except FinanceAPIError as e:
        return {
            "status": "unhealthy",
            "provider": "yfinance",
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "provider": "yfinance",
            "error": "Unexpected error occurred"
        }