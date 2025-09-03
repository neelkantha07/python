import streamlit as st
from nsepython import *
import pandas as pd
from datetime import date
import plotly.graph_objects as go
import ta

# --- Sidebar ---
st.sidebar.title("📈 NSE Stock Dashboard")
ticker = st.sidebar.text_input("Enter Symbol (e.g. RELIANCE)", "NIFTYBEES")
from_date = st.sidebar.date_input("From", date(2023, 1, 1))
to_date = st.sidebar.date_input("To", date.today())

# --- Indicators ---
st.sidebar.subheader("Indicators")
show_rsi = st.sidebar.checkbox("RSI", True)
show_macd = st.sidebar.checkbox("MACD", False)
show_boll = st.sidebar.checkbox("Bollinger Bands", False)
show_ema = st.sidebar.checkbox("EMA 50/100/200", False)

# --- Fetch Data ---
def get_data(symbol, start, end):
    try:
        df = equity_history(
            symbol=symbol,
            series="EQ",
            start_date=start.strftime('%d-%m-%Y'),
            end_date=end.strftime('%d-%m-%Y')
        )
        df['Date'] = pd.to_datetime(df['CH_TIMESTAMP'])
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        df.rename(columns={
            'CH_OPENING_PRICE': 'Open',
            'CH_TRADE_HIGH_PRICE': 'High',
            'CH_TRADE_LOW_PRICE': 'Low',
            'CH_CLOSING_PRICE': 'Close',
            'CH_TOT_TRADED_QTY': 'Volume'
        }, inplace=True)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# --- Main Chart ---
df = get_data(ticker.upper(), from_date, to_date)

if not df.empty:
    # --- Indicators ---
    if show_rsi:
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    if show_macd:
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
    if show_boll:
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_high'] = bb.bollinger_hband()
        df['BB_low'] = bb.bollinger_lband()
    if show_ema:
        df['EMA50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
        df['EMA100'] = ta.trend.EMAIndicator(df['Close'], window=100).ema_indicator()
        df['EMA200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()

    # --- Plot Candlestick ---
    st.title(f"📊 {ticker.upper()} Chart")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))

    if show_ema:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='blue', width=1), name='EMA50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA100'], line=dict(color='orange', width=1), name='EMA100'))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='green', width=1), name='EMA200'))

    if show_boll:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_high'], line=dict(color='gray', dash='dot'), name='BB High'))
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_low'], line=dict(color='gray', dash='dot'), name='BB Low'))

    st.plotly_chart(fig, use_container_width=True)

    # --- RSI ---
    if show_rsi:
        st.subheader("📉 RSI")
        st.line_chart(df[['RSI']])

    # --- MACD ---
    if show_macd:
        st.subheader("📉 MACD")
        st.line_chart(df[['MACD', 'MACD_signal']])

    # --- Download Option ---
    st.download_button("⬇️ Download Data as CSV", df.to_csv().encode(), file_name=f"{ticker}_data.csv")

else:
    st.warning("No data available. Please check the symbol or date range.")

# --- Screener ---
st.header("🔍 Screener: Stochastic RSI > 78")
uploaded = st.file_uploader("Upload CSV with symbols (no .NS needed)", type=["csv"])

if uploaded:
    tickers = pd.read_csv(uploaded, header=None)[0].tolist()
    results = []

    with st.spinner("Screening stocks..."):
        for raw_symbol in tickers:
            try:
                symbol = raw_symbol.strip().upper()
                data = get_data(symbol, from_date, to_date)
                if data.empty or len(data) < 30:
                    continue
                stoch_rsi = ta.momentum.StochRSIIndicator(close=data['Close'], window=60).stochrsi()

                if stoch_rsi.iloc[-1] > 0.78:
                    results.append((symbol, round(stoch_rsi.iloc[-1], 2)))
            except Exception:
                continue

    if results:
        st.success("Stocks where Stochastic RSI > 78:")
        st.dataframe(pd.DataFrame(results, columns=["Symbol", "StochRSI"]))
    else:
        st.info("No stocks found with Stochastic RSI > 78.")
