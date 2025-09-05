"""
Polygon.io utilities for market data retrieval
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolygonDataProvider:
    """Polygon.io data provider for stock and options data"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        self.base_url = "https://api.polygon.io"
        self.name = "Polygon.io"
        
        if not self.api_key:
            logger.warning("Polygon API key not found. Some features may not work.")
    
    def _make_request(self, endpoint, params=None):
        """Make API request to Polygon"""
        if not self.api_key:
            return None
        
        if params is None:
            params = {}
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {endpoint}: {str(e)}")
            return None
    
    def get_stock_data(self, symbol):
        """
        Get current stock data
        
        Args:
            symbol (str): Stock symbol
        
        Returns:
            dict: Stock data including price, change, volume
        """
        try:
            # Get previous close
            prev_close_endpoint = f"/v2/aggs/ticker/{symbol}/prev"
            prev_data = self._make_request(prev_close_endpoint)
            
            if not prev_data or prev_data.get('status') != 'OK':
                return None
            
            prev_close = prev_data['results'][0]['c']
            
            # Get current price (last trade)
            last_trade_endpoint = f"/v2/last/trade/{symbol}"
            current_data = self._make_request(last_trade_endpoint)
            
            if not current_data or current_data.get('status') != 'OK':
                return None
            
            current_price = current_data['results']['p']
            volume = prev_data['results'][0]['v']
            
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            
            return {
                'symbol': symbol.upper(),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': volume,
                'previous_close': round(prev_close, 2),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, start_date, end_date, timespan='day'):
        """
        Get historical stock data
        
        Args:
            symbol (str): Stock symbol
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            timespan (str): Timespan (minute, hour, day, week, month, quarter, year)
        
        Returns:
            pd.DataFrame: Historical data
        """
        try:
            endpoint = f"/v2/aggs/ticker/{symbol}/range/1/{timespan}/{start_date}/{end_date}"
            data = self._make_request(endpoint)
            
            if not data or data.get('status') != 'OK':
                return pd.DataFrame()
            
            results = data.get('results', [])
            if not results:
                return pd.DataFrame()
            
            df = pd.DataFrame(results)
            df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
            df = df.rename(columns={
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                'v': 'Volume'
            })
            df.set_index('timestamp', inplace=True)
            
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_options_chain(self, symbol, expiration_date=None):
        """
        Get options chain data
        
        Args:
            symbol (str): Stock symbol
            expiration_date (str): Expiration date (YYYY-MM-DD)
        
        Returns:
            dict: Options chain data
        """
        try:
            # Get options contracts
            endpoint = f"/v3/reference/options/contracts"
            params = {
                'underlying_ticker': symbol,
                'limit': 1000
            }
            
            if expiration_date:
                params['expiration_date'] = expiration_date
            
            data = self._make_request(endpoint, params)
            
            if not data or data.get('status') != 'OK':
                return None
            
            contracts = data.get('results', [])
            
            calls = []
            puts = []
            
            for contract in contracts:
                contract_type = contract.get('contract_type')
                if contract_type == 'call':
                    calls.append(contract)
                elif contract_type == 'put':
                    puts.append(contract)
            
            return {
                'calls': calls,
                'puts': puts,
                'total_contracts': len(contracts)
            }
        
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {str(e)}")
            return None
    
    def get_option_quote(self, option_symbol):
        """
        Get option quote
        
        Args:
            option_symbol (str): Option symbol
        
        Returns:
            dict: Option quote data
        """
        try:
            endpoint = f"/v2/last/trade/{option_symbol}"
            data = self._make_request(endpoint)
            
            if not data or data.get('status') != 'OK':
                return None
            
            return data.get('results')
        
        except Exception as e:
            logger.error(f"Error fetching option quote for {option_symbol}: {str(e)}")
            return None
    
    def calculate_historical_volatility(self, symbol, days=30):
        """
        Calculate historical volatility
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days for calculation
        
        Returns:
            float: Annualized historical volatility
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 10)
            
            df = self.get_historical_data(
                symbol, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            if df.empty or len(df) < days:
                return None
            
            # Calculate daily returns
            df['returns'] = df['Close'].pct_change()
            
            # Calculate volatility (annualized)
            volatility = df['returns'].std() * (252 ** 0.5)  # 252 trading days per year
            
            return round(volatility, 4)
        
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol}: {str(e)}")
            return None
    
    def get_market_overview(self):
        """
        Get market overview data for major indices
        
        Returns:
            dict: Market overview data
        """
        indices = {
            'SPY': 'SPDR S&P 500 ETF',
            'QQQ': 'Invesco QQQ Trust',
            'IWM': 'iShares Russell 2000 ETF',
            'VIX': 'CBOE Volatility Index'
        }
        
        market_data = {}
        
        for symbol, name in indices.items():
            data = self.get_stock_data(symbol)
            if data:
                market_data[symbol] = {
                    'name': name,
                    'price': data['price'],
                    'change': data['change'],
                    'change_percent': data['change_percent']
                }
        
        return market_data
    
    def search_stocks(self, query):
        """
        Search for stocks
        
        Args:
            query (str): Search query
        
        Returns:
            list: List of matching tickers
        """
        try:
            endpoint = "/v3/reference/tickers"
            params = {
                'search': query,
                'market': 'stocks',
                'active': 'true',
                'limit': 10
            }
            
            data = self._make_request(endpoint, params)
            
            if not data or data.get('status') != 'OK':
                return []
            
            results = data.get('results', [])
            return [ticker['ticker'] for ticker in results]
        
        except Exception as e:
            logger.error(f"Error searching for {query}: {str(e)}")
            return []
    
    def get_company_info(self, symbol):
        """
        Get company information
        
        Args:
            symbol (str): Stock symbol
        
        Returns:
            dict: Company information
        """
        try:
            endpoint = f"/v3/reference/tickers/{symbol}"
            data = self._make_request(endpoint)
            
            if not data or data.get('status') != 'OK':
                return None
            
            result = data.get('results', {})
            
            return {
                'symbol': symbol.upper(),
                'company_name': result.get('name', 'N/A'),
                'description': result.get('description', 'N/A'),
                'market_cap': result.get('market_cap', 'N/A'),
                'primary_exchange': result.get('primary_exchange', 'N/A'),
                'type': result.get('type', 'N/A'),
                'currency_name': result.get('currency_name', 'N/A'),
                'locale': result.get('locale', 'N/A')
            }
        
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return None
    
    def get_market_status(self):
        """
        Get market status
        
        Returns:
            dict: Market status information
        """
        try:
            endpoint = "/v1/marketstatus/now"
            data = self._make_request(endpoint)
            
            if not data or data.get('status') != 'OK':
                return None
            
            return data.get('results', {})
        
        except Exception as e:
            logger.error(f"Error fetching market status: {str(e)}")
            return None


# Convenience functions
def get_current_price(symbol):
    """Get current stock price using Polygon"""
    provider = PolygonDataProvider()
    data = provider.get_stock_data(symbol)
    return data['price'] if data else None


def get_historical_volatility(symbol, days=30):
    """Get historical volatility using Polygon"""
    provider = PolygonDataProvider()
    return provider.calculate_historical_volatility(symbol, days)

