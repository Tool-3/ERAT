import streamlit as st
import pandas as pd
from nsepy import get_history
from nsepy.derivatives import get_expiry_date
import matplotlib.pyplot as plt
import yfinance as yf

# Title of the app
st.title("Indian Options Trading Analysis Tool")

# Sidebar for user input
st.sidebar.header("User Input")
symbol = st.sidebar.text_input("Enter Symbol", "RELIANCE")
expireyear = st.sidebar.text_input("Enter Expire Year"," " )
expiremonth = st.sidebar.text_input("Enter Expire month"," " )
# Fetch expiry dates
try:
    expiry_date = st.sidebar.selectbox("Select Expiry Date", expiry_dates)
    expiry_dates = get_expiry_date(year="expireyear", month="expiremonth")
except Exception as e:
    st.sidebar.error(f"Error fetching expiry dates: {e}")
    expiry_date = None

if expiry_date:
    # Fetch option chain data
    try:
        option_chain = get_option_chain(symbol, expiry_date)

        # Display the option chain data
        st.subheader(f"Option Chain for {symbol} on {expiry_date}")
        st.write(option_chain)

        # Calculate and display basic statistics
        st.subheader("Basic Statistics")
        st.write(option_chain.describe())

        # Plot the option chain data
        st.subheader("Option Chain Data Visualization")
        fig, ax = plt.subplots()
        ax.plot(option_chain['strikePrice'], option_chain['CE.lastPrice'], label='Call Option Last Price')
        ax.plot(option_chain['strikePrice'], option_chain['PE.lastPrice'], label='Put Option Last Price')
        ax.set_xlabel('Strike Price')
        ax.set_ylabel('Last Price')
        ax.legend()
        st.pyplot(fig)

        # Calculate and display Greeks
        st.subheader("Greeks")
        greeks = option_chain[['CE.changeinOpenInterest', 'PE.changeinOpenInterest', 'CE.impliedVolatility', 'PE.impliedVolatility']]
        st.write(greeks)

        # Display Open Interest
        st.subheader("Open Interest")
        fig, ax = plt.subplots()
        ax.bar(option_chain['strikePrice'], option_chain['CE.openInterest'], label='Call Option Open Interest', alpha=0.6)
        ax.bar(option_chain['strikePrice'], option_chain['PE.openInterest'], label='Put Option Open Interest', alpha=0.6)
        ax.set_xlabel('Strike Price')
        ax.set_ylabel('Open Interest')
        ax.legend()
        st.pyplot(fig)

        # Calculate and display advanced Greeks
        st.subheader("Advanced Greeks")
        advanced_greeks = option_chain[['CE.delta', 'PE.delta', 'CE.gamma', 'PE.gamma', 'CE.theta', 'PE.theta', 'CE.vega', 'PE.vega']]
        st.write(advanced_greeks)

        # Historical Data Analysis
        st.subheader("Historical Data Analysis")
        start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
        end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

        # Fetch historical data from Yahoo Finance
        historical_data = yf.download(f"{symbol}.NS", start=start_date, end=end_date)

        # Display historical data
        st.write(historical_data)

        # Plot historical data
        st.subheader("Historical Price Chart")
        fig, ax = plt.subplots()
        ax.plot(historical_data['Close'], label='Close Price')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        st.pyplot(fig)

        # Strategy Analysis: Simple Straddle Strategy
        st.subheader("Simple Straddle Strategy")
        strike_price = st.sidebar.number_input("Enter Strike Price", value=option_chain['strikePrice'].iloc[0])

        # Filter option chain for the selected strike price
        call_option = option_chain[(option_chain['strikePrice'] == strike_price) & (option_chain['optionType'] == 'CE')]
        put_option = option_chain[(option_chain['strikePrice'] == strike_price) & (option_chain['optionType'] == 'PE')]

        # Calculate straddle cost
        straddle_cost = call_option['lastPrice'].values[0] + put_option['lastPrice'].values[0]

        # Display straddle cost
        st.write(f"Straddle Cost for Strike Price {strike_price}: {straddle_cost}")

        # Plot straddle payoff diagram
        st.subheader("Straddle Payoff Diagram")
        fig, ax = plt.subplots()
        strike_prices = option_chain['strikePrice'].unique()
        payoff = [max(0, abs(sp - strike_price) - straddle_cost) for sp in strike_prices]
        ax.plot(strike_prices, payoff, label='Straddle Payoff')
        ax.set_xlabel('Stock Price at Expiry')
        ax.set_ylabel('Payoff')
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error fetching option chain data: {e}")
else:
    st.error("Please select a valid expiry date.")
