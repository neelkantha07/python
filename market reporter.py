

def load_folder():
    global folder_path, file_results
    folder_path = filedialog.askdirectory()
    if folder_path:
        status_label.config(text=f"Loaded folder: {folder_path}")
        file_results = analyze_all_files()
        update_file_dropdown()
        display_summary()

def analyze_all_files():
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder first.")
        return
    
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not csv_files:
        messagebox.showerror("Error", "No CSV files found in the selected folder.")
        return
    
    period = period_var11.get()
    interval = interval_var11.get()
    
    all_results = {}
    
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        tickers = pd.read_csv(file_path, header=None)[0].tolist()
        tickers = [ticker + '.NS' for ticker in tickers]
        
        overbought = []
        oversold = []
        gaining_strength = []
        losing_strength = []
        
        listbox_data = {
            "Overbought": [],
            "Oversold": [],
            "Gaining Strength": [],
            "Losing Strength": []
        }
        
        for ticker in tickers:
            try:
                data = yf.download(ticker, period=period, interval=interval)
                data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
                
                if len(data) < 3:
                    continue
                
                current_rsi = data['RSI'].iloc[-1]
                previous_rsi = data['RSI'].iloc[-2]
                two_days_ago_rsi = data['RSI'].iloc[-3]
                
                if current_rsi > 70:
                    category = "Overbought"
                    overbought.append((ticker, current_rsi))
                elif current_rsi < 30:
                    category = "Oversold"
                    oversold.append((ticker, current_rsi))
                else:
                    if current_rsi > previous_rsi and previous_rsi > two_days_ago_rsi:
                        category = "Gaining Strength"
                        gaining_strength.append((ticker, current_rsi))
                    elif current_rsi < previous_rsi and previous_rsi < two_days_ago_rsi:
                        category = "Losing Strength"
                        losing_strength.append((ticker, current_rsi))
                    else:
                        category = None
                
                if category:
                    listbox_data[category].append((ticker, current_rsi))
            
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
        
        # Sort data in descending order of RSI
        for category in listbox_data:
            listbox_data[category].sort(key=lambda x: x[1], reverse=True)
        
        total_tickers = len(tickers)
        overbought_count = len(overbought)
        oversold_count = len(oversold)
        gaining_strength_count = len(gaining_strength)
        losing_strength_count = len(losing_strength)
        
        overbought_percentage = (overbought_count / total_tickers * 100) if total_tickers > 0 else 0
        oversold_percentage = (oversold_count / total_tickers * 100) if total_tickers > 0 else 0
        gaining_strength_percentage = (gaining_strength_count / total_tickers * 100) if total_tickers > 0 else 0
        losing_strength_percentage = (losing_strength_count / total_tickers * 100) if total_tickers > 0 else 0
        
        summary = (
            f"File: {csv_file}\n"
            f"Overbought: {overbought_count} ({overbought_percentage:.2f}%)\n"
            f"Oversold: {oversold_count} ({oversold_percentage:.2f}%)\n"
            f"Gaining Strength: {gaining_strength_count} ({gaining_strength_percentage:.2f}%)\n"
            f"Losing Strength: {losing_strength_count} ({losing_strength_percentage:.2f}%)\n"
            f"{'-'*50}\n"
        )
        
        all_results[csv_file] = {
            "summary": summary,
            "data": listbox_data
        }
    
    return all_results

def update_file_dropdown():
    if not folder_path:
        return
    
    csv_files = list(file_results.keys())
    if not csv_files:
        messagebox.showerror("Error", "No CSV files found.")
        return
    
    file_dropdown_menu['menu'].delete(0, 'end')
    for csv_file in csv_files:
        file_dropdown_menu['menu'].add_command(label=csv_file, command=tk._setit(selected_file_var, csv_file))
    
    selected_file_var.set(csv_files[0] if csv_files else "")

def display_summary():
    summary_text.delete(1.0, tk.END)
    
    # Configure tags for formatting
    summary_text.tag_configure("heading", font=('Helvetica', 12, 'bold'), foreground='blue')
    summary_text.tag_configure("file_name", font=('Helvetica', 10, 'bold'), foreground='dark green')
    summary_text.tag_configure("percentage", font=('Helvetica', 10, 'bold'), foreground='dark orange')
    summary_text.tag_configure("regular", font=('Helvetica', 10))
    
    summary_text.insert(tk.END, "===== Summary Report =====\n\n", "heading")
    
    for file_name, result in file_results.items():
        summary_text.insert(tk.END, f"File: {file_name}\n", "file_name")
        summary_text.insert(tk.END, "-" * 50 + "\n", "regular")
        summary_text.insert(tk.END, f"Overbought: {len(result['data']['Overbought'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Overbought: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Oversold: {len(result['data']['Oversold'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Oversold: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Gaining Strength: {len(result['data']['Gaining Strength'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Gaining Strength: ')[1].split(' (')[1].split('%)')[0]}%)\n", "percentage")
        summary_text.insert(tk.END, f"Losing Strength: {len(result['data']['Losing Strength'])} ", "regular")
        summary_text.insert(tk.END, f"({result['summary'].split('Losing Strength: ')[1].split(' (')[1].split('%)')[0]}%)\n\n", "percentage")
    
    summary_text.insert(tk.END, "=" * 50 + "\n", "regular")

def update_criteria(*args):
    file_name = selected_file_var.get()
    if not file_name or file_name not in file_results:
        return
    
    listbox_data = file_results[file_name]["data"]
    
    # Insert data into listboxes
    for category in listbox_widgets:
        listbox = listbox_widgets[category]
        listbox.delete(0, tk.END)
        for ticker, rsi in listbox_data.get(category, []):
            listbox.insert(tk.END, f"{ticker}: RSI={rsi:.2f}")

def save_report():
    if not file_results:
        messagebox.showerror("Error", "No data to save.")
        return
    
    save_folder = filedialog.askdirectory()
    if not save_folder:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(save_folder, f"RSI_Report_{timestamp}.json")
    
    with open(report_path, 'w') as f:
        json.dump(file_results, f, indent=4)
    
    messagebox.showinfo("Saved", f"Report saved to {report_path}")

def load_report():
    global file_results
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        return
    
    with open(file_path, 'r') as f:
        file_results = json.load(f)
    
    update_file_dropdown()
    display_summary()



def display_comparison(file1, file2):
    compare_text.delete(1.0, tk.END)
    
    with open(file1, 'r') as f:
        report1 = json.load(f)
    
    with open(file2, 'r') as f:
        report2 = json.load(f)
    
    differences = {}
    
    all_files = set(report1.keys()).union(report2.keys())
    
    for file_name in all_files:
        diff = {}
        data1 = report1.get(file_name, {}).get('data', {})
        data2 = report2.get(file_name, {}).get('data', {})
        
        for category in ["Overbought", "Oversold", "Gaining Strength", "Losing Strength"]:
            tickers1 = set(ticker for ticker, _ in data1.get(category, []))
            tickers2 = set(ticker for ticker, _ in data2.get(category, []))
            
            diff[category] = {
                "Added": list(tickers2 - tickers1),
                "Removed": list(tickers1 - tickers2)
            }
        
        if diff:
            differences[file_name] = diff
    
    compare_text.insert(tk.END, "===== Comparison Report =====\n\n")
    
    for file_name, diff in differences.items():
        compare_text.insert(tk.END, f"File: {file_name}\n", "file_name")
        compare_text.insert(tk.END, "-" * 50 + "\n", "regular")
        
        for category, changes in diff.items():
            compare_text.insert(tk.END, f"{category}:\n", "heading")
            if changes["Added"]:
                compare_text.insert(tk.END, "  Added:\n", "regular")
                for ticker in changes["Added"]:
                    compare_text.insert(tk.END, f"    {ticker}\n", "regular")
            if changes["Removed"]:
                compare_text.insert(tk.END, "  Removed:\n", "regular")
                for ticker in changes["Removed"]:
                    compare_text.insert(tk.END, f"    {ticker}\n", "regular")
            compare_text.insert(tk.END, "-" * 50 + "\n", "regular")
    
    compare_text.insert(tk.END, "=" * 50 + "\n", "regular")

def compare_reports():
    file1_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Select first report")
    file2_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Select second report")
    
    if not file1_path or not file2_path:
        return
    
    display_comparison(file1_path, file2_path)



# GUI Setup


folder_path = None
file_results = {}

# Compare Report Display
compare_frame = tk.Frame(tab_market_view)
compare_frame.grid(row=7, column=0, columnspan=3, pady=10)

compare_text = tk.Text(compare_frame, wrap=tk.WORD, height=15, width=100)
compare_text.grid(row=0, column=0, columnspan=3, pady=10)

# Folder selection
file_label = tk.Label(tab_market_view, text="Select Folder with CSV files:")
file_label.grid(row=0, column=0, columnspan=2, pady=10)

file_button = tk.Button(tab_market_view, text="Browse", command=load_folder)
file_button.grid(row=0, column=2, pady=10)

status_label = tk.Label(tab_market_view, text="")
status_label.grid(row=1, column=0, columnspan=3, pady=5)

# Save, Load, Compare buttons
save_button = tk.Button(tab_market_view, text="Save Report", command=save_report)
save_button.grid(row=3, column=3, padx=10, pady=5)

load_button = tk.Button(tab_market_view, text="Load Report", command=load_report)
load_button.grid(row=3, column=4, padx=10, pady=5)

compare_button = tk.Button(tab_market_view, text="Compare Reports", command=compare_reports)
compare_button.grid(row=3, column=2, padx=10, pady=5)

# File dropdown
selected_file_var = tk.StringVar(tab_market_view)
selected_file_var.set("Select a file")
file_dropdown_label = tk.Label(tab_market_view, text="Select CSV file:")
file_dropdown_label.grid(row=2, column=0, pady=5)

file_dropdown_menu = tk.OptionMenu(tab_market_view, selected_file_var, [])
file_dropdown_menu.grid(row=2, column=1, pady=5)
selected_file_var.trace("w", update_criteria)  # Update criteria when selection changes

# Period dropdown
period_var11 = tk.StringVar(tab_market_view)
period_var11.set("1y")  # default value
period_label = tk.Label(tab_market_view, text="Select Period:")
period_label.grid(row=3, column=0, pady=5)

period_menu = tk.OptionMenu(tab_market_view, period_var11, "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
period_menu.grid(row=3, column=1, pady=5)

# Interval dropdown
interval_var11 = tk.StringVar(tab_market_view)
interval_var11.set("1d")  # default value
interval_label = tk.Label(tab_market_view, text="Select Interval:")
interval_label.grid(row=4, column=0, pady=5)

interval_menu = tk.OptionMenu(tab_market_view, interval_var11, "1m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo")
interval_menu.grid(row=4, column=1, pady=5)

# Summary Text
summary_text = tk.Text(tab_market_view, wrap=tk.WORD, height=15, width=100)
summary_text.grid(row=5, column=0, columnspan=3, pady=10)

# Listboxes for criteria
criteria_frame = tk.Frame(tab_market_view)
criteria_frame.grid(row=6, column=0, columnspan=3, pady=10)

categories = ["Overbought", "Oversold", "Gaining Strength", "Losing Strength"]
listbox_widgets = {}

for idx, category in enumerate(categories):
    tk.Label(criteria_frame, text=category, font=('Helvetica', 10, 'bold')).grid(row=0, column=idx, padx=10, pady=5)
    listbox = Listbox(criteria_frame, width=30, height=10)
    listbox.grid(row=1, column=idx, padx=10, pady=5)
    listbox_widgets[category] = listbox


