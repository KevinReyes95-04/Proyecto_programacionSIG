# Identificación de Mineria

Proyecto reproducible para identificar zonas asociadas a mineria de oro de
aluvion usando imagenes Sentinel-2, indices espectrales y modelos Random
Forest. El flujo esta implementado con Kedro para separar cada etapa en
pipelines, nodos, parametros y catalogos de datos.

El proyecto incluye dos enfoques:

- Clasificacion binaria: `Mineria` vs `No Mineria`.
- Clasificacion multiclase: `Bosque Natural`, `Cuerpos de Agua`, `Mineria`,
  `Nubes`, `Suelo Desnudo` y `Vegetacion`.

## Contenido principal

```text
conf/
  base/
    catalog/        # Entradas y salidas declaradas para Kedro
    parameters/     # Parametros de GEE, Sentinel-2, modelos y mapas
data/
  01_raw/           # Insumos fuente
  04_feature/       # Bandas Sentinel-2 e indices generados
  05_model_input/   # Tablas para entrenamiento y prueba
  06_models/        # Modelos entrenados
  07_model_output/  # Mapas raster, CSV y vectores derivados
  08_reporting/     # Figuras, metricas y metadatos
docs/
  proyecto_final.qmd
src/
  centromonitoreo_mineria/
    pipeline_registry.py
    pipelines/
tests/
```

## Instalacion

El proyecto fue trabajado con Python `>=3.12,<3.13`.

En Windows PowerShell:

```powershell
python -m venv .env
.\.env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En Linux o entorno Docker:

```bash
python -m venv .env
source .env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En Linux, paquetes como `rasterio`, `geopandas` y `pyproj` pueden requerir
dependencias de sistema asociadas a GDAL, PROJ y GEOS si la imagen base no trae
ruedas binarias compatibles.

## Autenticacion de Google Earth Engine

Los primeros pipelines consultan datos desde Google Earth Engine. Para
usar autenticacion local por navegador:

```powershell
earthengine authenticate --auth_mode localhost:0
```

Luego revisar:

```text
conf/base/parameters/google_earth_engine/google_earth_engine.yml
conf/base/parameters/google_earth_engine/sentinel2_download.yml
conf/base/parameters/google_earth_engine/sentinel2_spectral_indices.yml
```

Las credenciales personales, llaves JSON y configuraciones sensibles deben
quedar fuera de Git, preferiblemente en `conf/local/`.

## Orden de ejecucion de pipelines

Ejecutar desde la raiz del repositorio:

```powershell
kedro run --pipeline download_sentinel2
kedro run --pipeline build_topographic_features
kedro run --pipeline sentinel2_spectral_indices
kedro run --pipeline prepare_training_data
kedro run --pipeline extract_sentinel2_training_features
kedro run --pipeline train_mining_binary_rf
kedro run --pipeline predict_mining_binary_map
kedro run --pipeline validate_mining_binary_map
kedro run --pipeline postprocess_mining_binary_map
kedro run --pipeline validate_postprocessed_mining_map
kedro run --pipeline train_mining_multiclass_rf
kedro run --pipeline predict_mining_multiclass_map
kedro run --pipeline validate_mining_multiclass_map
kedro run --pipeline postprocess_mining_multiclass_map
kedro run --pipeline validate_postprocessed_mining_multiclass_map
```

Si no se activa el entorno virtual, tambien se puede usar:

```powershell
.\.env\Scripts\python.exe -m kedro run --pipeline download_sentinel2
```

## Salidas principales

Las salidas generadas se organizan por carpeta dentro de `data/08_reporting`:

| Carpeta | Contenido |
|---|---|
| `sentinel2_download_visualizations` | RGB, falso color y grilla de bandas |
| `topographic_features` | Metadatos de DEM y pendiente alineados a Sentinel-2 |
| `sentinel2_spectral_indices_maps` | Mapas de indices espectrales |
| `prepare_training_data` | Distribucion espacial y por clase de puntos |
| `extract_sentinel2_training_features` | Metadatos de extraccion |
| `train_mining_binary_rf` | Metricas, matriz e importancia binaria |
| `predict_mining_binary_map` | Mapas binarios |
| `validate_mining_binary_map` | Mapas de probabilidad y errores |
| `postprocess_mining_binary_map` | Mapa binario postprocesado |
| `validate_postprocessed_mining_map` | Validacion final binaria |
| `train_mining_multiclass_rf` | Metricas, matriz e importancia multiclase |
| `predict_mining_multiclass_map` | Mapa multiclase |
| `validate_mining_multiclass_map` | Matriz y mapa de validacion multiclase |
| `postprocess_mining_multiclass_map` | Mapa multiclase filtrado |
| `validate_postprocessed_mining_multiclass_map` | Validacion final multiclase |

Los GeoTIFF y salidas pesadas se regeneran al correr los pipelines y estan
excluidos del repositorio mediante `.gitignore`.

## Informe final

El informe esta en:

```text
docs/proyecto_final.qmd
```

Renderizar HTML:

```powershell
quarto render docs\proyecto_final.qmd --to html
```

Renderizar PDF:

```powershell
quarto render docs\proyecto_final.qmd --to pdf
```

El HTML generado queda ignorado por Git para evitar subir archivos pesados:

```text
docs/proyecto_final.html
```

## Pruebas

Para verificar que los pipelines y funciones principales siguen consistentes:

```powershell
pytest
```

La ultima verificacion local reporto:

```text
47 passed, 1 warning
```

## Integracion continua

El repositorio incluye un workflow de GitHub Actions en:

```text
.github/workflows/ci.yml
```

Este workflow se ejecuta en `push`, `pull_request` y manualmente desde
`workflow_dispatch`. La accion instala Python 3.12, carga las dependencias de
`requirements.txt` y ejecuta:

```bash
python -m pytest
```

## Notas de reproducibilidad

- El codigo vive en `src/centromonitoreo_mineria`.
- Los parametros reproducibles viven en `conf/base/parameters`.
- Las entradas y salidas Kedro viven en `conf/base/catalog`.
- Las salidas de datos pesadas no se suben a Git.
- Las credenciales de Google Earth Engine y Drive no deben versionarse.
- Para inspeccionar el grafo visualmente se puede usar `kedro viz`.
