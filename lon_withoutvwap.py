# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:33:18 2025

@author: Mahadev
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 16:14:20 2025

@author: Mahadev
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
import json
import threading
import time
import os
from datetime import datetime



# Global variables
trades = {}
win=0
losst=0
monitored_tickers = []
csv_file_path = ""  # Path to the CSV file
def calculate_supertrend(data, period=10, multiplier=1.5):
    # Calculate ATR
    data['H-L'] = data['High'] - data['Low']
    data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
    data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=period).mean()

    # Calculate Basic Upper Band (BUB) and Basic Lower Band (BLB)
    data['BUB'] = (data['High'] + data['Low']) / 2 + multiplier * data['ATR']
    data['BLB'] = (data['High'] + data['Low']) / 2 - multiplier * data['ATR']

    # Initialize Final Upper Band (FUB) and Final Lower Band (FLB)
    data['FUB'] = 0.0
    data['FLB'] = 0.0
    data['Supertrend'] = 0.0

    for i in range(period, len(data)):
        # Final Upper Band
        if data['Close'].iloc[i-1] <= data['FUB'].iloc[i-1]:
            data.at[data.index[i], 'FUB'] = min(data['BUB'].iloc[i], data['FUB'].iloc[i-1])
        else:
            data.at[data.index[i], 'FUB'] = data['BUB'].iloc[i]

        # Final Lower Band
        if data['Close'].iloc[i-1] >= data['FLB'].iloc[i-1]:
            data.at[data.index[i], 'FLB'] = max(data['BLB'].iloc[i], data['FLB'].iloc[i-1])
        else:
            data.at[data.index[i], 'FLB'] = data['BLB'].iloc[i]

        # Supertrend Value
        if data['Close'].iloc[i] <= data['FUB'].iloc[i]:
            data.at[data.index[i], 'Supertrend'] = data['FUB'].iloc[i]
        else:
            data.at[data.index[i], 'Supertrend'] = data['FLB'].iloc[i]

    return data['Supertrend'].iloc[-1]


def add_ticker():
    ticker = ticker_entry.get().strip()  # Get the ticker from the entry field
    if ticker and ticker not in monitored_tickers:
        monitored_tickers.append(ticker)
        update_listboxes()  # Update listbox to reflect the added ticker
    ticker_entry.delete(0, tk.END)  # Clear the entry field


# Function to load tickers from CSV file
def load_tickers_from_csv():
    global monitored_tickers
    if os.path.exists(csv_file_path):
        try:
            tickers_df = pd.read_csv(csv_file_path, header=None)
            monitored_tickers = tickers_df[0].tolist()  # Extract the tickers column
            update_listboxes()
            print("Tickers loaded from CSV file.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")
    else:
        print("CSV file not found.")

# Function to browse and select CSV file
def browse_csv_file():
    global csv_file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_file_path = file_path
        print(f"CSV file path set to: {csv_file_path}")
        load_tickers_from_csv()  # Load the tickers after selecting the file
        update_listboxes()  # Update listbox with the loaded tickers

# Function to calculate stochastic oscillator
def stochastic(df, period=60, k_smooth=10):
    df['L'] = df['Low'].rolling(period).min()
    df['H'] = df['High'].rolling(period).max()
    df['%K'] = 100 * ((df['Close'] - df['L']) / (df['H'] - df['L']))
    df['%K'] = df['%K'].rolling(k_smooth).mean()
    return df
def fast_stochastic(data, k_period, d_period):
    """Calculate the Fast Stochastic Oscillator (%K and %D)."""
    lowest_low = data['Low'].rolling(window=k_period).min()
    highest_high = data['High'].rolling(window=k_period).max()
    k = ((data['Close'] - lowest_low) / (highest_high - lowest_low)) * 100
    d = k.rolling(window=d_period).mean()
    return d

# Function to calculate EMA
def ema(df, span):
    return df['Close'].ewm(span=span, adjust=False).mean()

# Function to monitor tickers
def monitor_tickers():
    while True:
        if csv_file_path:  # Check if a CSV file path is set
            load_tickers_from_csv()  # Reload tickers from CSV at every check
            for ticker in monitored_tickers.copy():
                print(f"Checking {ticker}...")
                check_trade_conditions(ticker)
            active_trades()
        time.sleep(15)  # Check every 30 seconds

# Function to manage active trades
def active_trades():
    global trades,win,losst
    global total_pl

    qty = 10

    for trade in trades:
        if trade['Status'] == "Active":
            ticker = trade['Ticker']
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if df.empty:
                return

            df = stochastic(df)
            df['EMA5'] = ema(df, 5)
            df['EMA15'] = ema(df, 15)

            last_row = df.iloc[-1]
            fast_stoch = last_row['%K']
            price = last_row['Close']
            ema5 = last_row['EMA5']
            ema15 = last_row['EMA15']
            fast40=fast_stochastic(df, 40, 4).iloc[-1]
            
            #atr=calculate_supertrend((df))
            #trade['Stop Loss']=min(trade['Stop Loss'], atr)



            exit_reason = None
            if price <= trade['Stop Loss']:
                trade['Status'] = "Stopped Out"
                losst=losst+1
                exit_reason = "Stop Loss"
            elif price >= trade['Target']:
                trade['Status'] = "Target Hit"
                win=win+1
                exit_reason = "Target"
                
            elif fast_stoch > 93:
                trade['Status'] = "Exit : Stoch > 93"
                win=win+1
                exit_reason = "Stoch > 93"
            elif fast40 < 80:
                trade['Status'] = "Exit : Stoch 40 < 80"
                win=win+1
                exit_reason = "Stoch > 93"


            if trade['Status'] != "Active":
                trade['Exit Price'] = round(price, 2)
                #trade['P&L'] = round((-trade['Entry'] + trade['Exit Price']) * trade['Qty'], 2)-trade['Chrg']
                trade['P&L'] = round((trade['Exit Price'] - trade['Entry']) * trade['Qty'] + trade['Chrg'], 2)

                total_pl += trade['P&L']  # Update Total P&L
                update_total_pl()
                update_listboxes()
                update_table()

# Function to check trade entry/exit conditions

    
def check_trade_conditions(ticker):
    global total_pl
    # Get current time
    now = datetime.now()
    

    # Extract hour and minute
    current_time = now.strftime("%H:%M")
    global trades
    try:
        df = yf.download(ticker, period="5d", interval="1m", progress=False)
        if df.empty:
            return

        df = stochastic(df)
        atr=calculate_supertrend((df))
        

        df['EMA5'] = ema(df, 50)
        df['EMA15'] = ema(df, 20)
        last_row = df.iloc[-1]
        fast_stoch = last_row['%K']
        price = last_row['Close']
        ema5 = last_row['EMA5']
        ema15 = last_row['EMA15']
        ndlast = df.iloc[-2]
        fast_stoch7 = fast_stochastic(df, 60, 3)
        fast_stoch2 = ndlast['%K']
        fast40=fast_stochastic(df, 40, 4).iloc[-1]
        trade_in = False  # Initialize before the loopvwap
        vwap=calculate_vwap(df)
        
        for trade in trades:
            if trade['Status'] == "Active" and ticker == trade['Ticker']:
                trade_in = True
                break  
        # Entry Condition
        if fast_stoch <=20 and fast_stoch7.iloc[-1]>fast_stoch7.iloc[-2]  and price > ema5 and price <ema15 and ema5 < ema15 and (not trade_in) and fast_stoch7.iloc[-1] >=85 and price > vwap :
            entry_price = price
            stop_loss = entry_price * (1 - 0.0013)  # -0.12%
            target = entry_price * (1 + 0.0031)     # +0.31%

            trade = {
                "Time": current_time,
                "Ticker": ticker,
                "Entry": round(entry_price, 2),
                "Stop Loss": round(stop_loss, 2),
                "Target": round(target, 2),
                "Exit Price": None,
                "P&L": 0,
                "Status": "Active",
                "Qty": 1000 if entry_price < 100 else 100 if entry_price < 4000 else 10,
                "Chrg": -50 if entry_price < 100 else -100 if entry_price < 4000 else -200,
                

            }
            trades.append(trade)
            monitored_tickers.remove(ticker)
            update_listboxes()
            update_table()

    except Exception as e:
        print(f"Error checking {ticker}: {e}")

# Update the listboxes
def update_listboxes():
    ticker_listbox.delete(0, tk.END)
    global trade_count 
    trade_count.set( "Trade Status Table:                Trade count: "+str(len(trades))+ "     W:"+str(win)+"    L:"+str(losst))
    for ticker in monitored_tickers:
        ticker_listbox.insert(tk.END, ticker)

    trade_listbox.delete(0, tk.END)
    for trade in trades:
        if(trade['Status'] == "Active"):
            trade_listbox.insert(tk.END, f"{trade['Ticker']} | Entry: {trade['Entry']} | Status: {trade['Status']}")

# Update the trade table
def update_table():
    for row in trade_table.get_children():
        trade_table.delete(row)
    for trade in trades[::-1]:
        trade_table.insert("", "end", values=(
            trade['Time'],
            trade['Ticker'], trade['Entry'], trade['Stop Loss'],
            trade['Target'], trade['Exit Price'], trade['P&L'], trade['Status']
        ))

# Update the total P&L display
def update_total_pl():
    total_pl_label.config(text=f"Total P&L: {round(total_pl, 2)}")

# Save trades to file
def save_trades():
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if filename:
        with open(filename, 'w') as f:
            json.dump(trades, f, indent=4)
        messagebox.showinfo("Saved", "Trade data saved successfully!")
# VWAP Calculation Function
def calculate_vwap(data):
    # Ensure data has 'Close', 'High', 'Low', and 'Volume' columns
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
    return vwap.iloc[-1]
# Load trades from file
def load_trades():
    filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if filename:
        global trades, total_pl
        with open(filename, 'r') as f:
            trades = json.load(f)
        total_pl = sum(trade.get('P&L', 0) for trade in trades)
        update_listboxes()
        update_table()
        update_total_pl()
        messagebox.showinfo("Loaded", "Trade data loaded successfully!")

# GUI setup
root = tk.Tk()
root.title("4knights-Long")
trade_count=tk.StringVar()


# Entry Frame
entry_frame = tk.Frame(root)
entry_frame.pack(pady=10)
tk.Label(entry_frame, text="Enter Ticker:").grid(row=0, column=0, padx=5, pady=5)
ticker_entry = tk.Entry(entry_frame)
ticker_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(entry_frame, text="Add Ticker", command=add_ticker).grid(row=0, column=2, padx=5, pady=5)

# Load CSV Button
load_csv_button = tk.Button(root, text="Load CSV", command=browse_csv_file)
load_csv_button.pack(pady=10)

# Ticker Monitoring Listbox
tk.Label(root, text="Monitored Tickers:").pack()
ticker_listbox = tk.Listbox(root, width=40, height=5)
ticker_listbox.pack(pady=5)

# Active Trades Listbox
tk.Label(root, text="Active Trades:").pack()
trade_listbox = tk.Listbox(root, width=60, height=5)
trade_listbox.pack(pady=5)

# Trade Table
tk.Label(root, textvariable=trade_count ).pack()
columns = ("Time","Ticker", "Entry", "Stop Loss", "Target", "Exit Price", "P&L", "Status")
trade_table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    trade_table.heading(col, text=col)
    trade_table.column(col, width=100)
trade_table.pack(pady=5)

# Total P&L Display
total_pl_label = tk.Label(root, text="Total P&L: 0", font=("Arial", 12, "bold"), fg="blue")
total_pl_label.pack(pady=5)

# Save/Load Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="Save Trades", command=save_trades).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Load Trades", command=load_trades).pack(side=tk.LEFT, padx=5)

# Data Structures
csv_file_path = ""  # Path to the CSV file (Initially empty)
monitored_tickers = []  # List to hold monitored tickers
trades = []  # List to hold active trades
total_pl = 0  # Total Profit & Loss

# Start trade monitoring in a background thread
trade_thread = threading.Thread(target=monitor_tickers, daemon=True)
trade_thread.start()

root.mainloop()
