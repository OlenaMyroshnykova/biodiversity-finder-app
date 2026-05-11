"""Tests para banderas seguras sin HTML."""

from src.ui import (
    ARTIFACTS_URL,
    LANGUAGE_FLAGS,
    MODEL_DASHBOARD_URL,
    get_language_flag_urls,
    get_supported_languages_accessible_text,
)


def test_language_flags_are_real_image_urls() -> None:
    """Debe usar URLs de imágenes PNG."""
    urls = get_language_flag_urls()

    assert "https://flagcdn.com/w80/es.png" in urls
    assert "https://flagcdn.com/w80/gb.png" in urls
    assert "https://flagcdn.com/w80/ua.png" in urls
    assert "https://flagcdn.com/w80/pt.png" in urls
    assert "https://flagcdn.com/w80/it.png" in urls
    assert "https://flagcdn.com/w80/ru.png" in urls


def test_accessible_language_text_is_available() -> None:
    """Debe mantener nombres de idiomas."""
    text = get_supported_languages_accessible_text()

    assert "Español" in text
    assert "English" in text
    assert "Українська" in text
    assert "Português" in text
    assert "Italiano" in text
    assert "Русский" in text


def test_model_dashboard_url_points_to_streamlit_dashboard() -> None:
    """El enlace principal debe apuntar al dashboard de training."""
    assert MODEL_DASHBOARD_URL == "https://biodiversity-finder-training.streamlit.app/"


def test_artifacts_url_is_still_available() -> None:
    """El enlace a Hugging Face debe seguir disponible."""
    assert ARTIFACTS_URL.startswith("https://huggingface.co/datasets/")


def test_language_flags_list_has_six_items() -> None:
    """Debe haber seis idiomas."""
    assert len(LANGUAGE_FLAGS) == 6
