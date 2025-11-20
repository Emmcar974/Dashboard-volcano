# ============================================
# constants.py — paramètres statiques
# ============================================

from pathlib import Path
import pandas as pd

# Répertoire des données
DATA_DIR = Path("data")

# -----------------------------------------------------------
# Liste des éruptions (fichiers + timestamp de référence)
# -----------------------------------------------------------

eruptions = {
    "24 Aoû 2015 – 16:50 UTC": {
        "file": "2015_08_24_19h_50_UTC_pf_aggregated_1min_1Hz.csv",
        "time": pd.to_datetime("2015-08-24 16:50:00", utc=True)
    },
    "11 Sep 2016 – 04:05 UTC": {
        "file": "2016_09_11_06h_41_UTC_pf_aggregated_1min_1Hz.csv",
        "time": pd.to_datetime("2016-09-11 04:05:00", utc=True)
    },
    "25 Oct 2019 – 12:40 UTC": {
        "file": "2019_10_25_12h_40_UTC_pf_aggregated_1min_1Hz.csv",
        "time": pd.to_datetime("2019-10-25 12:40:00", utc=True)
    },
    "07 Déc 2020 – 00:40 UTC": {
        "file": "2020_12_07_02h_40_UTC_pf_aggregated_1min_1Hz.csv",
        "time": pd.to_datetime("2020-12-07 00:40:00", utc=True)
    },
    "19 Sep 2022 – 06:23 UTC": {
        "file": "2022_09_19_06h_23_UTC_pf_aggregated_1min_1Hz.csv",
        "time": pd.to_datetime("2022-09-19 06:23:00", utc=True)
    },
    "02 Jui 2023 – 04:30 UTC": {
        "file": "2023_07_02_04h_30_UTC_pf_aggregated_1min_1Hz.csv",
        "time": pd.to_datetime("2023-07-02 04:30:00", utc=True)
    }
}

# -----------------------------------------------------------
# Couleurs par éruption (pour les courbes comparées)
# -----------------------------------------------------------

color_map = {
    "24 Aoû 2015 – 16:50 UTC": "#e6194B",
    "11 Sep 2016 – 04:05 UTC": "#f58231",
    "25 Oct 2019 – 12:40 UTC": "#3cb44b",
    "07 Déc 2020 – 00:40 UTC": "#42d4f4",
    "19 Sep 2022 – 06:23 UTC": "#4363d8",
    "02 Jui 2023 – 04:30 UTC": "#911eb4",
}

rgba_map = {
    "#e6194B": "rgba(230,25,75,0.2)",
    "#f58231": "rgba(245,130,49,0.2)",
    "#3cb44b": "rgba(60,180,60,0.2)",
    "#42d4f4": "rgba(66,212,244,0.2)",
    "#4363d8": "rgba(67,99,216,0.2)",
    "#911eb4": "rgba(145,30,180,0.2)"
}

# -----------------------------------------------------------
# Coordonnées des stations OVPF-IPGP
# -----------------------------------------------------------

station_coords = {
    "BON": (-21.280, 55.680), "DSM": (-21.270, 55.690), "DSO": (-21.235, 55.713),
    "ENO": (-21.260, 55.720), "NSR": (-21.250, 55.700), "NTR": (-21.260, 55.695),
    "BLE": (-21.252, 55.715), "CSS": (-21.238, 55.720), "HIM": (-21.225, 55.723),
    "PJR": (-21.263, 55.682), "PCR": (-21.246, 55.702), "PER": (-21.254, 55.692),
    "TKR": (-21.244, 55.708), "SNE": (-21.268, 55.685), "FJS": (-21.275, 55.705),
    "LCR": (-21.245, 55.715), "PRA": (-21.255, 55.705), "PHR": (-21.250, 55.710),
    "RVA": (-21.268, 55.675), "RVP": (-21.272, 55.680), "CRA": (-21.258, 55.698)
}
