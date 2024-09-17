import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import norm
import plotly.express as px

# Fetch real-time options data from Yahoo Finance
def fetch_options_data(ticker):
    stock = yf.Ticker(ticker)
    expirations = stock.options
    if not expirations:
        st.error(f"No options data available for {ticker}.")
        return pd.DataFrame(), pd.DataFrame(), []

    # Fetch the first expiration options data (for simplicity)
    opt_chain = stock.option_chain(expirations[0])
    calls = opt_chain.calls
    puts = opt_chain.puts
    return calls, puts, expirations

# Calculate Greeks using the Black-Scholes model
def calculate_greeks(option_df, stock_price, risk_free_rate=0.01):
    T = (pd.to_datetime(option_df['lastTradeDate']) - pd.to_datetime('today')).dt.days / 365
    d1 = (np.log(stock_price / option_df['strike']) + (risk_free_rate + 0.5 * option_df['impliedVolatility'] ** 2) * T) / (option_df['impliedVolatility'] * np.sqrt(T))
    d2 = d1 - option_df['impliedVolatility'] * np.sqrt(T)

    option_df['Delta'] = norm.cdf(d1)
    option_df['Gamma'] = norm.pdf(d1) / (stock_price * option_df['impliedVolatility'] * np.sqrt(T))
    option_df['Theta'] = (-stock_price * norm.pdf(d1) * option_df['impliedVolatility']) / (2 * np.sqrt(T))
    option_df['Theta'] -= risk_free_rate * option_df['strike'] * np.exp(-risk_free_rate * T) * norm.cdf(d2)
    option_df['Vega'] = stock_price * norm.pdf(d1) * np.sqrt(T)
    option_df['Rho'] = option_df['strike'] * T * np.exp(-risk_free_rate * T) * norm.cdf(d2)

    return option_df

# Monte Carlo simulation for Probability of Profit
def simulate_profit(option_df, stock_price, num_simulations=1000, days=30):
    results = []
    for i in range(num_simulations):
        # Simulate random price movement
        simulated_spot = stock_price * np.exp((0 - 0.5 * option_df['impliedVolatility']**2) * days/365 + option_df['impliedVolatility'] * np.sqrt(days/365) * np.random.normal())
        if option_df['Option Type'] == 'Call':
            payoff = max(0, simulated_spot - option_df['strike']) - option_df['Premium']
        elif option_df['Option Type'] == 'Put':
            payoff = max(0, option_df['strike'] - simulated_spot) - option_df['Premium']

        results.append(payoff > 0)  # Check if profit was made
    probability_of_profit = np.mean(results)
    return probability_of_profit

# Calculate VaR using the Delta-Normal Approximation
def calculate_var(option_df, stock_price, confidence_level=0.95, num_simulations=1000, days=30):
    results = []
    for i in range(num_simulations):
        # Simulate random price movement
        simulated_spot = stock_price * np.exp((0 - 0.5 * option_df['impliedVolatility']**2) * days/365 + option_df['impliedVolatility'] * np.sqrt(days/365) * np.random.normal())
        if option_df['Option Type'] == 'Call':
            payoff = max(0, simulated_spot - option_df['strike']) - option_df['Premium']
        elif option_df['Option Type'] == 'Put':
            payoff = max(0, option_df['strike'] - simulated_spot) - option_df['Premium']

        results.append(payoff)
    var = np.percentile(results, (1 - confidence_level) * 100)
    option_df['VaR'] = var
    return option_df

# Calculate Expected Return using the Delta-Normal Approximation
def calculate_expected_return(option_df, stock_price, risk_free_rate=0.01, days=30):
    T = (pd.to_datetime(option_df['lastTradeDate']) - pd.to_datetime('today')).dt.days / 365
    d1 = (np.log(stock_price / option_df['strike']) + (risk_free_rate + 0.5 * option_df['impliedVolatility'] ** 2) * T) / (option_df['impliedVolatility'] * np.sqrt(T))
    expected_return = option_df['Delta'] * stock_price * np.exp(risk_free_rate * T) - option_df['Premium'] * np.exp(-risk_free_rate * T)
    option_df['Expected Return'] = expected_return
    return option_df

# Main application
st.title("📈 Real-Time Options Trading Analytics Tool with Greeks & Profitability")

# Sidebar for user input
st.sidebar.header("Options Portfolio")
ticker = st.sidebar.text_input("Enter Stock Symbol", value="AAPL").upper()

# Fetch options data if ticker is valid
if ticker:
    try:
        stock = yf.Ticker(ticker)
        stock_price = stock.history(period="1d")['Close'].iloc[0]
        st.sidebar.write(f"Current Price of {ticker}: ${stock_price:.2f}")

        calls, puts, expirations = fetch_options_data(ticker)

        # Allow user to select option contracts (calls or puts)
        st.sidebar.subheader("Select Options Contracts")
        option_type = st.sidebar.radio("Option Type", ("Calls", "Puts"))
        options_data = calls if option_type == "Calls" else puts

        selected_options = st.sidebar.multiselect(
            "Select Options Contracts",
            options_data.index,
            format_func=lambda x: f"{options_data.at[x, 'strike']} - Exp: {options_data.at[x, 'lastTradeDate']}"
        )

        # Show selected portfolio
        portfolio = options_data.loc[selected_options]
        st.write(f"## Selected {option_type} Portfolio")
        st.write(portfolio)

        # Calculate and display Greeks
        if not portfolio.empty:
            portfolio = calculate_greeks(portfolio, stock_price)
            st.write(f"## Greeks for Selected {option_type} Contracts")
            st.write(portfolio[['strike', 'Delta', 'Gamma', 'Theta', 'Vega', 'Rho']])

        # Calculate and display probability of profit
        st.write("## Probability of Profit (Monte Carlo Simulation)")
        probabilities = []
        for idx, row in portfolio.iterrows():
            probability = simulate_profit(row, stock_price)
            probabilities.append(probability)
            st.write(f"Option {row['strike']} - Probability of Profit: {probability:.2%}")

        # Plot probability of profit
        st.write("## Probability of Profit Plot")
        fig = px.bar(portfolio, x='strike', y=probabilities, title="Probability of Profit", labels={'strike': 'Strike Price', 'y': 'Probability of Profit'})
        st.plotly_chart(fig)

        # Calculate and display additional analytics
        st.write("## Additional Analytics")
        portfolio = calculate_var(portfolio, stock_price)
        portfolio = calculate_expected_return(portfolio, stock_price)
        st.write(portfolio[['strike', 'Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'VaR', 'Expected Return']])

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

st.sidebar.markdown("""
---
🛠 **Features Coming Soon:**
- Real-time advanced options pricing models.
""")
