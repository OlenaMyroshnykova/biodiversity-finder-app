"""Tests para iconos reales de banderas."""

from src.ui import (
    ARTIFACTS_URL,
    LANGUAGE_FLAGS,
    MODEL_DASHBOARD_URL,
    get_language_flags_html,
    get_supported_languages_accessible_text,
)


def test_language_flags_use_png_images_not_emoji_letters() -> None:
    """Debe usar imágenes PNG de banderas."""
    html = get_language_flags_html()

    assert "flagcdn.com" in html
    assert "<img" in html
    assert "w80/es.png" in html
    assert "w80/gb.png" in html
    assert "w80/ua.png" in html
    assert "w80/pt.png" in html
    assert "w80/it.png" in html
    assert "w80/ru.png" in html


def test_accessible_language_text_is_available() -> None:
    """Debe mantener texto accesible con nombres de idiomas."""
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
