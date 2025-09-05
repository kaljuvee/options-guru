"""
Unit tests for data providers
"""

import pytest
import pandas as pd
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from yfinance_utils import YFinanceDataProvider
from polygon_utils import PolygonDataProvider
from alpaca_utils import AlpacaDataProvider
from data_provider import DataProviderManager


class TestYFinanceDataProvider:
    """Test cases for Yahoo Finance data provider"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.provider = YFinanceDataProvider()
    
    def test_initialization(self):
        """Test provider initialization"""
        assert self.provider.name == "Yahoo Finance"
    
    @patch('yfinance.Ticker')
    def test_get_stock_data_success(self, mock_ticker):
        """Test successful stock data retrieval"""
        # Mock yfinance response
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Mock history data
        mock_hist = pd.DataFrame({
            'Close': [100.0, 101.0],
            'Volume': [1000000, 1100000]
        })
        mock_ticker_instance.history.return_value = mock_hist
        
        # Mock info data
        mock_ticker_instance.info = {
            'previousClose': 100.0,
            'marketCap': 1000000000,
            'trailingPE': 15.5
        }
        
        result = self.provider.get_stock_data('AAPL')
        
        assert result is not None
        assert result['symbol'] == 'AAPL'
        assert result['price'] == 101.0
        assert result['change'] == 1.0
        assert result['change_percent'] == 1.0
        assert 'last_updated' in result
    
    @patch('yfinance.Ticker')
    def test_get_stock_data_failure(self, mock_ticker):
        """Test stock data retrieval failure"""
        # Mock yfinance to raise exception
        mock_ticker.side_effect = Exception("Network error")
        
        result = self.provider.get_stock_data('INVALID')
        assert result is None
    
    @patch('yfinance.Ticker')
    def test_calculate_historical_volatility(self, mock_ticker):
        """Test historical volatility calculation"""
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create mock historical data with some price movement
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        prices = [100 + i * 0.5 + (-1)**i * 2 for i in range(30)]  # Some volatility
        
        mock_hist = pd.DataFrame({
            'Close': prices
        }, index=dates)
        
        mock_ticker_instance.history.return_value = mock_hist
        
        volatility = self.provider.calculate_historical_volatility('AAPL', 30)
        
        assert volatility is not None
        assert isinstance(volatility, float)
        assert volatility > 0
    
    def test_get_risk_free_rate_default(self):
        """Test risk-free rate with default fallback"""
        # This should return default rate if unable to fetch
        rate = self.provider.get_risk_free_rate()
        assert isinstance(rate, float)
        assert 0 <= rate <= 1  # Should be between 0 and 100%


class TestPolygonDataProvider:
    """Test cases for Polygon data provider"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.provider = PolygonDataProvider(api_key='test_key')
    
    def test_initialization(self):
        """Test provider initialization"""
        assert self.provider.name == "Polygon.io"
        assert self.provider.api_key == 'test_key'
    
    def test_initialization_no_key(self):
        """Test provider initialization without API key"""
        provider = PolygonDataProvider()
        assert provider.api_key is None
    
    @patch('requests.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'OK', 'results': []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.provider._make_request('/test/endpoint')
        
        assert result == {'status': 'OK', 'results': []}
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_make_request_failure(self, mock_get):
        """Test failed API request"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.provider._make_request('/test/endpoint')
        assert result is None
    
    @patch.object(PolygonDataProvider, '_make_request')
    def test_get_stock_data_success(self, mock_request):
        """Test successful stock data retrieval"""
        # Mock API responses
        mock_request.side_effect = [
            # Previous close response
            {
                'status': 'OK',
                'results': [{'c': 100.0, 'v': 1000000}]
            },
            # Current price response
            {
                'status': 'OK',
                'results': {'p': 101.0}
            }
        ]
        
        result = self.provider.get_stock_data('AAPL')
        
        assert result is not None
        assert result['symbol'] == 'AAPL'
        assert result['price'] == 101.0
        assert result['change'] == 1.0
        assert result['volume'] == 1000000


class TestAlpacaDataProvider:
    """Test cases for Alpaca data provider"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create provider without actual API connection
        with patch('alpaca_trade_api.REST'):
            self.provider = AlpacaDataProvider(api_key='test_key', secret_key='test_secret')
    
    def test_initialization(self):
        """Test provider initialization"""
        assert self.provider.name == "Alpaca"
        assert self.provider.api_key == 'test_key'
        assert self.provider.secret_key == 'test_secret'
    
    def test_initialization_no_credentials(self):
        """Test provider initialization without credentials"""
        provider = AlpacaDataProvider()
        assert provider.api is None


class TestDataProviderManager:
    """Test cases for data provider manager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = DataProviderManager()
    
    def test_initialization(self):
        """Test manager initialization"""
        assert self.manager.default_provider == 'yfinance'
        assert self.manager.current_provider == 'yfinance'
        assert len(self.manager.providers) == 3
    
    def test_set_provider(self):
        """Test setting data provider"""
        self.manager.set_provider('polygon')
        assert self.manager.current_provider == 'polygon'
        
        # Test invalid provider
        self.manager.set_provider('invalid')
        assert self.manager.current_provider == 'polygon'  # Should remain unchanged
    
    def test_get_provider(self):
        """Test getting current provider"""
        provider = self.manager.get_provider()
        assert isinstance(provider, YFinanceDataProvider)
        
        self.manager.set_provider('polygon')
        provider = self.manager.get_provider()
        assert isinstance(provider, PolygonDataProvider)
    
    def test_get_available_providers(self):
        """Test getting available providers"""
        providers = self.manager.get_available_providers()
        expected = ['yfinance', 'polygon', 'alpaca']
        assert set(providers) == set(expected)
    
    @patch.object(YFinanceDataProvider, 'get_stock_data')
    def test_get_stock_data_success(self, mock_get_data):
        """Test successful stock data retrieval through manager"""
        mock_get_data.return_value = {
            'symbol': 'AAPL',
            'price': 150.0,
            'change': 2.5,
            'change_percent': 1.69
        }
        
        result = self.manager.get_stock_data('AAPL')
        
        assert result is not None
        assert result['symbol'] == 'AAPL'
        assert result['price'] == 150.0
        mock_get_data.assert_called_once_with('AAPL')
    
    @patch.object(YFinanceDataProvider, 'get_stock_data')
    @patch.object(PolygonDataProvider, 'get_stock_data')
    def test_get_stock_data_fallback(self, mock_polygon, mock_yfinance):
        """Test fallback to other providers when primary fails"""
        # Primary provider fails
        mock_yfinance.side_effect = Exception("Primary failed")
        
        # Fallback provider succeeds
        mock_polygon.return_value = {
            'symbol': 'AAPL',
            'price': 150.0,
            'change': 2.5,
            'change_percent': 1.69
        }
        
        result = self.manager.get_stock_data('AAPL')
        
        assert result is not None
        assert result['symbol'] == 'AAPL'
        mock_yfinance.assert_called_once()
        mock_polygon.assert_called_once()


class TestDataIntegrity:
    """Test data integrity and validation"""
    
    def test_stock_data_structure(self):
        """Test that stock data has required structure"""
        required_fields = [
            'symbol', 'price', 'change', 'change_percent', 
            'volume', 'previous_close', 'last_updated'
        ]
        
        # Mock data structure
        mock_data = {
            'symbol': 'AAPL',
            'price': 150.0,
            'change': 2.5,
            'change_percent': 1.69,
            'volume': 1000000,
            'previous_close': 147.5,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for field in required_fields:
            assert field in mock_data
        
        # Test data types
        assert isinstance(mock_data['symbol'], str)
        assert isinstance(mock_data['price'], (int, float))
        assert isinstance(mock_data['change'], (int, float))
        assert isinstance(mock_data['change_percent'], (int, float))
        assert isinstance(mock_data['volume'], (int, float))
        assert isinstance(mock_data['previous_close'], (int, float))
        assert isinstance(mock_data['last_updated'], str)
    
    def test_price_validation(self):
        """Test price validation logic"""
        def validate_price_data(data):
            """Validate price data consistency"""
            if data is None:
                return False
            
            # Price should be positive
            if data['price'] <= 0:
                return False
            
            # Change calculation should be consistent
            expected_change = data['price'] - data['previous_close']
            if abs(data['change'] - expected_change) > 0.01:
                return False
            
            # Change percent should be consistent
            if data['previous_close'] != 0:
                expected_change_percent = (data['change'] / data['previous_close']) * 100
                if abs(data['change_percent'] - expected_change_percent) > 0.01:
                    return False
            
            return True
        
        # Test valid data
        valid_data = {
            'symbol': 'AAPL',
            'price': 150.0,
            'change': 2.5,
            'change_percent': 1.69,
            'volume': 1000000,
            'previous_close': 147.5,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        assert validate_price_data(valid_data) == True
        
        # Test invalid data (inconsistent change)
        invalid_data = valid_data.copy()
        invalid_data['change'] = 5.0  # Inconsistent with price and previous_close
        
        assert validate_price_data(invalid_data) == False


if __name__ == '__main__':
    pytest.main([__file__])

