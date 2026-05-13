"""Configuración de UI.

La app ya no muestra banderas ni promete soporte multilingüe amplio.
El buscador de demo se mantiene estable con español e inglés.
"""

SUPPORTED_SEARCH_LANGUAGES = ["Español", "English"]

SEARCH_MODEL_DESCRIPTION = (
    "Búsqueda estructurada: primero traduce lenguaje natural a filtros df.loc "
    "(tamaño, hábitat, color, grupo) y solo después usa búsqueda textual "
    "por nombre científico o nombre común en español/inglés. "
    "Los nombres comunes de otros idiomas pueden mostrarse en las fichas, "
    "pero no participan en el vibe-search principal."
)

MODEL_DASHBOARD_URL = "https://biodiversity-finder-training.streamlit.app/"
ARTIFACTS_URL = "https://huggingface.co/datasets/selenamir/biodiversity-finder-artifacts"


def get_supported_languages_text() -> str:
    """Devuelve los idiomas realmente soportados por el buscador de demo."""
    return ", ".join(SUPPORTED_SEARCH_LANGUAGES)
