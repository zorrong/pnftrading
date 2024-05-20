import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from ta.volatility import BollingerBands, DonchianChannel
from ta.trend import PSARIndicator

def fetch_data(symbol, period):
    data = yf.Ticker(symbol)
    ts = data.history(period)
    ts['Date'] = ts.index
    ts.reset_index(level=0, inplace=True, drop=True)
    return ts

def calculate_boxsize(method, ts, atr_period=None, custom_value=None, percentage_value=None):
    if method == 'ATR':
        price_data = ts['Close']
        if len(price_data) < atr_period:
            atr_period = len(price_data)
        atr = sum(abs(price_data[i] - price_data[i-1]) for i in range(1, atr_period)) / atr_period
        boxsize = round(atr, 2)
    elif method == 'Percentage':
        price = (ts['High'].iloc[-1] + ts['Low'].iloc[-1]) / 2
        boxsize = round(price * (percentage_value / 100), 2)
    elif method == 'Manual':
        boxsize = round(custom_value, 2)
    else:
        price = (ts['High'].iloc[-1] + ts['Low'].iloc[-1]) / 2
        boxsize = round(price * 0.01, 2)
    return boxsize

def plot_pnf_chart(ts, symbol, boxsize):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Calculate indicators
    bb_indicator = BollingerBands(close=ts['Close'], window=20, window_dev=2)
    dc_indicator = DonchianChannel(high=ts['High'], low=ts['Low'], close=ts['Close'], window=20)
    psar_indicator = PSARIndicator(high=ts['High'], low=ts['Low'], close=ts['Close'], step=0.02, max_step=0.2)

    # Add indicators to the dataframe
    ts['bb_upper'] = bb_indicator.bollinger_hband()
    ts['bb_lower'] = bb_indicator.bollinger_lband()
    ts['dc_upper'] = dc_indicator.donchian_channel_hband()
    ts['dc_lower'] = dc_indicator.donchian_channel_lband()
    ts['psar'] = psar_indicator.psar()

    # Plot the PnF chart using mplfinance
    pnf_data = ts[['Date', 'Open', 'High', 'Low', 'Close']]
    pnf_data.set_index('Date', inplace=True)

    mpf.plot(
        pnf_data,
        type='pnf',
        mav=(50),
        volume=False,
        title=f"Point & Figure Chart for {symbol}",
        style='charles',
        ax=ax,
        addplot=[
            mpf.make_addplot(ts['bb_upper'], color='cyan', secondary_y=False),
            mpf.make_addplot(ts['bb_lower'], color='cyan', secondary_y=False),
            mpf.make_addplot(ts['dc_upper'], color='orange', secondary_y=False),
            mpf.make_addplot(ts['dc_lower'], color='orange', secondary_y=False),
            mpf.make_addplot(ts['psar'], color='purple', marker='.', markersize=5, secondary_y=False),
        ]
    )

    return fig

def main():
    st.title("Point and Figure Chart Application")

    # Move input elements to the sidebar
    symbol = st.sidebar.text_input("Enter the stock symbol:", "AAPL")
    period = st.sidebar.selectbox("Select the period for historical data:", ["1mo", "3mo", "6mo", "1y", "5y"])
    
    boxsize_method = st.sidebar.selectbox("Select box size calculation method:", ["ATR", "Percentage", "Manual", "Traditional"])
    
    atr_period = None
    custom_value = None
    percentage_value = None
    
    if boxsize_method == "ATR":
        atr_period = st.sidebar.number_input("Enter ATR period:", min_value=1, value=14, step=1)
    
    if boxsize_method == "Manual":
        custom_value = st.sidebar.number_input("Enter manual box size value:", min_value=0.01, step=0.01)
    
    if boxsize_method == "Percentage":
        percentage_value = st.sidebar.number_input("Enter percentage value:", min_value=0.01, max_value=100.0, value=1.0, step=0.01)

    if st.sidebar.button("Generate Chart"):
        ts = fetch_data(symbol, period)
        st.write(f"Data for {symbol} fetched successfully!")
        
        boxsize = calculate_boxsize(boxsize_method, ts, atr_period, custom_value, percentage_value)
        st.write(f"Box size calculated using {boxsize_method} method: {boxsize}")
        
        fig = plot_pnf_chart(ts, symbol, boxsize)
        
        st.pyplot(fig)
        st.text(f"PnF Chart for {symbol}")

if __name__ == "__main__":
    main()
