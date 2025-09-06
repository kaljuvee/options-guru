"""
Unified data provider interface for market data
"""

from yfinance_utils import YFinanceDataProvider
import logging

# Optional imports with error handling
try:
    from polygon_utils import PolygonDataProvider
    POLYGON_AVAILABLE = True
except ImportError:
    POLYGON_AVAILABLE = False
    logging.warning("Polygon API not available. Install polygon-api-client to enable.")

try:
    from alpaca_utils import AlpacaDataProvider
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logging.warning("Alpaca API not available. Install alpaca-trade-api to enable.")

logger = logging.getLogger(__name__)


class DataProviderManager:
    """Manages multiple data providers with fallback support"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = 'yfinance'
        self.current_provider = 'yfinance'
        
        # Always available
        self.providers['yfinance'] = YFinanceDataProvider()
        
        # Optional providers
        if POLYGON_AVAILABLE:
            self.providers['polygon'] = PolygonDataProvider()
        
        if ALPACA_AVAILABLE:
            self.providers['alpaca'] = AlpacaDataProvider()
    
    def get_available_providers(self):
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    def set_provider(self, provider_name):
        """Set the current data provider"""
        if provider_name in self.providers:
            self.current_provider = provider_name
            logger.info(f"Switched to {provider_name} data provider")
        else:
            available = ', '.join(self.get_available_providers())
            logger.warning(f"Provider {provider_name} not available. Available providers: {available}")
    
    def get_provider(self):
        """Get the current data provider instance"""
        return self.providers[self.current_provider]
    
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


# Global data provider instance
data_provider = DataProviderManager()

