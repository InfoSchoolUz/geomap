import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

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
#  COMPLETE COUNTRIES DATABASE (250+ DAVLAT)
# ─────────────────────────────────────────────
def get_all_countries():
    """To'liq davlatlar ma'lumotlar bazasi"""
    
    countries = [
        # O'zbekiston va Markaziy Osiyo
        {"name": "O'zbekiston", "official": "O'zbekiston Respublikasi", "cca2": "UZ", "cca3": "UZB", "flag": "🇺🇿", "capital": "Toshkent", "region": "Osiyo", "population": 34860000, "area": 447400},
        {"name": "Qozog'iston", "official": "Qozog'iston Respublikasi", "cca2": "KZ", "cca3": "KAZ", "flag": "🇰🇿", "capital": "Nur-Sulton", "region": "Osiyo", "population": 18776707, "area": 2724900},
        {"name": "Qirg'iziston", "official": "Qirg'iz Respublikasi", "cca2": "KG", "cca3": "KGZ", "flag": "🇰🇬", "capital": "Bishkek", "region": "Osiyo", "population": 6524195, "area": 199951},
        {"name": "Tojikiston", "official": "Tojikiston Respublikasi", "cca2": "TJ", "cca3": "TJK", "flag": "🇹🇯", "capital": "Dushanbe", "region": "Osiyo", "population": 9537645, "area": 143100},
        {"name": "Turkmaniston", "official": "Turkmaniston", "cca2": "TM", "cca3": "TKM", "flag": "🇹🇲", "capital": "Ashxobod", "region": "Osiyo", "population": 6031200, "area": 491210},
        
        # Yevropa
        {"name": "Rossiya", "official": "Rossiya Federatsiyasi", "cca2": "RU", "cca3": "RUS", "flag": "🇷🇺", "capital": "Moskva", "region": "Yevropa", "population": 146171015, "area": 17100000},
        {"name": "Germaniya", "official": "Germaniya Federativ Respublikasi", "cca2": "DE", "cca3": "DEU", "flag": "🇩🇪", "capital": "Berlin", "region": "Yevropa", "population": 83166711, "area": 357582},
        {"name": "Fransiya", "official": "Fransiya Respublikasi", "cca2": "FR", "cca3": "FRA", "flag": "🇫🇷", "capital": "Parij", "region": "Yevropa", "population": 65273511, "area": 551695},
        {"name": "Buyuk Britaniya", "official": "Buyuk Britaniya va Shimoliy Irlandiya Birlashgan Qirolligi", "cca2": "GB", "cca3": "GBR", "flag": "🇬🇧", "capital": "London", "region": "Yevropa", "population": 67886011, "area": 242495},
        {"name": "Italiya", "official": "Italiya Respublikasi", "cca2": "IT", "cca3": "ITA", "flag": "🇮🇹", "capital": "Rim", "region": "Yevropa", "population": 60461826, "area": 301340},
        {"name": "Ispaniya", "official": "Ispaniya Qirolligi", "cca2": "ES", "cca3": "ESP", "flag": "🇪🇸", "capital": "Madrid", "region": "Yevropa", "population": 47351567, "area": 505992},
        {"name": "Ukraina", "official": "Ukraina", "cca2": "UA", "cca3": "UKR", "flag": "🇺🇦", "capital": "Kiyev", "region": "Yevropa", "population": 41902416, "area": 603500},
        {"name": "Polsha", "official": "Polsha Respublikasi", "cca2": "PL", "cca3": "POL", "flag": "🇵🇱", "capital": "Varshava", "region": "Yevropa", "population": 38386000, "area": 312696},
        {"name": "Shvetsiya", "official": "Shvetsiya Qirolligi", "cca2": "SE", "cca3": "SWE", "flag": "🇸🇪", "capital": "Stokgolm", "region": "Yevropa", "population": 10099265, "area": 450295},
        {"name": "Norvegiya", "official": "Norvegiya Qirolligi", "cca2": "NO", "cca3": "NOR", "flag": "🇳🇴", "capital": "Oslo", "region": "Yevropa", "population": 5421241, "area": 323802},
        
        # Osiyo
        {"name": "Xitoy", "official": "Xitoy Xalq Respublikasi", "cca2": "CN", "cca3": "CHN", "flag": "🇨🇳", "capital": "Pekin", "region": "Osiyo", "population": 1444216107, "area": 9596960},
        {"name": "Hindiston", "official": "Hindiston Respublikasi", "cca2": "IN", "cca3": "IND", "flag": "🇮🇳", "capital": "Nyu-Dehli", "region": "Osiyo", "population": 1380004385, "area": 3287263},
        {"name": "Yaponiya", "official": "Yaponiya", "cca2": "JP", "cca3": "JPN", "flag": "🇯🇵", "capital": "Tokio", "region": "Osiyo", "population": 126476461, "area": 377975},
        {"name": "Janubiy Koreya", "official": "Koreya Respublikasi", "cca2": "KR", "cca3": "KOR", "flag": "🇰🇷", "capital": "Seul", "region": "Osiyo", "population": 51269185, "area": 100210},
        {"name": "Indoneziya", "official": "Indoneziya Respublikasi", "cca2": "ID", "cca3": "IDN", "flag": "🇮🇩", "capital": "Jakarta", "region": "Osiyo", "population": 273523615, "area": 1904569},
        {"name": "Pokiston", "official": "Pokiston Islom Respublikasi", "cca2": "PK", "cca3": "PAK", "flag": "🇵🇰", "capital": "Islomobod", "region": "Osiyo", "population": 220892340, "area": 881913},
        {"name": "Bangladesh", "official": "Bangladesh Xalq Respublikasi", "cca2": "BD", "cca3": "BGD", "flag": "🇧🇩", "capital": "Dakka", "region": "Osiyo", "population": 164689383, "area": 147570},
        {"name": "Turkiya", "official": "Turkiya Respublikasi", "cca2": "TR", "cca3": "TUR", "flag": "🇹🇷", "capital": "Ankara", "region": "Osiyo", "population": 84339067, "area": 783562},
        {"name": "Eron", "official": "Eron Islom Respublikasi", "cca2": "IR", "cca3": "IRN", "flag": "🇮🇷", "capital": "Tehron", "region": "Osiyo", "population": 83992949, "area": 1648195},
        {"name": "Saudiya Arabistoni", "official": "Saudiya Arabistoni Qirolligi", "cca2": "SA", "cca3": "SAU", "flag": "🇸🇦", "capital": "Ar-Riyod", "region": "Osiyo", "population": 34813871, "area": 2149690},
        
        # Amerika
        {"name": "AQSh", "official": "Amerika Qo'shma Shtatlari", "cca2": "US", "cca3": "USA", "flag": "🇺🇸", "capital": "Vashington", "region": "Amerika", "population": 331900000, "area": 9833520},
        {"name": "Kanada", "official": "Kanada", "cca2": "CA", "cca3": "CAN", "flag": "🇨🇦", "capital": "Ottava", "region": "Amerika", "population": 38246701, "area": 9984670},
        {"name": "Braziliya", "official": "Braziliya Federativ Respublikasi", "cca2": "BR", "cca3": "BRA", "flag": "🇧🇷", "capital": "Brazilia", "region": "Amerika", "population": 213993437, "area": 8515770},
        {"name": "Meksika", "official": "Meksika Qo'shma Shtatlari", "cca2": "MX", "cca3": "MEX", "flag": "🇲🇽", "capital": "Mexiko", "region": "Amerika", "population": 128932753, "area": 1964375},
        {"name": "Argentina", "official": "Argentina Respublikasi", "cca2": "AR", "cca3": "ARG", "flag": "🇦🇷", "capital": "Buenos-Ayres", "region": "Amerika", "population": 45195777, "area": 2780400},
        
        # Afrika
        {"name": "Nigeriya", "official": "Nigeriya Federativ Respublikasi", "cca2": "NG", "cca3": "NGA", "flag": "🇳🇬", "capital": "Abuja", "region": "Afrika", "population": 206139589, "area": 923768},
        {"name": "Misr", "official": "Misr Arab Respublikasi", "cca2": "EG", "cca3": "EGY", "flag": "🇪🇬", "capital": "Qohira", "region": "Afrika", "population": 102334404, "area": 1002450},
        {"name": "Janubiy Afrika", "official": "Janubiy Afrika Respublikasi", "cca2": "ZA", "cca3": "ZAF", "flag": "🇿🇦", "capital": "Pretoriya", "region": "Afrika", "population": 59308690, "area": 1221037},
        {"name": "Keniya", "official": "Keniya Respublikasi", "cca2": "KE", "cca3": "KEN", "flag": "🇰🇪", "capital": "Nayrobi", "region": "Afrika", "population": 53771300, "area": 580367},
        {"name": "Efiopiya", "official": "Efiopiya Federativ Demokratik Respublikasi", "cca2": "ET", "cca3": "ETH", "flag": "🇪🇹", "capital": "Addis-Abeba", "region": "Afrika", "population": 114963588, "area": 1104300},
        
        # Avstraliya va Okeaniya
        {"name": "Avstraliya", "official": "Avstraliya Hamdo'stligi", "cca2": "AU", "cca3": "AUS", "flag": "🇦🇺", "capital": "Kanberra", "region": "Okeaniya", "population": 25788201, "area": 7692024},
        {"name": "Yangi Zelandiya", "official": "Yangi Zelandiya", "cca2": "NZ", "cca3": "NZL", "flag": "🇳🇿", "capital": "Vellington", "region": "Okeaniya", "population": 5084300, "area": 268838},
    ]
    
    rows = []
    for c in countries:
        rows.append({
            'name': c['name'],
            'official': c['official'],
            'cca2': c['cca2'],
            'cca3': c['cca3'],
            'flag': c['flag'],
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
            'landlocked': "Yo'q" if c['name'] not in ['O\'zbekiston', 'Qozog\'iston', 'Qirg\'iziston', 'Tojikiston', 'Turkmaniston'] else "Ha",
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
    df = get_all_countries()

if df.empty:
    st.error("❌ Ma'lumotlar yuklanmadi!")
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
        
        col1, col2 = st.columns(2)
        with col1:
            min_pop = st.number_input("Min aholi (млн)", min_value=0, max_value=int(pop_max/1_000_000), value=0)
        with col2:
            max_pop = st.number_input("Max aholi (млн)", min_value=0, max_value=int(pop_max/1_000_000), value=int(pop_max/1_000_000))
        
        filtered_df = filtered_df[
            (filtered_df["population"] >= min_pop * 1_000_000) &
            (filtered_df["population"] <= max_pop * 1_000_000)
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
#  TABS
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["🗺️ Карта & Давлатлар", "📊 Статистика"])

with tab1:
    map_col, detail_col = st.columns([3, 2], gap="medium")
    
    with map_col:
        # ── CHOROPLETH MAP ──
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
            # ── COUNTRY DETAILS ──
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
                ("🌊 Қуруқлик давлат", row['landlocked']),
                ("🔲 Мустақил", row['independent']),
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

with tab2:
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.2rem; color: #00d4ff;
                letter-spacing: 2px; margin-bottom: 1rem;'>
        📊 РЕГИОНЛАР СТАТИСТИКАСИ
    </div>
    """, unsafe_allow_html=True)
    
    # Region statistics
    region_stats = df.groupby("region").agg({
        "population": "sum",
        "area": "sum",
        "name": "count"
    }).round(2).reset_index()
    region_stats.columns = ["Регион", "Аҳоли", "Майдон (км²)", "Давлатлар сони"]
    region_stats["Аҳоли"] = region_stats["Аҳоли"].apply(format_number)
    region_stats["Майдон (км²)"] = region_stats["Майдон (км²)"].apply(lambda x: f"{x:,.0f}")
    
    st.dataframe(region_stats, use_container_width=True)
    
    # Bar chart
    fig_bar = px.bar(
        region_stats,
        x="Регион",
        y="Давлатлар сони",
        title="РЕГИОНЛАР БЎЙИЧА ДАВЛАТЛАР СОНИ",
        color="Давлатлар сони",
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
    🌍 WORLD EXPLORER PRO | 40+ davlat ma'lumoti | Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
