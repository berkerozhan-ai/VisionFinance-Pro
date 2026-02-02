import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from quant_core.analysis.portfolio_runner import PortfolioRunner
from quant_core.analysis.backtester import Backtester # NEW
from quant_core.data.market_data import TICKER_UNIVERSE
import quant_core.data.market_data as md_core
import quant_core.analysis.portfolio_runner as pr_module
import quant_core.analysis.scanner as scanner_module
import importlib
# --- GİZLEME KODU BAŞLANGICI ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# --- GİZLEME KODU BİTİŞİ ---
# Force Reload to pick up code changes
importlib.reload(md_core)
importlib.reload(pr_module)
importlib.reload(scanner_module)

from quant_core.analysis.portfolio_runner import PortfolioRunner # Re-import class after reload
from quant_core.analysis.scanner import MarketScanner
import time

import quant_core.utils.localization as loc
import importlib
importlib.reload(loc) # FORCE RELOAD to fix caching issues

# --- PAGE CONFIG (WIDE MODE FOR PRO FEEL) ---
st.set_page_config(
    page_title="Financial-Gemi Pro", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'language' not in st.session_state:
    st.session_state['language'] = "Türkçe" # Default

# --- AUTHENTICATION LOGIC ---
from quant_core.auth.user_manager import UserManager
user_manager = UserManager()

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/144/bullish.png", width=120)
        st.markdown(f"# {loc.get_text('welcome', st.session_state['language'])}")
        st.caption(loc.get_text('slogan', st.session_state['language']))
        
        st.markdown("---")
        
        # Auth Tabs
        tab_login, tab_register = st.tabs(["Giriş Yap", "Kayıt Ol"])
        
        with tab_login:
            st.subheader("Giriş Yap")
            l_user = st.text_input("Kullanıcı Adı", key="login_user")
            l_pass = st.text_input("Şifre", type="password", key="login_pass")
            
            if st.button("Giriş", use_container_width=True):
                if user_manager.login(l_user, l_pass):
                    st.session_state['logged_in'] = True
                    st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")

        with tab_register:
            st.subheader("Kayıt Ol")
            r_user = st.text_input("Kullanıcı Adı", key="reg_user")
            r_pass = st.text_input("Şifre", type="password", key="reg_pass")
            r_pass2 = st.text_input("Şifre Tekrar", type="password", key="reg_pass2")
            
            if st.button("Kayıt Ol", use_container_width=True):
                if r_pass != r_pass2:
                    st.error("Şifreler uyuşmuyor!")
                else:
                    ok, msg = user_manager.register(r_user, r_pass)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
        
        st.markdown("---")
        
        # Language Selector
        lang = st.selectbox(loc.get_text('lang_select', st.session_state['language']), loc.get_available_languages(), index=loc.get_available_languages().index(st.session_state['language']))
        st.session_state['language'] = lang
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("⚠️ **YASAL UYARI:** Buradaki veriler yatırım tavsiyesi değildir. Sadece analiz amaçlıdır.")
            
    st.stop() # HALT execution here if not logged in

# --- MAIN DASHBOARD STARTS HERE ---

# --- AUTO-REFRESH LOGIC (10 Minutes) ---
import time
if 'last_run' not in st.session_state:
    st.session_state['last_run'] = time.time()

if time.time() - st.session_state['last_run'] > 600: # 600 seconds = 10 minutes
    st.session_state['last_run'] = time.time()
    st.rerun()

# --- CUSTOM CSS (DARK THEME & CARDS) ---
# --- CUSTOM CSS (DARK THEME & CARDS) ---
st.markdown("""
<style>
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
    }
    .status-ok { color: #2ea043; font-weight: bold; }
    .status-warn { color: #d29922; font-weight: bold; }
    .badge-buy { background-color: #2ea043; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-sell { background-color: #da3633; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-hold { background-color: #d29922; color: black; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: ASSET SELECTION (TOP) ---
st.sidebar.warning(loc.get_text('ytd_warning', st.session_state['language']))
st.sidebar.title(loc.get_text('sidebar_title', st.session_state['language']))
st.sidebar.subheader(f"🔍 {loc.get_text('ticker', st.session_state['language'])}")

# 1. Region Selection
# 1. Region Selection
regions = list(TICKER_UNIVERSE.keys())
if "region_select" not in st.session_state:
    st.session_state["region_select"] = regions[0]

selected_region = st.sidebar.selectbox(loc.get_text('region', st.session_state['language']), regions, key="region_select")

# 2. Sector Selection
sectors = list(TICKER_UNIVERSE[selected_region].keys())
# Ensure sector is valid for region (reset if needed)
if "sector_select" not in st.session_state or st.session_state["sector_select"] not in sectors:
    st.session_state["sector_select"] = sectors[0]

selected_sector = st.sidebar.selectbox(loc.get_text('sector', st.session_state['language']), sectors, key="sector_select")

# 3. Ticker Selection
available_tickers = TICKER_UNIVERSE[selected_region][selected_sector]
# Ensure ticker is valid for sector
if "ticker_select" not in st.session_state or st.session_state["ticker_select"] not in available_tickers:
    st.session_state["ticker_select"] = available_tickers[0]

selected_ticker = st.sidebar.selectbox("Hisse / Coin", available_tickers, key="ticker_select", format_func=md_core.get_display_name)

# Asset Refresh Button using Progress Bar
if st.sidebar.button("🔄 Verileri Şimdi Güncelle"):
    import quant_core.data.market_data as md
    import importlib
    importlib.reload(md) # FORCE RELOAD to see new functions
    
    all_tickers = md.get_all_tickers()
    total = len(all_tickers)
    
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    
    success_count = 0
    
    with st.spinner(f"{loc.get_text('processing', st.session_state['language'])}..."):
        for i, ticker in enumerate(all_tickers):
            status_text.text(f"İşleniyor ({i+1}/{total}): {ticker}")
            
            # Call single fetcher
            try:
                ok, msg = md.fetch_single_ticker(ticker)
                if ok:
                    success_count += 1
            except AttributeError:
                # Fallback if reload failed somehow, though unlikely now
                st.error("Kod güncellenemedi. Lütfen uygulamayı kapatıp tekrar açın.")
                break
            
            # Update Progress
            progress_bar.progress((i + 1) / total)
            time.sleep(0.05) # Tiny UI breath
            
    status_text.text(f"{loc.get_text('completed', st.session_state['language'])} {success_count}/{total} ok.")
    time.sleep(1)
    st.rerun()

st.sidebar.markdown("---")

# --- SIDEBAR: GLOBAL WHALE RADAR (MOVED UP) ---
st.sidebar.subheader(loc.get_text('whale_radar', st.session_state['language']))
st.sidebar.caption(loc.get_text('whale_caption', st.session_state['language']))

from quant_core.analysis.scanner import MarketScanner

@st.cache_data(ttl=300) # Cache for 5 mins
def run_whale_scan():
    scanner = MarketScanner()
    return scanner.scan_for_whales(threshold=1.5)

if st.sidebar.button(loc.get_text('scan_btn', st.session_state['language'])):
    with st.sidebar.status(loc.get_text('scanning', st.session_state['language']), expanded=True) as status:
        whale_df = run_whale_scan()
        st.session_state['whale_results'] = whale_df # Persist results
        status.update(label="Tarama Tamamlandı!", state="complete", expanded=True)

# Check for persisted results
if 'whale_results' in st.session_state and not st.session_state['whale_results'].empty:
    whale_df = st.session_state['whale_results']
    st.sidebar.success(f"{len(whale_df)} {loc.get_text('opps_found', st.session_state['language'])}")
    
    # Create Clickable List
    def update_view_state(ticker_id):
        # Find Region & Sector
        for reg, sectors_dict in TICKER_UNIVERSE.items():
            for sec, tickers_list in sectors_dict.items():
                if ticker_id in tickers_list:
                    st.session_state['region_select'] = reg
                    st.session_state['sector_select'] = sec
                    st.session_state['ticker_select'] = ticker_id
                    return

    st.sidebar.markdown(loc.get_text('quick_access', st.session_state['language']))
    for i, row in whale_df.iterrows():
        display_tick = row['Ticker'] # Friendly name
        raw_tick = row['RawTicker'] # Real ID: GC=F, SI=F etc.
        rvol = row['RVOL']
        sig = row['Signal']
        
        # Unique key for each button
        btn_label = f"{display_tick} ({rvol}x) {sig}"
        # Use on_click callback to avoid "After Instantiation" error
        st.sidebar.button(btn_label, key=f"btn_{raw_tick}", on_click=update_view_state, args=(raw_tick,))
else:
    st.sidebar.info(loc.get_text('scan_info', st.session_state['language']))

st.sidebar.markdown("---")

# --- SIDEBAR: SYSTEM CORE (TOGGLES & STATUS) ---
st.sidebar.subheader(loc.get_text('system_control', st.session_state['language']))

# Mathematical Core
with st.sidebar.expander(loc.get_text('math_core', st.session_state['language']), expanded=True):
    core_active = st.toggle(loc.get_text('active', st.session_state['language']), value=True, key="core_toggle")
    
    if core_active:
        st.markdown("""
        - ✅ **Veri İşleme:** OHLCV Normalize
        - ✅ **Rejim Tespiti:** Volatilite/Trend
        - ✅ **Formasyonlar:** Mum Desenleri
        - ✅ **Risk Yönetimi:** Kelly Kriteri
        """, unsafe_allow_html=True)
        st.caption(loc.get_text('core_status_ok', st.session_state['language']))
    else:
        st.warning(loc.get_text('core_disabled', st.session_state['language']))



# Live Data Indicator (Minimalist)
st.sidebar.markdown("---")
# Show a small pulsing badge or text indicating system is live
st.sidebar.caption("🟢 **System Status:** ONLINE (Live Feed)")


# AI Narrator
with st.sidebar.expander(loc.get_text('ai_narrator', st.session_state['language']), expanded=True):
    ai_active = st.toggle("AI", value=True, key="ai_toggle")
    
    if ai_active:
        st.markdown("""
        - 🤖 **Context:** Global Makro
        - 📰 **Haber:** RSS + NLP (Canlı)
        - 🧠 **Sentiment:** Duygu Analizi
        - 🗣️ **Narrative:** Türkçe Rapor
        """, unsafe_allow_html=True)
        st.caption(loc.get_text('ai_status_online', st.session_state['language']))
    else:
        st.warning(loc.get_text('ai_sleep', st.session_state['language']))

st.sidebar.markdown("---")
st.sidebar.info(loc.get_text('sidebar_tip', st.session_state['language']))



# --- MAIN CONTENT ---
def load_analysis(ticker):
    """Runs analysis for a SINGLE ticker on the fly."""
    runner = PortfolioRunner(initial_capital=10000, tickers=[ticker])
    stats, allocations = runner.run_full_analysis()
    
    # Get the specific allocation for this ticker
    if allocations:
        return allocations[0], runner
    return None, runner

with st.spinner(f"{loc.get_text('ai_analyzing', st.session_state['language'])}: {selected_ticker}..."):
    try:
        alloc, runner = load_analysis(selected_ticker)
    except Exception as e:
        st.error(f"{loc.get_text('error_occurred', st.session_state['language'])}: {e}")
        st.stop()

if not alloc:
    st.warning(loc.get_text('no_data', st.session_state['language']))
    st.stop()

# --- HEADER SECTION ---
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.image("https://img.icons8.com/color/96/bullish.png", width=64) # Placeholder icon

with col2:
    st.markdown(f"## {md_core.get_display_name(selected_ticker)}")
    # Determine Currency Symbol
    currency_symbol = "$" # Default
    if selected_ticker.endswith(".IS"):
        currency_symbol = "₺"
    elif selected_ticker.endswith(".DE") or selected_ticker.endswith(".PA"):
        currency_symbol = "€"
    elif selected_ticker.endswith(".L"):
        currency_symbol = "£"
    
    st.markdown(f"**{loc.get_text('price', st.session_state['language'])}:** {currency_symbol}{alloc['Price']:,.2f}")
    
    # --- WHALE & SENTIMENT INDICATORS ---
    
    # 1. Whale Alert
    rvol = alloc.get('RVOL', 1.0)
    vol_sig = alloc.get('Vol_Signal', 'NORMAL')
    
    if rvol > 1.5:
        st.markdown(f"🐋 **{loc.get_text('whale_alert', st.session_state['language'])}** ({loc.get_text('chart_vol', st.session_state['language'])}: {rvol:.1f}x)")
        if vol_sig == 'HIGH_VOL_BUY':
            st.success(loc.get_text('strong_buy', st.session_state['language']))
        elif vol_sig == 'HIGH_VOL_SELL':
            st.error(loc.get_text('panic_sell', st.session_state['language']))
    
    # 2. Sentiment Gauge (Mini Progress Bar)
    sent_score = alloc.get('Sentiment_Score', 0)
    # Map -1..1 to 0..100 for progress bar
    sent_norm = int((sent_score + 1) * 50) 
    sent_color = "green" if sent_score > 0.1 else "red" if sent_score < -0.1 else "gray"
    
    st.write("---")
    st.markdown(f"**{loc.get_text('sentiment', st.session_state['language'])}:** {sent_score:.2f}")
    st.progress(sent_norm)
    if sent_score > 0.2:
        st.caption(loc.get_text('market_optimistic', st.session_state['language']))
    elif sent_score < -0.2:
        st.caption(loc.get_text('market_fear', st.session_state['language']))
        
    st.write("---")
    
    # --- MACRO HEDGE SHIELD ---
    from quant_core.analysis.hedge_engine import HedgeEngine
    
    @st.cache_data(ttl=3600) # Cache heavily (1 hour) as correlations don't change fast
    def get_hedges(tick):
        eng = HedgeEngine()
        return eng.find_hedges(tick)
        
    hedges = get_hedges(selected_ticker)
    if hedges:
        # Show only the BEST hedge for simplicity
        best_h = hedges[0]
        st.markdown(f"**{loc.get_text('crisis_shield', st.session_state['language'])}: {best_h['Ticker']}**")
        st.caption(loc.get_text('shield_desc', st.session_state['language']).format(selected_ticker, best_h['Ticker'], best_h['Correlation']))
        
        # Use a more robust key and direct logic
        if st.button(loc.get_text('shield_inspect', st.session_state['language']).format(best_h['Ticker']), key="btn_hedge_master", use_container_width=True):
            st.session_state['override_ticker'] = best_h['Ticker']
            # Find Region/Sector
            for reg, sectors_dict in TICKER_UNIVERSE.items():
                for sec, tickers_list in sectors_dict.items():
                    if best_h['Ticker'] in tickers_list:
                        st.session_state['override_region'] = reg
                        st.session_state['override_sector'] = sec
                        break
            st.rerun()
    else:
        st.caption(loc.get_text('no_hedge', st.session_state['language']))

        

with col3:
    action = alloc['Action']
    badge_class = "badge-buy" if action == "BUY" else "badge-sell" if action == "SELL" else "badge-hold"
    st.markdown(f"""
        <div style="text-align: right;">
            <span class="{badge_class}" style="font-size: 20px;">{action}</span>
            <br>
            <span style="font-size: 12px; color: #888;">{loc.get_text('ai_decision', st.session_state['language'])}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Add Space



st.markdown("---")

# --- CHARTING SECTION (PLOTLY) ---
parquet_path = os.path.join("quant_core", "data", "raw", f"{selected_ticker}.parquet")

# Check if file exists OR attempt smart load
# We use smart_load_ticker to handle both exist check and auto-update
import quant_core.data.market_data as md

# Attempt to load (this will auto-heal history if stale)
df = md.smart_load_ticker(selected_ticker)

if df is not None and not df.empty:
    # df is already loaded
    
    # CRITICAL FIX: Ensure columns are flat (formatting issues with yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.droplevel(1)
        except:
            pass


    
    # --- LIVE DATA PATCH (SYNTHETIC DAILY CANDLE) ---
    # We fetch intraday 1m data to construct the "True Now" candle.
    # This avoids yfinance's daily bar lag.
    import quant_core.data.market_data as md
    try:
        # We reuse get_realtime_quote which fetches 1d of 1m data
        rt_price, rt_vol, intraday_df = md.get_realtime_quote(selected_ticker)
        
        if intraday_df is not None and not intraday_df.empty:
            # 1. Flatten columns if MultiIndex
            if isinstance(intraday_df.columns, pd.MultiIndex):
                intraday_df.columns = intraday_df.columns.droplevel(1)
            
            # 2. Check if this data is actually newer or same day
            # Get the date of the intraday data
            live_date = intraday_df.index[-1].normalize()
            
            # 3. Synthesize Daily Candle
            # Open = First minute Open
            # High = Max of all Highs
            # Low = Min of all Lows
            # Close = Last minute Close
            # Volume = Sum of all Volumes
            
            synthetic_candle = pd.DataFrame([{
                'Open': intraday_df['Open'].iloc[0],
                'High': intraday_df['High'].max(),
                'Low': intraday_df['Low'].min(),
                'Close': intraday_df['Close'].iloc[-1],
                'Volume': intraday_df['Volume'].sum()
            }], index=[live_date])
            
            # 4. Merge with History
            if df.index.tz is not None: df.index = df.index.tz_localize(None)
            if synthetic_candle.index.tz is not None: synthetic_candle.index = synthetic_candle.index.tz_localize(None)
            
            # If the last date of history is same as live, REPLACE it (it was incomplete)
            # If live is newer, APPEND it
            
            # Combine and deduplicate by index, keeping LAST (which is our synthetic live one)
            combined_df = pd.concat([df, synthetic_candle])
            df = combined_df[~combined_df.index.duplicated(keep='last')]
            df = df.sort_index()
            
            # print(f"DEBUG: Merged Synthetic Candle for {live_date}")

    except Exception as e:
        print(f"Live Merge Error: {e}")
        pass
    
    # --- CALCULATE INDICATORS ON THE FLY ---
    # use explicit assignment to avoid column name guessing issues
    df['RSI'] = df.ta.rsi(length=14)
    
    # MACD returns a DF with 3 columns usually: MACD, Histogram, Signal
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    if macd is not None:
        # MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        # We rename them to standard simple names
        df['MACD'] = macd.iloc[:, 0]
        df['MACD_Hist'] = macd.iloc[:, 1]
        df['MACD_Signal'] = macd.iloc[:, 2]
        
    # BBANDS
    bb = df.ta.bbands(length=20, std=2)
    if bb is not None:
        # BBL, BBM, BBU are usually 0, 1, 2 or similar order. 
        # Typically: BBL_..., BBM_..., BBU_... but order might vary.
        # checking column names for 'BBU', 'BBL'
        bbu_col = [c for c in bb.columns if c.startswith('BBU')][0]
        bbl_col = [c for c in bb.columns if c.startswith('BBL')][0]
        df['BB_Upper'] = bb[bbu_col]
        df['BB_Lower'] = bb[bbl_col]
    
    # Filter last 6 months for clear view
    df_view = df.tail(150) 
    
    # Create Subplots: 4 Rows (Main, Volume, RSI, MACD)
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.5, 0.15, 0.15, 0.2],

        subplot_titles=(f"{{selected_ticker}} {loc.get_text('chart_price', st.session_state['language'])}", loc.get_text('chart_vol', st.session_state['language']), loc.get_text('chart_rsi', st.session_state['language']), loc.get_text('chart_macd', st.session_state['language']))
    )

    # --- ROW 1: CANDLESTICK & OVERLAYS ---
    fig.add_trace(go.Candlestick(
        x=df_view.index,
        open=df_view['Open'],
        high=df_view['High'],
        low=df_view['Low'],
        close=df_view['Close'],
        name=loc.get_text('price', st.session_state['language'])
    ), row=1, col=1)

    # Bollinger Bands
    if 'BB_Upper' in df_view.columns:
        fig.add_trace(go.Scatter(x=df_view.index, y=df_view['BB_Upper'], mode='lines', line=dict(color='gray', width=1, dash='dot'), name='BB Üst'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_view.index, y=df_view['BB_Lower'], mode='lines', line=dict(color='gray', width=1, dash='dot'), name='BB Alt', fill='tonexty'), row=1, col=1)

    # SMA 50 (if exists or calc)
    if 'SMA_50' in df_view.columns:
        fig.add_trace(go.Scatter(x=df_view.index, y=df_view['SMA_50'], mode='lines', name='SMA 50', line=dict(color='orange', width=1.5)), row=1, col=1)
    
    # --- ROW 2: VOLUME ---
    colors = ['red' if row.Open > row.Close else 'green' for i, row in df_view.iterrows()]
    fig.add_trace(go.Bar(
        x=df_view.index, 
        y=df_view['Volume'],
        name=loc.get_text('chart_vol', st.session_state['language']),
        marker_color=colors
    ), row=2, col=1)

    # --- ROW 3: RSI ---
    if 'RSI' in df_view.columns:
        fig.add_trace(go.Scatter(x=df_view.index, y=df_view['RSI'], mode='lines', name='RSI (14)', line=dict(color='purple', width=2)), row=3, col=1)
        # Add Lines 30/70
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # --- ROW 4: MACD ---
    if 'MACD' in df_view.columns:
        # Histogram
        colors_macd = ['green' if v >= 0 else 'red' for v in df_view['MACD_Hist']]
        fig.add_trace(go.Bar(x=df_view.index, y=df_view['MACD_Hist'], name='MACD Hist', marker_color=colors_macd), row=4, col=1)
        # MACD Line
        fig.add_trace(go.Scatter(x=df_view.index, y=df_view['MACD'], mode='lines', name='MACD', line=dict(color='blue', width=1.5)), row=4, col=1)
        # Signal Line
        fig.add_trace(go.Scatter(x=df_view.index, y=df_view['MACD_Signal'], mode='lines', name='Signal', line=dict(color='orange', width=1.5)), row=4, col=1)

    # Layout Updates
    fig.update_layout(
        template='plotly_dark',
        height=900, # Taller for 4 rows
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_rangeslider_visible=False,
        showlegend=False # Too many items, cleaner without or selective
    )
    
    # Add Annotation for Decision
    action_color = "#2ea043" if action == "BUY" else "#da3633" if action == "SELL" else "#777"
    fig.add_annotation(
        x=df_view.index[-1], y=df_view['Close'].iloc[-1],
        text=f"{action}",
        showarrow=True, arrowhead=1,
        bgcolor=action_color, font=dict(color="white"),
        row=1, col=1
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(loc.get_text('error_occurred', st.session_state['language']))

# --- TABS: DETAIL, NEWS (REPLACED), BACKTEST, SETTINGS, ROBO-ADVISOR ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([loc.get_text('tab_ai', st.session_state['language']), loc.get_text('tab_news', st.session_state['language']), loc.get_text('tab_backtest', st.session_state['language']), loc.get_text('tab_settings', st.session_state['language']), loc.get_text('tab_robo', st.session_state['language'])])

with tab1:
    # ... (Keep existing Tab 1 content, no changes needed here, just context)
    st.subheader(loc.get_text('reason_header', st.session_state['language']))
    st.info(alloc['Advice'])
    st.markdown(f"### {loc.get_text('logic_header', st.session_state['language'])}")
    if alloc['Story']: st.markdown(alloc['Story'])
    else: st.write(loc.get_text('no_data', st.session_state['language']))
    st.markdown("---")
    st.caption(f"Hedeflenen Alım Adedi: {alloc['Shares']} lot (${alloc['Capital ($)']:,.2f})")
    with st.expander(loc.get_text('strategy_note', st.session_state['language'])):
        st.info(loc.get_text('strategy_desc', st.session_state['language']))

with tab2:
    # 3. Specific News (REAL RSS DATA)
    st.subheader(loc.get_text('in_the_news', st.session_state['language']).format(selected_ticker))
    
    news_items = alloc.get('News_Articles', [])
    
    if news_items and isinstance(news_items, list) and len(news_items) > 0:
        for news in news_items:
            # Parse Date if possible
            pub_date = news.get('published', '')
            
            with st.expander(f"📰 {news['title']}"):
                st.caption(loc.get_text('news_source', st.session_state['language']).format(pub_date))
                st.write(news.get('summary', ''))
                st.markdown(loc.get_text('read_more', st.session_state['language']).format(news['link']))
    else:
        st.info(loc.get_text('no_news', st.session_state['language']))
        
        # Fallback simulation only if absolutely empty
        st.markdown(loc.get_text('sim_mode', st.session_state['language']))
        st.markdown(f"- {selected_ticker} hakkında analist görüşleri pozitif.")

with tab3:
    st.subheader(loc.get_text('backtest_header', st.session_state['language']))
    st.markdown(loc.get_text('backtest_desc', st.session_state['language']))
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.caption(loc.get_text('ai_sensitivity', st.session_state['language']))
        threshold = st.slider(loc.get_text('buy_threshold', st.session_state['language']), 0, 100, 50, help=loc.get_text('threshold_help', st.session_state['language']))
        st.info(loc.get_text('threshold_info', st.session_state['language']))
    with col_b2:
        st.caption(loc.get_text('risk_mgmt', st.session_state['language']))
        sl_pct = st.number_input(loc.get_text('stop_loss', st.session_state['language']), 1.0, 20.0, 5.0, help=loc.get_text('stop_loss_help', st.session_state['language'])) / 100.0
        st.info(loc.get_text('stop_loss_info', st.session_state['language']))
        
    if st.button(loc.get_text('start_sim', st.session_state['language'])):
        # Load full DF again for backtest (need history)
        if os.path.exists(parquet_path):
            df_bt = pd.read_parquet(parquet_path)
            
            with st.spinner(loc.get_text('processing_history', st.session_state['language'])):
                from quant_core.data.indicators import add_features
                from quant_core.regimes.detectors.regime import detect_regime
                from quant_core.regimes.detectors.patterns import PatternScorer
                
                # 1. Prepare Data
                df_bt = add_features(df_bt)
                df_bt = detect_regime(df_bt)
                scorer = PatternScorer()
                df_bt = scorer.score_patterns(df_bt) # Calculate 'signal_score'
                
                # 2. Run Backtest
                bt = Backtester(initial_capital=10000)
                res = bt.run(df_bt, signal_threshold=threshold, stop_loss_pct=sl_pct)
                
                # 3. Visualization
                metrics = res['metrics']
                
                # Score Cards with Tooltips for Education
                c1, c2, c3, c4 = st.columns(4)
                st.metric(loc.get_text('total_return', st.session_state['language']), metrics['Total Return'], delta_color="normal")
                c2.metric(loc.get_text('max_drawdown', st.session_state['language']), metrics['Max Drawdown'], delta_color="inverse")
                c3.metric(loc.get_text('final_balance', st.session_state['language']), metrics['Final Balance'])
                c4.metric(loc.get_text('trade_count', st.session_state['language']), metrics['Trade Count'])
                
                # Equity Curve
                st.markdown(loc.get_text('portfolio_curve', st.session_state['language']))
                st.caption(loc.get_text('curve_desc', st.session_state['language']))
                eq_df = pd.DataFrame(res['equity_curve'], columns=['Portfolio Value'])
                st.line_chart(eq_df)
                
                # Trade Log
                with st.expander(loc.get_text('trade_log', st.session_state['language'])):
                    st.dataframe(res['trades'])
                    
        else:
            st.error("Veri dosyası bulunamadı, önce verileri güncelleyin.")

with tab4:
    st.subheader(loc.get_text('settings_header', st.session_state['language']))
    st.info(loc.get_text('settings_desc', st.session_state['language']))
    
    from quant_core.notification.bot import TelegramNotifier
    bot = TelegramNotifier()
    
    with st.form("telegram_form"):
        token_input = st.text_input("Bot Token (BotFather'dan alınan)", value=bot.token if bot.token else "", type="password")
        chat_id_input = st.text_input("Chat ID (userinfobot'tan alınan)", value=bot.chat_id if bot.chat_id else "")
        
        submitted = st.form_submit_button(loc.get_text('save_settings', st.session_state['language']))
        
        if submitted:
            bot.save_config(token_input, chat_id_input)
            st.success("Ayarlar başarıyla kaydedildi!")
            
    st.markdown("---")
    
    with st.expander("ℹ️ Telegram Bildirim Kurulumu Nasıl Yapılır?"):
        st.markdown("""
        **Adım 1: Kendi Botunuzu Oluşturun**
        1. Telegram uygulamasında arama çubuğuna **@BotFather** yazın ve sohbeti başlatın.
        2. `/newbot` komutunu gönderin ve talimatları izleyerek botunuza bir isim verin.
        3. İşlem sonunda verilen **HTTP API Token** şifresini kopyalayın ve yukarıdaki **Bot Token** alanına yapıştırın.

        **Adım 2: Chat ID'nizi Öğrenin**
        1. Telegram'da **@userinfobot** kullanıcısını aratın ve sohbeti başlatın.
        2. Botun size gönderdiği **Id** numarasını kopyalayın ve yukarıdaki **Chat ID** alanına yapıştırın.
        
        **Adım 3: Kaydet**
        * 'Ayarları Kaydet' butonuna basarak kurulumu tamamlayın.
        """)
    if st.button(loc.get_text('test_msg', st.session_state['language'])):
        ok, msg = bot.send_message("🦁 VisionFinance-Pro: Bağlantı Başarılı! Her şey yolunda patron.")
        if ok:
            st.success(msg)
        else:
            st.error(msg)
            
with tab5:
    st.subheader(loc.get_text('robo_header', st.session_state['language']))
    st.markdown(loc.get_text('robo_desc', st.session_state['language']))
    
    from quant_core.analysis.robo_advisor import RoboAdvisor
    
    col_robo_in, col_robo_out = st.columns([1, 2])
    
    with col_robo_in:
        st.info(loc.get_text('preferences', st.session_state['language']))
        st.caption(loc.get_text('robo_caption', st.session_state['language']))
        
        capital_input = st.number_input(loc.get_text('robo_budget', st.session_state['language']), min_value=1000, value=100000, step=1000)
        risk_choice = st.radio(loc.get_text('robo_risk', st.session_state['language']), [loc.get_text('risk_conservative', st.session_state['language']), loc.get_text('risk_balanced', st.session_state['language']), loc.get_text('risk_aggressive', st.session_state['language'])])
        
        # Sector Filter
        all_sectors_set = set()
        for reg in TICKER_UNIVERSE:
            all_sectors_set.update(TICKER_UNIVERSE[reg].keys())
        
        focus_sectors = st.multiselect(loc.get_text('sector_focus', st.session_state['language']), list(all_sectors_set), placeholder=loc.get_text('all_sectors', st.session_state['language']))
        
        risk_map = {
            loc.get_text('risk_conservative', st.session_state['language']): "Conservative", 
             loc.get_text('risk_balanced', st.session_state['language']): "Balanced", 
             loc.get_text('risk_aggressive', st.session_state['language']): "Aggressive"
        }
        
        st.write("")
        if st.button(f"✨ {loc.get_text('robo_gen', st.session_state['language'])}", use_container_width=True):
            advisor = RoboAdvisor()
            with st.spinner(loc.get_text('creating_portfolio', st.session_state['language'])):
                 # Pass focus_sectors (empty list means all)
                 allocation_res = advisor.generate_portfolio(capital_input, risk_map[risk_choice], focus_sectors=focus_sectors)
                 st.session_state['robo_allocation'] = allocation_res
    
    with col_robo_out:
        if 'robo_allocation' in st.session_state and st.session_state['robo_allocation']:
             allo = st.session_state['robo_allocation']
             df_allo = allo['portfolio']
             
             # Visualize Pie Chart
             fig_pie = go.Figure(data=[go.Pie(labels=df_allo['Ticker'], values=df_allo['Weight'], hole=.4)])
             fig_pie.update_layout(title_text=loc.get_text('rec_allocation', st.session_state['language']), template="plotly_dark", height=400)
             st.plotly_chart(fig_pie, use_container_width=True)
             
             # Summary Table
             st.markdown(loc.get_text('buy_list', st.session_state['language']))
             st.dataframe(
                 df_allo[['Ticker', 'Shares', 'Price', 'Allocation ($)']], 
                 hide_index=True, 
                 use_container_width=True
             )
        else:
            st.info(loc.get_text('start_prompt', st.session_state['language']))
            
    st.markdown("---")
    st.error(loc.get_text('legal_warning', st.session_state['language']))




# --- ALWAYS ON AUTO-REFRESH (BACKGROUND) ---
# Refreshes every 30 seconds to keep charts and data live
# This acts like a standard trading terminal
time.sleep(30)
st.rerun()

