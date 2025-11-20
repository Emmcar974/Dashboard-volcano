# ============================================
# data_loader.py — chargement + preprocessing
# ============================================

import pandas as pd
from pathlib import Path
from preprocess import preprocess_data
from constants import DATA_DIR, eruptions

# -----------------------------------------------------------
# Chargement d’un fichier d’éruption + preprocessing complet
# -----------------------------------------------------------

def load_eruption_file(eruption_name: str) -> pd.DataFrame:
    """
    Charge et prétraite le fichier d'une éruption choisie.
    """
    info = eruptions[eruption_name]
    path = DATA_DIR / info["file"]

    df = pd.read_csv(path)
    df = preprocess_data(df)

    return df


# -----------------------------------------------------------
# Chargement brut sans preprocessing (utile pour spectrogramme)
# -----------------------------------------------------------

def load_raw_file(eruption_name: str) -> pd.DataFrame:
    info = eruptions[eruption_name]
    path = DATA_DIR / info["file"]

    df = pd.read_csv(path)
    df["time_min"] = pd.to_datetime(df["time_min"], utc=True)

    return df


# -----------------------------------------------------------
# Extraction d’une fenêtre temporelle relative à l’éruption
# -----------------------------------------------------------

def load_window(eruption_name: str, hours_before=48, hours_after=12):
    df = load_raw_file(eruption_name)
    erupt_time = eruptions[eruption_name]["time"]

    start = erupt_time - pd.Timedelta(hours=hours_before)
    end = erupt_time + pd.Timedelta(hours=hours_after)

    return df[(df["time_min"] >= start) & (df["time_min"] <= end)]
