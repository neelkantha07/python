import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import os
import mplfinance as mpf
from datetime import datetime
import matplotlib.pyplot as plt

class BacktestApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Strategy Backtest Tool")

        self.left_frame = tk.Frame(master)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill='y')

        self.right_frame = tk.Frame(master)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill='both', expand=True)

        # Folder and Ticker selection
        self.folder_button = tk.Button(self.left_frame, text="Choose Data Folder", command=self.load_folder)
        self.folder_button.pack()

        self.ticker_combo = ttk.Combobox(self.left_frame, state='readonly')
        self.ticker_combo.pack(pady=5)

        # Date range
        tk.Label(self.left_frame, text="From (YYYY-MM-DD)").pack()
        self.start_entry = tk.Entry(self.left_frame)
        self.start_entry.pack()

        tk.Label(self.left_frame, text="To (YYYY-MM-DD)").pack()
        self.end_entry = tk.Entry(self.left_frame)
        self.end_entry.pack()

        # Indicator checkboxes
        self.ma_vars = {}
        for ma in [10, 20, 50, 200]:
            var = tk.IntVar()
            cb = tk.Checkbutton(self.left_frame, text=f"SMA {ma}", variable=var)
            cb.pack(anchor='w')
            self.ma_vars[ma] = var

        self.bb = tk.IntVar()
        tk.Checkbutton(self.left_frame, text="Bollinger Bands", variable=self.bb).pack(anchor='w')

        self.rsi = tk.IntVar()
        tk.Checkbutton(self.left_frame, text="RSI", variable=self.rsi).pack(anchor='w')

        self.volume = tk.IntVar()
        tk.Checkbutton(self.left_frame, text="Volume", variable=self.volume).pack(anchor='w')

        # Strategy selection
        self.strategy_var = tk.StringVar(value="SMA Crossover")
        tk.Label(self.left_frame, text="Select Strategy:").pack()
        ttk.Combobox(self.left_frame, textvariable=self.strategy_var, values=["SMA Crossover"]).pack(pady=5)

        # Buttons
        self.run_button = tk.Button(self.left_frame, text="Run Backtest", command=self.run_backtest)
        self.run_button.pack(pady=5)

        self.save_button = tk.Button(self.left_frame, text="Save Trade Log", command=self.save_trades)
        self.save_button.pack(pady=5)

        # Trade log display
        self.text = tk.Text(self.left_frame, width=40, height=20)
        self.text.pack(pady=5)

        self.data_folder = ""
        self.df = pd.DataFrame()
        self.trades = []
        self.equity_curve = pd.Series(dtype=float)

    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.data_folder = folder
            files = [f.replace('.csv', '') for f in os.listdir(folder) if f.endswith('.csv')]
            self.ticker_combo['values'] = files
            if files:
                self.ticker_combo.set(files[0])

    def calculate_indicators(self, df):
        for ma, var in self.ma_vars.items():
            if var.get():
                df[f"SMA{ma}"] = df['Close'].rolling(window=ma).mean()

        if self.bb.get():
            df['BB_Mid'] = df['Close'].rolling(window=20).mean()
            df['BB_Std'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
            df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']

        if self.rsi.get():
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def strategy_sma_crossover(self, df):
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()

        position = None
        self.trades = []
        equity = []
        capital = 100000
        shares = 0

        for i in range(1, len(df)):
            if df['SMA20'].iloc[i] > df['SMA50'].iloc[i] and df['SMA20'].iloc[i - 1] <= df['SMA50'].iloc[i - 1]:
                if position != 'long':
                    entry_price = df['Close'].iloc[i]
                    entry_date = df.index[i]
                    shares = capital // entry_price
                    capital -= shares * entry_price
                    position = 'long'
                    self.trades.append({"Date": entry_date, "Action": "BUY", "Price": entry_price})

            elif df['SMA20'].iloc[i] < df['SMA50'].iloc[i] and df['SMA20'].iloc[i - 1] >= df['SMA50'].iloc[i - 1]:
                if position == 'long':
                    exit_price = df['Close'].iloc[i]
                    exit_date = df.index[i]
                    capital += shares * exit_price
                    pnl = (exit_price - entry_price) * shares
                    self.trades.append({"Date": exit_date, "Action": "SELL", "Price": exit_price, "PnL": pnl})
                    shares = 0
                    position = None

            current_value = capital + shares * df['Close'].iloc[i]
            equity.append(current_value)

        self.equity_curve = pd.Series(equity, index=df.index[1:])
        return df

    def run_backtest(self):
        ticker = self.ticker_combo.get()
        if not ticker:
            messagebox.showerror("Error", "Select a ticker.")
            return

        path = os.path.join(self.data_folder, ticker + '.csv')
        df = pd.read_csv(path, header=[2], index_col=0, parse_dates=True)
        df = df[['Close', 'Open', 'High', 'Low', 'Volume']]
        df = df.dropna()
        df.columns = ['Close', 'Open', 'High', 'Low', 'Volume']

        start = self.start_entry.get()
        end = self.end_entry.get()
        if start:
            df = df[df.index >= pd.to_datetime(start)]
        if end:
            df = df[df.index <= pd.to_datetime(end)]

        df = self.calculate_indicators(df)
        self.df = self.strategy_sma_crossover(df)
        self.plot_chart()

        # Show trade log
        self.text.delete(1.0, tk.END)
        for trade in self.trades:
            line = f"{trade['Date'].strftime('%Y-%m-%d')} | {trade['Action']} @ {trade['Price']}"
            if 'PnL' in trade:
                line += f" | PnL: {trade['PnL']:.2f}"
            self.text.insert(tk.END, line + "\n")

    def plot_chart(self):
        df = self.df.copy()
        apds = []

        for ma, var in self.ma_vars.items():
            if var.get() and f"SMA{ma}" in df.columns:
                apds.append(mpf.make_addplot(df[f"SMA{ma}"], color='blue'))

        if self.bb.get() and 'BB_Upper' in df:
            apds.append(mpf.make_addplot(df['BB_Upper'], color='red'))
            apds.append(mpf.make_addplot(df['BB_Lower'], color='red'))

        panels = {}

        if self.rsi.get():
            if 'RSI' not in df.columns:
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
            apds.append(mpf.make_addplot(df['RSI'], panel=1, color='purple'))
            panels['RSI'] = 1

        if self.volume.get():
            panels['Volume'] = 2

        fig, axes = mpf.plot(df, type='candle', volume=self.volume.get(),
                             addplot=apds, returnfig=True, style='yahoo',
                             panel_ratios=(3, 1, 1) if self.rsi.get() and self.volume.get() else None)

        # Plot Buy/Sell Markers
        for trade in self.trades:
            idx = trade['Date']
            if idx in df.index:
                price = df.loc[idx]['Close']
                color = 'green' if trade['Action'] == 'BUY' else 'red'
                marker = '^' if trade['Action'] == 'BUY' else 'v'
                axes[0].plot(idx, price, marker=marker, color=color, markersize=10)

        # Equity curve
        if not self.equity_curve.empty:
            fig_equity, ax_equity = plt.subplots(figsize=(8, 2))
            ax_equity.plot(self.equity_curve, color='black')
            ax_equity.set_title("Equity Curve")
            ax_equity.set_ylabel("Equity")
            plt.tight_layout()
            plt.show()

    def save_trades(self):
        if not self.trades:
            messagebox.showinfo("No Trades", "No trades to save.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv")
        if filepath:
            df = pd.DataFrame(self.trades)
            df.to_csv(filepath, index=False)
            messagebox.showinfo("Saved", "Trade log saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BacktestApp(root)
    root.mainloop()
