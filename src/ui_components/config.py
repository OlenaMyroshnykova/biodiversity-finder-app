"""Configuración de UI."""

SUPPORTED_SEARCH_LANGUAGES = ["Español", "English"]

SEARCH_MODEL_DESCRIPTION = (
    "Búsqueda estructurada: la frase del usuario se traduce primero a filtros "
    "df.loc de tamaño, hábitat, color y grupo. Después, solo como apoyo, "
    "se usa búsqueda textual sobre nombres científicos y nombres comunes."
)
MODEL_DASHBOARD_URL = "https://biodiversity-finder-training.streamlit.app/"
ARTIFACTS_URL = "https://huggingface.co/datasets/selenamir/biodiversity-finder-artifacts"


def get_supported_languages_text() -> str:
    """Devuelve nombres de idiomas soportados por el vibe-search estable."""
    return ", ".join(SUPPORTED_SEARCH_LANGUAGES)
