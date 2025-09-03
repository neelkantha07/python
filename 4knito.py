import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import yfinance as yf
import talib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()
root.title("Stock Analysis GUI")
root.geometry("1200x700")

# Functions
def load_csv():
    file_path = filedialog.askopenfilename()
    if file_path:
        df = pd.read_csv(file_path, header=None)
        tickers = df[0].tolist()
        for ticker in tickers:
            listbox.insert(tk.END, f"{ticker}: RSI=NA")

def save_tickers():
    tickers = [item.split(":")[0] for item in listbox.get(0, tk.END)]
    save_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if save_path:
        pd.DataFrame(tickers).to_csv(save_path, index=False, header=False)

def analyze_rsi():
    for item in listbox.get(0, tk.END):
        ticker = item.split(":")[0]
        data = yf.download(f"{ticker}.NSE", period='1y', interval='1d')
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
        rsi_value = data['RSI'].iloc[-1]
        listbox.insert(tk.END, f"{ticker}: RSI={rsi_value:.2f}")

def plot_chart(event):
    selected = listbox.get(listbox.curselection())
    ticker = selected.split(":")[0]
    data = yf.download(f"{ticker}.NSE", period='1y', interval='1d')
    data['EMA50'] = talib.EMA(data['Close'], timeperiod=50)
    data['EMA100'] = talib.EMA(data['Close'], timeperiod=100)
    data['EMA200'] = talib.EMA(data['Close'], timeperiod=200)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    ax1.plot(data['Close'], label='Close Price')
    ax1.plot(data['EMA50'], label='EMA 50')
    ax1.plot(data['EMA100'], label='EMA 100')
    ax1.plot(data['EMA200'], label='EMA 200')
    ax1.legend()
    ax1.set_title(f"{ticker} Price & EMAs")

    ax2.plot(data['RSI'], label='RSI')
    ax2.axhline(70, color='r', linestyle='--')
    ax2.axhline(30, color='g', linestyle='--')
    ax2.legend()
    ax2.set_title("RSI")

    for widget in plot_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Widgets
frame = tk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

listbox = tk.Listbox(frame, width=50)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
listbox.bind('<Double-1>', plot_chart)

scrollbar = tk.Scrollbar(frame, orient="vertical")
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, fill=tk.X)

load_button = tk.Button(button_frame, text="Load CSV", command=load_csv)
load_button.pack(side=tk.LEFT, padx=5, pady=5)

save_button = tk.Button(button_frame, text="Save Tickers", command=save_tickers)
save_button.pack(side=tk.LEFT, padx=5, pady=5)

analyze_button = tk.Button(button_frame, text="Analyze RSI", command=analyze_rsi)
analyze_button.pack(side=tk.LEFT, padx=5, pady=5)

plot_frame = tk.Frame(root)
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

root.mainloop()
