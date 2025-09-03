# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 21:23:07 2025

@author: Mahadev
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

DB_FILE = "mf_portfolio.db"
TABLE_NAME = "monthly_holdings"

# === Database Setup ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        [Name of the Instrument] TEXT,
        ISIN TEXT,
        [Industry / Rating] TEXT,
        Quantity REAL,
        [Market/Fair Value  (Rs. in Lakhs)] REAL,
        [% to Net  Assets] REAL,
        date TEXT
    )
    """)
    conn.commit()
    conn.close()

# === File Upload ===
def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        try:
            df = pd.read_excel(file_path)
            df.columns = [col.strip() for col in df.columns]
            df = df[[
                'Name of the Instrument', 'ISIN', 'Industry / Rating',
                'Quantity', 'Market/Fair Value  (Rs. in Lakhs)', '% to Net  Assets']]
            df['date'] = datetime.today().strftime('%Y-%m-%d')

            conn = sqlite3.connect(DB_FILE)
            df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
            conn.close()
            messagebox.showinfo("Success", "Data uploaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# === Comparison Logic ===
def compare_dates(date1, date2):
    conn = sqlite3.connect(DB_FILE)
    df1 = pd.read_sql(f"SELECT * FROM {TABLE_NAME} WHERE date = ?", conn, params=(date1,))
    df2 = pd.read_sql(f"SELECT * FROM {TABLE_NAME} WHERE date = ?", conn, params=(date2,))
    conn.close()

    merged = pd.merge(df1, df2, on='ISIN', how='outer', suffixes=('_new', '_old'))
    summary = {
        'New Entries': merged[merged['% to Net  Assets_old'].isna()],
        'Removed': merged[merged['% to Net  Assets_new'].isna()],
        'Increased': merged[(merged['% to Net  Assets_new'] > merged['% to Net  Assets_old']) & merged['% to Net  Assets_old'].notna()],
        'Decreased': merged[(merged['% to Net  Assets_new'] < merged['% to Net  Assets_old']) & merged['% to Net  Assets_old'].notna()]
    }
    return summary

# === Show Comparison ===
def run_comparison():
    date1 = date1_cb.get()
    date2 = date2_cb.get()
    if date1 and date2:
        summary = compare_dates(date1, date2)
        for key, df in summary.items():
            output.insert(tk.END, f"\n--- {key} ---\n")
            output.insert(tk.END, df[['Name of the Instrument_new', '% to Net  Assets_new', '% to Net  Assets_old']].to_string(index=False))
            output.insert(tk.END, "\n")
    else:
        messagebox.showwarning("Warning", "Select two valid dates")

# === GUI Setup ===
init_db()
root = tk.Tk()
root.title("Mutual Fund Portfolio Tracker")

notebook = ttk.Notebook(root)

# === Upload Tab ===
upload_tab = ttk.Frame(notebook)
upload_btn = ttk.Button(upload_tab, text="Upload Monthly Excel File", command=upload_file)
upload_btn.pack(pady=20)
notebook.add(upload_tab, text="Upload Data")

# === Analysis Tab ===
analysis_tab = ttk.Frame(notebook)
date1_cb = ttk.Combobox(analysis_tab)
date2_cb = ttk.Combobox(analysis_tab)
run_btn = ttk.Button(analysis_tab, text="Compare", command=run_comparison)
output = tk.Text(analysis_tab, height=30, width=120)

date1_cb.pack(pady=5)
date2_cb.pack(pady=5)
run_btn.pack(pady=5)
output.pack(pady=5)

notebook.add(analysis_tab, text="Compare Data")
notebook.pack(expand=True, fill='both')

# === Load available dates into combo boxes ===
def refresh_dates():
    conn = sqlite3.connect(DB_FILE)
    dates = pd.read_sql(f"SELECT DISTINCT date FROM {TABLE_NAME} ORDER BY date DESC", conn)['date'].tolist()
    conn.close()
    date1_cb['values'] = dates
    date2_cb['values'] = dates

refresh_dates()
root.mainloop()
