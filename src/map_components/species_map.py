"""Mapa Folium de avistamientos por especie."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_species_occurrence_map(
    occurrence_points_df: pd.DataFrame,
    selected_species_name: str,
    *,
    height: int = 420,
    max_points: int = 250,
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

    for _, row in species_points_df.head(max_points).iterrows():
        popup_text = build_popup_text(row)

        folium.CircleMarker(
            location=[
                float(row["decimalLatitude"]),
                float(row["decimalLongitude"]),
            ],
            radius=5,
            popup=popup_text,
            fill=True,
        ).add_to(species_map)

    st.caption(
        f"Mostrando {min(len(species_points_df), max_points)} "
        f"de {len(species_points_df)} puntos disponibles para esta especie."
    )

    st_folium(
        species_map,
        width=None,
        height=height,
        key=build_map_key(selected_species_name),
    )


def render_results_occurrence_map(
    occurrence_points_df: pd.DataFrame,
    result_df: pd.DataFrame,
    *,
    height: int = 520,
    max_points: int = 500,
) -> None:
    """Muestra un mapa combinado para todas las especies visibles en resultados."""
    if occurrence_points_df.empty:
        st.info("No hay puntos de avistamiento disponibles para el mapa.")
        return

    if result_df.empty or "scientific_name" not in result_df.columns:
        st.info("No hay resultados para mostrar en el mapa.")
        return

    selected_names = result_df["scientific_name"].dropna().astype(str).tolist()
    points_df = filter_points_for_species_list(occurrence_points_df, selected_names)

    if points_df.empty:
        st.info("No hay coordenadas disponibles para los resultados actuales.")
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

    if len(points_df) > max_points:
        points_df = points_df.sample(n=max_points, random_state=42)

    center_latitude = float(points_df["decimalLatitude"].mean())
    center_longitude = float(points_df["decimalLongitude"].mean())

    result_map = folium.Map(
        location=[center_latitude, center_longitude],
        zoom_start=2,
        control_scale=True,
    )

    for _, row in points_df.iterrows():
        folium.CircleMarker(
            location=[
                float(row["decimalLatitude"]),
                float(row["decimalLongitude"]),
            ],
            radius=4,
            popup=build_popup_text(row),
            fill=True,
        ).add_to(result_map)

    st.caption(f"Mapa combinado: {len(points_df)} puntos de los resultados actuales.")
    st_folium(result_map, width=None, height=height, key="results_occurrence_map")


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
        canonical_selected = canonicalize_selected_species_name(selected)
        mask |= (
            occurrence_points_df["canonical_scientific_name"]
            .fillna("")
            .astype(str)
            .eq(canonical_selected)
        )

    return occurrence_points_df.loc[mask].copy()


def filter_points_for_species_list(
    occurrence_points_df: pd.DataFrame,
    selected_species_names: list[str],
) -> pd.DataFrame:
    """Filtra puntos para varias especies."""
    if occurrence_points_df.empty or not selected_species_names:
        return occurrence_points_df.iloc[0:0].copy()

    selected_values = set()
    canonical_values = set()

    for selected_name in selected_species_names:
        selected = str(selected_name).strip()

        if not selected:
            continue

        selected_values.add(selected)
        canonical_values.add(canonicalize_selected_species_name(selected))

    mask = pd.Series(False, index=occurrence_points_df.index)

    if "scientific_name" in occurrence_points_df.columns:
        mask |= occurrence_points_df["scientific_name"].fillna("").astype(str).isin(selected_values)

    if "canonical_scientific_name" in occurrence_points_df.columns:
        mask |= occurrence_points_df["canonical_scientific_name"].fillna("").astype(str).isin(canonical_values)

    return occurrence_points_df.loc[mask].copy()


def canonicalize_selected_species_name(selected_species_name: str) -> str:
    """Quita autoría entre paréntesis para cruzar con canonical_scientific_name."""
    selected = str(selected_species_name).strip()
    return selected.split("(")[0].strip()


def build_popup_text(row: pd.Series) -> str:
    """Texto del popup del mapa."""
    country = str(row.get("countryCode", "Unknown"))
    event_date = str(row.get("eventDate", "Unknown date"))
    name = str(row.get("scientific_name", "Unknown species"))

    return f"{name}<br>Country: {country}<br>Date: {event_date}"


def build_map_key(selected_species_name: str) -> str:
    """Genera clave estable para Streamlit-Folium."""
    safe_key = (
        str(selected_species_name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(".", "")
    )

    return f"species_map_{safe_key[:80]}"
