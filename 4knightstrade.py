import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
import numpy as np
import json
import threading
import time

trades={}
# Function to calculate stochastic oscillator
def stochastic(df, period=60, k_smooth=10):
    df['L'] = df['Low'].rolling(period).min()
    df['H'] = df['High'].rolling(period).max()
    df['%K'] = 100 * ((df['Close'] - df['L']) / (df['H'] - df['L']))
    df['%K'] = df['%K'].rolling(k_smooth).mean()
    return df

# Function to calculate EMA
def ema(df, span):
    return df['Close'].ewm(span=span, adjust=False).mean()

# Function to monitor tickers
def monitor_tickers():
    while True:
        for ticker in monitored_tickers.copy():
            print("Checking... ")
            check_trade_conditions(ticker)
        active_trades()
        time.sleep(30)  # Check every 1 minute
def active_trades():
    global trades
    global total_pl
  
    qty=10
    
    trade = {
                "Ticker": "",
                "Entry": round(2, 2),
                "Stop Loss": round(2, 2),
                "Target": round(2, 2),
                "Exit Price": None,
                "P&L": 0,
                "Status": "Active"
            }
    
    for trade in trades:
        if  trade['Status'] == "Active":
            ticker=trade['Ticker']
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if df.empty:
                return

            df = stochastic(df)
            df['EMA5'] = ema(df, 5)
            df['EMA15'] = ema(df, 15)
            #print(df)

            last_row = df.iloc[-1]
            fast_stoch = last_row['%K']
            price = last_row['Close']
            ema5 = last_row['EMA5']
            ema15 = last_row['EMA15']
            
            exit_reason = None
            if price >= trade['Stop Loss']:
                trade['Status'] = "Stopped Out"
                exit_reason = "Stop Loss"
            elif price <= trade['Target']:
                trade['Status'] = "Target Hit"
                exit_reason = "Target"
            elif fast_stoch < 55:
                trade['Status'] = "Exit :Stoch < 55"
                exit_reason = "Stoch < 55"

            # Calculate P&L if exited
            if trade['Status'] != "Active":
                trade['Exit Price'] = round(price, 2)
                trade['P&L'] = round(( trade['Entry']- trade['Exit Price'])* trade['Qty'], 2)
                total_pl += trade['P&L']  # Update Total P&L
                update_total_pl()
                update_listboxes()
                update_table()
    
# Function to check trade entry/exit conditions
def check_trade_conditions(ticker):
    global total_pl
    global trades
    try:
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
        ndlast=df.iloc[-2]
        fast_stoch2=ndlast['%K']

        # Entry Condition
        if fast_stoch < 80 and fast_stoch2 > fast_stoch and price < ema5 and ema5 < ema15:
            entry_price = price
            stop_loss = entry_price * (1 + 0.0013)  # -0.12%
            target = entry_price * (1 - 0.0031)     # +0.31%

            trade = {
                "Ticker": ticker,
                "Entry": round(entry_price, 2),
                "Stop Loss": round(stop_loss, 2),
                "Target": round(target, 2),
                "Exit Price": None,
                "P&L": 0,
                "Status": "Active",
                "Qty":  10 if entry_price > 7000 else 100
                }
            trades.append(trade)
            monitored_tickers.remove(ticker)
            update_listboxes()
            update_table()

        # # Exit Condition for Active Trades
        # for trade in trades:
        #     if trade['Ticker'] == ticker and trade['Status'] == "Active":
        #         exit_reason = None
        #         if price >= trade['Stop Loss']:
        #             trade['Status'] = "Stopped Out"
        #             exit_reason = "Stop Loss"
        #         elif price <= trade['Target']:
        #             trade['Status'] = "Target Hit"
        #             exit_reason = "Target"
        #         elif fast_stoch < 55:
        #             trade['Status'] = "Exit Signal"
        #             exit_reason = "Stoch < 55"

        #         # Calculate P&L if exited
        #         if trade['Status'] != "Active":
        #             trade['Exit Price'] = round(price, 2)
        #             trade['P&L'] = round(price - trade['Entry'], 2)
        #             total_pl += trade['P&L']  # Update Total P&L
        #             update_total_pl()
        #             update_table()

    except Exception as e:
        print(f"Error checking {ticker}: {e}")

# Function to add ticker for monitoring
def add_ticker():
    ticker = ticker_entry.get().strip().upper()
    ticker_entry.delete(0,tk.END)
    if ticker and ticker not in monitored_tickers:
        monitored_tickers.append(ticker)
        update_listboxes()
    else:
        messagebox.showerror("Error", "Invalid or duplicate ticker!")

# Update the listboxes
def update_listboxes():
    ticker_listbox.delete(0, tk.END)
    for ticker in monitored_tickers:
        ticker_listbox.insert(tk.END, ticker)

    trade_listbox.delete(0, tk.END)
    for trade in trades:
        trade_listbox.insert(tk.END, f"{trade['Ticker']} | Entry: {trade['Entry']} | Status: {trade['Status']}")

# Update the trade table
def update_table():
    for row in trade_table.get_children():
        trade_table.delete(row)
    for trade in trades:
        trade_table.insert("", "end", values=(
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
root.title("Real-Time Trade Monitor with P&L")

# Entry Frame
entry_frame = tk.Frame(root)
entry_frame.pack(pady=10)
tk.Label(entry_frame, text="Enter Ticker:").grid(row=0, column=0, padx=5, pady=5)
ticker_entry = tk.Entry(entry_frame)
ticker_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(entry_frame, text="Add Ticker", command=add_ticker).grid(row=0, column=2, padx=5, pady=5)

# Ticker Monitoring Listbox
tk.Label(root, text="Monitored Tickers:").pack()
ticker_listbox = tk.Listbox(root, width=40, height=5)
ticker_listbox.pack(pady=5)

# Active Trades Listbox
tk.Label(root, text="Active Trades:").pack()
trade_listbox = tk.Listbox(root, width=60, height=5)
trade_listbox.pack(pady=5)

# Trade Table
tk.Label(root, text="Trade Status Table:").pack()
columns = ("Ticker", "Entry", "Stop Loss", "Target", "Exit Price", "P&L", "Status")
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
monitored_tickers = []
trades = []
total_pl = 0  # Total P&L tracker

# Start background thread for monitoring
threading.Thread(target=monitor_tickers, daemon=True).start()

root.mainloop()
