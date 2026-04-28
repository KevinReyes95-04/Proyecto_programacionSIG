# sat-mining-kedro

Proyecto de clasificacion de imagenes satelitales (Sentinel-2 y PlanetScope) para:

- Mineria vs no mineria (binario)
- Coberturas de suelo (multiclase)

## Stack

- Kedro
- Random Forest (scikit-learn)
- Geoespacial: rasterio, geopandas, rioxarray, xarray

## Estructura de pipelines

- `data_engineering`: ingesta, limpieza, armonizacion de sensores
- `features`: construccion de variables espectrales y texturales
- `train_binary_rf`: entrenamiento mineria/no mineria
- `train_multiclass_rf`: entrenamiento coberturas de suelo
- `evaluate`: metricas y analisis de errores
- `predict`: inferencia y salida para mapas

## Configuracion inicial (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
kedro run
```

## Siguientes pasos

1. Ajustar rutas y catologo en `conf/base/catalog.yml`
2. Cargar datos reales en `data/01_raw`
3. Completar nodos placeholder en `src/sat_mining_kedro/pipelines`
4. Agregar pruebas unitarias y de integracion
