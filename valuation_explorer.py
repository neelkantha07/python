# -*- coding: utf-8 -*-
"""
Updated Valuation Modeling App with DCF and improved side panel
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
from datetime import datetime

class ValuationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Valuation Modeling App")
        self.root.geometry("1400x800")

        # Main container
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel for controls
        self.control_frame = tk.Frame(self.main_frame, width=300, padx=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right panel for chart and results
        self.display_frame = tk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # File selection
        self.file_label = tk.Label(self.control_frame, text="No file selected", fg="blue")
        self.file_label.pack(pady=5)
        tk.Button(self.control_frame, text="Upload CSV/Excel", command=self.load_file).pack(pady=5)

        # Valuation parameters frame
        param_frame = tk.LabelFrame(self.control_frame, text="Valuation Parameters", padx=5, pady=5)
        param_frame.pack(pady=10, fill=tk.X)

        # CAGR input
        tk.Label(param_frame, text="CAGR (%)").grid(row=0, column=0, sticky="w")
        self.cagr_entry = tk.Entry(param_frame, width=8)
        self.cagr_entry.insert(0, "10")
        self.cagr_entry.grid(row=0, column=1, pady=2)

        # PE inputs
        tk.Label(param_frame, text="PE Ratios").grid(row=1, column=0, sticky="w", pady=(10,0))
        tk.Label(param_frame, text="Min:").grid(row=2, column=0, sticky="e")
        self.pe_min = tk.Entry(param_frame, width=6)
        self.pe_min.insert(0, "15")
        self.pe_min.grid(row=2, column=1, sticky="w")
        
        tk.Label(param_frame, text="Avg:").grid(row=3, column=0, sticky="e")
        self.pe_avg = tk.Entry(param_frame, width=6)
        self.pe_avg.insert(0, "22")
        self.pe_avg.grid(row=3, column=1, sticky="w")
        
        tk.Label(param_frame, text="Max:").grid(row=4, column=0, sticky="e")
        self.pe_max = tk.Entry(param_frame, width=6)
        self.pe_max.insert(0, "30")
        self.pe_max.grid(row=4, column=1, sticky="w")

        # DCF inputs
        tk.Label(param_frame, text="DCF Parameters").grid(row=5, column=0, sticky="w", pady=(10,0))
        tk.Label(param_frame, text="Growth % (5y):").grid(row=6, column=0, sticky="e")
        self.dcf_growth = tk.Entry(param_frame, width=6)
        self.dcf_growth.insert(0, "12")
        self.dcf_growth.grid(row=6, column=1, sticky="w")
        
        tk.Label(param_frame, text="Terminal %:").grid(row=7, column=0, sticky="e")
        self.dcf_terminal = tk.Entry(param_frame, width=6)
        self.dcf_terminal.insert(0, "3")
        self.dcf_terminal.grid(row=7, column=1, sticky="w")
        
        tk.Label(param_frame, text="Discount %:").grid(row=8, column=0, sticky="e")
        self.dcf_discount = tk.Entry(param_frame, width=6)
        self.dcf_discount.insert(0, "10")
        self.dcf_discount.grid(row=8, column=1, sticky="w")

        # Regression type
        tk.Label(param_frame, text="Regression Type:").grid(row=9, column=0, sticky="w", pady=(10,0))
        self.reg_type = ttk.Combobox(param_frame, values=["None", "Linear", "Log"], width=8)
        self.reg_type.set("None")
        self.reg_type.grid(row=9, column=1, sticky="w")

        # Action buttons
        btn_frame = tk.Frame(self.control_frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Calculate", command=self.plot_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Export Chart", command=self.save_chart).pack(side=tk.LEFT, padx=5)

        # Results display
        self.results_frame = tk.LabelFrame(self.control_frame, text="Valuation Results", padx=5, pady=5)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Initialize result labels
        self.result_vars = {
            'current_price': tk.StringVar(value="Current Price: -"),
            'cagr_fair_value': tk.StringVar(value="CAGR Fair Value: -"),
            'cagr_discount': tk.StringVar(value="CAGR Discount: -"),
            'pe_valuation': tk.StringVar(value="PE Valuation: -"),
            'dcf_value': tk.StringVar(value="DCF Value: -"),
            'dcf_discount': tk.StringVar(value="DCF Discount: -")
        }
        
        for var in self.result_vars.values():
            tk.Label(self.results_frame, textvariable=var, anchor="w", justify=tk.LEFT).pack(fill=tk.X, pady=2)

        # Chart area
        self.chart_frame = tk.Frame(self.display_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = None
        self.fig = None

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")])
        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            df.columns = [str(col).strip() for col in df.columns]
            date_col = [col for col in df.columns if "date" in col.lower()][0]
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df.dropna(subset=[date_col])
            df = df.sort_values(by=date_col)

            self.data = df[[date_col, 'Price', 'PE Ratio', 'Earning']].copy()
            self.data.columns = ['Date', 'Price', 'PE', 'Earnings']
            self.file_label.config(text=f"Loaded: {file_path.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

    def calculate_dcf(self, earnings, growth_rate, terminal_rate, discount_rate):
        """Calculate DCF valuation"""
        try:
            growth_rate = float(growth_rate)/100
            terminal_rate = float(terminal_rate)/100
            discount_rate = float(discount_rate)/100
            
            # Use last available earnings as base
            fcf = earnings.iloc[-1]
            
            # 5-year projection
            years = 5
            cash_flows = []
            for year in range(1, years+1):
                cash_flows.append(fcf * (1 + growth_rate)**year / (1 + discount_rate)**year)
            
            # Terminal value
            terminal_value = (cash_flows[-1] * (1 + terminal_rate)) / (discount_rate - terminal_rate)
            terminal_value_discounted = terminal_value / (1 + discount_rate)**years
            
            dcf_value = sum(cash_flows) + terminal_value_discounted
            return dcf_value
        except:
            return None

    def plot_data(self):
        if self.data is None:
            messagebox.showerror("Error", "No data loaded.")
            return

        if not self.validate_inputs():
            return

        df = self.data.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.dropna(subset=['Price', 'Earnings'])

        # Get parameters
        cagr = float(self.cagr_entry.get())/100
        pe_min = float(self.pe_min.get())
        pe_avg = float(self.pe_avg.get())
        pe_max = float(self.pe_max.get())
        
        # Calculate valuations
        base_earning = df['Earnings'].iloc[-5:].mean()
        df['Earnings_Forecast'] = [base_earning * ((1 + cagr) ** i) for i in range(len(df))]
        df['FairValue_CAGR'] = df['Earnings_Forecast'] * pe_avg
        
        # PE bands
        df['PE_Min'] = df['Earnings'] * pe_min
        df['PE_Avg'] = df['Earnings'] * pe_avg
        df['PE_Max'] = df['Earnings'] * pe_max
        
        # DCF calculation
        dcf_value = self.calculate_dcf(
            df['Earnings'],
            self.dcf_growth.get(),
            self.dcf_terminal.get(),
            self.dcf_discount.get()
        )
        
        # Regression
        reg = self.reg_type.get()
        if reg != "None":
            X = df['Date'].map(datetime.toordinal).values.reshape(-1, 1)
            y = np.log(df['Price']) if reg == "Log" else df['Price']
            model = LinearRegression().fit(X, y)
            trend = model.predict(X)
            df['Regression'] = np.exp(trend) if reg == "Log" else trend

        # Update results panel
        latest = df.iloc[-1]
        current_price = latest['Price']
        cagr_fair_value = latest['FairValue_CAGR']
        cagr_discount = ((cagr_fair_value - current_price) / cagr_fair_value) * 100
        
        pe_valuation = f"{latest['PE_Min']:.2f}-{latest['PE_Avg']:.2f}-{latest['PE_Max']:.2f}"
        
        self.result_vars['current_price'].set(f"Current Price: ₹{current_price:.2f}")
        self.result_vars['cagr_fair_value'].set(f"CAGR Fair Value: ₹{cagr_fair_value:.2f}")
        self.result_vars['cagr_discount'].set(f"CAGR Discount: {cagr_discount:.1f}%")
        self.result_vars['pe_valuation'].set(f"PE Valuation: ₹{pe_valuation}")
        
        if dcf_value:
            dcf_discount = ((dcf_value - current_price) / dcf_value) * 100
            self.result_vars['dcf_value'].set(f"DCF Value: ₹{dcf_value:.2f}")
            self.result_vars['dcf_discount'].set(f"DCF Discount: {dcf_discount:.1f}%")
        else:
            self.result_vars['dcf_value'].set("DCF Value: Calculation failed")
            self.result_vars['dcf_discount'].set("")

        # Plot
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(df['Date'], df['Price'], label="Actual Price", color="black", linewidth=2)
        ax.plot(df['Date'], df['FairValue_CAGR'], label="Fair Value (CAGR)", linestyle='--', color="blue")
        ax.plot(df['Date'], df['PE_Min'], label="PE Min", linestyle=':', color="green")
        ax.plot(df['Date'], df['PE_Avg'], label="PE Avg", linestyle='--', color="orange")
        ax.plot(df['Date'], df['PE_Max'], label="PE Max", linestyle=':', color="red")

        if reg != "None":
            ax.plot(df['Date'], df['Regression'], label=f"{reg} Regression", linestyle="-.", color="purple")

        # Annotations
        ax.axhline(current_price, color='grey', linestyle='dotted')
        ax.annotate(f"Current: ₹{current_price:.2f}", 
                   xy=(df['Date'].iloc[-1], current_price), 
                   xytext=(-100, 10),
                   textcoords='offset points', 
                   arrowprops=dict(arrowstyle="->"), 
                   color="black")

        ax.annotate(f"Fair Value: ₹{cagr_fair_value:.2f}\nDiscount: {cagr_discount:.1f}%",
                   xy=(df['Date'].iloc[-1], cagr_fair_value), 
                   xytext=(-120, -60),
                   textcoords='offset points', 
                   arrowprops=dict(arrowstyle="->"), 
                   color="blue")

        ax.set_title("Valuation Analysis")
        ax.set_ylabel("Price (₹)")
        ax.legend(loc='upper left')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Clear previous chart
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.fig = fig

    def validate_inputs(self):
        try:
            float(self.cagr_entry.get())
            float(self.pe_min.get())
            float(self.pe_avg.get())
            float(self.pe_max.get())
            float(self.dcf_growth.get())
            float(self.dcf_terminal.get())
            float(self.dcf_discount.get())
            return True
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all inputs")
            return False

    def save_chart(self):
        if hasattr(self, 'fig'):
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                    filetypes=[("PNG Image", "*.png"),
                                                               ("JPEG Image", "*.jpg"),
                                                               ("PDF Document", "*.pdf")])
            if file_path:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Saved", f"Chart saved as: {file_path}")
        else:
            messagebox.showerror("Error", "Generate the chart before saving.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ValuationGUI(root)
    root.mainloop()