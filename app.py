import time

# ─────────────────────────────────────────────
#  EXTRA DATA HELPERS (HOZIRGI FUNKSIYALARGA TEGMAYDI)
# ─────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_world_bank_indicator(country_code, indicator):
    """
    World Bank indikatorini olib keladi.
    country_code: ISO3 (masalan UZB, USA)
    indicator: masalan NY.GDP.MKTP.CD
    """
    try:
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=100"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()

        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return None, None

        # Eng oxirgi bo'sh bo'lmagan qiymatni olamiz
        for item in data[1]:
            if item.get("value") is not None:
                return item.get("value"), item.get("date")

        return None, None
    except Exception:
        return None, None


@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_wikidata_head_of_state(country_name_en):
    """
    Wikidata SPARQL orqali davlat rahbarini olishga urinadi.
    Eslatma: bu yerda English country label bilan qidirish barqarorroq.
    """
    try:
        query = f"""
        SELECT ?countryLabel ?headOfStateLabel WHERE {{
          ?country rdfs:label "{country_name_en}"@en.
          ?country wdt:P31 wd:Q3624078.
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
        r = requests.get(url, params={"query": query}, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()

        bindings = data.get("results", {}).get("bindings", [])
        if bindings:
            return bindings[0].get("headOfStateLabel", {}).get("value")
        return None
    except Exception:
        return None


def uz_to_en_country_name(name_uz):
    """
    Ba'zi davlat nomlarini English formatga yaqinlashtirish.
    Hammasini mukammal qilmaydi, lekin asosiylari ishlaydi.
    """
    mapping = {
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
    return mapping.get(name_uz, name_uz)


@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def enrich_country_row(cca3, name_uz):
    """
    Har bir davlat uchun qo'shimcha statistika.
    """
    country_name_en = uz_to_en_country_name(name_uz)

    # World Bank indikatorlari
    gdp, gdp_year = fetch_world_bank_indicator(cca3, "NY.GDP.MKTP.CD")              # GDP (current US$)
    gdp_per_capita, gdp_pc_year = fetch_world_bank_indicator(cca3, "NY.GDP.PCAP.CD") # GDP per capita
    agr_pct, agr_year = fetch_world_bank_indicator(cca3, "NV.AGR.TOTL.ZS")           # Agriculture % of GDP
    industry_pct, ind_year = fetch_world_bank_indicator(cca3, "NV.IND.TOTL.ZS")      # Industry % of GDP
    services_pct, serv_year = fetch_world_bank_indicator(cca3, "NV.SRV.TOTL.ZS")     # Services % of GDP
    inflation, infl_year = fetch_world_bank_indicator(cca3, "FP.CPI.TOTL.ZG")        # Inflation
    life_exp, life_year = fetch_world_bank_indicator(cca3, "SP.DYN.LE00.IN")         # Life expectancy
    urban_pct, urban_year = fetch_world_bank_indicator(cca3, "SP.URB.TOTL.IN.ZS")    # Urban population %

    # Wikidata
    president = fetch_wikidata_head_of_state(country_name_en)

    return {
        "president": president if president else "—",
        "gdp_usd": gdp,
        "gdp_year": gdp_year,
        "gdp_per_capita": gdp_per_capita,
        "gdp_pc_year": gdp_pc_year,
        "agriculture_pct": agr_pct,
        "agriculture_year": agr_year,
        "industry_pct": industry_pct,
        "industry_year": ind_year,
        "services_pct": services_pct,
        "services_year": serv_year,
        "inflation_pct": inflation,
        "inflation_year": infl_year,
        "life_expectancy": life_exp,
        "life_year": life_year,
        "urban_population_pct": urban_pct,
        "urban_year": urban_year,
    }


@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def enrich_dataframe(df):
    enriched_rows = []

    for _, row in df.iterrows():
        extra = enrich_country_row(row["cca3"], row["name"])
        enriched_rows.append(extra)
        time.sleep(0.05)  # Juda tez urib API'ni bo'g'maslik uchun

    extra_df = pd.DataFrame(enriched_rows)
    return pd.concat([df.reset_index(drop=True), extra_df.reset_index(drop=True)], axis=1)


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
