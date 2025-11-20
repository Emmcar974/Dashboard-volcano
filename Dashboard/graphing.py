# ============================================
# graphing.py — graphes Plotly du dashboard
# ============================================

import numpy as np
import plotly.graph_objects as go
from constants import eruptions, color_map, rgba_map

# -----------------------------------------------------------
# 1. Courbe : amplitude moyenne
# -----------------------------------------------------------

def plot_amplitude(df_compare):
    fig = go.Figure()

    for eruption in df_compare["eruption"].unique():
        sub = df_compare[df_compare["eruption"] == eruption]
        c = sub["color"].iloc[0]

        fig.add_trace(go.Scatter(
            x=sub["hours_to_eruption"],
            y=sub["amplitude_mean"],
            mode="lines",
            name=eruption,
            line=dict(width=4, color=c)
        ))

    fig.add_vline(x=0, line=dict(color="red", width=4, dash="dash"))

    fig.update_layout(
        height=500,
        template="simple_white",
        xaxis_title="Heures avant/après éruption",
        yaxis_title="Amplitude moyenne"
    )
    return fig


# -----------------------------------------------------------
# 2. Courbe RSAM
# -----------------------------------------------------------

def plot_rsam(df_compare):
    fig = go.Figure()

    for eruption in df_compare["eruption"].unique():
        sub = df_compare[df_compare["eruption"] == eruption]
        c = sub["color"].iloc[0]

        fig.add_trace(go.Scatter(
            x=sub["hours_to_eruption"],
            y=sub["RSAM"],
            mode="lines",
            name=eruption,
            line=dict(width=4, color=c)
        ))

    fig.add_vline(x=0, line=dict(color="red", width=4, dash="dash"))

    fig.update_layout(
        height=500,
        template="simple_white",
        xaxis_title="Heures avant/après éruption",
        yaxis_title="RSAM"
    )
    return fig


# -----------------------------------------------------------
# 3. Énergie cumulée
# -----------------------------------------------------------

def plot_energy(df_compare):
    fig = go.Figure()

    for eruption in df_compare["eruption"].unique():
        sub = df_compare[df_compare["eruption"] == eruption].sort_values("hours_to_eruption")
        energy = (sub["amplitude_mean"]**2).cumsum()

        c = sub["color"].iloc[0]

        fig.add_trace(go.Scatter(
            x=sub["hours_to_eruption"],
            y=energy,
            mode="lines",
            name=eruption,
            line=dict(width=4, color=c)
        ))

    fig.add_vline(x=0, line=dict(color="red", width=4, dash="dash"))

    fig.update_layout(
        height=500,
        template="simple_white",
        xaxis_title="Heures avant/après éruption",
        yaxis_title="Énergie sismique cumulée"
    )
    return fig


# -----------------------------------------------------------
# 4. Intervalle de confiance à 95 %
# -----------------------------------------------------------

def plot_confidence(df_compare):
    fig = go.Figure()

    for eruption in df_compare["eruption"].unique():
        sub = df_compare[df_compare["eruption"] == eruption]

        sub = sub.set_index("time_min")["amplitude_mean"]
        res = sub.resample("10min").mean()

        roll = res.rolling(window=6, min_periods=3, center=True)
        mean = roll.mean()
        std = roll.std()
        count = roll.count()

        hours = (mean.index - eruptions[eruption]["time"]).total_seconds() / 3600
        upper = mean + 1.96 * std / np.sqrt(count)
        lower = mean - 1.96 * std / np.sqrt(count)

        color = color_map[eruption]
        rgba = rgba_map[color]

        fig.add_trace(go.Scatter(
            x=hours,
            y=mean,
            mode="lines",
            name=eruption,
            line=dict(color=color, width=4)
        ))

        fig.add_trace(go.Scatter(
            x=list(hours) + list(hours[::-1]),
            y=list(upper) + list(lower[::-1]),
            fill="toself",
            fillcolor=rgba,
            line=dict(width=0),
            showlegend=False
        ))

    fig.add_vline(x=0, line=dict(color="red", width=4, dash="dash"))

    fig.update_layout(
        height=650,
        template="simple_white",
        xaxis_title="Heures",
        yaxis_title="Amplitude ± 95% IC"
    )
    return fig
