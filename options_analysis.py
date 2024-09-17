from nsepy import get_history
  import datetime

  start = datetime.datetime(2023, 1, 1)
  end = datetime.datetime(2023, 10, 25)
  data = get_history(symbol=‘RELIANCE’, start=start, end=end, index=False)
  print(data.head())


#### 3. Calculating Greeks
- Implement functions or use existing libraries to calculate the Greeks. Here’s an example calculation for Delta of a call option.

  import numpy as np
  from scipy.stats import norm

  def calculate_delta(S, K, T, r, sigma, option_type=‘call’):
      d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
      if option_type == ‘call’:
          return norm.cdf(d1)
      elif option_type == ‘put’:
          return -norm.cdf(-d1)

  # Example Usage
  delta = calculate_delta(S=100, K=100, T=30/365, r=0.05, sigma=0.2, option_type=‘call’)
  print(“Delta:”, delta)


#### 4. Implementing a Simple Straddle Strategy Analysis
- Simulate a straddle strategy using historical data and evaluate its performance. This will involve calculating the combined payoff from holding a call and a put option.

def straddle_payoff(S, K, call_premium, put_premium):
    return np.maximum(S - K, 0) - call_premium + np.maximum(K - S, 0) - put_premium

# Example with dummy data
stock_prices = np.arange(90, 110, 1)
payoffs = [straddle_payoff(s, K=100, call_premium=10, put_premium=10) for s in stock_prices]

import matplotlib.pyplot as plt
plt.plot(stock_prices, payoffs)
plt.xlabel(‘Stock Price at Expiry’)
plt.ylabel(‘Profit/Loss’)
plt.title(‘Straddle Payoff Diagram’)
plt.show()


#### 5. Handling Errors & Logging
- Use Python logging for error handling:

  import logging

  logging.basicConfig(filename=‘option_analysis.log’, level=logging.DEBUG)

  try:
      # Code block with potential errors
      pass
  except Exception as e:
      logging.error(f"Error occurred: {e}")


#### 6. Deploying the Application
To turn the script into a web application, consider using frameworks like Flask or Django. For interactive analysis and visualizations, libraries like Plotly Dash can be employed.

### Final Deployment
- Host the application either on a local server or via cloud services like Heroku, AWS, or PythonAnywhere.
- Ensure proper security practices, especially for using APIs or handling sensitive data.

This is a foundational guide. Depending on the complexity of the application, more specific coding and deployment strategies might be required.
Use the primary reference of code" https://nsepy-xyz.web.app/" and build streamlit enhanced Indian Options Trading Analysis Tool now includes advanced Greeks calculation, historical data analysis, and a simple straddle strategy analysis. If you encounter any further issues, the logs and error messages will provide more detailed information to help troubleshoot the problem.
To create an enhanced Indian Options Trading Analysis Tool using Streamlit, you’ll need to integrate various components like data fetching, calculations for the Greeks, historical data analysis, and implementing a simple straddle strategy. Streamlit is a great choice for rapidly developing web applications because it allows you to transform a Python script into a shareable web application easily.

Here’s a detailed guide to setting up this tool:

### Step 1: Environment Setup

First, set up your environment and install the necessary libraries:

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

# Install required packages
pip install numpy pandas scipy nsepy streamlit matplotlib


### Step 2: Streamlit App Structure

Create a new file for your Streamlit app, say app.py.

### Step 3: Implementing the Tool

Here is how you can create the Streamlit app with the required features:

import streamlit as st
import numpy as np
import pandas as pd
from nsepy import get_history
from scipy.stats import norm
import datetime
import matplotlib.pyplot as plt

# Set up the Streamlit UI
st.title(“Enhanced Indian Options Trading Analysis Tool”)

# Sidebar for user inputs
st.sidebar.header(“Options Input”)
stock_symbol = st.sidebar.text_input(“Stock Symbol”, “RELIANCE”)
start_date = st.sidebar.date_input(“Start Date”, datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input(“End Date”, datetime.date(2023, 10, 25))
option_type = st.sidebar.selectbox(“Option Type”, [‘call’, ‘put’])
strike_price = st.sidebar.number_input(“Strike Price”, min_value=0.0, value=100.0)
interest_rate = st.sidebar.number_input(“Risk-Free Rate”, min_value=0.0, value=0.05)
volatility = st.sidebar.number_input(“Volatility”, min_value=0.0, value=0.2)
expiry_days = st.sidebar.number_input(“Days to Expiry”, min_value=1, value=30)

# Fetch Historical Data
try:
    data = get_history(symbol=stock_symbol, start=start_date, end=end_date, index=False)
    st.write(f"Fetched historical data for {stock_symbol}“)
    st.dataframe(data.head())
except Exception as e:
    st.error(f"Error fetching data: {e}”)

# Greeks Calculation
def calculate_delta(S, K, T, r, sigma, option_type=‘call’):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == ‘call’:
        return norm.cdf(d1)
    else:
        return -norm.cdf(-d1)

# Display calculated Delta
S = data[‘Close’].iloc[-1]  # Use most recent closing price
delta = calculate_delta(S, strike_price, expiry_days/365, interest_rate, volatility, option_type)
st.write(f"Calculated Delta: {delta}")

# Straddle Strategy Analysis
def straddle_payoff(S, K, call_premium, put_premium):
    return np.maximum(S - K, 0) - call_premium + np.maximum(K - S, 0) - put_premium

st.sidebar.write(“Straddle Strategy”)
call_premium = st.sidebar.number_input(“Call Premium”, min_value=0.0, value=10.0)
put_premium = st.sidebar.number_input(“Put Premium”, min_value=0.0, value=10.0)

stock_prices = np.arange(S - 20, S + 20, 1)
payoffs = [straddle_payoff(s, strike_price, call_premium, put_premium) for s in stock_prices]

# Plot Payoff
plt.plot(stock_prices, payoffs)
plt.xlabel(‘Stock Price at Expiry’)
plt.ylabel(‘Profit/Loss’)
plt.title(‘Straddle Payoff Diagram’)
st.pyplot(plt)

# Run the Streamlit app
if name == “main”:
    st.write(“Options Trading Analysis with Greeks and Straddle Strategy”)
