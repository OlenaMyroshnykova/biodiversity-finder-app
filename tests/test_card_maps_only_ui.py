"""Tests para simplificación de UI: mapas solo dentro de tarjetas."""

from pathlib import Path


def test_app_removes_top_map_tab() -> None:
    """La app no debe tener pestaña superior de mapa combinado."""
    app_text = Path("app.py").read_text(encoding="utf-8")

    assert "Mapa combinado" not in app_text
    assert "render_results_occurrence_map" not in app_text
    assert "render_species_cards(" in app_text
    assert "occurrence_points_df=occurrence_points_df" in app_text


def test_sidebar_removes_species_map_selector() -> None:
    """El sidebar no debe pedir especie para mapa Folium."""
    sidebar_text = Path("src/ui_components/sidebar.py").read_text(encoding="utf-8")

    assert "Especie para mapa Folium" not in sidebar_text
    assert "Los mapas están dentro de cada tarjeta" in sidebar_text
