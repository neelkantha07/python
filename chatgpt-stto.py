import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import yfinance as yf
import threading
import time
from datetime import datetime
import numpy as np

# Function to calculate Fast Stochastic
def fast_stochastic(df, k_period, d_period, smooth_k):
    df['L_low'] = df['Low'].rolling(window=k_period).min()
    df['H_high'] = df['High'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['Close'] - df['L_low']) / (df['H_high'] - df['L_low']))
    df['%K_smooth'] = df['%K'].rolling(window=smooth_k).mean()
    df['%D'] = df['%K_smooth'].rolling(window=d_period).mean()
    return df

# Load tickers via CSV button
def load_tickers():
    file_path = filedialog.askopenfilename()
    if file_path:
        df = pd.read_csv(file_path, header=None)
        tickers.extend([str(t).strip() + '.NS' for t in df[0].tolist()])
        ticker_label.config(text=f"{len(tickers)} tickers loaded")

# Function to fetch live data and check signals
def run_strategy():
    period = '5d'
    interval = '1m'

    while True:
        for ticker in tickers:
            try:
                data = yf.download(ticker, period=period, interval=interval, group_by='ticker', progress=False)

                if data.empty:
                    continue

                # If data columns are MultiIndex — extract for ticker
                if isinstance(data.columns, pd.MultiIndex):
                    data = data.xs(ticker, axis=1, level=0)

                if len(data) < 60:
                    continue

                data = fast_stochastic(data, 60, 10, 1)
                data = fast_stochastic(data, 40, 4, 1)

                latest = data.iloc[-1]

                # Check buy signal
                if latest['%K_smooth'] > latest['%D'] and (ticker not in active_trades):
                    entry_price = latest['Close']
                    sl = entry_price - (entry_price * 0.005)
                    tp = entry_price + (entry_price * 0.005)
                    pnl = 0
                    active_trades[ticker] = [entry_price, sl, tp, pnl, 'LONG']
                    update_table()

                # Check for exit
                elif ticker in active_trades:
                    current_price = latest['Close']
                    entry_price, sl, tp, pnl, direction = active_trades[ticker]

                    if current_price >= tp:
                        pnl = tp - entry_price
                        active_trades.pop(ticker)
                        log_trade(ticker, 'TP HIT', pnl)
                    elif current_price <= sl:
                        pnl = sl - entry_price
                        active_trades.pop(ticker)
                        log_trade(ticker, 'SL HIT', pnl)
                    else:
                        pnl = current_price - entry_price
                        active_trades[ticker][3] = pnl
                        update_table()

            except Exception as e:
                print(f"{ticker} error: {e}")

        time.sleep(60)  # 1 minute interval

# Function to update table
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    for ticker, values in active_trades.items():
        tree.insert("", "end", values=(ticker, round(values[0], 2), round(values[1], 2),
                                       round(values[2], 2), round(values[3], 2), values[4]))

# Function to log closed trade
def log_trade(ticker, result, pnl):
    tree.insert("", "end", values=(ticker, result, "", "", round(pnl, 2), ""))

# GUI Setup
root = tk.Tk()
root.title("Intraday Stochastic Strategy Live Tracker")
root.geometry("850x500")

tickers = []
active_trades = {}

load_btn = tk.Button(root, text="Load Tickers CSV", command=load_tickers)
load_btn.pack(pady=5)

ticker_label = tk.Label(root, text="No tickers loaded.")
ticker_label.pack()

columns = ('Ticker', 'Entry', 'Stop Loss', 'Target', 'P&L', 'Type')
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(expand=True, fill='both')

# Start strategy thread
strategy_thread = threading.Thread(target=run_strategy, daemon=True)
strategy_thread.start()

root.mainloop()
