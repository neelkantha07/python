import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import yfinance as yf
import numpy as np
import pygame
import os
import threading,csv


def calculate_vwap(data):
    # Ensure data has 'Close', 'High', 'Low', and 'Volume' columns
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
    return vwap

def save_to_csv(file_name, data):
    """Save only the ticker names to a CSV file without headers."""
    try:
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow([row[0]])  # Write only the ticker name (first element)
        print(f"Data saved to {file_name}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

def fast_stochastic(data, k_period, d_period):
    """Calculate the Fast Stochastic Oscillator (%K and %D)."""
    lowest_low = data['Low'].rolling(window=k_period).min()
    highest_high = data['High'].rolling(window=k_period).max()
    k = ((data['Close'] - lowest_low) / (highest_high - lowest_low)) * 100
    d = k.rolling(window=d_period).mean()
    return d

def full_stochastic(data, k_period=60, smooth_k=10, d_period=10):
    """Calculate the Full Stochastic Oscillator (%K and %D)."""
    lowest_low = data['Low'].rolling(window=k_period).min()
    highest_high = data['High'].rolling(window=k_period).max()
    fast_k = ((data['Close'] - lowest_low) / (highest_high - lowest_low)) * 100
    full_k = fast_k.rolling(window=smooth_k).mean()
    full_d = full_k.rolling(window=d_period).mean()
    return full_d

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
    best20 = []
    best201 = []
    volup=[]
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=period, interval=interval, group_by='ticker', progress=True)
            
            if data.empty:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data = data.xs(ticker, axis=1, level=0)
            # Calculate Stochastic RSI for different periods
            stoch1 = fast_stochastic(data,9, 3)
            stoch2 = fast_stochastic(data, 14, 3)
            stoch3 = fast_stochastic(data,40, 4)
            #stoch4 = full_stochastic(data)
            stoch4 = fast_stochastic(data,60,10)
            avg_volume_5d = data['Volume'].mean()
            current_volume = data['Volume'].iloc[-1]
            vwap=calculate_vwap(data)
            vwap_up=vwap.iloc[-1]*(1+.0002)
            vwap_down=vwap.iloc[-1]*(1-.0002)
            price=data['Close'].iloc[-1]


            
            latest_values = [stoch4.iloc[-1], stoch3.iloc[-1], stoch2.iloc[-1],stoch1.iloc[-1] ]
            print(ticker, latest_values)
            
            # Check conditions for overbought, oversold, and best20
            if all(pd.notna(val) and val < 20 for val in latest_values):
                oversold.append((ticker, *latest_values))
            elif all(pd.notna(val) and val > 80 for val in latest_values):
                overbought.append((ticker, *latest_values))
            elif ( stoch4.iloc[-1] > 85):
                best20.append((ticker, *latest_values))
           # elif (stoch1.iloc[-1] > 80 and stoch4.iloc[-1] >69 and stoch4.iloc[-1] < 80 ):
           # elif ((stoch1.iloc[-1] > 80 and stoch4.iloc[-1] >60 )   ):
            elif price > vwap_down and price < vwap_up:

                best201.append((ticker, *latest_values))
            elif(current_volume > 3*avg_volume_5d):
                volup.append((ticker,*latest_values))
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    
    # Sort the lists
    oversold.sort(key=lambda x: x[1])
    overbought.sort(key=lambda x: x[1], reverse=True)
    best20.sort(key=lambda x: x[1], reverse=True)
    best201.sort(key=lambda x: x[1])
    volup.sort(key=lambda x: x[1], reverse=True)
    
    
    # Clear the listboxes and insert sorted tickers with all four RSI values
    listbox_oversold.delete(0, tk.END)
    listbox_overbought.delete(0, tk.END)
    listbox_best_20.delete(0, tk.END)
    listbox_best_201.delete(0, tk.END)
    listbox_best_202.delete(0, tk.END)
    
    for ticker, stoch1_rsi, stoch2_rsi, stoch3_rsi, stoch4_rsi in oversold:
        listbox_oversold.insert(tk.END, f"{ticker}")
        
    for ticker, stoch1_rsi, stoch2_rsi, stoch3_rsi, stoch4_rsi in overbought:
        listbox_overbought.insert(tk.END, f"{ticker},{latest_values}")
        
    for ticker, stoch1_rsi, stoch2_rsi, stoch3_rsi, stoch4_rsi in best20:
        listbox_best_20.insert(tk.END, f"{ticker}")
    for ticker, stoch1_rsi, stoch2_rsi, stoch3_rsi, stoch4_rsi in best201:
        listbox_best_201.insert(tk.END, f"{ticker}")
    for ticker, stoch1_rsi, stoch2_rsi, stoch3_rsi, stoch4_rsi in volup:
        listbox_best_202.insert(tk.END, f"{ticker}")
        
    save_to_csv("best_20_down.csv", best20)
    save_to_csv("best_20_up.csv", best201)
    save_to_csv("vol_up.csv", volup)
    save_to_csv("overbought.csv", overbought)

 
    play_sound()

def load_tickers():
    global tickers
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    listbox_tickers.delete(0,tk.END)
    if file_path:
        df = pd.read_csv(file_path, header=None)
        tickers = [str(t).strip() + ".NS" for t in df[0].tolist()]
        listbox_tickers.delete(0, tk.END)
        for ticker in tickers:
            listbox_tickers.insert(tk.END, ticker)

def auto_run():
    if auto_var.get():
        analyze_tickers()
        root.after(120000, auto_run)

def run_analysis_thread():
    threading.Thread(target=analyze_tickers, daemon=True).start()

tickers = []

root = tk.Tk()
root.title("Stochastic RSI Analyzer")
root.geometry("800x650")

frame_controls = tk.Frame(root)
frame_controls.pack(pady=10)

btn_load = tk.Button(frame_controls, text="Load Tickers", command=load_tickers)
btn_load.pack(side=tk.LEFT, padx=5)

btn_analyze = tk.Button(frame_controls, text="Analyze", command=run_analysis_thread)
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

oversold_frame = tk.Frame(frame_lists)
oversold_frame.pack(side=tk.LEFT, padx=10)

tk.Label(oversold_frame, text="Oversold").pack()
listbox_oversold = tk.Listbox(oversold_frame, height=10, width=20)
listbox_oversold.pack()

best_20_frame = tk.Frame(frame_lists)
best_20_frame.pack(side=tk.LEFT, padx=10)

best_20_frame2 = tk.Frame(frame_lists)
best_20_frame2.pack(side=tk.LEFT, padx=10)

tk.Label(best_20_frame, text="Best 20 down").pack()
listbox_best_20 = tk.Listbox(best_20_frame, height=10, width=20)
listbox_best_20.pack()

tk.Label(best_20_frame2, text="Best 20 up").pack()
listbox_best_201 = tk.Listbox(best_20_frame, height=10, width=20)
listbox_best_201.pack()

tk.Label(best_20_frame2, text="Volume up").pack()
listbox_best_202 = tk.Listbox(best_20_frame, height=10, width=20)
listbox_best_202.pack()


root.mainloop()
