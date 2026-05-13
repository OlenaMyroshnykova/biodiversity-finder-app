"""Configuración de UI.

The app does not show flags and does not promise broad multilingual search. The
stable demo search supports Spanish and English.
"""

SUPPORTED_SEARCH_LANGUAGES = ["Español", "English"]

SEARCH_MODEL_DESCRIPTION = (
    "Búsqueda estructurada: primero traduce lenguaje natural a filtros df.loc "
    "(tamaño, hábitat, color, grupo) y solo después usa búsqueda textual "
    "por nombre científico o nombre común en español/inglés. Los nombres "
    "comunes de otros idiomas pueden aparecer en las fichas, pero no deciden "
    "los filtros del vibe-search principal."
)

MODEL_DASHBOARD_URL = "https://biodiversity-finder-training.streamlit.app/"
ARTIFACTS_URL = "https://huggingface.co/datasets/selenamir/biodiversity-finder-artifacts"


def get_supported_languages_text() -> str:
    """Return the languages promised by the demo search."""

    return ", ".join(SUPPORTED_SEARCH_LANGUAGES)
