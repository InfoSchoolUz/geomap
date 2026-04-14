import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="World Explorer Pro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

:root {
    --bg: #050b1a;
    --card: #0d1b2e;
    --border: #1e3a5f;
    --accent: #00d4ff;
    --text: #c8e6ff;
    --dim: #4a7a9b;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Rajdhani', sans-serif;
}

.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00d4ff, #7b2fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: 4px;
    margin-bottom: 0.2rem;
}

.sub-title {
    text-align: center;
    color: var(--dim);
    font-size: 0.95rem;
    letter-spacing: 2px;
    margin-bottom: 1.5rem;
}

.info-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 20px rgba(0,212,255,0.05);
}

.info-card h3 {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    color: var(--accent);
    margin-bottom: 0.8rem;
    letter-spacing: 2px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    padding: 0.35rem 0;
    border-bottom: 1px solid rgba(30,58,95,0.5);
    font-size: 0.92rem;
}

.stat-label { color: var(--dim); }
.stat-value { color: var(--accent); font-weight: 600; text-align: right; }

.metric-box {
    background: linear-gradient(135deg, #0d1b2e, #0a2240);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    margin: 0.3rem;
}

.metric-num {
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    color: var(--accent);
    font-weight: 700;
}

.metric-label {
    font-size: 0.8rem;
    color: var(--dim);
    letter-spacing: 1px;
    margin-top: 0.2rem;
}

.flag-display {
    font-size: 5rem;
    text-align: center;
    padding: 1rem 0;
    filter: drop-shadow(0 0 15px rgba(0,212,255,0.4));
}

.country-name {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    color: white;
    text-align: center;
    font-weight: 700;
    letter-spacing: 2px;
}

.country-official {
    text-align: center;
    color: var(--dim);
    font-size: 0.85rem;
    margin-top: 0.2rem;
}

.flag-image-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(30,58,95,0.7);
    border-radius: 12px;
    padding: 0.75rem;
    margin-bottom: 1rem;
    text-align: center;
}

[data-testid="stSidebar"] {
    background: #030810 !important;
    border-right: 1px solid var(--border);
}

.no-selection {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--dim);
    font-size: 1.1rem;
    border: 2px dashed var(--border);
    border-radius: 12px;
    margin: 1rem 0;
}

.no-selection .emoji { font-size: 3rem; display: block; margin-bottom: 1rem; }

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: var(--card);
    border-radius: 8px;
    padding: 8px 16px;
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  COMPLETE COUNTRIES DATABASE (40+ DAVLAT)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def get_all_countries():
    """195 ta davlatni REST Countries orqali olib keladi."""

    UN_195 = {
        "AFG","ALB","DZA","AND","AGO","ATG","ARG","ARM","AUS","AUT","AZE",
        "BHS","BHR","BGD","BRB","BLR","BEL","BLZ","BEN","BTN","BOL","BIH",
        "BWA","BRA","BRN","BGR","BFA","BDI","CPV","KHM","CMR","CAN","CAF",
        "TCD","CHL","CHN","COL","COM","COG","CRI","CIV","HRV","CUB","CYP",
        "CZE","COD","DNK","DJI","DMA","DOM","ECU","EGY","SLV","GNQ","ERI",
        "EST","SWZ","ETH","FJI","FIN","FRA","GAB","GMB","GEO","DEU","GHA",
        "GRC","GRD","GTM","GIN","GNB","GUY","HTI","HND","HUN","ISL","IND",
        "IDN","IRN","IRQ","IRL","ISR","ITA","JAM","JPN","JOR","KAZ","KEN",
        "KIR","PRK","KOR","KWT","KGZ","LAO","LVA","LBN","LSO","LBR","LBY",
        "LIE","LTU","LUX","MDG","MWI","MYS","MDV","MLI","MLT","MHL","MRT",
        "MUS","MEX","FSM","MDA","MCO","MNG","MNE","MAR","MOZ","MMR","NAM",
        "NRU","NPL","NLD","NZL","NIC","NER","NGA","MKD","NOR","OMN","PAK",
        "PLW","PAN","PNG","PRY","PER","PHL","POL","PRT","QAT","ROU","RUS",
        "RWA","KNA","LCA","VCT","WSM","SMR","STP","SAU","SEN","SRB","SYC",
        "SLE","SGP","SVK","SVN","SLB","SOM","ZAF","SSD","ESP","LKA","SDN",
        "SUR","SWE","CHE","SYR","TJK","TZA","THA","TLS","TGO","TON","TTO",
        "TUN","TUR","TKM","TUV","UGA","UKR","ARE","GBR","USA","URY","UZB",
        "VUT","VEN","VNM","YEM","ZMB","ZWE","VAT","PSE"
    }

    REGION_UZ = {
        "Africa": "Afrika",
        "Americas": "Amerika",
        "Asia": "Osiyo",
        "Europe": "Yevropa",
        "Oceania": "Okeaniya",
        "Antarctic": "Antarktida"
    }

    NAME_UZ = {
        "United States": "AQSh",
        "United States of America": "AQSh",
        "United Kingdom": "Buyuk Britaniya",
        "Russia": "Rossiya",
        "Germany": "Germaniya",
        "France": "Fransiya",
        "Italy": "Italiya",
        "Spain": "Ispaniya",
        "Japan": "Yaponiya",
        "China": "Xitoy",
        "India": "Hindiston",
        "South Korea": "Janubiy Koreya",
        "Korea": "Koreya",
        "North Korea": "Shimoliy Koreya",
        "Turkey": "Turkiya",
        "Türkiye": "Turkiya",
        "Iran": "Eron",
        "Saudi Arabia": "Saudiya Arabistoni",
        "United Arab Emirates": "Birlashgan Arab Amirliklari",
        "Uzbekistan": "O'zbekiston",
        "Kazakhstan": "Qozog'iston",
        "Kyrgyzstan": "Qirg'iziston",
        "Tajikistan": "Tojikiston",
        "Turkmenistan": "Turkmaniston",
        "Egypt": "Misr",
        "South Africa": "Janubiy Afrika",
        "New Zealand": "Yangi Zelandiya",
        "Czechia": "Chexiya",
        "Netherlands": "Niderlandiya",
        "Sweden": "Shvetsiya",
        "Norway": "Norvegiya",
        "Switzerland": "Shveytsariya",
        "Belarus": "Belarus",
        "Ukraine": "Ukraina",
        "Poland": "Polsha",
        "Mexico": "Meksika",
        "Brazil": "Braziliya",
        "Argentina": "Argentina",
        "Canada": "Kanada",
        "Australia": "Avstraliya",
        "Pakistan": "Pokiston",
        "Bangladesh": "Bangladesh",
        "Indonesia": "Indoneziya",
        "Afghanistan": "Afg'oniston",
        "Iraq": "Iroq",
        "Syria": "Suriya",
        "Israel": "Isroil",
        "Palestine": "Falastin",
        "Vatican City": "Vatikan",
        "Holy See": "Vatikan",
    }

    def fetch_all_fields(fields):
        url = f"https://restcountries.com/v3.1/all?fields={','.join(fields)}"
        response = requests.get(url, timeout=40)
        response.raise_for_status()
        return response.json()

    try:
        base_fields = [
            "name", "cca2", "cca3", "capital", "region",
            "subregion", "population", "area", "flag", "independent"
        ]
        extra_fields = [
            "cca3", "languages", "currencies", "timezones", "borders",
            "tld", "landlocked", "car", "latlng"
        ]

        base_data = fetch_all_fields(base_fields)
        extra_data = fetch_all_fields(extra_fields)
        extra_map = {
            item.get("cca3", ""): item
            for item in extra_data
            if item.get("cca3")
        }

        rows = []
        for c in base_data:
            cca3 = c.get("cca3", "")
            if cca3 not in UN_195:
                continue

            extra = extra_map.get(cca3, {})

            common_name = c.get("name", {}).get("common", "Noma'lum")
            official_name = c.get("name", {}).get("official", common_name)
            name_display = NAME_UZ.get(common_name, common_name)

            capital = c.get("capital", ["—"])
            capital = capital[0] if capital else "—"

            languages = extra.get("languages", {})
            currencies = extra.get("currencies", {})
            timezones = extra.get("timezones", [])
            borders = extra.get("borders", [])
            tld = extra.get("tld", [])
            latlng = extra.get("latlng", [0, 0])
            car = extra.get("car", {})

            region_raw = c.get("region", "—")
            region_uz = REGION_UZ.get(region_raw, region_raw if region_raw else "—")

            rows.append({
                "name": name_display,
                "official": official_name,
                "cca2": c.get("cca2", ""),
                "cca3": cca3,
                "flag": c.get("flag", "🏳️"),
                "capital": capital,
                "region": region_uz,
                "subregion": c.get("subregion", "—") or "—",
                "population": int(c.get("population", 0) or 0),
                "area": float(c.get("area", 0) or 0),
                "languages": ", ".join(languages.values()) if languages else "—",
                "currencies": ", ".join(
                    [f"{v.get('name', k)} ({k})" for k, v in currencies.items()]
                ) if currencies else "—",
                "timezones": ", ".join(timezones) if timezones else "—",
                "borders": ", ".join(borders) if borders else "Dengizga chegaralangan",
                "tld": ", ".join(tld) if tld else "—",
                "landlocked": "Ha" if extra.get("landlocked", False) else "Yo'q",
                "independent": "Ha" if c.get("independent", True) else "Yo'q",
                "car_side": car.get("side", "—").capitalize() if car.get("side") else "—",
                "lat": latlng[0] if isinstance(latlng, list) and len(latlng) > 0 else 0,
                "lon": latlng[1] if isinstance(latlng, list) and len(latlng) > 1 else 0,
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.drop_duplicates(subset=["cca3"]).reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"❌ 195 davlatni yuklashda xatolik: {e}")
        return pd.DataFrame()

def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f} mlrd"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.2f} mln"
    elif n >= 1_000:
        return f"{n/1_000:.1f} ming"
    return str(n)

def format_money(value):
    if value is None or pd.isna(value):
        return "—"
    value = float(value)
    if value >= 1_000_000_000_000:
        return f"${value/1_000_000_000_000:.2f} trln"
    elif value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f} mlrd"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f} mln"
    return f"${value:,.0f}"

def format_float(value, suffix=""):
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.2f}{suffix}"

# ─────────────────────────────────────────────
#  EXTRA DATA HELPERS (NEW)
# ─────────────────────────────────────────────
COUNTRY_NAME_EN_MAP = {
    "O'zbekiston": "Uzbekistan",
    "Qozog'iston": "Kazakhstan",
    "Qirg'iziston": "Kyrgyzstan",
    "Tojikiston": "Tajikistan",
    "Turkmaniston": "Turkmenistan",
    "Rossiya": "Russia",
    "Germaniya": "Germany",
    "Fransiya": "France",
    "Buyuk Britaniya": "United Kingdom",
    "Italiya": "Italy",
    "Ispaniya": "Spain",
    "Ukraina": "Ukraine",
    "Polsha": "Poland",
    "Shvetsiya": "Sweden",
    "Norvegiya": "Norway",
    "Xitoy": "China",
    "Hindiston": "India",
    "Yaponiya": "Japan",
    "Janubiy Koreya": "South Korea",
    "Indoneziya": "Indonesia",
    "Pokiston": "Pakistan",
    "Bangladesh": "Bangladesh",
    "Turkiya": "Turkey",
    "Eron": "Iran",
    "Saudiya Arabistoni": "Saudi Arabia",
    "AQSh": "United States of America",
    "Kanada": "Canada",
    "Braziliya": "Brazil",
    "Meksika": "Mexico",
    "Argentina": "Argentina",
    "Nigeriya": "Nigeria",
    "Misr": "Egypt",
    "Janubiy Afrika": "South Africa",
    "Keniya": "Kenya",
    "Efiopiya": "Ethiopia",
    "Avstraliya": "Australia",
    "Yangi Zelandiya": "New Zealand",
}

@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_flag_url(cca2):
    try:
        url = f"https://restcountries.com/v3.1/alpha/{cca2}"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and data:
            flags = data[0].get("flags", {})
            return flags.get("png") or flags.get("svg") or None
    except Exception:
        return None
    return None

@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_world_bank_indicator(country_code, indicator):
    try:
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=100"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return None, None

        for item in data[1]:
            if item.get("value") is not None:
                return item.get("value"), item.get("date")

    except Exception:
        pass

    return None, None

@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_head_of_state(country_name_en):
    try:
        query = f"""
        SELECT ?headOfStateLabel WHERE {{
          ?country rdfs:label "{country_name_en}"@en.
          OPTIONAL {{ ?country wdt:P35 ?headOfState. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """

        url = "https://query.wikidata.org/sparql"
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "WorldExplorerPro/1.0"
        }
        response = requests.get(url, params={"query": query}, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        bindings = data.get("results", {}).get("bindings", [])
        if bindings:
            return bindings[0].get("headOfStateLabel", {}).get("value")
    except Exception:
        pass

    return "—"

@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def get_country_extra_data(cca2, cca3, name_uz):
    country_name_en = COUNTRY_NAME_EN_MAP.get(name_uz, name_uz)
    if country_name_en == name_uz:
        country_name_en = name_uz

    flag_url = fetch_flag_url(cca2)
    president = fetch_head_of_state(country_name_en)

    gdp, gdp_year = fetch_world_bank_indicator(cca3, "NY.GDP.MKTP.CD")
    gdp_per_capita, gdp_pc_year = fetch_world_bank_indicator(cca3, "NY.GDP.PCAP.CD")
    agriculture_pct, agriculture_year = fetch_world_bank_indicator(cca3, "NV.AGR.TOTL.ZS")
    industry_pct, industry_year = fetch_world_bank_indicator(cca3, "NV.IND.TOTL.ZS")
    services_pct, services_year = fetch_world_bank_indicator(cca3, "NV.SRV.TOTL.ZS")
    inflation_pct, inflation_year = fetch_world_bank_indicator(cca3, "FP.CPI.TOTL.ZG")
    life_expectancy, life_year = fetch_world_bank_indicator(cca3, "SP.DYN.LE00.IN")
    urban_population_pct, urban_year = fetch_world_bank_indicator(cca3, "SP.URB.TOTL.IN.ZS")

    return {
        "flag_url": flag_url,
        "president": president or "—",
        "gdp_usd": gdp,
        "gdp_year": gdp_year,
        "gdp_per_capita": gdp_per_capita,
        "gdp_pc_year": gdp_pc_year,
        "agriculture_pct": agriculture_pct,
        "agriculture_year": agriculture_year,
        "industry_pct": industry_pct,
        "industry_year": industry_year,
        "services_pct": services_pct,
        "services_year": services_year,
        "inflation_pct": inflation_pct,
        "inflation_year": inflation_year,
        "life_expectancy": life_expectancy,
        "life_year": life_year,
        "urban_population_pct": urban_population_pct,
        "urban_year": urban_year,
    }

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">🌍 WORLD EXPLORER PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">INTERACTIVE GLOBAL COUNTRIES INTELLIGENCE PLATFORM</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("🛰️ Dunyo ma'lumotlari yuklanmoqda..."):
    df = get_all_countries()

if df.empty:
    st.error("❌ Ma'lumotlar yuklanmadi!")
    st.stop()

df = df.drop_duplicates(subset=['name'])
df = df.sort_values("name").reset_index(drop=True)

st.success(f"✅ {len(df)} ta davlat ma'lumoti yuklandi!")

# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 0.9rem; color: #00d4ff;
                letter-spacing: 2px; padding: 0.5rem 0; border-bottom: 1px solid #1e3a5f;
                margin-bottom: 1rem;'>
        ⚙️ FILTERLAR
    </div>
    """, unsafe_allow_html=True)

    regions = ["Hammasi"] + sorted(df["region"].dropna().unique().tolist())
    selected_region = st.selectbox("🌐 Region", regions)
    
    filtered_df = df if selected_region == "Hammasi" else df[df["region"] == selected_region]
    
    st.divider()
    
    if not filtered_df.empty:
        pop_min = int(filtered_df["population"].min())
        pop_max = int(filtered_df["population"].max())
        
        col1, col2 = st.columns(2)
        with col1:
            min_pop = st.number_input("Min aholi (mln)", min_value=0, max_value=int(pop_max/1_000_000), value=0)
        with col2:
            max_pop = st.number_input("Max aholi (mln)", min_value=0, max_value=int(pop_max/1_000_000), value=int(pop_max/1_000_000))
        
        filtered_df = filtered_df[
            (filtered_df["population"] >= min_pop * 1_000_000) &
            (filtered_df["population"] <= max_pop * 1_000_000)
        ]
    
    st.divider()
    
    color_by = st.selectbox(
        "🎨 Xarita rangi",
        ["population", "area"],
        format_func=lambda x: "Aholi soni" if x == "population" else "Maydon (km²)"
    )
    
    st.divider()
    st.markdown(f"""
    <div style='text-align:center; color: #4a7a9b; font-size: 0.85rem;'>
        📊 Ko'rsatilmoqda: <span style='color:#00d4ff; font-weight:700'>{len(filtered_df)}</span> davlat
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  GLOBAL STATS
# ─────────────────────────────────────────────
if not filtered_df.empty:
    total_pop = filtered_df["population"].sum()
    total_area = filtered_df["area"].sum()
    n_countries = len(filtered_df)
    avg_pop = total_pop / n_countries if n_countries > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, f"{n_countries}", "DAVLATLAR"),
        (c2, format_number(total_pop), "JAMI AHOLI"),
        (c3, f"{total_area:,.0f} km²", "JAMI MAYDON"),
        (c4, format_number(avg_pop), "O'RTACHA AHOLI"),
    ]
    
    for col, num, label in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-num">{num}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["🗺️ Xarita & Davlatlar", "📊 Statistika"])

with tab1:
    map_col, detail_col = st.columns([3, 2], gap="medium")
    
    with map_col:
        map_df = filtered_df[filtered_df["cca3"] != ""].copy()
        
        if not map_df.empty:
            fig = px.choropleth(
                map_df,
                locations="cca3",
                color=color_by,
                hover_name="name",
                hover_data={
                    "cca3": False,
                    "capital": True,
                    "region": True,
                    "population": ":,",
                    "area": ":,.0f",
                },
                color_continuous_scale="Viridis",
                projection="natural earth",
            )
            
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                geo=dict(
                    bgcolor="rgba(5,11,26,1)",
                    showframe=False,
                    showcoastlines=True,
                    coastlinecolor="#1e3a5f",
                    showland=True,
                    landcolor="#0d1b2e",
                    showocean=True,
                    oceancolor="#030d1a",
                    showcountries=True,
                    countrycolor="#1e3a5f",
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                height=450,
                font=dict(color="#c8e6ff"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🗺️ Xarita uchun yetarli geografik ma'lumot mavjud emas")
        
        st.markdown("""
        <div style='font-family: Orbitron, monospace; font-size: 0.85rem; color: #00d4ff;
                    letter-spacing: 2px; margin: 0.5rem 0;'>
            📋 TOP 10 — AHOLI SONI BO'YICHA
        </div>
        """, unsafe_allow_html=True)
        
        top10 = filtered_df.nlargest(10, "population")[["flag", "name", "capital", "region", "population", "area"]].copy()
        top10["population"] = top10["population"].apply(format_number)
        top10["area"] = top10["area"].apply(lambda x: f"{x:,.0f} km²")
        top10.columns = ["🏳", "Davlat", "Poytaxt", "Region", "Aholi", "Maydon"]
        top10 = top10.reset_index(drop=True)
        top10.index = top10.index + 1
        
        st.dataframe(top10, use_container_width=True, height=280)
    
    with detail_col:
        st.markdown("""
        <div style='font-family: Orbitron, monospace; font-size: 0.85rem; color: #00d4ff;
                    letter-spacing: 2px; margin-bottom: 0.5rem;'>
            🔍 DAVLAT TANLANG
        </div>
        """, unsafe_allow_html=True)
        
        country_names = ["— Tanlang —"] + filtered_df["name"].tolist()
        selected_country = st.selectbox("", country_names, label_visibility="collapsed")
        
        if selected_country == "— Tanlang —":
            st.markdown("""
            <div class="no-selection">
                <span class="emoji">🌐</span>
                Chap tarafdagi xaritani ko'ring yoki<br>
                yuqoridan davlat tanlang
            </div>
            """, unsafe_allow_html=True)
            
            if not filtered_df.empty:
                region_stats = filtered_df.groupby("region")["population"].sum().reset_index()
                fig_pie = px.pie(
                    region_stats,
                    values="population",
                    names="region",
                    hole=0.55,
                    color_discrete_sequence=px.colors.sequential.Plasma_r,
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#c8e6ff", size=11),
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=300,
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            row = filtered_df[filtered_df["name"] == selected_country].iloc[0]

            with st.spinner("📡 Qo'shimcha davlat statistikasi yuklanmoqda..."):
                extra_data = get_country_extra_data(
                    row["cca2"],
                    row["cca3"],
                    row["name"]
                )
            
            st.markdown(f"""
            <div class="info-card">
                <div class="flag-display">{row['flag']}</div>
                <div class="country-name">{row['name'].upper()}</div>
                <div class="country-official">{row['official']}</div>
            </div>
            """, unsafe_allow_html=True)

            if extra_data.get("flag_url"):
                st.markdown('<div class="flag-image-box">', unsafe_allow_html=True)
                st.image(extra_data["flag_url"], caption=f"{row['name']} bayrog'i", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-num">{format_number(row['population'])}</div>
                    <div class="metric-label">AHOLI</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-num">{f"{row['area']:,.0f}"}</div>
                    <div class="metric-label">MAYDON km²</div>
                </div>
                """, unsafe_allow_html=True)
            
            details = [
                ("🏛️ Poytaxt", row['capital']),
                ("🌐 Region", row['region']),
                ("🌊 Quruqlik davlat", row['landlocked']),
                ("🔲 Mustaqil", row['independent']),
                ("👤 Prezident", extra_data.get("president", "—")),
            ]
            
            details_html = '<div class="info-card"><h3>📡 TO\'LIQ MA\'LUMOT</h3>'
            for label, value in details:
                if value and value != "—":
                    details_html += f"""
                    <div class="stat-row">
                        <span class="stat-label">{label}</span>
                        <span class="stat-value">{value}</span>
                    </div>"""
            details_html += "</div>"
            st.markdown(details_html, unsafe_allow_html=True)

            economy_details = [
                ("💰 GDP", f"{format_money(extra_data.get('gdp_usd'))} ({extra_data.get('gdp_year') or '—'})"),
                ("🧮 GDP per capita", f"{format_money(extra_data.get('gdp_per_capita'))} ({extra_data.get('gdp_pc_year') or '—'})"),
                ("🌾 Qishloq xo'jaligi", f"{format_float(extra_data.get('agriculture_pct'), '%')} ({extra_data.get('agriculture_year') or '—'})"),
                ("🏭 Sanoat", f"{format_float(extra_data.get('industry_pct'), '%')} ({extra_data.get('industry_year') or '—'})"),
                ("🏢 Xizmatlar", f"{format_float(extra_data.get('services_pct'), '%')} ({extra_data.get('services_year') or '—'})"),
                ("📈 Inflatsiya", f"{format_float(extra_data.get('inflation_pct'), '%')} ({extra_data.get('inflation_year') or '—'})"),
                ("❤️ Umr davomiyligi", f"{format_float(extra_data.get('life_expectancy'), ' yil')} ({extra_data.get('life_year') or '—'})"),
                ("🏙️ Shahar aholisi", f"{format_float(extra_data.get('urban_population_pct'), '%')} ({extra_data.get('urban_year') or '—'})"),
            ]

            econ_html = '<div class="info-card"><h3>📊 IQTISODIY STATISTIKA</h3>'
            for label, value in economy_details:
                if value and value != "—":
                    econ_html += f"""
                    <div class="stat-row">
                        <span class="stat-label">{label}</span>
                        <span class="stat-value">{value}</span>
                    </div>"""
            econ_html += "</div>"
            st.markdown(econ_html, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.2rem; color: #00d4ff;
                letter-spacing: 2px; margin-bottom: 1rem;'>
        📊 REGIONLAR STATISTIKASI
    </div>
    """, unsafe_allow_html=True)
    
    region_stats = df.groupby("region").agg({
        "population": "sum",
        "area": "sum",
        "name": "count"
    }).round(2).reset_index()
    region_stats.columns = ["Region", "Aholi", "Maydon (km²)", "Davlatlar soni"]
    region_stats["Aholi"] = region_stats["Aholi"].apply(format_number)
    region_stats["Maydon (km²)"] = region_stats["Maydon (km²)"].apply(lambda x: f"{x:,.0f}")
    
    st.dataframe(region_stats, use_container_width=True)
    
    fig_bar = px.bar(
        region_stats,
        x="Region",
        y="Davlatlar soni",
        title="REGIONLAR BO'YICHA DAVLATLAR SONI",
        color="Davlatlar soni",
        color_continuous_scale="Viridis"
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c8e6ff"),
        title_font=dict(color="#00d4ff")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color: #1e3a5f; font-size: 0.8rem; letter-spacing: 2px;
            border-top: 1px solid #0d1b2e; padding-top: 1rem;'>
    🌍 WORLD EXPLORER PRO | 195 ta davlat ma'lumoti | Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
