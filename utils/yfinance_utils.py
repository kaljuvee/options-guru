"""
Yahoo Finance utilities for market data retrieval
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YFinanceDataProvider:
    """Yahoo Finance data provider for stock and options data"""
    
    def __init__(self):
        self.name = "Yahoo Finance"
    
    def get_stock_data(self, symbol, period="1d"):
        """
        Get current stock data
        
        Args:
            symbol (str): Stock symbol
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            dict: Stock data including price, change, volume
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            return {
                'symbol': symbol.upper(),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                'previous_close': round(previous_close, 2),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, start_date, end_date):
        """
        Get historical stock data
        
        Args:
            symbol (str): Stock symbol
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: Historical data
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            return hist
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_options_chain(self, symbol, expiration_date=None):
        """
        Get options chain data
        
        Args:
            symbol (str): Stock symbol
            expiration_date (str): Expiration date (YYYY-MM-DD), if None uses nearest expiration
        
        Returns:
            dict: Options chain data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            if not expirations:
                return None
            
            # Use specified expiration or nearest one
            if expiration_date is None:
                expiration_date = expirations[0]
            elif expiration_date not in expirations:
                # Find closest expiration date
                target_date = datetime.strptime(expiration_date, '%Y-%m-%d')
                closest_exp = min(expirations, 
                                key=lambda x: abs(datetime.strptime(x, '%Y-%m-%d') - target_date))
                expiration_date = closest_exp
            
            # Get options chain
            options_chain = ticker.option_chain(expiration_date)
            
            return {
                'calls': options_chain.calls,
                'puts': options_chain.puts,
                'expiration_date': expiration_date,
                'available_expirations': expirations
            }
        
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {str(e)}")
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
            start_date = end_date - timedelta(days=days + 10)  # Extra days for calculation
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if len(hist) < days:
                return None
            
            # Calculate daily returns
            hist['returns'] = hist['Close'].pct_change()
            
            # Calculate volatility (annualized)
            volatility = hist['returns'].std() * np.sqrt(252)  # 252 trading days per year
            
            return round(volatility, 4)
        
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol}: {str(e)}")
            return None
    
    def get_risk_free_rate(self):
        """
        Get current risk-free rate (10-year Treasury yield)
        
        Returns:
            float: Risk-free rate as decimal
        """
        try:
            treasury = yf.Ticker("^TNX")
            hist = treasury.history(period="5d")
            
            if not hist.empty:
                rate = hist['Close'].iloc[-1] / 100  # Convert percentage to decimal
                return round(rate, 4)
            else:
                return 0.05  # Default 5% if unable to fetch
        
        except Exception as e:
            logger.error(f"Error fetching risk-free rate: {str(e)}")
            return 0.05  # Default 5%
    
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
        Search for stocks (basic implementation)
        
        Args:
            query (str): Search query
        
        Returns:
            list: List of matching symbols
        """
        # This is a basic implementation
        # For a more comprehensive search, consider using other APIs
        try:
            # Try to get data for the query as a symbol
            data = self.get_stock_data(query.upper())
            if data:
                return [query.upper()]
            else:
                return []
        
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
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol.upper(),
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A')
            }
        
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return None


# Convenience functions
def get_current_price(symbol):
    """Get current stock price"""
    provider = YFinanceDataProvider()
    data = provider.get_stock_data(symbol)
    return data['price'] if data else None


def get_historical_volatility(symbol, days=30):
    """Get historical volatility"""
    provider = YFinanceDataProvider()
    return provider.calculate_historical_volatility(symbol, days)


def get_risk_free_rate():
    """Get current risk-free rate"""
    provider = YFinanceDataProvider()
    return provider.get_risk_free_rate()

