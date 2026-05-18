from typing import Any


def load_ee() -> Any:
    try:
        import ee
    except ImportError as exc:
        raise ImportError(
            "Falta earthengine-api. Instala dependencias con "
            "`pip install -r requirements.txt`."
        ) from exc

    return ee
