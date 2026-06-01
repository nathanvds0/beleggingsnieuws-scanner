import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from urllib.parse import quote_plus
from datetime import datetime

st.set_page_config(page_title="Beleggingsnieuws Scanner v3", layout="wide")

st.title("📈 Beleggingsnieuws Scanner v3")
st.caption("Automatische beoordeling + nieuws + koers/volume. Geen financieel advies.")

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
    {"ticker":"NVDA","naam":"NVIDIA","sector":"AI / Semiconductors","keywords":"earnings,guidance,AI chip,demand,upgrade,partnership","sector_score":2},
    {"ticker":"ASML.AS","naam":"ASML","sector":"Semiconductors","keywords":"earnings,guidance,EUV,chip demand,China,orders","sector_score":2},
    {"ticker":"MSFT","naam":"Microsoft","sector":"AI / Cloud","keywords":"earnings,Azure,AI,Copilot,guidance,partnership","sector_score":2},
    {"ticker":"BTC-USD","naam":"Bitcoin","sector":"Crypto","keywords":"ETF inflows,halving,regulation,institutional,rate cuts","sector_score":1},
    {"ticker":"ETH-USD","naam":"Ethereum","sector":"Crypto","keywords":"ETF,upgrade,staking,DeFi,regulation","sector_score":1},
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

def load_watchlist():
    uploaded = st.sidebar.file_uploader("Upload je eigen watchlist CSV", type=["csv"])
    if uploaded is not None:
        return pd.read_csv(uploaded)
    return DEFAULT_WATCHLIST.copy()

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

def setup_label(score):
    if score >= 8:
        return "Sterke setup"
    if score >= 6:
        return "Interessant"
    if score >= 4:
        return "Alleen volgen"
    return "Negeren"

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

watchlist = load_watchlist()
required_cols = {"ticker", "naam", "sector", "keywords", "sector_score"}
missing = required_cols - set(watchlist.columns)
if missing:
    st.error(f"Je CSV mist kolommen: {', '.join(missing)}")
    st.stop()

st.sidebar.header("Instellingen")
max_news = st.sidebar.slider("Nieuwsberichten per asset", 3, 15, 8)
extra_query = st.sidebar.text_input("Extra zoekterm", value="stock news")
st.sidebar.download_button("Download voorbeeld-watchlist", DEFAULT_WATCHLIST.to_csv(index=False), file_name="watchlist_template.csv", mime="text/csv")

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
        results.append({
            "Ticker": ticker, "Naam": name, "Sector": sector, "Actie": action, "Beoordeling": decision,
            "Totaalscore": total, "Label": setup_label(total), "Sector-score": sector_score,
            "Katalysator-score": ns["catalyst_score"], "Koers-score": pv["price_score"], "Volume-score": pv["volume_score"],
            "Risk/reward-score": rr_score, "Trend": pv["trend"],
            "7d %": None if pv["pct_7d"] is None else round(pv["pct_7d"], 2),
            "30d %": None if pv["pct_30d"] is None else round(pv["pct_30d"], 2),
            "Volume ratio": None if pv["volume_ratio"] is None else round(pv["volume_ratio"], 2),
            "Laatste koers": None if pv["last_close"] is None else round(pv["last_close"], 2),
            "SMA20": None if pv["sma20"] is None else round(pv["sma20"], 2),
            "SMA50": None if pv["sma50"] is None else round(pv["sma50"], 2),
            "Catalyst hits": ", ".join(ns["catalyst_hits"][:5]), "Keyword hits": ", ".join(ns["keyword_hits"][:5]),
            "Negatief nieuws": ", ".join(ns["negative_hits"][:5]), "Redenen": reasons, "Waarschuwingen": warnings,
            "Positie-regel": position_suggestion(action), "Nieuws": news
        })

df = pd.DataFrame(results).sort_values(["Totaalscore", "Volume-score", "Koers-score"], ascending=False)

st.subheader("Automatische beoordeling")
st.dataframe(df[["Ticker","Naam","Actie","Totaalscore","Beoordeling","7d %","30d %","Volume ratio","Trend"]], use_container_width=True, hide_index=True)

st.download_button("Download resultaten als CSV", df.drop(columns=["Nieuws"]).to_csv(index=False), "scanner_resultaten_v3.csv", "text/csv")

st.subheader("Top-kandidaten")
top = df[df["Actie"].isin(["KOOP-KANDIDAAT", "SERIEUS ANALYSEREN", "WACHT OP VOLUME"])]
if top.empty:
    st.info("Geen sterke kandidaten gevonden volgens deze scan.")
else:
    for _, row in top.iterrows():
        st.write(f"**{row['Ticker']} — {row['Naam']}**")
        st.write(f"Actie: **{row['Actie']}** | Score: **{row['Totaalscore']}/10**")
        st.write(row["Beoordeling"])
        st.write(f"Waarschuwing: {row['Waarschuwingen']}")
        st.divider()

st.subheader("Details per asset")
for item in results:
    with st.expander(f"{item['Ticker']} — {item['Naam']} — {item['Actie']} — score {item['Totaalscore']}/10"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Totaalscore", f"{item['Totaalscore']}/10")
        c2.metric("7 dagen", "n.v.t." if item["7d %"] is None else f"{item['7d %']}%")
        c3.metric("30 dagen", "n.v.t." if item["30d %"] is None else f"{item['30d %']}%")
        c4.metric("Volume ratio", "n.v.t." if item["Volume ratio"] is None else f"{item['Volume ratio']}x")
        st.write("### Automatische beoordeling")
        st.write(f"**Actie:** {item['Actie']}")
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

st.divider()
st.write("""
### Auto-refresh
Als auto-refresh aanstaat, laadt de website zichzelf opnieuw na het gekozen aantal minuten.
Bij elke herlaadbeurt worden nieuws en koersdata opnieuw opgehaald.

### Belangrijke waarschuwing
Dit dashboard is een scanner en beoordelingssysteem. Het is geen financieel adviseur.
Gebruik het om kandidaten te vinden, niet om blind te kopen.

- **KOOP-KANDIDAAT** = verder onderzoeken en alleen kopen met plan.
- **WACHT OP VOLUME** = nog niet haasten.
- **WATCHLIST / ALLEEN VOLGEN** = niet kopen volgens deze scan.
- **VERMIJDEN** = overslaan.
""")