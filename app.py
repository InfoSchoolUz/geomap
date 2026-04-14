import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def get_all_countries():
    """195 ta davlatni bitta fayl ichida REST Countries orqali olib keladi."""

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
        "North Korea": "Shimoliy Koreya",
        "Turkey": "Turkiya",
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
    }

    try:
        url = (
            "https://restcountries.com/v3.1/all"
            "?fields=name,cca2,cca3,capital,region,subregion,population,area,"
            "languages,currencies,timezones,borders,tld,landlocked,car,latlng,flag,independent"
        )
        response = requests.get(url, timeout=40)
        response.raise_for_status()
        data = response.json()

        rows = []
        for c in data:
            cca3 = c.get("cca3", "")
            if cca3 not in UN_195:
                continue

            common_name = c.get("name", {}).get("common", "Noma'lum")
            official_name = c.get("name", {}).get("official", common_name)

            name_display = NAME_UZ.get(common_name, common_name)

            capital = c.get("capital", ["—"])
            capital = capital[0] if capital else "—"

            languages = c.get("languages", {})
            currencies = c.get("currencies", {})
            timezones = c.get("timezones", [])
            borders = c.get("borders", [])
            tld = c.get("tld", [])
            latlng = c.get("latlng", [0, 0])
            car = c.get("car", {})

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
                "landlocked": "Ha" if c.get("landlocked", False) else "Yo'q",
                "independent": "Ha" if c.get("independent", True) else "Yo'q",
                "car_side": car.get("side", "—").capitalize() if car.get("side") else "—",
                "lat": latlng[0] if isinstance(latlng, list) and len(latlng) > 0 else 0,
                "lon": latlng[1] if isinstance(latlng, list) and len(latlng) > 1 else 0,
            })

        df = pd.DataFrame(rows)

        # Ba'zi nomlar takror chiqsa, oxirgi holatda bitta qoldiramiz
        if not df.empty:
            df = df.drop_duplicates(subset=["cca3"]).reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"❌ 195 davlatni yuklashda xatolik: {e}")
        return pd.DataFrame()
