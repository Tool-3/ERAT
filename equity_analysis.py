import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import ta

# Title of the app
st.title("Equity Research Analysis Tool")

# Sidebar for user input
st.sidebar.header("User Input")
ticker = st.sidebar.text_input("Enter Ticker Symbol", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Fetch data from Yahoo Finance
data = yf.download(ticker, start=start_date, end=end_date)

# Display the data
st.subheader(f"Data for {ticker}")
st.write(data)

# Plot the closing prices
st.subheader("Closing Price")
fig, ax = plt.subplots()
ax.plot(data['Close'], label='Close Price')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.legend()
st.pyplot(fig)

# Calculate and display basic statistics
st.subheader("Basic Statistics")
st.write(data.describe())

# Calculate and display returns
st.subheader("Returns")
data['Returns'] = data['Close'].pct_change()
st.line_chart(data['Returns'])

# Calculate and display moving averages
st.subheader("Moving Averages")
data['MA50'] = data['Close'].rolling(window=50).mean()
data['MA200'] = data['Close'].rolling(window=200).mean()
st.line_chart(data[['Close', 'MA50', 'MA200']])

# Calculate RSI
data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()

# Display RSI
st.subheader("RSI")
st.line_chart(data['RSI'])
