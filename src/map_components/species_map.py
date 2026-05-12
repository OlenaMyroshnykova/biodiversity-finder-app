"""Mapa Folium de avistamientos por especie."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_species_occurrence_map(
    occurrence_points_df: pd.DataFrame,
    selected_species_name: str,
) -> None:
    """Muestra un mapa dinámico con coordenadas de la especie seleccionada."""
    if occurrence_points_df.empty:
        st.info("No hay puntos de avistamiento disponibles para el mapa.")
        return

    if not selected_species_name:
        st.info("Selecciona una especie para ver sus avistamientos en el mapa.")
        return

    species_points_df = filter_points_for_species(
        occurrence_points_df,
        selected_species_name,
    )

    if species_points_df.empty:
        st.info("No hay coordenadas disponibles para esta especie.")
        return

    try:
        import folium
        from streamlit_folium import st_folium
    except ImportError:
        st.warning(
            "Para ver el mapa instala folium y streamlit-folium: "
            "`pip install folium streamlit-folium`"
        )
        return

    center_latitude = float(species_points_df["decimalLatitude"].mean())
    center_longitude = float(species_points_df["decimalLongitude"].mean())

    species_map = folium.Map(
        location=[center_latitude, center_longitude],
        zoom_start=3,
        control_scale=True,
    )

    for _, row in species_points_df.head(250).iterrows():
        popup_text = build_popup_text(row)

        folium.CircleMarker(
            location=[
                float(row["decimalLatitude"]),
                float(row["decimalLongitude"]),
            ],
            radius=4,
            popup=popup_text,
            fill=True,
        ).add_to(species_map)

    st_folium(species_map, width=None, height=520)


def filter_points_for_species(
    occurrence_points_df: pd.DataFrame,
    selected_species_name: str,
) -> pd.DataFrame:
    """Filtra puntos por nombre científico o canónico."""
    selected = str(selected_species_name).strip()

    if not selected:
        return occurrence_points_df.iloc[0:0].copy()

    mask = pd.Series(False, index=occurrence_points_df.index)

    for column in ["scientific_name", "canonical_scientific_name"]:
        if column in occurrence_points_df.columns:
            mask |= occurrence_points_df[column].fillna("").astype(str).eq(selected)

    if "canonical_scientific_name" in occurrence_points_df.columns:
        canonical_selected = selected.split("(")[0].strip()
        mask |= (
            occurrence_points_df["canonical_scientific_name"]
            .fillna("")
            .astype(str)
            .eq(canonical_selected)
        )

    return occurrence_points_df.loc[mask].copy()


def build_popup_text(row: pd.Series) -> str:
    """Texto del popup del mapa."""
    country = str(row.get("countryCode", "Unknown"))
    event_date = str(row.get("eventDate", "Unknown date"))
    name = str(row.get("scientific_name", "Unknown species"))

    return f"{name}<br>Country: {country}<br>Date: {event_date}"
