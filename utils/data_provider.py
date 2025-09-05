"""
Unified data provider interface for market data
"""

from yfinance_utils import YFinanceDataProvider
from polygon_utils import PolygonDataProvider
from alpaca_utils import AlpacaDataProvider
import logging

logger = logging.getLogger(__name__)


class DataProviderManager:
    """Manages multiple data providers and provides unified interface"""
    
    def __init__(self, default_provider='yfinance'):
        self.providers = {
            'yfinance': YFinanceDataProvider(),
            'polygon': PolygonDataProvider(),
            'alpaca': AlpacaDataProvider()
        }
        self.default_provider = default_provider
        self.current_provider = default_provider
    
    def set_provider(self, provider_name):
        """Set the current data provider"""
        if provider_name in self.providers:
            self.current_provider = provider_name
            logger.info(f"Switched to {provider_name} data provider")
        else:
            logger.error(f"Provider {provider_name} not available")
    
    def get_provider(self):
        """Get the current data provider"""
        return self.providers[self.current_provider]
    
    def get_available_providers(self):
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_stock_data(self, symbol, provider=None):
        """Get stock data using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            return self.providers[provider_name].get_stock_data(symbol)
        except Exception as e:
            logger.error(f"Error getting stock data from {provider_name}: {str(e)}")
            # Try fallback providers
            for fallback_provider in self.providers:
                if fallback_provider != provider_name:
                    try:
                        logger.info(f"Trying fallback provider: {fallback_provider}")
                        return self.providers[fallback_provider].get_stock_data(symbol)
                    except Exception as fallback_e:
                        logger.error(f"Fallback provider {fallback_provider} also failed: {str(fallback_e)}")
                        continue
            return None
    
    def get_historical_data(self, symbol, start_date, end_date, provider=None):
        """Get historical data using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            return self.providers[provider_name].get_historical_data(symbol, start_date, end_date)
        except Exception as e:
            logger.error(f"Error getting historical data from {provider_name}: {str(e)}")
            return None
    
    def calculate_historical_volatility(self, symbol, days=30, provider=None):
        """Calculate historical volatility using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            return self.providers[provider_name].calculate_historical_volatility(symbol, days)
        except Exception as e:
            logger.error(f"Error calculating volatility from {provider_name}: {str(e)}")
            # Try fallback providers
            for fallback_provider in self.providers:
                if fallback_provider != provider_name:
                    try:
                        logger.info(f"Trying fallback provider for volatility: {fallback_provider}")
                        return self.providers[fallback_provider].calculate_historical_volatility(symbol, days)
                    except Exception as fallback_e:
                        logger.error(f"Fallback provider {fallback_provider} also failed: {str(fallback_e)}")
                        continue
            return None
    
    def get_market_overview(self, provider=None):
        """Get market overview using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            return self.providers[provider_name].get_market_overview()
        except Exception as e:
            logger.error(f"Error getting market overview from {provider_name}: {str(e)}")
            return {}
    
    def get_options_chain(self, symbol, expiration_date=None, provider=None):
        """Get options chain using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            provider_obj = self.providers[provider_name]
            if hasattr(provider_obj, 'get_options_chain'):
                return provider_obj.get_options_chain(symbol, expiration_date)
            else:
                logger.warning(f"Provider {provider_name} does not support options chain")
                return None
        except Exception as e:
            logger.error(f"Error getting options chain from {provider_name}: {str(e)}")
            return None
    
    def search_stocks(self, query, provider=None):
        """Search stocks using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            provider_obj = self.providers[provider_name]
            if hasattr(provider_obj, 'search_stocks'):
                return provider_obj.search_stocks(query)
            else:
                logger.warning(f"Provider {provider_name} does not support stock search")
                return []
        except Exception as e:
            logger.error(f"Error searching stocks from {provider_name}: {str(e)}")
            return []
    
    def get_company_info(self, symbol, provider=None):
        """Get company info using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            provider_obj = self.providers[provider_name]
            if hasattr(provider_obj, 'get_company_info'):
                return provider_obj.get_company_info(symbol)
            else:
                logger.warning(f"Provider {provider_name} does not support company info")
                return None
        except Exception as e:
            logger.error(f"Error getting company info from {provider_name}: {str(e)}")
            return None
    
    def get_risk_free_rate(self, provider=None):
        """Get risk-free rate using specified or current provider"""
        provider_name = provider or self.current_provider
        if provider_name not in self.providers:
            provider_name = self.default_provider
        
        try:
            provider_obj = self.providers[provider_name]
            if hasattr(provider_obj, 'get_risk_free_rate'):
                return provider_obj.get_risk_free_rate()
            else:
                # Default risk-free rate if provider doesn't support it
                return 0.05
        except Exception as e:
            logger.error(f"Error getting risk-free rate from {provider_name}: {str(e)}")
            return 0.05  # Default 5%


# Global data provider instance
data_provider = DataProviderManager()


# Convenience functions
def get_current_price(symbol, provider=None):
    """Get current stock price"""
    data = data_provider.get_stock_data(symbol, provider)
    return data['price'] if data else None


def get_historical_volatility(symbol, days=30, provider=None):
    """Get historical volatility"""
    return data_provider.calculate_historical_volatility(symbol, days, provider)


def get_risk_free_rate(provider=None):
    """Get current risk-free rate"""
    return data_provider.get_risk_free_rate(provider)

