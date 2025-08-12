# app/services/finance_api.py
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class FinanceAPIError(Exception):
    """Custom exception for Finance API related errors"""
    pass

class FinanceAPIService:
    """
    Finance API Service using Alpha Vantage API for stock market data.
    Provides static methods for various financial data operations.
    """
    
    BASE_URL = settings.ALPHA_VANTAGE_BASE_URL
    API_KEY = settings.ALPHA_VANTAGE_API_KEY
    REQUEST_TIMEOUT = settings.API_REQUEST_TIMEOUT
    
    @staticmethod
    def _validate_symbol(symbol: str) -> str:
        """Validate and format stock symbol."""
        if not symbol or not isinstance(symbol, str):
            raise FinanceAPIError("Invalid symbol provided")
        return symbol.upper().strip()
    
    @staticmethod
    def _make_request(params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Alpha Vantage API with error handling."""
        params['apikey'] = FinanceAPIService.API_KEY
        
        try:
            response = requests.get(
                FinanceAPIService.BASE_URL,
                params=params,
                timeout=FinanceAPIService.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise FinanceAPIError(f"API Error: {data['Error Message']}")
            
            if 'Note' in data:
                # Rate limit hit
                raise FinanceAPIError("API rate limit exceeded. Please try again later.")
            
            if 'Information' in data:
                # API limit or other info message
                raise FinanceAPIError(f"API Info: {data['Information']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise FinanceAPIError(f"Failed to make API request: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise FinanceAPIError("Invalid response format from API")
    
    @staticmethod
    def get_stock_quote(symbol: str) -> Dict[str, Any]:
        """
        Get current stock quote for a symbol using Alpha Vantage.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            
        Returns:
            Dictionary containing stock quote data
            
        Raises:
            FinanceAPIError: If request fails or symbol not found
        """
        try:
            symbol = FinanceAPIService._validate_symbol(symbol)
            
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol
            }
            
            data = FinanceAPIService._make_request(params)
            
            # Parse Alpha Vantage response
            if 'Global Quote' not in data:
                raise FinanceAPIError(f"No quote data found for symbol {symbol}")
            
            quote = data['Global Quote']
            
            # Alpha Vantage returns data with prefixed keys
            return {
                "symbol": symbol,
                "current_price": float(quote.get('05. price', 0)),
                "previous_close": float(quote.get('08. previous close', 0)),
                "open": float(quote.get('02. open', 0)),
                "day_high": float(quote.get('03. high', 0)),
                "day_low": float(quote.get('04. low', 0)),
                "volume": int(quote.get('06. volume', 0)),
                "change": float(quote.get('09. change', 0)),
                "change_percent": quote.get('10. change percent', '0%').replace('%', ''),
                "last_trading_day": quote.get('07. latest trading day'),
                "last_updated": datetime.now().isoformat(),
                "provider": "Alpha Vantage"
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
        Get historical stock data using Alpha Vantage.
        
        Args:
            symbol: Stock symbol
            period: Data period (not directly used, mapped to Alpha Vantage functions)
            interval: Data interval (maps to Alpha Vantage intervals)
            start: Start date (not used in this implementation)
            end: End date (not used in this implementation)
            
        Returns:
            Dictionary containing historical data
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            symbol = FinanceAPIService._validate_symbol(symbol)
            
            # Map intervals to Alpha Vantage functions
            if interval in ['1min', '5min', '15min', '30min', '60min']:
                function = 'TIME_SERIES_INTRADAY'
                params = {
                    'function': function,
                    'symbol': symbol,
                    'interval': interval
                }
                time_series_key = f'Time Series ({interval})'
            else:
                # Default to daily
                function = 'TIME_SERIES_DAILY'
                params = {
                    'function': function,
                    'symbol': symbol
                }
                time_series_key = 'Time Series (Daily)'
            
            data = FinanceAPIService._make_request(params)
            
            if time_series_key not in data:
                raise FinanceAPIError(f"No historical data found for symbol {symbol}")
            
            time_series = data[time_series_key]
            
            # Convert to standard format
            historical_data = []
            for date_str, values in time_series.items():
                historical_data.append({
                    "date": date_str,
                    "open": float(values.get('1. open', 0)),
                    "high": float(values.get('2. high', 0)),
                    "low": float(values.get('3. low', 0)),
                    "close": float(values.get('4. close', 0)),
                    "volume": int(values.get('5. volume', 0))
                })
            
            # Sort by date (most recent first)
            historical_data.sort(key=lambda x: x['date'], reverse=True)
            
            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "function": function,
                "count": len(historical_data),
                "data": historical_data,
                "provider": "Alpha Vantage"
            }
            
        except FinanceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get historical data for {symbol}: {str(e)}")
    
    @staticmethod
    def search_symbols(query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for stock symbols using Alpha Vantage.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary containing search results
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': query
            }
            
            data = FinanceAPIService._make_request(params)
            
            if 'bestMatches' not in data:
                return {
                    "query": query,
                    "count": 0,
                    "results": [],
                    "provider": "Alpha Vantage"
                }
            
            matches = data['bestMatches'][:limit]
            
            results = []
            for match in matches:
                results.append({
                    "symbol": match.get('1. symbol'),
                    "name": match.get('2. name'),
                    "type": match.get('3. type'),
                    "region": match.get('4. region'),
                    "market_open": match.get('5. marketOpen'),
                    "market_close": match.get('6. marketClose'),
                    "timezone": match.get('7. timezone'),
                    "currency": match.get('8. currency'),
                    "match_score": float(match.get('9. matchScore', 0))
                })
            
            return {
                "query": query,
                "count": len(results),
                "results": results,
                "provider": "Alpha Vantage"
            }
            
        except FinanceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error searching symbols for query {query}: {e}")
            raise FinanceAPIError(f"Failed to search symbols: {str(e)}")
    
    @staticmethod
    def get_market_movers(market_type: str = "gainers", count: int = 10) -> Dict[str, Any]:
        """
        Get market movers. Note: Alpha Vantage doesn't have a direct endpoint for this.
        This is a placeholder implementation that could be enhanced with additional logic.
        
        Args:
            market_type: Type of movers ('gainers', 'losers', 'most_active')
            count: Number of results to return
            
        Returns:
            Dictionary containing market movers data
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            # Alpha Vantage doesn't have market movers endpoint
            # This would need to be implemented using other data or a different approach
            return {
                "market_type": market_type,
                "count": 0,
                "results": [],
                "message": "Market movers not available with Alpha Vantage. Consider using sector performance or implement custom logic.",
                "provider": "Alpha Vantage"
            }
            
        except Exception as e:
            logger.error(f"Error getting market movers: {e}")
            raise FinanceAPIError(f"Failed to get market movers: {str(e)}")
    
    @staticmethod
    def get_company_info(symbol: str) -> Dict[str, Any]:
        """
        Get company information using Alpha Vantage.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary containing company information
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            symbol = FinanceAPIService._validate_symbol(symbol)
            
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol
            }
            
            data = FinanceAPIService._make_request(params)
            
            if not data or data.get('Symbol') != symbol:
                raise FinanceAPIError(f"No company info found for symbol {symbol}")
            
            return {
                "symbol": symbol,
                "name": data.get('Name'),
                "description": data.get('Description'),
                "sector": data.get('Sector'),
                "industry": data.get('Industry'),
                "exchange": data.get('Exchange'),
                "currency": data.get('Currency'),
                "country": data.get('Country'),
                "address": data.get('Address'),
                "financials": {
                    "market_cap": int(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else None,
                    "pe_ratio": float(data.get('PERatio', 0)) if data.get('PERatio') != 'None' else None,
                    "peg_ratio": float(data.get('PEGRatio', 0)) if data.get('PEGRatio') != 'None' else None,
                    "price_to_book": float(data.get('PriceToBookRatio', 0)) if data.get('PriceToBookRatio') != 'None' else None,
                    "dividend_per_share": float(data.get('DividendPerShare', 0)) if data.get('DividendPerShare') != 'None' else None,
                    "dividend_yield": float(data.get('DividendYield', 0)) if data.get('DividendYield') != 'None' else None,
                    "eps": float(data.get('EPS', 0)) if data.get('EPS') != 'None' else None,
                    "revenue_per_share": float(data.get('RevenuePerShareTTM', 0)) if data.get('RevenuePerShareTTM') != 'None' else None,
                    "profit_margin": float(data.get('ProfitMargin', 0)) if data.get('ProfitMargin') != 'None' else None,
                    "operating_margin": float(data.get('OperatingMarginTTM', 0)) if data.get('OperatingMarginTTM') != 'None' else None,
                    "beta": float(data.get('Beta', 0)) if data.get('Beta') != 'None' else None,
                    "52_week_high": float(data.get('52WeekHigh', 0)) if data.get('52WeekHigh') != 'None' else None,
                    "52_week_low": float(data.get('52WeekLow', 0)) if data.get('52WeekLow') != 'None' else None,
                },
                "analyst_rating": data.get('AnalystTargetPrice'),
                "last_updated": datetime.now().isoformat(),
                "provider": "Alpha Vantage"
            }
            
        except FinanceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {e}")
            raise FinanceAPIError(f"Failed to get company info for {symbol}: {str(e)}")
    
    @staticmethod
    def get_market_news(symbol: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Get market news using Alpha Vantage.
        
        Args:
            symbol: Stock symbol to filter news (optional)
            limit: Maximum number of news items
            
        Returns:
            Dictionary containing news data
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            params = {
                'function': 'NEWS_SENTIMENT'
            }
            
            if symbol:
                symbol = FinanceAPIService._validate_symbol(symbol)
                params['tickers'] = symbol
            
            # Add limit parameter
            params['limit'] = limit
            
            data = FinanceAPIService._make_request(params)
            
            if 'feed' not in data:
                return {
                    "symbol": symbol,
                    "count": 0,
                    "news": [],
                    "provider": "Alpha Vantage"
                }
            
            news_items = data['feed'][:limit]
            
            results = []
            for item in news_items:
                results.append({
                    "title": item.get('title'),
                    "url": item.get('url'),
                    "published": item.get('time_published'),
                    "summary": item.get('summary'),
                    "banner_image": item.get('banner_image'),
                    "source": item.get('source'),
                    "category": item.get('category_within_source'),
                    "sentiment": {
                        "label": item.get('overall_sentiment_label'),
                        "score": float(item.get('overall_sentiment_score', 0))
                    },
                    "relevance_score": float(item.get('relevance_score', 0)) if symbol else None
                })
            
            return {
                "symbol": symbol,
                "count": len(results),
                "news": results,
                "provider": "Alpha Vantage"
            }
                
        except FinanceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting market news: {e}")
            raise FinanceAPIError(f"Failed to get market news: {str(e)}")
    
    @staticmethod
    def get_market_status() -> Dict[str, Any]:
        """
        Get current market status. Alpha Vantage doesn't have a direct endpoint,
        so this uses logic to determine market hours.
        
        Returns:
            Dictionary containing market status information
            
        Raises:
            FinanceAPIError: If request fails
        """
        try:
            now = datetime.now()
            is_weekday = now.weekday() < 5  # Monday = 0, Sunday = 6
            
            # Market hours: 9:30 AM - 4:00 PM ET
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
                "timezone": "US/Eastern",
                "note": "Market status calculated locally (Alpha Vantage doesn't provide real-time market status)",
                "provider": "Alpha Vantage"
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            raise FinanceAPIError(f"Failed to get market status: {str(e)}")
    
    @staticmethod
    def get_multiple_quotes(symbols: List[str]) -> Dict[str, Any]:
        """
        Get quotes for multiple symbols at once.
        Note: Alpha Vantage requires individual requests for each symbol.
        
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
            
            # Validate symbols
            validated_symbols = [FinanceAPIService._validate_symbol(s) for s in symbols]
            
            results = {}
            successful_count = 0
            
            for symbol in validated_symbols:
                try:
                    quote_data = FinanceAPIService.get_stock_quote(symbol)
                    results[symbol] = {
                        "symbol": symbol,
                        "current_price": quote_data.get('current_price'),
                        "previous_close": quote_data.get('previous_close'),
                        "change": quote_data.get('change'),
                        "change_percent": quote_data.get('change_percent'),
                        "volume": quote_data.get('volume'),
                        "last_trading_day": quote_data.get('last_trading_day')
                    }
                    successful_count += 1
                    
                    # Add a small delay to avoid rate limiting
                    import time
                    time.sleep(0.1)  # 100ms delay between requests
                    
                except FinanceAPIError as e:
                    results[symbol] = {"error": str(e)}
                except Exception as e:
                    results[symbol] = {"error": f"Unexpected error: {str(e)}"}
            
            return {
                "requested_symbols": validated_symbols,
                "successful_count": successful_count,
                "results": results,
                "provider": "Alpha Vantage",
                "note": "Multiple quotes require individual API calls with Alpha Vantage"
            }
            
        except Exception as e:
            logger.error(f"Error getting multiple quotes: {e}")
            raise FinanceAPIError(f"Failed to get multiple quotes: {str(e)}")