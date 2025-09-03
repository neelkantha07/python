import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import ta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# List of stock tickers
tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "SBIN.NS", "INFY.NS",
           # (remaining tickers...)
           "UNITDSPR.NS"]

# Function to calculate stocks where Bollinger Bands are inside the Keltner Channel
def check_bollinger_inside_keltner():
    matching_tickers = []
    
    for ticker in tickers:
        try:
            # Download historical data for the ticker
            df = yf.download(ticker, period="6mo", interval="1d")
            
            if df.empty:
                messagebox.showinfo("Loading error","empty")
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

            # If the latest value of bb_inside_kc is True, add ticker to the list
            if df['bb_inside_kc'].iloc[-1]:
                matching_tickers.append(ticker)
        
        except Exception as e:
            messagebox.showinfo("Loading error",f"Error processing ticker {ticker}: {e}")
    
    return matching_tickers

# Function to display matching tickers in the Listbox
def display_matching_stocks():
    matching_stocks = check_bollinger_inside_keltner()
    
    if matching_stocks:
        listbox.delete(0, tk.END)  # Clear the listbox
        for stock in matching_stocks:
            listbox.insert(tk.END, stock)
    else:
        messagebox.showinfo("No Matches", "No tickers meet the criteria.")

# Function to plot the price chart of the selected ticker
def plot_chart(event):
    selected_ticker = listbox.get(listbox.curselection())
    df = yf.download(selected_ticker, period="6mo", interval="1d")
    
    # Clear the previous plot
    for widget in chart_frame.winfo_children():
        widget.destroy()

    # Create a new plot
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df.index, df['Close'], label='Close Price')
    ax.set_title(f"{selected_ticker} - Price Chart")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()

    # Embed the plot in the Tkinter GUI
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Setting up the GUI
root = tk.Tk()
root.title("Stock Ticker Analysis")

# Create a frame for the layout
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Create a frame for the Listbox and the chart
listbox_frame = tk.Frame(main_frame)
listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

chart_frame = tk.Frame(main_frame)
chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Add a label
tk.Label(listbox_frame, text="Matching Stock Tickers:").pack(pady=10)

# Add a Listbox to display matching tickers
listbox = tk.Listbox(listbox_frame, width=50, height=20)
listbox.pack(pady=10)
listbox.bind("<<ListboxSelect>>", plot_chart)  # Bind click event to the Listbox

# Add a scrollbar to the Listbox
scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
scrollbar.config(command=listbox.yview)
scrollbar.pack(side="right", fill="y")
listbox.config(yscrollcommand=scrollbar.set)

# Add a button to run the calculation
calculate_button = tk.Button(listbox_frame, text="Calculate", command=display_matching_stocks)
calculate_button.pack(pady=10)

# Run the application
root.mainloop()
