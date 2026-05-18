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
python -m venv .env
.\.env\Scripts\Activate.ps1
pip install -r requirements.txt
kedro run
```

## Descarga de Sentinel-2 desde Google Earth Engine

El pipeline `download_sentinel2` queda separado del flujo por defecto para que el
proyecto siga corriendo aunque el usuario no tenga Earth Engine autenticado.

1. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

2. Elegir el metodo de autenticacion en
   `conf/base/parameters/google_earth_engine/google_earth_engine.yml`:

- `gee.auth_method: oauth`: recomendado para desarrollo local. Requiere
  autenticar una vez con navegador.
- `gee.auth_method: service_account`: recomendado para ejecucion reproducible
  sin navegador. Configura `gee.service_account_email` y
  `gee.service_account_key_path` en `conf/local/` o en un archivo no versionado.
- `gee.auth_method: adc`: usa Application Default Credentials, util en Google
  Cloud o con `gcloud`.

3. Para `oauth`, autenticar Earth Engine una vez:

```powershell
earthengine authenticate --auth_mode localhost:0
```

4. Configurar la descarga en
   `conf/base/parameters/google_earth_engine/sentinel2_download.yml`:

- `gee.project`: id del proyecto de Google Cloud con Earth Engine habilitado.
- `sentinel2_download.roi.source`: `bbox`, `inline_geojson` o `geojson_path`.
- `sentinel2_download.roi.bbox`: area rectangular definida con `min_lon`,
  `min_lat`, `max_lon` y `max_lat`.
- `sentinel2_download.drive_export`: carpeta de Drive, prefijo de archivo,
  `max_pixels`, formato y opciones de espera de la tarea. Este pipeline exporta
  siempre a Google Drive.
- `sentinel2_download.start_date` y `sentinel2_download.end_date`.
- `sentinel2_download.bands`, `scale`, `crs`, filtro de nubosidad y metodo de composicion.

5. Ejecutar solo ese pipeline:

```powershell
kedro run --pipeline download_sentinel2
```

Las credenciales y llaves JSON no deben subirse al repositorio. Usa
`conf/local/` o rutas fuera del proyecto para datos sensibles.

Kedro inicia una tarea de Earth Engine y la imagen queda en la carpeta
configurada de Google Drive cuando la tarea termina. Los metadatos de la
descarga/exportacion quedan en
`data/08_reporting/sentinel2_download_metadata.json`.

Nota: este flujo usa Google Drive porque los ROIs reales superan con facilidad
los limites de descarga directa de Earth Engine.

## Siguientes pasos

1. Ajustar rutas y catologo en `conf/base/catalog.yml`
2. Cargar datos reales en `data/01_raw`
3. Completar nodos placeholder en `src/centromonitoreo_mineria/pipelines`
4. Agregar pruebas unitarias y de integracion
