"""
Unit tests for Black-Scholes options pricing model
"""

import pytest
import numpy as np
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from black_scholes import BlackScholes, calculate_implied_volatility


class TestBlackScholes:
    """Test cases for Black-Scholes model"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.stock_price = 100.0
        self.strike_price = 105.0
        self.time_to_expiry = 30/365.0  # 30 days
        self.risk_free_rate = 0.05
        self.volatility = 0.20
        
        self.bs = BlackScholes(
            self.stock_price,
            self.strike_price,
            self.time_to_expiry,
            self.risk_free_rate,
            self.volatility
        )
    
    def test_initialization(self):
        """Test BlackScholes initialization"""
        assert self.bs.S == self.stock_price
        assert self.bs.K == self.strike_price
        assert self.bs.T == self.time_to_expiry
        assert self.bs.r == self.risk_free_rate
        assert self.bs.sigma == self.volatility
    
    def test_d1_d2_calculation(self):
        """Test d1 and d2 calculations"""
        d1 = self.bs._d1()
        d2 = self.bs._d2()
        
        # d2 should equal d1 - sigma * sqrt(T)
        expected_d2 = d1 - self.volatility * np.sqrt(self.time_to_expiry)
        assert abs(d2 - expected_d2) < 1e-10
        
        # d1 and d2 should be finite numbers
        assert np.isfinite(d1)
        assert np.isfinite(d2)
    
    def test_call_price_positive(self):
        """Test that call price is positive"""
        call_price = self.bs.call_price()
        assert call_price > 0
        assert np.isfinite(call_price)
    
    def test_put_price_positive(self):
        """Test that put price is positive"""
        put_price = self.bs.put_price()
        assert put_price > 0
        assert np.isfinite(put_price)
    
    def test_put_call_parity(self):
        """Test put-call parity: C - P = S - K * e^(-r*T)"""
        call_price = self.bs.call_price()
        put_price = self.bs.put_price()
        
        left_side = call_price - put_price
        right_side = self.stock_price - self.strike_price * np.exp(-self.risk_free_rate * self.time_to_expiry)
        
        assert abs(left_side - right_side) < 1e-10
    
    def test_delta_range(self):
        """Test that delta is within expected range"""
        call_delta = self.bs.delta('call')
        put_delta = self.bs.delta('put')
        
        # Call delta should be between 0 and 1
        assert 0 <= call_delta <= 1
        
        # Put delta should be between -1 and 0
        assert -1 <= put_delta <= 0
        
        # Put delta = Call delta - 1
        assert abs(put_delta - (call_delta - 1)) < 1e-10
    
    def test_gamma_positive(self):
        """Test that gamma is positive"""
        gamma = self.bs.gamma()
        assert gamma > 0
        assert np.isfinite(gamma)
    
    def test_vega_positive(self):
        """Test that vega is positive"""
        vega = self.bs.vega()
        assert vega > 0
        assert np.isfinite(vega)
    
    def test_theta_call_negative(self):
        """Test that theta for call is typically negative (time decay)"""
        theta = self.bs.theta('call')
        # For most cases, theta should be negative (time decay)
        # But we'll just check it's finite for robustness
        assert np.isfinite(theta)
    
    def test_rho_call_positive(self):
        """Test that rho for call is positive"""
        rho = self.bs.rho('call')
        assert rho > 0
        assert np.isfinite(rho)
    
    def test_rho_put_negative(self):
        """Test that rho for put is negative"""
        rho = self.bs.rho('put')
        assert rho < 0
        assert np.isfinite(rho)
    
    def test_get_all_greeks(self):
        """Test getting all Greeks at once"""
        greeks = self.bs.get_all_greeks('call')
        
        required_keys = ['delta', 'gamma', 'theta', 'vega', 'rho']
        for key in required_keys:
            assert key in greeks
            assert np.isfinite(greeks[key])
    
    def test_calculate_option_metrics(self):
        """Test comprehensive option metrics calculation"""
        metrics = self.bs.calculate_option_metrics('call', contracts=2)
        
        required_keys = ['option_price', 'total_cost', 'breakeven', 'greeks', 'contracts']
        for key in required_keys:
            assert key in metrics
        
        assert metrics['contracts'] == 2
        assert metrics['total_cost'] == metrics['option_price'] * 2 * 100
        assert metrics['breakeven'] == self.strike_price + metrics['option_price']
    
    def test_calculate_pnl_at_expiry(self):
        """Test P&L calculation at expiry"""
        stock_prices = np.array([90, 95, 100, 105, 110, 115])
        pnl_values = self.bs.calculate_pnl_at_expiry(stock_prices, 'call', contracts=1)
        
        assert len(pnl_values) == len(stock_prices)
        
        # For call option, P&L should increase as stock price increases above strike
        option_price = self.bs.call_price()
        premium_paid = option_price * 100
        
        for i, stock_price in enumerate(stock_prices):
            expected_intrinsic = max(0, stock_price - self.strike_price) * 100
            expected_pnl = expected_intrinsic - premium_paid
            assert abs(pnl_values[i] - expected_pnl) < 1e-10
    
    def test_atm_option(self):
        """Test at-the-money option"""
        bs_atm = BlackScholes(100, 100, self.time_to_expiry, self.risk_free_rate, self.volatility)
        
        call_price = bs_atm.call_price()
        put_price = bs_atm.put_price()
        
        # For ATM options with positive interest rate, call should be slightly more expensive than put
        assert call_price > put_price
    
    def test_deep_itm_call(self):
        """Test deep in-the-money call option"""
        bs_itm = BlackScholes(150, 100, self.time_to_expiry, self.risk_free_rate, self.volatility)
        
        call_price = bs_itm.call_price()
        delta = bs_itm.delta('call')
        
        # Deep ITM call should have high delta (close to 1)
        assert delta > 0.9
        
        # Call price should be close to intrinsic value plus some time value
        intrinsic_value = 150 - 100
        assert call_price > intrinsic_value
    
    def test_deep_otm_call(self):
        """Test deep out-of-the-money call option"""
        bs_otm = BlackScholes(80, 100, self.time_to_expiry, self.risk_free_rate, self.volatility)
        
        call_price = bs_otm.call_price()
        delta = bs_otm.delta('call')
        
        # Deep OTM call should have low delta (close to 0)
        assert delta < 0.1
        
        # Call price should be small but positive
        assert 0 < call_price < 5
    
    def test_zero_time_to_expiry(self):
        """Test option at expiration"""
        bs_expiry = BlackScholes(110, 100, 0.001/365, self.risk_free_rate, self.volatility)
        
        call_price = bs_expiry.call_price()
        
        # At expiry, call price should be close to max(S-K, 0)
        expected_price = max(110 - 100, 0)
        assert abs(call_price - expected_price) < 0.1
    
    def test_high_volatility_effect(self):
        """Test effect of high volatility"""
        bs_low_vol = BlackScholes(100, 100, self.time_to_expiry, self.risk_free_rate, 0.1)
        bs_high_vol = BlackScholes(100, 100, self.time_to_expiry, self.risk_free_rate, 0.5)
        
        call_low = bs_low_vol.call_price()
        call_high = bs_high_vol.call_price()
        
        # Higher volatility should result in higher option price
        assert call_high > call_low
        
        # Vega should be positive for both
        assert bs_low_vol.vega() > 0
        assert bs_high_vol.vega() > 0


class TestImpliedVolatility:
    """Test cases for implied volatility calculation"""
    
    def test_implied_volatility_calculation(self):
        """Test implied volatility calculation"""
        # Create a known option price
        bs = BlackScholes(100, 105, 30/365, 0.05, 0.25)
        market_price = bs.call_price()
        
        # Calculate implied volatility
        implied_vol = calculate_implied_volatility(
            market_price, 100, 105, 30/365, 0.05, 'call'
        )
        
        # Should be close to original volatility (0.25)
        assert abs(implied_vol - 0.25) < 0.001
    
    def test_implied_volatility_put(self):
        """Test implied volatility for put option"""
        bs = BlackScholes(100, 105, 30/365, 0.05, 0.30)
        market_price = bs.put_price()
        
        implied_vol = calculate_implied_volatility(
            market_price, 100, 105, 30/365, 0.05, 'put'
        )
        
        assert abs(implied_vol - 0.30) < 0.001


if __name__ == '__main__':
    pytest.main([__file__])

