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
    opt_chain = stock.option_chain(expirations[0])
    calls, puts = opt_chain.calls, opt_chain.puts
    return calls, puts, expirations

# Calculate Greeks for an option
def calculate_greeks(option_df, stock_price, risk_free_rate=0.01):
    option_df['lastTradeDate'] = pd.to_datetime(option_df['lastTradeDate'], errors='coerce')
    option_df = option_df.dropna(subset=['lastTradeDate'])
    T = (option_df['lastTradeDate'] - pd.Timestamp('today')).dt.days / 365
    T = T.apply(lambda x: max(x, 1e-6))

    d1 = (np.log(stock_price / option_df['strike']) + (risk_free_rate + 0.5 * option_df['impliedVolatility']**2) * T) / (option_df['impliedVolatility'] * np.sqrt(T))
    d2 = d1 - option_df['impliedVolatility'] * np.sqrt(T)

    option_df['Delta'] = norm.cdf(d1)
    option_df['Gamma'] = norm.pdf(d1) / (stock_price * option_df['impliedVolatility'] * np.sqrt(T))
    option_df['Theta'] = (-stock_price * norm.pdf(d1) * option_df['impliedVolatility']) / (2 * np.sqrt(T)) - risk_free_rate * option_df['strike'] * np.exp(-risk_free_rate * T) * norm.cdf(d2)
    option_df['Vega'] = stock_price * norm.pdf(d1) * np.sqrt(T)
    option_df['Rho'] = option_df['strike'] * T * np.exp(-risk_free_rate * T) * norm.cdf(d2)
    return option_df

# Calculate Probability of Profit (POP)
def calculate_pop(option_df, stock_price):
    option_df['POP'] = norm.cdf((option_df['strike'] - stock_price) / (option_df['impliedVolatility'] * stock_price * np.sqrt(30/365)))
    return option_df

# Streamlit App
def main():
    st.title("Indian Stock Market Options Analysis Tool")
    st.sidebar.header("User Inputs")
    
    # List of Indian Stock Tickers
    INDIAN_TICKERS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'ITC.NS', 'SBIN.NS', 'LT.NS', 'BHARTIARTL.NS']
    ticker = st.sidebar.selectbox("Select Stock Symbol", INDIAN_TICKERS)
    
    if ticker:
        stock = yf.Ticker(ticker)
        try:
            stock_price = stock.history(period='1d')['Close'][0]
            st.sidebar.write(f"Current Stock Price: {stock_price}")
        except IndexError:
            st.error(f"Failed to retrieve stock price for {ticker}.")
            return
        
        calls, puts, expirations = fetch_options_data(ticker)
        
        if not calls.empty and not puts.empty:
            st.sidebar.write(f"Available Expirations: {', '.join(expirations)}")
            
            # Greeks and POP calculation for Calls
            calls = calculate_greeks(calls, stock_price)
            calls = calculate_pop(calls, stock_price)
            st.markdown(f"### {ticker} Call Options Data")
            st.write(calls)
            
            # Plot Call Options Payoff
            fig = px.scatter(calls, x='strike', y='openInterest', size='volume', color='impliedVolatility', 
                             hover_data=['Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'POP'], title='Call Options - Open Interest vs Strike')
            st.plotly_chart(fig)

            # Greeks and POP calculation for Puts
            puts = calculate_greeks(puts, stock_price)
            puts = calculate_pop(puts, stock_price)
            st.markdown(f"### {ticker} Put Options Data")
            st.write(puts)

            # Plot Put Options Payoff
            fig = px.scatter(puts, x='strike', y='openInterest', size='volume', color='impliedVolatility', 
                             hover_data=['Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'POP'], title='Put Options - Open Interest vs Strike')
            st.plotly_chart(fig)
        else:
            st.info("No options data available for the selected stock.")

if __name__ == "__main__":
    main()
