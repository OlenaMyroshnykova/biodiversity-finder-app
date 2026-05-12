"""Tests simples para verificar que los estilos de imagen existen."""

from pathlib import Path


def test_species_image_css_uses_stable_aspect_ratio() -> None:
    """El CSS debe evitar imágenes panorámicas aplastadas."""
    styles_path = Path("src/ui_components/styles.py")
    styles_text = styles_path.read_text(encoding="utf-8")

    assert ".species-image-frame" in styles_text
    assert "max-width: 360px" in styles_text
    assert "aspect-ratio: 4 / 3" in styles_text
    assert "object-fit: contain" in styles_text
