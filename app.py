import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🌍 World Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  (dark space / neon aesthetic)
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
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_countries():
    """REST Countries API dan barcha davlatlar ma'lumotini olish"""
    try:
        url = "https://restcountries.com/v3.1/all?fields=name,flags,capital,region,subregion,population,area,languages,currencies,timezones,borders,latlng,tld,cca2,cca3,independent,landlocked,continents,car,coatOfArms"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()

        rows = []
        for c in data:
            try:
                name = c.get("name", {}).get("common", "Unknown")
                official = c.get("name", {}).get("official", name)
                latlng = c.get("latlng", [0, 0])
                lat = latlng[0] if len(latlng) > 0 else 0
                lon = latlng[1] if len(latlng) > 1 else 0

                # Languages
                langs = c.get("languages", {})
                languages = ", ".join(langs.values()) if langs else "—"

                # Currencies
                curr = c.get("currencies", {})
                currencies = ", ".join(
                    f"{v.get('name','')} ({v.get('symbol','')})"
                    for v in curr.values()
                ) if curr else "—"

                # Capital
                capitals = c.get("capital", [])
                capital = ", ".join(capitals) if capitals else "—"

                # TLD
                tlds = c.get("tld", [])
                tld = ", ".join(tlds) if tlds else "—"

                # Borders
                borders = c.get("borders", [])

                # Car side
                car_side = c.get("car", {}).get("side", "—")

                rows.append({
                    "name": name,
                    "official": official,
                    "cca2": c.get("cca2", ""),
                    "cca3": c.get("cca3", ""),
                    "flag": c.get("flags", {}).get("emoji", "🏳️"),
                    "capital": capital,
                    "region": c.get("region", "Unknown"),
                    "subregion": c.get("subregion", "—"),
                    "continents": ", ".join(c.get("continents", [])),
                    "population": c.get("population", 0),
                    "area": c.get("area", 0),
                    "languages": languages,
                    "currencies": currencies,
                    "timezones": ", ".join(c.get("timezones", [])),
                    "borders_list": borders,
                    "borders": ", ".join(borders) if borders else "Dengizga yoki okean bilan chegaralangan",
                    "tld": tld,
                    "landlocked": "Ha" if c.get("landlocked", False) else "Yo'q",
                    "independent": "Ha" if c.get("independent", False) else "Yo'q",
                    "car_side": car_side.capitalize() if car_side else "—",
                    "lat": lat,
                    "lon": lon,
                })
            except Exception:
                continue

        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"API xatosi: {e}")
        return pd.DataFrame()


def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f} mlrd"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.2f} mln"
    elif n >= 1_000:
        return f"{n/1_000:.1f} ming"
    return str(n)


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">🌍 WORLD EXPLORER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">INTERACTIVE GLOBAL COUNTRIES INTELLIGENCE PLATFORM</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("🛰️ Dunyo ma'lumotlari yuklanmoqda..."):
    df = load_countries()

if df.empty:
    st.error("Ma'lumotlar yuklanmadi. Internet aloqasini tekshiring.")
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

    # Subregion
    subregions = ["Hammasi"] + sorted(filtered_df["subregion"].dropna().unique().tolist())
    selected_sub = st.selectbox("📍 Subregion", subregions)
    if selected_sub != "Hammasi":
        filtered_df = filtered_df[filtered_df["subregion"] == selected_sub]

    st.divider()

    # Population filter
    pop_min, pop_max = int(df["population"].min()), int(df["population"].max())
    pop_range = st.slider(
        "👥 Aholi (mln)",
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
        format_func=lambda x: "Aholi soni" if x == "population" else "Maydon (km²)",
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
n_landlocked = (filtered_df["landlocked"] == "Ha").sum()

c1, c2, c3, c4 = st.columns(4)
for col, num, label in [
    (c1, f"{n_countries}", "DAVLATLAR"),
    (c2, format_number(total_pop), "JAMI AHOLI"),
    (c3, f"{total_area:,.0f} km²", "JAMI MAYDON"),
    (c4, f"{n_landlocked}", "QURUQLIK DAVLAT"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-num">{num}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN LAYOUT: Map | Detail
# ─────────────────────────────────────────────
map_col, detail_col = st.columns([3, 2], gap="medium")

with map_col:
    # ── CHOROPLETH MAP ──
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
            "population": "Aholi",
            "area": "Maydon km²",
            "capital": "Poytaxt",
            "region": "Region",
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

    # ── TOP 10 TABLE ──
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 0.85rem; color: #00d4ff;
                letter-spacing: 2px; margin: 0.5rem 0;'>
        📋 TOP 10 — AHOLI SONI BO'YICHA
    </div>
    """, unsafe_allow_html=True)

    top10 = filtered_df.nlargest(10, "population")[
        ["flag", "name", "capital", "region", "population", "area"]
    ].copy()
    top10["population"] = top10["population"].apply(format_number)
    top10["area"] = top10["area"].apply(lambda x: f"{x:,.0f} km²")
    top10.columns = ["🏳", "Davlat", "Poytaxt", "Region", "Aholi", "Maydon"]
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

        # Region breakdown pie
        if not filtered_df.empty:
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
                REGIONLAR BO'YICHA AHOLI
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})

    else:
        # ── COUNTRY DETAIL ──
        row = filtered_df[filtered_df["name"] == selected_country].iloc[0]

        # Flag + name
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

        # Details card
        details = [
            ("🏛️ Poytaxt", row["capital"]),
            ("🌐 Region", row["region"]),
            ("📍 Subregion", row["subregion"]),
            ("🗣️ Tillar", row["languages"]),
            ("💰 Valyuta", row["currencies"]),
            ("🕐 Vaqt zonasi", row["timezones"][:40] + "..." if len(row["timezones"]) > 40 else row["timezones"]),
            ("🌊 Quruqlik davlat", row["landlocked"]),
            ("🚗 Yo'l tomoni", row["car_side"]),
            ("🌐 TLD (domen)", row["tld"]),
            ("🔲 Mustaqil", row["independent"]),
            ("🗺️ Qo'shni davlatlar", row["borders"] if row["borders"] else "—"),
        ]

        details_html = '<div class="info-card"><h3>📡 TO\'LIQ MA\'LUMOT</h3>'
        for label, value in details:
            details_html += f"""
            <div class="stat-row">
                <span class="stat-label">{label}</span>
                <span class="stat-value" style="max-width:55%; text-align:right; font-size:0.82rem;">{value}</span>
            </div>"""
        details_html += "</div>"
        st.markdown(details_html, unsafe_allow_html=True)

        # Mini map for selected country
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
            🌐 GLOBUS JOYLASHUVI
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(mini_fig, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color: #1e3a5f; font-size: 0.8rem; letter-spacing: 2px;
            border-top: 1px solid #0d1b2e; padding-top: 1rem;'>
    🛰️ DATA: REST Countries API &nbsp;|&nbsp; 🌍 WORLD EXPLORER &nbsp;|&nbsp; Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
