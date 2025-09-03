import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Canvas, Scrollbar
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Buy everyday strategy
def buy_everyday_strategy(data):
    total_capital = data['Close'].sum()
    num_shares = len(data)
    final_value = data['Close'].iloc[-1] * num_shares
    profit_loss = final_value - total_capital
    profit_loss_percent = (profit_loss / total_capital) * 100
    return total_capital, final_value, profit_loss, profit_loss_percent

# Buy only when the closing price is above the custom EMA, and buy more based on previous missed candles
def buy_above_ema_strategy(data, ema_period):
    ema = data['Close'].ewm(span=ema_period, adjust=False).mean()
    total_capital = 0
    num_shares = 0
    missed_candles = 0  # Count candles where price is below EMA
    buy_indices = []  # To store indices where new buying occurs
    prices_at_buy = []  # To store prices at which shares were bought
    
    for i in range(len(data)):
        if data['Close'].iloc[i] > ema.iloc[i]:
            # Buy more when the price crosses above the EMA
            shares_to_buy = 1 + missed_candles
            total_capital += data['Close'].iloc[i] * shares_to_buy
            num_shares += shares_to_buy
            prices_at_buy.extend([data['Close'].iloc[i]] * shares_to_buy)
            buy_indices.append(i)  # Store the index of new buyin
            missed_candles = 0  # Reset missed candles counter
        else:
            missed_candles += 1
    
    final_value = data['Close'].iloc[-1] * num_shares
    average_buy_price = sum(prices_at_buy) / len(prices_at_buy) if prices_at_buy else 0
    profit_loss = final_value - total_capital
    profit_loss_percent = (profit_loss / total_capital) * 100
    
    return total_capital, final_value, profit_loss, profit_loss_percent, average_buy_price, buy_indices

# Buy Above EMA with Exit and Re-entry Strategy
def buy_exit_reenter_strategy(data, ema_period):
    ema = data['Close'].ewm(span=ema_period, adjust=False).mean()
    num_shares = 0
    current_capital = data['Close'].iloc[0]  # Track the capital used to buy shares
    total_invested = 0  # Track total amount invested
    previous_capital = 0  # Track profit/loss from previous exits
    buy_indices = []  # Track the indices where buys occur
    in_position = False  # Track whether we're currently in a position (holding shares)

    for i in range(len(data)):
        close_price = data['Close'].iloc[i]

        if close_price > ema.iloc[i]:  # If the price is above the EMA, we buy
            if not in_position:
                # Buy shares with previous capital + profit/loss (reinvested)
                shares_to_buy = (current_capital + previous_capital) / close_price if close_price > 0 else 0
                num_shares += shares_to_buy
                total_invested = close_price * num_shares  # Track how much we've invested
                buy_indices.append(i)  # Store the index of new buying
                previous_capital = 0  # Reset previous capital after re-entering
                in_position = True

        elif in_position:  # If the price goes below the EMA, we exit the position
            # Sell all shares at the current price
            exit_value = close_price * num_shares
            previous_capital += exit_value  # Store the capital for re-entry later
            num_shares = 0  # No shares held after selling
            in_position = False

    # If we're still holding shares at the end, sell them
    if in_position:
        final_value = data['Close'].iloc[-1] * num_shares
        previous_capital += final_value  # Add the final sale value to the previous capital

    total_profit_loss = previous_capital - total_invested  # Profit or loss based on the total investment
    profit_loss_percent = (total_profit_loss / total_invested) * 100 if total_invested != 0 else 0

    print(total_invested, previous_capital, total_profit_loss, profit_loss_percent, buy_indices )
    return total_invested, previous_capital, total_profit_loss, profit_loss_percent, buy_indices



# Main function to calculate profit/loss, CAGR, and plot the graph
def calculate_gain_loss():
    ticker = selected_ticker.get()
    
    period = period_var.get()
    interval = interval_var.get()
    strategy = strategy_var.get()
    ema_period = int(entry_ema.get())  # Get the EMA period from the input

    try:
        # Download stock data
        data = yf.download(ticker, period=period, interval=interval)
        
        if data.empty:
            messagebox.showerror("Error", "No data found for the given ticker and period.")
            return

        # Print the starting and closing price
        starting_price = data['Close'].iloc[0]
        closing_price = data['Close'].iloc[-1]
        result_starting_price.config(text=f"Starting Price: {starting_price:.2f}")
        result_closing_price.config(text=f"Closing Price: {closing_price:.2f}")

        # Choose the strategy
        if strategy == "Buy Everyday":
            total_capital, final_value, profit_loss, profit_loss_percent = buy_everyday_strategy(data)
            buy_indices = []  # No specific buy indices for this strategy
        elif strategy == "Buy Above EMA":
            total_capital, final_value, profit_loss, profit_loss_percent, average_buy_price, buy_indices = buy_above_ema_strategy(data, ema_period)
        elif strategy == "Buy, Exit, Re-enter":
            total_capital, final_value, profit_loss, profit_loss_percent, buy_indices = buy_exit_reenter_strategy(data, ema_period)

        # Calculate CAGR
        num_periods = len(data)
        if interval == '1d':
           years = num_periods / 252  # Approximate trading days in a year
        elif interval == '1wk':
           years = num_periods / 52   # Approximate weeks in a year
        elif interval == '1mo':
           years = num_periods / 12   # Approximate months in a year
        else:
           raise ValueError("Unsupported interval. Choose 'daily', 'weekly', or 'monthly'.")

        cagr = (final_value / total_capital) ** (1 / years) - 1
        print(years)

        # Handle division by zero for profit_loss_percent
        if total_capital == 0:
            profit_loss_percent = 0
        else:
            profit_loss_percent = (profit_loss / total_capital) * 100

        # Update results on the GUI
        result_capital.config(text=f"Total Capital Spent: {total_capital:.2f}")
        result_final_value.config(text=f"Final Value of Shares: {final_value:.2f}")
        result_profit_loss.config(text=f"Profit/Loss: {profit_loss:.2f}")
        result_profit_loss_percent.config(text=f"Profit/Loss Percentage: {profit_loss_percent:.2f}%")
        result_cagr.config(text=f"CAGR: {cagr * 100:.2f}%")

        # Plotting the stock price and EMA
        fig, ax = plt.subplots(figsize=(20, 10))  # Set plot size to 20x10 inches
        close_n=data['Close'].iloc[-1];
        ax.plot(data.index, data['Close'], label=f'Closing Price:{close_n:.2f}')
        ema = data['Close'].ewm(span=ema_period, adjust=False).mean()
        ax.plot(data.index, ema, label=f'EMA {ema_period}:{ema.iloc[-1]:.2f}', color='orange')

        # Mark areas of new buying
        if buy_indices:
            for idx in buy_indices:
                ax.axvline(data.index[idx], color='red', linestyle='--', alpha=0.5, label='Buy Point')

        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(f'{ticker} Price Chart with EMA')
        ax.legend()
        
        # Embedding the plot in Tkinter window
        for widget in frame_chart.winfo_children():
            widget.destroy()  # Clear previous charts
        canvas = FigureCanvasTkAgg(fig, master=frame_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Create the GUI
root = tk.Tk()
root.title("Stock Gain/Loss Calculator")

# Create a frame for options
frame_options = tk.Frame(root)
frame_options.pack(side="left", fill="both", expand=True, padx=10, pady=10)

result_starting_price = tk.Label(frame_options, text="Starting Price: ")
result_starting_price.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

result_closing_price = tk.Label(frame_options, text="Closing Price: ")
result_closing_price.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

tickers = ["^NSEI","NIFTYBEES.NS","HDFCFLEXI-","0P0000XW77.BO","Kotak_emer:","0P00008TH7.BO","Ppf:","0P0000YWL1.BO","Quantflexi:","0P0000XW4X.BO", "TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS","Conservative:","0P0001MB7K.BO"]
selected_ticker = tk.StringVar()
selected_ticker.set(tickers[0])  # Set NIFTYBEES.NS as the default ticker



# Create a frame for the chart
frame_chart = tk.Frame(root)
frame_chart.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Ticker entry
tk.Label(frame_options, text="Ticker:").grid(row=0, column=0, padx=5, pady=5)
entry_ticker = tk.OptionMenu(frame_options, selected_ticker, *tickers)
entry_ticker.grid(row=0, column=1, padx=5, pady=5)
#entry_ticker.insert(0, "NIFTYBEES.NS")  # Set NIFTYBEES.NS as the default ticker

# Period selection
tk.Label(frame_options, text="Period:").grid(row=1, column=0, padx=5, pady=5)
period_var = tk.StringVar(value="1mo")
period_menu = ttk.Combobox(frame_options, textvariable=period_var, values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
period_menu.grid(row=1, column=1, padx=5, pady=5)

# Interval selection
tk.Label(frame_options, text="Interval:").grid(row=2, column=0, padx=5, pady=5)
interval_var = tk.StringVar(value="1d")
interval_menu = ttk.Combobox(frame_options, textvariable=interval_var, values=["1d", "1wk", "1mo"])
interval_menu.grid(row=2, column=1, padx=5, pady=5)

# Strategy selection
tk.Label(frame_options, text="Strategy:").grid(row=3, column=0, padx=5, pady=5)
strategy_var = tk.StringVar(value="Buy Everyday")
strategy_menu = ttk.Combobox(frame_options, textvariable=strategy_var, values=["Buy Everyday", "Buy Above EMA", "Buy, Exit, Re-enter"])
strategy_menu.grid(row=3, column=1, padx=5, pady=5)

# EMA period entry
tk.Label(frame_options, text="EMA Period:").grid(row=4, column=0, padx=5, pady=5)
entry_ema = tk.Entry(frame_options)
entry_ema.grid(row=4, column=1, padx=5, pady=5)
entry_ema.insert(0,"50")

# Calculate button
btn_calculate = tk.Button(frame_options, text="Calculate", command=calculate_gain_loss)
btn_calculate.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Results display
result_capital = tk.Label(frame_options, text="Total Capital Spent: ")
result_capital.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
result_final_value = tk.Label(frame_options, text="Final Value of Shares: ")
result_final_value.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
result_profit_loss = tk.Label(frame_options, text="Profit/Loss: ")
result_profit_loss.grid(row=8, column=0, columnspan=2, padx=5, pady=5)
result_profit_loss_percent = tk.Label(frame_options, text="Profit/Loss Percentage: ")
result_profit_loss_percent.grid(row=9, column=0, columnspan=2, padx=5, pady=5)
result_cagr = tk.Label(frame_options, text="CAGR: ")
result_cagr.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
