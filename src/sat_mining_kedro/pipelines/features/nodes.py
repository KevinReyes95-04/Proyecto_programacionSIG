import pandas as pd


def build_spectral_features(harmonized_samples: pd.DataFrame) -> pd.DataFrame:
    """Crea variables espectrales basicas de ejemplo."""
    df = harmonized_samples.copy()
    if {"nir", "red"}.issubset(df.columns):
        df["ndvi"] = (df["nir"] - df["red"]) / (df["nir"] + df["red"] + 1e-6)
    if {"nir", "swir"}.issubset(df.columns):
        df["nbr"] = (df["nir"] - df["swir"]) / (df["nir"] + df["swir"] + 1e-6)
    return df
