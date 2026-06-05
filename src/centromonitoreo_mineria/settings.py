"""Kedro project settings"""
import os
from importlib.util import find_spec
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=env_path)

rasterio_spec = find_spec("rasterio")
if rasterio_spec and rasterio_spec.origin:
    rasterio_proj_data = Path(rasterio_spec.origin).parent / "proj_data"
    if rasterio_proj_data.exists():
        os.environ["PROJ_LIB"] = str(rasterio_proj_data)
        os.environ["PROJ_DATA"] = str(rasterio_proj_data)
