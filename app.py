import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime
import time

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🌍 World Explorer Pro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS (dark space / neon aesthetic)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

/* Root */
:root {
    --bg: #050b1a;
    --card: #0d1b2e;
    --border: #1e3a5f;
    --accent: #00d4ff;
    --accent2: #7b2fff;
    --text: #c8e6ff;
    --dim: #4a7a9b;
    --success: #00ff88;
    --warning: #ffaa00;
    --danger: #ff3366;
}

/* Global */
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Rajdhani', sans-serif;
}

/* Header */
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

/* Cards */
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
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(30,58,95,0.5);
    font-size: 0.92rem;
}
.stat-label { color: var(--dim); }
.stat-value { color: var(--accent); font-weight: 600; }

/* Metric boxes */
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

/* Flag */
.flag-display {
    font-size: 5rem;
    text-align: center;
    padding: 1rem 0;
    filter: drop-shadow(0 0 15px rgba(0,212,255,0.4));
}

/* Country name */
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

/* Sidebar */
[data-testid="stSidebar"] {
    background: #030810 !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Selectbox, slider */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* No country selected */
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

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Tabs */
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
#  MULTI-API DATA LOADING FUNCTIONS
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def test_api_availability():
    """Bir nechta API larni tekshirib, qaysi biri ishlayotganini aniqlaydi"""
    apis = {
        'restcountries_v3': 'https://restcountries.com/v3/all',
        'restcountries_v2': 'https://restcountries.com/v2/all',
        'countriesnow': 'https://countriesnow.space/api/v0.1/countries',
        'graphql': 'https://countries-274616.ew.r.appspot.com/'
    }
    
    working_apis = []
    for name, url in apis.items():
        try:
            if name == 'graphql':
                response = requests.post(url, json={'query': '{countries{name}}'}, timeout=5)
                if response.status_code == 200:
                    working_apis.append(name)
            else:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    working_apis.append(name)
        except:
            continue
    
    return working_apis

@st.cache_data(ttl=3600, show_spinner=False)
def load_countries_from_restcountries_v3():
    """REST Countries API v3 dan ma'lumot olish"""
    try:
        url = "https://restcountries.com/v3/all"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        rows = []
        for c in data:
            try:
                # Asosiy ma'lumotlar
                name = c.get("name", {}).get("common", "Unknown")
                official = c.get("name", {}).get("official", name)
                
                # Geolokatsiya
                latlng = c.get("latlng", [0, 0])
                lat = latlng[0] if len(latlng) > 0 else 0
                lon = latlng[1] if len(latlng) > 1 else 0
                
                # Tillar
                langs = c.get("languages", {})
                languages = ", ".join(langs.values()) if langs else "—"
                
                # Valyutalar
                curr = c.get("currencies", {})
                currencies = ", ".join(
                    f"{v.get('name','')} ({v.get('symbol','')})"
                    for v in curr.values()
                ) if curr else "—"
                currencies_iso = list(curr.keys()) if curr else []
                
                # Boshqa ma'lumotlar
                capitals = c.get("capital", [])
                capital = ", ".join(capitals) if capitals else "—"
                
                tlds = c.get("tld", [])
                tld = ", ".join(tlds) if tlds else "—"
                
                borders = c.get("borders", [])
                car_side = c.get("car", {}).get("side", "—")
                
                # Bayroq
                flag = c.get("flags", {}).get("emoji", "🏳️")
                flag_url = c.get("flags", {}).get("png", "")
                
                rows.append({
                    "name": name,
                    "official": official,
                    "cca2": c.get("cca2", ""),
                    "cca3": c.get("cca3", ""),
                    "flag": flag,
                    "flag_url": flag_url,
                    "capital": capital,
                    "region": c.get("region", "Unknown"),
                    "subregion": c.get("subregion", "—"),
                    "continents": ", ".join(c.get("continents", [])),
                    "population": c.get("population", 0),
                    "area": c.get("area", 0),
                    "languages": languages,
                    "currencies": currencies,
                    "currencies_iso": currencies_iso,
                    "timezones": ", ".join(c.get("timezones", [])),
                    "borders_list": borders,
                    "borders": ", ".join(borders) if borders else "Dengizga yoki okean bilan chegaralangan",
                    "tld": tld,
                    "landlocked": "Ha" if c.get("landlocked", False) else "Yo'q",
                    "independent": "Ha" if c.get("independent", False) else "Yo'q",
                    "car_side": car_side.capitalize() if car_side else "—",
                    "lat": lat,
                    "lon": lon,
                    "start_of_week": c.get("startOfWeek", "—"),
                    "maps": c.get("maps", {}).get("googleMaps", ""),
                    "population_density": round(c.get("population", 0) / c.get("area", 1), 2) if c.get("area", 0) > 0 else 0
                })
            except Exception as e:
                continue
        
        return pd.DataFrame(rows), "REST Countries v3"
    except Exception as e:
        return pd.DataFrame(), None

@st.cache_data(ttl=3600, show_spinner=False)
def load_countries_from_restcountries_v2():
    """REST Countries API v2 dan ma'lumot olish (fallback)"""
    try:
        url = "https://restcountries.com/v2/all"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        rows = []
        for c in data:
            try:
                latlng = c.get("latlng", [0, 0])
                langs = c.get("languages", [])
                languages = ", ".join(l.get("name", "") for l in langs) if langs else "—"
                curr = c.get("currencies", [])
                currencies = ", ".join(
                    f"{cu.get('name','')} ({cu.get('symbol','')})" for cu in curr
                ) if curr else "—"
                
                rows.append({
                    "name": c.get("name", "Unknown"),
                    "official": c.get("name", "Unknown"),
                    "cca2": c.get("alpha2Code", ""),
                    "cca3": c.get("alpha3Code", ""),
                    "flag": c.get("flag", "🏳️"),
                    "flag_url": "",
                    "capital": c.get("capital", "—") or "—",
                    "region": c.get("region", "Unknown") or "Unknown",
                    "subregion": c.get("subregion", "—") or "—",
                    "continents": c.get("region", "—"),
                    "population": c.get("population", 0),
                    "area": c.get("area", 0) or 0,
                    "languages": languages,
                    "currencies": currencies,
                    "currencies_iso": [],
                    "timezones": ", ".join(c.get("timezones", [])),
                    "borders_list": c.get("borders", []),
                    "borders": ", ".join(c.get("borders", [])) or "Dengizga chegaralangan",
                    "tld": ", ".join(c.get("topLevelDomain", [])),
                    "landlocked": "Ha" if c.get("landlocked", False) else "Yo'q",
                    "independent": "—",
                    "car_side": "—",
                    "lat": latlng[0] if len(latlng) > 0 else 0,
                    "lon": latlng[1] if len(latlng) > 1 else 0,
                    "start_of_week": "—",
                    "maps": "",
                    "population_density": round(c.get("population", 0) / c.get("area", 1), 2) if c.get("area", 0) > 0 else 0
                })
            except Exception:
                continue
        
        return pd.DataFrame(rows), "REST Countries v2"
    except Exception as e:
        return pd.DataFrame(), None

@st.cache_data(ttl=3600, show_spinner=False)
def load_countries_from_countriesnow():
    """CountriesNow API dan ma'lumot olish"""
    try:
        url = "https://countriesnow.space/api/v0.1/countries"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        rows = []
        for item in data.get('data', []):
            try:
                name = item.get("name", "Unknown")
                capital = item.get("capital", "—")
                code = item.get("code", "")
                
                rows.append({
                    "name": name,
                    "official": name,
                    "cca2": code,
                    "cca3": "",
                    "flag": "🏳️",
                    "flag_url": "",
                    "capital": capital if capital else "—",
                    "region": item.get("region", "Unknown"),
                    "subregion": "—",
                    "continents": item.get("region", "—"),
                    "population": item.get("population", 0),
                    "area": item.get("area", 0),
                    "languages": "—",
                    "currencies": "—",
                    "currencies_iso": [],
                    "timezones": "—",
                    "borders_list": [],
                    "borders": "Dengizga chegaralangan",
                    "tld": "—",
                    "landlocked": "Yo'q",
                    "independent": "Ha",
                    "car_side": "—",
                    "lat": 0,
                    "lon": 0,
                    "start_of_week": "—",
                    "maps": "",
                    "population_density": round(item.get("population", 0) / item.get("area", 1), 2) if item.get("area", 0) > 0 else 0
                })
            except Exception:
                continue
        
        return pd.DataFrame(rows), "CountriesNow"
    except Exception as e:
        return pd.DataFrame(), None

@st.cache_data(ttl=3600, show_spinner=False)
def load_countries_from_graphql():
    """GraphQL Countries API dan ma'lumot olish"""
    try:
        query = """
        {
          countries {
            name
            capital
            population
            area
            currency
            continent {
              name
            }
            languages {
              name
            }
            code
            emoji
            phone
          }
        }
        """
        
        response = requests.post(
            'https://countries-274616.ew.r.appspot.com/',
            json={'query': query},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        
        rows = []
        for c in data.get('data', {}).get('countries', []):
            try:
                languages = ", ".join([lang.get('name', '') for lang in c.get('languages', [])]) if c.get('languages') else "—"
                
                rows.append({
                    "name": c.get("name", "Unknown"),
                    "official": c.get("name", "Unknown"),
                    "cca2": c.get("code", ""),
                    "cca3": "",
                    "flag": c.get("emoji", "🏳️"),
                    "flag_url": "",
                    "capital": c.get("capital", "—") or "—",
                    "region": c.get("continent", {}).get("name", "Unknown"),
                    "subregion": "—",
                    "continents": c.get("continent", {}).get("name", "—"),
                    "population": c.get("population", 0),
                    "area": c.get("area", 0) or 0,
                    "languages": languages,
                    "currencies": c.get("currency", "—") or "—",
                    "currencies_iso": [c.get("currency", "")] if c.get("currency") else [],
                    "timezones": "—",
                    "borders_list": [],
                    "borders": "—",
                    "tld": "—",
                    "landlocked": "Yo'q",
                    "independent": "Ha",
                    "car_side": "—",
                    "lat": 0,
                    "lon": 0,
                    "start_of_week": "—",
                    "maps": "",
                    "population_density": round(c.get("population", 0) / c.get("area", 1), 2) if c.get("area", 0) > 0 else 0
                })
            except Exception:
                continue
        
        return pd.DataFrame(rows), "GraphQL Countries"
    except Exception as e:
        return pd.DataFrame(), None

def load_countries():
    """Barcha API larni sinab ko'rib, eng to'liq ma'lumotni yig'adi"""
    
    # API larni sinab ko'rish
    with st.spinner("🔍 API larni tekshirilmoqda..."):
        working_apis = test_api_availability()
    
    if not working_apis:
        st.error("Hech qanday API ishlamayapti. Internet aloqasini tekshiring!")
        return pd.DataFrame()
    
    st.info(f"✅ Ishlayotgan API'lar: {', '.join(working_apis)}")
    
    # API'lar ro'yxati (eng to'liqdan boshlab)
    api_functions = [
        ('restcountries_v3', load_countries_from_restcountries_v3, "REST Countries v3 (eng to'liq)"),
        ('restcountries_v2', load_countries_from_restcountries_v2, "REST Countries v2"),
        ('countriesnow', load_countries_from_countriesnow, "CountriesNow"),
        ('graphql', load_countries_from_graphql, "GraphQL Countries")
    ]
    
    # Har bir API ni sinab ko'rish
    for api_name, api_func, api_label in api_functions:
        if api_name in working_apis:
            with st.spinner(f"📡 {api_label} dan ma'lumot olinmoqda..."):
                df, source = api_func()
                if not df.empty:
                    st.success(f"✅ Ma'lumotlar {api_label} dan olindi")
                    return df
    
    # Hech qanday API ishlamasa
    st.error("Barcha API'lar ishlamadi. Ma'lumotlar yuklanmadi.")
    return pd.DataFrame()

@st.cache_data(ttl=1800, show_spinner=False)
def load_covid_stats():
    """Disease.sh API dan COVID-19 statistikasi"""
    try:
        url = "https://disease.sh/v3/covid-19/countries"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        covid_df = pd.DataFrame(data)
        covid_df = covid_df[['country', 'cases', 'deaths', 'recovered', 'active', 'critical', 'todayCases', 'todayDeaths', 'population']]
        covid_df.columns = ['country', 'COVID Cases', 'Deaths', 'Recovered', 'Active', 'Critical', 'Today Cases', 'Today Deaths', 'Population']
        
        return covid_df
    except Exception as e:
        st.warning(f"⚠️ COVID-19 ma'lumotlarini yuklab bo'lmadi: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def load_exchange_rates():
    """Open Exchange Rates API (free tier) - valyuta kurslari"""
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        rates = data.get('rates', {})
        return rates, data.get('time_last_update_utc', 'N/A')
    except Exception as e:
        st.warning(f"⚠️ Valyuta kurslarini yuklab bo'lmadi: {e}")
        return {}, 'N/A'

@st.cache_data(ttl=7200, show_spinner=False)
def load_world_bank_data(country_code):
    """World Bank API dan qo'shimcha iqtisodiy ma'lumotlar"""
    try:
        url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if len(data) > 1 and data[1]:
            gdp = data[1][0].get('value', 'N/A') if data[1] else 'N/A'
            return gdp
        return 'N/A'
    except:
        return 'N/A'

def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f} млрд"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.2f} млн"
    elif n >= 1_000:
        return f"{n/1_000:.1f} тыс"
    return str(n)


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">🌍 WORLD EXPLORER PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">INTERACTIVE GLOBAL COUNTRIES INTELLIGENCE PLATFORM | 4x API INTEGRATION</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
df = load_countries()

if df.empty:
    st.error("❌ Ma'lumotlar yuklanmadi. Internet aloqasini tekshiring va qayta urining.")
    st.stop()

# Sort by name
df = df.sort_values("name").reset_index(drop=True)

# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 0.9rem; color: #00d4ff;
                letter-spacing: 2px; padding: 0.5rem 0; border-bottom: 1px solid #1e3a5f;
                margin-bottom: 1rem;'>
        ⚙️ FILTERS
    </div>
    """, unsafe_allow_html=True)

    # Region filter
    regions = ["Hammasi"] + sorted(df["region"].dropna().unique().tolist())
    selected_region = st.selectbox("🌐 Region", regions)

    # Filter by region
    filtered_df = df if selected_region == "Hammasi" else df[df["region"] == selected_region]

    # Subregion (agar mavjud bo'lsa)
    if "subregion" in filtered_df.columns and not filtered_df["subregion"].isna().all():
        subregions = ["Hammasi"] + sorted(filtered_df["subregion"].dropna().unique().tolist())
        selected_sub = st.selectbox("📍 Subregion", subregions)
        if selected_sub != "Hammasi":
            filtered_df = filtered_df[filtered_df["subregion"] == selected_sub]

    st.divider()

    # Population filter
    pop_min, pop_max = int(df["population"].min()), int(df["population"].max())
    pop_range = st.slider(
        "👥 Aholi (млн)",
        min_value=0,
        max_value=int(pop_max / 1_000_000) + 1,
        value=(0, int(pop_max / 1_000_000) + 1),
        step=1,
    )
    filtered_df = filtered_df[
        (filtered_df["population"] >= pop_range[0] * 1_000_000) &
        (filtered_df["population"] <= pop_range[1] * 1_000_000)
    ]

    st.divider()

    # Map color metric
    color_options = ["population", "area", "population_density"]
    color_labels = {"population": "Aholi soni", "area": "Maydon (km²)", "population_density": "Aholi zichligi"}
    
    color_by = st.selectbox(
        "🎨 Xarita rangi",
        color_options,
        format_func=lambda x: color_labels.get(x, x)
    )

    st.divider()
    st.markdown(f"""
    <div style='text-align:center; color: #4a7a9b; font-size: 0.85rem;'>
        📊 Ko'rsatilmoqda: <span style='color:#00d4ff; font-weight:700'>{len(filtered_df)}</span> davlat
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  GLOBAL STATS ROW
# ─────────────────────────────────────────────
total_pop = filtered_df["population"].sum()
total_area = filtered_df["area"].sum()
n_countries = len(filtered_df)
n_landlocked = (filtered_df["landlocked"] == "Ha").sum() if "landlocked" in filtered_df.columns else 0
avg_density = filtered_df["population_density"].mean() if "population_density" in filtered_df.columns else 0

c1, c2, c3, c4, c5 = st.columns(5)
metrics_data = [
    (c1, f"{n_countries}", "ДАВЛАТЛАР"),
    (c2, format_number(total_pop), "ЖАМИ АҲОЛИ"),
    (c3, f"{total_area:,.0f} км²", "ЖАМИ МАЙДОН"),
    (c4, f"{n_landlocked}", "ҚУРУҚЛИК ДАВЛАТ"),
    (c5, f"{avg_density:.1f}", "ЎРТА ЗИЧЛИК (киши/км²)"),
]

for col, num, label in metrics_data:
    with col:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-num">{num}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS FOR DIFFERENT VIEWS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗺️ Карта & Давлатлар", "🦠 COVID-19 Статистикаси", "💰 Валюта Курслари"])

with tab1:
    map_col, detail_col = st.columns([3, 2], gap="medium")
    
    with map_col:
        # ── CHOROPLETH MAP ──
        if "cca3" in filtered_df.columns and not filtered_df["cca3"].isna().all():
            fig = px.choropleth(
                filtered_df,
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
                color_continuous_scale=[
                    [0, "#0d1b2e"],
                    [0.2, "#0a3060"],
                    [0.5, "#0066cc"],
                    [0.8, "#00aaff"],
                    [1, "#00d4ff"],
                ],
                projection="natural earth",
                labels={
                    "population": "Аҳоли",
                    "area": "Майдон км²",
                    "capital": "Пойтахт",
                    "region": "Регион",
                    "population_density": "Аҳоли зичлиги (киши/км²)"
                },
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
                    showlakes=True,
                    lakecolor="#030d1a",
                    showcountries=True,
                    countrycolor="#1e3a5f",
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                height=420,
                coloraxis_colorbar=dict(
                    title=dict(text="", side="right"),
                    tickfont=dict(color="#4a7a9b", size=10),
                    bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(0,0,0,0)",
                ),
                font=dict(color="#c8e6ff"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("🗺️ Xarita uchun yetarli ma'lumot mavjud emas")

        # ── TOP 10 TABLE ──
        st.markdown("""
        <div style='font-family: Orbitron, monospace; font-size: 0.85rem; color: #00d4ff;
                    letter-spacing: 2px; margin: 0.5rem 0;'>
            📋 TOP 10 — АҲОЛИ СОНИ БЎЙИЧА
        </div>
        """, unsafe_allow_html=True)

        display_cols = ["flag", "name", "capital", "region", "population", "area"]
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        
        if available_cols:
            top10 = filtered_df.nlargest(10, "population")[available_cols].copy()
            if "population" in top10.columns:
                top10["population"] = top10["population"].apply(format_number)
            if "area" in top10.columns:
                top10["area"] = top10["area"].apply(lambda x: f"{x:,.0f} км²")
            
            column_names = {
                "flag": "🏳",
                "name": "Давлат",
                "capital": "Пойтахт",
                "region": "Регион",
                "population": "Аҳоли",
                "area": "Майдон"
            }
            top10 = top10.rename(columns=column_names)
            top10 = top10.reset_index(drop=True)
            top10.index = top10.index + 1

            st.dataframe(
                top10,
                use_container_width=True,
                height=280,
            )
    
    with detail_col:
        # ── COUNTRY SELECTOR ──
        st.markdown("""
        <div style='font-family: Orbitron, monospace; font-size: 0.85rem; color: #00d4ff;
                    letter-spacing: 2px; margin-bottom: 0.5rem;'>
            🔍 ДАВЛАТ ТАНЛАНГ
        </div>
        """, unsafe_allow_html=True)

        country_names = ["— Танланг —"] + filtered_df["name"].tolist()
        selected_country = st.selectbox("", country_names, label_visibility="collapsed")

        if selected_country == "— Танланг —":
            st.markdown("""
            <div class="no-selection">
                <span class="emoji">🌐</span>
                Чап тарафдаги харитани кўринг ёки<br>
                юқоридан давлат танланг
            </div>
            """, unsafe_allow_html=True)

            # Region breakdown pie
            if not filtered_df.empty and "region" in filtered_df.columns:
                region_counts = filtered_df.groupby("region")["population"].sum().reset_index()
                pie = px.pie(
                    region_counts,
                    values="population",
                    names="region",
                    hole=0.55,
                    color_discrete_sequence=["#00d4ff", "#7b2fff", "#00ffaa", "#ff6b35", "#ffd700", "#ff4488"],
                )
                pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#c8e6ff", size=11),
                    showlegend=True,
                    legend=dict(
                        bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#c8e6ff"),
                        orientation="v",
                    ),
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=300,
                )
                pie.update_traces(textfont_color="white", textinfo="percent")
                st.markdown("""
                <div style='font-family: Orbitron, monospace; font-size: 0.75rem; color: #4a7a9b;
                            letter-spacing: 2px; text-align:center; margin-top: 1rem;'>
                    РЕГИОНЛАР БЎЙИЧА АҲОЛИ
                </div>
                """, unsafe_allow_html=True)
                st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})

        else:
            # ── COUNTRY DETAIL ──
            row = filtered_df[filtered_df["name"] == selected_country].iloc[0]

            # Flag + name
            st.markdown(f"""
            <div class="info-card">
                <div class="flag-display">{row.get('flag', '🏳️')}</div>
                <div class="country-name">{row['name'].upper()}</div>
                <div class="country-official">{row.get('official', row['name'])}</div>
            </div>
            """, unsafe_allow_html=True)

            # Key metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-num">{format_number(row['population'])}</div>
                    <div class="metric-label">АҲОЛИ</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-num">{f"{row['area']:,.0f}"}</div>
                    <div class="metric-label">МАЙДОН км²</div>
                </div>
                """, unsafe_allow_html=True)

            # Details card
            details = []
            if "capital" in row and row["capital"] != "—":
                details.append(("🏛️ Пойтахт", row["capital"]))
            if "region" in row and row["region"] != "Unknown":
                details.append(("🌐 Регион", row["region"]))
            if "subregion" in row and row["subregion"] not in ["—", "Unknown"]:
                details.append(("📍 Субрегион", row["subregion"]))
            if "languages" in row and row["languages"] != "—":
                details.append(("🗣️ Тиллар", row["languages"]))
            if "currencies" in row and row["currencies"] != "—":
                details.append(("💰 Валюта", row["currencies"]))
            if "timezones" in row and row["timezones"] != "—":
                details.append(("🕐 Вакт зонаси", row["timezones"][:40] + "..." if len(row["timezones"]) > 40 else row["timezones"]))
            if "landlocked" in row and row["landlocked"] != "—":
                details.append(("🌊 Қуруқлик давлат", row["landlocked"]))
            if "car_side" in row and row["car_side"] != "—":
                details.append(("🚗 Йўл томони", row["car_side"]))
            if "tld" in row and row["tld"] != "—":
                details.append(("🌐 TLD (домен)", row["tld"]))
            if "independent" in row and row["independent"] != "—":
                details.append(("🔲 Мустақил", row["independent"]))
            if "borders" in row and row["borders"] != "—":
                details.append(("🗺️ Қўшни давлатлар", row["borders"]))
            if "population_density" in row and row["population_density"] > 0:
                details.append(("📊 Аҳоли зичлиги", f"{row['population_density']:.2f} киши/км²"))

            details_html = '<div class="info-card"><h3>📡 ТЎЛИҚ МАЪЛУМОТ</h3>'
            for label, value in details:
                details_html += f"""
                <div class="stat-row">
                    <span class="stat-label">{label}</span>
                    <span class="stat-value" style="max-width:55%; text-align:right; font-size:0.82rem;">{value}</span>
                </div>"""
            details_html += "</div>"
            st.markdown(details_html, unsafe_allow_html=True)

            # Mini map for selected country
            if "lat" in row and "lon" in row and row["lat"] != 0 and row["lon"] != 0:
                mini_fig = go.Figure(go.Scattergeo(
                    lat=[row["lat"]],
                    lon=[row["lon"]],
                    mode="markers",
                    marker=dict(
                        size=18,
                        color="#00d4ff",
                        symbol="circle",
                        line=dict(width=3, color="#7b2fff"),
                    ),
                    text=[row["name"]],
                    hovertemplate=f"<b>{row['name']}</b><br>Lat: {row['lat']:.2f}<br>Lon: {row['lon']:.2f}<extra></extra>",
                ))
                mini_fig.update_layout(
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
                        projection_type="orthographic",
                        center=dict(lat=row["lat"], lon=row["lon"]),
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=200,
                    showlegend=False,
                )
                st.markdown("""
                <div style='font-family: Orbitron, monospace; font-size: 0.75rem; color: #4a7a9b;
                            letter-spacing: 2px; text-align:center; margin-top:0.5rem;'>
                    🌐 ГЛОБУС ЖОЙЛАШУВИ
                </div>
                """, unsafe_allow_html=True)
                st.plotly_chart(mini_fig, use_container_width=True, config={"displayModeBar": False})

with tab2:
    covid_df = load_covid_stats()
    if not covid_df.empty:
        st.markdown("""
        <div style='font-family: Orbitron, monospace; font-size: 1.2rem; color: #00d4ff;
                    letter-spacing: 2px; margin-bottom: 1rem;'>
            🦠 ДУНЁ БЎЙИЧА COVID-19 СТАТИСТИКАСИ
        </div>
        """, unsafe_allow_html=True)
        
        # Global COVID metrics
        global_cases = covid_df['COVID Cases'].sum()
        global_deaths = covid_df['Deaths'].sum()
        global_recovered = covid_df['Recovered'].sum()
        global_active = covid_df['Active'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Жами касалланган", f"{global_cases:,}")
        with col2:
            st.metric("💀 Вафот этганлар", f"{global_deaths:,}")
        with col3:
            st.metric("❤️‍🩹 Тузалганлар", f"{global_recovered:,}")
        with col4:
            active_percent = (global_active / global_cases * 100) if global_cases > 0 else 0
            st.metric("🟡 Фаол касаллар", f"{global_active:,}", delta=f"{active_percent:.1f}%")
        
        # Top COVID affected countries
        st.markdown("---")
        top_covid = covid_df.nlargest(10, 'COVID Cases')[['country', 'COVID Cases', 'Deaths', 'Recovered', 'Active']]
        top_covid.columns = ['Давлат', 'Касалланган', 'Вафот', 'Тузалган', 'Фаол']
        st.dataframe(top_covid, use_container_width=True)
        
        # COVID Bar chart
        fig_covid = px.bar(
            covid_df.nlargest(15, 'COVID Cases'),
            x='country',
            y='COVID Cases',
            title="ТОП-15 КЎП КАСАЛЛАНГАН ДАВЛАТЛАР",
            color='COVID Cases',
            color_continuous_scale='Reds',
            labels={'country': 'Давлат', 'COVID Cases': 'Касалланганлар сони'}
        )
        fig_covid.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c8e6ff"),
            title_font=dict(color="#00d4ff"),
            xaxis=dict(tickangle=45)
        )
        st.plotly_chart(fig_covid, use_container_width=True)
    else:
        st.info("⚠️ COVID-19 маълумотлари ҳозирча мавжуд эмас")

with tab3:
    exchange_rates, last_update = load_exchange_rates()
    if exchange_rates:
        st.markdown("""
        <div style='font-family: Orbitron, monospace; font-size: 1.2rem; color: #00d4ff;
                    letter-spacing: 2px; margin-bottom: 1rem;'>
            💱 ВАЛЮТА КУРСЛАРИ (USD га нисбатан)
        </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"📅 Oxirgi yangilanish: {last_update}")
        
        # Convert to DataFrame for display
        rates_df = pd.DataFrame(list(exchange_rates.items()), columns=['Валюта', 'Курс'])
        rates_df = rates_df.sort_values('Курс', ascending=False)
        
        # Show top 20 strongest currencies
        st.markdown("### 💪 Энг кучли валюталар")
        st.dataframe(rates_df.head(20), use_container_width=True)
        
        # Currency search
        search_currency = st.text_input("🔍 Валюта қидириш (масалан: UZS, EUR, GBP)", value="UZS")
        if search_currency.upper() in exchange_rates:
            st.success(f"💵 1 USD = {exchange_rates[search_currency.upper()]:,.2f} {search_currency.upper()}")
        elif search_currency:
            st.warning(f"⚠️ '{search_currency}' валютаси топилмади")
        
        # Exchange rate chart
        fig_rates = px.bar(
            rates_df.head(20),
            x='Валюта',
            y='Курс',
            title="ЭНГ КУЧЛИ 20 ВАЛЮТА",
            color='Курс',
            color_continuous_scale='Greens'
        )
        fig_rates.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c8e6ff"),
            title_font=dict(color="#00d4ff"),
            xaxis=dict(tickangle=45)
        )
        st.plotly_chart(fig_rates, use_container_width=True)
    else:
        st.info("⚠️ Валюта курслари маълумотлари ҳозирча мавжуд эмас")

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color: #1e3a5f; font-size: 0.8rem; letter-spacing: 2px;
            border-top: 1px solid #0d1b2e; padding-top: 1rem;'>
    🛰️ DATA SOURCES: REST Countries API | CountriesNow API | GraphQL Countries API | Disease.sh COVID-19 API | Open Exchange Rates API<br>
    🌍 WORLD EXPLORER PRO | Multi-API Intelligence Platform | Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
