"""
Alpaca utilities for market data retrieval and trading
"""

import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlpacaDataProvider:
    """Alpaca data provider for stock and options data"""
    
    def __init__(self, api_key=None, secret_key=None, paper=True):
        self.api_key = api_key or os.getenv('ALPACA_PAPER_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_PAPER_SECRET_KEY')
        self.paper = paper
        self.name = "Alpaca"
        
        if not self.api_key or not self.secret_key:
            logger.warning("Alpaca API credentials not found. Some features may not work.")
            self.api = None
        else:
            try:
                base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'
                self.api = tradeapi.REST(
                    self.api_key,
                    self.secret_key,
                    base_url,
                    api_version='v2'
                )
                # Test connection
                self.api.get_account()
                logger.info("Successfully connected to Alpaca API")
            except Exception as e:
                logger.error(f"Error connecting to Alpaca API: {str(e)}")
                self.api = None
    
    def get_stock_data(self, symbol):
        """
        Get current stock data
        
        Args:
            symbol (str): Stock symbol
        
        Returns:
            dict: Stock data including price, change, volume
        """
        if not self.api:
            return None
        
        try:
            # Get latest trade
            latest_trade = self.api.get_latest_trade(symbol)
            current_price = latest_trade.price
            
            # Get previous close
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=5)  # Get a few days to ensure we have data
            
            bars = self.api.get_bars(
                symbol,
                tradeapi.TimeFrame.Day,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                limit=5
            )
            
            if not bars:
                return None
            
            # Get the most recent bar (previous day's close)
            latest_bar = bars[-1]
            previous_close = latest_bar.c
            volume = latest_bar.v
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            return {
                'symbol': symbol.upper(),
                'price': round(float(current_price), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_percent), 2),
                'volume': int(volume),
                'previous_close': round(float(previous_close), 2),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, start_date, end_date, timeframe='1Day'):
        """
        Get historical stock data
        
        Args:
            symbol (str): Stock symbol
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            timeframe (str): Timeframe (1Min, 5Min, 15Min, 1Hour, 1Day)
        
        Returns:
            pd.DataFrame: Historical data
        """
        if not self.api:
            return pd.DataFrame()
        
        try:
            # Map timeframe string to Alpaca TimeFrame
            timeframe_map = {
                '1Min': tradeapi.TimeFrame.Minute,
                '5Min': tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute),
                '15Min': tradeapi.TimeFrame(15, tradeapi.TimeFrameUnit.Minute),
                '1Hour': tradeapi.TimeFrame.Hour,
                '1Day': tradeapi.TimeFrame.Day
            }
            
            tf = timeframe_map.get(timeframe, tradeapi.TimeFrame.Day)
            
            bars = self.api.get_bars(
                symbol,
                tf,
                start=start_date,
                end=end_date,
                limit=10000
            )
            
            if not bars:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for bar in bars:
                data.append({
                    'timestamp': bar.t,
                    'Open': bar.o,
                    'High': bar.h,
                    'Low': bar.l,
                    'Close': bar.c,
                    'Volume': bar.v
                })
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
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
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days + 10)
            
            df = self.get_historical_data(
                symbol, 
                start_date.isoformat(), 
                end_date.isoformat()
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
            'IWM': 'iShares Russell 2000 ETF'
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
    
    def get_account_info(self):
        """
        Get account information
        
        Returns:
            dict: Account information
        """
        if not self.api:
            return None
        
        try:
            account = self.api.get_account()
            return {
                'account_number': account.account_number,
                'status': account.status,
                'currency': account.currency,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'multiplier': int(account.multiplier),
                'day_trade_count': int(account.day_trade_count),
                'daytrade_buying_power': float(account.daytrade_buying_power)
            }
        
        except Exception as e:
            logger.error(f"Error fetching account info: {str(e)}")
            return None
    
    def get_positions(self):
        """
        Get current positions
        
        Returns:
            list: List of positions
        """
        if not self.api:
            return []
        
        try:
            positions = self.api.list_positions()
            position_list = []
            
            for position in positions:
                position_list.append({
                    'symbol': position.symbol,
                    'qty': float(position.qty),
                    'side': position.side,
                    'market_value': float(position.market_value),
                    'cost_basis': float(position.cost_basis),
                    'unrealized_pl': float(position.unrealized_pl),
                    'unrealized_plpc': float(position.unrealized_plpc),
                    'current_price': float(position.current_price),
                    'lastday_price': float(position.lastday_price),
                    'change_today': float(position.change_today)
                })
            
            return position_list
        
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            return []
    
    def get_orders(self, status='all', limit=50):
        """
        Get orders
        
        Args:
            status (str): Order status filter
            limit (int): Maximum number of orders to return
        
        Returns:
            list: List of orders
        """
        if not self.api:
            return []
        
        try:
            orders = self.api.list_orders(status=status, limit=limit)
            order_list = []
            
            for order in orders:
                order_list.append({
                    'id': order.id,
                    'symbol': order.symbol,
                    'qty': float(order.qty),
                    'side': order.side,
                    'order_type': order.order_type,
                    'time_in_force': order.time_in_force,
                    'status': order.status,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at,
                    'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                    'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0
                })
            
            return order_list
        
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            return []
    
    def place_order(self, symbol, qty, side, order_type='market', time_in_force='day', limit_price=None):
        """
        Place an order (for paper trading)
        
        Args:
            symbol (str): Stock symbol
            qty (int): Quantity
            side (str): 'buy' or 'sell'
            order_type (str): 'market' or 'limit'
            time_in_force (str): 'day', 'gtc', etc.
            limit_price (float): Limit price for limit orders
        
        Returns:
            dict: Order information
        """
        if not self.api:
            return None
        
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price
            )
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'status': order.status,
                'created_at': order.created_at
            }
        
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def cancel_order(self, order_id):
        """
        Cancel an order
        
        Args:
            order_id (str): Order ID
        
        Returns:
            bool: Success status
        """
        if not self.api:
            return False
        
        try:
            self.api.cancel_order(order_id)
            return True
        
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {str(e)}")
            return False
    
    def get_market_calendar(self, start_date=None, end_date=None):
        """
        Get market calendar
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
        
        Returns:
            list: Market calendar data
        """
        if not self.api:
            return []
        
        try:
            if not start_date:
                start_date = datetime.now().date().isoformat()
            if not end_date:
                end_date = (datetime.now().date() + timedelta(days=30)).isoformat()
            
            calendar = self.api.get_calendar(start=start_date, end=end_date)
            
            calendar_list = []
            for day in calendar:
                calendar_list.append({
                    'date': day.date.isoformat(),
                    'open': day.open.isoformat(),
                    'close': day.close.isoformat()
                })
            
            return calendar_list
        
        except Exception as e:
            logger.error(f"Error fetching market calendar: {str(e)}")
            return []


# Convenience functions
def get_current_price(symbol):
    """Get current stock price using Alpaca"""
    provider = AlpacaDataProvider()
    data = provider.get_stock_data(symbol)
    return data['price'] if data else None


def get_historical_volatility(symbol, days=30):
    """Get historical volatility using Alpaca"""
    provider = AlpacaDataProvider()
    return provider.calculate_historical_volatility(symbol, days)

