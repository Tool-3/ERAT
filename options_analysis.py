import streamlit as st
import numpy as np
from scipy.stats import norm

# Option Pricing function using Black Scholes Model
def black_scholes_option_price(S, K, r, T, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return option_price

# Streamlit App
st.title('Options Analysis in the Indian Stock Market')

st.header('Calculate Option Price and Greeks using Black-Scholes Model')

# Input variables
S = st.number_input('Underlying Stock Price (S)', min_value=0.0, format="%.2f")
K = st.number_input('Strike Price (K)', min_value=0.0, format="%.2f")
r = st.number_input('Risk-free Rate (r)', min_value=0.0, format="%.2%") / 100
T = st.number_input('Time to Expiry (T)', min_value=0.0, format="%.2f")
sigma = st.number_input('Volatility (sigma)', min_value=0.0, format="%.2%") / 100

option_type = st.radio('Option Type', ('Call', 'Put'))

if option_type == 'Call':
    option_type = 'call'
else:
    option_type = 'put'

# Calculate Option Price
option_price = black_scholes_option_price(S, K, r, T, sigma, option_type)

st.write(f'Theoretical Option Price: {option_price:.2f}')
