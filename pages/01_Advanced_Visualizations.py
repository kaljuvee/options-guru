"""
Advanced Visualizations Page for Options Guru
"""

import streamlit as st
import numpy as np
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from visualization import (
    create_3d_option_surface,
    create_greeks_3d_surface,
    create_time_decay_heatmap,
    create_volatility_smile,
    create_pnl_heatmap,
    create_multi_strike_pnl,
    create_greeks_dashboard,
    create_strategy_comparison
)
from black_scholes import BlackScholes

st.set_page_config(
    page_title="Advanced Visualizations - Options Guru",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Advanced Options Visualizations")
st.markdown("Explore advanced 3D visualizations and analytical tools for options trading")

# Sidebar parameters
st.sidebar.header("Visualization Parameters")

# Basic parameters
stock_price = st.sidebar.number_input("Stock Price ($)", min_value=1.0, value=100.0, step=1.0)
strike_price = st.sidebar.number_input("Strike Price ($)", min_value=1.0, value=105.0, step=1.0)
days_to_expiry = st.sidebar.number_input("Days to Expiry", min_value=1, value=30, step=1)
volatility = st.sidebar.number_input("Volatility (%)", min_value=1.0, value=20.0, step=1.0) / 100
risk_free_rate = st.sidebar.number_input("Risk-Free Rate (%)", min_value=0.0, value=5.0, step=0.1) / 100
option_type = st.sidebar.selectbox("Option Type", ["call", "put"])

time_to_expiry = days_to_expiry / 365.0

# Tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏔️ 3D Surfaces", 
    "🔥 Heatmaps", 
    "📈 Greeks Dashboard", 
    "📊 Multi-Analysis", 
    "🎯 Strategy Comparison"
])

with tab1:
    st.header("3D Option Price and Greeks Surfaces")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("3D Option Price Surface")
        
        # Parameters for 3D surface
        stock_range = np.linspace(stock_price * 0.5, stock_price * 1.5, 20)
        vol_range = np.linspace(0.1, 0.8, 20)
        
        # Create 3D option surface
        fig_3d_price = create_3d_option_surface(
            stock_range, vol_range, time_to_expiry, strike_price, risk_free_rate, option_type
        )
        st.plotly_chart(fig_3d_price, use_container_width=True)
    
    with col2:
        st.subheader("3D Greeks Surface")
        
        greek_choice = st.selectbox("Select Greek", ["delta", "gamma", "theta", "vega", "rho"])
        
        # Create 3D Greeks surface
        fig_3d_greek = create_greeks_3d_surface(
            stock_range, vol_range, time_to_expiry, strike_price, risk_free_rate, greek_choice, option_type
        )
        st.plotly_chart(fig_3d_greek, use_container_width=True)
    
    # Additional 3D visualization controls
    st.markdown("---")
    st.subheader("Interactive 3D Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stock_min = st.number_input("Min Stock Price", value=stock_price * 0.5, step=1.0)
        stock_max = st.number_input("Max Stock Price", value=stock_price * 1.5, step=1.0)
    
    with col2:
        vol_min = st.number_input("Min Volatility", value=0.1, step=0.05, format="%.2f")
        vol_max = st.number_input("Max Volatility", value=0.8, step=0.05, format="%.2f")
    
    with col3:
        resolution = st.slider("Surface Resolution", min_value=10, max_value=50, value=20)
    
    if st.button("Update 3D Surfaces"):
        # Update ranges
        stock_range = np.linspace(stock_min, stock_max, resolution)
        vol_range = np.linspace(vol_min, vol_max, resolution)
        
        # Recreate surfaces with new parameters
        col1, col2 = st.columns(2)
        
        with col1:
            fig_3d_price_updated = create_3d_option_surface(
                stock_range, vol_range, time_to_expiry, strike_price, risk_free_rate, option_type
            )
            st.plotly_chart(fig_3d_price_updated, use_container_width=True)
        
        with col2:
            fig_3d_greek_updated = create_greeks_3d_surface(
                stock_range, vol_range, time_to_expiry, strike_price, risk_free_rate, greek_choice, option_type
            )
            st.plotly_chart(fig_3d_greek_updated, use_container_width=True)

with tab2:
    st.header("Heatmap Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Time Decay Heatmap")
        
        # Parameters for heatmap
        stock_range_hm = np.linspace(stock_price * 0.8, stock_price * 1.2, 20)
        days_range = np.arange(1, 61, 2)  # 1 to 60 days
        
        fig_time_decay = create_time_decay_heatmap(
            stock_range_hm, days_range, strike_price, volatility, risk_free_rate, option_type
        )
        st.plotly_chart(fig_time_decay, use_container_width=True)
    
    with col2:
        st.subheader("P&L Heatmap")
        
        position = st.selectbox("Position", ["long", "short"], key="pnl_position")
        
        fig_pnl_heatmap = create_pnl_heatmap(
            stock_range_hm, days_range, stock_price, strike_price, 
            volatility, risk_free_rate, option_type, position
        )
        st.plotly_chart(fig_pnl_heatmap, use_container_width=True)
    
    # Volatility Smile
    st.markdown("---")
    st.subheader("Volatility Smile")
    
    # Generate sample volatility smile data
    strikes = np.linspace(stock_price * 0.8, stock_price * 1.2, 11)
    # Simulate volatility smile (higher vol for OTM options)
    atm_vol = volatility
    vols = []
    for k in strikes:
        moneyness = k / stock_price
        if moneyness < 0.95 or moneyness > 1.05:  # OTM options
            vol_adjustment = 0.02 * abs(moneyness - 1) ** 0.5
        else:  # ATM options
            vol_adjustment = 0
        vols.append(atm_vol + vol_adjustment)
    
    fig_vol_smile = create_volatility_smile(strikes, np.array(vols), stock_price, time_to_expiry, risk_free_rate)
    st.plotly_chart(fig_vol_smile, use_container_width=True)

with tab3:
    st.header("Comprehensive Greeks Dashboard")
    
    # Greeks dashboard
    fig_greeks_dashboard = create_greeks_dashboard(
        stock_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type
    )
    st.plotly_chart(fig_greeks_dashboard, use_container_width=True)
    
    # Greeks sensitivity analysis
    st.markdown("---")
    st.subheader("Greeks Sensitivity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Greeks Values**")
        bs = BlackScholes(stock_price, strike_price, time_to_expiry, risk_free_rate, volatility)
        
        delta = bs.delta(option_type)
        gamma = bs.gamma()
        theta = bs.theta(option_type)
        vega = bs.vega()
        rho = bs.rho(option_type)
        
        st.metric("Delta", f"{delta:.4f}")
        st.metric("Gamma", f"{gamma:.4f}")
        st.metric("Theta", f"{theta:.4f}")
        st.metric("Vega", f"{vega:.4f}")
        st.metric("Rho", f"{rho:.4f}")
    
    with col2:
        st.markdown("**Greeks Interpretation**")
        
        # Delta interpretation
        if abs(delta) > 0.7:
            delta_interp = "High price sensitivity"
        elif abs(delta) > 0.3:
            delta_interp = "Moderate price sensitivity"
        else:
            delta_interp = "Low price sensitivity"
        
        # Gamma interpretation
        if gamma > 0.05:
            gamma_interp = "High gamma - Delta changes rapidly"
        elif gamma > 0.02:
            gamma_interp = "Moderate gamma"
        else:
            gamma_interp = "Low gamma - Delta stable"
        
        # Theta interpretation
        if abs(theta) > 0.05:
            theta_interp = "High time decay"
        elif abs(theta) > 0.02:
            theta_interp = "Moderate time decay"
        else:
            theta_interp = "Low time decay"
        
        st.write(f"**Delta:** {delta_interp}")
        st.write(f"**Gamma:** {gamma_interp}")
        st.write(f"**Theta:** {theta_interp}")
        st.write(f"**Vega:** Volatility sensitivity of {vega:.4f}")
        st.write(f"**Rho:** Interest rate sensitivity of {rho:.4f}")

with tab4:
    st.header("Multi-Strike and Multi-Expiry Analysis")
    
    # Multi-strike P&L comparison
    st.subheader("Multi-Strike P&L Comparison")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("**Strike Selection**")
        num_strikes = st.slider("Number of Strikes", min_value=2, max_value=5, value=3)
        
        strikes = []
        for i in range(num_strikes):
            strike = st.number_input(
                f"Strike {i+1} ($)", 
                min_value=1.0, 
                value=stock_price + (i-1) * 5, 
                step=1.0,
                key=f"strike_{i}"
            )
            strikes.append(strike)
    
    with col2:
        stock_range_multi = np.linspace(stock_price * 0.7, stock_price * 1.3, 100)
        
        fig_multi_strike = create_multi_strike_pnl(
            stock_range_multi, strikes, time_to_expiry, volatility, risk_free_rate, option_type
        )
        st.plotly_chart(fig_multi_strike, use_container_width=True)
    
    # Multi-expiry analysis
    st.markdown("---")
    st.subheader("Multi-Expiry Analysis")
    
    expiry_days = [7, 14, 30, 60, 90]
    stock_range_exp = np.linspace(stock_price * 0.8, stock_price * 1.2, 50)
    
    import plotly.graph_objects as go
    fig_multi_exp = go.Figure()
    
    colors = ['red', 'orange', 'green', 'blue', 'purple']
    
    for i, days in enumerate(expiry_days):
        time_exp = days / 365.0
        pnl_values = []
        
        bs_initial = BlackScholes(stock_price, strike_price, time_exp, risk_free_rate, volatility)
        if option_type == 'call':
            initial_price = bs_initial.call_price()
        else:
            initial_price = bs_initial.put_price()
        
        for s in stock_range_exp:
            if option_type == 'call':
                intrinsic = max(0, s - strike_price)
            else:
                intrinsic = max(0, strike_price - s)
            
            pnl = intrinsic - initial_price
            pnl_values.append(pnl)
        
        fig_multi_exp.add_trace(go.Scatter(
            x=stock_range_exp,
            y=pnl_values,
            mode='lines',
            name=f'{days} days',
            line=dict(color=colors[i], width=2)
        ))
    
    fig_multi_exp.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_multi_exp.update_layout(
        title=f'Multi-Expiry P&L Comparison - {option_type.title()} Option',
        xaxis_title='Stock Price at Expiration ($)',
        yaxis_title='Profit/Loss ($)',
        height=500
    )
    
    st.plotly_chart(fig_multi_exp, use_container_width=True)

with tab5:
    st.header("Options Strategy Comparison")
    
    st.markdown("Compare different options strategies side by side")
    
    # Strategy builder
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Strategy Builder")
        
        strategies = []
        
        # Long Call
        if st.checkbox("Long Call", value=True):
            call_strike = st.number_input("Call Strike", value=strike_price, key="long_call_strike")
            bs_call = BlackScholes(stock_price, call_strike, time_to_expiry, risk_free_rate, volatility)
            call_premium = bs_call.call_price()
            
            stock_range_strat = np.linspace(stock_price * 0.7, stock_price * 1.3, 100)
            pnl_call = []
            
            for s in stock_range_strat:
                intrinsic = max(0, s - call_strike)
                pnl = intrinsic - call_premium
                pnl_call.append(pnl)
            
            strategies.append({
                'name': f'Long Call (${call_strike})',
                'pnl': pnl_call
            })
        
        # Long Put
        if st.checkbox("Long Put"):
            put_strike = st.number_input("Put Strike", value=strike_price, key="long_put_strike")
            bs_put = BlackScholes(stock_price, put_strike, time_to_expiry, risk_free_rate, volatility)
            put_premium = bs_put.put_price()
            
            stock_range_strat = np.linspace(stock_price * 0.7, stock_price * 1.3, 100)
            pnl_put = []
            
            for s in stock_range_strat:
                intrinsic = max(0, put_strike - s)
                pnl = intrinsic - put_premium
                pnl_put.append(pnl)
            
            strategies.append({
                'name': f'Long Put (${put_strike})',
                'pnl': pnl_put
            })
        
        # Straddle
        if st.checkbox("Long Straddle"):
            straddle_strike = st.number_input("Straddle Strike", value=strike_price, key="straddle_strike")
            bs_straddle = BlackScholes(stock_price, straddle_strike, time_to_expiry, risk_free_rate, volatility)
            call_premium = bs_straddle.call_price()
            put_premium = bs_straddle.put_price()
            total_premium = call_premium + put_premium
            
            stock_range_strat = np.linspace(stock_price * 0.7, stock_price * 1.3, 100)
            pnl_straddle = []
            
            for s in stock_range_strat:
                call_intrinsic = max(0, s - straddle_strike)
                put_intrinsic = max(0, straddle_strike - s)
                total_intrinsic = call_intrinsic + put_intrinsic
                pnl = total_intrinsic - total_premium
                pnl_straddle.append(pnl)
            
            strategies.append({
                'name': f'Long Straddle (${straddle_strike})',
                'pnl': pnl_straddle
            })
    
    with col2:
        if strategies:
            fig_strategy_comp = create_strategy_comparison(strategies, stock_range_strat)
            st.plotly_chart(fig_strategy_comp, use_container_width=True)
            
            # Strategy summary table
            st.subheader("Strategy Summary")
            
            summary_data = []
            for strategy in strategies:
                max_profit = max(strategy['pnl'])
                max_loss = min(strategy['pnl'])
                
                summary_data.append({
                    'Strategy': strategy['name'],
                    'Max Profit': f"${max_profit:.2f}" if max_profit < 1000 else "Unlimited",
                    'Max Loss': f"${max_loss:.2f}" if max_loss > -1000 else "Unlimited",
                    'Breakeven': "Multiple" if len([p for p in strategy['pnl'] if abs(p) < 0.1]) > 2 else "Single"
                })
            
            import pandas as pd
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
        else:
            st.info("Select at least one strategy to compare")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Advanced Options Visualizations • Built with Streamlit and Plotly"
    "</div>",
    unsafe_allow_html=True
)

