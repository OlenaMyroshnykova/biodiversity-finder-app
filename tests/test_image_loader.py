"""Tests para extracción de imágenes de GBIF."""

from src.image_loader import extract_image_url_from_occurrence, is_image_url


def test_is_image_url_accepts_jpg_url() -> None:
    """
    Debe aceptar una URL de imagen válida.
    """
    assert is_image_url("https://example.com/photo.jpg")


def test_is_image_url_rejects_non_image_url() -> None:
    """
    Debe rechazar URL sin extensión de imagen.
    """
    assert not is_image_url("https://example.com/page")


def test_extract_image_url_from_media_identifier() -> None:
    """
    Debe extraer imagen desde media.identifier.
    """
    record = {
        "media": [
            {
                "identifier": "https://example.com/species.jpeg",
            }
        ]
    }

    assert extract_image_url_from_occurrence(record) == "https://example.com/species.jpeg"
