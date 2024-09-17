import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from scipy.stats import norm

# Function to fetch options data
def fetch_options_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        # Check if expirations are available
        if not expirations:
            st.error(f"No options data available for {ticker}.")
            return pd.DataFrame(), pd.DataFrame(), []

        # Retrieve the option chain for a specified expiration
        opt_data = stock.option_chain(expirations[0])
        calls = opt_data.calls
        puts = opt_data.puts

        return calls, puts, expirations
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}.")
        return pd.DataFrame(), pd.DataFrame(), []

# Function to calculate Greeks
def calculate_greeks(option_df, stock_price, risk_free_rate=0.01):
    try:
        T = (option_df['lastTradeDate'] - pd.to_datetime('today')).dt.days / 365
        option_df['d1'] = (np.log(stock_price / option_df['strike']) + (risk_free_rate + 0.5 * option_df['impliedVolatility'] ** 2) * T) / (option_df['impliedVolatility'] * np.sqrt(T))
        option_df['d2'] = option_df['d1'] - option_df['impliedVolatility'] * np.sqrt(T)
        
        option_df['Delta'] = norm.cdf(option_df['d1'])
        option_df['Gamma'] = norm.pdf(option_df['d1']) / (stock_price * option_df['impliedVolatility'] * np.sqrt(T))
        option_df['Theta'] = - (stock_price * norm.pdf(option_df['d1']) * option_df['impliedVolatility']) / (2 * np.sqrt(T))
        option_df['Theta'] -= risk_free_rate * option_df['strike'] * np.exp(-risk_free_rate * T) * norm.cdf(option_df['d2'])
        option_df['Vega'] = stock_price * norm.pdf(option_df['d1']) * np.sqrt(T)
        option_df['Rho'] = option_df['strike'] * T * np.exp(-risk_free_rate * T) * norm.cdf(option_df['d2'])
        return option_df
    except KeyError as e:
        st.error(f"Key error in calculating Greeks: {str(e)}")
        return option_df

# Streamlit App
def main():
    st.set_page_config(page_title="Options Analysis Tool", page_icon="📈")
    
    st.title("Indian Stock Market Option Analysis Tool")
    st.sidebar.header("User Inputs")

    # Sample ticker list
    INDIAN_TICKERS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'HINDUNILVR.NS', 'ITC.NS', 'ICICIBANK.NS', 'SBIN.NS', 'LT.NS', 'BHARTIARTL.NS']
    
    ticker = st.sidebar.selectbox("Select Stock Symbol", options=INDIAN_TICKERS)
    
    if ticker:
        stock = yf.Ticker(ticker)
        try:
            stock_price = stock.history(period="1d")['Close'].iloc[0]
        except IndexError:
            st.error(f"Failed to retrieve the stock price for {ticker}.")
            return

        calls, puts, expirations = fetch_options_data(ticker)
        
        if not calls.empty and not puts.empty:
            calls = calculate_greeks(calls, stock_price)
            puts = calculate_greeks(puts, stock_price)

            st.markdown(f"### Options Data for {ticker}")
            st.markdown("#### Calls")
            fig = px.scatter(calls, x='strike', y='openInterest', size='volume', color='impliedVolatility', 
                             hover_data=['Delta', 'Gamma', 'Theta', 'Vega', 'Rho'], title='Call Options - Open Interest vs Strike')
            st.plotly_chart(fig)

            st.markdown("#### Puts")
            fig = px.scatter(puts, x='strike', y='openInterest', size='volume', color='impliedVolatility', 
                             hover_data=['Delta', 'Gamma', 'Theta', 'Vega', 'Rho'], title='Put Options - Open Interest vs Strike')
            st.plotly_chart(fig)

            st.sidebar.write(f"Available Expirations: {', '.join(expirations)}")
        else:
            st.info("No data available for the selected symbol.")

    st.sidebar.markdown("""
    ---
    Note: Data provided by Yahoo Finance. Real-time accuracy may vary.
    """)

if __name__ == "__main__":
    main()
