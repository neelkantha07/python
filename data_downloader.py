import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mplfinance.original_flavor import candlestick_ohlc
import yfinance as yf

# GUI setup
root = tk.Tk()
root.title("Stock Analysis Tool")
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ---------- DOWNLOAD TAB ----------
tab_download = ttk.Frame(notebook)
notebook.add(tab_download, text="Download Data")

interval_var = tk.StringVar(value='1d')
period_var = tk.StringVar(value='3mo')
ticker_file_path = tk.StringVar()

def browse_file():
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    ticker_file_path.set(path)

def download_data():
    path = ticker_file_path.get()
    if not path:
        messagebox.showerror("Error", "No CSV file selected.")
        return

    df = pd.read_csv(path)
    tickers = [x + ".NS" for x in df.iloc[:, 0].dropna()]
    os.makedirs("data", exist_ok=True)

    for ticker in tickers:
        data = yf.download(ticker, interval=interval_var.get(), period=period_var.get())

        if not data.empty:
            # Flatten column headers if they are MultiIndex
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # Drop rows with any missing values to avoid NaNs in output
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

            # Save clean file
            clean_filename = f"data/{ticker.replace('.', '_')}.csv"
            data.to_csv(clean_filename)
            print(f"Saved: {clean_filename}")


ttk.Label(tab_download, text="Select Interval").pack()
ttk.Combobox(tab_download, textvariable=interval_var, values=['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']).pack()
ttk.Label(tab_download, text="Select Period").pack()
ttk.Combobox(tab_download, textvariable=period_var, values=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']).pack()

ttk.Button(tab_download, text="Select Ticker CSV", command=browse_file).pack()
ttk.Label(tab_download, textvariable=ticker_file_path).pack()
ttk.Button(tab_download, text="Download Data", command=download_data).pack(pady=10)

# ---------- PLOT TAB ----------
tab_plot = ttk.Frame(notebook)
notebook.add(tab_plot, text="Plot Chart")

frame_left = tk.Frame(tab_plot)
frame_left.pack(side="left", fill="y", padx=10, pady=10)
frame_right = tk.Frame(tab_plot)
frame_right.pack(side="right", fill="both", expand=True)

data_folder = tk.StringVar(value="data")
plot_canvas = None
toolbar_frame = None

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        data_folder.set(folder)
        update_ticker_list()

def update_ticker_list():
    files = [f[:-4] for f in os.listdir(data_folder.get()) if f.endswith('.csv')]
    ticker_combo['values'] = files

def plot_selected_ticker():
    global plot_canvas, toolbar_frame
    ticker = ticker_combo.get()
    path = os.path.join(data_folder.get(), ticker + '.csv')
    if not os.path.exists(path):
        messagebox.showerror("File not found", path)
        return

    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

        # Filter date range
        start_date = start_entry.get()
        end_date = end_entry.get()
        if start_date:
            df = df[df.index >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df.index <= pd.to_datetime(end_date)]

        df['NumDate'] = mdates.date2num(df.index.to_pydatetime())
        ohlc_data = df[['NumDate', 'Open', 'High', 'Low', 'Close']].values

        fig, (ax1, ax2, ax3) = plt.subplots(
            3, 1, figsize=(10, 7),
            gridspec_kw={"height_ratios": [3, 1, 1]},
            sharex=True
        )

        candlestick_ohlc(ax1, ohlc_data, width=0.6, colorup='green', colordown='red')

        if ma_var.get():
            for ma in [10, 20, 50, 200]:
                df[f"MA{ma}"] = df['Close'].rolling(ma).mean()
                ax1.plot(df.index, df[f"MA{ma}"], label=f"MA{ma}", linewidth=1)

        if bb_var.get():
            ma = df['Close'].rolling(20).mean()
            std = df['Close'].rolling(20).std()
            upper = ma + 2 * std
            lower = ma - 2 * std
            ax1.fill_between(df.index, upper, lower, color='gray', alpha=0.2)

        ax1.set_ylabel("Price")
        ax1.legend()
        ax1.grid(True)

        if vol_var.get():
            ax2.bar(df.index, df['Volume'], color='blue', width=1.0)
            ax2.set_ylabel("Volume")
            ax2.grid(True)

        if rsi_var.get():
            delta = df['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            ax3.plot(df.index, rsi, color='purple')
            ax3.axhline(70, color='red', linestyle='--')
            ax3.axhline(30, color='green', linestyle='--')
            ax3.set_ylim(0, 100)
            ax3.set_ylabel("RSI")
            ax3.grid(True)

        fig.tight_layout()
        fig.autofmt_xdate()

        # Clear previous
        if plot_canvas:
            plot_canvas.get_tk_widget().destroy()
        if toolbar_frame:
            toolbar_frame.destroy()

        plot_canvas = FigureCanvasTkAgg(fig, master=frame_right)
        plot_canvas.draw()
        plot_canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = tk.Frame(frame_right)
        toolbar_frame.pack()
        NavigationToolbar2Tk(plot_canvas, toolbar_frame)

    except Exception as e:
        messagebox.showerror("Plot Error", str(e))


# Plot Controls (Left)
tk.Button(frame_left, text="Select Data Folder", command=choose_folder).pack(pady=5)
ticker_combo = ttk.Combobox(frame_left)
ticker_combo.pack(pady=5)

tk.Label(frame_left, text="Start Date (YYYY-MM-DD)").pack()
start_entry = tk.Entry(frame_left)
start_entry.pack()

tk.Label(frame_left, text="End Date (YYYY-MM-DD)").pack()
end_entry = tk.Entry(frame_left)
end_entry.pack()

ma_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame_left, text="Moving Averages", variable=ma_var).pack(anchor="w")
bb_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame_left, text="Bollinger Bands", variable=bb_var).pack(anchor="w")
vol_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame_left, text="Volume", variable=vol_var).pack(anchor="w")
rsi_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame_left, text="RSI", variable=rsi_var).pack(anchor="w")

tk.Button(frame_left, text="Plot Chart", command=plot_selected_ticker).pack(pady=10)

root.mainloop()
