import pandas as pd
import numpy as np

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing pipeline for seismic data used in the Piton de la Fournaise dashboard.
    This version does NOT save CSV files; it only returns an enriched DataFrame.

    Parameters:
        df (pd.DataFrame): Raw dataframe loaded from the original CSV.

    Returns:
        pd.DataFrame: Processed dataframe with multiple new seismic features.
    """

    # -------------------------------------------------------------
    # 1. Copy to avoid modifying the original dataframe
    # -------------------------------------------------------------
    data = df.copy()

    # -------------------------------------------------------------
    # 2. Basic cleaning
    # -------------------------------------------------------------
    data.drop_duplicates(inplace=True)
    data.dropna(how="all", inplace=True)

    # Standardize timestamps
    if "time_min" in data.columns:
        data["time_min"] = pd.to_datetime(data["time_min"], errors="coerce")

    # -------------------------------------------------------------
    # 3. Core seismic metrics
    # -------------------------------------------------------------
    # Convert to numeric safely
    numeric_cols = ["amplitude_mean", "amplitude_std", "amplitude_max",
                    "amplitude_min", "amplitude_count"]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # Rolling seismic amplitude measurement (RSAM)
    if "amplitude_mean" in data.columns:
        data["RSAM"] = data["amplitude_mean"].rolling(10, min_periods=3).mean()

    # Standard deviation & mean (for convenience)
    if "amplitude_std" in data.columns:
        data["std"] = data["amplitude_std"]

    if "amplitude_mean" in data.columns:
        data["mean"] = data["amplitude_mean"]

    # Percentiles 10 and 90
    if "amplitude_mean" in data.columns:
        data["per10"] = data["amplitude_mean"].rolling(20, min_periods=5).quantile(0.10)
        data["per90"] = data["amplitude_mean"].rolling(20, min_periods=5).quantile(0.90)

    # -------------------------------------------------------------
    # 4. Higher-order statistics (SE, FI, Kurtosis)
    # -------------------------------------------------------------
    # Spectral Entropy (SE)
    if "amplitude_mean" in data.columns:
        x = data["amplitude_mean"].fillna(0)
        p = x / (x.sum() + 1e-9)
        data["SE"] = -p * np.log2(p + 1e-12)

    # Frequency Index (FI)
    if "amplitude_mean" in data.columns:
        data["FI"] = np.gradient(data["amplitude_mean"].fillna(0))

    # Kurtosis
    if "amplitude_mean" in data.columns:
        data["Kurtosis"] = (
            (data["amplitude_mean"] - data["amplitude_mean"].rolling(20).mean())**4
        ).rolling(20, min_periods=5).mean()

    # -------------------------------------------------------------
    # 5. Geophysical stress proxy (tension)
    # -------------------------------------------------------------
    if "amplitude_mean" in data.columns:
        data["tension"] = np.sqrt(data["amplitude_mean"].fillna(0)) * data["per90"].fillna(0)

    # -------------------------------------------------------------
    # 6. Smoothed “envelope” versions of SE / FI / Kurtosis
    # -------------------------------------------------------------
    data["SE_env"] = data["SE"].rolling(15, min_periods=5).mean()
    data["FI_env"] = data["FI"].rolling(15, min_periods=5).mean()
    data["Kurt_env"] = data["Kurtosis"].rolling(15, min_periods=5).mean()

    # -------------------------------------------------------------
    # 7. Optional label (for ML / classification)
    # -------------------------------------------------------------
    data["label"] = 0  # Placeholder – kept for ML compatibility

    # Final cleanup
    data.reset_index(drop=True, inplace=True)

    return data
