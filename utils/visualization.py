"""
Advanced visualization utilities for Options Guru
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from black_scholes import BlackScholes


def create_3d_option_surface(stock_prices, volatilities, time_to_expiry, strike_price, risk_free_rate, option_type='call'):
    """
    Create 3D option price surface
    
    Args:
        stock_prices (array): Range of stock prices
        volatilities (array): Range of volatilities
        time_to_expiry (float): Time to expiration in years
        strike_price (float): Strike price
        risk_free_rate (float): Risk-free rate
        option_type (str): 'call' or 'put'
    
    Returns:
        plotly.graph_objects.Figure: 3D surface plot
    """
    # Create meshgrid
    S_mesh, vol_mesh = np.meshgrid(stock_prices, volatilities)
    
    # Calculate option prices for each combination
    option_prices = np.zeros_like(S_mesh)
    
    for i in range(len(volatilities)):
        for j in range(len(stock_prices)):
            bs = BlackScholes(
                stock_prices[j],
                strike_price,
                time_to_expiry,
                risk_free_rate,
                volatilities[i]
            )
            if option_type.lower() == 'call':
                option_prices[i, j] = bs.call_price()
            else:
                option_prices[i, j] = bs.put_price()
    
    # Create 3D surface
    fig = go.Figure(data=[go.Surface(
        x=S_mesh,
        y=vol_mesh * 100,  # Convert to percentage
        z=option_prices,
        colorscale='Viridis',
        name='Option Price'
    )])
    
    fig.update_layout(
        title=f'3D {option_type.title()} Option Price Surface',
        scene=dict(
            xaxis_title='Stock Price ($)',
            yaxis_title='Volatility (%)',
            zaxis_title='Option Price ($)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=600
    )
    
    return fig


def create_greeks_3d_surface(stock_prices, volatilities, time_to_expiry, strike_price, risk_free_rate, greek='delta', option_type='call'):
    """
    Create 3D surface for Greeks
    
    Args:
        stock_prices (array): Range of stock prices
        volatilities (array): Range of volatilities
        time_to_expiry (float): Time to expiration in years
        strike_price (float): Strike price
        risk_free_rate (float): Risk-free rate
        greek (str): Greek to plot ('delta', 'gamma', 'theta', 'vega', 'rho')
        option_type (str): 'call' or 'put'
    
    Returns:
        plotly.graph_objects.Figure: 3D surface plot
    """
    # Create meshgrid
    S_mesh, vol_mesh = np.meshgrid(stock_prices, volatilities)
    
    # Calculate Greek values for each combination
    greek_values = np.zeros_like(S_mesh)
    
    for i in range(len(volatilities)):
        for j in range(len(stock_prices)):
            bs = BlackScholes(
                stock_prices[j],
                strike_price,
                time_to_expiry,
                risk_free_rate,
                volatilities[i]
            )
            
            if greek.lower() == 'delta':
                greek_values[i, j] = bs.delta(option_type)
            elif greek.lower() == 'gamma':
                greek_values[i, j] = bs.gamma()
            elif greek.lower() == 'theta':
                greek_values[i, j] = bs.theta(option_type)
            elif greek.lower() == 'vega':
                greek_values[i, j] = bs.vega()
            elif greek.lower() == 'rho':
                greek_values[i, j] = bs.rho(option_type)
    
    # Create 3D surface
    fig = go.Figure(data=[go.Surface(
        x=S_mesh,
        y=vol_mesh * 100,  # Convert to percentage
        z=greek_values,
        colorscale='RdYlBu',
        name=f'{greek.title()}'
    )])
    
    fig.update_layout(
        title=f'3D {greek.title()} Surface - {option_type.title()} Option',
        scene=dict(
            xaxis_title='Stock Price ($)',
            yaxis_title='Volatility (%)',
            zaxis_title=f'{greek.title()}',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=600
    )
    
    return fig


def create_time_decay_heatmap(stock_prices, days_to_expiry_range, strike_price, volatility, risk_free_rate, option_type='call'):
    """
    Create heatmap showing time decay effects
    
    Args:
        stock_prices (array): Range of stock prices
        days_to_expiry_range (array): Range of days to expiry
        strike_price (float): Strike price
        volatility (float): Volatility
        risk_free_rate (float): Risk-free rate
        option_type (str): 'call' or 'put'
    
    Returns:
        plotly.graph_objects.Figure: Heatmap
    """
    # Create matrix for option prices
    option_matrix = np.zeros((len(days_to_expiry_range), len(stock_prices)))
    
    for i, days in enumerate(days_to_expiry_range):
        time_to_expiry = days / 365.0
        for j, stock_price in enumerate(stock_prices):
            bs = BlackScholes(
                stock_price,
                strike_price,
                time_to_expiry,
                risk_free_rate,
                volatility
            )
            if option_type.lower() == 'call':
                option_matrix[i, j] = bs.call_price()
            else:
                option_matrix[i, j] = bs.put_price()
    
    fig = go.Figure(data=go.Heatmap(
        x=stock_prices,
        y=days_to_expiry_range,
        z=option_matrix,
        colorscale='Viridis',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=f'Time Decay Heatmap - {option_type.title()} Option',
        xaxis_title='Stock Price ($)',
        yaxis_title='Days to Expiry',
        height=500
    )
    
    return fig


def create_volatility_smile(strike_prices, market_volatilities, stock_price, time_to_expiry, risk_free_rate):
    """
    Create volatility smile chart
    
    Args:
        strike_prices (array): Array of strike prices
        market_volatilities (array): Corresponding market volatilities
        stock_price (float): Current stock price
        time_to_expiry (float): Time to expiration
        risk_free_rate (float): Risk-free rate
    
    Returns:
        plotly.graph_objects.Figure: Volatility smile chart
    """
    # Calculate moneyness (K/S)
    moneyness = strike_prices / stock_price
    
    fig = go.Figure()
    
    # Add volatility smile
    fig.add_trace(go.Scatter(
        x=moneyness,
        y=market_volatilities * 100,
        mode='lines+markers',
        name='Implied Volatility',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    # Add ATM line
    fig.add_vline(x=1.0, line_dash="dash", line_color="red", annotation_text="ATM")
    
    fig.update_layout(
        title='Volatility Smile',
        xaxis_title='Moneyness (Strike/Stock Price)',
        yaxis_title='Implied Volatility (%)',
        height=400,
        showlegend=True
    )
    
    return fig


def create_pnl_heatmap(stock_prices, days_to_expiry_range, current_stock_price, strike_price, 
                      volatility, risk_free_rate, option_type='call', position='long'):
    """
    Create P&L heatmap over time and stock price
    
    Args:
        stock_prices (array): Range of stock prices
        days_to_expiry_range (array): Range of days to expiry
        current_stock_price (float): Current stock price
        strike_price (float): Strike price
        volatility (float): Volatility
        risk_free_rate (float): Risk-free rate
        option_type (str): 'call' or 'put'
        position (str): 'long' or 'short'
    
    Returns:
        plotly.graph_objects.Figure: P&L heatmap
    """
    # Calculate initial option price
    initial_time = max(days_to_expiry_range) / 365.0
    bs_initial = BlackScholes(current_stock_price, strike_price, initial_time, risk_free_rate, volatility)
    
    if option_type.lower() == 'call':
        initial_price = bs_initial.call_price()
    else:
        initial_price = bs_initial.put_price()
    
    # Create P&L matrix
    pnl_matrix = np.zeros((len(days_to_expiry_range), len(stock_prices)))
    
    for i, days in enumerate(days_to_expiry_range):
        time_to_expiry = days / 365.0
        for j, stock_price in enumerate(stock_prices):
            bs = BlackScholes(stock_price, strike_price, time_to_expiry, risk_free_rate, volatility)
            
            if option_type.lower() == 'call':
                current_price = bs.call_price()
            else:
                current_price = bs.put_price()
            
            if position.lower() == 'long':
                pnl = current_price - initial_price
            else:
                pnl = initial_price - current_price
            
            pnl_matrix[i, j] = pnl
    
    fig = go.Figure(data=go.Heatmap(
        x=stock_prices,
        y=days_to_expiry_range,
        z=pnl_matrix,
        colorscale='RdYlGn',
        zmid=0,
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=f'P&L Heatmap - {position.title()} {option_type.title()} Option',
        xaxis_title='Stock Price ($)',
        yaxis_title='Days to Expiry',
        height=500
    )
    
    return fig


def create_multi_strike_pnl(stock_prices, strikes, time_to_expiry, volatility, risk_free_rate, option_type='call'):
    """
    Create P&L chart for multiple strikes
    
    Args:
        stock_prices (array): Range of stock prices
        strikes (list): List of strike prices
        time_to_expiry (float): Time to expiration
        volatility (float): Volatility
        risk_free_rate (float): Risk-free rate
        option_type (str): 'call' or 'put'
    
    Returns:
        plotly.graph_objects.Figure: Multi-strike P&L chart
    """
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, strike in enumerate(strikes):
        bs = BlackScholes(stock_prices[0], strike, time_to_expiry, risk_free_rate, volatility)
        
        if option_type.lower() == 'call':
            initial_price = bs.call_price()
        else:
            initial_price = bs.put_price()
        
        pnl_values = []
        for stock_price in stock_prices:
            if option_type.lower() == 'call':
                intrinsic = max(0, stock_price - strike)
            else:
                intrinsic = max(0, strike - stock_price)
            
            pnl = intrinsic - initial_price
            pnl_values.append(pnl)
        
        fig.add_trace(go.Scatter(
            x=stock_prices,
            y=pnl_values,
            mode='lines',
            name=f'Strike ${strike}',
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    # Add breakeven line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break Even")
    
    fig.update_layout(
        title=f'Multi-Strike P&L Comparison - {option_type.title()} Options',
        xaxis_title='Stock Price at Expiration ($)',
        yaxis_title='Profit/Loss ($)',
        height=500,
        showlegend=True
    )
    
    return fig


def create_greeks_dashboard(stock_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type='call'):
    """
    Create comprehensive Greeks dashboard
    
    Args:
        stock_price (float): Current stock price
        strike_price (float): Strike price
        time_to_expiry (float): Time to expiration
        risk_free_rate (float): Risk-free rate
        volatility (float): Volatility
        option_type (str): 'call' or 'put'
    
    Returns:
        plotly.graph_objects.Figure: Greeks dashboard
    """
    # Create subplots
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=('Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'Option Price'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Stock price range
    stock_range = np.linspace(stock_price * 0.7, stock_price * 1.3, 50)
    
    # Calculate Greeks for each stock price
    deltas, gammas, thetas, vegas, rhos, prices = [], [], [], [], [], []
    
    for s in stock_range:
        bs = BlackScholes(s, strike_price, time_to_expiry, risk_free_rate, volatility)
        
        deltas.append(bs.delta(option_type))
        gammas.append(bs.gamma())
        thetas.append(bs.theta(option_type))
        vegas.append(bs.vega())
        rhos.append(bs.rho(option_type))
        
        if option_type.lower() == 'call':
            prices.append(bs.call_price())
        else:
            prices.append(bs.put_price())
    
    # Add traces
    fig.add_trace(go.Scatter(x=stock_range, y=deltas, name='Delta', line=dict(color='green')), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_range, y=gammas, name='Gamma', line=dict(color='purple')), row=1, col=2)
    fig.add_trace(go.Scatter(x=stock_range, y=thetas, name='Theta', line=dict(color='red')), row=1, col=3)
    fig.add_trace(go.Scatter(x=stock_range, y=vegas, name='Vega', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=stock_range, y=rhos, name='Rho', line=dict(color='orange')), row=2, col=2)
    fig.add_trace(go.Scatter(x=stock_range, y=prices, name='Price', line=dict(color='black')), row=2, col=3)
    
    # Add current stock price line to all subplots
    for row in range(1, 3):
        for col in range(1, 4):
            fig.add_vline(x=stock_price, line_dash="dot", line_color="gray", row=row, col=col)
    
    fig.update_layout(
        title=f'Greeks Dashboard - {option_type.title()} Option',
        height=600,
        showlegend=False
    )
    
    return fig


def create_strategy_comparison(strategies_data, stock_prices):
    """
    Create strategy comparison chart
    
    Args:
        strategies_data (list): List of strategy dictionaries
        stock_prices (array): Range of stock prices
    
    Returns:
        plotly.graph_objects.Figure: Strategy comparison chart
    """
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, strategy in enumerate(strategies_data):
        fig.add_trace(go.Scatter(
            x=stock_prices,
            y=strategy['pnl'],
            mode='lines',
            name=strategy['name'],
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    # Add breakeven line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break Even")
    
    fig.update_layout(
        title='Options Strategy Comparison',
        xaxis_title='Stock Price at Expiration ($)',
        yaxis_title='Profit/Loss ($)',
        height=500,
        showlegend=True
    )
    
    return fig

