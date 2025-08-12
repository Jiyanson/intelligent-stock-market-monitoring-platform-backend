# app/services/finance_api.py
import requests
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class FinanceAPIError(Exception):
    """Custom exception for Finance API related errors"""
    pass

class FinanceAPIService:
    """
    Finance API Service with static methods that integrate calls to finance APIs.
    Uses requests library and handles errors as requested.
    """
    
    # API URLs from settings
    API_URLS = {
        "yfinance_quote": "https://query1.finance.yahoo.com/v8/finance/quote",
        "yfinance_chart": "https://query1.finance.yahoo.com/v8/finance/chart",
        "yfinance_search": "https://query1.finance.yahoo.com/v1/finance/search",
        "yfinance_screener": "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved",
        "yfinance_news": "https://query1.finance.yahoo.com/v1/finance/search"
    }
    
    @staticmethod
    def _get_api_url(endpoint: str) -> str:
        """Get API URL from settings or fallback to default"""
        provider = getattr(settings, 'FINANCE_API_PROVIDER', 'yfinance')
        url_key = f"{provider}_{endpoint}"
        return FinanceAPIService.API_URLS.get(url_key, FinanceAPIService.API_URLS[f"yfinance_{endpoint}"])
    
    @staticmethod
    def _make_request(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling using requests library"""
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for URL: {url}")
            raise FinanceAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for URL: {url}")
            raise FinanceAPIError("Connection error")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            raise FinanceAPIError(f"HTTP error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            raise FinanceAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise FinanceAPIError("Invalid JSON response")
    
    @staticmethod
    def get_stock_quote(symbol: str) -> Dict[str, Any]:
        """Get stock quote using API URL from settings"""
        try:
            url = FinanceAPIService._get_api_url("quote")
            params = {
                "symbols": symbol.upper(),
                "region": "US",
                "lang": "en"
            }
            return FinanceAPIService._make_request(url, params)
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get quote for {symbol}: {str(e)}")
    
    @staticmethod
    def get_historical_data(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """Get historical data using API URL from settings"""
        try:
            url = FinanceAPIService._get_api_url("chart") + f"/{symbol.upper()}"
            params = {
                "range": period,
                "interval": interval,
                "region": "US",
                "lang": "en"
            }
            return FinanceAPIService._make_request(url, params)
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get historical data for {symbol}: {str(e)}")
    
    @staticmethod
    def search_symbols(query: str, limit: int = 10) -> Dict[str, Any]:
        """Search symbols using API URL from settings"""
        try:
            url = FinanceAPIService._get_api_url("search")
            params = {
                "q": query,
                "quotesCount": limit,
                "newsCount": 0,
                "listsCount": 0
            }
            return FinanceAPIService._make_request(url, params)
        except Exception as e:
            logger.error(f"Error searching symbols for query {query}: {e}")
            raise FinanceAPIError(f"Failed to search symbols: {str(e)}")
    
    @staticmethod
    def get_market_movers(market_type: str = "gainers", count: int = 10) -> Dict[str, Any]:
        """Get market movers using API URL from settings"""
        try:
            url = FinanceAPIService._get_api_url("screener")
            screener_map = {
                "gainers": "day_gainers",
                "losers": "day_losers",
                "most_active": "most_actives"
            }
            params = {
                "formatted": "true",
                "lang": "en-US",
                "region": "US",
                "scrIds": screener_map.get(market_type, "day_gainers"),
                "count": count
            }
            return FinanceAPIService._make_request(url, params)
        except Exception as e:
            logger.error(f"Error getting market movers: {e}")
            raise FinanceAPIError(f"Failed to get market movers: {str(e)}")
    
    @staticmethod
    def get_company_news(symbol: str, limit: int = 10) -> Dict[str, Any]:
        """Get company news using API URL from settings"""
        try:
            url = FinanceAPIService._get_api_url("news")
            params = {
                "q": symbol.upper(),
                "quotesCount": 0,
                "newsCount": limit,
                "listsCount": 0
            }
            return FinanceAPIService._make_request(url, params)
        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get news for {symbol}: {str(e)}")
    
    @staticmethod
    def get_multiple_quotes(symbols: List[str]) -> Dict[str, Any]:
        """Get multiple quotes using API URL from settings"""
        try:
            if len(symbols) > 100:
                raise FinanceAPIError("Too many symbols (max 100)")
            
            url = FinanceAPIService._get_api_url("quote")
            symbol_string = ",".join([s.upper() for s in symbols])
            params = {
                "symbols": symbol_string,
                "region": "US",
                "lang": "en"
            }
            return FinanceAPIService._make_request(url, params)
        except Exception as e:
            logger.error(f"Error getting multiple quotes: {e}")
            raise FinanceAPIError(f"Failed to get multiple quotes: {str(e)}")