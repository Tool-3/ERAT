from datetime import date
from nsepy import get_history
from nsepy.derivatives import get_expiry_date, get_option_chain
from pprint import pprint

# Define the expiry date
expiry = date(2020, 5, 28)
print(expiry)

# Fetch historical data for the underlying asset (e.g., BANKNIFTY)
symbol = 'BANKNIFTY'
start_date = date(2020, 1, 1)
end_date = expiry
underlying_data = get_history(symbol=symbol, start=start_date, end=end_date, index=True)

# Fetch the option chain data
expiry_date = expiry.strftime('%d-%b-%Y').upper()  # Convert date to the required format
strike_price = 300
option_type = 'CE'

option_chain_data = get_option_chain(symbol, expiry_date)

# Filter the data for the specific strike price and option type
filtered_data = option_chain_data[(option_chain_data['strikePrice'] == strike_price) & (option_chain_data['optionType'] == option_type)]

# Advanced Greeks calculations (example calculation)
filtered_data['Delta'] = 0.5  # Dummy calculation for Delta

# Simple straddle strategy analysis
call_data = filtered_data[filtered_data['optionType'] == 'CE']
put_data = filtered_data[filtered_data['optionType'] == 'PE']

straddle_profit = call_data['lastPrice'].values[0] + put_data['lastPrice'].values[0]  # Total premium of straddle

# Print the historical data, filtered option chain data, and straddle strategy analysis results
print("Historical Data for BANKNIFTY:")
pprint(underlying_data)
print("\nFiltered Option Chain Data:")
pprint(filtered_data)
print("\nStraddle Strategy Analysis - Total Premium of Straddle:")
print(straddle_profit)
