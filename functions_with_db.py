#!/usr/bin/env python3
"""
tk_screener_scrollable_chart_full.py

Fixed: ScreenerThread db_path parameter handling
Added feature: Ticker Notes system with persistent storage in database.
Users can now add, edit, and view notes for each ticker.
"""
import os
import sqlite3
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import yfinance as yf
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

matplotlib.use("TkAgg")

# ---------------- Config ----------------
DATA_DIR = "E:\Ebooks\stovks\Kimiya Vidya_17\Data\data_db_day"
DEFAULT_DB = os.path.join(DATA_DIR, "market_data.db")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- Helpers / Indicators ----------------
def table_name_for_ticker(ticker: str) -> str:
    return ticker.upper().replace(".", "_").replace("-", "_")


def create_raw_table(conn_local, ticker: str):
    c = conn_local.cursor()
    tbl = table_name_for_ticker(ticker)
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS '{tbl}' (
            date TEXT PRIMARY KEY,
            open REAL, high REAL, low REAL, close REAL, volume REAL
        )
    """)
    conn_local.commit()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi


def bollinger_bands(close: pd.Series, n: int = 20, n_std: int = 2):
    mid = close.rolling(window=n).mean()
    std = close.rolling(window=n).std()
    upper = mid + n_std * std
    lower = mid - n_std * std
    return upper, mid, lower

# --- New: Keltner Channels helper ---
def keltner_channels(df, ema_period: int = 20, atr_period: int = 10, mult: float = 1.5):
    """
    Compute Keltner upper/mid/lower using typical price EMA and ATR.
    Expects df with lowercase columns: 'high','low','close'.
    """
    typical_price = (df['high'] + df['low'] + df['close']) / 3.0
    ema_mid = typical_price.ewm(span=ema_period, adjust=False).mean()

    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=atr_period).mean()

    keltner_upper = ema_mid + atr * mult
    keltner_lower = ema_mid - atr * mult
    return keltner_upper, ema_mid, keltner_lower

# ---------------- Threads (Download & Screener) ----------------
class DownloadThread(threading.Thread):
    def __init__(self, tickers, period, interval, db_path, status_cb, finished_cb):
        super().__init__(daemon=True)
        self.tickers = tickers
        self.period = period
        self.interval = interval
        self.db_path = db_path
        self.status_cb = status_cb
        self.finished_cb = finished_cb
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        conn_local = sqlite3.connect(self.db_path, check_same_thread=False)
        cur_local = conn_local.cursor()
        try:
            total = len(self.tickers)
            for i, raw in enumerate(self.tickers, start=1):
                if self._stop:
                    break
                t = raw.strip().upper()
                if not t.endswith(".NS"):
                    t = t + ".NS"
                self.status_cb(f"[{i}/{total}] Downloading {t} ...")
                try:
                    df = yf.download(t, period=self.period, interval=self.interval, progress=False, auto_adjust=False)
                except Exception as e:
                    print(f"[ERROR] yfinance download failed for {t}: {e}")
                    traceback.print_exc()
                    self.status_cb(f"Download error {t} (see console)")
                    continue
                if df is None or df.empty:
                    self.status_cb(f"No data for {t}")
                    continue
                try:
                    df.rename(columns=lambda c: c.capitalize(), inplace=True)
                    create_raw_table(conn_local, t)
                    tbl = table_name_for_ticker(t)
                    cur_local.execute(f"SELECT MAX(date) FROM '{tbl}'")
                    last = cur_local.fetchone()[0]
                    rows = []
                    if not isinstance(df.index, pd.DatetimeIndex):
                        df.index = pd.to_datetime(df.index)
                    df.sort_index(inplace=True)
                    for idx, row in df.iterrows():
                        date_str = idx.strftime("%Y-%m-%d %H:%M:%S")
                        if last is None or date_str > last:
                            rows.append((date_str, float(row['Open']), float(row['High']), float(row['Low']),
                                         float(row['Close']), float(row['Volume'])))
                    if rows:
                        cur_local.executemany(f"INSERT OR REPLACE INTO '{tbl}' (date, open, high, low, close, volume) VALUES (?,?,?,?,?,?)", rows)
                        conn_local.commit()
                    self.status_cb(f"Stored {t} ({len(rows)} new rows)")
                except Exception as e:
                    print(f"[ERROR] storing data for {t}: {e}")
                    traceback.print_exc()
                    self.status_cb(f"DB write error {t} (see console)")
                    continue
            self.status_cb("Download finished")
            self.finished_cb()
        except Exception as e:
            print("[CRITICAL] DownloadThread crashed:", e)
            traceback.print_exc()
            self.status_cb("Download crashed (see console)")
            self.finished_cb()
        finally:
            conn_local.close()


class ScreenerThread(threading.Thread):
    def __init__(self, tickers, period, interval, streak_days, db_path, status_cb, finished_cb, result_cb):
        super().__init__(daemon=True)
        self.tickers = tickers
        self.period = period
        self.interval = interval
        self.streak_days = streak_days
        self.db_path = db_path  # Fixed: properly assign to instance variable
        self.status_cb = status_cb
        self.finished_cb = finished_cb
        self.result_cb = result_cb
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            # download index for RS
            index_sym = "^NSEI"
            try:
                idx_df = yf.download(index_sym, period=self.period, interval=self.interval, progress=False, auto_adjust=False)
                if idx_df is not None and not idx_df.empty:
                    idx_df.rename(columns=lambda c: c.capitalize(), inplace=True)
                    if 'Close' in idx_df.columns:
                        idx_df.index = pd.to_datetime(idx_df.index)
                        idx_df['rsi'] = compute_rsi(idx_df['Close'])
                else:
                    idx_df = None
            except Exception as e:
                print("[WARN] index download failed:", e)
                traceback.print_exc()
                idx_df = None

            conn_local = sqlite3.connect(self.db_path)
            cur_local = conn_local.cursor()
            # include the new squeeze buckets
            buckets = {
                'Up Squeeze': [],
                'Down Squeeze': [],
                'Overbought':[], 'Oversold':[], 'Gaining Streak':[], 'Losing Streak':[], 'RS':[], 'Bollinger Break':[], 'Top Gainers':[]
            }

            total = len(self.tickers)
            for i, raw in enumerate(self.tickers, start=1):
                if self._stop:
                    break
                t = raw.strip().upper()
                if not t.endswith(".NS"):
                    t = t + ".NS"
                self.status_cb(f"[{i}/{total}] Loading {t} from DB ...")
                try:
                    tbl = table_name_for_ticker(t)
                    cur_local.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
                    if cur_local.fetchone() is None:
                        continue
                    df = pd.read_sql(f"SELECT * FROM '{tbl}' ORDER BY date", conn_local)
                    if df.empty:
                        continue
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    df.columns = [c.lower() for c in df.columns]
                    if not all(col in df.columns for col in ['open','high','low','close','volume']):
                        continue

                    # compute indicators (in-memory)
                    if 'rsi' not in df.columns or df['rsi'].isna().all():
                        df['rsi'] = compute_rsi(df['close'])
                    df['ema10'] = df['close'].ewm(span=10, adjust=False).mean()
                    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
                    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
                    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
                    u,m,l = bollinger_bands(df['close'])
                    df['bb_upper'] = u; df['bb_mid'] = m; df['bb_lower'] = l

                    # --- Compute Keltner Channels and attach ---
                    try:
                        ku, km, kl = keltner_channels(df)
                        df['kc_upper'] = ku; df['kc_mid'] = km; df['kc_lower'] = kl
                    except Exception as e:
                        # keltner failure should not break screener
                        print(f"[WARN] keltner failed for {t}: {e}")
                        traceback.print_exc()

                    df['pct_day'] = (df['close'].iloc[-1]-df['close'].iloc[-2])/df['close'].iloc[-2] * 100.0

                    # streaks
                    diff = df['close'].diff()
                    consec_up = 0
                    for v in reversed((diff > 0).fillna(False).tolist()):
                        if v: consec_up += 1
                        else: break
                    consec_down = 0
                    for v in reversed((diff < 0).fillna(False).tolist()):
                        if v: consec_down += 1
                        else: break

                    last = df.iloc[-1]
                    rsi_val = float(last['rsi']) if not pd.isna(last['rsi']) else None
                    pct_last = float(last['pct_day']) if 'pct_day' in df.columns else 0.0
                    bb_break = int(last['close'] > last['bb_upper']) if 'bb_upper' in df.columns else 0

                    # ----------------- SQUEEZE (BEFORE other checks) -----------------
                    squeeze_msg = None
                    # Up Squeeze: Bollinger upper > Keltner upper
                    try:
                        if (
                            'bb_upper' in df.columns and 'kc_upper' in df.columns
                            and len(df) >= 2
                            and pd.notna(df['bb_upper'].iloc[-1]) and pd.notna(df['kc_upper'].iloc[-1])
                            and pd.notna(df['bb_upper'].iloc[-2]) and pd.notna(df['kc_upper'].iloc[-2])
                        ):
                            # Last bar outside, previous inside
                            if df['bb_upper'].iloc[-1] > df['kc_upper'].iloc[-1] and df['bb_upper'].iloc[-2] < df['kc_upper'].iloc[-2] and df['close'].iloc[-1]>df['kc_upper'].iloc[-1] :
                                up_delta = float(df['bb_upper'].iloc[-1] - df['kc_upper'].iloc[-1])
                                buckets['Up Squeeze'].append((t, up_delta, float(last['close'])))
                                squeeze_msg = f"UpS Break Δ:{up_delta:+.2f}"
                    except Exception as e:
                        print(f"[WARN] up squeeze breakout check failed for {t}: {e}")
                        traceback.print_exc()

                    # Down Squeeze Breakout: Bollinger lower crosses below Keltner lower
                    try:
                        if (
                            'bb_lower' in df.columns and 'kc_lower' in df.columns
                            and len(df) >= 2
                            and pd.notna(df['bb_lower'].iloc[-1]) and pd.notna(df['kc_lower'].iloc[-1])
                            and pd.notna(df['bb_lower'].iloc[-2]) and pd.notna(df['kc_lower'].iloc[-2])
                        ):
                            # Last bar outside, previous inside
                            if df['bb_lower'].iloc[-1] < df['kc_lower'].iloc[-1] and df['bb_lower'].iloc[-2] > df['kc_lower'].iloc[-2] and  df['close'].iloc[-1]<df['kc_upper'].iloc[-1]:
                                down_delta = float(df['bb_lower'].iloc[-1] - df['kc_lower'].iloc[-1])
                                buckets['Down Squeeze'].append((t, down_delta, float(last['close'])))
                                if squeeze_msg:
                                    squeeze_msg += f" | DownS Break Δ:{down_delta:+.2f}"
                                else:
                                    squeeze_msg = f"DownS Break Δ:{down_delta:+.2f}"
                    except Exception as e:
                        print(f"[WARN] down squeeze breakout check failed for {t}: {e}")
                        traceback.print_exc()

                    if squeeze_msg:
                        # update status to show current computation stat for this ticker
                        self.status_cb(f"[{i}/{total}] {t} {squeeze_msg}")

                    # ----------------- ORIGINAL CHECKS -----------------
                    # Overbought/Oversold
                    if rsi_val is not None and rsi_val >= 70:
                        buckets['Overbought'].append((t, rsi_val, consec_up))
                    if rsi_val is not None and rsi_val <= 30:
                        buckets['Oversold'].append((t, rsi_val, consec_up))

                    # Gaining/Losing
                    if consec_up >= self.streak_days:
                        buckets['Gaining Streak'].append((t, rsi_val, consec_up))
                    if consec_down >= self.streak_days:
                        buckets['Losing Streak'].append((t, rsi_val, consec_down))

                    # Bollinger break
                    if bb_break:
                        buckets['Bollinger Break'].append((t, rsi_val, pct_last))

                    # Top Gainers
                    if pct_last is not None and pct_last > 0.0:
                        buckets['Top Gainers'].append((t, pct_last, rsi_val))

                    # Relative Strength: align stock.rsi with index.rsi
                    if idx_df is not None and 'rsi' in idx_df.columns:
                        try:
                            stock_rsi = df['rsi'].dropna()
                            index_rsi = idx_df['rsi'].dropna()
                            if not stock_rsi.empty and not index_rsi.empty:
                                stock_rsi_al, index_rsi_al = stock_rsi.align(index_rsi, join='inner')
                                if len(stock_rsi_al) > 0 and stock_rsi_al.iloc[-1] > index_rsi_al.iloc[-1]:
                                    rs_val = float(stock_rsi_al.iloc[-1] - index_rsi_al.iloc[-1])
                                    buckets['RS'].append((t, rs_val, rsi_val))
                        except Exception as e:
                            print(f"[WARN] RS alignment failed for {t}: {e}")
                            traceback.print_exc()
                except Exception as e:
                    print(f"[ERROR] screener loop failed for {t}: {e}")
                    traceback.print_exc()
                    continue

            # send back results
            self.result_cb(buckets)
            self.status_cb("Screener finished")
            self.finished_cb()
        except Exception as e:
            print("[CRITICAL] ScreenerThread crashed:", e)
            traceback.print_exc()
            self.status_cb("Screener crashed (see console)")
            self.finished_cb()
        finally:
            try:
                conn_local.close()
            except:
                pass

# ---------------- Ticker Notes System ----------------
class TickerNotes:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize the notes table in the database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ticker_notes (
                ticker TEXT PRIMARY KEY,
                notes TEXT,
                last_updated TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    def get_notes(self, ticker):
        """Get notes for a specific ticker"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT notes FROM ticker_notes WHERE ticker = ?", (ticker,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else ""
        
    def save_notes(self, ticker, notes):
        """Save notes for a specific ticker"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(
            "INSERT OR REPLACE INTO ticker_notes (ticker, notes, last_updated) VALUES (?, ?, ?)",
            (ticker, notes, now)
        )
        conn.commit()
        conn.close()

# ---------------- Tkinter UI (scrollable main frame) ----------------
class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame that holds the app content.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0)
        vscroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.interior = ttk.Frame(canvas)
        self.interior_id = canvas.create_window((0,0), window=self.interior, anchor="nw")
        def _configure_interior(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.interior.bind("<Configure>", _configure_interior)
        def _configure_canvas(event):
            canvas.itemconfig(self.interior_id, width=event.width)
        canvas.bind("<Configure>", _configure_canvas)
        # mousewheel scroll for Windows and Mac/Linux
        def _on_mousewheel(event):
            # event.delta works on Windows; on Linux use event.num
            try:
                if event.num == 4 or event.delta > 0:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5 or event.delta < 0:
                    canvas.yview_scroll(1, "units")
            except Exception:
                pass
        # bind to wheel events
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

# ---------------- Main App ----------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Ticker Screener - JAI MA SARADA")
        root.geometry("1360x820")

        # database path (selectable)
        self.database_path = DEFAULT_DB

        # main read connection (for quick checks; threads will open their own)
        os.makedirs(DATA_DIR, exist_ok=True)
        self.conn = sqlite3.connect(self.database_path, check_same_thread=False)
        self.cur = self.conn.cursor()

        # Initialize notes system
        self.notes_manager = TickerNotes(self.database_path)

        # top-level scrollable frame
        self.scrollable = ScrollableFrame(root)
        self.scrollable.pack(fill="both", expand=True)

        top_frame = ttk.Frame(self.scrollable.interior, padding=6)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        buckets_frame = ttk.Frame(self.scrollable.interior, padding=6)
        buckets_frame.pack(side=tk.TOP, fill=tk.X)

        # Controls
        self.btn_load_csv = ttk.Button(top_frame, text="Load CSV", command=self.load_csv)
        self.btn_load_csv.pack(side=tk.LEFT, padx=4)
        self.btn_select_db = ttk.Button(top_frame, text="Select Database", command=self.select_database)
        self.btn_select_db.pack(side=tk.LEFT, padx=4)
        self.db_lbl = ttk.Label(top_frame, text=f"DB: {self.database_path}")
        self.db_lbl.pack(side=tk.LEFT, padx=(4,12))

        self.btn_download = ttk.Button(top_frame, text="Download Data", command=self.download_data)
        self.btn_download.pack(side=tk.LEFT, padx=4)

        ttk.Label(top_frame, text="Period:").pack(side=tk.LEFT, padx=(8,2))
        self.period_cb = ttk.Combobox(top_frame, values=['1mo','3mo','6mo','5d','1y','2y','5y','10y','max'], width=6)
        self.period_cb.set('1y'); self.period_cb.pack(side=tk.LEFT)

        ttk.Label(top_frame, text="Interval:").pack(side=tk.LEFT, padx=(8,2))
        self.interval_cb = ttk.Combobox(top_frame, values=['1m','5m','1d','1wk','1h','30m','15m','1mo'], width=6)
        self.interval_cb.set('1d'); self.interval_cb.pack(side=tk.LEFT)

        ttk.Label(top_frame, text="Streak days:").pack(side=tk.LEFT, padx=(8,2))
        self.streak_spin = ttk.Spinbox(top_frame, values=[1,2,3,4,5,7,10], width=4)
        self.streak_spin.set(1); self.streak_spin.pack(side=tk.LEFT)

        # Bucket visibility control frame (dynamic show/hide)
        bucket_ctrl = ttk.LabelFrame(buckets_frame, text="Show Buckets")
        bucket_ctrl.pack(side=tk.LEFT, padx=8)

        # include new squeeze buckets in categories
        self.categories = ['Up Squeeze','Down Squeeze','Overbought','Oversold','Gaining Streak','Losing Streak','RS','Bollinger Break','Top Gainers']
        self.bucket_vars = {}
        for cat in self.categories:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(bucket_ctrl, text=cat, variable=var, command=self.update_bucket_visibility)
            cb.pack(side=tk.LEFT, padx=2)
            self.bucket_vars[cat] = var

        self.btn_screener = ttk.Button(top_frame, text="Run Screener", command=self.run_screener)
        self.btn_screener.pack(side=tk.LEFT, padx=8)

        self.status_lbl = ttk.Label(top_frame, text="Idle")
        self.status_lbl.pack(side=tk.LEFT, padx=12)

        # main content area (inside scrollable.interior)
        main = ttk.Frame(self.scrollable.interior, padding=6)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # left multi-column lists (screener)
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=4, pady=4)

        self.lists = {}
        self.bucket_frames = {}
        for cat in self.categories:
            fr = ttk.Labelframe(left, text=cat, height=140)
            fr.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
            lb = tk.Listbox(fr, height=6, font=("Courier",10),width=40)
            lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            sb = ttk.Scrollbar(fr, command=lb.yview); sb.pack(side=tk.RIGHT, fill=tk.Y)
            lb.config(yscrollcommand=sb.set)
            lb.bind("<Double-Button-1>", self.on_list_double)
            lb.bind("<Return>", self.on_list_double)
            self.lists[cat] = lb
            self.bucket_frames[cat] = fr

        # right chart area (embedded)
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        # Create a notebook for chart and notes
        self.right_notebook = ttk.Notebook(right)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Chart tab
        chart_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(chart_frame, text="Chart")
        
        # Notes tab
        notes_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(notes_frame, text="Notes")
        
        # Chart controls
        control_right = ttk.Frame(chart_frame)
        control_right.pack(side=tk.TOP, fill=tk.X)

        # Ticker label + entry to allow manual ticker / or double click list
        ttk.Label(control_right, text="Ticker (e.g., TCS.NS):").pack(side=tk.LEFT)
        self.ticker_entry = ttk.Entry(control_right, width=12)
        self.ticker_entry.pack(side=tk.LEFT, padx=(4,8))
        self.ticker_entry.bind("<Return>", lambda e: self.plot_ticker())

        # Indicator toggles area
        self.show_mas = tk.BooleanVar(value=True)
        self.show_ema10 = tk.BooleanVar(value=True)
        self.show_ema20 = tk.BooleanVar(value=True)
        self.show_ema50 = tk.BooleanVar(value=True)
        self.show_ema200 = tk.BooleanVar(value=True)
        self.show_boll = tk.BooleanVar(value=True)
        self.show_rsi = tk.BooleanVar(value=True)
        self.show_volume = tk.BooleanVar(value=True)

        ttk.Checkbutton(control_right, text="Show MAs", variable=self.show_mas).pack(side=tk.LEFT, padx=4)
        # individual EMA toggles (visible only if user wants fine control)
        ttk.Checkbutton(control_right, text="EMA10", variable=self.show_ema10).pack(side=tk.LEFT)
        ttk.Checkbutton(control_right, text="EMA20", variable=self.show_ema20).pack(side=tk.LEFT)
        ttk.Checkbutton(control_right, text="EMA50", variable=self.show_ema50).pack(side=tk.LEFT)
        ttk.Checkbutton(control_right, text="EMA200", variable=self.show_ema200).pack(side=tk.LEFT)

        ttk.Checkbutton(control_right, text="Bollinger", variable=self.show_boll).pack(side=tk.LEFT, padx=6)
        ttk.Checkbutton(control_right, text="RSI", variable=self.show_rsi).pack(side=tk.LEFT)
        ttk.Checkbutton(control_right, text="Volume", variable=self.show_volume).pack(side=tk.LEFT, padx=4)

        ttk.Button(control_right, text="Plot Ticker", command=self.plot_ticker).pack(side=tk.LEFT, padx=8)

        # container for canvas + toolbar
        self.canvas_container = ttk.Frame(chart_frame)
        self.canvas_container.pack(fill=tk.BOTH, expand=True)

        # Notes controls
        notes_control_frame = ttk.Frame(notes_frame)
        notes_control_frame.pack(side=tk.TOP, fill=tk.X, pady=4)
        
        ttk.Label(notes_control_frame, text="Notes for:").pack(side=tk.LEFT)
        self.notes_ticker_label = ttk.Label(notes_control_frame, text="No ticker selected", font=("Arial", 10, "bold"))
        self.notes_ticker_label.pack(side=tk.LEFT, padx=5)
        
        self.save_notes_btn = ttk.Button(notes_control_frame, text="Save Notes", command=self.save_current_notes)
        self.save_notes_btn.pack(side=tk.RIGHT, padx=5)
        
        # Notes text area
        self.notes_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD, width=60, height=20)
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add a context menu to the notes text area
        self.notes_menu = tk.Menu(self.notes_text, tearoff=0)
        self.notes_menu.add_command(label="Cut", command=lambda: self.notes_text.event_generate("<<Cut>>"))
        self.notes_menu.add_command(label="Copy", command=lambda: self.notes_text.event_generate("<<Copy>>"))
        self.notes_menu.add_command(label="Paste", command=lambda: self.notes_text.event_generate("<<Paste>>"))
        self.notes_text.bind("<Button-3>", self.show_notes_context_menu)

        # Matplotlib placeholders
        self.mpf_fig = None
        self.mpf_canvas = None
        self.toolbar = None

        # state
        self.loaded_tickers = []
        self.download_thread = None
        self.screener_thread = None
        self.current_ticker = None  # Track the currently selected ticker

        # initial visibility
        self.update_bucket_visibility()

    # ---------- Notes System ----------
    def show_notes_context_menu(self, event):
        """Show context menu for notes text area"""
        self.notes_menu.tk_popup(event.x_root, event.y_root)
        
    def save_current_notes(self):
        """Save notes for the current ticker"""
        if not self.current_ticker:
            messagebox.showwarning("No Ticker", "Please select a ticker first.")
            return
            
        notes = self.notes_text.get(1.0, tk.END).strip()
        self.notes_manager.save_notes(self.current_ticker, notes)
        messagebox.showinfo("Notes Saved", f"Notes for {self.current_ticker} saved successfully.")
        
    def load_notes_for_ticker(self, ticker):
        """Load notes for a specific ticker"""
        self.current_ticker = ticker
        self.notes_ticker_label.config(text=ticker)
        notes = self.notes_manager.get_notes(ticker)
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(1.0, notes)
        
    # ---------- CSV load ----------
    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path:
            return
        try:
            df = pd.read_csv(path, header=None)
            tickers = df.iloc[:,0].astype(str).str.strip().tolist()
            normalized = []
            for t in tickers:
                if not t: continue
                tu = t.upper()
                if not tu.endswith(".NS"): tu = tu + ".NS"
                if tu not in normalized: normalized.append(tu)
            self.loaded_tickers = normalized
            messagebox.showinfo("CSV loaded", f"Loaded {len(self.loaded_tickers)} tickers.")
        except Exception as e:
            print("[ERROR] Could not read CSV:", e)
            traceback.print_exc()
            messagebox.showerror("CSV error", f"Could not read CSV: {e}")

    # ---------- Select DB ----------
    def select_database(self):
        path = filedialog.askopenfilename(filetypes=[("SQLite DB","*.db"),("All files","*.*")])
        if not path:
            return
        try:
            # close existing connection and open new one
            try:
                self.conn.close()
            except Exception:
                pass
            self.database_path = path
            self.conn = sqlite3.connect(self.database_path, check_same_thread=False)
            self.cur = self.conn.cursor()
            self.db_lbl.config(text=f"DB: {self.database_path}")
            # Reinitialize notes manager with new database
            self.notes_manager = TickerNotes(self.database_path)
            self.update_status(f"Selected DB: {os.path.basename(self.database_path)}")
        except Exception as e:
            print("[ERROR] selecting DB:", e)
            traceback.print_exc()
            messagebox.showerror("DB error", f"Could not open DB: {e}")

    # ---------- Download ----------
    def download_data(self):
        if not self.loaded_tickers:
            messagebox.showwarning("No tickers", "Load a CSV first.")
            return
        period = self.period_cb.get()
        interval = self.interval_cb.get()
        # disable controls while downloading
        self.btn_load_csv.config(state=tk.DISABLED)
        self.btn_download.config(state=tk.DISABLED)
        self.btn_screener.config(state=tk.DISABLED)
        self.update_status("Starting download...")
        self.download_thread = DownloadThread(self.loaded_tickers, period, interval, self.database_path, self.update_status, self.download_finished)
        self.download_thread.start()

    def download_finished(self):
        def _done():
            self.update_status("Download finished.")
            self.btn_load_csv.config(state=tk.NORMAL)
            self.btn_download.config(state=tk.NORMAL)
            self.btn_screener.config(state=tk.NORMAL)
            messagebox.showinfo("Download", "Download & store finished.")
        self.root.after(0, _done)

    # ---------- Screener ----------
    def run_screener(self):
        if not self.loaded_tickers:
            messagebox.showwarning("No tickers", "Load a CSV first.")
            return
        period = self.period_cb.get()
        interval = self.interval_cb.get()
        streak = int(self.streak_spin.get())
        self.btn_load_csv.config(state=tk.DISABLED)
        self.btn_download.config(state=tk.DISABLED)
        self.btn_screener.config(state=tk.DISABLED)
        self.update_status("Starting screener...")
        self.screener_thread = ScreenerThread(self.loaded_tickers, period, interval, streak, self.database_path, self.update_status, self.screener_finished, self.receive_results)
        self.screener_thread.start()

    def screener_finished(self):
        def _done():
            self.update_status("Screener finished.")
            self.btn_load_csv.config(state=tk.NORMAL)
            self.btn_download.config(state=tk.NORMAL)
            self.btn_screener.config(state=tk.NORMAL)
        self.root.after(0, _done)

    def receive_results(self, buckets):
        def _populate():
            # clear lists
            for lb in self.lists.values():
                lb.delete(0, tk.END)
            # populate
            for cat, items in buckets.items():
                # sort by appropriate metric
                if cat == 'RS':
                    items.sort(key=lambda x: x[1] if x[1] is not None else -999, reverse=True)
                elif cat == 'Top Gainers':
                    items.sort(key=lambda x: x[1] if x[1] is not None else -999, reverse=True)
                else:
                    # generic sort on second element (works for squeeze too where second is delta)
                    items.sort(key=lambda x: x[1] if x[1] is not None else -999, reverse=True)
                lb = self.lists[cat]
                for it in items:
                    if cat == 'RS':
                        text = f"{it[0]:<14} RSdiff:{it[1]:+6.2f} RSI:{(it[2] if it[2] is not None else 0):6.2f}"
                    elif cat == 'Top Gainers':
                        text = f"{it[0]:<14} %Δ:{it[1]:6.2f} RSI:{(it[2] if it[2] is not None else 0):6.2f}"
                    elif cat == 'Bollinger Break':
                        text = f"{it[0]:<14} RSI:{(it[1] if it[1] is not None else 0):6.2f} %Δ:{it[2]:6.2f}"
                    elif cat in ('Gaining Streak','Losing Streak'):
                        text = f"{it[0]:<14} RSI:{(it[1] if it[1] is not None else 0):6.2f} Streak:{it[2]}"
                    elif cat in ('Up Squeeze','Down Squeeze'):
                        # it = (ticker, delta, close)
                        text = f"{it[0]:<14} Δ:{it[1]:+6.2f} Close:{it[2]:7.2f}"
                    else:
                        text = f"{it[0]:<14} RSI:{(it[1] if it[1] is not None else 0):6.2f}"
                    lb.insert(tk.END, text)
            self.update_status("Lists updated.")
        self.root.after(0, _populate)

    # ---------- Charting (embedded, unified plot_ticker) ----------
    def on_list_double(self, event):
        widget = event.widget
        sel = widget.curselection()
        if not sel:
            return
        text = widget.get(sel[0])
        ticker = text.split()[0]
        # populate ticker entry and plot
        self.ticker_entry.delete(0, tk.END)
        self.ticker_entry.insert(0, ticker)
        self.plot_ticker()
        # Load notes for this ticker
        self.load_notes_for_ticker(ticker)

    def plot_ticker(self):
        ticker_raw = self.ticker_entry.get().strip()
        if not ticker_raw:
            messagebox.showwarning("No ticker", "Enter a ticker (e.g., TCS.NS) or double-click a list item.")
            return

        ticker = ticker_raw.upper()
        if not ticker.endswith(".NS"):
            ticker = ticker + ".NS"

        # Load notes for this ticker
        self.load_notes_for_ticker(ticker)

        # read DB table
        try:
            conn_local = sqlite3.connect(self.database_path)
            tbl = table_name_for_ticker(ticker)
            cur_local = conn_local.cursor()
            cur_local.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
            if cur_local.fetchone() is None:
                messagebox.showwarning("No data", f"No stored data for {ticker} in DB.")
                conn_local.close()
                return
            df = pd.read_sql(f"SELECT * FROM '{tbl}' ORDER BY date", conn_local, parse_dates=['date'])
            conn_local.close()
        except Exception as e:
            print(f"[ERROR] plot_ticker DB read failed: {e}")
            traceback.print_exc()
            messagebox.showerror("DB Error", f"Could not read data for {ticker}:\n{e}")
            return

        if df.empty:
            messagebox.showwarning("No data", f"No stored rows for {ticker}")
            return

        # prepare DataFrame
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df[['open','high','low','close','volume']].copy()
        df.columns = ['Open','High','Low','Close','Volume']
        # ensure numeric
        for c in ['Open','High','Low','Close','Volume']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df.dropna(subset=['Open','High','Low','Close'], inplace=True)

        if df.empty:
            messagebox.showwarning("No data", f"No valid OHLC rows for {ticker}")
            return

        # compute full-series indicators
        full_close = df['Close'].copy()

        # EMAs
        if self.show_mas.get() or self.show_ema10.get() or self.show_ema20.get() or self.show_ema50.get() or self.show_ema200.get():
            df['EMA10'] = full_close.ewm(span=10, adjust=False).mean()
            df['EMA20'] = full_close.ewm(span=20, adjust=False).mean()
            df['EMA50'] = full_close.ewm(span=50, adjust=False).mean()
            df['EMA200'] = full_close.ewm(span=200, adjust=False).mean()

        # Bollinger
        if self.show_boll.get():
            ub, mb, lb = bollinger_bands(full_close)
            df['BB_upper'] = ub
            df['BB_mid'] = mb
            df['BB_lower'] = lb

        # RSI
        if self.show_rsi.get():
            df['RSI'] = compute_rsi(full_close)

        # Resample / filter by interval + period
        interval_val = self.interval_cb.get()
        period_val = self.period_cb.get()

        # Determine resampling rule if needed
        if interval_val != "1d":
            # map typical interval choices to resample rules (coarse)
            resample_map = {
                "1wk": "W",
                "1mo": "M",
                "1m": None, "5m": None, "15m": None, "30m": None, "1h": None  # intraday not supported by this simple resample
            }
            rule = resample_map.get(interval_val, None)
            if rule:
                agg = {
                    'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum',
                    'EMA10': 'last','EMA20':'last','EMA50':'last','EMA200':'last',
                    'BB_upper':'last','BB_mid':'last','BB_lower':'last','RSI':'last'
                }
                # Only include the keys that exist
                agg = {k:v for k,v in agg.items() if k in df.columns}
                df = df.resample(rule).agg(agg).dropna()

        # Period filter (by days approximation)
        now = df.index.max()
        if period_val.endswith("mo"):
            try:
                months = int(period_val[:-2])
                start_date = now - pd.DateOffset(months=months)
                df = df[df.index >= start_date]
            except Exception:
                pass
        elif period_val.endswith("y"):
            try:
                years = int(period_val[:-1])
                start_date = now - pd.DateOffset(years=years)
                df = df[df.index >= start_date]
            except Exception:
                pass
        elif period_val == "5d":
            start_date = now - pd.Timedelta(days=5)
            df = df[df.index >= start_date]
        elif period_val == "max":
            pass

        if df.empty:
            messagebox.showwarning("No data", "No data after resample/filter. Try a larger period or different interval.")
            return

        # Build addplots list (for mplfinance)
        addplots = []

        # Bollinger as addplot (plot UB/MB/LB)
        if self.show_boll.get() and all(col in df.columns for col in ['BB_upper','BB_mid','BB_lower']):
            # mpf.make_addplot expects series or list
            addplots.append(mpf.make_addplot(df['BB_upper'], color='tab:blue'))
            addplots.append(mpf.make_addplot(df['BB_mid'], color='tab:cyan'))
            addplots.append(mpf.make_addplot(df['BB_lower'], color='tab:blue'))

        # MAs: either master show_mas shows all, or user-level toggles
        mav_tuple = ()
        if self.show_mas.get():
            # show only those EMAs that exist in df and whose individual toggles are True
            mav_list = []
            if self.show_ema10.get() and 'EMA10' in df.columns: mav_list.append(10)
            if self.show_ema20.get() and 'EMA20' in df.columns: mav_list.append(20)
            if self.show_ema50.get() and 'EMA50' in df.columns: mav_list.append(50)
            if self.show_ema200.get() and 'EMA200' in df.columns: mav_list.append(200)
            mav_tuple = tuple(mav_list)

        # RSI as panel addplot
        rsi_addplot = None
        if self.show_rsi.get() and 'RSI' in df.columns:
            rsi_addplot = mpf.make_addplot(df['RSI'], panel=1, ylabel='RSI')

        # Clear old chart
        for w in self.canvas_container.winfo_children():
            w.destroy()

        # Create figure using mplfinance
        try:
            fig, axes = mpf.plot(df,
                                 type='candle',
                                 mav=mav_tuple if mav_tuple else (),
                                 volume=self.show_volume.get(),
                                 addplot = ([rsi_addplot] if rsi_addplot is not None else []) + addplots,
                                 returnfig=True,
                                 figscale=1.2,
                                 figratio=(12,8),
                                 tight_layout=True,
                                 warn_too_much_data=100000)
            plt.close(fig)  # avoid external window pop

            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_container)
            canvas.draw()
            widget = canvas.get_tk_widget()
            
            toolbar = NavigationToolbar2Tk(canvas, self.canvas_container)
            toolbar.update()
            toolbar.pack(side=tk.TOP, fill=tk.X,anchor='w')
            widget.pack(fill=tk.BOTH, expand=True)

            # store refs
            self.mpf_fig = fig
            self.mpf_canvas = canvas
            self.toolbar = toolbar

        except Exception as e:
            print(f"[ERROR] plot_ticker {ticker} failed:", e)
            traceback.print_exc()
            messagebox.showerror("Plot error", f"See console for details: {e}")

    # ---------- utilities ----------
    def update_status(self, text):
        self.root.after(0, lambda: self.status_lbl.config(text=text))

    def update_bucket_visibility(self):
        """Show or hide bucket frames based on the checkboxes in top controls."""
        for cat, fr in self.bucket_frames.items():
            should_show = bool(self.bucket_vars.get(cat, tk.BooleanVar()).get())
            # pack or forget accordingly
            if should_show:
                # if not already visible, pack it (we keep original packing order)
                if not fr.winfo_ismapped():
                    fr.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
            else:
                if fr.winfo_ismapped():
                    fr.pack_forget()

# ---------------- Run ---------------
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()