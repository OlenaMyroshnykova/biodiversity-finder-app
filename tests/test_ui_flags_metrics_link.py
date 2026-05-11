"""Tests para interfaz con banderas y enlace a métricas."""

from src.ui import (
    ARTIFACTS_URL,
    LANGUAGE_FLAGS,
    MODEL_DASHBOARD_URL,
    get_language_flags_text,
    get_supported_languages_accessible_text,
)


def test_language_flags_are_visible() -> None:
    """Debe mostrar idiomas con banderas."""
    flags_text = get_language_flags_text()

    assert "🇪🇸" in flags_text
    assert "🇬🇧" in flags_text
    assert "🇺🇦" in flags_text
    assert "🇵🇹" in flags_text
    assert "🇮🇹" in flags_text
    assert "🇷🇺" in flags_text


def test_accessible_language_text_is_available() -> None:
    """Debe mantener texto accesible con nombres de idiomas."""
    text = get_supported_languages_accessible_text()

    assert "Español" in text
    assert "Українська" in text
    assert "Português" in text
    assert "Italiano" in text


def test_model_dashboard_url_points_to_streamlit_dashboard() -> None:
    """El enlace principal debe apuntar al dashboard de training."""
    assert MODEL_DASHBOARD_URL == "https://biodiversity-finder-training.streamlit.app/"


def test_artifacts_url_is_still_available() -> None:
    """El enlace a Hugging Face debe seguir disponible."""
    assert ARTIFACTS_URL.startswith("https://huggingface.co/datasets/")


def test_flags_list_has_six_languages() -> None:
    """Debe haber seis banderas."""
    assert len(LANGUAGE_FLAGS) == 6
