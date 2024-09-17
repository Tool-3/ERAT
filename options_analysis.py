import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Sample Options Data (In practice, you would fetch this from an API or database)
def get_sample_options_data():
    # Placeholder for actual data retrieval logic
    data = {
        'Option Type': ['Call', 'Put', 'Call', 'Put'],
        'Strike Price': [15000, 15000, 15500, 15500],
        'Expiry Date': ['2023-12-31', '2023-12-31', '2023-12-31', '2023-12-31'],
        'Premium': [250, 300, 200, 150],
        'Implied Volatility': [0.25, 0.30, 0.20, 0.15],
    }
    return pd.DataFrame(data)

# Calculate Payoff for an Option
def calculate_payoff(option_type, strike_price, premium, spot_price):
    if option_type == 'Call':
        return max(0, spot_price - strike_price) - premium
    elif option_type == 'Put':
        return max(0, strike_price - spot_price) - premium

# Main Application
st.title("📈 Indian Options Trading Analytics Tool")

# Sidebar for user input
st.sidebar.header("Options Portfolio")
spot_price = st.sidebar.slider("Current Spot Price", 14000, 16000, 15000, step=100)

# Fetch options data
options_data = get_sample_options_data()

# User can select multiple option contracts from the sample portfolio
selected_options = st.sidebar.multiselect(
    "Select Options Contracts",
    options_data.index,
    format_func=lambda x: f"{options_data.at[x, 'Option Type']} {options_data.at[x, 'Strike Price']} - {options_data.at[x, 'Expiry Date']}"
)

# Filter the portfolio based on user selection
portfolio = options_data.loc[selected_options]

# Display Portfolio
st.write("## 📋 Selected Options Portfolio")
st.dataframe(portfolio)

# Calculate and display Profit/Loss Scenarios
st.write("## 💰 Profit/Loss Scenarios at Spot Price: ₹{:,}".format(spot_price))

payoff_data = []
for _, row in portfolio.iterrows():
    payoff = calculate_payoff(row['Option Type'], row['Strike Price'], row['Premium'], spot_price)
    payoff_data.append({
        'Option': f"{row['Option Type']} {row['Strike Price']}",
        'Payoff (₹)': payoff
    })

payoff_df = pd.DataFrame(payoff_data)
st.write(payoff_df)

# Payoff Graph
st.write("## 📊 Payoff Graph")
fig = px.bar(
    payoff_df, 
    x='Option', 
    y='Payoff (₹)', 
    title=f"Option Payoff at Spot Price: ₹{spot_price}",
    labels={'Payoff (₹)': 'Payoff (₹)', 'Option': 'Option Contract'},
    color='Payoff (₹)',
    color_continuous_scale='Blues'
)
fig.update_layout(
    xaxis_title="Option Contract",
    yaxis_title="Payoff (₹)",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=12),
)
st.plotly_chart(fig)

# Sidebar footer
st.sidebar.markdown("""
---
🛠 **Features to Develop:**
- Integration with real-time data
- Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- Advanced analytics like probability of profit
""")

# Main footer
st.markdown("""
---
📊 **Note:** The current version uses sample data. In future releases, we will integrate real-time data from financial APIs and offer advanced options analytics. Stay tuned!
""")
