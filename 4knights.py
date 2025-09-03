import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import yfinance as yf
import numpy as np
import pygame
import os
import threading

def stochastic_rsi(data, period, smooth_k, smooth_d):
    delta = data['Close'].diff(1)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    min_rsi = rsi.rolling(window=period).min()
    max_rsi = rsi.rolling(window=period).max()
    stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
    
    k = stoch_rsi.rolling(window=smooth_k).mean()
    d = k.rolling(window=smooth_d).mean()
    
    return d

def play_sound():
    sound_file = r"E:\Github\python\report.wav"
    if os.path.exists(sound_file):
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    else:
        print("File not found:", sound_file)

def analyze_tickers():
    global tickers
    if not tickers:
        return
    
    period = period_var.get()
    interval = interval_var.get()
    
    overbought = []
    oversold = []
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=period, interval=interval)
            if data.empty:
                continue
            
            # Calculate Stochastic RSI for different periods
            stoch1 = stochastic_rsi(data,14, 9, 3)
            stoch2 = stochastic_rsi(data,14, 14, 3)
            stoch3 = stochastic_rsi(data,14, 40, 4)
            stoch4 = stochastic_rsi(data, 14,60, 10)
            
            latest_values = [stoch1.iloc[-1], stoch2.iloc[-1], stoch3.iloc[-1], stoch4.iloc[-1]]
            print(ticker, latest_values)
            # Check conditions for overbought and oversold
            if all(pd.notna(val) and val < .20 for val in latest_values):
                oversold.append((ticker, *latest_values))  # Store ticker with all four RSI values
            elif all(pd.notna(val) and val > .80 for val in latest_values):
                overbought.append((ticker, *latest_values))  # Store ticker with all four RSI values
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    
    # Sort the lists
    oversold.sort(key=lambda x: x[1])  # Sort oversold based on ascending RSI value
    overbought.sort(key=lambda x: x[1], reverse=True)  # Sort overbought based on descending RSI value
    
    # Clear the listboxes and insert sorted tickers with all four RSI values
    listbox_oversold.delete(0, tk.END)
    listbox_overbought.delete(0, tk.END)
    
    for ticker, stoch1_rsi, stoch2_rsi, stoch3_rsi, stoch4_rsi in oversold:
        #listbox_oversold.insert(tk.END, f"{ticker}: 9-period={stoch1_rsi:.2f}, 14-period={stoch2_rsi:.2f}, 40-period={stoch3_rsi:.2f}, 60-period={stoch4_rsi:.2f}")
        listbox_oversold.insert(tk.END, f"{ticker}")
        
    for ticker, stoch1_rsi, stoch2_rsi, stoch3_rsi, stoch4_rsi in overbought:
        listbox_overbought.insert(tk.END, f"{ticker}")
    
    play_sound()



def load_tickers():
    global tickers
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path, header=None)
        tickers = [str(t).strip() + ".NS" for t in df[0].tolist()]
        listbox_tickers.delete(0, tk.END)
        for ticker in tickers:
            listbox_tickers.insert(tk.END, ticker)

def auto_run():
    if auto_var.get():
        analyze_tickers()
        root.after(120000, auto_run)  # Run every 3 minutes

tickers = []

root = tk.Tk()
root.title("Stochastic RSI Analyzer")
root.geometry("600x450")

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10)

btn_load = tk.Button(frame_controls, text="Load Tickers", command=load_tickers)
btn_load.pack(side=tk.LEFT, padx=5)

btn_analyze = tk.Button(frame_controls, text="Analyze", command=analyze_tickers)
btn_analyze.pack(side=tk.LEFT, padx=5)

auto_var = tk.BooleanVar()
btn_auto = tk.Checkbutton(frame_controls, text="Auto Run", variable=auto_var, command=auto_run)
btn_auto.pack(side=tk.LEFT, padx=5)

period_var = tk.StringVar(value="1y")
interval_var = tk.StringVar(value="1d")

period_label = tk.Label(frame_controls, text="Period:")
period_label.pack(side=tk.LEFT)
period_dropdown = ttk.Combobox(frame_controls, textvariable=period_var, values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
period_dropdown.pack(side=tk.LEFT)
period_dropdown.current(1)

interval_label = tk.Label(frame_controls, text="Interval:")
interval_label.pack(side=tk.LEFT)
interval_dropdown = ttk.Combobox(frame_controls, textvariable=interval_var, values=["1m", "2m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"])
interval_dropdown.pack(side=tk.LEFT)
interval_dropdown.current(0)

frame_lists = tk.Frame(root)
frame_lists.pack(pady=10)

listbox_tickers = tk.Listbox(frame_lists, height=10, width=20)
listbox_tickers.pack(side=tk.LEFT, padx=10)

overbought_frame = tk.Frame(frame_lists)
overbought_frame.pack(side=tk.LEFT, padx=10)

tk.Label(overbought_frame, text="Overbought").pack()
listbox_overbought = tk.Listbox(overbought_frame, height=10, width=20)
listbox_overbought.pack()

overSOLD_frame = tk.Frame(frame_lists)
overSOLD_frame.pack(side=tk.LEFT, padx=10)

tk.Label(overSOLD_frame, text="Oversold").pack()
listbox_oversold = tk.Listbox(overSOLD_frame, height=10, width=20)
listbox_oversold.pack()

root.mainloop()
