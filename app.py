
import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from urllib.parse import quote_plus
from datetime import datetime

st.set_page_config(page_title="BelegRadar v5.3", page_icon="📈", layout="wide")

THEMES = {
    "🌈 Neon donker": {
        "hero": "linear-gradient(135deg, #111827, #7c3aed, #db2777)",
        "accent": "#ec4899", "accent2": "#8b5cf6",
        "app_bg": "#070b14", "sidebar_bg": "#111827", "panel_bg": "#0f172a",
        "card_bg": "#111827", "card_border": "#7c3aed",
        "text": "#f9fafb", "muted": "#d1d5db", "input_bg": "#0b1220"
    },
    "🔵 Blauw duidelijk": {
        "hero": "linear-gradient(135deg, #0f172a, #1d4ed8)",
        "accent": "#2563eb", "accent2": "#38bdf8",
        "app_bg": "#f8fafc", "sidebar_bg": "#e0f2fe", "panel_bg": "#ffffff",
        "card_bg": "#ffffff", "card_border": "#60a5fa",
        "text": "#0f172a", "muted": "#1e3a8a", "input_bg": "#ffffff"
    },
    "🟢 Groen duidelijk": {
        "hero": "linear-gradient(135deg, #064e3b, #16a34a)",
        "accent": "#16a34a", "accent2": "#65a30d",
        "app_bg": "#f7fee7", "sidebar_bg": "#dcfce7", "panel_bg": "#ffffff",
        "card_bg": "#ffffff", "card_border": "#4ade80",
        "text": "#052e16", "muted": "#14532d", "input_bg": "#ffffff"
    },
    "🟣 Paars duidelijk": {
        "hero": "linear-gradient(135deg, #312e81, #7e22ce)",
        "accent": "#7e22ce", "accent2": "#c026d3",
        "app_bg": "#faf5ff", "sidebar_bg": "#f3e8ff", "panel_bg": "#ffffff",
        "card_bg": "#ffffff", "card_border": "#a855f7",
        "text": "#1e1b4b", "muted": "#4c1d95", "input_bg": "#ffffff"
    },
    "🔥 Oranje duidelijk": {
        "hero": "linear-gradient(135deg, #7c2d12, #ea580c)",
        "accent": "#ea580c", "accent2": "#f59e0b",
        "app_bg": "#fff7ed", "sidebar_bg": "#ffedd5", "panel_bg": "#ffffff",
        "card_bg": "#ffffff", "card_border": "#fb923c",
        "text": "#431407", "muted": "#7c2d12", "input_bg": "#ffffff"
    },
}
selected_theme = st.sidebar.selectbox("🎨 Kleurthema", list(THEMES.keys()), index=0)
theme = THEMES[selected_theme]

st.markdown(f"""
<style>
.stApp {{
    background: {theme["app_bg"]} !important;
    color: {theme["text"]} !important;
}}
.block-container {{
    padding-top: 1.4rem;
    max-width: 1300px;
    color: {theme["text"]} !important;
}}
section[data-testid="stSidebar"] {{
    background: {theme["sidebar_bg"]} !important;
    border-right: 1px solid {theme["card_border"]};
}}
section[data-testid="stSidebar"] * {{
    color: {theme["text"]} !important;
}}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background: {theme["input_bg"]} !important;
    color: {theme["text"]} !important;
    border-color: {theme["card_border"]} !important;
}}
.hero {{
    background: {theme["hero"]};
    color: white;
    padding: 28px 32px;
    border-radius: 24px;
    margin-bottom: 22px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.25);
}}
.hero h1 {{ font-size: 44px; margin-bottom: 4px; color: white !important; }}
.hero p {{ font-size: 16px; color: #f8fafc !important; margin-bottom: 4px; }}
h1, h2, h3, h4, h5, h6, p, label, span {{
    color: {theme["text"]};
}}
div[data-testid="stMetric"] {{
    background: {theme["panel_bg"]};
    border: 1px solid {theme["card_border"]};
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}}
div[data-testid="stMetric"] label,
div[data-testid="stMetricValue"] {{
    color: {theme["text"]} !important;
}}
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: {theme["muted"]} !important;
    border-radius: 12px 12px 0 0;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {theme["accent"]} !important;
    border-bottom: 3px solid {theme["accent"]} !important;
    font-weight: 800;
}}
.stButton > button,
.stDownloadButton > button {{
    background: linear-gradient(135deg, {theme["accent"]}, {theme["accent2"]}) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
}}
details {{
    background: {theme["panel_bg"]} !important;
    border: 1px solid {theme["card_border"]} !important;
    border-radius: 14px !important;
    color: {theme["text"]} !important;
}}
input, textarea, select {{
    background: {theme["input_bg"]} !important;
    color: {theme["text"]} !important;
}}
div[data-testid="stDataFrame"] {{
    border: 1px solid {theme["card_border"]};
    border-radius: 14px;
    overflow: hidden;
}}
.candidate-card, .compact-card, .info-card {{
    background: {theme["card_bg"]};
    color: {theme["text"]};
    border: 1px solid {theme["card_border"]};
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}}
.candidate-card {{
    padding: 16px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
}}
.compact-card {{
    padding: 14px 16px;
    border-radius: 16px;
    margin-bottom: 10px;
}}
.info-card {{
    padding: 18px;
    border-radius: 16px;
    margin-bottom: 14px;
}}
.candidate-card h3, .compact-card strong, .info-card h3 {{
    color: {theme["text"]} !important;
}}
.candidate-card p, .compact-card p, .info-card p, .info-card li {{
    color: {theme["muted"]} !important;
}}
.badge {{
    padding: 5px 10px;
    border-radius: 999px;
    font-weight: 800;
    display: inline-block;
    font-size: 12px;
    margin: 4px 0 6px 0;
}}
.badge-green {{ background-color: #dcfce7; color: #166534; }}
.badge-yellow {{ background-color: #fef9c3; color: #854d0e; }}
.badge-orange {{ background-color: #ffedd5; color: #9a3412; }}
.badge-red {{ background-color: #fee2e2; color: #991b1b; }}
.badge-blue {{ background-color: #dbeafe; color: #1e40af; }}
.badge-gray {{ background-color: #e5e7eb; color: #374151; }}
.small-muted {{ color: {theme["muted"]} !important; font-size: 13px; }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📈 BelegRadar</h1>
    <p>Scan beleggingen op nieuws, momentum, volume, kosten en automatische research-signalen.</p>
    <p><strong>Geen persoonlijk financieel advies — alleen een hulpmiddel om sneller interessante beleggingen te vinden.</strong></p>
</div>
""", unsafe_allow_html=True)

if "force_refresh_token" not in st.session_state:
    st.session_state.force_refresh_token = 0

DEFAULT_WATCHLIST = pd.DataFrame([
    {"ticker":"IBM","naam":"IBM","sector":"AI / Cloud / Enterprise software","keywords":"earnings,guidance,AI,watsonx,cloud,mainframe,consulting,dividend,upgrade,partnership","sector_score":1},
    {"ticker":"INTC","naam":"Intel","sector":"Semiconductors / Foundry","keywords":"earnings,guidance,foundry,AI chip,datacenter,manufacturing,CHIPS Act,upgrade,partnership","sector_score":1},
    {"ticker":"ELI.BR","naam":"Elia Group","sector":"Utilities / Electricity grid","keywords":"earnings,guidance,grid investment,electricity transmission,renewables,energy transition,capex,dividend,regulation","sector_score":1},
    {"ticker":"AED.BR","naam":"Aedifica","sector":"Healthcare real estate / REIT","keywords":"earnings,guidance,healthcare real estate,elderly care,occupancy,dividend,interest rates,portfolio,valuation","sector_score":1},
    {"ticker":"MC.PA","naam":"LVMH","sector":"Luxury goods","keywords":"earnings,guidance,luxury,China demand,pricing power,margin,brands,Fashion,upgrade","sector_score":1},
    {"ticker":"ASML.AS","naam":"ASML","sector":"Semiconductor equipment","keywords":"earnings,guidance,EUV,High-NA,orders,chip demand,AI chips,China,upgrade","sector_score":2},
    {"ticker":"MSFT","naam":"Microsoft","sector":"AI / Cloud","keywords":"earnings,guidance,Azure,AI,Copilot,cloud,OpenAI,datacenter,upgrade","sector_score":2},
    {"ticker":"GOOGL","naam":"Alphabet","sector":"AI / Advertising / Cloud","keywords":"earnings,guidance,AI,Gemini,cloud,advertising,YouTube,upgrade","sector_score":2},
    {"ticker":"AMZN","naam":"Amazon","sector":"E-commerce / Cloud / AI","keywords":"earnings,guidance,AWS,AI,retail,margin,cloud,advertising,upgrade","sector_score":2},
    {"ticker":"AMD","naam":"AMD","sector":"Semiconductors / AI chips","keywords":"earnings,guidance,AI chip,GPU,datacenter,MI300,MI400,server,upgrade","sector_score":2},
    {"ticker":"AVGO","naam":"Broadcom","sector":"Semiconductors / AI infrastructure","keywords":"earnings,guidance,AI chip,custom silicon,datacenter,VMware,networking,upgrade,partnership","sector_score":2},
    {"ticker":"TSM","naam":"Taiwan Semiconductor","sector":"Semiconductor foundry","keywords":"earnings,guidance,AI chips,foundry,advanced nodes,Apple,NVIDIA,capex,upgrade","sector_score":2},
    {"ticker":"NVDA","naam":"NVIDIA","sector":"AI / Semiconductors","keywords":"earnings,guidance,AI chip,GPU,datacenter,Blackwell,CUDA,upgrade,demand","sector_score":2},
    {"ticker":"PLTR","naam":"Palantir","sector":"AI software / Data analytics","keywords":"earnings,guidance,AI,AIP,government contracts,commercial growth,defense,upgrade","sector_score":2},
])

SUGGESTION_DB = {
    "IBM": {"ticker":"IBM","naam":"IBM","sector":"AI / Cloud / Enterprise software","keywords":"earnings,guidance,AI,watsonx,cloud,mainframe,consulting,dividend,upgrade,partnership","sector_score":1},
    "INTEL": {"ticker":"INTC","naam":"Intel","sector":"Semiconductors / Foundry","keywords":"earnings,guidance,foundry,AI chip,datacenter,manufacturing,CHIPS Act,upgrade,partnership","sector_score":1},
    "INTC": {"ticker":"INTC","naam":"Intel","sector":"Semiconductors / Foundry","keywords":"earnings,guidance,foundry,AI chip,datacenter,manufacturing,CHIPS Act,upgrade,partnership","sector_score":1},
    "ELIA": {"ticker":"ELI.BR","naam":"Elia Group","sector":"Utilities / Electricity grid","keywords":"earnings,guidance,grid investment,electricity transmission,renewables,energy transition,capex,dividend,regulation","sector_score":1},
    "AEDIFICA": {"ticker":"AED.BR","naam":"Aedifica","sector":"Healthcare real estate / REIT","keywords":"earnings,guidance,healthcare real estate,elderly care,occupancy,dividend,interest rates,portfolio,valuation","sector_score":1},
    "LVMH": {"ticker":"MC.PA","naam":"LVMH","sector":"Luxury goods","keywords":"earnings,guidance,luxury,China demand,pricing power,margin,brands,Fashion,upgrade","sector_score":1},
    "ASML": {"ticker":"ASML.AS","naam":"ASML","sector":"Semiconductor equipment","keywords":"earnings,guidance,EUV,High-NA,orders,chip demand,AI chips,China,upgrade","sector_score":2},
    "MICROSOFT": {"ticker":"MSFT","naam":"Microsoft","sector":"AI / Cloud","keywords":"earnings,guidance,Azure,AI,Copilot,cloud,OpenAI,datacenter,upgrade","sector_score":2},
    "MSFT": {"ticker":"MSFT","naam":"Microsoft","sector":"AI / Cloud","keywords":"earnings,guidance,Azure,AI,Copilot,cloud,OpenAI,datacenter,upgrade","sector_score":2},
    "GOOGLE": {"ticker":"GOOGL","naam":"Alphabet","sector":"AI / Advertising / Cloud","keywords":"earnings,guidance,AI,Gemini,cloud,advertising,YouTube,upgrade","sector_score":2},
    "ALPHABET": {"ticker":"GOOGL","naam":"Alphabet","sector":"AI / Advertising / Cloud","keywords":"earnings,guidance,AI,Gemini,cloud,advertising,YouTube,upgrade","sector_score":2},
    "AMAZON": {"ticker":"AMZN","naam":"Amazon","sector":"E-commerce / Cloud / AI","keywords":"earnings,guidance,AWS,AI,retail,margin,cloud,advertising,upgrade","sector_score":2},
    "AMD": {"ticker":"AMD","naam":"AMD","sector":"Semiconductors / AI chips","keywords":"earnings,guidance,AI chip,GPU,datacenter,MI300,MI400,server,upgrade","sector_score":2},
    "BROADCOM": {"ticker":"AVGO","naam":"Broadcom","sector":"Semiconductors / AI infrastructure","keywords":"earnings,guidance,AI chip,custom silicon,datacenter,VMware,networking,upgrade,partnership","sector_score":2},
    "TSMC": {"ticker":"TSM","naam":"Taiwan Semiconductor","sector":"Semiconductor foundry","keywords":"earnings,guidance,AI chips,foundry,advanced nodes,Apple,NVIDIA,capex,upgrade","sector_score":2},
    "NVIDIA": {"ticker":"NVDA","naam":"NVIDIA","sector":"AI / Semiconductors","keywords":"earnings,guidance,AI chip,GPU,datacenter,Blackwell,CUDA,upgrade,demand","sector_score":2},
    "PALANTIR": {"ticker":"PLTR","naam":"Palantir","sector":"AI software / Data analytics","keywords":"earnings,guidance,AI,AIP,government contracts,commercial growth,defense,upgrade","sector_score":2},
    "TESLA": {"ticker":"TSLA","naam":"Tesla","sector":"EV / AI / Robotics","keywords":"earnings,guidance,deliveries,FSD,robotaxi,energy,upgrade,AI,autonomous driving","sector_score":2},
    "APPLE": {"ticker":"AAPL","naam":"Apple","sector":"Consumer tech / AI","keywords":"earnings,guidance,iPhone,services,AI,upgrade,buyback,China","sector_score":1},
    "META": {"ticker":"META","naam":"Meta Platforms","sector":"AI / Social media / Advertising","keywords":"earnings,guidance,AI,ads,Instagram,WhatsApp,metaverse,upgrade","sector_score":2},
    "COCA COLA": {"ticker":"KO","naam":"Coca-Cola","sector":"Consumer defensive / Dividend","keywords":"earnings,guidance,dividend,consumer staples,pricing,margin,upgrade","sector_score":1},
    "SHELL": {"ticker":"SHEL","naam":"Shell","sector":"Energy / Oil & Gas","keywords":"earnings,guidance,oil,gas,LNG,dividend,buyback,energy prices","sector_score":1},
    "BEL20": {"ticker":"^BFX","naam":"BEL 20","sector":"Belgische index","keywords":"Belgium stocks,BEL 20,index,Europe stocks,Brussels","sector_score":1},
    "BEL 20": {"ticker":"^BFX","naam":"BEL 20","sector":"Belgische index","keywords":"Belgium stocks,BEL 20,index,Europe stocks,Brussels","sector_score":1},
    "S&P 500": {"ticker":"^GSPC","naam":"S&P 500","sector":"US index","keywords":"S&P 500,index,US stocks,market,rate cuts,inflation","sector_score":1},
    "NASDAQ": {"ticker":"^IXIC","naam":"Nasdaq Composite","sector":"US tech index","keywords":"Nasdaq,index,technology,AI,semiconductors,rate cuts","sector_score":2},
}

CATALYST_WORDS = [
    "earnings","guidance","upgrade","partnership","contract","approval","acquisition","merger",
    "record revenue","beat expectations","raises outlook","ETF inflows","rate cut","FDA approval",
    "launch","investment","buy rating","outperform","price target","revenue growth"
]
NEGATIVE_WORDS = [
    "downgrade","misses","lawsuit","investigation","cuts outlook","decline","falls","warning",
    "delay","ban","regulatory probe","sell rating","underperform","fraud","fine","weak demand"
]

BROKER_PRESETS = {
    "Zelf invullen": {"buy_fixed": 2.0, "sell_fixed": 2.0, "buy_pct": 0.0, "sell_pct": 0.0, "spread": 0.2},
    "Lage kosten / neo-broker": {"buy_fixed": 1.0, "sell_fixed": 1.0, "buy_pct": 0.0, "sell_pct": 0.0, "spread": 0.15},
    "Gemiddelde bank/broker": {"buy_fixed": 7.5, "sell_fixed": 7.5, "buy_pct": 0.0, "sell_pct": 0.0, "spread": 0.25},
    "Hoge bankkosten": {"buy_fixed": 15.0, "sell_fixed": 15.0, "buy_pct": 0.0, "sell_pct": 0.0, "spread": 0.35},
    "Procentuele kosten": {"buy_fixed": 0.0, "sell_fixed": 0.0, "buy_pct": 0.25, "sell_pct": 0.25, "spread": 0.25},
}

def find_suggestion(query):
    q = str(query).strip().upper()
    if not q:
        return None
    if q in SUGGESTION_DB:
        return SUGGESTION_DB[q]
    for key, val in SUGGESTION_DB.items():
        if q in key or q in val["naam"].upper() or q == val["ticker"].upper():
            return val
    return None

def normalize_watchlist(df):
    required = ["ticker", "naam", "sector", "keywords", "sector_score"]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    df = df[required].copy()
    df["ticker"] = df["ticker"].astype(str).str.strip()
    df["naam"] = df["naam"].astype(str).str.strip()
    df["sector"] = df["sector"].astype(str).str.strip()
    df["keywords"] = df["keywords"].astype(str).str.strip()
    df["sector_score"] = pd.to_numeric(df["sector_score"], errors="coerce").fillna(1).astype(int).clip(0, 2)
    df = df[df["ticker"] != ""]
    df = df.drop_duplicates(subset=["ticker"], keep="last")
    return df.reset_index(drop=True)

def init_watchlist_state():
    if "watchlist_df" not in st.session_state:
        st.session_state.watchlist_df = DEFAULT_WATCHLIST.copy()

def add_asset_to_watchlist(ticker, naam, sector, keywords, sector_score):
    init_watchlist_state()
    new_row = pd.DataFrame([{
        "ticker": ticker.strip().upper(),
        "naam": naam.strip() if naam.strip() else ticker.strip().upper(),
        "sector": sector.strip() if sector.strip() else "Zelf toegevoegd",
        "keywords": keywords.strip() if keywords.strip() else "earnings,guidance,upgrade,partnership,AI,growth",
        "sector_score": int(sector_score),
    }])
    st.session_state.watchlist_df = normalize_watchlist(pd.concat([st.session_state.watchlist_df, new_row], ignore_index=True))

def remove_asset_from_watchlist(ticker):
    init_watchlist_state()
    ticker = ticker.strip().upper()
    st.session_state.watchlist_df = st.session_state.watchlist_df[
        st.session_state.watchlist_df["ticker"].astype(str).str.upper() != ticker
    ].reset_index(drop=True)

def load_watchlist():
    init_watchlist_state()
    uploaded = st.sidebar.file_uploader("Upload je eigen watchlist CSV", type=["csv"])
    if uploaded is not None:
        st.session_state.watchlist_df = normalize_watchlist(pd.read_csv(uploaded))
    return normalize_watchlist(st.session_state.watchlist_df.copy())

def action_badge(action):
    classes = {
        "STERK RESEARCH-SIGNAAL": "badge-green",
        "SERIEUS ANALYSEREN": "badge-yellow",
        "WACHT OP VOLUME": "badge-orange",
        "WATCHLIST": "badge-blue",
        "ALLEEN VOLGEN": "badge-gray",
        "VERMIJDEN": "badge-red",
        "OPPASSEN": "badge-orange",
    }
    return f'<span class="badge {classes.get(action, "badge-gray")}">{action}</span>'

@st.cache_data(ttl=900, show_spinner=False)
def google_news_cached(query, max_items=8, refresh_token=0):
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return [{"title": e.get("title",""), "link": e.get("link",""), "published": e.get("published","")} for e in feed.entries[:max_items]]

@st.cache_data(ttl=900, show_spinner=False)
def get_price_data_cached(ticker, refresh_token=0):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if data.empty:
            return None
        return data.dropna()
    except Exception:
        return None

def google_news(query, max_items=8):
    return google_news_cached(query, max_items, st.session_state.force_refresh_token)

def get_price_data(ticker):
    return get_price_data_cached(ticker, st.session_state.force_refresh_token)

def safe_float(value):
    try:
        if hasattr(value, "iloc"):
            return float(value.iloc[0])
        return float(value)
    except Exception:
        return None

def score_price_volume(data):
    if data is None or len(data) < 50:
        return {"price_score":0,"volume_score":0,"trend":"Onvoldoende data","last_close":None,"pct_7d":None,"pct_30d":None,"volume_ratio":None,"sma20":None,"sma50":None}

    close = data["Close"]
    volume = data["Volume"]
    last_close = safe_float(close.iloc[-1])
    close_7d_ago = safe_float(close.iloc[-8]) if len(close) >= 8 else None
    close_30d_ago = safe_float(close.iloc[-31]) if len(close) >= 31 else None
    sma20 = safe_float(close.rolling(20).mean().iloc[-1])
    sma50 = safe_float(close.rolling(50).mean().iloc[-1])
    avg_vol20 = safe_float(volume.rolling(20).mean().iloc[-1])
    last_vol = safe_float(volume.iloc[-1])

    pct_7d = ((last_close / close_7d_ago) - 1) * 100 if last_close and close_7d_ago else None
    pct_30d = ((last_close / close_30d_ago) - 1) * 100 if last_close and close_30d_ago else None
    volume_ratio = last_vol / avg_vol20 if last_vol and avg_vol20 else None

    price_score = 0
    if last_close and sma20 and last_close > sma20:
        price_score += 1
    if last_close and sma50 and last_close > sma50:
        price_score += 1

    volume_score = 0
    if volume_ratio is not None:
        if volume_ratio > 1.5:
            volume_score = 2
        elif volume_ratio > 1.1:
            volume_score = 1

    if last_close and sma20 and sma50:
        if last_close > sma20 and last_close > sma50:
            trend = "Sterk: boven 20- en 50-daags gemiddelde"
        elif last_close > sma20:
            trend = "Redelijk: boven 20-daags, maar niet boven 50-daags"
        elif last_close > sma50:
            trend = "Twijfelachtig: boven 50-daags, onder 20-daags"
        else:
            trend = "Zwak: onder 20- en 50-daags gemiddelde"
    else:
        trend = "Onbekend"

    return {"price_score":price_score,"volume_score":volume_score,"trend":trend,"last_close":last_close,"pct_7d":pct_7d,"pct_30d":pct_30d,"volume_ratio":volume_ratio,"sma20":sma20,"sma50":sma50}

def score_news(news_items, custom_keywords):
    text = " ".join([n["title"] for n in news_items]).lower()
    custom = [k.strip().lower() for k in str(custom_keywords).split(",") if k.strip()]
    catalyst_hits = [w for w in CATALYST_WORDS if w.lower() in text]
    keyword_hits = [w for w in custom if w in text]
    negative_hits = [w for w in NEGATIVE_WORDS if w.lower() in text]

    catalyst_score = 2 if len(catalyst_hits) >= 2 or len(keyword_hits) >= 2 else 1 if len(catalyst_hits) >= 1 or len(keyword_hits) >= 1 else 0
    if negative_hits:
        catalyst_score = max(0, catalyst_score - 1)
    return {"catalyst_score":catalyst_score,"catalyst_hits":catalyst_hits,"keyword_hits":keyword_hits,"negative_hits":negative_hits}

def risk_reward_score(pct_7d, pct_30d, volume_ratio):
    if pct_7d is None:
        return 0
    if pct_7d > 18 or (pct_30d is not None and pct_30d > 35):
        return 0
    if -3 <= pct_7d <= 10:
        return 2
    if pct_7d > 10 and volume_ratio is not None and volume_ratio >= 1.5:
        return 1
    if pct_7d > 10:
        return 1
    return 1

def long_term_score(sector_score, price_score, pct_30d, name, sector):
    # Proxy-score, geen fundamentele waardering. Geeft alleen een ruwe kwaliteit/stabiliteit-inschatting.
    quality_names = ["Microsoft","ASML","Alphabet","Amazon","IBM","LVMH","Broadcom","Taiwan Semiconductor","NVIDIA","Apple","Coca-Cola"]
    stability_sectors = ["Consumer", "Utilities", "Healthcare", "Luxury", "Cloud", "Semiconductor"]
    score = 0
    score += min(sector_score, 2)
    score += 2 if any(q.lower() in name.lower() for q in quality_names) else 1
    score += 1 if any(s.lower() in sector.lower() for s in stability_sectors) else 0
    score += 1 if price_score >= 1 else 0
    if pct_30d is not None and -15 <= pct_30d <= 25:
        score += 2
    elif pct_30d is not None and pct_30d > 40:
        score += 0
    else:
        score += 1
    return min(score, 10)

def automatic_decision(total, catalyst_score, price_score, volume_score, rr_score, negative_hits, pct_7d, volume_ratio):
    reasons, warnings = [], []
    if negative_hits:
        warnings.append("Er zijn negatieve woorden in het nieuws gevonden.")
    if volume_ratio is not None and volume_ratio < 1.0:
        warnings.append("Volume is lager dan normaal; bevestiging is zwak.")
    if pct_7d is not None and pct_7d > 15:
        warnings.append("Koers is al hard gestegen; kans op pullback is groter.")
    if rr_score == 0:
        warnings.append("Risk/reward is zwak door overextensie of onvoldoende data.")
    reasons.append("Sterke katalysator-score." if catalyst_score >= 2 else "Mogelijke katalysator, maar niet supersterk." if catalyst_score == 1 else "Geen duidelijke katalysator gevonden.")
    reasons.append("Koerstrend is positief." if price_score >= 2 else "Koerstrend is redelijk." if price_score == 1 else "Koerstrend is zwak of onduidelijk.")
    reasons.append("Volume bevestigt sterk." if volume_score >= 2 else "Volume bevestigt licht." if volume_score == 1 else "Volume bevestigt niet.")
    warning_text = " ".join(warnings) if warnings else "Geen grote waarschuwingen gevonden."
    if total >= 8 and catalyst_score >= 1 and price_score >= 1 and volume_score >= 1 and rr_score >= 1 and not negative_hits:
        return "STERK RESEARCH-SIGNAAL", "Sterk research-signaal. Alleen verder onderzoeken met instap, exit en maximale positie.", " ".join(reasons), warning_text
    if total >= 8 and volume_score == 0:
        return "WACHT OP VOLUME", "Sterke score, maar wacht liever op hoger volume voordat je koopt.", " ".join(reasons), warning_text
    if total >= 7 and rr_score >= 1 and not negative_hits:
        return "SERIEUS ANALYSEREN", "Interessant genoeg om serieus te analyseren, maar geen automatische koop.", " ".join(reasons), warning_text
    if total >= 6:
        return "WATCHLIST", "Zet op je watchlist. Wacht op betere bevestiging.", " ".join(reasons), warning_text
    if total >= 4:
        return "ALLEEN VOLGEN", "Volgen, maar nu niet sterk genoeg.", " ".join(reasons), warning_text
    return "VERMIJDEN", "Niet interessant volgens deze scan.", " ".join(reasons), warning_text

def position_suggestion(action):
    if action == "STERK RESEARCH-SIGNAAL":
        return "Onderzoek eerst. Algemene risicoregel: begin klein en gebruik geen te grote positie."
    if action == "WACHT OP VOLUME":
        return "Wacht tot volume-ratio boven 1.1x komt; boven 1.5x is sterker."
    if action == "SERIEUS ANALYSEREN":
        return "Eerst nieuws openen en instap/stop-loss bepalen."
    if action == "WATCHLIST":
        return "Nu niet kopen; later opnieuw scannen."
    return "Geen positie nemen volgens deze scan."

def bereken_kosten_per_asset(laatste_koers, orderbedrag, aankoopkost_vast, verkoopkost_vast, aankoopkost_pct, verkoopkost_pct, spread_pct):
    if laatste_koers is None or laatste_koers <= 0 or orderbedrag <= 0:
        return {"aantal_stuks": None, "aankoopkosten_totaal": None, "verkoopkosten_totaal": None, "kosten_totaal": None, "kosten_pct_order": None, "netto_aankoopprijs_per_stuk": None, "break_even_prijs": None, "nodige_stijging_pct": None}
    aantal_stuks = orderbedrag / laatste_koers
    spread_kost_totaal = orderbedrag * spread_pct / 100
    aankoop_pct_kost = orderbedrag * aankoopkost_pct / 100
    verkoop_pct_kost = orderbedrag * verkoopkost_pct / 100
    aankoopkosten_totaal = aankoopkost_vast + aankoop_pct_kost + (spread_kost_totaal / 2)
    verkoopkosten_totaal = verkoopkost_vast + verkoop_pct_kost + (spread_kost_totaal / 2)
    kosten_totaal = aankoopkosten_totaal + verkoopkosten_totaal
    kosten_pct_order = (kosten_totaal / orderbedrag) * 100
    netto_aankoopprijs_per_stuk = laatste_koers + (aankoopkosten_totaal / aantal_stuks)
    break_even_prijs = laatste_koers + (kosten_totaal / aantal_stuks)
    nodige_stijging_pct = ((break_even_prijs / laatste_koers) - 1) * 100
    return {"aantal_stuks": aantal_stuks, "aankoopkosten_totaal": aankoopkosten_totaal, "verkoopkosten_totaal": verkoopkosten_totaal, "kosten_totaal": kosten_totaal, "kosten_pct_order": kosten_pct_order, "netto_aankoopprijs_per_stuk": netto_aankoopprijs_per_stuk, "break_even_prijs": break_even_prijs, "nodige_stijging_pct": nodige_stijging_pct}


def init_paper_portfolio():
    if "paper_cash" not in st.session_state:
        st.session_state.paper_cash = 10000.0
    if "paper_positions" not in st.session_state:
        st.session_state.paper_positions = []

def get_latest_price_from_df(ticker, df):
    try:
        row = df[df["Ticker"].astype(str).str.upper() == str(ticker).upper()].iloc[0]
        price = row["Prijs per stuk"]
        if pd.notna(price):
            return float(price)
    except Exception:
        pass
    data = score_price_volume(get_price_data(ticker))
    return data["last_close"]

def paper_buy(ticker, name, amount, price):
    init_paper_portfolio()
    if amount <= 0:
        return False, "Vul een bedrag groter dan 0 in."
    if price is None or price <= 0:
        return False, "Geen geldige koers gevonden voor deze ticker."
    if amount > st.session_state.paper_cash:
        return False, "Je hebt niet genoeg oefencash."
    shares = amount / price
    st.session_state.paper_cash -= amount
    st.session_state.paper_positions.append({
        "ticker": ticker,
        "name": name,
        "shares": shares,
        "buy_price": price,
        "invested": amount,
        "buy_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    })
    return True, f"Virtueel gekocht: {shares:.4f} stuks {ticker} voor €{amount:.2f}."

def paper_sell(position_index, current_price):
    init_paper_portfolio()
    if position_index < 0 or position_index >= len(st.session_state.paper_positions):
        return False, "Positie niet gevonden."
    pos = st.session_state.paper_positions[position_index]
    if current_price is None or current_price <= 0:
        return False, "Geen geldige huidige koers."
    value = pos["shares"] * current_price
    st.session_state.paper_cash += value
    sold = st.session_state.paper_positions.pop(position_index)
    pnl = value - sold["invested"]
    return True, f"Virtueel verkocht: {sold['ticker']} voor €{value:.2f}. Resultaat: €{pnl:.2f}."


# Sidebar
st.sidebar.header("Verversen")
auto_refresh = st.sidebar.toggle("Automatisch verversen", value=False)
refresh_minutes = st.sidebar.selectbox("Ververs elke", [5, 10, 15, 30, 60], index=2)
if st.sidebar.button("🔄 Nu data verversen"):
    st.session_state.force_refresh_token += 1
    google_news_cached.clear()
    get_price_data_cached.clear()
    st.success("Data wordt opnieuw opgehaald.")

if auto_refresh:
    refresh_ms = refresh_minutes * 60 * 1000
    st.markdown(f"<script>setTimeout(function() {{ window.location.reload(); }}, {refresh_ms});</script>", unsafe_allow_html=True)

init_watchlist_state()
st.sidebar.header("Belegging toevoegen")
st.sidebar.caption("Typ alleen een naam of ticker. De app vult ticker, sector, keywords en score automatisch in als hij de belegging kent.")

with st.sidebar.expander("🔎 Zoek & voeg toe", expanded=True):
    search_query = st.text_input("Zoek belegging", placeholder="Bijv. Microsoft, IBM, LVMH, BEL20")
    suggestion = find_suggestion(search_query)
    if suggestion:
        st.success(f"Suggestie gevonden: {suggestion['naam']} ({suggestion['ticker']})")
        suggested_ticker = st.text_input("Ticker", value=suggestion["ticker"])
        suggested_name = st.text_input("Naam", value=suggestion["naam"])
        suggested_sector = st.text_input("Sector", value=suggestion["sector"])
        suggested_keywords = st.text_input("Keywords", value=suggestion["keywords"])
        suggested_sector_score = st.selectbox("Sector-score", [0, 1, 2], index=int(suggestion["sector_score"]))
    else:
        st.info("Geen automatische suggestie gevonden. Je kunt hem handmatig toevoegen.")
        suggested_ticker = st.text_input("Ticker", value=search_query.upper() if search_query else "")
        suggested_name = st.text_input("Naam", value=search_query if search_query else "")
        suggested_sector = st.text_input("Sector", value="Zelf toegevoegd")
        suggested_keywords = st.text_input("Keywords", value="earnings,guidance,upgrade,partnership,AI,growth")
        suggested_sector_score = st.selectbox("Sector-score", [0, 1, 2], index=1)
    if st.button("Toevoegen aan watchlist"):
        if suggested_ticker.strip():
            add_asset_to_watchlist(suggested_ticker, suggested_name, suggested_sector, suggested_keywords, suggested_sector_score)
            st.success(f"{suggested_name} ({suggested_ticker}) toegevoegd.")
        else:
            st.error("Vul eerst een ticker in.")

with st.sidebar.expander("🧹 Belegging verwijderen", expanded=False):
    current_tickers = st.session_state.watchlist_df["ticker"].astype(str).tolist()
    ticker_to_remove = st.selectbox("Kies ticker", current_tickers) if current_tickers else None
    if st.button("Verwijderen") and ticker_to_remove:
        remove_asset_from_watchlist(ticker_to_remove)
        st.success(f"{ticker_to_remove} verwijderd.")

if st.sidebar.button("Reset naar standaardlijst"):
    st.session_state.watchlist_df = DEFAULT_WATCHLIST.copy()
    st.success("Watchlist gereset.")

watchlist = load_watchlist()

st.sidebar.header("Instellingen")
max_news = st.sidebar.slider("Nieuwsberichten per asset", 3, 15, 8)
extra_query = st.sidebar.text_input("Extra zoekterm", value="stock news")

st.sidebar.header("Kosten per transactie")
preset_name = st.sidebar.selectbox("Brokerkosten preset", list(BROKER_PRESETS.keys()), index=0)
preset = BROKER_PRESETS[preset_name]
orderbedrag = st.sidebar.number_input("Gemiddeld orderbedrag (€)", min_value=1.0, value=1000.0, step=50.0)
aankoopkost_vast = st.sidebar.number_input("Vaste aankoopkost (€)", min_value=0.0, value=float(preset["buy_fixed"]), step=0.5)
verkoopkost_vast = st.sidebar.number_input("Vaste verkoopkost (€)", min_value=0.0, value=float(preset["sell_fixed"]), step=0.5)
aankoopkost_pct = st.sidebar.number_input("Aankoopkost (%)", min_value=0.0, value=float(preset["buy_pct"]), step=0.05)
verkoopkost_pct = st.sidebar.number_input("Verkoopkost (%)", min_value=0.0, value=float(preset["sell_pct"]), step=0.05)
spread_pct = st.sidebar.number_input("Spread/slippage (%)", min_value=0.0, value=float(preset["spread"]), step=0.05)
belasting_winst_pct = st.sidebar.number_input("Belasting op winst (%)", min_value=0.0, value=0.0, step=0.5)

st.sidebar.download_button("Download huidige watchlist", watchlist.to_csv(index=False), file_name="mijn_watchlist.csv", mime="text/csv")
st.sidebar.download_button("Download standaard-watchlist", DEFAULT_WATCHLIST.to_csv(index=False), file_name="watchlist_template.csv", mime="text/csv")

st.caption(f"Laatst geladen: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
st.warning("Deze tool geeft geen persoonlijk financieel advies. Scores zijn automatisch gegenereerd op basis van openbare data, nieuwswoorden, koersdata, volume en kosteninstellingen.")
st.caption("Snelheidsmodus: koersdata en nieuws worden tijdelijk gecachet. Gebruik links 'Nu data verversen' als je alles opnieuw wilt ophalen.")

required_cols = {"ticker", "naam", "sector", "keywords", "sector_score"}
missing = required_cols - set(watchlist.columns)
if missing:
    st.error(f"Je CSV mist kolommen: {', '.join(missing)}")
    st.stop()

results = []
with st.spinner("Data laden... eerste keer kan wat langer duren, daarna gebruikt de app cache."):
    for _, row in watchlist.iterrows():
        ticker = str(row["ticker"]).strip()
        name = str(row["naam"]).strip()
        sector = str(row["sector"]).strip()
        keywords = str(row["keywords"]).strip()
        news = google_news(f"{name} {ticker} {extra_query}", max_items=max_news)
        pv = score_price_volume(get_price_data(ticker))
        ns = score_news(news, keywords)
        try:
            sector_score = max(0, min(int(row["sector_score"]), 2))
        except Exception:
            sector_score = 0
        rr_score = risk_reward_score(pv["pct_7d"], pv["pct_30d"], pv["volume_ratio"])
        short_total = sector_score + ns["catalyst_score"] + pv["price_score"] + pv["volume_score"] + rr_score
        lt_score = long_term_score(sector_score, pv["price_score"], pv["pct_30d"], name, sector)
        action, decision, reasons, warnings = automatic_decision(short_total, ns["catalyst_score"], pv["price_score"], pv["volume_score"], rr_score, ns["negative_hits"], pv["pct_7d"], pv["volume_ratio"])
        kosten = bereken_kosten_per_asset(pv["last_close"], orderbedrag, aankoopkost_vast, verkoopkost_vast, aankoopkost_pct, verkoopkost_pct, spread_pct)
        score_breakdown = f"Sector {sector_score}/2 + Katalysator {ns['catalyst_score']}/2 + Trend {pv['price_score']}/2 + Volume {pv['volume_score']}/2 + Risk/reward {rr_score}/2 = {short_total}/10"
        use_case = "Trade / kort-middellang" if short_total >= 7 and lt_score < 7 else "Langere termijn research" if lt_score >= 7 and short_total < 7 else "Trade én research" if short_total >= 7 and lt_score >= 7 else "Alleen volgen"
        results.append({
            "Ticker": ticker, "Naam": name, "Sector": sector, "Actie": action, "Beoordeling": decision,
            "Korte termijn score": short_total, "Lange termijn score": lt_score, "Geschikt als": use_case,
            "Score-uitleg": score_breakdown,
            "Sector-score": sector_score, "Katalysator-score": ns["catalyst_score"],
            "Koers-score": pv["price_score"], "Volume-score": pv["volume_score"], "Risk/reward-score": rr_score,
            "Trend": pv["trend"], "7d %": None if pv["pct_7d"] is None else round(pv["pct_7d"], 2),
            "30d %": None if pv["pct_30d"] is None else round(pv["pct_30d"], 2),
            "Volume ratio": None if pv["volume_ratio"] is None else round(pv["volume_ratio"], 2),
            "Prijs per stuk": None if pv["last_close"] is None else round(pv["last_close"], 2),
            "Aandelen bij order": None if kosten["aantal_stuks"] is None else round(kosten["aantal_stuks"], 4),
            "Aankoopkosten": None if kosten["aankoopkosten_totaal"] is None else round(kosten["aankoopkosten_totaal"], 2),
            "Verkoopkosten": None if kosten["verkoopkosten_totaal"] is None else round(kosten["verkoopkosten_totaal"], 2),
            "Totale kosten": None if kosten["kosten_totaal"] is None else round(kosten["kosten_totaal"], 2),
            "Kosten %": None if kosten["kosten_pct_order"] is None else round(kosten["kosten_pct_order"], 2),
            "Netto aankoopprijs/stuk": None if kosten["netto_aankoopprijs_per_stuk"] is None else round(kosten["netto_aankoopprijs_per_stuk"], 2),
            "Break-even prijs": None if kosten["break_even_prijs"] is None else round(kosten["break_even_prijs"], 2),
            "Nodige stijging %": None if kosten["nodige_stijging_pct"] is None else round(kosten["nodige_stijging_pct"], 2),
            "Laatste koers": None if pv["last_close"] is None else round(pv["last_close"], 2),
            "SMA20": None if pv["sma20"] is None else round(pv["sma20"], 2),
            "SMA50": None if pv["sma50"] is None else round(pv["sma50"], 2),
            "Catalyst hits": ", ".join(ns["catalyst_hits"][:5]), "Keyword hits": ", ".join(ns["keyword_hits"][:5]),
            "Negatief nieuws": ", ".join(ns["negative_hits"][:5]), "Redenen": reasons, "Waarschuwingen": warnings,
            "Positie-regel": position_suggestion(action), "Nieuws": news
        })

df = pd.DataFrame(results).sort_values(["Korte termijn score", "Volume-score", "Koers-score"], ascending=False)

# Filters
with st.expander("🔎 Filters", expanded=False):
    f1, f2, f3, f4 = st.columns(4)
    min_score = f1.slider("Min. korte termijn score", 0, 10, 0)
    min_lt_score = f2.slider("Min. lange termijn score", 0, 10, 0)
    action_filter = f3.multiselect("Actie", sorted(df["Actie"].unique().tolist()), default=[])
    sector_filter = f4.multiselect("Sector bevat", sorted(df["Sector"].unique().tolist()), default=[])
    sort_choice = st.selectbox("Sorteren op", ["Korte termijn score", "Lange termijn score", "Volume ratio", "Kosten %", "7d %", "30d %"], index=0)

filtered = df.copy()
filtered = filtered[filtered["Korte termijn score"] >= min_score]
filtered = filtered[filtered["Lange termijn score"] >= min_lt_score]
if action_filter:
    filtered = filtered[filtered["Actie"].isin(action_filter)]
if sector_filter:
    filtered = filtered[filtered["Sector"].isin(sector_filter)]
filtered = filtered.sort_values(sort_choice, ascending=False if sort_choice != "Kosten %" else True)

best = filtered.iloc[0] if not filtered.empty else None
col1, col2, col3 = st.columns(3)
col1.metric("Gescand", len(df))
col2.metric("Beste zichtbare score", "n.v.t." if best is None else f"{best['Ticker']} — {best['Korte termijn score']}/10")
col3.metric("Sterke signalen", int(df["Actie"].isin(["STERK RESEARCH-SIGNAAL", "SERIEUS ANALYSEREN", "WACHT OP VOLUME"]).sum()))

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["📊 Overzicht", "📱 Mobiele kaarten", "🔥 Top-signalen", "📰 Details & nieuws", "💼 Portfolio simulatie", "🎮 Oefenportfolio", "🚨 Alerts", "📱 Upload-hulp", "ℹ️ Uitleg"])

with tab1:
    st.subheader("Automatische beoordeling")
    st.dataframe(
        filtered[["Ticker","Naam","Actie","Korte termijn score","Lange termijn score","Geschikt als","Prijs per stuk","Netto aankoopprijs/stuk","Totale kosten","Kosten %","Break-even prijs","Nodige stijging %","7d %","30d %","Volume ratio","Beoordeling"]],
        use_container_width=True,
        hide_index=True
    )
    st.download_button("Download resultaten als CSV", filtered.drop(columns=["Nieuws"]).to_csv(index=False), "scanner_resultaten_v5_3.csv", "text/csv")

with tab2:
    st.subheader("Mobiele kaartweergave")
    st.write("Handiger op gsm dan een brede tabel.")
    for _, row in filtered.iterrows():
        st.markdown(f"""
        <div class="compact-card">
            <h3>{row['Ticker']} — {row['Naam']}</h3>
            {action_badge(row['Actie'])}
            <p><strong>Korte termijn:</strong> {row['Korte termijn score']}/10 | <strong>Lange termijn:</strong> {row['Lange termijn score']}/10</p>
            <p><strong>Prijs:</strong> €{row['Prijs per stuk']} | <strong>Break-even:</strong> €{row['Break-even prijs']} | <strong>Kosten:</strong> {row['Kosten %']}%</p>
            <p><strong>Geschikt als:</strong> {row['Geschikt als']}</p>
            <p>{row['Beoordeling']}</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.subheader("Top 3 volgens BelegRadar")
    top3 = filtered.head(3)
    cols = st.columns(3)
    for idx, (_, row) in enumerate(top3.iterrows()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="candidate-card">
                <h3>{row['Ticker']}</h3>
                <p><strong>{row['Naam']}</strong></p>
                {action_badge(row['Actie'])}
                <p><strong>Kort:</strong> {row['Korte termijn score']}/10 | <strong>Lang:</strong> {row['Lange termijn score']}/10</p>
                <p><strong>Prijs:</strong> €{row['Prijs per stuk']} | <strong>Break-even:</strong> €{row['Break-even prijs']}</p>
                <p class="small-muted">{row['Beoordeling']}</p>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.subheader("Details per belegging")
    for item in results:
        with st.expander(f"{item['Ticker']} — {item['Naam']} — {item['Actie']} — kort {item['Korte termijn score']}/10 | lang {item['Lange termijn score']}/10"):
            st.markdown(action_badge(item["Actie"]), unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Korte termijn", f"{item['Korte termijn score']}/10")
            c2.metric("Lange termijn", f"{item['Lange termijn score']}/10")
            c3.metric("7 dagen", "n.v.t." if item["7d %"] is None else f"{item['7d %']}%")
            c4.metric("Volume ratio", "n.v.t." if item["Volume ratio"] is None else f"{item['Volume ratio']}x")

            st.write("### Score-uitleg")
            st.write(item["Score-uitleg"])
            st.write(f"**Geschikt als:** {item['Geschikt als']}")

            st.write("### Prijs & kosten")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Prijs per stuk", "n.v.t." if item["Prijs per stuk"] is None else f"€{item['Prijs per stuk']}")
            k2.metric("Netto aankoop/stuk", "n.v.t." if item["Netto aankoopprijs/stuk"] is None else f"€{item['Netto aankoopprijs/stuk']}")
            k3.metric("Break-even prijs", "n.v.t." if item["Break-even prijs"] is None else f"€{item['Break-even prijs']}")
            k4.metric("Nodige stijging", "n.v.t." if item["Nodige stijging %"] is None else f"{item['Nodige stijging %']}%")
            st.write(f"Bij een order van **€{orderbedrag:,.2f}** koop je ongeveer **{item['Aandelen bij order']} stuks**. Geschatte totale kosten voor aankoop + verkoop: **€{item['Totale kosten']}** (**{item['Kosten %']}%**).")

            st.write("### Automatische beoordeling")
            st.write(f"**Beoordeling:** {item['Beoordeling']}")
            st.write(f"**Waarom:** {item['Redenen']}")
            st.write(f"**Waarschuwingen:** {item['Waarschuwingen']}")
            st.write(f"**Positie-regel:** {item['Positie-regel']}")

            st.write("### Recent nieuws")
            if item["Nieuws"]:
                for n in item["Nieuws"]:
                    st.markdown(f"- [{n['title']}]({n['link']})  \n  _{n['published']}_")
            else:
                st.write("Geen nieuws gevonden.")

with tab5:
    st.subheader("💼 Portfolio simulatie")
    st.write("Vul per belegging een bedrag in. Deze invoervelden blijven staan nadat je op Enter drukt.")

    if "portfolio_amounts" not in st.session_state:
        st.session_state.portfolio_amounts = {}

    c_reset, c_info = st.columns([1, 3])
    with c_reset:
        if st.button("Reset simulatie"):
            st.session_state.portfolio_amounts = {}
            st.success("Simulatie gereset.")
    with c_info:
        st.caption("Tip: vul bijvoorbeeld 500 in bij MSFT en 300 bij ASML. De resultaten verschijnen direct onder de invoervelden.")

    st.write("### Bedragen invullen")
    sim_rows = []
    visible = df[["Ticker","Naam","Prijs per stuk","Netto aankoopprijs/stuk","Break-even prijs","Kosten %"]].copy()

    for _, row in visible.iterrows():
        ticker = str(row["Ticker"])
        prijs = row["Prijs per stuk"]
        kosten_pct = row["Kosten %"]
        break_even = row["Break-even prijs"]

        with st.expander(f"{ticker} — {row['Naam']} | prijs €{prijs} | kosten {kosten_pct}%", expanded=False):
            amount = st.number_input(
                f"Inleg voor {ticker} (€)",
                min_value=0.0,
                value=float(st.session_state.portfolio_amounts.get(ticker, 0.0)),
                step=50.0,
                key=f"portfolio_amount_{ticker}"
            )
            st.session_state.portfolio_amounts[ticker] = amount

            if amount > 0 and pd.notna(prijs) and prijs > 0:
                estimated_shares = amount / prijs
                estimated_costs = amount * (kosten_pct / 100) if pd.notna(kosten_pct) else 0
                sim_rows.append({
                    "Ticker": ticker,
                    "Naam": row["Naam"],
                    "Inleg (€)": round(amount, 2),
                    "Prijs per stuk": prijs,
                    "Geschatte stuks": round(estimated_shares, 4),
                    "Kosten %": kosten_pct,
                    "Geschatte kosten (€)": round(estimated_costs, 2),
                    "Break-even prijs": break_even,
                })
                st.write(f"Geschatte stuks: **{estimated_shares:.4f}**")
                st.write(f"Geschatte kosten: **€{estimated_costs:.2f}**")
            elif amount > 0:
                st.warning("Geen prijsdata beschikbaar voor deze ticker. Controleer de ticker.")

    st.write("### Resultaat")
    if not sim_rows:
        st.info("Vul hierboven bij één of meer beleggingen een bedrag groter dan 0 in.")
    else:
        valid = pd.DataFrame(sim_rows)
        st.dataframe(valid, use_container_width=True, hide_index=True)
        total_invested = valid["Inleg (€)"].sum()
        total_costs = valid["Geschatte kosten (€)"].sum()
        avg_cost_pct = (total_costs / total_invested * 100) if total_invested > 0 else 0

        p1, p2, p3 = st.columns(3)
        p1.metric("Totale inleg", f"€{total_invested:,.2f}")
        p2.metric("Geschatte totale kosten", f"€{total_costs:,.2f}")
        p3.metric("Gemiddelde kosten %", f"{avg_cost_pct:.2f}%")

        st.download_button(
            "Download portfolio-simulatie",
            valid.to_csv(index=False),
            "portfolio_simulatie.csv",
            "text/csv"
        )


with tab6:
    st.subheader("🎮 Oefenportfolio")
    st.write("Oefen met kopen en verkopen zonder echt geld. De waarde beweegt mee met de actuele koersdata die de app ophaalt.")

    init_paper_portfolio()

    c_start, c_reset = st.columns([2, 1])
    with c_start:
        start_cash = st.number_input("Startkapitaal / oefencash (€)", min_value=100.0, value=float(st.session_state.paper_cash if not st.session_state.paper_positions else st.session_state.paper_cash), step=100.0, help="Pas dit vooral aan als je nog geen posities hebt.")
    with c_reset:
        if st.button("Reset oefenportfolio"):
            st.session_state.paper_cash = 10000.0
            st.session_state.paper_positions = []
            st.success("Oefenportfolio gereset naar €10.000 cash.")

    if not st.session_state.paper_positions and start_cash != st.session_state.paper_cash:
        st.session_state.paper_cash = start_cash

    st.write("### Virtueel kopen")
    buy_cols = st.columns([2, 1, 1])
    tickers_available = df["Ticker"].astype(str).tolist()
    with buy_cols[0]:
        buy_ticker = st.selectbox("Kies belegging", tickers_available)
    selected_row = df[df["Ticker"].astype(str) == buy_ticker].iloc[0]
    current_price = selected_row["Prijs per stuk"]
    with buy_cols[1]:
        st.metric("Huidige prijs", "n.v.t." if pd.isna(current_price) else f"€{float(current_price):.2f}")
    with buy_cols[2]:
        buy_amount = st.number_input("Bedrag kopen (€)", min_value=0.0, value=500.0, step=50.0)

    if st.button("Virtueel kopen"):
        ok, msg = paper_buy(buy_ticker, selected_row["Naam"], buy_amount, None if pd.isna(current_price) else float(current_price))
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.write("### Oefenportfolio resultaat")
    position_rows = []
    total_value = 0.0
    total_invested = 0.0

    for i, pos in enumerate(st.session_state.paper_positions):
        price_now = get_latest_price_from_df(pos["ticker"], df)
        if price_now is None:
            value_now = None
            pnl = None
            pnl_pct = None
        else:
            value_now = pos["shares"] * price_now
            pnl = value_now - pos["invested"]
            pnl_pct = (pnl / pos["invested"] * 100) if pos["invested"] > 0 else 0
            total_value += value_now
        total_invested += pos["invested"]
        position_rows.append({
            "Nr": i,
            "Ticker": pos["ticker"],
            "Naam": pos["name"],
            "Stuks": round(pos["shares"], 4),
            "Koopprijs": round(pos["buy_price"], 2),
            "Huidige prijs": None if price_now is None else round(price_now, 2),
            "Ingelegd": round(pos["invested"], 2),
            "Waarde nu": None if value_now is None else round(value_now, 2),
            "Winst/verlies €": None if pnl is None else round(pnl, 2),
            "Winst/verlies %": None if pnl_pct is None else round(pnl_pct, 2),
            "Gekocht op": pos["buy_time"],
        })

    total_account = st.session_state.paper_cash + total_value
    total_pnl = total_account - (st.session_state.paper_cash + total_invested)  # current value - invested for open positions
    open_pnl = total_value - total_invested
    open_pnl_pct = (open_pnl / total_invested * 100) if total_invested > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cash", f"€{st.session_state.paper_cash:,.2f}")
    m2.metric("Waarde posities", f"€{total_value:,.2f}")
    m3.metric("Totale waarde", f"€{total_account:,.2f}")
    m4.metric("Open winst/verlies", f"€{open_pnl:,.2f}", f"{open_pnl_pct:.2f}%")

    if not position_rows:
        st.info("Je hebt nog geen virtuele posities. Kies hierboven een belegging en klik op 'Virtueel kopen'.")
    else:
        positions_df = pd.DataFrame(position_rows)
        st.dataframe(positions_df, use_container_width=True, hide_index=True)

        st.write("### Virtueel verkopen")
        sell_options = [f"{row['Nr']} — {row['Ticker']} — {row['Stuks']} stuks" for row in position_rows]
        sell_choice = st.selectbox("Kies positie om te verkopen", sell_options)
        sell_index = int(sell_choice.split(" — ")[0])
        sell_current_price = get_latest_price_from_df(st.session_state.paper_positions[sell_index]["ticker"], df)
        if st.button("Virtueel verkopen"):
            ok, msg = paper_sell(sell_index, sell_current_price)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        st.download_button("Download oefenportfolio", positions_df.to_csv(index=False), "oefenportfolio.csv", "text/csv")

    st.caption("Let op: dit oefenportfolio wordt opgeslagen in je huidige Streamlit-sessie. Als de app reset of je cache wordt gewist, kan het verdwijnen. Download je portfolio als CSV als je het wilt bewaren.")


with tab7:
    st.subheader("🚨 Alerts")
    alert_score = st.slider("Alert vanaf korte termijn score", 0, 10, 8)
    alert_volume = st.slider("Alert vanaf volume ratio", 0.0, 3.0, 1.5, 0.1)
    score_alerts = df[df["Korte termijn score"] >= alert_score]
    volume_alerts = df[df["Volume ratio"].fillna(0) >= alert_volume]
    st.write("### Score-alerts")
    if score_alerts.empty:
        st.info("Geen beleggingen boven deze score.")
    else:
        st.dataframe(score_alerts[["Ticker","Naam","Actie","Korte termijn score","Volume ratio","Beoordeling"]], use_container_width=True, hide_index=True)
    st.write("### Volume-alerts")
    if volume_alerts.empty:
        st.info("Geen beleggingen met zo'n hoge volume ratio.")
    else:
        st.dataframe(volume_alerts[["Ticker","Naam","Actie","Korte termijn score","Volume ratio","7d %"]], use_container_width=True, hide_index=True)
    st.caption("Dit zijn alleen alerts op de pagina. E-mail/Telegram alerts zouden een latere uitbreiding zijn.")

with tab8:
    st.subheader("📱 Watchlist maken of uploaden")
    st.markdown("""
    Je hebt twee opties:

    **Optie 1 — makkelijk:** gebruik links in de sidebar **Belegging toevoegen**. Typ alleen een naam zoals Microsoft, IBM, LVMH of BEL20. De app vult de rest automatisch in als hij de belegging kent.

    **Optie 2 — veel tegelijk:** upload een CSV-bestand met meerdere aandelen.

    Een CSV-bestand moet deze 5 kolommen hebben:

    `ticker, naam, sector, keywords, sector_score`
    """)
    voorbeeld = pd.DataFrame([
        {"ticker":"IBM","naam":"IBM","sector":"AI / Cloud","keywords":"earnings,guidance,AI,cloud,upgrade","sector_score":1},
        {"ticker":"INTC","naam":"Intel","sector":"Semiconductors","keywords":"earnings,guidance,AI chip,foundry,datacenter","sector_score":1},
        {"ticker":"ASML.AS","naam":"ASML","sector":"Semiconductor equipment","keywords":"earnings,guidance,EUV,orders,AI chips","sector_score":2},
    ])
    st.dataframe(voorbeeld, use_container_width=True, hide_index=True)
    st.download_button("Download simpel CSV-voorbeeld", voorbeeld.to_csv(index=False), "simpel_watchlist_voorbeeld.csv", "text/csv")

with tab9:
    st.subheader("Hoe de score werkt")
    st.write("""
    De korte-termijnscore loopt van 0 tot 10:

    - Sector-score: 0-2
    - Katalysator-score: 0-2
    - Koers-score: 0-2
    - Volume-score: 0-2
    - Risk/reward-score: 0-2

    De lange-termijnscore is een ruwe proxy en geen echte fundamentele analyse. Hij kijkt onder andere naar sector, stabiliteit, naamkwaliteit en of de koers niet extreem doorgeschoten is.

    Acties zijn bewust geformuleerd als research-signalen, niet als koopadvies.
    """)
    st.warning("Dit dashboard is geen financieel adviseur. Gebruik het om kandidaten te vinden, niet om blind te kopen.")
