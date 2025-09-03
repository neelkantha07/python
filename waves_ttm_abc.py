import tkinter as tk
from tkinter import ttk
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def weighted_moving_average(series, period):
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hull_moving_average(series, period):
    wma_half = weighted_moving_average(series, period // 2)
    wma_full = weighted_moving_average(series, period)
    hma_raw = (2 * wma_half) - wma_full
    return weighted_moving_average(hma_raw, int(np.sqrt(period)))

def calculate_ttm_waves(df):
    df['Wave_A'] = hull_moving_average(df['Close'], 13)
    df['Wave_B'] = df['Close'].ewm(span=34).mean()
    df['Wave_C'] = df['Close'].rolling(window=55).mean()
    
    df['Wave_A_Positive'] = df['Wave_A'].diff() > 0
    df['Wave_B_Positive'] = df['Wave_B'].diff() > 0
    df['Wave_C_Positive'] = df['Wave_C'].diff() > 0
    
    return df

def plot_ttm_wave(df, ticker):
    fig, ax = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    ax[0].plot(df.index, df['Close'], label='Close Price', color='black', linewidth=1.5)
    ax[0].set_title(f'{ticker} Price Chart')
    ax[0].legend()
    ax[0].grid()
    
    ax[1].bar(df.index, df['Wave_A'], color=df['Wave_A_Positive'].map({True: 'green', False: 'red'}))
    ax[1].set_title('Wave A (Green: Positive, Red: Negative)')
    ax[1].grid()
    
    ax[2].bar(df.index, df['Wave_B'], color=df['Wave_B_Positive'].map({True: 'blue', False: 'orange'}))
    ax[2].set_title('Wave B (Blue: Positive, Orange: Negative)')
    ax[2].grid()
    
    ax[3].bar(df.index, df['Wave_C'], color=df['Wave_C_Positive'].map({True: 'purple', False: 'brown'}))
    ax[3].set_title('Wave C (Purple: Positive, Brown: Negative)')
    ax[3].grid()
    
    return fig

def fetch_and_plot():
    ticker = ticker_entry.get()
    period = period_var.get()
    interval = interval_var.get()
    if not ticker:
        return
    
    df = yf.download(ticker, period=period, interval=interval)
    if df.empty:
        return
    
    df = calculate_ttm_waves(df)
    fig = plot_ttm_wave(df, ticker)
    
    for widget in plot_frame.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

root = tk.Tk()
root.title("TTM Wave Analysis")
root.geometry("900x700")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Ticker:").grid(row=0, column=0, padx=5)
ticker_entry = tk.Entry(frame)
ticker_entry.grid(row=0, column=1, padx=5)

period_var = tk.StringVar(value="1y")
tk.Label(frame, text="Period:").grid(row=0, column=2, padx=5)
period_dropdown = ttk.Combobox(frame, textvariable=period_var, values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
period_dropdown.grid(row=0, column=3, padx=5)

interval_var = tk.StringVar(value="1d")
tk.Label(frame, text="Interval:").grid(row=0, column=4, padx=5)
interval_dropdown = ttk.Combobox(frame, textvariable=interval_var, values=["1m", "2m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo", "3mo"])
interval_dropdown.grid(row=0, column=5, padx=5)

tk.Button(frame, text="Analyze", command=fetch_and_plot).grid(row=0, column=6, padx=5)

plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
