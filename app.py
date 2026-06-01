import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from urllib.parse import quote_plus
from datetime import datetime

st.set_page_config(page_title="BelegRadar v4.7", page_icon="📈", layout="wide")

THEMES = {
    "🌈 Neon donker": {
        "hero": "linear-gradient(135deg, #111827, #7c3aed, #db2777)",
        "accent": "#ec4899",
        "accent2": "#8b5cf6",
        "app_bg": "#070b14",
        "sidebar_bg": "#111827",
        "panel_bg": "#0f172a",
        "card_bg": "#111827",
        "card_border": "#7c3aed",
        "text": "#f9fafb",
        "muted": "#d1d5db",
        "table_header": "#1f2937",
        "input_bg": "#0b1220"
    },
    "🔵 Blauw professioneel": {
        "hero": "linear-gradient(135deg, #0f172a, #1d4ed8)",
        "accent": "#2563eb",
        "accent2": "#38bdf8",
        "app_bg": "#eff6ff",
        "sidebar_bg": "#dbeafe",
        "panel_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_border": "#93c5fd",
        "text": "#0f172a",
        "muted": "#334155",
        "table_header": "#dbeafe",
        "input_bg": "#ffffff"
    },
    "🟢 Groen finance": {
        "hero": "linear-gradient(135deg, #052e16, #16a34a)",
        "accent": "#22c55e",
        "accent2": "#84cc16",
        "app_bg": "#ecfdf5",
        "sidebar_bg": "#dcfce7",
        "panel_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_border": "#86efac",
        "text": "#052e16",
        "muted": "#166534",
        "table_header": "#dcfce7",
        "input_bg": "#ffffff"
    },
    "🟣 Paars premium": {
        "hero": "linear-gradient(135deg, #1e1b4b, #7e22ce)",
        "accent": "#a855f7",
        "accent2": "#ec4899",
        "app_bg": "#faf5ff",
        "sidebar_bg": "#f3e8ff",
        "panel_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_border": "#d8b4fe",
        "text": "#1e1b4b",
        "muted": "#581c87",
        "table_header": "#f3e8ff",
        "input_bg": "#ffffff"
    },
    "🔥 Oranje energie": {
        "hero": "linear-gradient(135deg, #431407, #ea580c)",
        "accent": "#f97316",
        "accent2": "#facc15",
        "app_bg": "#fff7ed",
        "sidebar_bg": "#ffedd5",
        "panel_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_border": "#fdba74",
        "text": "#431407",
        "muted": "#9a3412",
        "table_header": "#ffedd5",
        "input_bg": "#ffffff"
    },
}

selected_theme = st.sidebar.selectbox("🎨 Kleurthema", list(THEMES.keys()), index=0)
theme = THEMES[selected_theme]

st.markdown(f"""
<style>
/* Hele app achtergrond */
.stApp {{
    background: {theme["app_bg"]} !important;
    color: {theme["text"]} !important;
}}

/* Hoofdcontainer */
.block-container {{
    padding-top: 1.4rem;
    max-width: 1250px;
    color: {theme["text"]} !important;
}}

/* Sidebar volledig meekleuren */
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

/* Header */
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

/* Algemene tekst */
h1, h2, h3, h4, h5, h6, p, label, span {{
    color: {theme["text"]};
}}

/* Metrics */
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

/* Tabs */
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

/* Buttons */
.stButton > button,
.stDownloadButton > button {{
    background: linear-gradient(135deg, {theme["accent"]}, {theme["accent2"]}) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
}}
.stButton > button:hover,
.stDownloadButton > button:hover {{
    filter: brightness(1.08);
    transform: translateY(-1px);
}}

/* Expander */
details {{
    background: {theme["panel_bg"]} !important;
    border: 1px solid {theme["card_border"]} !important;
    border-radius: 14px !important;
    color: {theme["text"]} !important;
}}

/* Inputs hoofdgedeelte */
input, textarea, select {{
    background: {theme["input_bg"]} !important;
    color: {theme["text"]} !important;
}}

/* Dataframe / tabel */
div[data-testid="stDataFrame"] {{
    border: 1px solid {theme["card_border"]};
    border-radius: 14px;
    overflow: hidden;
}}
div[data-testid="stDataFrame"] * {{
    color: {theme["text"]};
}}

/* Kaarten */
.candidate-card {{
    background: {theme["card_bg"]};
    color: {theme["text"]};
    padding: 16px 18px;
    border-radius: 18px;
    border: 1px solid {theme["card_border"]};
    margin-bottom: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.14);
}}
.candidate-card h3 {{
    color: {theme["text"]} !important;
    font-size: 20px;
    margin: 0 0 8px 0;
}}
.candidate-card p {{
    color: {theme["muted"]} !important;
    margin: 6px 0;
    font-size: 14px;
}}
.candidate-card strong {{ color: {theme["text"]} !important; }}

.compact-card {{
    background: {theme["card_bg"]};
    color: {theme["text"]};
    padding: 14px 16px;
    border-radius: 16px;
    border: 1px solid {theme["card_border"]};
    margin-bottom: 10px;
    box-shadow: 0 5px 16px rgba(0,0,0,0.10);
}}
.compact-card p {{ color: {theme["muted"]} !important; margin: 4px 0; }}
.compact-card strong {{ color: {theme["text"]} !important; }}

.info-card {{
    background: {theme["card_bg"]};
    color: {theme["text"]};
    padding: 18px;
    border-radius: 16px;
    border: 1px solid {theme["card_border"]};
    margin-bottom: 14px;
}}
.info-card p, .info-card li {{ color: {theme["muted"]} !important; }}
.info-card h3 {{ color: {theme["text"]} !important; }}

/* Badges blijven contrasterend */
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

/* Meldingen iets mooier */
div[data-testid="stAlert"] {{
    border-radius: 14px;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📈 BelegRadar</h1>
    <p>Scan aandelen op nieuws, momentum, volume en automatische research-signalen.</p>
    <p><strong>Geen financieel advies — alleen een hulpmiddel om sneller interessante beleggingen te vinden.</strong></p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("Auto-refresh")
auto_refresh = st.sidebar.toggle("Automatisch verversen", value=True)
refresh_minutes = st.sidebar.selectbox("Ververs elke", [5, 10, 15, 30, 60], index=2)

if auto_refresh:
    refresh_ms = refresh_minutes * 60 * 1000
    st.markdown(
        f"""
        <script>
            setTimeout(function() {{
                window.location.reload();
            }}, {refresh_ms});
        </script>
        """,
        unsafe_allow_html=True
    )

st.caption(f"Laatst geladen: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

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

CATALYST_WORDS = [
    "earnings","guidance","upgrade","partnership","contract","approval","acquisition","merger",
    "record revenue","beat expectations","raises outlook","ETF inflows","rate cut","FDA approval",
    "launch","investment","buy rating","outperform","price target","revenue growth"
]
NEGATIVE_WORDS = [
    "downgrade","misses","lawsuit","investigation","cuts outlook","decline","falls","warning",
    "delay","ban","regulatory probe","sell rating","underperform","fraud","fine","weak demand"
]

def action_badge(action):
    classes = {
        "KOOP-KANDIDAAT": "badge-green",
        "SERIEUS ANALYSEREN": "badge-yellow",
        "WACHT OP VOLUME": "badge-orange",
        "WATCHLIST": "badge-blue",
        "ALLEEN VOLGEN": "badge-gray",
        "VERMIJDEN": "badge-red",
        "OPPASSEN": "badge-orange",
    }
    return f'<span class="badge {classes.get(action, "badge-gray")}">{action}</span>'

SUGGESTION_DB = {
    "IBM": {"ticker":"IBM","naam":"IBM","sector":"AI / Cloud / Enterprise software","keywords":"earnings,guidance,AI,watsonx,cloud,mainframe,consulting,dividend,upgrade,partnership","sector_score":1},
    "INTEL": {"ticker":"INTC","naam":"Intel","sector":"Semiconductors / Foundry","keywords":"earnings,guidance,foundry,AI chip,datacenter,manufacturing,CHIPS Act,upgrade,partnership","sector_score":1},
    "INTC": {"ticker":"INTC","naam":"Intel","sector":"Semiconductors / Foundry","keywords":"earnings,guidance,foundry,AI chip,datacenter,manufacturing,CHIPS Act,upgrade,partnership","sector_score":1},
    "ELIA": {"ticker":"ELI.BR","naam":"Elia Group","sector":"Utilities / Electricity grid","keywords":"earnings,guidance,grid investment,electricity transmission,renewables,energy transition,capex,dividend,regulation","sector_score":1},
    "ELIA GROUP": {"ticker":"ELI.BR","naam":"Elia Group","sector":"Utilities / Electricity grid","keywords":"earnings,guidance,grid investment,electricity transmission,renewables,energy transition,capex,dividend,regulation","sector_score":1},
    "AEDIFICA": {"ticker":"AED.BR","naam":"Aedifica","sector":"Healthcare real estate / REIT","keywords":"earnings,guidance,healthcare real estate,elderly care,occupancy,dividend,interest rates,portfolio,valuation","sector_score":1},
    "LVMH": {"ticker":"MC.PA","naam":"LVMH","sector":"Luxury goods","keywords":"earnings,guidance,luxury,China demand,pricing power,margin,brands,Fashion,upgrade","sector_score":1},
    "ASML": {"ticker":"ASML.AS","naam":"ASML","sector":"Semiconductor equipment","keywords":"earnings,guidance,EUV,High-NA,orders,chip demand,AI chips,China,upgrade","sector_score":2},
    "MICROSOFT": {"ticker":"MSFT","naam":"Microsoft","sector":"AI / Cloud","keywords":"earnings,guidance,Azure,AI,Copilot,cloud,OpenAI,datacenter,upgrade","sector_score":2},
    "MSFT": {"ticker":"MSFT","naam":"Microsoft","sector":"AI / Cloud","keywords":"earnings,guidance,Azure,AI,Copilot,cloud,OpenAI,datacenter,upgrade","sector_score":2},
    "ALPHABET": {"ticker":"GOOGL","naam":"Alphabet","sector":"AI / Advertising / Cloud","keywords":"earnings,guidance,AI,Gemini,cloud,advertising,YouTube,upgrade","sector_score":2},
    "GOOGLE": {"ticker":"GOOGL","naam":"Alphabet","sector":"AI / Advertising / Cloud","keywords":"earnings,guidance,AI,Gemini,cloud,advertising,YouTube,upgrade","sector_score":2},
    "AMAZON": {"ticker":"AMZN","naam":"Amazon","sector":"E-commerce / Cloud / AI","keywords":"earnings,guidance,AWS,AI,retail,margin,cloud,advertising,upgrade","sector_score":2},
    "AMD": {"ticker":"AMD","naam":"AMD","sector":"Semiconductors / AI chips","keywords":"earnings,guidance,AI chip,GPU,datacenter,MI300,MI400,server,upgrade","sector_score":2},
    "BROADCOM": {"ticker":"AVGO","naam":"Broadcom","sector":"Semiconductors / AI infrastructure","keywords":"earnings,guidance,AI chip,custom silicon,datacenter,VMware,networking,upgrade,partnership","sector_score":2},
    "TSMC": {"ticker":"TSM","naam":"Taiwan Semiconductor","sector":"Semiconductor foundry","keywords":"earnings,guidance,AI chips,foundry,advanced nodes,Apple,NVIDIA,capex,upgrade","sector_score":2},
    "NVIDIA": {"ticker":"NVDA","naam":"NVIDIA","sector":"AI / Semiconductors","keywords":"earnings,guidance,AI chip,GPU,datacenter,Blackwell,CUDA,upgrade,demand","sector_score":2},
    "PALANTIR": {"ticker":"PLTR","naam":"Palantir","sector":"AI software / Data analytics","keywords":"earnings,guidance,AI,AIP,government contracts,commercial growth,defense,upgrade","sector_score":2},
    "TESLA": {"ticker":"TSLA","naam":"Tesla","sector":"EV / AI / Robotics","keywords":"earnings,guidance,deliveries,FSD,robotaxi,energy,upgrade,AI,autonomous driving","sector_score":2},
    "APPLE": {"ticker":"AAPL","naam":"Apple","sector":"Consumer tech / AI","keywords":"earnings,guidance,iPhone,services,AI,upgrade,buyback,China","sector_score":1},
    "META": {"ticker":"META","naam":"Meta Platforms","sector":"AI / Social media / Advertising","keywords":"earnings,guidance,AI,ads,Instagram,WhatsApp,metaverse,upgrade","sector_score":2},
    "BEL 20": {"ticker":"^BFX","naam":"BEL 20","sector":"Belgische index","keywords":"Belgium stocks,BEL 20,index,Europe stocks,Brussels","sector_score":1},
    "BEL20": {"ticker":"^BFX","naam":"BEL 20","sector":"Belgische index","keywords":"Belgium stocks,BEL 20,index,Europe stocks,Brussels","sector_score":1},
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
    df["sector_score"] = pd.to_numeric(df["sector_score"], errors="coerce").fillna(1).astype(int)
    df["sector_score"] = df["sector_score"].clip(0, 2)
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

def google_news(query, max_items=8):
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return [{"title": e.get("title",""), "link": e.get("link",""), "published": e.get("published","")} for e in feed.entries[:max_items]]

def get_price_data(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if data.empty:
            return None
        return data.dropna()
    except Exception:
        return None

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
        return "KOOP-KANDIDAAT", "Koop-kandidaat voor verder onderzoek. Alleen kopen met instap, stop-loss en maximale positie.", " ".join(reasons), warning_text
    if total >= 8 and volume_score == 0:
        return "WACHT OP VOLUME", "Sterke score, maar wacht liever op hoger volume voordat je koopt.", " ".join(reasons), warning_text
    if total >= 7 and rr_score >= 1 and not negative_hits:
        return "SERIEUS ANALYSEREN", "Interessant genoeg om serieus te analyseren, maar nog geen automatische koop.", " ".join(reasons), warning_text
    if total >= 6:
        return "WATCHLIST", "Zet op je watchlist. Wacht op betere bevestiging.", " ".join(reasons), warning_text
    if total >= 4:
        return "ALLEEN VOLGEN", "Volgen, maar nu niet sterk genoeg om te kopen.", " ".join(reasons), warning_text
    return "VERMIJDEN", "Niet interessant volgens deze scan.", " ".join(reasons), warning_text

def position_suggestion(action):
    if action == "KOOP-KANDIDAAT":
        return "Algemene risicoregel: begin klein. Bijvoorbeeld 25-50% van je normale positie, niet alles in één keer."
    if action == "WACHT OP VOLUME":
        return "Wacht tot volume-ratio boven 1.1x komt; boven 1.5x is sterker."
    if action == "SERIEUS ANALYSEREN":
        return "Eerst nieuws openen en instap/stop-loss bepalen."
    if action == "WATCHLIST":
        return "Nu niet kopen; later opnieuw scannen."
    return "Geen positie nemen volgens deze scan."

init_watchlist_state()

st.sidebar.header("Belegging toevoegen")
st.sidebar.caption("Typ alleen een naam of ticker. De app vult ticker, sector, keywords en score automatisch in als hij de belegging kent.")

with st.sidebar.expander("🔎 Zoek & voeg toe", expanded=True):
    search_query = st.text_input("Zoek belegging", placeholder="Bijv. Microsoft, IBM, LVMH, BEL20, Tesla")
    suggestion = find_suggestion(search_query)

    if suggestion:
        st.success(f"Suggestie gevonden: {suggestion['naam']} ({suggestion['ticker']})")
        suggested_ticker = st.text_input("Ticker", value=suggestion["ticker"])
        suggested_name = st.text_input("Naam", value=suggestion["naam"])
        suggested_sector = st.text_input("Sector", value=suggestion["sector"])
        suggested_keywords = st.text_input("Keywords", value=suggestion["keywords"])
        suggested_sector_score = st.selectbox("Sector-score", [0, 1, 2], index=int(suggestion["sector_score"]))
    else:
        st.info("Geen automatische suggestie gevonden. Je kunt hem nog steeds handmatig toevoegen.")
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
required_cols = {"ticker", "naam", "sector", "keywords", "sector_score"}
missing = required_cols - set(watchlist.columns)
if missing:
    st.error(f"Je CSV mist kolommen: {', '.join(missing)}")
    st.stop()

st.sidebar.header("Instellingen")
max_news = st.sidebar.slider("Nieuwsberichten per asset", 3, 15, 8)
extra_query = st.sidebar.text_input("Extra zoekterm", value="stock news")

st.sidebar.header("Kosten per transactie")
orderbedrag = st.sidebar.number_input("Gemiddeld orderbedrag (€)", min_value=1.0, value=1000.0, step=50.0)
aankoopkost_vast = st.sidebar.number_input("Vaste aankoopkost (€)", min_value=0.0, value=2.0, step=0.5)
verkoopkost_vast = st.sidebar.number_input("Vaste verkoopkost (€)", min_value=0.0, value=2.0, step=0.5)
aankoopkost_pct = st.sidebar.number_input("Aankoopkost (%)", min_value=0.0, value=0.00, step=0.05)
verkoopkost_pct = st.sidebar.number_input("Verkoopkost (%)", min_value=0.0, value=0.00, step=0.05)
spread_pct = st.sidebar.number_input("Spread/slippage (%)", min_value=0.0, value=0.20, step=0.05)
belasting_winst_pct = st.sidebar.number_input("Belasting op winst (%)", min_value=0.0, value=0.0, step=0.5)

st.sidebar.caption("Deze kosten zijn schattingen. Vul je eigen brokerkosten in.")
st.sidebar.download_button("Download huidige watchlist", watchlist.to_csv(index=False), file_name="mijn_watchlist.csv", mime="text/csv")
st.sidebar.download_button("Download standaard-watchlist", DEFAULT_WATCHLIST.to_csv(index=False), file_name="watchlist_template.csv", mime="text/csv")

def bereken_kosten_per_asset(laatste_koers, orderbedrag, aankoopkost_vast, verkoopkost_vast, aankoopkost_pct, verkoopkost_pct, spread_pct):
    if laatste_koers is None or laatste_koers <= 0 or orderbedrag <= 0:
        return {
            "aantal_stuks": None,
            "aankoopkosten_totaal": None,
            "verkoopkosten_totaal": None,
            "kosten_totaal": None,
            "kosten_pct_order": None,
            "netto_aankoopprijs_per_stuk": None,
            "break_even_prijs": None,
            "nodige_stijging_pct": None,
        }

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

    return {
        "aantal_stuks": aantal_stuks,
        "aankoopkosten_totaal": aankoopkosten_totaal,
        "verkoopkosten_totaal": verkoopkosten_totaal,
        "kosten_totaal": kosten_totaal,
        "kosten_pct_order": kosten_pct_order,
        "netto_aankoopprijs_per_stuk": netto_aankoopprijs_per_stuk,
        "break_even_prijs": break_even_prijs,
        "nodige_stijging_pct": nodige_stijging_pct,
    }

results = []
with st.spinner("Laatste nieuws en koersdata ophalen..."):
    for _, row in watchlist.iterrows():
        ticker, name, sector, keywords = str(row["ticker"]).strip(), str(row["naam"]).strip(), str(row["sector"]).strip(), str(row["keywords"]).strip()
        news = google_news(f"{name} {ticker} {extra_query}", max_items=max_news)
        pv = score_price_volume(get_price_data(ticker))
        ns = score_news(news, keywords)
        try:
            sector_score = max(0, min(int(row["sector_score"]), 2))
        except Exception:
            sector_score = 0
        rr_score = risk_reward_score(pv["pct_7d"], pv["pct_30d"], pv["volume_ratio"])
        total = sector_score + ns["catalyst_score"] + pv["price_score"] + pv["volume_score"] + rr_score
        action, decision, reasons, warnings = automatic_decision(total, ns["catalyst_score"], pv["price_score"], pv["volume_score"], rr_score, ns["negative_hits"], pv["pct_7d"], pv["volume_ratio"])
        kosten = bereken_kosten_per_asset(
            pv["last_close"],
            orderbedrag,
            aankoopkost_vast,
            verkoopkost_vast,
            aankoopkost_pct,
            verkoopkost_pct,
            spread_pct
        )
        results.append({
            "Ticker": ticker, "Naam": name, "Sector": sector, "Actie": action, "Beoordeling": decision,
            "Totaalscore": total, "Sector-score": sector_score, "Katalysator-score": ns["catalyst_score"],
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

df = pd.DataFrame(results).sort_values(["Totaalscore", "Volume-score", "Koers-score"], ascending=False)

best = df.iloc[0] if not df.empty else None
col1, col2, col3 = st.columns(3)
col1.metric("Gescand", len(df))
col2.metric("Beste score", "n.v.t." if best is None else f"{best['Ticker']} — {best['Totaalscore']}/10")
col3.metric("Sterke kandidaten", int(df["Actie"].isin(["KOOP-KANDIDAAT", "SERIEUS ANALYSEREN", "WACHT OP VOLUME"]).sum()))

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Overzicht", "🔥 Top-kandidaten", "📰 Details & nieuws", "💸 Kosten-uitleg", "📱 CSV upload-hulp", "ℹ️ Uitleg"])

with tab1:
    st.subheader("Automatische beoordeling")
    st.dataframe(
        df[["Ticker","Naam","Actie","Totaalscore","Prijs per stuk","Netto aankoopprijs/stuk","Totale kosten","Kosten %","Break-even prijs","Nodige stijging %","7d %","30d %","Volume ratio","Beoordeling"]],
        use_container_width=True,
        hide_index=True
    )
    st.download_button("Download resultaten als CSV", df.drop(columns=["Nieuws"]).to_csv(index=False), "scanner_resultaten_v4_7.csv", "text/csv")

with tab2:
    st.subheader("Top 3 volgens BelegRadar")
    top3 = df.head(3)
    cols = st.columns(3)
    for idx, (_, row) in enumerate(top3.iterrows()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="candidate-card">
                <h3>{row['Ticker']}</h3>
                <p><strong>{row['Naam']}</strong></p>
                {action_badge(row['Actie'])}
                <p><strong>Score:</strong> {row['Totaalscore']}/10</p>
                <p><strong>7d:</strong> {row['7d %']}% &nbsp; <strong>30d:</strong> {row['30d %']}%</p>
                <p><strong>Prijs:</strong> €{row['Prijs per stuk']} | <strong>Netto/stuk:</strong> €{row['Netto aankoopprijs/stuk']}</p>
                <p><strong>Break-even:</strong> €{row['Break-even prijs']} | <strong>Nodig:</strong> {row['Nodige stijging %']}%</p>
                <p><strong>Volume:</strong> {row['Volume ratio']}x</p>
                <p class="small-muted">{row['Beoordeling']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.subheader("Sterke kandidaten")
    top = df[df["Actie"].isin(["KOOP-KANDIDAAT", "SERIEUS ANALYSEREN", "WACHT OP VOLUME"])]
    if top.empty:
        st.info("Geen sterke kandidaten gevonden volgens deze scan.")
    else:
        for _, row in top.iterrows():
            st.markdown(f"""
            <div class="compact-card">
                <strong>{row['Ticker']} — {row['Naam']}</strong><br>
                {action_badge(row['Actie'])}
                <p><strong>Score:</strong> {row['Totaalscore']}/10 | <strong>Prijs:</strong> €{row['Prijs per stuk']} | <strong>Netto/stuk:</strong> €{row['Netto aankoopprijs/stuk']}</p>
                <p><strong>Break-even:</strong> €{row['Break-even prijs']} | <strong>Nodige stijging:</strong> {row['Nodige stijging %']}%</p>
                <p>{row['Beoordeling']}</p>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("Details per belegging")
    for item in results:
        with st.expander(f"{item['Ticker']} — {item['Naam']} — {item['Actie']} — score {item['Totaalscore']}/10"):
            st.markdown(action_badge(item["Actie"]), unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Totaalscore", f"{item['Totaalscore']}/10")
            c2.metric("7 dagen", "n.v.t." if item["7d %"] is None else f"{item['7d %']}%")
            c3.metric("30 dagen", "n.v.t." if item["30d %"] is None else f"{item['30d %']}%")
            c4.metric("Volume ratio", "n.v.t." if item["Volume ratio"] is None else f"{item['Volume ratio']}x")

            st.write("### Prijs & kosten")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Prijs per stuk", "n.v.t." if item["Prijs per stuk"] is None else f"€{item['Prijs per stuk']}")
            k2.metric("Netto aankoop/stuk", "n.v.t." if item["Netto aankoopprijs/stuk"] is None else f"€{item['Netto aankoopprijs/stuk']}")
            k3.metric("Break-even prijs", "n.v.t." if item["Break-even prijs"] is None else f"€{item['Break-even prijs']}")
            k4.metric("Nodige stijging", "n.v.t." if item["Nodige stijging %"] is None else f"{item['Nodige stijging %']}%")

            st.write(f"Bij een order van **€{orderbedrag:,.2f}** koop je ongeveer **{item['Aandelen bij order']} stuks**. Geschatte totale kosten voor aankoop + verkoop: **€{item['Totale kosten']}** (**{item['Kosten %']}%** van je order).")

            st.write("### Automatische beoordeling")
            st.write(f"**Beoordeling:** {item['Beoordeling']}")
            st.write(f"**Waarom:** {item['Redenen']}")
            st.write(f"**Waarschuwingen:** {item['Waarschuwingen']}")
            st.write(f"**Positie-regel:** {item['Positie-regel']}")
            st.write("### Data")
            st.write("**Sector:**", item["Sector"])
            st.write("**Trend:**", item["Trend"])
            st.write("**Laatste koers:**", item["Laatste koers"])
            st.write("**SMA20:**", item["SMA20"])
            st.write("**SMA50:**", item["SMA50"])
            st.write("**Catalyst hits:**", item["Catalyst hits"] or "Geen")
            st.write("**Keyword hits:**", item["Keyword hits"] or "Geen")
            st.write("**Negatieve signalen:**", item["Negatief nieuws"] or "Geen")
            st.write("### Recent nieuws")
            if item["Nieuws"]:
                for n in item["Nieuws"]:
                    st.markdown(f"- [{n['title']}]({n['link']})  \\n  _{n['published']}_")
            else:
                st.write("Geen nieuws gevonden.")

with tab4:
    st.subheader("💸 Kosten-uitleg")
    st.write("De kosten worden nu automatisch naast elke belegging berekend op basis van je instellingen links in de sidebar.")

    st.markdown("""
    ### Wat betekenen de nieuwe kolommen?

    - **Prijs per stuk**: de laatst opgehaalde koers van Yahoo Finance.
    - **Netto aankoopprijs/stuk**: prijs per aandeel inclusief geschatte aankoopkosten en halve spread.
    - **Totale kosten**: geschatte aankoopkosten + verkoopkosten + spread/slippage.
    - **Kosten %**: hoeveel procent van je order naar kosten gaat.
    - **Break-even prijs**: vanaf welke prijs je ongeveer uit de kosten bent.
    - **Nodige stijging %**: hoeveel het aandeel moet stijgen voor je netto ongeveer break-even staat.

    Voorbeeld: als een aandeel bruto 5% stijgt, maar je totale kosten 1%, dan hou je ongeveer 4% netto over vóór eventuele belastingen.
    """)

    st.info("Wil je de kosten aanpassen? Gebruik links in de sidebar de velden bij 'Kosten per transactie'.")
    st.warning("De prijsdata en kosten zijn schattingen. Check altijd je echte broker/bank-app voordat je koopt.")

with tab5:
    st.subheader("📱 Watchlist maken of uploaden")
    st.markdown("""
    Je hebt nu twee opties:

    **Optie 1 — makkelijk:** gebruik links in de sidebar **Belegging toevoegen**. Typ alleen een naam zoals Microsoft, IBM of LVMH. De app vult de rest automatisch in als hij de belegging kent.

    **Optie 2 — veel tegelijk:** upload een CSV-bestand met meerdere aandelen.

    Een CSV-bestand moet deze 5 kolommen hebben:

    `ticker, naam, sector, keywords, sector_score`
    """)

    st.markdown("""
    <div class="info-card">
    <h3>Wat betekent elke kolom?</h3>
    <ul>
        <li><strong>ticker</strong>: de beurscode, bijvoorbeeld IBM, INTC, ASML.AS, ELI.BR, MC.PA</li>
        <li><strong>naam</strong>: de gewone naam, bijvoorbeeld Microsoft</li>
        <li><strong>sector</strong>: zelf gekozen beschrijving, bijvoorbeeld AI / Cloud</li>
        <li><strong>keywords</strong>: woorden waarop de scanner nieuws controleert, gescheiden door komma's</li>
        <li><strong>sector_score</strong>: 0, 1 of 2. Gebruik 2 voor sterke/hype sectoren, 1 normaal, 0 zwak/onduidelijk</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    voorbeeld = pd.DataFrame([
        {"ticker":"IBM","naam":"IBM","sector":"AI / Cloud","keywords":"earnings,guidance,AI,cloud,upgrade","sector_score":1},
        {"ticker":"INTC","naam":"Intel","sector":"Semiconductors","keywords":"earnings,guidance,AI chip,foundry,datacenter","sector_score":1},
        {"ticker":"ASML.AS","naam":"ASML","sector":"Semiconductor equipment","keywords":"earnings,guidance,EUV,orders,AI chips","sector_score":2},
    ])
    st.dataframe(voorbeeld, use_container_width=True, hide_index=True)
    st.download_button("Download simpel CSV-voorbeeld", voorbeeld.to_csv(index=False), "simpel_watchlist_voorbeeld.csv", "text/csv")

    st.markdown("""
    ### Makkelijkste manier met je gsm
    1. Open de website op je gsm.
    2. Open links de sidebar.
    3. Ga naar **Belegging toevoegen**.
    4. Vul alleen de naam of ticker in, bijvoorbeeld `Microsoft`, `IBM`, `LVMH`, `BEL20` of `ASML`.
    5. Klik op **Toevoegen aan watchlist**.

    ### Veel beleggingen tegelijk uploaden met je gsm
    1. Download het voorbeeldbestand hierboven.
    2. Open het in Google Sheets, Excel of Numbers.
    3. Pas de regels aan of voeg nieuwe aandelen toe.
    4. Sla/exporteer het bestand als **CSV**.
    5. Ga terug naar deze website.
    6. Klik links op **Upload** en kies je CSV-bestand.

    ### Ticker voorbeelden
    - Amerikaanse aandelen: `IBM`, `INTC`, `MSFT`, `NVDA`
    - Nederlandse aandelen: `ASML.AS`, `ADYEN.AS`, `INGA.AS`
    - Belgische aandelen: `ELI.BR`, `AED.BR`
    - Franse aandelen: `MC.PA`
    - Crypto: `BTC-USD`, `ETH-USD`
    """)

with tab6:
    st.subheader("Hoe de score werkt")
    st.write("""
    De score loopt van 0 tot 10 en kijkt naar vijf onderdelen:

    - Sector-score: zit het aandeel in een sterke of interessante sector?
    - Katalysator-score: is er relevant nieuws of zijn er belangrijke keywords?
    - Koers-score: staat de koers boven belangrijke gemiddelden?
    - Volume-score: bevestigt het volume de beweging?
    - Risk/reward-score: is de beweging niet al te ver doorgeschoten?

    Betekenis van acties:

    - KOOP-KANDIDAAT: sterk research-signaal, maar nog steeds zelf controleren.
    - SERIEUS ANALYSEREN: interessant, maar geen automatische koop.
    - WACHT OP VOLUME: score goed, maar volume bevestigt nog niet.
    - WATCHLIST: volgen.
    - ALLEEN VOLGEN: nog zwak.
    - VERMIJDEN: overslaan volgens deze scan.
    """)
    st.warning("Dit dashboard is geen financieel adviseur. Gebruik het om kandidaten te vinden, niet om blind te kopen.")