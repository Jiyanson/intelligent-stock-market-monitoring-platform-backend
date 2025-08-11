# app/services/finance_api.py
import yfinance as yf
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class FinanceAPIError(Exception):
    """Custom exception for Finance API related errors"""
    pass

class FinanceAPIService:
    """
    Finance API Service using yfinance library for stock market data.
    Provides static methods for various financial data operations.
    """
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = 30
    
    @staticmethod
    def _validate_symbol(symbol: str) -> str:
        """Validate and format stock symbol."""
        if not symbol or not isinstance(symbol, str):
            raise FinanceAPIError("Invalid symbol provided")
        return symbol.upper().strip()
    
    @staticmethod
    def _handle_yfinance_error(symbol: str, operation: str) -> None:
        """Handle common yfinance errors."""
        logger.error(f"YFinance error during {operation} for symbol {symbol}")
        raise FinanceAPIError(f"Failed to {operation} for symbol {symbol}")
    
    @staticmethod
    def get_stock_quote(symbol: str) -> Dict[str, Any]:
        """
        Get current stock quote for a symbol using yfinance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            
        Returns:
            Dictionary containing stock quote data
            
        Raises:
            FinanceAPIError: If request fails or symbol not found
        """
        try:
            symbol = FinanceAPIService._validate_symbol(symbol)
            ticker = yf.Ticker(symbol)
            
            # Get current info
            info = ticker.info
            if not info or 'regularMarketPrice' not in info:
                raise FinanceAPIError(f"No data found for symbol {symbol}")
            
            # Get fast info for real-time data
            try:
                fast_info = ticker.fast_info
                current_price = fast_info.last_price if hasattr(fast_info, 'last_price') else info.get('regularMarketPrice')
            except:
                current_price = info.get('regularMarketPrice')
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "previous_close": info.get('previousClose'),
                "open": info.get('regularMarketOpen'),
                "day_high": info.get('regularMarketDayHigh'),
                "day_low": info.get('regularMarketDayLow'),
                "volume": info.get('regularMarketVolume'),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "eps": info.get('trailingEps'),
                "dividend_yield": info.get('dividendYield'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "currency": info.get('currency'),
                "exchange": info.get('exchange'),
                "timezone": info.get('timeZoneFullName'),
                "last_updated": datetime.now().isoformat()
            }
            
        except FinanceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get quote for {symbol}: {str(e)}")
    
    @staticmethod
    def get_historical_data(
        symbol: str, 
        period: str = "1mo", 
        interval: str = "1d",
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical stock data using yfinance.
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            start: Start date (YYYY-MM-DD format)
            end: End date (YYYY-MM-DD format)
            
        Returns:
            Dictionary containing historical data
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            symbol = FinanceAPIService._validate_symbol(symbol)
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            if start and end:
                hist = ticker.history(start=start, end=end, interval=interval)
            else:
                hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                raise FinanceAPIError(f"No historical data found for symbol {symbol}")
            
            # Convert to dictionary format
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.isoformat(),
                    "open": float(row['Open']) if not pd.isna(row['Open']) else None,
                    "high": float(row['High']) if not pd.isna(row['High']) else None,
                    "low": float(row['Low']) if not pd.isna(row['Low']) else None,
                    "close": float(row['Close']) if not pd.isna(row['Close']) else None,
                    "volume": int(row['Volume']) if not pd.isna(row['Volume']) else None,
                })
            
            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "start": start,
                "end": end,
                "count": len(data),
                "data": data
            }
            
        except FinanceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get historical data for {symbol}: {str(e)}")
    
    @staticmethod
    def search_symbols(query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for stock symbols using Yahoo Finance search API.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary containing search results
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            url = "https://query1.finance.yahoo.com/v1/finance/search"
            params = {
                "q": query,
                "quotesCount": limit,
                "newsCount": 0,
                "listsCount": 0
            }
            
            response = requests.get(url, params=params, timeout=FinanceAPIService.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            quotes = data.get('quotes', [])
            
            results = []
            for quote in quotes:
                results.append({
                    "symbol": quote.get('symbol'),
                    "name": quote.get('shortname') or quote.get('longname'),
                    "exchange": quote.get('exchange'),
                    "type": quote.get('quoteType'),
                    "sector": quote.get('sector'),
                    "industry": quote.get('industry')
                })
            
            return {
                "query": query,
                "count": len(results),
                "results": results
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error searching for {query}: {e}")
            raise FinanceAPIError(f"Failed to search symbols: {str(e)}")
        except Exception as e:
            logger.error(f"Error searching symbols for query {query}: {e}")
            raise FinanceAPIError(f"Failed to search symbols: {str(e)}")
    
    @staticmethod
    def get_market_movers(market_type: str = "gainers", count: int = 10) -> Dict[str, Any]:
        """
        Get market movers (gainers, losers, most active) using Yahoo Finance.
        
        Args:
            market_type: Type of movers ('gainers', 'losers', 'most_active')
            count: Number of results to return
            
        Returns:
            Dictionary containing market movers data
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            screener_map = {
                "gainers": "day_gainers",
                "losers": "day_losers", 
                "most_active": "most_actives"
            }
            
            if market_type not in screener_map:
                raise FinanceAPIError(f"Invalid market_type: {market_type}")
            
            url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
            params = {
                "formatted": "true",
                "lang": "en-US",
                "region": "US",
                "scrIds": screener_map[market_type],
                "count": count
            }
            
            response = requests.get(url, params=params, timeout=FinanceAPIService.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            results = []
            for quote in quotes:
                results.append({
                    "symbol": quote.get('symbol'),
                    "name": quote.get('shortName'),
                    "price": quote.get('regularMarketPrice'),
                    "change": quote.get('regularMarketChange'),
                    "change_percent": quote.get('regularMarketChangePercent'),
                    "volume": quote.get('regularMarketVolume'),
                    "market_cap": quote.get('marketCap')
                })
            
            return {
                "market_type": market_type,
                "count": len(results),
                "results": results
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error getting market movers: {e}")
            raise FinanceAPIError(f"Failed to get market movers: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting market movers: {e}")
            raise FinanceAPIError(f"Failed to get market movers: {str(e)}")
    
    @staticmethod
    def get_company_info(symbol: str) -> Dict[str, Any]:
        """
        Get company information and profile using yfinance.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary containing company information
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            symbol = FinanceAPIService._validate_symbol(symbol)
            ticker = yf.Ticker(symbol)
            
            info = ticker.info
            if not info:
                raise FinanceAPIError(f"No company info found for symbol {symbol}")
            
            return {
                "symbol": symbol,
                "name": info.get('longName') or info.get('shortName'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "description": info.get('longBusinessSummary'),
                "website": info.get('website'),
                "employees": info.get('fullTimeEmployees'),
                "headquarters": {
                    "city": info.get('city'),
                    "state": info.get('state'),
                    "country": info.get('country'),
                    "address": info.get('address1')
                },
                "financials": {
                    "market_cap": info.get('marketCap'),
                    "enterprise_value": info.get('enterpriseValue'),
                    "pe_ratio": info.get('trailingPE'),
                    "peg_ratio": info.get('pegRatio'),
                    "price_to_book": info.get('priceToBook'),
                    "debt_to_equity": info.get('debtToEquity'),
                    "roe": info.get('returnOnEquity'),
                    "revenue": info.get('totalRevenue'),
                    "gross_margins": info.get('grossMargins'),
                    "operating_margins": info.get('operatingMargins'),
                    "profit_margins": info.get('profitMargins')
                },
                "dividend_info": {
                    "dividend_rate": info.get('dividendRate'),
                    "dividend_yield": info.get('dividendYield'),
                    "payout_ratio": info.get('payoutRatio'),
                    "ex_dividend_date": info.get('exDividendDate')
                }
            }
            
        except FinanceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get company info for {symbol}: {str(e)}")
    
    @staticmethod
    def get_market_news(symbol: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Get market news, optionally filtered by symbol using yfinance.
        
        Args:
            symbol: Stock symbol to filter news (optional)
            limit: Maximum number of news items
            
        Returns:
            Dictionary containing news data
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            if symbol:
                # Get company-specific news
                symbol = FinanceAPIService._validate_symbol(symbol)
                ticker = yf.Ticker(symbol)
                news = ticker.news
                
                results = []
                for item in news[:limit]:
                    results.append({
                        "title": item.get('title'),
                        "link": item.get('link'),
                        "published": item.get('providerPublishTime'),
                        "publisher": item.get('publisher'),
                        "summary": item.get('summary'),
                        "thumbnail": item.get('thumbnail', {}).get('resolutions', [{}])[0].get('url') if item.get('thumbnail') else None
                    })
                
                return {
                    "symbol": symbol,
                    "count": len(results),
                    "news": results
                }
            else:
                # Get general market news using Yahoo Finance trending endpoint
                url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
                params = {"count": limit}
                
                response = requests.get(url, params=params, timeout=FinanceAPIService.REQUEST_TIMEOUT)
                response.raise_for_status()
                
                data = response.json()
                quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
                
                results = []
                for quote in quotes:
                    results.append({
                        "symbol": quote.get('symbol'),
                        "name": quote.get('shortName'),
                        "price": quote.get('regularMarketPrice'),
                        "change_percent": quote.get('regularMarketChangePercent')
                    })
                
                return {
                    "type": "trending",
                    "count": len(results),
                    "trending_stocks": results
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error getting news: {e}")
            raise FinanceAPIError(f"Failed to get market news: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting market news: {e}")
            raise FinanceAPIError(f"Failed to get market news: {str(e)}")
    
    @staticmethod
    def get_market_status() -> Dict[str, Any]:
        """
        Get current market status (open/closed).
        
        Returns:
            Dictionary containing market status information
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            # Use a major index to check market status
            ticker = yf.Ticker("^GSPC")  # S&P 500
            info = ticker.info
            
            # Check if we have recent data
            now = datetime.now()
            is_weekday = now.weekday() < 5  # Monday = 0, Sunday = 6
            
            # Market hours: 9:30 AM - 4:00 PM ET (approximately)
            market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            is_market_hours = market_open_time <= now <= market_close_time
            is_open = is_weekday and is_market_hours
            
            # Extended hours: 4:00 AM - 9:30 AM and 4:00 PM - 8:00 PM ET
            extended_open_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
            extended_close_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
            
            is_extended_hours = is_weekday and (
                (extended_open_time <= now < market_open_time) or 
                (market_close_time < now <= extended_close_time)
            )
            
            market_state = "REGULAR" if is_open else ("EXTENDED" if is_extended_hours else "CLOSED")
            
            return {
                "market_state": market_state,
                "is_open": is_open,
                "is_extended_hours": is_extended_hours,
                "current_time": now.isoformat(),
                "next_open": market_open_time.isoformat() if not is_open else None,
                "next_close": market_close_time.isoformat() if is_open else None,
                "timezone": "US/Eastern"
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            raise FinanceAPIError(f"Failed to get market status: {str(e)}")
    
    @staticmethod
    def get_multiple_quotes(symbols: List[str]) -> Dict[str, Any]:
        """
        Get quotes for multiple symbols at once.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary containing quotes for all symbols
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            if not symbols or len(symbols) == 0:
                raise FinanceAPIError("No symbols provided")
            
            # Validate and format symbols
            validated_symbols = [FinanceAPIService._validate_symbol(s) for s in symbols]
            
            # Create tickers string
            tickers = yf.Tickers(' '.join(validated_symbols))
            
            results = {}
            for symbol in validated_symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info
                    
                    if info and 'regularMarketPrice' in info:
                        results[symbol] = {
                            "symbol": symbol,
                            "current_price": info.get('regularMarketPrice'),
                            "previous_close": info.get('previousClose'),
                            "change": info.get('regularMarketChange'),
                            "change_percent": info.get('regularMarketChangePercent'),
                            "volume": info.get('regularMarketVolume')
                        }
                    else:
                        results[symbol] = {"error": "No data available"}
                        
                except Exception as e:
                    results[symbol] = {"error": str(e)}
            
            return {
                "requested_symbols": validated_symbols,
                "successful_count": len([r for r in results.values() if 'error' not in r]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error getting multiple quotes: {e}")
            raise FinanceAPIError(f"Failed to get multiple quotes: {str(e)}")

# Import pandas for data processing
try:
    import pandas as pd
except ImportError:
    logger.warning("pandas not installed, some functionality may be limited")
    pd = None