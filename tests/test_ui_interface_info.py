"""Tests para textos informativos de la interfaz."""

from src.ui import (
    ARTIFACTS_URL,
    MODEL_ADEQUACY_URL,
    SEARCH_MODEL_DESCRIPTION,
    SUPPORTED_SEARCH_LANGUAGES,
    get_supported_languages_text,
)


def test_supported_languages_include_required_languages() -> None:
    """La interfaz debe mostrar idiomas requeridos."""
    languages_text = get_supported_languages_text()

    assert "Español" in languages_text
    assert "English" in languages_text
    assert "Українська" in languages_text
    assert "Português" in languages_text
    assert "Italiano" in languages_text
    assert "Русский" in languages_text


def test_search_model_description_is_explicit() -> None:
    """La descripción debe explicar el tipo de búsqueda."""
    assert "TF-IDF" in SEARCH_MODEL_DESCRIPTION
    assert "sinónimos" in SEARCH_MODEL_DESCRIPTION
    assert "taxonómicos" in SEARCH_MODEL_DESCRIPTION


def test_model_links_point_to_hugging_face() -> None:
    """Los enlaces deben apuntar a Hugging Face."""
    assert MODEL_ADEQUACY_URL.startswith("https://huggingface.co/datasets/")
    assert ARTIFACTS_URL.startswith("https://huggingface.co/datasets/")


def test_supported_languages_list_is_not_empty() -> None:
    """La lista de idiomas no debe estar vacía."""
    assert len(SUPPORTED_SEARCH_LANGUAGES) >= 6
