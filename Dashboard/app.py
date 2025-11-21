# dashboard.py rewritten using modules
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium

from Dashboard_VF.Dashboard.constants import eruptions, color_map, rgba_map, station_coords
from Dashboard_VF.Dashboard.data_loader import load_eruption_file, load_raw_file, load_window
from Dashboard_VF.Dashboard.graphing import plot_amplitude, plot_rsam, plot_energy, plot_confidence
from Dashboard_VF.Dashboard.mapping import create_station_map
from Dashboard_VF.Dashboard.preprocess import preprocess_data

st.set_page_config(page_title="Piton de la Fournaise - Prédiction", layout="wide")

# Title
st.markdown("<h1 style='text-align:center; color:darkred; font-weight:bold;'>Prédiction d'éruption volcanique🌋 </h1>", unsafe_allow_html=True)

main_col, risk_col = st.columns([4.5, 1.5])

# Sidebar alert system
st.sidebar.image("https://media.gettyimages.com/id/110834060/fr/photo/reunion-eruption-of-the-piton-de-la-fournaise-in-reunion-on-april-03-2007-piton-de-la.jpg?s=612x612&w=0&k=20&c=32ejXjNKw5GpQf9ypQdWXSHV8BIhbkNW9hw8m9zu9nE=")
st.sidebar.title("Système d'alerte en temps réel")

# Compute latest RSAM from last eruption
latest_name = list(eruptions.keys())[-1]
try:
    df_latest = load_eruption_file(latest_name).tail(100)
    latest_rsam = df_latest["amplitude_mean"].mean() if "amplitude_mean" in df_latest else 500
except:
    latest_rsam = 500

if latest_rsam > 5000:
    level, color, emoji = "ÉRUPTION", "#9f00e0", "🟪"
elif latest_rsam > 3000:
    level, color, emoji = "IMMINENT (<1h)", "#e60000", "🔴"
elif latest_rsam > 1500:
    level, color, emoji = "ÉLEVÉ (<12h)", "#ff6600", "🟠"
elif latest_rsam > 800:
    level, color, emoji = "MOYEN (<48h)", "#ffd700", "🟡"
else:
    level, color, emoji = "NORMAL", "#00b300", "🟢"

st.sidebar.markdown(f"""
<div style='text-align:center; padding:20px; border-radius:20px; background:linear-gradient(135deg, #1a1a1a, #2d2d2d); border:3px solid {color}; box-shadow:0 0 30px {color}40;'>
    <h1 style='margin:0; color:{color}; font-size:60px;'>{emoji}</h1>
    <h2 style='margin:10px 0 5px; color:white;'>{level}</h2>
    <p style='margin:0; color:#ccc; font-size:14px;'>RSAM: {latest_rsam:,.0f}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar selection for comparison
st.sidebar.markdown("---")
st.sidebar.subheader("Éruptions comparées")
selected_for_compare = st.sidebar.multiselect(
    "Sélectionnez les éruptions à comparer",
    options=list(eruptions.keys()),
    default=list(eruptions.keys())
)
st.sidebar.markdown("### Stations pour les comparatifs")
selected_compare_stations = st.sidebar.multiselect(
    "Stations à inclure dans les comparatifs",
    options=station_coords.keys(),
    default=list(station_coords.keys())
)

# MAP SECTION
st.markdown("### Stations sismiques actives")
col_map, col_controls = st.columns([7, 3])

with col_map:
    selected_main = st.session_state.get("main_eruption_map", list(eruptions.keys())[0])

    df_map = load_eruption_file(selected_main)
    erupt_time = eruptions[selected_main]["time"]
    df_map = df_map[df_map["time_min"] >= erupt_time - pd.Timedelta(days=4)]

    tile_option = st.radio(
        "Style de carte",
        options=["Street (OpenStreetMap)", "Satellite (Google)", "Topographic (OpenTopoMap)"],
        index=1,
        horizontal=True,
        key="map_tile_selector"
    )

    if tile_option == "Street (OpenStreetMap)":
        tiles = "OpenStreetMap"; attr = "© OpenStreetMap contributors"
    elif tile_option == "Satellite (Google)":
        tiles = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&s=Galileo"; attr = "© Google"
    else:
        tiles = "https://tile.opentopomap.org/{z}/{x}/{y}.png"; attr = "© OpenTopoMap"

    selected_stations_map = st.session_state.get("selected_stations_map", [])
    m = create_station_map(selected_stations_map, tiles, attr)
    st_folium(m, width=700, height=555, key="map_final")

with col_controls:
    st.markdown("**Paramètres de la carte**")
    selected_main = st.selectbox("Éruption pour l'affichage de la carte", options=list(eruptions.keys()), key="main_eruption_map")

    df_temp = load_raw_file(selected_main)
    available_stations = sorted(df_temp["station"].unique())

    selected_stations_map = st.multiselect(
        "Stations à afficher",
        options=available_stations,
        default=available_stations[:10],
        key="selected_stations_map"
    )

# COMPARISON DATA
@st.cache_data
def load_aligned_selected(selected_list, selected_stations):
    frames = []
    for name in selected_list:
        df = load_eruption_file(name)

        # filtrage par stations
        df = df[df["station"].isin(selected_stations)]

        info = eruptions[name]
        start = info["time"] - pd.Timedelta(hours=82)
        end = info["time"] + pd.Timedelta(hours=24)

        df = df[(df["time_min"] >= start) & (df["time_min"] <= end)]
        if df.empty:
            continue

        # Ré-agrégation APRÈS filtrage
        df["hours_to_eruption"] = (df["time_min"] - info["time"]).dt.total_seconds() / 3600
        df = df[(df["hours_to_eruption"] >= -80) & (df["hours_to_eruption"] <= 24)]

        res = (
            df.set_index("time_min")
            .resample("10min")
            .mean(numeric_only=True)
            .reset_index()
        )

        res["hours_to_eruption"] = (res["time_min"] - info["time"]).dt.total_seconds() / 3600
        res["eruption"] = name
        res["color"] = color_map[name]

        frames.append(res)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

df_compare = load_aligned_selected(selected_for_compare, selected_compare_stations)

if not df_compare.empty:
    st.markdown("---")
    st.markdown(f"# Précurseurs pré-éruptifs – {len(selected_for_compare)} éruptions alignées")

    st.subheader("Amplitude sismique moyenne du réseau")
    st.plotly_chart(plot_amplitude(df_compare), use_container_width=True)

    st.subheader("RSAM – mesure en temps réel")
    st.plotly_chart(plot_rsam(df_compare), use_container_width=True)

    st.subheader("Énergie sismique cumulée libérée")
    st.plotly_chart(plot_energy(df_compare), use_container_width=True)

    st.subheader("Amplitude ± IC95%")
    st.plotly_chart(plot_confidence(df_compare), use_container_width=True)

# FOOTER
st.success("**Piton de la Fournaise – Next-Gen Volcano Monitoring System** | Dashboard optimisé")
st.caption("© David, Gabriel, Emmeline & Mathias | Jedha Fullstack 2025")