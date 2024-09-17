import streamlit as st
import pandas as pd
import yfinance as yf

# Define a function to fetch options data
def fetch_options_data(ticker):
    # Use yfinance to get the options data
    stock = yf.Ticker(ticker)
    expirations = stock.options

    # Get options data for the first expiration date
    opt_data = stock.option_chain(expirations[0])
    calls = opt_data.calls
    puts = opt_data.puts

    return calls, puts, expirations

# Streamlit App
def main():
    st.title(“Indian Stock Market Option Analysis Tool”)

    # Sidebar inputs
    st.sidebar.header(“User Input”)
    ticker = st.sidebar.text_input(“Stock Symbol”, “RELIANCE.NS”).strip()

    # Fetch and display options data
    if ticker:
        calls, puts, expirations = fetch_options_data(ticker)
        if not calls.empty and not puts.empty:
            st.write(f"Options data for {ticker}“)
            st.subheader(“Calls”)
            st.dataframe(calls)

            st.subheader(“Puts”)
            st.dataframe(puts)

            st.write(f"Available Expirations: {expirations}”)
        else:
            st.error(“Could not fetch options data. Please check the stock symbol and try again.”)

# Run the app
if name == “main”:
    main()
