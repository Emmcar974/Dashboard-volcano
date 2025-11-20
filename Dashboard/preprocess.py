# ============================================
# preprocess_seismic.py
# Pipeline propre & ML-ready
# ============================================

import numpy as np
import pandas as pd
from scipy.signal import welch
from typing import List, Optional

# --------------------------------------------
# SECTION 1 — FONCTIONS DE BASE
# --------------------------------------------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage basique : doublons, timestamps, NA."""
    data = df.copy()
    
    data.drop_duplicates(inplace=True)
    data.dropna(how="all", inplace=True)

    if "time_min" in data.columns:
        data["time_min"] = pd.to_datetime(data["time_min"], errors="coerce", utc=True)
    
    return data


def enforce_numeric(data: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Convertit les colonnes en numérique."""
    for col in cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data


# --------------------------------------------
# SECTION 2 — STATISTIQUES SISMOMÉTRIQUES
# --------------------------------------------

def compute_rsam(data: pd.DataFrame) -> pd.DataFrame:
    """RSAM = moyenne glissante amplitude_mean."""
    if "amplitude_mean" in data.columns:
        data["RSAM"] = data["amplitude_mean"].rolling(10, min_periods=3).mean()
    return data


def compute_percentiles(data: pd.DataFrame) -> pd.DataFrame:
    """Rolling percentiles P10 et P90."""
    if "amplitude_mean" in data.columns:
        data["per10"] = data["amplitude_mean"].rolling(20, min_periods=5).quantile(0.10)
        data["per90"] = data["amplitude_mean"].rolling(20, min_periods=5).quantile(0.90)
    return data


def compute_kurtosis(data: pd.DataFrame) -> pd.DataFrame:
    """Kurtosis glissante simplifiée."""
    if "amplitude_mean" in data.columns:
        roll = data["amplitude_mean"].rolling(20, min_periods=5)
        data["Kurtosis"] = ((data["amplitude_mean"] - roll.mean()) ** 4).rolling(20).mean()
    return data


def compute_frequency_index(data: pd.DataFrame) -> pd.DataFrame:
    """Gradient de l'amplitude = proxy fréquence."""
    if "amplitude_mean" in data.columns:
        data["FI"] = np.gradient(data["amplitude_mean"].fillna(0))
    return data


# --------------------------------------------
# SECTION 3 — ENTROPIE SPECTRALE RÉALISTE
# --------------------------------------------

def compute_spectral_entropy(data: pd.DataFrame, fs: float = 1/60) -> pd.DataFrame:
    """
    Entropie spectrale via Welch :
    fs = 1/60 = 1 point par minute
    """
    if "amplitude_mean" not in data.columns:
        return data
    
    x = data["amplitude_mean"].fillna(method='ffill').values
    
    # Spectre via Welch
    f, Pxx = welch(x, fs=fs, nperseg=256)

    # Distribution normalisée
    p = Pxx / (np.sum(Pxx) + 1e-12)
    entropy = -np.sum(p * np.log2(p + 1e-12))

    # Même entropie pour toutes les lignes (proxy global)
    data["SE"] = entropy  
    return data


# --------------------------------------------
# SECTION 4 — ENVELOPPE LISSÉE
# --------------------------------------------

def smooth_envelopes(data: pd.DataFrame) -> pd.DataFrame:
    """Enveloppes lissées des stats avancées."""
    for col in ["SE", "FI", "Kurtosis"]:
        if col in data.columns:
            data[f"{col}_env"] = data[col].rolling(15, min_periods=5).mean()
    return data


# --------------------------------------------
# SECTION 5 — NORMALISATION (OPTION ML)
# --------------------------------------------

def normalize_features(
    data: pd.DataFrame,
    feature_cols: List[str],
    mode: str = "inference",
    stats: Optional[dict] = None
):
    """
    Normalisation standard :
    mode = "train" : calcule et renvoie les stats
    mode = "inference" : applique les stats fournies
    """
    data = data.copy()

    if mode == "train":
        stats = {}
        for col in feature_cols:
            mean = data[col].mean()
            std = data[col].std() + 1e-9
            stats[col] = {"mean": mean, "std": std}
            data[col] = (data[col] - mean) / std
        return data, stats

    elif mode == "inference":
        if stats is None:
            raise ValueError("Stats must be provided in inference mode.")

        for col in feature_cols:
            mean = stats[col]["mean"]
            std = stats[col]["std"]
            data[col] = (data[col] - mean) / std
        return data


# --------------------------------------------
# SECTION 6 — SÉQUENCES ML (Transformer-ready)
# --------------------------------------------

def make_sequence(
    df: pd.DataFrame,
    features: List[str],
    seq_len: int = 480
):
    """
    Transforme un dataframe en séquence ML :
    - padding automatique si data < seq_len
    - format (1, seq_len, nb_features)
    """
    seq = df[features].tail(seq_len).values

    # Padding en haut
    if len(seq) < seq_len:
        pad = np.zeros((seq_len - len(seq), len(features)))
        seq = np.vstack([pad, seq])

    return seq.reshape(1, seq_len, len(features))


# --------------------------------------------
# SECTION 7 — PIPELINE PRINCIPAL (Dashboard)
# --------------------------------------------

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline complet pour le dashboard (pas ML)."""
    
    data = clean_dataframe(df)

    data = enforce_numeric(data, [
        "amplitude_mean", "amplitude_std", "amplitude_max",
        "amplitude_min", "amplitude_count"
    ])
    
    data = compute_rsam(data)
    data = compute_percentiles(data)
    data = compute_frequency_index(data)
    data = compute_kurtosis(data)
    
    # Entropie spectrale simplifiée (optimale pour dashboard)
    data = compute_spectral_entropy(data)

    data = smooth_envelopes(data)

    data["label"] = 0  # placeholder ML

    data.reset_index(drop=True, inplace=True)
    return data
