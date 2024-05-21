import yfinance as yf
from pypnf import PointFigureChart
import streamlit as st
import matplotlib.pyplot as plt

def fetch_data(symbol, period):
    data = yf.Ticker(symbol)
    ts = data.history(period)
    ts.reset_index(level=0, inplace=True)
    ts['Date'] = ts['Date'].dt.strftime('%Y-%m-%d')
    ts = ts.to_dict('list')
    return ts

def calculate_boxsize(method, ts, atr_period=None, custom_value=None, percentage_value=None):
    if method == 'ATR':
        # Use ATR calculation with the specified period
        price_data = [price for price in ts['Close']]
        if len(price_data) < atr_period:
            atr_period = len(price_data)
        atr = sum(abs(price_data[i] - price_data[i-1]) for i in range(1, atr_period)) / atr_period
        boxsize = round(atr, 2)
    elif method == 'Percentage':
        # Use the specified percentage of the current price
        price = (ts['High'][-1] + ts['Low'][-1]) / 2
        boxsize = round(price * (percentage_value / 100), 2)
    elif method == 'Manual':
        # Use custom manual input value
        boxsize = round(custom_value, 2)
    else:
        # Traditional calculation (default percentage of price, e.g., 1%)
        price = (ts['High'][-1] + ts['Low'][-1]) / 2
        boxsize = round(price * 0.01, 2)
    return boxsize

def plot_pnf_chart(ts, symbol, boxsize):
    pnf = PointFigureChart(ts=ts, method='h/l', reversal=3, boxsize=boxsize, scaling='abs', title=symbol)
    pnf.show_trendlines = 'external'
    pnf.get_trendlines(length=4, mode='weak')
    pnf.ema(21)
    # Customize the chart appearance to match the uploaded image
    pnf.color_up = 'blue'
    pnf.color_down = 'red'
    pnf.show()
    return pnf

def identify_patterns(pnf):
    boxes = pnf.boxes
    patterns = []

    # Double Top
    for i in range(1, len(boxes) - 1):
        if boxes[i].type == 'X' and boxes[i-1].type == 'O' and boxes[i+1].type == 'O' and boxes[i].value == boxes[i-1].value:
            patterns.append(('Double Top', boxes[i].value))

    # Double Bottom
    for i in range(1, len(boxes) - 1):
        if boxes[i].type == 'O' and boxes[i-1].type == 'X' and boxes[i+1].type == 'X' and boxes[i].value == boxes[i-1].value:
            patterns.append(('Double Bottom', boxes[i].value))

    # Triple Top
    for i in range(2, len(boxes) - 2):
        if (boxes[i].type == 'X' and 
            boxes[i-1].type == 'O' and 
            boxes[i-2].type == 'X' and 
            boxes[i+1].type == 'O' and 
            boxes[i+2].type == 'X' and 
            boxes[i].value == boxes[i-2].value == boxes[i+2].value):
            patterns.append(('Triple Top', boxes[i].value))

    # Triple Bottom
    for i in range(2, len(boxes) - 2):
        if (boxes[i].type == 'O' and 
            boxes[i-1].type == 'X' and 
            boxes[i-2].type == 'O' and 
            boxes[i+1].type == 'X' and 
            boxes[i+2].type == 'O' and 
            boxes[i].value == boxes[i-2].value == boxes[i+2].value):
            patterns.append(('Triple Bottom', boxes[i].value))
    
    # Add more patterns as needed

    return patterns

def main():
    st.title("Point and Figure Chart Application")

    # Move input elements to the sidebar
    symbol = st.sidebar.text_input("Enter the stock symbol:", "VND.VN")
    period = st.sidebar.selectbox("Select the period for historical data:", [“1d”, “5d”, “1mo”, “3mo”, “6mo”, “1y”, “2y”, “5y”, “10y”, “ytd”, “max”])
    
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
        
        pnf = plot_pnf_chart(ts, symbol, boxsize)
        
        st.pyplot(plt.gcf())
        st.text(pnf)

        # Identify patterns
        patterns = identify_patterns(pnf)
        if patterns:
            for pattern in patterns:
                st.write(f"Pattern detected: {pattern[0]} at value {pattern[1]}")
        else:
            st.write("No significant patterns detected.")

if __name__ == "__main__":
    main()
