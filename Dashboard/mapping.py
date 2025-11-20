# ============================================
# mapping.py — création de la carte Folium
# ============================================

import folium
import plotly.express as px
from constants import station_coords


def create_station_map(selected_stations, tiles, attr):
    """
    Crée la carte Folium avec les stations sélectionnées.
    """
    m = folium.Map(
        location=[-21.244, 55.708],
        zoom_start=13,
        tiles=tiles,
        attr=attr
    )

    colors = px.colors.qualitative.Bold * 2

    for i, sta in enumerate(selected_stations):
        if sta not in station_coords:
            continue

        lat, lon = station_coords[sta]

        folium.CircleMarker(
            location=[lat, lon],
            radius=22,
            color="#222",
            weight=3,
            fill=True,
            fill_color=colors[i % len(colors)],
            fill_opacity=0.90
        ).add_to(m)

        folium.Marker(
            [lat, lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:16px; font-weight:bold; color:white; text-shadow:2px 2px 4px black;">{sta}</div>'
            )
        ).add_to(m)

    return m
