"""
Options Guru - Professional Options Trading Analysis and Visualization Tool
Main Streamlit Application
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from black_scholes import BlackScholes
from data_provider import data_provider
from stock_data import get_stock_list, get_stock_name, get_popular_stocks, search_stocks
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Options Guru - Professional Options Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .greek-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .neutral {
        color: #6c757d;
    }
    .tab-content {
        padding: 1rem 0;
    }
    .stock-info {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .parameter-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    .calculate-button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .quick-results {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = 'AAPL'
if 'stock_price' not in st.session_state:
    st.session_state.stock_price = 150.0
if 'strike_price' not in st.session_state:
    st.session_state.strike_price = 155.0
if 'days_to_expiry' not in st.session_state:
    st.session_state.days_to_expiry = 30
if 'volatility' not in st.session_state:
    st.session_state.volatility = 25.0
if 'risk_free_rate' not in st.session_state:
    st.session_state.risk_free_rate = 5.0
if 'contracts' not in st.session_state:
    st.session_state.contracts = 1
if 'option_type' not in st.session_state:
    st.session_state.option_type = 'Call'
if 'position' not in st.session_state:
    st.session_state.position = 'Long (Buy)'
if 'recalculate_trigger' not in st.session_state:
    st.session_state.recalculate_trigger = 0

# Header
st.markdown('<h1 class="main-header">📊 Options Pricing Calculator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional options trading analysis and visualization tool</p>', unsafe_allow_html=True)

# Sidebar - Only Data Source
st.sidebar.header("⚙️ Settings")

# Market Data Source Selection
st.sidebar.subheader("Data Source")
available_providers = data_provider.get_available_providers()
data_source = st.sidebar.selectbox(
    "Market Data Provider",
    options=available_providers,
    index=0,
    help="Select your preferred market data provider"
)
data_provider.set_provider(data_source)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Provider:** {data_provider.get_provider().name}")
st.sidebar.markdown(f"**Available Providers:** {len(available_providers)}")

# Function to calculate option metrics
def calculate_metrics():
    """Calculate option metrics based on current parameters"""
    time_to_expiry = st.session_state.days_to_expiry / 365.0
    volatility_decimal = st.session_state.volatility / 100.0
    risk_free_decimal = st.session_state.risk_free_rate / 100.0

    bs = BlackScholes(
        st.session_state.stock_price,
        st.session_state.strike_price,
        time_to_expiry,
        risk_free_decimal,
        volatility_decimal
    )

    option_metrics = bs.calculate_option_metrics(
        st.session_state.option_type.lower(),
        st.session_state.contracts
    )

    # Adjust for short position
    if st.session_state.position == 'Short (Sell)':
        option_metrics['total_cost'] = -option_metrics['total_cost']
    
    return bs, option_metrics

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Stock Selection Section
    st.markdown('<div class="parameter-section">', unsafe_allow_html=True)
    st.subheader("📈 Stock Selection")
    
    # Popular stocks for quick selection
    st.markdown("**Quick Selection:**")
    popular_stocks = get_popular_stocks()
    cols = st.columns(6)
    
    for i, stock in enumerate(popular_stocks[:6]):
        with cols[i]:
            if st.button(f"{stock}", help=f"{get_stock_name(stock)}", key=f"quick_{stock}"):
                st.session_state.selected_stock = stock
                st.rerun()
    
    # Stock search and selection
    col_search, col_current = st.columns([1, 1])
    
    with col_search:
        stock_search = st.text_input(
            "Search Stock Symbol",
            value="",
            placeholder="Type symbol (e.g., AAPL, MSFT)",
            help="Search for stocks by symbol or company name"
        )
        
        if stock_search:
            matches = search_stocks(stock_search)
            if matches:
                selected_from_search = st.selectbox(
                    "Select from matches:",
                    options=matches,
                    format_func=lambda x: f"{x} - {get_stock_name(x)}",
                    key="search_results"
                )
                if st.button("Select Stock", key="select_from_search"):
                    st.session_state.selected_stock = selected_from_search
                    st.rerun()
    
    with col_current:
        current_stock = st.selectbox(
            "Current Stock",
            options=get_stock_list(),
            index=get_stock_list().index(st.session_state.selected_stock) if st.session_state.selected_stock in get_stock_list() else 0,
            format_func=lambda x: f"{x} - {get_stock_name(x)}",
            key="current_stock_select"
        )
        
        if current_stock != st.session_state.selected_stock:
            st.session_state.selected_stock = current_stock
    
    # Display current stock info and live price button
    col_info, col_price = st.columns([2, 1])
    
    with col_info:
        st.markdown(f"""
        <div class="stock-info">
            <strong>Selected:</strong> {st.session_state.selected_stock}<br>
            <strong>Company:</strong> {get_stock_name(st.session_state.selected_stock)}
        </div>
        """, unsafe_allow_html=True)
    
    with col_price:
        if st.button("🔄 Get Live Price", help="Fetch current market price", key="get_live_price"):
            with st.spinner("Fetching live data..."):
                stock_data = data_provider.get_stock_data(st.session_state.selected_stock)
                if stock_data:
                    st.session_state.stock_price = stock_data['price']
                    current_price = stock_data['price']
                    st.session_state.strike_price = round(current_price * 1.05, 2)  # 5% OTM
                    st.success(f"Updated! Current price: ${current_price:.2f}")
                    st.rerun()
                else:
                    st.error("Could not fetch live data.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Parameters Section
    st.markdown('<div class="parameter-section">', unsafe_allow_html=True)
    st.subheader("💰 Option Parameters")
    
    # Price parameters
    col1_param, col2_param, col3_param = st.columns(3)
    
    with col1_param:
        st.session_state.stock_price = st.number_input(
            "Stock Price ($)",
            min_value=0.01,
            value=st.session_state.stock_price,
            step=0.01,
            format="%.2f",
            help="Current price of the underlying stock",
            key="stock_price_input"
        )
    
    with col2_param:
        st.session_state.strike_price = st.number_input(
            "Strike Price ($)",
            min_value=0.01,
            value=st.session_state.strike_price,
            step=0.01,
            format="%.2f",
            help="Strike price of the option",
            key="strike_price_input"
        )
    
    with col3_param:
        st.session_state.days_to_expiry = st.number_input(
            "Days to Expiration",
            min_value=1,
            max_value=365,
            value=st.session_state.days_to_expiry,
            step=1,
            help="Number of days until option expiration",
            key="days_to_expiry_input"
        )
    
    # Market parameters
    col4_param, col5_param, col6_param = st.columns(3)
    
    with col4_param:
        st.session_state.volatility = st.number_input(
            "Volatility (%)",
            min_value=0.1,
            max_value=200.0,
            value=st.session_state.volatility,
            step=0.1,
            format="%.1f",
            help="Implied volatility of the option",
            key="volatility_input"
        )
    
    with col5_param:
        st.session_state.risk_free_rate = st.number_input(
            "Risk-Free Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=st.session_state.risk_free_rate,
            step=0.1,
            format="%.1f",
            help="Risk-free interest rate",
            key="risk_free_rate_input"
        )
    
    with col6_param:
        st.session_state.contracts = st.number_input(
            "Contracts",
            min_value=1,
            max_value=1000,
            value=st.session_state.contracts,
            step=1,
            help="Number of option contracts",
            key="contracts_input"
        )
    
    # Option type and position
    col7_param, col8_param, col_calc = st.columns([1, 1, 1])
    
    with col7_param:
        st.session_state.option_type = st.selectbox(
            "Option Type",
            options=['Call', 'Put'],
            index=0 if st.session_state.option_type == 'Call' else 1,
            help="Type of option contract",
            key="option_type_select"
        )
    
    with col8_param:
        st.session_state.position = st.selectbox(
            "Position",
            options=['Long (Buy)', 'Short (Sell)'],
            index=0 if st.session_state.position == 'Long (Buy)' else 1,
            help="Long (buy) or Short (sell) position",
            key="position_select"
        )
    
    with col_calc:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("🧮 Calculate", type="primary", help="Recalculate option metrics", key="main_calculate"):
            st.session_state.recalculate_trigger += 1
            st.rerun()
    
    # Quick strike suggestions
    st.markdown("**Quick Strike Selection:**")
    current_price = st.session_state.stock_price
    strike_suggestions = [
        ("ATM", current_price),
        ("5% OTM", current_price * 1.05 if st.session_state.option_type == 'Call' else current_price * 0.95),
        ("10% OTM", current_price * 1.10 if st.session_state.option_type == 'Call' else current_price * 0.90),
        ("5% ITM", current_price * 0.95 if st.session_state.option_type == 'Call' else current_price * 1.05),
        ("10% ITM", current_price * 0.90 if st.session_state.option_type == 'Call' else current_price * 1.10),
    ]
    
    cols_strikes = st.columns(5)
    for i, (label, strike) in enumerate(strike_suggestions):
        with cols_strikes[i]:
            if st.button(label, help=f"${strike:.2f}", key=f"strike_{label}"):
                st.session_state.strike_price = round(strike, 2)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Quick Results Section
    st.markdown('<div class="quick-results">', unsafe_allow_html=True)
    st.subheader("📊 Quick Results")
    
    # Calculate metrics
    bs, option_metrics = calculate_metrics()
    
    # Display key metrics
    profit_color = "positive" if option_metrics['total_cost'] >= 0 else "negative"
    cost_label = "Premium Received" if st.session_state.position == 'Short (Sell)' else "Premium Paid"
    
    st.metric("Option Price", f"${option_metrics['option_price']:.2f}")
    st.metric(cost_label, f"${abs(option_metrics['total_cost']):.2f}")
    st.metric("Breakeven", f"${option_metrics['breakeven']:.2f}")
    
    # Moneyness indicator
    moneyness = st.session_state.stock_price / st.session_state.strike_price
    if st.session_state.option_type == 'Call':
        if moneyness > 1.02:
            moneyness_label = "ITM (In-the-Money)"
            moneyness_color = "positive"
        elif moneyness < 0.98:
            moneyness_label = "OTM (Out-of-the-Money)"
            moneyness_color = "negative"
        else:
            moneyness_label = "ATM (At-the-Money)"
            moneyness_color = "neutral"
    else:  # Put
        if moneyness < 0.98:
            moneyness_label = "ITM (In-the-Money)"
            moneyness_color = "positive"
        elif moneyness > 1.02:
            moneyness_label = "OTM (Out-of-the-Money)"
            moneyness_color = "negative"
        else:
            moneyness_label = "ATM (At-the-Money)"
            moneyness_color = "neutral"
    
    st.markdown(f"""
    <div style="margin-top: 1rem;">
        <strong>Moneyness:</strong> <span class="{moneyness_color}">{moneyness_label}</span><br>
        <small>Ratio: {moneyness:.3f}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Greeks summary
    greeks = option_metrics['greeks']
    st.markdown("---")
    st.markdown("**Greeks Summary:**")
    st.markdown(f"• **Delta:** {greeks['delta']:.3f}")
    st.markdown(f"• **Gamma:** {greeks['gamma']:.4f}")
    st.markdown(f"• **Theta:** {greeks['theta']:.4f}")
    st.markdown(f"• **Vega:** {greeks['vega']:.4f}")
    st.markdown(f"• **Rho:** {greeks['rho']:.4f}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area with tabs
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["📈 P&L Chart", "🔢 Greeks", "📊 Analysis", "📰 Market Data"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Calculate button for this tab
    col_title, col_calc_tab = st.columns([3, 1])
    with col_title:
        st.subheader("Profit & Loss at Expiration")
    with col_calc_tab:
        if st.button("🧮 Recalculate P&L", help="Recalculate P&L chart", key="pnl_calculate"):
            st.session_state.recalculate_trigger += 1
    
    # Generate P&L chart
    stock_prices = np.linspace(
        st.session_state.stock_price * 0.7,
        st.session_state.stock_price * 1.3,
        100
    )
    
    pnl_values = bs.calculate_pnl_at_expiry(
        stock_prices,
        st.session_state.option_type.lower(),
        st.session_state.contracts
    )
    
    # Adjust for short position
    if st.session_state.position == 'Short (Sell)':
        pnl_values = [-pnl for pnl in pnl_values]
    
    fig = go.Figure()
    
    # P&L line
    fig.add_trace(go.Scatter(
        x=stock_prices,
        y=pnl_values,
        mode='lines',
        name='Profit/Loss',
        line=dict(color='#1f77b4', width=3),
        hovertemplate='Stock Price: $%{x:.2f}<br>P&L: $%{y:.2f}<extra></extra>'
    ))
    
    # Breakeven line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break Even")
    
    # Current stock price line
    fig.add_vline(
        x=st.session_state.stock_price,
        line_dash="dot",
        line_color="orange",
        annotation_text="Current Price"
    )
    
    # Breakeven point
    breakeven_price = option_metrics['breakeven']
    fig.add_vline(
        x=breakeven_price,
        line_dash="dot",
        line_color="red",
        annotation_text="Breakeven Point"
    )
    
    fig.update_layout(
        title=f"Profit & Loss at Expiration - {st.session_state.position} {st.session_state.option_type} ({st.session_state.selected_stock})",
        xaxis_title="Stock Price at Expiration ($)",
        yaxis_title="Profit/Loss ($)",
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # P&L Summary
    max_pnl = max(pnl_values)
    min_pnl = min(pnl_values)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Max Profit",
            f"${max_pnl:.2f}" if max_pnl < 10000 else "Unlimited",
            help="Maximum potential profit"
        )
    
    with col2:
        st.metric(
            "Max Loss",
            f"${abs(min_pnl):.2f}" if min_pnl > -10000 else "Unlimited",
            help="Maximum potential loss"
        )
    
    with col3:
        st.metric(
            "Breakeven",
            f"${breakeven_price:.2f}",
            help="Stock price at which the position breaks even"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Calculate button for this tab
    col_title, col_calc_tab = st.columns([3, 1])
    with col_title:
        st.subheader("Greeks Analysis")
    with col_calc_tab:
        if st.button("🧮 Recalculate Greeks", help="Recalculate Greeks", key="greeks_calculate"):
            st.session_state.recalculate_trigger += 1
    
    greeks = option_metrics['greeks']
    
    # Greeks cards in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        delta_color = "positive" if greeks['delta'] > 0 else "negative"
        st.markdown(f"""
        <div class="greek-card" style="border-left: 4px solid #28a745;">
            <h4>📈 Delta</h4>
            <h2 class="{delta_color}">{greeks['delta']:.4f}</h2>
            <p>Price sensitivity to underlying asset movement</p>
            <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                <div style="background-color: #28a745; height: 10px; width: {abs(greeks['delta']) * 100}%; border-radius: 5px;"></div>
            </div>
            <small>{'High' if abs(greeks['delta']) > 0.5 else 'Low'} sensitivity</small>
        </div>
        """, unsafe_allow_html=True)
        
        vega_color = "positive" if greeks['vega'] > 0 else "negative"
        st.markdown(f"""
        <div class="greek-card" style="border-left: 4px solid #007bff;">
            <h4>📊 Vega</h4>
            <h2 class="{vega_color}">{greeks['vega']:.4f}</h2>
            <p>Sensitivity to volatility changes</p>
            <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                <div style="background-color: #007bff; height: 10px; width: {min(abs(greeks['vega']) * 10, 100)}%; border-radius: 5px;"></div>
            </div>
            <small>{'High' if abs(greeks['vega']) > 0.1 else 'Low'} vol sensitivity</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        gamma_color = "positive" if greeks['gamma'] > 0 else "negative"
        st.markdown(f"""
        <div class="greek-card" style="border-left: 4px solid #6f42c1;">
            <h4>⚡ Gamma</h4>
            <h2 class="{gamma_color}">{greeks['gamma']:.4f}</h2>
            <p>Rate of change of Delta</p>
            <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                <div style="background-color: #6f42c1; height: 10px; width: {min(abs(greeks['gamma']) * 1000, 100)}%; border-radius: 5px;"></div>
            </div>
            <small>{'High' if abs(greeks['gamma']) > 0.01 else 'Low'} gamma</small>
        </div>
        """, unsafe_allow_html=True)
        
        rho_color = "positive" if greeks['rho'] > 0 else "negative"
        st.markdown(f"""
        <div class="greek-card" style="border-left: 4px solid #fd7e14;">
            <h4>💰 Rho</h4>
            <h2 class="{rho_color}">{greeks['rho']:.4f}</h2>
            <p>Sensitivity to interest rate changes</p>
            <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                <div style="background-color: #fd7e14; height: 10px; width: {min(abs(greeks['rho']) * 100, 100)}%; border-radius: 5px;"></div>
            </div>
            <small>{'High' if abs(greeks['rho']) > 0.1 else 'Low'} rate sensitivity</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        theta_color = "negative" if greeks['theta'] < 0 else "positive"
        st.markdown(f"""
        <div class="greek-card" style="border-left: 4px solid #dc3545;">
            <h4>⏰ Theta</h4>
            <h2 class="{theta_color}">{greeks['theta']:.4f}</h2>
            <p>Time decay per day</p>
            <div style="background-color: #e9ecef; height: 10px; border-radius: 5px;">
                <div style="background-color: #dc3545; height: 10px; width: {min(abs(greeks['theta']) * 100, 100)}%; border-radius: 5px;"></div>
            </div>
            <small>{'High' if abs(greeks['theta']) > 0.05 else 'Low'} time decay</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Greeks Summary
    st.markdown("---")
    st.subheader("Greeks Summary & Interpretation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Risk Metrics**")
        delta_risk = "Low" if abs(greeks['delta']) < 0.3 else "Medium" if abs(greeks['delta']) < 0.7 else "High"
        theta_risk = "Low" if abs(greeks['theta']) < 0.02 else "Medium" if abs(greeks['theta']) < 0.05 else "High"
        vega_risk = "Low" if abs(greeks['vega']) < 0.05 else "Medium" if abs(greeks['vega']) < 0.15 else "High"
        
        st.write(f"• **Price Risk (Delta):** {delta_risk}")
        st.write(f"• **Time Risk (Theta):** {theta_risk}")
        st.write(f"• **Volatility Risk (Vega):** {vega_risk}")
    
    with col2:
        st.markdown("**Trading Insights**")
        delta_insight = f"For every $1 move in {st.session_state.selected_stock}, this option will move approximately ${abs(greeks['delta']):.2f}"
        theta_insight = f"This option loses approximately ${abs(greeks['theta']):.2f} in value each day"
        vega_insight = f"A 1% increase in volatility will change the option price by approximately ${greeks['vega']:.2f}"
        
        st.write(f"• **Delta:** {delta_insight}")
        st.write(f"• **Theta:** {theta_insight}")
        st.write(f"• **Vega:** {vega_insight}")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Calculate button for this tab
    col_title, col_calc_tab = st.columns([3, 1])
    with col_title:
        st.subheader("Strategy Analysis")
    with col_calc_tab:
        if st.button("🧮 Recalculate Analysis", help="Recalculate strategy analysis", key="analysis_calculate"):
            st.session_state.recalculate_trigger += 1
    
    # Calculate max profit and loss
    if st.session_state.option_type == 'Call':
        if st.session_state.position == 'Long (Buy)':
            max_profit = "Unlimited upside potential"
            max_loss = f"${option_metrics['total_cost']:.2f}"
            max_loss_desc = "Premium paid"
        else:
            max_profit = f"${abs(option_metrics['total_cost']):.2f}"
            max_loss = "Unlimited"
            max_loss_desc = "Unlimited upside risk"
    else:  # Put
        if st.session_state.position == 'Long (Buy)':
            max_profit_val = (st.session_state.strike_price - 0) * st.session_state.contracts * 100 - option_metrics['total_cost']
            max_profit = f"${max_profit_val:.2f}"
            max_loss = f"${option_metrics['total_cost']:.2f}"
            max_loss_desc = "Premium paid"
        else:
            max_profit = f"${abs(option_metrics['total_cost']):.2f}"
            max_profit_val = (st.session_state.strike_price - 0) * st.session_state.contracts * 100
            max_loss = f"${max_profit_val:.2f}"
            max_loss_desc = "If stock goes to zero"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #d4edda; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #28a745;">
            <h4 style="color: #155724; margin-bottom: 1rem;">📈 Maximum Profit</h4>
            <h2 style="color: #28a745; margin-bottom: 0.5rem;">{max_profit}</h2>
            <p style="color: #155724; margin: 0;">{'Unlimited upside potential' if max_profit == 'Unlimited upside potential' else 'Premium received' if st.session_state.position == 'Short (Sell)' else 'Strike minus premium'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: #f8d7da; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #dc3545;">
            <h4 style="color: #721c24; margin-bottom: 1rem;">📉 Maximum Loss</h4>
            <h2 style="color: #dc3545; margin-bottom: 0.5rem;">{max_loss}</h2>
            <p style="color: #721c24; margin: 0;">{max_loss_desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Strategy Summary")
    
    # Strategy classification
    strategy_name = f"{st.session_state.position.split()[0]} {st.session_state.option_type}"
    
    if st.session_state.option_type == 'Call' and st.session_state.position == 'Long (Buy)':
        market_outlook = "Bullish"
        risk_level = "Limited"
        time_decay = "Negative"
    elif st.session_state.option_type == 'Call' and st.session_state.position == 'Short (Sell)':
        market_outlook = "Bearish/Neutral"
        risk_level = "Unlimited"
        time_decay = "Positive"
    elif st.session_state.option_type == 'Put' and st.session_state.position == 'Long (Buy)':
        market_outlook = "Bearish"
        risk_level = "Limited"
        time_decay = "Negative"
    else:  # Short Put
        market_outlook = "Bullish/Neutral"
        risk_level = "High"
        time_decay = "Positive"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #e7f3ff; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h5 style="color: #0066cc;">Strategy</h5>
            <span style="background-color: #0066cc; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem;">{strategy_name}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        outlook_color = "#28a745" if market_outlook == "Bullish" else "#dc3545" if market_outlook == "Bearish" else "#ffc107"
        st.markdown(f"""
        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h5 style="color: #856404;">Market Outlook</h5>
            <span style="background-color: {outlook_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem;">{market_outlook}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        risk_color = "#28a745" if risk_level == "Limited" else "#ffc107" if risk_level == "High" else "#dc3545"
        st.markdown(f"""
        <div style="background-color: #f8d7da; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h5 style="color: #721c24;">Risk Level</h5>
            <span style="background-color: {risk_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem;">{risk_level}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        decay_color = "#dc3545" if time_decay == "Negative" else "#28a745"
        st.markdown(f"""
        <div style="background-color: #d1ecf1; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h5 style="color: #0c5460;">Time Decay</h5>
            <span style="background-color: {decay_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem;">{time_decay}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Calculate button for this tab
    col_title, col_calc_tab = st.columns([3, 1])
    with col_title:
        st.subheader("📈 Market Overview")
    with col_calc_tab:
        if st.button("🔄 Refresh Market Data", help="Refresh market data", key="market_refresh"):
            st.rerun()
    
    # Get market overview
    market_data = data_provider.get_market_overview()
    
    if market_data:
        cols = st.columns(len(market_data))
        for i, (symbol, data) in enumerate(market_data.items()):
            with cols[i]:
                change_color = "positive" if data['change'] >= 0 else "negative"
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <h4>{symbol}</h4>
                    <h3>${data['price']:.2f}</h3>
                    <p class="{change_color}">
                        {'+' if data['change'] >= 0 else ''}{data['change']:.2f} ({data['change_percent']:+.2f}%)
                    </p>
                    <small>{data['name']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔍 Current Stock Data")
    
    # Display current stock data
    with st.spinner("Fetching current market data..."):
        current_stock_data = data_provider.get_stock_data(st.session_state.selected_stock)
        
        if current_stock_data:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Symbol", current_stock_data['symbol'])
            
            with col2:
                st.metric("Price", f"${current_stock_data['price']:.2f}")
            
            with col3:
                change_delta = f"{current_stock_data['change']:+.2f}"
                change_percent = f"({current_stock_data['change_percent']:+.2f}%)"
                st.metric("Change", change_delta, change_percent)
            
            with col4:
                st.metric("Volume", f"{current_stock_data['volume']:,}")
            
            with col5:
                st.metric("Prev Close", f"${current_stock_data['previous_close']:.2f}")
            
            # Update button
            if st.button("📊 Use This Price", type="primary", key="use_market_price"):
                st.session_state.stock_price = current_stock_data['price']
                st.success(f"Updated stock price to ${current_stock_data['price']:.2f}")
                st.rerun()
            
            st.caption(f"Last updated: {current_stock_data['last_updated']} | Data provided by {data_provider.get_provider().name}")
        else:
            st.error(f"Could not fetch data for {st.session_state.selected_stock}. Please check the symbol or try a different data provider.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    f"Options Guru - Professional Options Trading Analysis Tool<br>"
    f"Current Position: {st.session_state.position} {st.session_state.option_type} on {st.session_state.selected_stock} • "
    f"Data provided by {data_provider.get_provider().name} • "
    "Built with Streamlit and Plotly"
    "</div>",
    unsafe_allow_html=True
)

