import streamlit as st
import numpy as np
import pandas as pd
from nsepy import get_history
from scipy.stats import norm
import datetime
import matplotlib.pyplot as plt

# Function to calculate Delta
def calculate_delta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        return norm.cdf(d1)
    else:
        return -norm.cdf(-d1)

# Function to calculate straddle payoff
def straddle_payoff(S, K, call_premium, put_premium):
    return np.maximum(S - K, 0) - call_premium + np.maximum(K - S, 0) - put_premium

# Set up the Streamlit UI
st.title("Enhanced Indian Options Trading Analysis Tool")

# Sidebar for user inputs
st.sidebar.header("Options Input")
stock_symbol = st.sidebar.text_input("Stock Symbol", "RELIANCE")
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date(2023, 10, 25))
option_type = st.sidebar.selectbox("Option Type", [‘call', ‘put'])
strike_price = st.sidebar.number_input("Strike Price", min_value=0.0, value=100.0)
interest_rate = st.sidebar.number_input("Risk-Free Rate", min_value=0.0, value=0.05)
volatility = st.sidebar.number_input("Volatility", min_value=0.0, value=0.2)
expiry_days = st.sidebar.number_input("Days to Expiry", min_value=1, value=30)

# Fetch Historical Data
try:
    data = get_history(symbol=stock_symbol, start=start_date, end=end_date, index=False)
    st.write(f"Fetched historical data for {stock_symbol}")
    st.dataframe(data.head())
except Exception as e:
    st.error(f"Error fetching data: {e}")

# Greeks Calculation
if not data.empty:
    S = data[‘Close'].iloc[-1]  # Use most recent closing price
    delta = calculate_delta(S, strike_price, expiry_days/365, interest_rate, volatility, option_type)
    st.write(f"Calculated Delta: {delta}")

# Straddle Strategy Analysis
st.sidebar.write("Straddle Strategy")
call_premium = st.sidebar.number_input("Call Premium", min_value=0.0, value=10.0)
put_premium = st.sidebar.number_input("Put Premium", min_value=0.0, value=10.0)

if not data.empty:
    stock_prices = np.arange(S - 20, S + 20, 1)
    payoffs = [straddle_payoff(s, strike_price, call_premium, put_premium) for s in stock_prices]

    # Plot Payoff
    plt.figure(figsize=(10, 5))
    plt.plot(stock_prices, payoffs)
    plt.xlabel(‘Stock Price at Expiry')
    plt.ylabel(‘Profit/Loss')
    plt.title(‘Straddle Payoff Diagram')
    st.pyplot(plt)
