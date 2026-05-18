from centromonitoreo_mineria.utils.earth_engine import load_ee


DEFAULT_ADC_SCOPES = [
    "https://www.googleapis.com/auth/earthengine",
    "https://www.googleapis.com/auth/cloud-platform",
]


def initialize_earth_engine_client(params_gee: dict) -> dict:
    ee = load_ee()
    auth_method = params_gee.get("auth_method", "oauth")
    project = params_gee.get("project")

    try:
        if auth_method == "oauth":
            if params_gee.get("authenticate", False):
                auth_mode = params_gee.get("auth_mode")
                ee.Authenticate(auth_mode=auth_mode) if auth_mode else ee.Authenticate()
            credentials = None
            resolved_project = project
        elif auth_method == "service_account":
            credentials = ee.ServiceAccountCredentials(
                params_gee["service_account_email"],
                params_gee["service_account_key_path"],
            )
            resolved_project = project
        elif auth_method == "adc":
            import google.auth

            credentials, adc_project = google.auth.default(
                scopes=params_gee.get("adc_scopes") or DEFAULT_ADC_SCOPES
            )
            resolved_project = project or adc_project
        else:
            raise ValueError("gee.auth_method debe ser oauth, service_account o adc.")

        kwargs = {"project": resolved_project} if resolved_project else {}
        if credentials is not None:
            kwargs["credentials"] = credentials
        ee.Initialize(**kwargs)
    except Exception as exc:
        raise RuntimeError(
            "No se pudo inicializar Google Earth Engine con "
            f"gee.auth_method={auth_method!r}. Revisa la autenticacion y "
            "conf/base/parameters/google_earth_engine/google_earth_engine.yml."
        ) from exc

    return {
        "initialized": True,
        "project": resolved_project,
        "auth_method": auth_method,
        "authenticate": params_gee.get("authenticate", False),
        "auth_mode": params_gee.get("auth_mode"),
        "service_account_email": (
            params_gee.get("service_account_email")
            if auth_method == "service_account"
            else None
        ),
    }
