"""Configuración de UI."""

LANGUAGE_FLAGS = [
    {"code": "es", "label": "Español",    "image_url": "https://flagcdn.com/w80/es.png"},
    {"code": "gb", "label": "English",    "image_url": "https://flagcdn.com/w80/gb.png"},
    {"code": "ua", "label": "Українська", "image_url": "https://flagcdn.com/w80/ua.png"},
    {"code": "pt", "label": "Português",  "image_url": "https://flagcdn.com/w80/pt.png"},
    {"code": "it", "label": "Italiano",   "image_url": "https://flagcdn.com/w80/it.png"},
    {"code": "ru", "label": "Русский",    "image_url": "https://flagcdn.com/w80/ru.png"},
]

SEARCH_MODEL_DESCRIPTION = (
    "Búsqueda combinada: traducción de lenguaje natural a filtros df.loc "
    "(tamaño, hábitat, color, grupo) + TF-IDF por palabras y caracteres "
    "sobre nombres comunes, taxonomía y etiquetas de búsqueda. "
    "Cubre mamíferos, aves, reptiles, peces, anfibios, insectos, "
    "arácnidos, plantas y hongos."
)

MODEL_DASHBOARD_URL = "https://biodiversity-finder-training.streamlit.app/"
ARTIFACTS_URL = "https://huggingface.co/datasets/selenamir/biodiversity-finder-artifacts"


def get_supported_languages_text() -> str:
    """Devuelve nombres de idiomas."""
    return ", ".join(language["label"] for language in LANGUAGE_FLAGS)
