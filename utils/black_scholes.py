"""
Black-Scholes Options Pricing Model Implementation
"""

import numpy as np
from scipy.stats import norm
import math


class BlackScholes:
    """Black-Scholes options pricing model with Greeks calculations"""
    
    def __init__(self, stock_price, strike_price, time_to_expiry, risk_free_rate, volatility):
        """
        Initialize Black-Scholes parameters
        
        Args:
            stock_price (float): Current stock price
            strike_price (float): Option strike price
            time_to_expiry (float): Time to expiration in years
            risk_free_rate (float): Risk-free interest rate (as decimal)
            volatility (float): Implied volatility (as decimal)
        """
        self.S = stock_price
        self.K = strike_price
        self.T = time_to_expiry
        self.r = risk_free_rate
        self.sigma = volatility
        
    def _d1(self):
        """Calculate d1 parameter"""
        return (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))
    
    def _d2(self):
        """Calculate d2 parameter"""
        return self._d1() - self.sigma * np.sqrt(self.T)
    
    def call_price(self):
        """Calculate call option price"""
        d1 = self._d1()
        d2 = self._d2()
        
        call_price = (self.S * norm.cdf(d1) - 
                     self.K * np.exp(-self.r * self.T) * norm.cdf(d2))
        return call_price
    
    def put_price(self):
        """Calculate put option price"""
        d1 = self._d1()
        d2 = self._d2()
        
        put_price = (self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - 
                    self.S * norm.cdf(-d1))
        return put_price
    
    def delta(self, option_type='call'):
        """Calculate Delta (price sensitivity to underlying price change)"""
        d1 = self._d1()
        
        if option_type.lower() == 'call':
            return norm.cdf(d1)
        else:  # put
            return norm.cdf(d1) - 1
    
    def gamma(self):
        """Calculate Gamma (rate of change of Delta)"""
        d1 = self._d1()
        return norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
    
    def theta(self, option_type='call'):
        """Calculate Theta (time decay)"""
        d1 = self._d1()
        d2 = self._d2()
        
        if option_type.lower() == 'call':
            theta = (-(self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T)) -
                    self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2))
        else:  # put
            theta = (-(self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T)) +
                    self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2))
        
        return theta / 365  # Convert to daily theta
    
    def vega(self):
        """Calculate Vega (sensitivity to volatility)"""
        d1 = self._d1()
        return self.S * norm.pdf(d1) * np.sqrt(self.T) / 100  # Divide by 100 for 1% change
    
    def rho(self, option_type='call'):
        """Calculate Rho (sensitivity to interest rate)"""
        d2 = self._d2()
        
        if option_type.lower() == 'call':
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2) / 100
        else:  # put
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2) / 100
    
    def get_all_greeks(self, option_type='call'):
        """Get all Greeks in a dictionary"""
        return {
            'delta': self.delta(option_type),
            'gamma': self.gamma(),
            'theta': self.theta(option_type),
            'vega': self.vega(),
            'rho': self.rho(option_type)
        }
    
    def calculate_option_metrics(self, option_type='call', contracts=1):
        """Calculate comprehensive option metrics"""
        if option_type.lower() == 'call':
            option_price = self.call_price()
        else:
            option_price = self.put_price()
        
        greeks = self.get_all_greeks(option_type)
        total_cost = option_price * contracts * 100  # Standard contract size
        
        # Calculate breakeven
        if option_type.lower() == 'call':
            breakeven = self.K + option_price
        else:
            breakeven = self.K - option_price
        
        return {
            'option_price': option_price,
            'total_cost': total_cost,
            'breakeven': breakeven,
            'greeks': greeks,
            'contracts': contracts
        }
    
    def calculate_pnl_at_expiry(self, stock_prices, option_type='call', contracts=1):
        """Calculate P&L at different stock prices at expiry"""
        if option_type.lower() == 'call':
            option_price = self.call_price()
        else:
            option_price = self.put_price()
        
        premium_paid = option_price * contracts * 100
        pnl_values = []
        
        for price in stock_prices:
            if option_type.lower() == 'call':
                intrinsic_value = max(0, price - self.K) * contracts * 100
            else:
                intrinsic_value = max(0, self.K - price) * contracts * 100
            
            pnl = intrinsic_value - premium_paid
            pnl_values.append(pnl)
        
        return pnl_values


def calculate_implied_volatility(market_price, stock_price, strike_price, 
                               time_to_expiry, risk_free_rate, option_type='call'):
    """
    Calculate implied volatility using Newton-Raphson method
    """
    def bs_price(vol):
        bs = BlackScholes(stock_price, strike_price, time_to_expiry, risk_free_rate, vol)
        if option_type.lower() == 'call':
            return bs.call_price()
        else:
            return bs.put_price()
    
    def bs_vega(vol):
        bs = BlackScholes(stock_price, strike_price, time_to_expiry, risk_free_rate, vol)
        return bs.vega() * 100  # Convert back to full vega
    
    # Initial guess
    vol = 0.2
    tolerance = 1e-6
    max_iterations = 100
    
    for i in range(max_iterations):
        price_diff = bs_price(vol) - market_price
        
        if abs(price_diff) < tolerance:
            return vol
        
        vega = bs_vega(vol)
        if vega == 0:
            break
            
        vol = vol - price_diff / vega
        
        # Keep volatility positive
        if vol <= 0:
            vol = 0.01
    
    return vol

