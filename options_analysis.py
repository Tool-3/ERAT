import streamlit as st
import pandas as pd
from nsepy import get_history
from nsepy.derivatives import get_expiry_date, get_option_chain
import matplotlib.pyplot as plt
import yfinance as yf

def get_option_chain_data(symbol: str, expiry_date: pd.Timestamp) -> pd.DataFrame:
    """
    Fetches option chain data for a given symbol and expiry date.

    Args:
        symbol: Symbol (e.g., RELIANCE)
        expiry_date: Expiry date (e.g., 2023-12-15)

    Returns:
        Option chain data as a Pandas DataFrame
    """
    option_chain = get_option_chain(symbol, expiry_date)
    return option_chain

def plot_option_chain_data(option_chain: pd.DataFrame) -> None:
    """
    Plots option chain data using Matplotlib.

    Args:
        option_chain: Option chain data as a Pandas DataFrame
    """
    fig, ax = plt.subplots()
    ax.plot(option_chain['strikePrice'], option_chain['CE.lastPrice'], label='Call Option Last Price')
    ax.plot(option_chain['strikePrice'], option_chain['PE.lastPrice'], label='Put Option Last Price')
    ax.set_xlabel('Strike Price')
    ax.set_ylabel('Last Price')
    ax.legend()
    st.pyplot(fig)

def main():
    st.title("Indian Options Trading Analysis Tool")

    # Sidebar for user input
    st.sidebar.header("User Input")
    symbol = st.sidebar.text_input("Enter Symbol", "RELIANCE")
    expiry_date = st.sidebar.selectbox("Select Expiry Date", get_expiry_date(year=2023, month=12))

    # Fetch option chain data
    option_chain = get_option_chain_data(symbol, expiry_date)

    # Display option chain data
    st.subheader(f"Option Chain for {symbol} on {expiry_date}")
    st.write(option_chain)

    # Calculate and display basic statistics
    st.subheader("Basic Statistics")
    st.write(option_chain.describe())

    # Plot option chain data
    plot_option_chain_data(option_chain)

    # Calculate and display Greeks
    st.subheader("Greeks")
    greeks = option_chain[['CE.changeinOpenInterest', 'PE.changeinOpenInterest', 'CE.impliedVolatility', 'PE.impliedVolatility']]
    st.write(greeks)

    # ... rest of the code ...

if __name__ == "__main__":
    main()
