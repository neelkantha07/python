# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 11:43:28 2024

@author: Mahadev
"""

import tkinter as tk
from tkinter import ttk, messagebox
from functions import (
    check_20_day_high,
    check_20_day_low,
    check_higher_highs,
    check_bollinger_band_crossings,
    check_double_bottom,
    check_bollinger_inside_keltner,
    plot_chart
)

# Global variables
chart_type = "candlestick"

# Create the main window
root = tk.Tk()
root.title("Stock Analysis")

# Create a notebook (tabs)
notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

notebook.add(tab1, text="Stock Analysis")
notebook.add(tab2, text="Introduction")
notebook.pack(expand=1, fill="both")

# Tab 1: Stock Analysis
frame1 = tk.Frame(tab1)
frame1.pack(padx=10, pady=10)

# Listbox for displaying results
listbox = tk.Listbox(frame1, selectmode=tk.SINGLE, width=50, height=10)
listbox.pack(side=tk.LEFT, padx=(0, 10))

# Scrollbar for Listbox
scrollbar = tk.Scrollbar(frame1, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

# Button to check 20-day high
btn_check_high = tk.Button(frame1, text="Check 20-day High", command=lambda: listbox.insert(tk.END, *check_20_day_high()))
btn_check_high.pack(pady=5)

# Button to check 20-day low
btn_check_low = tk.Button(frame1, text="Check 20-day Low", command=lambda: listbox.insert(tk.END, *check_20_day_low()))
btn_check_low.pack(pady=5)

# Button to check higher highs
btn_check_highs = tk.Button(frame1, text="Check Higher Highs", command=lambda: listbox.insert(tk.END, *check_higher_highs()))
btn_check_highs.pack(pady=5)

# Button to check Bollinger Bands crossings
btn_check_bb = tk.Button(frame1, text="Check Bollinger Band Crossings", command=lambda: listbox.insert(tk.END, *check_bollinger_band_crossings()))
btn_check_bb.pack(pady=5)

# Button to check double bottom
btn_check_double_bottom = tk.Button(frame1, text="Check Double Bottom", command=lambda: listbox.insert(tk.END, *check_double_bottom()))
btn_check_double_bottom.pack(pady=5)

# Button to check Bollinger Bands inside Keltner Channel
btn_check_bb_kc = tk.Button(frame1, text="Check Bollinger Inside Keltner", command=lambda: listbox.insert(tk.END, *check_bollinger_inside_keltner()))
btn_check_bb_kc.pack(pady=5)

# Frame for plotting charts
chart_frame = tk.Frame(tab1)
chart_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Plot button
plot_btn = tk.Button(frame1, text="Plot Chart", command=lambda event=None: plot_chart(event, listbox, chart_frame))
plot_btn.pack(pady=5)

# Tab 2: Introduction
intro_label = tk.Label(tab2, text="Welcome to the Stock Analysis Application. Use the tabs to analyze stock data.")
intro_label.pack(padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
