"""Configuración de UI."""

LANGUAGE_FLAGS = [
    {"code": "es", "label": "Español", "image_url": "https://flagcdn.com/w80/es.png"},
    {"code": "gb", "label": "English", "image_url": "https://flagcdn.com/w80/gb.png"},
    {"code": "ua", "label": "Українська", "image_url": "https://flagcdn.com/w80/ua.png"},
    {"code": "pt", "label": "Português", "image_url": "https://flagcdn.com/w80/pt.png"},
    {"code": "it", "label": "Italiano", "image_url": "https://flagcdn.com/w80/it.png"},
    {"code": "ru", "label": "Русский", "image_url": "https://flagcdn.com/w80/ru.png"},
]

SEARCH_MODEL_DESCRIPTION = (
    "Búsqueda genérica sobre la enciclopedia: TF-IDF por palabras + "
    "TF-IDF por caracteres + nombres comunes de GBIF + taxonomía. "
    "Sin reglas específicas por animal."
)

MODEL_DASHBOARD_URL = "https://biodiversity-finder-training.streamlit.app/"
ARTIFACTS_URL = "https://huggingface.co/datasets/selenamir/biodiversity-finder-artifacts"


def get_supported_languages_text() -> str:
    """Devuelve nombres de idiomas."""
    return ", ".join(language["label"] for language in LANGUAGE_FLAGS)
