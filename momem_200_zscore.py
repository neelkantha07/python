import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import yfinance as yf
import numpy as np

# Function to load stocks from a CSV file
def load_csv():
    global stocks
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            # Read CSV file
            df = pd.read_csv(file_path, header=None)
            stocks = [ticker.strip() + ".NS" for ticker in df[0].tolist()]
            
            # Update the listbox
            listbox.delete(0, tk.END)
            for stock in stocks:
                listbox.insert(tk.END, stock)
            
            messagebox.showinfo("Success", f"{len(stocks)} stocks loaded with '.NS' suffix.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")

# Function to save stocks to a CSV file
def save_csv():
    if not displayed_stocks:
        messagebox.showwarning("Warning", "No stocks to save.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                             filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            # Remove '.NS' and save only tickers
            tickers_to_save = [ticker.replace(".NS", "") for ticker, _ in displayed_stocks]
            pd.DataFrame(tickers_to_save, columns=["Ticker"]).to_csv(file_path, index=False)
            messagebox.showinfo("Success", "Tickers saved successfully without '.NS'.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

# Function to calculate and rank the stocks
def calculate_rankings():
    global displayed_stocks
    if not stocks:
        messagebox.showwarning("Warning", "No stocks loaded.")
        return

    try:
        selected_period = period_var.get()
        selected_interval = interval_var.get()
        
        stock_data = []
        for ticker in stocks:
            try:
                # Fetch historical data
                data = yf.download(ticker, period=selected_period, interval=selected_interval, progress=False)
                
                # Calculate 6M and 12M returns
                price_m1 = data['Close'][-1]
                price_m7 = data['Close'][-126] if len(data) >= 126 else None
                price_m13 = data['Close'][-252] if len(data) >= 252 else None
                
                if price_m1 and price_m7 and price_m13:
                    return_6m = (price_m1 / price_m7) - 1
                    return_12m = (price_m1 / price_m13) - 1
                    
                    # Calculate annualized standard deviation
                    log_returns = np.log(data['Close'] / data['Close'].shift(1)).dropna()
                    std_dev = log_returns.std() * np.sqrt(252)
                    
                    # Calculate momentum ratios
                    mr6 = return_6m / std_dev if std_dev else 0
                    mr12 = return_12m / std_dev if std_dev else 0
                    
                    stock_data.append((ticker, return_6m, return_12m, std_dev, mr6, mr12))
            except Exception:
                continue

        # Create DataFrame
        df = pd.DataFrame(stock_data, columns=["Ticker", "6M Return", "12M Return", "Std Dev", "MR6", "MR12"])
        
        # Calculate Z-scores
        df["Z_MR6"] = (df["MR6"] - df["MR6"].mean()) / df["MR6"].std()
        df["Z_MR12"] = (df["MR12"] - df["MR12"].mean()) / df["MR12"].std()
        
        # Weighted Z-score
        df["Weighted_Z"] = 0.5 * df["Z_MR6"] + 0.5 * df["Z_MR12"]
        
        # Normalized Momentum Score
        df["Normalized_Score"] = df["Weighted_Z"].apply(
            lambda z: 1 + z if z >= 0 else (1 - z) ** -1
        )
        
        # Rank by score
        ranked_stocks = df.sort_values("Normalized_Score", ascending=False).head(30)
        displayed_stocks = ranked_stocks[["Ticker", "Normalized_Score"]].values.tolist()
        
        # Update the listbox
        listbox.delete(0, tk.END)
        for ticker, score in displayed_stocks:
            listbox.insert(tk.END, f"{ticker}: {score:.4f}")
        
        messagebox.showinfo("Success", "Top 30 stocks ranked.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the GUI
root = tk.Tk()
root.title("Stock Manager")

# Initialize stock data
stocks = []
displayed_stocks = []

# Period and Interval Variables
period_var = tk.StringVar(value="1y")
interval_var = tk.StringVar(value="1d")

# Add GUI elements
frame = tk.Frame(root)
frame.pack(pady=10)

load_button = tk.Button(frame, text="Load CSV", command=load_csv)
load_button.pack(side=tk.LEFT, padx=5)

save_button = tk.Button(frame, text="Save CSV", command=save_csv)
save_button.pack(side=tk.LEFT, padx=5)

calculate_button = tk.Button(frame, text="Calculate Rankings", command=calculate_rankings)
calculate_button.pack(side=tk.LEFT, padx=5)

# Dropdowns for Period and Interval
dropdown_frame = tk.Frame(root)
dropdown_frame.pack(pady=10)

tk.Label(dropdown_frame, text="Period:").pack(side=tk.LEFT, padx=5)
period_dropdown = ttk.Combobox(dropdown_frame, textvariable=period_var, 
                               values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"], width=10)
period_dropdown.pack(side=tk.LEFT)

tk.Label(dropdown_frame, text="Interval:").pack(side=tk.LEFT, padx=5)
interval_dropdown = ttk.Combobox(dropdown_frame, textvariable=interval_var, 
                                 values=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"], width=10)
interval_dropdown.pack(side=tk.LEFT)

# Listbox to Display Stocks
listbox = tk.Listbox(root, width=50, height=20)
listbox.pack(pady=10)

# Run the application
root.mainloop()
