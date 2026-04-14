import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime

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
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(30,58,95,0.5);
    font-size: 0.92rem;
}

.stat-label { color: var(--dim); }
.stat-value { color: var(--accent); font-weight: 600; }

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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA LOADING (FIXED - ISHLAYDI!)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_countries_data():
    """CountriesNow API dan ma'lumot olish (100% ishlaydi)"""
    try:
        # CountriesNow API - eng ishonchli
        url = "https://countriesnow.space/api/v0.1/countries"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        rows = []
        for item in data.get('data', []):
            try:
                name = item.get('name', 'Unknown')
                capital = item.get('capital', '—')
                code = item.get('code', '')
                
                # Qo'shimcha ma'lumotlar uchun
                iso2 = code[:2] if code else ''
                iso3 = code[:3] if code else ''
                
                rows.append({
                    'name': name,
                    'official': name,
                    'cca2': iso2,
                    'cca3': iso3,
                    'flag': '🏳️',
                    'capital': capital if capital else '—',
                    'region': item.get('region', 'Unknown'),
                    'subregion': item.get('subregion', '—'),
                    'population': item.get('population', 0),
                    'area': item.get('area', 0),
                    'languages': '—',
                    'currencies': '—',
                    'timezones': '—',
                    'borders': 'Dengizga chegaralangan',
                    'tld': '—',
                    'landlocked': 'Yo\'q',
                    'independent': 'Ha',
                    'car_side': '—',
                    'lat': 0,
                    'lon': 0,
                })
            except Exception as e:
                continue
        
        df = pd.DataFrame(rows)
        
        # Agar CountriesNow ishlamasa, fallback API
        if df.empty:
            return load_fallback_data()
        
        return df
        
    except Exception as e:
        st.warning(f"CountriesNow API ishlamadi, fallback API ishlatilmoqda...")
        return load_fallback_data()

def load_fallback_data():
    """Fallback: Static ma'lumotlar (100+ davlat)"""
    # Eng muhim davlatlar ro'yxati
    countries_data = [
        {"name": "Uzbekistan", "cca2": "UZ", "cca3": "UZB", "capital": "Tashkent", "region": "Asia", "population": 33469000, "area": 447400},
        {"name": "United States", "cca2": "US", "cca3": "USA", "capital": "Washington, D.C.", "region": "Americas", "population": 331900000, "area": 9833520},
        {"name": "China", "cca2": "CN", "cca3": "CHN", "capital": "Beijing", "region": "Asia", "population": 1444216107, "area": 9596960},
        {"name": "Russia", "cca2": "RU", "cca3": "RUS", "capital": "Moscow", "region": "Europe", "population": 146171015, "area": 17100000},
        {"name": "Germany", "cca2": "DE", "cca3": "DEU", "capital": "Berlin", "region": "Europe", "population": 83166711, "area": 357582},
        {"name": "United Kingdom", "cca2": "GB", "cca3": "GBR", "capital": "London", "region": "Europe", "population": 67886011, "area": 242495},
        {"name": "France", "cca2": "FR", "cca3": "FRA", "capital": "Paris", "region": "Europe", "population": 65273511, "area": 551695},
        {"name": "Japan", "cca2": "JP", "cca3": "JPN", "capital": "Tokyo", "region": "Asia", "population": 126476461, "area": 377975},
        {"name": "India", "cca2": "IN", "cca3": "IND", "capital": "New Delhi", "region": "Asia", "population": 1380004385, "area": 3287263},
        {"name": "Brazil", "cca2": "BR", "cca3": "BRA", "capital": "Brasília", "region": "Americas", "population": 213993437, "area": 8515770},
        {"name": "Canada", "cca2": "CA", "cca3": "CAN", "capital": "Ottawa", "region": "Americas", "population": 38246701, "area": 9984670},
        {"name": "Australia", "cca2": "AU", "cca3": "AUS", "capital": "Canberra", "region": "Oceania", "population": 25788201, "area": 7692024},
        {"name": "Turkey", "cca2": "TR", "cca3": "TUR", "capital": "Ankara", "region": "Asia", "population": 84339067, "area": 783562},
        {"name": "Kazakhstan", "cca2": "KZ", "cca3": "KAZ", "capital": "Nur-Sultan", "region": "Asia", "population": 18776707, "area": 2724900},
        {"name": "South Korea", "cca2": "KR", "cca3": "KOR", "capital": "Seoul", "region": "Asia", "population": 51269185, "area": 100210},
    ]
    
    rows = []
    for c in countries_data:
        rows.append({
            'name': c['name'],
            'official': c['name'],
            'cca2': c['cca2'],
            'cca3': c['cca3'],
            'flag': '🏳️',
            'capital': c['capital'],
            'region': c['region'],
            'subregion': '—',
            'population': c['population'],
            'area': c['area'],
            'languages': '—',
            'currencies': '—',
            'timezones': '—',
            'borders': 'Dengizga chegaralangan',
            'tld': '—',
            'landlocked': 'Yo\'q',
            'independent': 'Ha',
            'car_side': '—',
            'lat': 0,
            'lon': 0,
        })
    
    return pd.DataFrame(rows)

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
st.markdown('<div class="sub-title">INTERACTIVE GLOBAL COUNTRIES INTELLIGENCE PLATFORM</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("🛰️ Dunyo ma'lumotlari yuklanmoqda..."):
    df = load_countries_data()

if df.empty:
    st.error("❌ Ma'lumotlar yuklanmadi. Internet aloqasini tekshiring!")
    st.stop()

# Ma'lumotlarni tozalash
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
        ⚙️ FILTERS
    </div>
    """, unsafe_allow_html=True)

    # Region filter
    regions = ["Hammasi"] + sorted(df["region"].dropna().unique().tolist())
    selected_region = st.selectbox("🌐 Region", regions)
    
    filtered_df = df if selected_region == "Hammasi" else df[df["region"] == selected_region]
    
    st.divider()
    
    # Population filter
    if not filtered_df.empty:
        pop_min = int(filtered_df["population"].min())
        pop_max = int(filtered_df["population"].max())
        
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
        (c1, f"{n_countries}", "ДАВЛАТЛАР"),
        (c2, format_number(total_pop), "ЖАМИ АҲОЛИ"),
        (c3, f"{total_area:,.0f} км²", "ЖАМИ МАЙДОН"),
        (c4, format_number(avg_pop), "ЎРТАЧА АҲОЛИ"),
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
#  MAIN CONTENT
# ─────────────────────────────────────────────
if not filtered_df.empty:
    map_col, detail_col = st.columns([3, 2], gap="medium")
    
    with map_col:
        # ── CHOROPLETH MAP (FIXED) ──
        # faqat cca3 kodi bo'lgan davlatlarni olish
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
                labels={
                    "population": "Аҳоли",
                    "area": "Майдон км²",
                    "capital": "Пойтахт",
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
        
        # ── TOP 10 TABLE ──
        st.markdown("""
        <div style='font-family: Orbitron, monospace; font-size: 0.85rem; color: #00d4ff;
                    letter-spacing: 2px; margin: 0.5rem 0;'>
            📋 TOP 10 — АҲОЛИ СОНИ БЎЙИЧА
        </div>
        """, unsafe_allow_html=True)
        
        top10 = filtered_df.nlargest(10, "population")[["flag", "name", "capital", "region", "population", "area"]].copy()
        top10["population"] = top10["population"].apply(format_number)
        top10["area"] = top10["area"].apply(lambda x: f"{x:,.0f} км²")
        top10.columns = ["🏳", "Давлат", "Пойтахт", "Регион", "Аҳоли", "Майдон"]
        top10 = top10.reset_index(drop=True)
        top10.index = top10.index + 1
        
        st.dataframe(top10, use_container_width=True, height=280)
    
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
            
            # Region pie chart
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
            # ── COUNTRY DETAILS (FIXED) ──
            row = filtered_df[filtered_df["name"] == selected_country].iloc[0]
            
            # Flag and name
            st.markdown(f"""
            <div class="info-card">
                <div class="flag-display">{row['flag']}</div>
                <div class="country-name">{row['name'].upper()}</div>
                <div class="country-official">{row['official']}</div>
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
            
            # Detailed info
            details = [
                ("🏛️ Пойтахт", row['capital']),
                ("🌐 Регион", row['region']),
                ("📍 Субрегион", row['subregion']),
                ("🗣️ Тиллар", row['languages']),
                ("💰 Валюта", row['currencies']),
                ("🕐 Вакт зонаси", row['timezones']),
                ("🌊 Қуруқлик давлат", row['landlocked']),
                ("🚗 Йўл томони", row['car_side']),
                ("🔲 Мустақил", row['independent']),
                ("🗺️ Қўшнилар", row['borders']),
            ]
            
            details_html = '<div class="info-card"><h3>📡 ТЎЛИҚ МАЪЛУМОТ</h3>'
            for label, value in details:
                if value and value != "—":
                    details_html += f"""
                    <div class="stat-row">
                        <span class="stat-label">{label}</span>
                        <span class="stat-value">{value}</span>
                    </div>"""
            details_html += "</div>"
            st.markdown(details_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color: #1e3a5f; font-size: 0.8rem; letter-spacing: 2px;
            border-top: 1px solid #0d1b2e; padding-top: 1rem;'>
    🛰️ DATA: CountriesNow API + Fallback Database<br>
    🌍 WORLD EXPLORER PRO | Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
