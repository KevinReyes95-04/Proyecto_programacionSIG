import pandas as pd


def harmonize_sources(raw_data: dict) -> pd.DataFrame:
    """Lee muestras CSV de ambos sensores y las concatena con columnas compatibles."""
    sentinel_samples = pd.read_csv(raw_data["sentinel_samples_path"])
    planetscope_samples = pd.read_csv(raw_data["planetscope_samples_path"])
    sentinel_samples["sensor"] = "sentinel2"
    planetscope_samples["sensor"] = "planetscope"
    return pd.concat([sentinel_samples, planetscope_samples], ignore_index=True)
