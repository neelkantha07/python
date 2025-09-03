import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import csv
import quantstats as qs
import webbrowser
from datetime import datetime
import json,threading,time
from tkinter import font
import pygame
# Global variables for period, interval, and chart type
period = "1y"
interval = "1d"
chart_type = "candlestick"
info_ticker=""
indices = ["^NSEI", "^BSESN", "^CNX100", "MIDCAP.NS", "^NIFTYSMCP50", "MONIFTY500.NS", "^CNXIT", "^CNXPHARMA", "^CNXMETAL", "^CNXPSUBANK", "^NIFTYFMCG", "^NIFTYBANK", "^NIFTYENERGY", "^NIFTYAUTO", "^CNXREALTY", "^NIFTYINFRA", "^NIFTYMEDIA", "^NIFTYCOMMODITIES", "^NIFTYCONSUMPTION", "^NIFTYSERVSECTOR", "^NIFTY50EQUALWEIGHT", "^NIFTYALPHA50", "^NIFTYDIVOPPS50", "^NIFTYGS15YRPLUS", "^NIFTYMIDLIQ15", "^NIFTY100LOWVOL3", "NIFTY200MOMENTM30.NS", "NIFTYALPHA50.NS"]

# Global variable for tickers list
tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "SBIN.NS", "INFY.NS", "UNITDSPR.NS"]




# Function to check if stocks are breaking their 20-day high
def check_20_day_high():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            
            if df.empty:
                continue
            
            df['20_day_high'] = df['High'].rolling(window=20).max()
            if df['Close'].iloc[-1] > df['20_day_high'].iloc[-1]:
                matching_tickers.append(ticker)
        
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
    
    return matching_tickers

# Function to check if stocks are breaking their 20-day low
def check_20_day_low():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            
            if df.empty:
                continue
            
            df['20_day_low'] = df['Low'].rolling(window=20).min()
            if df['Close'].iloc[-1] < df['20_day_low'].iloc[-1]:
                matching_tickers.append(ticker)
        
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
    
    return matching_tickers

# Function to check if stocks are making higher highs
def check_higher_highs():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            
            if df.empty:
                continue
            
            df['previous_high'] = df['High'].shift(1)
            if (df['High'].iloc[-1] > df['previous_high'].iloc[-1]):
                matching_tickers.append(ticker)
        
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
    
    return matching_tickers

# Function to check if price is crossing above or below Bollinger Bands
def check_bollinger_band_crossings_down():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            
            if df.empty:
                continue
            
            df['bb_middle_band'] = df['Close'].rolling(window=20).mean()
            df['bb_std_dev'] = df['Close'].rolling(window=20).std()
            df['bb_upper_band'] = df['bb_middle_band'] + (df['bb_std_dev'] * 2)
            df['bb_lower_band'] = df['bb_middle_band'] - (df['bb_std_dev'] * 2)
            
            if (df['Close'].iloc[-1] < df['bb_lower_band'].iloc[-1]) :
                matching_tickers.append((ticker,calculate_percentage_change(df['Close'].iloc[-1],df['bb_lower_band'].iloc[-1])))
        
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
            
        matching_tickers=sort_descending(matching_tickers)
    
    return [ticker for ticker, _ in matching_tickers]

def calculate_percentage_change(old_value, new_value):
    if old_value == 0:
        raise ValueError("The old value cannot be zero.")
    percentage_change = ((new_value - old_value) / old_value) * 100
    return percentage_change
def sort_descending(arr):
    return sorted(arr, reverse=True)

def check_bollinger_band_crossings_up():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            
            if df.empty:
                continue
            
            df['bb_middle_band'] = df['Close'].rolling(window=20).mean()
            df['bb_std_dev'] = df['Close'].rolling(window=20).std()
            df['bb_upper_band'] = df['bb_middle_band'] + (df['bb_std_dev'] * 2)
            df['bb_lower_band'] = df['bb_middle_band'] - (df['bb_std_dev'] * 2)
            
            if (df['Close'].iloc[-1] > df['bb_upper_band'].iloc[-1]) :
                matching_tickers.append((ticker,calculate_percentage_change(df['Close'].iloc[-1],df['bb_upper_band'].iloc[-1])))
        
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
            
        matching_tickers=sort_descending(matching_tickers)
    
    return [ticker for ticker, _ in matching_tickers]

# Function to check for double bottom pattern within the last 2 months
def check_double_bottom():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            
            if df.empty or len(df) < 2:
                continue
            
            df['min_20d'] = df['Low'].rolling(window=60).min()
            df['min_20d_count'] = df['Low'].rolling(window=20).apply(lambda x: list(x).count(min(x)))
            if df['min_20d_count'].iloc[-1] >= 2:
                matching_tickers.append(ticker)
        
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
    
    return matching_tickers

# Function to calculate stocks where Bollinger Bands are inside the Keltner Channel
def check_bollinger_inside_keltner():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval)
            print(period,interval)
            
            if df.empty:
                continue

            # Calculate Bollinger Bands
            df['bb_middle_band'] = df['Close'].rolling(window=20).mean()
            df['bb_std_dev'] = df['Close'].rolling(window=20).std()
            df['bb_upper_band'] = df['bb_middle_band'] + (df['bb_std_dev'] * 2)
            df['bb_lower_band'] = df['bb_middle_band'] - (df['bb_std_dev'] * 2)

            # Calculate Keltner Channel
            df['atr'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=20)
            df['kc_middle_band'] = df['Close'].rolling(window=20).mean()
            df['kc_upper_band'] = df['kc_middle_band'] + (df['atr'] * 1.5)
            df['kc_lower_band'] = df['kc_middle_band'] - (df['atr'] * 1.5)

            # Check if Bollinger Bands are inside the Keltner Channel
            df['bb_inside_kc'] = (df['bb_upper_band'] < df['kc_upper_band']) & (df['bb_lower_band'] > df['kc_lower_band'])

            if df['bb_inside_kc'].iloc[-1]:
                matching_tickers.append(ticker)
        
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
    
    return matching_tickers

def RS():
    matching_tickers=[]
    base_ticker = '^NSEI'  # Nifty 50 index symbol
    length = 52
    lengthRSMA = 50
    lengthPriceSMA = 50

    # Fetch data
    base_data = yf.download(base_ticker, period=period, interval=interval)
     
    for ticker in tickers:
        try:
            comparative_data = yf.download(ticker, period=period, interval=interval)
            
            if comparative_data.empty:
                continue
            data = pd.concat([base_data['Close'], comparative_data['Close']], axis=1)
            data.columns = ['Base', 'Comparative']
            data = data.dropna()
            
            # Calculate Relative Strength
            data['RS'] = (data['Comparative'] / data['Comparative'].shift(length)) / (data['Base'] / data['Base'].shift(length))- 1
            current_rs = data['RS'].iloc[-1]
            print(f"{ticker}: {current_rs}")
            if (current_rs > 0 and data['RS'].iloc[-1] ):
               matching_tickers.append((ticker, current_rs))
            #if (current_rs > 0 and data['RS'].iloc[-1] > data['RS'].iloc[-2] and data['RS'].iloc[-2] > data['RS'].iloc[-3] and data['RS'].iloc[-3] >data['RS'].iloc[-4] and data['RS'].iloc[-4] >data['RS'].iloc[-5] and data['RS'].iloc[-5]>data['RS'].iloc[-6] ):
             

          
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")    
    matching_tickers.sort(key=lambda x: x[1], reverse=True)

    # Extract only the tickers from the sorted list
    sorted_tickers = [ticker for ticker, rs in matching_tickers]

    return sorted_tickers
def RS_indices():
    matching_tickers=[]
    base_ticker = '^NSEI'  # Nifty 50 index symbol
    length = 52
    lengthRSMA = 50
    lengthPriceSMA = 50

    # Fetch data
    base_data = yf.download(base_ticker, period=period, interval=interval)
     
    for ticker in indices:
        try:
            comparative_data = yf.download(ticker, period=period, interval=interval)
            
            if comparative_data.empty:
                continue
            data = pd.concat([base_data['Close'], comparative_data['Close']], axis=1)
            data.columns = ['Base', 'Comparative']
            data = data.dropna()
            
            # Calculate Relative Strength
            data['RS'] = (data['Comparative'] / data['Comparative'].shift(length)) / (data['Base'] / data['Base'].shift(length))- 1
            current_rs = data['RS'].iloc[-1]
            print(f"{ticker}: {current_rs}")
            if (current_rs > 0 and data['RS'].iloc[-1] ):
               matching_tickers.append((ticker, current_rs))
            #if (current_rs > 0 and data['RS'].iloc[-1] > data['RS'].iloc[-2] and data['RS'].iloc[-2] > data['RS'].iloc[-3] and data['RS'].iloc[-3] >data['RS'].iloc[-4] and data['RS'].iloc[-4] >data['RS'].iloc[-5] and data['RS'].iloc[-5]>data['RS'].iloc[-6] ):
             

          
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")    
    matching_tickers.sort(key=lambda x: x[1], reverse=True)

    # Extract only the tickers from the sorted list
    sorted_tickers = [ticker for ticker, rs in matching_tickers]

    return sorted_tickers
def get_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date)
def momemtum():
    matching_tickers=[]
        
# Set dates
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * 2)  # 2 years of data for moving averages
    
    # Data dictionary to hold stock data
    data = {}
    
    # Fetch data for all tickers
    for ticker in tickers:
        try:
            stock_data = get_data(ticker, start_date, end_date)
            if len(stock_data) > 0:
                data[ticker] = stock_data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    # Create a DataFrame for summary
    summary = []
    
    # Analyze each stock
    for ticker, df in data.items():
        try:
            # Calculate EMAs
            df['EMA100'] = df['Close'].ewm(span=100).mean()
            df['EMA200'] = df['Close'].ewm(span=200).mean()
    
            # Last 1-year return
            one_year_return = (df['Close'][-1] / df['Close'][-252] - 1) * 100
    
            # 52-week high
            high_52_week = df['Close'][-252:].max()
            within_20_pct_high = df['Close'][-1] >= high_52_week * 0.8
    
            # More than 50% up days in the last 6 months (126 trading days)
            six_month_data = df['Close'][-126:]
            up_days = (six_month_data.pct_change() > 0).sum()
            up_days_pct = up_days / len(six_month_data) * 100
    
            # Filtering criteria
            if (df['Close'][-1] >= df['EMA100'][-1] >= df['EMA200'][-1] and
                one_year_return >= 6.5 and
                within_20_pct_high and
                up_days_pct > 50):
    
                # Calculate returns
                return_6m = (df['Close'][-1] / df['Close'][-126] - 1) * 100
                return_3m = (df['Close'][-1] / df['Close'][-63] - 1) * 100
                return_1m = (df['Close'][-1] / df['Close'][-21] - 1) * 100
    
                summary.append({
                    'Ticker': ticker,
                    'Return_6M': return_6m,
                    'Return_3M': return_3m,
                    'Return_1M': return_1m,
                })
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
    
    # Convert summary to DataFrame
    df_summary = pd.DataFrame(summary)
    
    # Round off returns to 1 decimal place
    df_summary['Return_6M'] = df_summary['Return_6M'].round(1)
    df_summary['Return_3M'] = df_summary['Return_3M'].round(1)
    df_summary['Return_1M'] = df_summary['Return_1M'].round(1)
    
    # Ranking based on returns
    df_summary['Rank_6M'] = df_summary['Return_6M'].rank(ascending=False)
    df_summary['Rank_3M'] = df_summary['Return_3M'].rank(ascending=False)
    df_summary['Rank_1M'] = df_summary['Return_1M'].rank(ascending=False)
    
    # Calculate final rank
    df_summary['Final_Rank'] = df_summary['Rank_6M'] + df_summary['Rank_3M'] + df_summary['Rank_1M']
    
    # Sort by final rank and get top 30
    df_summary_sorted = df_summary.sort_values('Final_Rank').head(30)
    
    # Assign position based on final rank
    df_summary_sorted['Position'] = np.arange(1, len(df_summary_sorted) + 1)
    for i, row in df_summary_sorted.iterrows():
        matching_tickers.append(row['Ticker']) 
  
    return matching_tickers
    
# Function to display matching tickers in the Listbox
def display_matching_stocks():
    selected_action = action_var.get()
    if selected_action == "Squeeze":
        matching_stocks = check_bollinger_inside_keltner()
    elif selected_action == "20 Day High Breaking":
        matching_stocks = check_20_day_high()
    elif selected_action == "RS":
        matching_stocks = RS()
    elif selected_action == "RS_Indices":
        matching_stocks = RS_indices()   
    elif selected_action == "Momemtum":
         matching_stocks = momemtum()    
    elif selected_action == "20 Day Low Breaking":
        matching_stocks = check_20_day_low()
    elif selected_action == "Higher High":
        matching_stocks = check_higher_highs()
    elif selected_action == "bb_up":
        matching_stocks = check_bollinger_band_crossings_up()
    elif selected_action == "bb_down":
        matching_stocks = check_bollinger_band_crossings_down()    
    elif selected_action == "Double Bottom":
        matching_stocks = check_double_bottom()
    
    if matching_stocks:
        listbox.delete(0, tk.END)  # Clear the listbox
        for stock in matching_stocks:
            listbox.insert(tk.END, stock)
    else:
        messagebox.showinfo("No Matches", "No tickers meet the criteria.")

# Function to plot the chart of the selected ticker using Matplotlib
def plot_chart(event):
    global info_ticker
    info_ticker = selected_ticker = listbox.get(listbox.curselection())
    df = yf.download(selected_ticker, period=period, interval=interval)
    
    if df.empty:
        messagebox.showerror("Data Error", "No data available for the selected ticker.")
        return

    # Calculate EMAs
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA100'] = df['Close'].ewm(span=100, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # Calculate RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # Calculate Bollinger Bands
    df['bb_middle_band'] = df['Close'].rolling(window=20).mean()
    df['bb_std_dev'] = df['Close'].rolling(window=20).std()
    df['bb_upper_band'] = df['bb_middle_band'] + (df['bb_std_dev'] * 2)
    df['bb_lower_band'] = df['bb_middle_band'] - (df['bb_std_dev'] * 2)

    # Clear the previous plot
    for widget in chart_frame1.winfo_children():
        widget.destroy()

    # Create a new plot
    fig, (ax_price, ax_volume, ax_rsi) = plt.subplots(figsize=(10, 10), nrows=3, ncols=1, sharex=True, 
                                                      gridspec_kw={'height_ratios': [3, 1, 1]})

    # Enable zoom and pan
    def on_zoom(event):
        scale_factor = 1.1 if event.button == 'up' else 0.9
        ax_price.set_xlim(ax_price.get_xlim()[0] * scale_factor, ax_price.get_xlim()[1] * scale_factor)
        ax_volume.set_xlim(ax_volume.get_xlim()[0] * scale_factor, ax_volume.get_xlim()[1] * scale_factor)
        ax_rsi.set_xlim(ax_rsi.get_xlim()[0] * scale_factor, ax_rsi.get_xlim()[1] * scale_factor)
        fig.canvas.draw()

    fig.canvas.mpl_connect('scroll_event', on_zoom)

    def on_pan(event):
        if event.button == 1:
            pan_amount = (ax_price.get_xlim()[1] - ax_price.get_xlim()[0]) * 0.05
            ax_price.set_xlim(ax_price.get_xlim()[0] + pan_amount, ax_price.get_xlim()[1] + pan_amount)
            ax_volume.set_xlim(ax_volume.get_xlim()[0] + pan_amount, ax_volume.get_xlim()[1] + pan_amount)
            ax_rsi.set_xlim(ax_rsi.get_xlim()[0] + pan_amount, ax_rsi.get_xlim()[1] + pan_amount)
            fig.canvas.draw()

    fig.canvas.mpl_connect('button_press_event', on_pan)

    ax_price.xaxis_date()
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    ax_price.set_title(f"{selected_ticker} {chart_type.capitalize()} Chart")
    ax_price.set_ylabel('Price')
    ax_price.grid(True)
    current_price = df['Close'].iloc[-1]

    if chart_type == "candlestick":
        df['Date'] = mdates.date2num(df.index.to_pydatetime())
        ohlc = df[['Date', 'Open', 'High', 'Low', 'Close']].copy()

        # Plot the candlestick chart
        candlestick_ohlc(ax_price, ohlc.values, width=0.6, colorup='g', colordown='r', alpha=0.8)
        ax_price.plot([], [], ' ', label=f'Close Price (Current: {current_price:.2f})')

    elif chart_type == "line":
        ax_price.plot(df.index, df['Close'], label=f'Close Price (Current: {current_price:.2f})', color='blue')

    # Plot EMAs
    ax_price.plot(df.index, df['EMA20'], label='20-day EMA', color='orange')
    ax_price.plot(df.index, df['EMA50'], label='50-day EMA', color='purple')
    ax_price.plot(df.index, df['EMA100'], label='100-day EMA', color='red')
    ax_price.plot(df.index, df['EMA200'], label='200-day EMA', color='blue')

    # Plot Bollinger Bands
    ax_price.plot(df.index, df['bb_middle_band'], label='Middle Band (20-day SMA)', color='black')
    ax_price.plot(df.index, df['bb_upper_band'], label='Upper Band (2 std dev)', color='gray', linestyle='--')
    ax_price.plot(df.index, df['bb_lower_band'], label='Lower Band (2 std dev)', color='gray', linestyle='--')

    ax_price.legend()

    # Plot Volume
    ax_volume.bar(df.index, df['Volume'], color='gray')
    ax_volume.set_ylabel('Volume')

    # Plot RSI
    ax_rsi.plot(df.index, df['RSI'], label='14-day RSI', color='green')
    ax_rsi.axhline(70, color='red', linestyle='--', label='Overbought')
    ax_rsi.axhline(30, color='blue', linestyle='--', label='Oversold')

    # Mark the current RSI value
    current_rsi = df['RSI'].iloc[-1]
    ax_rsi.axhline(current_rsi, color='purple', linestyle='-', label=f'Current RSI: {current_rsi:.2f}')
    ax_rsi.text(df.index[-1], current_rsi, f'{current_rsi:.2f}', color='purple', fontsize=10, ha='left', va='center')

    ax_rsi.set_ylabel('RSI')
    ax_rsi.set_xlabel('Date')
    ax_rsi.legend()

    # Embed the plot in the Tkinter GUI
    canvas = FigureCanvasTkAgg(fig, master=chart_frame1)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# Function to update the chart type based on selection
def update_chart_type(event):
    global chart_type
    chart_type = chart_type_var.get()
    # Refresh the chart based on the new chart type if an item is selected
    if listbox.curselection():
        plot_chart(None)

# Function to update the period based on selection
def update_period(event):
    global period
    period = period_var.get()
    #display_matching_stocks()  # Refresh the list based on the new period

# Function to update the interval based on selection
def update_interval(event):
    global interval
    interval = interval_var.get()
    #display_matching_stocks()  # Refresh the list based on the new interval

# Function to save the list of matching tickers to a file
def save_list1():
    matching_stocks = listbox.get(0, tk.END)
    if not matching_stocks:
        messagebox.showinfo("Save Error", "No tickers to save.")
        return
    
    save_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_file:
        with open(save_file, "w") as file:
            file.write("\n".join(ticker.replace('.NS', '') for ticker in matching_stocks))
        messagebox.showinfo("Save Successful", f"List saved to {save_file}")

# Function to open and load a list of tickers from a file
def open_list():
    open_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if open_file:
        with open(open_file, "r") as file:
            loaded_tickers = [line.strip() + '.NS' for line in file]
        listbox.delete(0, tk.END)  # Clear existing items in the listbox
        for ticker in loaded_tickers:
            listbox.insert(tk.END, ticker)
        messagebox.showinfo("Load Successful", f"List loaded from {open_file}")

# Function to load tickers from a CSV file
def load_tickers():
    global tickers
    csv_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if csv_file:
        df = pd.read_csv(csv_file, header=None)
        tickers = [f"{ticker.strip()}.NS" for ticker in df[0].tolist()]
        # Update the Listbox with new tickers
        listbox.delete(0, tk.END)
        for ticker in tickers:
            listbox.insert(tk.END, ticker)
        messagebox.showinfo("Tickers Loaded", "Tickers list has been updated from the CSV file.")

# Function to handle dropdown menu actions
def menu_action(selection):
    if selection == "Squeeze":
        display_matching_stocks()
    elif selection == "Save List":
        save_list1()
    elif selection == "Open List":
        open_list()
    elif selection == "Load Tickers":
        load_tickers()
        
def open_link():
    global info_ticker
    url = f"https://www.screener.in/company/{info_ticker.replace('.NS','')}/"
    webbrowser.open(url)
        

# Setting up the GUI
root = tk.Tk()
root.title("Ninjalui... ")
root.geometry("1280x1080")
# Create the main Notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)



# Create a frame for the layout
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Create tabs

tab_intro = ttk.Frame(notebook)
tab_compare =ttk.Frame(notebook)
tab_signs=ttk.Frame(notebook)
tab_cleaner=ttk.Frame(notebook)
tab_rsi=ttk.Frame(notebook)
tab_compare_rank=ttk.Frame(notebook)
tab_near_break=ttk.Frame(notebook)
tab_roe=ttk.Frame(notebook)
tab_quant=ttk.Frame(notebook)
tab_market_view1=ttk.Frame(notebook)
tab_market_view1.grid(row=0, column=0, pady=1)

#Add to the notebook 
notebook.add(tab_intro, text=" The Fact ")
notebook.add(main_frame, text=" The Seer ")
notebook.add(tab_compare,text=" The Happenings ")
notebook.add(tab_signs,text=" The Signs ")
notebook.add(tab_rsi,text=" RSI ")
notebook.add(tab_near_break,text=" Near High ")
notebook.add(tab_compare_rank,text=" Rank Compare ")
notebook.add(tab_roe,text=" ROE ")
notebook.add(tab_quant,text=" Quant Report ")
notebook.add(tab_market_view1, text=" Market State ")
notebook.add(tab_cleaner, text=" Mass cleaner ")


intro_label = tk.Label(tab_intro, text=" ||  JAI MAA SARADA ... ||\n\n The Creator and Destroyer of Worlds..The Omnipotenet The Omniscient .... The Giver of Knowledge and Power .... "
                                        ".\n   ..This will break the Market ... Ninjalui... "
                                        "Select stocks from the list or load your own, and use the provided criteria to find potential trading opportunities.\n\n"
                                        "Use the controls on the Stock Analysis tab to customize your analysis.", justify=tk.LEFT, padx=10, pady=10)
intro_label.pack()

# Create a frame for the Listbox and the chart
listbox_frame = tk.Frame(main_frame)
listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

chart_frame1 = tk.Frame(main_frame)
chart_frame1.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create a button to load tickers from a CSV file
load_tickers_button = tk.Button(listbox_frame, text="Tickers", command=load_tickers)
load_tickers_button.pack(anchor="nw", padx=10, pady=10)

info_button = tk.Button(listbox_frame, text="Info ",command=open_link)
info_button.pack(anchor="nw", padx=10, pady=10)

# Create a dropdown menu for actions at the top left
action_var = tk.StringVar(value="Squeeze")
action_menu = ttk.Combobox(listbox_frame, textvariable=action_var, values=[
    "Squeeze","Momemtum", "20 Day High Breaking", "20 Day Low Breaking", "Higher High",
    "bb_up","bb_down", "Double Bottom","RS","RS_Indices"], state="readonly")
action_menu.pack(anchor="nw", padx=10, pady=10)
action_menu.bind("<<ComboboxSelected>>", lambda event: display_matching_stocks())

# Create a label and dropdown for chart type selection at the top
chart_type_label = tk.Label(listbox_frame, text="Select Chart Type:")
chart_type_label.pack(pady=5)

chart_type_var = tk.StringVar(value="candlestick")
chart_type_menu = ttk.Combobox(listbox_frame, textvariable=chart_type_var, values=["candlestick", "line"], state="readonly")
chart_type_menu.pack(pady=5)
chart_type_menu.bind("<<ComboboxSelected>>", update_chart_type)

# Create a label and dropdown for period selection
period_label = tk.Label(listbox_frame, text="Select Period:")
period_label.pack(pady=5)

period_var = tk.StringVar(value="1y")
period_menu = ttk.Combobox(listbox_frame, textvariable=period_var, values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"], state="readonly")
period_menu.pack(pady=5)
period_menu.bind("<<ComboboxSelected>>", update_period)

# Create a label and dropdown for interval selection
interval_label = tk.Label(listbox_frame, text="Select Interval:")
interval_label.pack(pady=5)

interval_var = tk.StringVar(value="1d")
interval_menu = ttk.Combobox(listbox_frame, textvariable=interval_var, values=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"], state="readonly")
interval_menu.pack(pady=5)
interval_menu.bind("<<ComboboxSelected>>", update_interval)

# Create a Listbox to display the matching stocks
listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
listbox.bind('<<ListboxSelect>>', plot_chart)

# Existing code...

# Function to delete the selected ticker from the Listbox and refresh the list
def delete_selected_ticker(event=None):
    selected_index = listbox.curselection()
    if selected_index:
        selected_ticker = listbox.get(selected_index)
        tickers.remove(selected_ticker)
        listbox.delete(selected_index)
        #refresh_listbox()

# Function to refresh the Listbox with current tickers
def refresh_listbox():
    listbox.delete(0, tk.END)  # Clear the Listbox
    for ticker in tickers:
        listbox.insert(tk.END, ticker)  # Re-populate the Listbox with updated tickers

# Function to create a context menu for the Listbox
def create_context_menu(event):
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Delete", command=delete_selected_ticker)
    context_menu.post(event.x_root, event.y_root)
    
def weekly_report():
    
    
    return
    
def daily_report():
    return
# Binding the right-click to the Listbox
listbox.bind("<Button-3>", create_context_menu)

# Existing code...


# Create a menu for file operations
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)



# New tab code for compare
# Function to load a CSV file and return the list of values from the first column
def load_csv_list():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        return df.iloc[:, 0].tolist(), os.path.basename(file_path)   # Get the first column as a list
    return []

# Function to compare the two lists and display the result
def compare_lists():
    if not list1 or not list2:
        messagebox.showerror("Error", "Please load both CSV files.")
        return

    common_elements = set(list1) & set(list2)
    new_in_list1 = set(list1) - set(list2)
    new_in_list2 = set(list2) - set(list1)

    txt_common.delete(1.0, tk.END)
    txt_new_in_list1.delete(1.0, tk.END)
    txt_new_in_list2.delete(1.0, tk.END)

    txt_common.insert(tk.END, "\n".join(common_elements))
    txt_new_in_list1.insert(tk.END, "\n".join(new_in_list1))
    txt_new_in_list2.insert(tk.END, "\n".join(new_in_list2))

# Initialize the lists
list1 = []
list2 = []
file1_name = ""
file2_name = ""

# Function to load the first list
def load_list1():
    global list1
    list1, file1_name = load_csv_list()
    lbl_status1.config(text=f"Loaded {len(list1)} items from {file1_name}")

# Function to load the second list
def load_list2():
    global list2
    list2, file2_name = load_csv_list()
    lbl_status2.config(text=f"Loaded {len(list2)} items from {file2_name}")

# Create the main window


# Create buttons to load CSV files
btn_load_list1 = tk.Button(tab_compare, text="Load List 1 (CSV)", command=load_list1)
btn_load_list2 = tk.Button(tab_compare, text="Load List 2 (CSV)", command=load_list2)

btn_load_list1.grid(row=0, column=0, padx=10, pady=10)
btn_load_list2.grid(row=0, column=1, padx=10, pady=10)

# Create labels to show the status of loaded lists
lbl_status1 = tk.Label(tab_compare, text="List 1 not loaded")
lbl_status2 = tk.Label(tab_compare, text="List 2 not loaded")

lbl_status1.grid(row=1, column=0, padx=10, pady=5)
lbl_status2.grid(row=1, column=1, padx=10, pady=5)

# Create button to compare lists
btn_compare = tk.Button(tab_compare, text="Compare Lists", command=compare_lists)
btn_compare.grid(row=2, column=0, columnspan=2, pady=10)

# Create text boxes to display the results
lbl_common = tk.Label(tab_compare, text="Common Elements:")
lbl_common.grid(row=3, column=0, padx=10, pady=5)

txt_common = tk.Text(tab_compare, height=10, width=40)
txt_common.grid(row=4, column=0, padx=10, pady=5)

lbl_new_in_list1 = tk.Label(tab_compare, text="New in List 1:")
lbl_new_in_list1.grid(row=3, column=1, padx=10, pady=5)

txt_new_in_list1 = tk.Text(tab_compare, height=10, width=40)
txt_new_in_list1.grid(row=4, column=1, padx=10, pady=5)

lbl_new_in_list2 = tk.Label(tab_compare, text="New in List 2:")
lbl_new_in_list2.grid(row=5, column=0, padx=10, pady=5)

txt_new_in_list2 = tk.Text(tab_compare, height=10, width=40)
txt_new_in_list2.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

#Code for nse sectors chart

# List of Nifty indices symbols and corresponding ETFs or proxies for PE ratio
nifty_indices = {
    "NIFTY 50": "^NSEI",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY FIN SERVICE": "^CNXFINANCE",
    "Parag flexi":"0P0000YWL1.BO",
    "HDFC flexi":"0P0000XW77.BO",
    "Conservative:":"0P0001MB7K.BO"
    
}

# Corresponding symbols for PE ratio (for example, NIFTYBEES for NIFTY 50)
pe_proxies = {
    "NIFTY 50": "NIFTYBEES.NS",
    "NIFTY BANK": "BANKBEES.NS",
    "NIFTY IT": "ITBEES.NS",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY AUTO": "AUTOBEES.NS",
    "NIFTY PHARMA": "NETFPHARMA.NS",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY ENERGY": "ENERGYBEES.NS",
    "NIFTY FIN SERVICE": "^CNXFINANCE",
    "Parag flexi":"^CNXFINANCE",
    "HDFC flexi":"0P0000XW77.BO",
    "Conservative:":"0P0001MB7K.BO"
}

# Available periods and intervals
periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

# Function to plot the data
def plot_data(symbol, period, interval):
    data = yf.download(symbol, period=period, interval=interval)
    
    if data.empty:
        messagebox.showerror("Error", "No data available for the selected options.")
        return
    
    # Calculate technical indicators
    data['EMA20'] = ta.trend.ema_indicator(data['Close'], window=20)
    data['EMA50'] = ta.trend.ema_indicator(data['Close'], window=50)
    data['EMA100'] = ta.trend.ema_indicator(data['Close'], window=100)
    data['EMA200'] = ta.trend.ema_indicator(data['Close'], window=200)
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    
    # Plotting
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1, 1]})
    
    # Plot the closing price and EMAs
    axs[0].plot(data['Close'], label='Close Price')
    axs[0].plot(data['EMA20'], label='EMA20')
    axs[0].plot(data['EMA50'], label='EMA50')
    axs[0].plot(data['EMA100'], label='EMA100')
    axs[0].plot(data['EMA200'], label='EMA200')
    axs[0].set_title(f'{symbol} - {period} - {interval}')
    axs[0].legend()
    
    # Plot the volume
    axs[1].bar(data.index, data['Volume'], color='gray')
    axs[1].set_title('Volume')
    
    # Plot the RSI
    current_rsi2=data['RSI'].iloc[-1]
    axs[2].plot(data['RSI'], label=f'RSI: {current_rsi2:.2f}')
    axs[2].axhline(70, color='red', linestyle='--')
    axs[2].axhline(30, color='green', linestyle='--')
    axs[2].set_title('Relative Strength Index (RSI)')
    axs[2].legend()
    
    # Display the plot
    for ax in axs:
        ax.grid()
    fig.tight_layout()
    
    # Clear the previous plot
    for widget in plot_frame.winfo_children():
        widget.destroy()
    
    # Display the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Function to update the PE ratio and the plot when an index, period, or interval is selected
def update_plot(*args):
    symbol = nifty_indices[cmb_indices.get()]
    pe_symbol = pe_proxies[cmb_indices.get()]
    
    # Try to get PE ratio using the PE proxy symbol
    try:
        stock = yf.Ticker(pe_symbol)
        pe_ratio = stock.info.get('trailingPE', 'N/A')
    except:
        pe_ratio = "N/A"
    
    lbl_pe_value.config(text=f"PE Ratio: {pe_ratio}")
    
    period = cmb_periods.get()
    interval = cmb_intervals.get()
    plot_data(symbol, period, interval)



# Dropdown for selecting Nifty index
lbl_index = tk.Label(tab_signs, text="Select Nifty Index:")
lbl_index.grid(row=0, column=0, padx=10, pady=10, sticky="w")
cmb_indices = ttk.Combobox(tab_signs, values=list(nifty_indices.keys()), state='readonly')
cmb_indices.grid(row=0, column=1, padx=10, pady=10, sticky="w")
cmb_indices.current(0)
cmb_indices.bind("<<ComboboxSelected>>", update_plot)

# Dropdown for selecting period
lbl_period = tk.Label(tab_signs, text="Select Period:")
lbl_period.grid(row=1, column=0, padx=10, pady=10, sticky="w")
cmb_periods = ttk.Combobox(tab_signs, values=periods, state='readonly')
cmb_periods.grid(row=1, column=1, padx=10, pady=10, sticky="w")
cmb_periods.set('1y')  # Set default period to 1y
cmb_periods.bind("<<ComboboxSelected>>", update_plot)

# Dropdown for selecting interval
lbl_interval = tk.Label(tab_signs, text="Select Interval:")
lbl_interval.grid(row=2, column=0, padx=10, pady=10, sticky="w")
cmb_intervals = ttk.Combobox(tab_signs, values=intervals, state='readonly')
cmb_intervals.grid(row=2, column=1, padx=10, pady=10, sticky="w")
cmb_intervals.set('1d')  # Set default interval to 1d
cmb_intervals.bind("<<ComboboxSelected>>", update_plot)

# Label to display PE ratio
lbl_pe = tk.Label(tab_signs, text="PE Ratio:")
lbl_pe.grid(row=3, column=0, padx=10, pady=10, sticky="w")
lbl_pe_value = tk.Label(tab_signs, text="Loading...")
lbl_pe_value.grid(row=3, column=1, padx=10, pady=10, sticky="w")

# Frame to display the plot
plot_frame = tk.Frame(tab_signs)
plot_frame.grid(row=0, column=2, rowspan=4, padx=10, pady=10)

# Initial plot with default settings
update_plot()


#Code for cleaner


def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory(
        title="Select Folder Containing CSV Files"
    )
    if folder_path:
        process_button.config(state=tk.NORMAL)
        folder_path_var.set(folder_path)
        messagebox.showinfo("Folder Selected", f"Selected folder: {folder_path}")

def process_files():
    if not folder_path:
        messagebox.showerror("Error", "No folder selected")
        return

    try:
        # Create a new folder for cleaned files
        cleaned_folder = os.path.join(folder_path, "Cleaned_Files")
        os.makedirs(cleaned_folder, exist_ok=True)

        # Process each CSV file in the selected folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv") and file_name != "Cleaned_Files":
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_csv(file_path)

                # Check if column 'Symbol' exists
                if 'Symbol' not in df.columns:
                    messagebox.showwarning("Warning", f"Column 'Symbol' not found in file: {file_name}")
                    continue

                # Keep only the 'Symbol' column and remove the header
                df_filtered = df[['Symbol']]

                # Save the filtered data to a new CSV file in the 'Cleaned_Files' folder
                cleaned_file_path = os.path.join(cleaned_folder, file_name)
                df_filtered.to_csv(cleaned_file_path, index=False, header=False)

        messagebox.showinfo("Success", "All files processed and saved in the 'Cleaned_Files' folder")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window


# Variables
folder_path = None
folder_path_var = tk.StringVar()

# Create GUI elements
label = tk.Label(tab_cleaner, text="Select a folder containing CSV files:")
label.pack(pady=10)

select_button = tk.Button(tab_cleaner, text="Select Folder", command=select_folder)
select_button.pack(pady=10)

process_button = tk.Button(tab_cleaner, text="Process Files", command=process_files, state=tk.DISABLED)
process_button.pack(pady=10)


# Rsi tab

def load_csv():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

def search_rsi():
    if not file_path or not min_rsi_entry.get() or not max_rsi_entry.get():
        messagebox.showerror("Error", "Please select a CSV file and enter both minimum and maximum RSI levels.")
        return

    try:
        min_rsi = float(min_rsi_entry.get())
        max_rsi = float(max_rsi_entry.get())
        interval = period_var1.get()
        period = "5y"  # Default period is 5 years
        
        # Read CSV without headers and append ".NS" to each ticker
        stocks = pd.read_csv(file_path, header=None)[0].tolist()
        stocks = [f"{stock}.NS" for stock in stocks]

        stock_listbox.delete(0, tk.END)
        
        matching_stocks = []

        for stock in stocks:
            data = yf.download(stock, period=period, interval=interval)
            data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
            
            if not data.empty:
                current_rsi = data['RSI'].iloc[-1]
                if min_rsi <= current_rsi <= max_rsi:
                    stock_info = yf.Ticker(stock).info
                    mcap = stock_info.get('marketCap', 0)
                    matching_stocks.append((stock, round(current_rsi, 2), mcap))

        # Sort matching stocks by market capitalization in descending order
        matching_stocks.sort(key=lambda x: x[2], reverse=True)

        stock_listbox.delete(0, tk.END)
        for stock, rsi, mcap in matching_stocks:
            stock_listbox.insert(tk.END, f"{stock} - RSI: {rsi}, MCAP: {mcap:,}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def save_list():
    try:
        #if not file_path:
           # messagebox.showerror("Error", "Please select a CSV file first.")
           # return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV Files", "*.csv")])
        if not save_path:
            messagebox.showerror("Error", "No save_path")
            return
        
        # Extract tickers from listbox and remove ".NS"
        tickers = [item.split(' ')[0] for item in stock_listbox.get(0, tk.END)]
        tickers = [ticker.replace('.NS', '') for ticker in tickers]

        # Save to CSV
        df = pd.DataFrame(tickers, columns=["Ticker"])
        df.to_csv(save_path, index=False)
        
        messagebox.showinfo("Success", "List saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")



file_path = None

# Frame for CSV file selection
frame_file = tk.Frame(tab_rsi)
frame_file.pack(pady=10)

tk.Label(frame_file, text="Select CSV File:").pack(side=tk.LEFT, padx=5)
csv_entry = tk.Entry(frame_file, width=40)
csv_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_file, text="Browse", command=load_csv).pack(side=tk.LEFT, padx=5)

# Frame for RSI value input
frame_rsi = tk.Frame(tab_rsi)
frame_rsi.pack(pady=10)

tk.Label(frame_rsi, text="Min RSI Level:").pack(side=tk.LEFT, padx=5)
min_rsi_entry = tk.Entry(frame_rsi, width=10)
min_rsi_entry.pack(side=tk.LEFT, padx=5)

tk.Label(frame_rsi, text="Max RSI Level:").pack(side=tk.LEFT, padx=5)
max_rsi_entry = tk.Entry(frame_rsi, width=10)
max_rsi_entry.pack(side=tk.LEFT, padx=5)

# Frame for period selection
frame_period = tk.Frame(tab_rsi)
frame_period.pack(pady=10)

tk.Label(frame_period, text="Select Interval:").pack(side=tk.LEFT, padx=5)
period_var1 = tk.StringVar(value="1wk")  # Default interval is 1 week
period_options = ["1d", "1wk", "1mo"]
period_menu = ttk.Combobox(frame_period, textvariable=period_var1, values=period_options, state="readonly")
period_menu.pack(side=tk.LEFT, padx=5)


# Search Button
tk.Button(tab_rsi, text="Search", command=search_rsi).pack(pady=20)

# Save List Button
tk.Button(tab_rsi, text="Save List", command=save_list).pack(pady=10)

# Listbox for displaying matching stocks
tk.Label(tab_rsi, text="Matching Stocks:").pack(pady=10)
stock_listbox = tk.Listbox(tab_rsi, selectmode=tk.SINGLE, height=15)
stock_listbox.pack(fill=tk.BOTH, expand=True)

# Scrollbar for listbox
scrollbar = tk.Scrollbar(stock_listbox, orient="vertical")
scrollbar.config(command=stock_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
stock_listbox.config(yscrollcommand=scrollbar.set)


#CODE FOR TAB_RANK
def load_old_csv():
    global old_file_path
    old_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if old_file_path:
        old_csv_entry.delete(0, tk.END)
        old_csv_entry.insert(0, old_file_path)
        display_old_tickers()

def load_new_csv():
    global new_file_path
    new_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if new_file_path:
        new_csv_entry.delete(0, tk.END)
        new_csv_entry.insert(0, new_file_path)
        display_new_tickers()

def display_old_tickers():
    if not old_file_path:
        return
    
    try:
        old_df = pd.read_csv(old_file_path, header=None, names=['Ticker'])
        old_listbox.delete(0, tk.END)
        for index, row in old_df.iterrows():
            old_listbox.insert(tk.END, f"{row['Ticker']} - Rank: {index + 1}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the old file: {str(e)}")

def display_new_tickers():
    if not new_file_path:
        return
    
    try:
        new_df = pd.read_csv(new_file_path, header=None, names=['Ticker'])
        new_listbox.delete(0, tk.END)
        for index, row in new_df.iterrows():
            new_listbox.insert(tk.END, f"{row['Ticker']} - Rank: {index + 1}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the new file: {str(e)}")

def compare_lists():
    if not old_file_path or not new_file_path:
        messagebox.showerror("Error", "Please select both old and new CSV files.")
        return

    try:
        # Read CSV files
        old_df = pd.read_csv(old_file_path, header=None, names=['Ticker'])
        new_df = pd.read_csv(new_file_path, header=None, names=['Ticker'])

        # Assign ranks based on position (index + 1)
        old_df['Rank'] = old_df.index + 1
        new_df['Rank'] = new_df.index + 1

        # Convert to dictionaries with ticker as key and rank as value
        old_list = old_df.set_index('Ticker')['Rank'].to_dict()
        new_list = new_df.set_index('Ticker')['Rank'].to_dict()

        # Clear previous listbox entries
        comparison_listbox.delete(0, tk.END)

        # Prepare comparison results
        comparison = []

        # Compare tickers in the old list
        for ticker, old_rank in old_list.items():
            if ticker in new_list:
                new_rank = new_list[ticker]
                comparison.append(f"{ticker} - Old Rank: {old_rank} / New Rank: {new_rank}")
            else:
                comparison.append(f"{ticker} - Old Rank: {old_rank} / New Rank: Out")

        # Add new list tickers not present in old list
        for ticker, new_rank in new_list.items():
            if ticker not in old_list:
                comparison.append(f"{ticker} - Old Rank: In / New Rank: {new_rank}")

        # Populate listbox with comparison results and apply highlighting
        for idx, entry in enumerate(comparison):
            comparison_listbox.insert(tk.END, entry)
            
            # Apply highlighting
            if "Out" in entry:
                comparison_listbox.itemconfig(idx, {'bg': 'red'})
            elif "In" in entry:
                comparison_listbox.itemconfig(idx, {'bg': 'green'})

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during comparison: {str(e)}")

# Create main window


old_file_path = None
new_file_path = None

# Frame for old CSV file selection
frame_old_file = tk.Frame(tab_compare_rank)
frame_old_file.pack(pady=10)

tk.Label(frame_old_file, text="Select Old CSV File:").pack(side=tk.LEFT, padx=5)
old_csv_entry = tk.Entry(frame_old_file, width=50)
old_csv_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_old_file, text="Browse", command=load_old_csv).pack(side=tk.LEFT, padx=5)

# Frame for new CSV file selection
frame_new_file = tk.Frame(tab_compare_rank)
frame_new_file.pack(pady=10)

tk.Label(frame_new_file, text="Select New CSV File:").pack(side=tk.LEFT, padx=5)
new_csv_entry = tk.Entry(frame_new_file, width=50)
new_csv_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_new_file, text="Browse", command=load_new_csv).pack(side=tk.LEFT, padx=5)

# Compare Button
tk.Button(tab_compare_rank, text="Compare", command=compare_lists).pack(pady=20)

# Listboxes for displaying tickers
frame_listboxes = tk.Frame(tab_compare_rank)
frame_listboxes.pack(pady=10, fill=tk.BOTH, expand=True)

tk.Label(frame_listboxes, text="Old Tickers:").pack(side=tk.LEFT, padx=10)
old_listbox = tk.Listbox(frame_listboxes, height=20, width=40)
old_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(frame_listboxes, text="New Tickers:").pack(side=tk.LEFT, padx=10)
new_listbox = tk.Listbox(frame_listboxes, height=20, width=40)
new_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Listbox for comparison results
tk.Label(tab_compare_rank, text="Old vs New Comparison:").pack(pady=10)
comparison_listbox = tk.Listbox(tab_compare_rank, height=30, width=100)
comparison_listbox.pack(pady=10, fill=tk.BOTH, expand=True)


#Code for Near High
tickers = []

# Function to find the swing high
def find_swing_high(data):
    return data['High'].max()

# Function to check the percentage away from the swing high
def check_swing_high():
    period = period_var3.get()
    interval = interval_var3.get()
    print(period,interval)
    
    results = []
    
    # Clear the listbox
    result_listbox.delete(0, tk.END)
    
    for ticker in tickers:
        # Download the data
        data = yf.download(ticker, period=period, interval=interval)
        
        if not data.empty:
            # Find the swing high
            swing_high = find_swing_high(data)
            
            # Calculate the percentage away from the swing high
            last_close = data['Close'][-1]
            percentage_away = ((swing_high - last_close) / swing_high) * 100
            
            # Append the result
            results.append((ticker, percentage_away))
    
    # Sort the results by percentage away in ascending order
    results.sort(key=lambda x: x[1])
    
    # Display the results in the listbox
    for ticker, percentage_away in results:
        result_listbox.insert(tk.END, f" {ticker}:   {percentage_away:.2f}% ")

# Function to load tickers from a CSV file
def load_tickers():
    global tickers
    file_path = filedialog.askopenfilename(title="Open CSV", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            tickers = [row[0].strip() + ".NS" for row in reader]
        messagebox.showinfo("Loaded", f"Loaded {len(tickers)} tickers from the file.")

# Function to save the results to a CSV file
def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for ticker in result_listbox.get(0, tk.END):
                ticker_name = ticker.split(":")[0].replace(".NS", "")
                writer.writerow([ticker_name])
        messagebox.showinfo("Saved", "Results saved successfully.")

# Create the main application window


# Period dropdown
tk.Label(tab_near_break, text="Period:").grid(row=0, column=0, padx=10, pady=10)
period_var3 = tk.StringVar(value="5y")
period_dropdown = ttk.Combobox(tab_near_break, textvariable=period_var3)
period_dropdown['values'] = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
period_dropdown.grid(row=0, column=1, padx=10, pady=10)

# Interval dropdown
tk.Label(tab_near_break, text="Interval:").grid(row=1, column=0, padx=10, pady=10)
interval_var3 = tk.StringVar(value="1d")
interval_dropdown = ttk.Combobox(tab_near_break, textvariable=interval_var3)
interval_dropdown['values'] = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
interval_dropdown.grid(row=1, column=1, padx=10, pady=10)

# Load Tickers button
load_button = tk.Button(tab_near_break, text="Load Tickers", command=load_tickers)
load_button.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

# Check button
check_button = tk.Button(tab_near_break, text="Check", command=check_swing_high)
check_button.grid(row=2, column=1, pady=10, padx=10, sticky="ew")

# Save Results button
save_button = tk.Button(tab_near_break, text="Save Results", command=save_results)
save_button.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

# Result listbox
tk.Label(tab_near_break, text="Tickers and % Away from Swing High:").grid(row=4, column=0, padx=10, pady=10)
result_listbox = tk.Listbox(tab_near_break, width=50, height=15)
result_listbox.grid(row=5, column=0, columnspan=2, padx=10, pady=10)


#Code for ROE 


def load_csv():
    print("Loading CSV file...")
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return

    try:
        global tickers
        tickers = pd.read_csv(file_path, header=None)[0].tolist()
        tickers = [ticker + ".NS" for ticker in tickers]
        print(f"Tickers loaded: {tickers}")
        messagebox.showinfo("Success", "Tickers loaded successfully.")
    except Exception as e:
        print(f"Failed to load CSV file: {e}")
        messagebox.showerror("Error", f"Failed to load CSV file.\n{e}")

def analyze_stocks():
    print("Analyzing stocks...")
    try:
        min_roe = float(roe_entry.get()) / 100  # Convert percentage to decimal
        print(f"Minimum ROE: {min_roe * 100:.2f}%")
    except ValueError:
        print("Invalid input for ROE.")
        messagebox.showerror("Error", "Please enter a valid percentage for ROE.")
        return

    global sort_by
    sort_by = sort_criteria.get()

    results = []

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            roe = info.get('returnOnEquity', None)
            pe_ratio = info.get('forwardEps', None)
            market_cap = info.get('marketCap', None)
            
            # Check if ROE, PE Ratio, and Market Cap are valid numbers
            if roe is None:
                print(f"ROE data is not available for {ticker}. Skipping...")
                continue
            if not isinstance(roe, (int, float)) or not isinstance(market_cap, (int, float)):
                print(f"Invalid data for {ticker}. ROE: {roe}, Market Cap: {market_cap}. Skipping...")
                continue

            if roe >= min_roe:
                if pe_ratio is None:
                    pe_ratio = float('nan')  # Handle missing PE ratio
                results.append((ticker, roe * 100, market_cap, pe_ratio))
                print(f"Added {ticker}: ROE={roe * 100:.2f}%, Market Cap={market_cap}, PE Ratio={pe_ratio}")
            else:
                print(f"{ticker} does not meet the ROE criteria.")
                
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            result_listbox.insert(tk.END, f"Error fetching data for {ticker}: {e}")
    
    # Sort results based on selected criteria
    print(f"Sorting results by {sort_by}...")
    if sort_by == 'ROE':
        results.sort(key=lambda x: x[1], reverse=True)
    elif sort_by == 'Market Cap':
        results.sort(key=lambda x: x[2], reverse=True)
    elif sort_by == 'PE Ratio':
        results.sort(key=lambda x: x[3] if not pd.isna(x[3]) else float('-inf'), reverse=True)

    result_listbox.delete(0, tk.END)  # Clear previous results
    
    for ticker, roe, market_cap, pe_ratio in results:
        result_listbox.insert(tk.END, f"{ticker}: ROE={roe:.2f}%, Market Cap={market_cap}, PE Ratio={pe_ratio}")
        print(f"Displaying {ticker}: ROE={roe:.2f}%, Market Cap={market_cap}, PE Ratio={pe_ratio}")

    global sorted_results
    sorted_results = results
    print("Analysis complete.")

def save_results():
    if not sorted_results:
        print("No results to save.")
        messagebox.showerror("Error", "No results to save.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not save_path:
        return

    try:
        # Save only the ticker symbols, removing the ".NS" suffix
        cleaned_tickers = [ticker[:-3] for ticker, _, _, _ in sorted_results]
        df = pd.DataFrame(cleaned_tickers, columns=["Ticker"])
        df.to_csv(save_path, index=False)
        print(f"Ticker symbols saved to {save_path}.")
        messagebox.showinfo("Success", "Ticker symbols saved successfully.")
    except Exception as e:
        print(f"Failed to save results: {e}")
        messagebox.showerror("Error", f"Failed to save results.\n{e}")

# Create the main window


# Create UI elements
load_button = tk.Button(tab_roe, text="Load CSV", command=load_csv)
load_button.pack(pady=10)

roe_label = tk.Label(tab_roe, text="Minimum ROE (%):")
roe_label.pack()
roe_entry = tk.Entry(tab_roe)
roe_entry.pack()

sort_criteria = tk.StringVar(value='ROE')
sort_menu = tk.OptionMenu(tab_roe, sort_criteria, 'ROE', 'Market Cap', 'PE Ratio')
sort_menu.pack(pady=10)

analyze_button = tk.Button(tab_roe, text="Analyze", command=analyze_stocks)
analyze_button.pack(pady=10)

result_listbox = tk.Listbox(tab_roe, width=80)
result_listbox.pack(pady=20)

save_button = tk.Button(tab_roe, text="Save Results", command=save_results)
save_button.pack(pady=10)

# Start the GUI main loop

#Code for Quant
# Function to load tickers from a CSV file and append '.NS'
def load_csv():
    print("Loading CSV file...")
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return

    try:
        global tickers
        tickers = pd.read_csv(file_path, header=None)[0].tolist()
        tickers = [ticker + ".NS" for ticker in tickers]
        print(f"Tickers loaded: {tickers}")

        ticker_listbox.delete(0, tk.END)  # Clear previous entries in the listbox
        for ticker in tickers:
            ticker_listbox.insert(tk.END, ticker)

        messagebox.showinfo("Success", "Tickers loaded successfully.")
    except Exception as e:
        print(f"Failed to load CSV file: {e}")
        messagebox.showerror("Error", f"Failed to load CSV file.\n{e}")

# Function to calculate metrics
def calculate_metrics(ticker, period, interval):
    try:
        print(f"Fetching data for {ticker}...")
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            print(f"No data found for {ticker}.")
            return None

        # Calculate metrics
        returns = data['Adj Close'].pct_change().dropna()
        cumulative_returns = (1 + returns).cumprod()
        annualized_return = cumulative_returns[-1] ** (1 / (len(returns) / 252)) - 1
        annualized_volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / annualized_volatility
        
        # Placeholder for actual beta and alpha calculations
        beta = np.random.uniform(0.5, 1.5)  # Example values for illustration
        alpha = np.random.uniform(-0.05, 0.05)  # Example values for illustration
        
        # Placeholder for Sortino Ratio and Calmar Ratio calculations
        downside_returns = returns[returns < 0].dropna()
        sortino_ratio = annualized_return / downside_returns.std() * np.sqrt(252) if downside_returns.std() > 0 else np.nan
        max_drawdown = (cumulative_returns.cummax() - cumulative_returns).max()
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else np.nan

        return {
            'ticker': ticker,
            'beta': beta,
            'alpha': alpha,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio
        }
    except Exception as e:
        print(f"Error fetching or analyzing data for {ticker}: {e}")
        return None

# Function to calculate and display metrics
def calculate_and_display_metrics():
    period = period_var.get()
    interval = interval_var.get()

    results = []
    for ticker in tickers:
        metrics = calculate_metrics(ticker, period, interval)
        if metrics:
            results.append(metrics)

    # Sort results based on user selection
    sort_by = sort_by_var.get()
    if sort_by:
        results.sort(key=lambda x: x[sort_by], reverse=True)

    # Display results
    ticker_listbox.delete(0, tk.END)  # Clear previous entries in the listbox
    for result in results:
        display_text = f"{result['ticker']} - Beta: {result['beta']:.2f}, Alpha: {result['alpha']:.2f}, Sharpe: {result['sharpe_ratio']:.2f}, Sortino: {result['sortino_ratio']:.2f}, Calmar: {result['calmar_ratio']:.2f}"
        ticker_listbox.insert(tk.END, display_text)

    messagebox.showinfo("Success", "Metrics calculated and displayed successfully.")

# Function to save the displayed tickers to a CSV file
def save_csv():
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not save_path:
        print("No save path selected.")
        return

    try:
        results = [line.split(" - ")[0] for line in ticker_listbox.get(0, tk.END)]
        results = [ticker.replace(".NS", "") for ticker in results]
        df = pd.DataFrame(results, columns=["Ticker"])
        df.to_csv(save_path, index=False)
        print(f"File saved as {save_path}")
        messagebox.showinfo("Success", "Tickers saved successfully.")
    except Exception as e:
        print(f"Failed to save CSV file: {e}")
        messagebox.showerror("Error", f"Failed to save CSV file.\n{e}")

# Function to show hints about the metrics
def show_hints():
    hints = (
        "Beta: Measures the volatility of the stock relative to the market. \n"
        "  - Optimal Value: Around 1 (similar volatility to the market).\n"
        "  - High Beta (>1) indicates higher volatility than the market.\n"
        "  - Low Beta (<1) indicates lower volatility than the market.\n\n"
        "Alpha: Represents the stock's return relative to the expected return based on its beta. \n"
        "  - Optimal Value: Positive value indicates outperformance relative to the expected return.\n"
        "  - Higher Alpha is better, with a positive value indicating better performance.\n\n"
        "Sharpe Ratio: Measures the risk-adjusted return of the stock. \n"
        "  - Optimal Value: Higher values are better. A Sharpe Ratio >1 is considered good.\n\n"
        "Sortino Ratio: Similar to Sharpe Ratio but only considers downside volatility. \n"
        "  - Optimal Value: Higher values are better. A Sortino Ratio >1 is considered good.\n\n"
        "Calmar Ratio: Measures the risk-adjusted return considering maximum drawdown. \n"
        "  - Optimal Value: Higher values are better. A Calmar Ratio >1 is considered good."
    )
    messagebox.showinfo("Metric Hints", hints)


# Dropdown for period selection
period_var7 = tk.StringVar(value="5y")
period_label = tk.Label(tab_quant, text="Select Period:")
period_label.pack()
period_dropdown = tk.OptionMenu(tab_quant, period_var7, "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
period_dropdown.pack(pady=5)

# Dropdown for interval selection
interval_var7 = tk.StringVar(value="1d")
interval_label = tk.Label(tab_quant, text="Select Interval:")
interval_label.pack()
interval_dropdown = tk.OptionMenu(tab_quant, interval_var7, "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
interval_dropdown.pack(pady=5)

# Dropdown for sorting
sort_by_var = tk.StringVar(value="sharpe_ratio")
sort_by_label = tk.Label(tab_quant, text="Sort By:")
sort_by_label.pack()
sort_by_dropdown = tk.OptionMenu(tab_quant, sort_by_var, "beta", "alpha", "sharpe_ratio", "sortino_ratio", "calmar_ratio")
sort_by_dropdown.pack(pady=5)

# Button to load tickers from CSV
load_button = tk.Button(tab_quant, text="Load CSV", command=load_csv)
load_button.pack(pady=10)

# Button to calculate and display metrics
calculate_button = tk.Button(tab_quant, text="Calculate & Display Metrics", command=calculate_and_display_metrics)
calculate_button.pack(pady=10)

# Button to save the displayed tickers to CSV
save_button = tk.Button(tab_quant, text="Save CSV", command=save_csv)
save_button.pack(pady=10)

# Button to show hints about metrics
hints_button = tk.Button(tab_quant, text="Show Metric Hints", command=show_hints)
hints_button.pack(pady=10)

# Listbox to display tickers
ticker_listbox = tk.Listbox(tab_quant, width=80, height=20)
ticker_listbox.pack(pady=20)







#Code for Market Report

canvas = tk.Canvas(tab_market_view1)
scroll_y = tk.Scrollbar(tab_market_view1, orient="vertical", command=canvas.yview)
scroll_x = tk.Scrollbar(tab_market_view1, orient="horizontal", command=canvas.xview)
tab_market_view = ttk.Frame(canvas)

canvas.create_window((0, 0), window=tab_market_view, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
canvas.pack(side="left", fill="both", expand=True)


def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

tab_market_view.bind("<Configure>", on_frame_configure)
stop_thread=False
def auto():
    #print("Function is running!")

    # Schedule the function to run again after 4 minutes (240 seconds)
    
    while not stop_thread:
        messagebox.Message("Refreshing....")
        load_folder_auto()
        time.sleep(240)
        print("Auto On")
        
        
    print ("Stopped  ....")

def load_folder_auto():
    global folder_path, file_results
    #folder_path = filedialog.askdirectory()
    if folder_path:
        status_label.config(text=f"Loaded folder: {folder_path}")
        file_results = analyze_all_files()
       # print(file_results)
        update_file_dropdown()
        display_summary()
        play_sound()

def play_sound():
    # Initialize pygame mixer
    pygame.mixer.init()

    # Load and play the sound
    pygame.mixer.music.load("E:\Github\python\dist\Bell2.wav")
    pygame.mixer.music.play()

    # Wait until the sound finishes playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def load_folder():
    global folder_path, file_results
    folder_path = filedialog.askdirectory()
    if folder_path:
        status_label.config(text=f"Loaded folder: {folder_path}")
        file_results = analyze_all_files()
       # print(file_results)
        update_file_dropdown()
        display_summary()
        play_sound()



import numpy as np

def analyze_all_files():
   
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder first.")
        return
    
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not csv_files:
        messagebox.showerror("Error", "No CSV files found in the selected folder.")
        return
    
    period = period_var11.get()
    interval = interval_var11.get()
    
    all_results = {}
    matching_tickers = []
    base_ticker = '^NSEI'  # Nifty 50 index symbol
    length = 52
    lengthRSMA = 50
    lengthPriceSMA = 50

    # Fetch data for the base ticker
    base_data = yf.download(base_ticker, period=period, interval=interval)
    
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        tickers = pd.read_csv(file_path, header=None)[0].tolist()
        tickers = [ticker + '.NS' for ticker in tickers]
        choice=int(ema_var.get())
        print(choice)
        overbought = []
        oversold = []
        gaining_strength = []
        losing_strength = []
        RS = []
        Sq = []
        top_gainers = []
        buy = []
        bollinger_up=[]
        
        listbox_data = {
            "Overbought": [],
            "Oversold": [],
            "Gaining Strength": [],
            "Losing Strength": [],
            "RS": [],
            "Sq": [],
            "Top Gainers": [],
            "Buy": [],
            "Bollinger Up":[]
        }
        
        for ticker in tickers:
            try:
                data = yf.download(ticker, period=period, interval=interval)
                data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
                data['bb_middle_band'] = data['Close'].rolling(window=20).mean()
                data['bb_std_dev'] = data['Close'].rolling(window=20).std()
                data['bb_upper_band'] = data['bb_middle_band'] + (data['bb_std_dev'] * 2)
                data['bb_lower_band'] = data['bb_middle_band'] - (data['bb_std_dev'] * 2)
                data['atr'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'], window=20)
                data['kc_middle_band'] = data['Close'].rolling(window=20).mean()
                data['kc_upper_band'] = data['kc_middle_band'] + (data['atr'] * 1.5)
                data['kc_lower_band'] = data['kc_middle_band'] - (data['atr'] * 1.5)
                data['bb_inside_kc'] = (data['bb_upper_band'] < data['kc_upper_band']) & (data['bb_lower_band'] > data['kc_lower_band'])

                # Calculate 50 EMA
                data['50_EMA'] = data['Close'].ewm(span=choice, adjust=False).mean()

                if len(data) < 3:
                    continue
                
                # Calculate RSI-related categories
                current_rsi = data['RSI'].iloc[-1]
                previous_rsi = data['RSI'].iloc[-2]
                two_days_ago_rsi = data['RSI'].iloc[-3]
                days3_ago_rsi_ago_rsi = data['RSI'].iloc[-4]
                days4_ago_rsi_ago_rsi = data['RSI'].iloc[-5]
                days5_ago_rsi = data['RSI'].iloc[-6]
                
                latest_price = data['Close'].iloc[-1]
                
                if data['bb_inside_kc'].iloc[-2]:
                    if (data['bb_upper_band'].iloc[-1] > data['kc_upper_band'].iloc[-1]):
                        Sq.append((ticker, current_rsi))
                        listbox_data["Sq"].append((ticker, current_rsi))
                    
                if current_rsi > 70:
                    overbought.append((ticker, current_rsi))
                    listbox_data["Overbought"].append((ticker, current_rsi))
                    
                if  latest_price > data['bb_upper_band'].iloc[-1] :
                    bollinger_up.append((ticker, current_rsi))
                    listbox_data["Bollinger Up"].append((ticker, current_rsi))    
                    
                if current_rsi < 30:
                    oversold.append((ticker, current_rsi))
                    listbox_data["Oversold"].append((ticker, current_rsi))
                gaining = True
                for i in range(1, gaining_days.get()):
                    if data['RSI'].iloc[-i] <= data['RSI'].iloc[-(i + 1)]:
                        gaining = False
                        break
                
                if gaining:
                    gaining_strength.append((ticker, data['RSI'].iloc[-1]))
                    listbox_data["Gaining Strength"].append((ticker, data['RSI'].iloc[-1]))
                    
                loosing = True
               
                # if current_rsi > previous_rsi and previous_rsi > two_days_ago_rsi and (gaining_days.get()==2):
                #     gaining_strength.append((ticker, current_rsi))
                #     listbox_data["Gaining Strength"].append((ticker, current_rsi))
                    
                # if current_rsi < previous_rsi and previous_rsi < two_days_ago_rsi and gaining_days.get()==2:
                #     losing_strength.append((ticker, current_rsi))
                #     listbox_data["Losing Strength"].append((ticker, current_rsi))
                for i in range(1, gaining_days.get()):
                    if data['RSI'].iloc[-i] >= data['RSI'].iloc[-(i + 1)]:
                        loosing = False
                        break
                
                if loosing:
                    losing_strength.append((ticker, current_rsi))
                    listbox_data["Losing Strength"].append((ticker, current_rsi))
                
                
                #print("gain_days:",gaining_days.get())
                # Calculate Relative Strength
                rs_data = pd.concat([base_data['Close'], data['Close']], axis=1)
                rs_data.columns = ['Base', 'Comparative']
                rs_data = rs_data.dropna()
                rs_data['RS'] = (rs_data['Comparative'] / rs_data['Comparative'].shift(length)) / (rs_data['Base'] / rs_data['Base'].shift(length)) - 1
                current_rs = rs_data['RS'].iloc[-1]
                if current_rs > 0:
                    RS.append((ticker, current_rs))
                    listbox_data["RS"].append((ticker, current_rs))
                
                # Calculate percentage price gain
                initial_price = data['Close'].iloc[-2]
                
                price_gain = ((latest_price - initial_price) / initial_price) * 100
                if price_gain > 0 :
                    top_gainers.append((ticker, price_gain))
                    listbox_data["Top Gainers"].append((ticker, price_gain))
                
                # Check if ticker is in RS and its price is above the 50 EMA and within 0.5% of the 50 EMA
                if any(ticker == rs_ticker[0] for rs_ticker in RS):
                    price_above_ema = latest_price > data['50_EMA'].iloc[-1] and data['50_EMA'].iloc[-1] > data['50_EMA'].iloc[-2]
                    near_ema = np.abs((latest_price - data['50_EMA'].iloc[-1]) / data['50_EMA'].iloc[-1]) <= 0.03
                    
                    if price_above_ema and near_ema:
                        buy.append((ticker, latest_price))
                        listbox_data["Buy"].append((ticker, current_rs))
            
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
        
        # Sort data in descending order of RSI, RS, and Top Gainers
        for category in listbox_data:
            listbox_data[category].sort(key=lambda x: x[1], reverse=True)
        
        total_tickers = len(tickers)
        summary = (
            f"File: {csv_file}\n"
            f"Overbought: {len(overbought)} ({len(overbought)/total_tickers*100:.2f}%)\n"
            f"Oversold: {len(oversold)} ({len(oversold)/total_tickers*100:.2f}%)\n"
            f"Gaining Strength: {len(gaining_strength)} ({len(gaining_strength)/total_tickers*100:.2f}%)\n"
            f"Losing Strength: {len(losing_strength)} ({len(losing_strength)/total_tickers*100:.2f}%)\n"
            f"Relative Strength: {len(RS)} ({len(RS)/total_tickers*100:.2f}%)\n"
            f"Squeeze: {len(Sq)} ({len(Sq)/total_tickers*100:.2f}%)\n"
            f"Top Gainers: {len(top_gainers)} ({len(top_gainers)/total_tickers*100:.2f}%)\n"
            f"Buy: {len(buy)} ({len(buy)/total_tickers*100:.2f}%)\n"
            f"Bollinger_up: {len(bollinger_up)} ({len(bollinger_up)/total_tickers*100:.2f}%)\n"
            f"{'-'*50}\n"
        )
        
        all_results[csv_file] = {
            "summary": summary,
            "data": listbox_data
        }
    
    return all_results


def update_file_dropdown2():
    

    
    csv_files = list(file_results.keys())
    print(file_results.keys())
    if not csv_files:
        messagebox.showerror("Error", "No CSV files found.")
        return
    
    file_dropdown_menu['menu'].delete(0, 'end')
    for csv_file in csv_files:
        file_dropdown_menu['menu'].add_command(label=csv_file, command=tk._setit(selected_file_var, csv_file))
    
    selected_file_var.set(csv_files[0] if csv_files else "")
    
def update_file_dropdown():
    if not folder_path:
        return
    
    csv_files = list(file_results.keys())
    if not csv_files:
        messagebox.showerror("Error", "No CSV files found.")
        return
    
    file_dropdown_menu['menu'].delete(0, 'end')
    for csv_file in csv_files:
        file_dropdown_menu['menu'].add_command(label=csv_file, command=tk._setit(selected_file_var, csv_file))
    
    selected_file_var.set(csv_files[0] if csv_files else "")

def display_summary():
    summary_text.delete(1.0, tk.END)
    
    # Configure tags for formatting
    summary_text.tag_configure("heading", font=('Helvetica', 12, 'bold'), foreground='blue')
    summary_text.tag_configure("file_name", font=('Helvetica', 10, 'bold'), foreground='dark green')
    summary_text.tag_configure("percentage", font=('Helvetica', 10, 'bold'), foreground='dark orange')
    summary_text.tag_configure("regular", font=('Helvetica', 10))
    
    summary_text.insert(tk.END, "===== Summary Report =====\n\n", "heading")
    
    for file_name, result in file_results.items():
        summary_text.insert(tk.END, f"File: {file_name}\n", "file_name")
        summary_text.insert(tk.END, "-" * 50 + "\n", "regular")
        summary_text.insert(tk.END, f"Overbought: {len(result['data']['Overbought'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Overbought: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Oversold: {len(result['data']['Oversold'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Oversold: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Gaining Strength: {len(result['data']['Gaining Strength'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Gaining Strength: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Losing Strength: {len(result['data']['Losing Strength'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Losing Strength: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Relative Strength: {len(result['data']['RS'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Relative Strength: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Squeeze: {len(result['data']['Sq'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Squeeze: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Top Gainers: {len(result['data']['Top Gainers'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Top Gainers: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Buy: {len(result['data']['Buy'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Buy: ')[1].split(' (')[1].split('%)')[0]}%)\n\n", "percentage")
        summary_text.insert(tk.END, f"Bollinger Up: {len(result['data']['Bollinger Up'])}\n\n ", "regular")
        #summary_text.insert(tk.END, f"({result['summary'].split('Bollinger Up: ')[1].split(' (')[1].split('%)')[0]}%)\n\n", "percentage")
    summary_text.insert(tk.END, "=" * 50 + "\n", "regular")



def update_criteria(*args):
    file_name = selected_file_var.get()
    if not file_name or file_name not in file_results:
        return
    
    listbox_data = file_results[file_name]["data"]
    
    # Insert data into listboxes
    for category in listbox_widgets:
        listbox11 = listbox_widgets[category]
        listbox11.delete(0, tk.END)
        for ticker, rsi in listbox_data.get(category, []):
            listbox11.insert(tk.END, f"{ticker}: RSI={rsi:.2f}")

def save_report():
    if not file_results:
        messagebox.showerror("Error", "No data to save.")
        return
    
    save_folder = filedialog.askdirectory()
    if not save_folder:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(save_folder, f"RSI_Report_{timestamp}.json")
    
    with open(report_path, 'w') as f:
        json.dump(file_results, f, indent=4)
    
    messagebox.showinfo("Saved", f"Report saved to {report_path}")

def load_report():
    global file_results
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return
    
    try :
        with open(file_path, 'r') as f:
            file_results = json.load(f)
            
    except Exception as e:
    # Code that runs for any other exception
        print(f"An error occurred: {e}")    
    
    
    update_file_dropdown2()
    display_summary()


differences = {}

def display_comparison(file1, file2):
    compare_text.delete(1.0, tk.END)
    
    with open(file1, 'r') as f:
        report1 = json.load(f)
    
    with open(file2, 'r') as f:
        report2 = json.load(f)
    
    global differences
    
    all_files = set(report1.keys()).union(report2.keys())
    
    for file_name in all_files:
        diff = {}
        data1 = report1.get(file_name, {}).get('data', {})
        data2 = report2.get(file_name, {}).get('data', {})
        
        for category in ["Overbought", "Oversold", "Gaining Strength", "Losing Strength", "RS", "Sq", "Top Gainers"]:
            tickers1 = set(ticker for ticker, _ in data1.get(category, []))
            tickers2 = set(ticker for ticker, _ in data2.get(category, []))
            
            diff[category] = {
                "Added": list(tickers2 - tickers1),
                "Removed": list(tickers1 - tickers2)
            }
        
        if diff:
            differences[file_name] = diff
    
    compare_text.insert(tk.END, "===== Comparison Report =====\n\n", "header")
    
    for file_name, diff in differences.items():
        compare_text.insert(tk.END, f"File: {file_name}\n", "file_name")
        compare_text.insert(tk.END, "-" * 50 + "\n", "separator")
        file_selector['values'] = (*file_selector['values'], file_name)
        
        
        for category, changes in diff.items():
            compare_text.insert(tk.END, f"**{category}:**\n", "bold_heading")
            if changes["Added"]:
                compare_text.insert(tk.END, "  \u2022 **Added:**\n", "sub_heading")
                for ticker in changes["Added"]:
                    compare_text.insert(tk.END, f"    \u2022 {ticker}\n", "regular")
            if changes["Removed"]:
                compare_text.insert(tk.END, "  \u2022 **Removed:**\n", "sub_heading")
                for ticker in changes["Removed"]:
                    compare_text.insert(tk.END, f"    \u2022 {ticker}\n", "regular")
            compare_text.insert(tk.END, "\n", "spacing")
        
        compare_text.insert(tk.END, "-" * 50 + "\n", "separator")
    
    compare_text.insert(tk.END, "=" * 50 + "\n", "end_separator")

# Tag configuration for better visualization (example)
    compare_text.tag_configure("header", font=("Helvetica", 14, "bold"))
    compare_text.tag_configure("file_name", font=("Helvetica", 12, "bold italic"))
    compare_text.tag_configure("bold_heading", font=("Helvetica", 12, "bold"), foreground="blue")
    compare_text.tag_configure("sub_heading", font=("Helvetica", 10, "bold"), foreground="green")
    compare_text.tag_configure("regular", font=("Helvetica", 10), foreground="black")
    compare_text.tag_configure("separator", font=("Helvetica", 10), foreground="grey")
    compare_text.tag_configure("spacing", font=("Helvetica", 5))
    compare_text.tag_configure("end_separator", font=("Helvetica", 10, "bold"), foreground="grey")


def compare_reports():
    file1_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Select OLD report")
    file2_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Select NEW report")
    
    if not file1_path or not file2_path:
        return
    
    display_comparison(file1_path, file2_path)
    





folder_path = None
file_results = {}


#Settings Display

settings_frame=ttk.Frame(tab_market_view)
settings_frame.grid(row=7,column=0,pady=1)




# Compare Report Display
compare_frame = tk.Frame(tab_market_view)
compare_frame.grid(row=8, column=0,pady=1)

compare_text = tk.Text(compare_frame, wrap=tk.WORD, height=15, width=100)
compare_text.grid(row=0, column=0,  pady=1)

# Folder selection
file_label = tk.Label(settings_frame, text="Select Folder with CSV files:")
file_label.grid(row=0, column=0,  pady=1)

file_button = tk.Button(settings_frame, text="Browse", command=load_folder)
file_button.grid(row=0, column=2, pady=1)

file_button2 = tk.Button(settings_frame, text="Browse single file", command=load_folder)
file_button2.grid(row=0, column=3, pady=1)

status_label = tk.Label(settings_frame, text="EMA")
status_label.grid(row=0, column=4, pady=1)

ema_var = tk.StringVar()
ema_entry = tk.Entry(settings_frame, textvariable=ema_var)
ema_entry.grid(row=0, column=5, pady=1)  # Adjust the placement according to your layout
ema_var.set("20")  # Set a default value, e.g., 50


# Save, Load, Compare buttons
save_button = tk.Button(settings_frame, text="Save Report", command=save_report)
save_button.grid(row=0, column=14, padx=1, pady=5)

load_button = tk.Button(settings_frame, text="Load Report", command=load_report)
load_button.grid(row=0, column=13, padx=1, pady=5)

compare_button = tk.Button(settings_frame, text="Compare Reports", command=compare_reports)
compare_button.grid(row=0, column=12, padx=1, pady=5)

def start_thread():
    global stop_thread
    stop_thread=False
    background_thread.start()
def stop_thread2():
    global stop_thread 
    stop_thread=True
    print(f"Flag value:{stop_thread}")

background_thread = threading.Thread(target=auto, daemon=True)

compare_button = tk.Button(settings_frame, text="Auto_on", command=start_thread)
compare_button.grid(row=0, column=15, padx=1, pady=5)

compare_button = tk.Button(settings_frame, text="Auto_stop", command=stop_thread2)
compare_button.grid(row=0, column=16, padx=1, pady=5)

gaining_day_label=tk.Label(settings_frame,text="Gain days:")
gaining_day_label.grid(row=0, column=17, padx=1, pady=5)
gaining_days=tk.IntVar(settings_frame)
gaining_days.set(2)

gain_days_menu=tk.OptionMenu(settings_frame, gaining_days, 1,2,3,4,5,6,7,8,9,10)
gain_days_menu.grid(row=0, column=18, padx=1, pady=1)

# File dropdown
selected_file_var = tk.StringVar(settings_frame)
selected_file_var.set("Select a file")
file_dropdown_label = tk.Label(settings_frame, text="Select CSV file:")
file_dropdown_label.grid(row=0, column=6, pady=1)

file_dropdown_menu = tk.OptionMenu(settings_frame, selected_file_var, [])
file_dropdown_menu.grid(row=0, column=7, pady=1)
selected_file_var.trace("w", update_criteria)  # Update criteria when selection changes

# Period dropdown
period_var11 = tk.StringVar(settings_frame)
period_var11.set("1y")  # default value
period_label = tk.Label(settings_frame, text="Select Period:")
period_label.grid(row=0, column=8, pady=1)

period_menu = tk.OptionMenu(settings_frame, period_var11, "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
period_menu.grid(row=0, column=9, pady=1)

# Interval dropdown
interval_var11 = tk.StringVar(settings_frame)
interval_var11.set("1d")  # default value
interval_label = tk.Label(settings_frame, text="Select Interval:")
interval_label.grid(row=0, column=10, pady=1)

interval_menu = tk.OptionMenu(settings_frame, interval_var11, "1m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo")
interval_menu.grid(row=0, column=11, pady=1)

# Summary Text
summary_text = tk.Text(compare_frame, wrap=tk.WORD, height=15, width=100)
summary_text.grid(row=0, column=1,  pady=1)

#trade Text
#trad_text = tk.Text(compare_frame, wrap=tk.WORD, height=15, width=100)
#trad_text.grid(row=0, column=2,  pady=1)

# Listboxes for criteria
criteria_frame = tk.Frame(tab_market_view)
criteria_frame.grid(row=6, column=0, columnspan=3, pady=10)

chart_frame = tk.Frame(tab_market_view)
chart_frame.grid(row=0, column=0, pady=1, sticky='nsew')



text_trade = tk.Text(tab_market_view, wrap='word', width=50, height=30,)  # Set a fixed width for the Listbox
text_trade.grid(row=0, column=1, pady=1, sticky='nsw')
text_font = font.Font(family="Helvetica", size=10)
header_font = font.Font(family="Helvetica", size=12, weight="bold")

text_trade.tag_configure('header', font=header_font, foreground='#2c3e50')
text_trade.tag_configure('details', font=header_font, foreground='#2c3e50')


def update_display(differences, selected_file):
    compare_text.delete(1.0, tk.END)
    
    if selected_file not in differences:
        compare_text.insert(tk.END, "No differences found for the selected file.\n", "regular")
        return
    
    diff = differences[selected_file]
    
    compare_text.insert(tk.END, f"File: {selected_file}\n", "file_name")
    compare_text.insert(tk.END, "-" * 50 + "\n", "separator")
    
    
    for category, changes in diff.items():
        compare_text.insert(tk.END, f"**{category}:**\n", "bold_heading")
        if changes["Added"] and category != "Sq":
            compare_text.insert(tk.END, "  \u2022 **Added:**\n", "sub_heading")
            for ticker in changes["Added"]:
                compare_text.insert(tk.END, f"    \u2022 {ticker}\n", ticker)
                compare_text.tag_bind(ticker, "<Button-1>", lambda event, tick=ticker: plot_chart2(tick))
        
        if changes["Removed"] and category == "Sq":
            compare_text.insert(tk.END, "  \u2022 **Removed:**\n", "sub_heading")
            for ticker in changes["Removed"]:
                compare_text.insert(tk.END, f"    \u2022 {ticker}\n", ticker)
                compare_text.tag_bind(ticker, "<Button-1>", lambda event, tick=ticker: plot_chart2(tick))
        
        compare_text.insert(tk.END, "\n", "spacing")
    
    compare_text.insert(tk.END, "-" * 50 + "\n", "separator")
    # saving the report in json 
    save_to_json(diff)


    
def save_to_json(differences):
    save_location = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if save_location:
        with open(save_location, 'w') as f:
            json.dump(differences, f, indent=4)
        print(f"File saved successfully at {save_location}")
                
                
def on_file_select(event):
    selected_file = file_selector.get()
    update_display(differences, selected_file)
    return

file_selector = ttk.Combobox(compare_frame)
file_selector.grid(row=1, column=0, pady=1)
file_selector.bind("<<ComboboxSelected>>", on_file_select)





def save_listbox_content(category):
    # Get the listbox associated with the category
    listbox = listbox_widgets[category]
    # Get all items from the listbox
    content = listbox.get(0, tk.END)
    
    if not content:
        tk.messagebox.showinfo("Info", f"No items to save in '{category}' listbox.")
        return
    
    # Ask for the file location to save the content
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    
    if file_path:
        # Save the content to a file
        with open(file_path, 'w') as file:
            for item in content:
                # Extract the part before '.NS'
                ticker = item.split('.NS')[0]
                file.write(ticker + '\n')
        tk.messagebox.showinfo("Success", f"Content saved successfully to '{file_path}'.")


file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save List", command=save_list1)
file_menu.add_command(label="Open List", command=open_list)
file_menu.add_command(label="Load Tickers", command=load_tickers)
file_menu.add_command(label="Save Report", command=save_report)
file_menu.add_command(label="Load Report", command=load_report)

def plot_chart2(tick):
  
    selected_ticker = tick
    
    df = yf.download(selected_ticker, period=period_var11.get(), interval=interval_var11.get())
    
    if df.empty:
        messagebox.showerror("Data Error", "No data available for the selected ticker.")
        return

    # Calculate EMAs
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA100'] = df['Close'].ewm(span=100, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # Calculate RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # Calculate Bollinger Bands
    df['bb_middle_band'] = df['Close'].rolling(window=20).mean()
    df['bb_std_dev'] = df['Close'].rolling(window=20).std()
    df['bb_upper_band'] = df['bb_middle_band'] + (df['bb_std_dev'] * 2)
    df['bb_lower_band'] = df['bb_middle_band'] - (df['bb_std_dev'] * 2)

    # Clear the previous plot
    for widget in chart_frame.winfo_children():
        widget.destroy()

    # Create a new plot
    fig, (ax_price, ax_volume, ax_rsi) = plt.subplots(figsize=(3,6), nrows=3, ncols=1, sharex=True, 
                                                      gridspec_kw={'height_ratios': [3, 1, 1]})
    plt.tight_layout()

    # Enable zoom and pan
    def on_zoom(event):
        scale_factor = 1.1 if event.button == 'up' else 0.9
        ax_price.set_xlim(ax_price.get_xlim()[0] * scale_factor, ax_price.get_xlim()[1] * scale_factor)
        ax_volume.set_xlim(ax_volume.get_xlim()[0] * scale_factor, ax_volume.get_xlim()[1] * scale_factor)
        ax_rsi.set_xlim(ax_rsi.get_xlim()[0] * scale_factor, ax_rsi.get_xlim()[1] * scale_factor)
        fig.canvas.draw()

    fig.canvas.mpl_connect('scroll_event', on_zoom)

    def on_pan(event):
        if event.button == 1:
            pan_amount = (ax_price.get_xlim()[1] - ax_price.get_xlim()[0]) * 0.05
            ax_price.set_xlim(ax_price.get_xlim()[0] + pan_amount, ax_price.get_xlim()[1] + pan_amount)
            ax_volume.set_xlim(ax_volume.get_xlim()[0] + pan_amount, ax_volume.get_xlim()[1] + pan_amount)
            ax_rsi.set_xlim(ax_rsi.get_xlim()[0] + pan_amount, ax_rsi.get_xlim()[1] + pan_amount)
            fig.canvas.draw()

    fig.canvas.mpl_connect('button_press_event', on_pan)

    ax_price.xaxis_date()
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    ax_price.set_title(f"{selected_ticker} {chart_type.capitalize()} Chart")
    ax_price.set_ylabel('Price')
    ax_price.grid(True)
    current_price = df['Close'].iloc[-1]

    if chart_type == "candlestick":
        df['Date'] = mdates.date2num(df.index.to_pydatetime())
        ohlc = df[['Date', 'Open', 'High', 'Low', 'Close']].copy()

        # Plot the candlestick chart
        candlestick_ohlc(ax_price, ohlc.values, width=0.6, colorup='g', colordown='r', alpha=0.8)
        ax_price.plot([], [], ' ', label=f'Close Price (Current: {current_price:.2f})')

    elif chart_type == "line":
        ax_price.plot(df.index, df['Close'], label=f'Close Price (Current: {current_price:.2f})', color='blue')

    # Plot EMAs
    ax_price.plot(df.index, df['EMA20'], label=f"20-day EMA {df['EMA20'].iloc[-1]:.2f}", color='orange')
    ax_price.plot(df.index, df['EMA50'], label=f"'50-day EMA {df['EMA50'].iloc[-1]:.2f}", color='purple')
    ax_price.plot(df.index, df['EMA100'], label=f"100-day EMA {df['EMA100'].iloc[-1]:.2f}", color='red')
    ax_price.plot(df.index, df['EMA200'], label=f"200-day EMA {df['EMA200'].iloc[-1]:.2f}", color='blue')

    # Plot Bollinger Bands
    ax_price.plot(df.index, df['bb_middle_band'], label='Middle Band (20-day SMA)', color='black')
    ax_price.plot(df.index, df['bb_upper_band'], label=f"Upper Band- {df['bb_upper_band'].iloc[-1]:.2f}", color='gray', linestyle='--')
    ax_price.plot(df.index, df['bb_lower_band'], label=f"Lower Band {df['bb_lower_band'].iloc[-1]:.2f}", color='gray', linestyle='--')

    ax_price.legend()

    # Plot Volume
    ax_volume.bar(df.index, df['Volume'], color='gray')
    ax_volume.set_ylabel('Volume')

    # Plot RSI
    ax_rsi.plot(df.index, df['RSI'], label='14-day RSI', color='green')
    ax_rsi.axhline(70, color='red', linestyle='--', label='Overbought')
    ax_rsi.axhline(30, color='blue', linestyle='--', label='Oversold')

    # Mark the current RSI value
    current_rsi = df['RSI'].iloc[-1]
    ax_rsi.axhline(current_rsi, color='purple', linestyle='-', label=f'Current RSI: {current_rsi:.2f}')
    ax_rsi.text(df.index[-1], current_rsi, f'{current_rsi:.2f}', color='purple', fontsize=10, ha='left', va='center')

    ax_rsi.set_ylabel('RSI')
    ax_rsi.set_xlabel('Date')
    ax_rsi.legend()
    
    previous_close = df['Close'].iloc[-2]  # Previous candle close
    current_close = df['Close'].iloc[-1]   # Today's closing price
    investment_amt = 10000  # Investment amount
    
    # Risk (entry price - stoploss price)
    risk = current_close - previous_close
    
    # Calculate the quantity that can be bought with the given investment amount
    quantity = investment_amt // current_close  # Integer division for whole shares
    
    # Calculate risk amount (total risk in terms of money)
    risk_amount = risk * quantity
    
    target = current_close + (2 * risk)

# Risk-to-reward ratio is 1:2, so the target price is:
    text_trade.config(state=tk.NORMAL)
    text_trade.delete(1.0, tk.END)  # Clears the content
    
    # Insert trade details into the Text widget with formatted numbers (2 decimal places)
    text_trade.insert(tk.END, "Trade Details:\n\n", 'header')
    text_trade.insert(tk.END, f"Trade Type: {'Buy' if risk > 0 else 'Short'}\n", 'header')
    text_trade.insert(tk.END, f"\nStoploss: Prev candle close - {previous_close:.2f}\n", 'details')
    text_trade.insert(tk.END, f"Entry: Today's closing - {current_close:.2f}\n", 'details')
    text_trade.insert(tk.END, f"Risk per share: {risk:.2f}\n", 'details')
    text_trade.insert(tk.END, f"Quantity (for 10,000): {quantity} shares\n", 'details')
    text_trade.insert(tk.END, f"Total Risk Amount: {risk_amount:.2f}\n", 'details')
    text_trade.insert(tk.END, f"Target Price (1:2 risk/reward): {target:.2f}\n", 'details')
  

# Disable editing in the Text widget
    text_trade.config(state=tk.DISABLED)
    # Embed the plot in the Tkinter GUI
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    



categories = ["Overbought", "Oversold", "Gaining Strength", "Losing Strength","RS","Sq","Top Gainers","Buy","Bollinger Up"]
listbox_widgets = {}



# Add labels and listboxes for each category
for idx, category in enumerate(categories):
    label = tk.Label(criteria_frame, text=category, font=('Helvetica', 10, 'bold'))
    label.grid(row=0, column=idx, padx=10, pady=5)
    listbox11 = tk.Listbox(criteria_frame, width=30, height=10)
    listbox11.grid(row=1, column=idx, padx=10, pady=5)
    listbox_widgets[category] = listbox11
    
    # Bind label click event to save the content of the corresponding listbox
    label.bind("<Button-1>", lambda e, cat=category: save_listbox_content(cat))


for category in categories:
    listbox_widgets[category].bind("<Button-1>", lambda e, cat=category: plot_chart2(listbox_widgets[cat].get(listbox_widgets[cat].curselection()).split(':')[0]))


def populate_listboxes(data, listbox_widgets):
    for category, changes in data.items():
        listbox = listbox_widgets.get(category)
        if listbox:
            # Clear the listbox before adding new data
            listbox.delete(0, tk.END)
            if category == "Sq":
                # Only list "Removed" items for the "Sq" category
                for item in changes["Removed"]:
                    listbox.insert(tk.END, f"{item}")
            else:
                # Only list "Added" items for all other categories
                for item in changes["Added"]:
                    listbox.insert(tk.END, f"{item}")

# Function to open JSON file and load data
def load_json_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as file:
            data = json.load(file)
            populate_listboxes(data, listbox_widgets)
            
save_button = tk.Button(compare_frame, text="Load JSON Data", command=load_json_file)            
save_button.grid(row=1, column=2, pady=1)



# Start the Tkinter event loop
root.mainloop()
