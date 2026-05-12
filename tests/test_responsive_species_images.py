"""Tests simples para estilos responsive de imágenes."""

from pathlib import Path


def test_species_images_are_responsive() -> None:
    """El CSS debe hacer que las imágenes escalen sin aplastarse."""
    styles_text = Path("src/ui_components/styles.py").read_text(encoding="utf-8")

    assert ".species-image-frame img" in styles_text
    assert "width: 100%" in styles_text
    assert "height: clamp(220px, 24vw, 420px)" in styles_text
    assert "aspect-ratio: 4 / 3" in styles_text
    assert "object-fit: contain" in styles_text
    assert "@media (max-width: 768px)" in styles_text
