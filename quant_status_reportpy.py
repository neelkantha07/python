import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yfinance as yf
import pandas as pd
import quantstats as qs
import os

# Global variable to hold data
data = None

# Function to load tickers and weights from a CSV file
def load_csv():
    global data  # Declare data as global to use it in this function
    print("Loading CSV file...")
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected.")
        return

    try:
        data = pd.read_csv(file_path, header=None)
        if data.shape[1] != 2:
            raise ValueError("CSV must have exactly two columns.")
        data.columns = ["Ticker", "Weight"]
        data["Weight"] = data["Weight"] / 100  # Convert weights to decimal
        data["Ticker"] = data["Ticker"].astype(str) + ".NS"  # Add '.NS' suffix

        ticker_listbox.delete(0, tk.END)  # Clear previous entries in the listbox
        for i, row in data.iterrows():
            ticker_listbox.insert(tk.END, f"{row['Ticker']} - Weight: {row['Weight']:.2f}")

        messagebox.showinfo("Success", "Tickers and weights loaded successfully.")
    except Exception as e:
        print(f"Failed to load CSV file: {e}")
        messagebox.showerror("Error", f"Failed to load CSV file.\n{e}")

# Function to generate and save the QuantStats report
def generate_and_save_report():
    global data  # Declare data as global to use it in this function
    if data is None or data.empty:
        messagebox.showerror("Error", "No data loaded.")
        return

    # Get selected period and interval
    period = period_combobox.get()
    interval = interval_combobox.get()

    # Create the 'Reports' folder if it does not exist
    if not os.path.exists('Reports'):
        os.makedirs('Reports')

    try:
        # Prepare the portfolio with weights
        portfolio = {}
        for _, row in data.iterrows():
            ticker = row['Ticker']
            weight = row['Weight']
            portfolio[ticker] = weight

        # Download data and calculate portfolio returns
        portfolio_returns = pd.DataFrame()
        for ticker in portfolio:
            print(f"Fetching data for {ticker}...")
            ticker_data = yf.download(ticker, period=period, interval=interval, progress=False)
            ticker_data['Returns'] = ticker_data['Adj Close'].pct_change()
            portfolio_returns[ticker] = ticker_data['Returns'] * portfolio[ticker]

        portfolio_returns['Portfolio'] = portfolio_returns.sum(axis=1).dropna()

        # Ensure data is sorted and prepared for report
        qs.extend_pandas()
        qs.reports.html(portfolio_returns['Portfolio'], benchmark="^NSEI", output='Reports/quantstats_report.html', title="QuantStats Report")

        print("Report saved as 'Reports/quantstats_report.html'")
        messagebox.showinfo("Success", "Report generated and saved in 'Reports' folder.")
    except Exception as e:
        print(f"Error generating or saving report: {e}")
        messagebox.showerror("Error", f"Error generating or saving report.\n{e}")

# Create the main window
root = tk.Tk()
root.title("QuantStats Report Generator")

# Button to load tickers and weights from CSV
load_button = tk.Button(root, text="Load CSV", command=load_csv)
load_button.pack(pady=10)

# Dropdown for selecting period
period_label = tk.Label(root, text="Select Period:")
period_label.pack(pady=5)
period_combobox = ttk.Combobox(root, values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
period_combobox.set("1mo")  # Default period
period_combobox.pack(pady=5)

# Dropdown for selecting interval
interval_label = tk.Label(root, text="Select Interval:")
interval_label.pack(pady=5)
interval_combobox = ttk.Combobox(root, values=["1m", "5m", "15m", "30m", "60m", "1d", "5d", "1wk", "1mo"])
interval_combobox.set("1d")  # Default interval
interval_combobox.pack(pady=5)

# Button to generate and save the QuantStats report
generate_button = tk.Button(root, text="Generate & Save Report", command=generate_and_save_report)
generate_button.pack(pady=10)

# Listbox to display tickers and weights
ticker_listbox = tk.Listbox(root, width=80, height=20)
ticker_listbox.pack(pady=20)

# Start the GUI main loop
root.mainloop()
