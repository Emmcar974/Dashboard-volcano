import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Piton de la Fournaise - Prédiction", layout="wide")

# ==================== TITRE ====================
st.markdown(
    "<h1 style='text-align:center; color:darkred; font-weight:bold;'>Prédiction d'éruption volcanique🌋 </h1>",
    unsafe_allow_html=True,
)

main_col, risk_col = st.columns([4.5, 1.5])

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("Filtres & Paramètres")

    st.markdown(
        """
        **Dates des éruptions passées étudiées :**
        - 11/09/2016  
        - 25/10/2019  
        - 07/12/2020  
        - 02/07/2023
        """
    )

    eruption_dates = [
        date(2016, 9, 11),
        date(2019, 10, 25),
        date(2020, 12, 7),
        date(2023, 7, 2),
    ]

    # 🔥 Sélection multiple d'éruptions
    selected_eruptions = st.multiselect(
        "Éruptions à analyser",
        options=eruption_dates,
        default=[date(2020, 12, 7)],
        format_func=lambda d: d.strftime("%d/%m/%Y"),
    )

    file_map = {
        date(2016, 9, 11): "2016_09_pf_aggregated_2016_1min_1Hz.csv",
        date(2019, 10, 25): "2019_10_pf_aggregated_2019_1min_1Hz.csv",
        date(2020, 12, 7): "2020_12_04pf_aggregated_1min_1Hz.csv",
        date(2023, 7, 2): "2023_07_pf_aggregated_2023_1min_1Hz.csv",
    }

    @st.cache_data
    def load_data(d):
        df = pd.read_csv(file_map[d])
        df["time_min"] = pd.to_datetime(df["time_min"])
        df["eruption_date"] = d
        return df

    # 🔥 Charger plusieurs éruptions
    if selected_eruptions:
        df = pd.concat([load_data(d) for d in selected_eruptions], ignore_index=True)
    else:
        df = pd.DataFrame()

    stations = sorted(df["station"].unique())
    selected_stations = st.multiselect("Stations", stations, default=stations[:6])

df_filtered = df[df["station"].isin(selected_stations)].copy() if selected_stations else pd.DataFrame()

# ==================== RISQUE ====================
max_std = df["amplitude_std"].max() if not df.empty else 0

if max_std > 100_000:
    risk_text, risk_color, risk_emoji = "Éruption en cours", "purple", "🟪"
elif max_std > 30_000:
    risk_text, risk_color, risk_emoji = "Risque < 1h", "red", "🔴"
elif max_std > 10_000:
    risk_text, risk_color, risk_emoji = "Risque < 12h", "orange", "🟠"
elif max_std > 3_000:
    risk_text, risk_color, risk_emoji = "Risque < 24h", "goldenrod", "🟡"
else:
    risk_text, risk_color, risk_emoji = "Pas de risque", "green", "🟢"

# ==================== COLONNE RISQUE ====================
with risk_col:
    st.markdown("## Niveau de risque actuel")
    st.markdown(
        f"""
        <div style="text-align:center; padding:20px; border-radius:15px; background:#333; color:white;">
            <h2 style="margin:5px; color:{risk_color}">{risk_emoji}🌋</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Légende")
    legend = [
        ("purple","Éruption en cours"),
        ("red","Risque très élevé (<1h)"),
        ("orange","Risque élevé (<12h)"),
        ("goldenrod","Risque modéré (<24h)"),
        ("green","Pas de risque détecté"),
    ]
    for col, txt in legend:
        if txt == risk_text:
            st.markdown(
                f"<div style='background:linear-gradient(90DEG,{col}40,transparent); padding:12px; border-left:6px solid {col}; border-radius:8px; margin:8px 0;'><strong style='color:{col}'>➤ {txt} ← ACTUEL</strong></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"<small style='color:{col}'>{txt}</small>", unsafe_allow_html=True)

# ==================== CARTE ====================
with main_col:
    st.markdown("## Carte des stations")

    coords = {
        'DSM': (-21.11, 55.53), 'BON': (-21.24, 55.70), 'DSO': (-21.17, 55.55),
        'ENO': (-21.31, 55.68), 'NSR': (-21.39, 55.60), 'NTR': (-21.30, 55.60),
        'BLE': (-21.28, 55.57), 'CSS': (-21.26, 55.68), 'HIM': (-21.20, 55.67),
        'PJR': (-21.35, 55.69), 'PCR': (-21.29, 55.64), 'PER': (-21.34, 55.61),
        'TKR': (-21.23, 55.56), 'FJS': (-21.27, 55.62), 'SNE': (-21.32, 55.58),
    }

    map_df = pd.DataFrame([{"station": s, "lat": coords[s][0], "lon": coords[s][1]}
                           for s in selected_stations if s in coords])

    if not map_df.empty:
        fig_map = px.scatter_mapbox(
            map_df, lat="lat", lon="lon", color="station",
            hover_name="station", text="station", zoom=10.3,
            center={"lat": -21.25, "lon": 55.60}, height=620
        )
        fig_map.update_traces(marker=dict(size=48, opacity=0.95))
        fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_map, use_container_width=True)

# ==================== GRAPHIQUES ====================
if not df_filtered.empty:

    st.markdown("## Comparaison de l’activité avant plusieurs éruptions")

    # ------- 1. Graphique par station -------
    fig1 = px.line(
        df_filtered.sort_values("time_min"),
        x="time_min",
        y="amplitude_std",
        color="eruption_date",    # 🔥 distinction par date d’éruption
        line_dash="station",
        title="Écart-type de l'amplitude par station et par éruption"
    )

    # 🔥 Ligne verticale pour CHAQUE éruption sélectionnée
    for d in selected_eruptions:
        eruption_time = df[df["eruption_date"] == d]["time_min"].max()

        fig1.add_shape(
            type="line", x0=eruption_time, x1=eruption_time, y0=0, y1=1,
            xref="x", yref="paper", line=dict(width=4)
        )
        fig1.add_annotation(
            x=eruption_time, y=1, yref="paper",
            text=d.strftime("%d/%m/%Y"),
            showarrow=False,
            font=dict(color="white", size=12),
            bgcolor="black",
            yanchor="bottom"
        )

    fig1.update_layout(height=600)
    st.plotly_chart(fig1, use_container_width=True)

    # ------- 2. Moyenne + intervalle -------
    st.markdown("## Moyenne globale (±1 écart-type)")

    df_avg = df_filtered.groupby(["eruption_date", "time_min"])["amplitude_std"].agg(["mean", "std"]).reset_index()
    df_avg["lower"] = df_avg["mean"] - df_avg["std"]
    df_avg["upper"] = df_avg["mean"] + df_avg["std"]

    fig2 = go.Figure()

    for d in selected_eruptions:
        sub = df_avg[df_avg["eruption_date"] == d]

        fig2.add_trace(go.Scatter(
            x=sub["time_min"], y=sub["upper"],
            line=dict(width=0), showlegend=False
        ))
        fig2.add_trace(go.Scatter(
            x=sub["time_min"], y=sub["lower"],
            fill="tonexty", fillcolor="rgba(255,100,100,0.3)",
            line=dict(width=0), showlegend=False
        ))
        fig2.add_trace(go.Scatter(
            x=sub["time_min"], y=sub["mean"],
            line=dict(width=4), name=d.strftime("%d/%m/%Y")
        ))

        # Ligne verticale
        eruption_time = df[df["eruption_date"] == d]["time_min"].max()

        fig2.add_shape(
            type="line", x0=eruption_time, x1=eruption_time, y0=0, y1=1,
            xref="x", yref="paper", line=dict(width=4)
        )

        fig2.add_annotation(
            x=eruption_time, y=1, yref="paper",
            text=d.strftime("%d/%m/%Y"),
            showarrow=False, bgcolor="black",
            font=dict(color="white", size=12),
            yanchor="bottom"
        )

    fig2.update_layout(height=600, title="Activité moyenne par éruption")
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("Aucune station sélectionnée.")
