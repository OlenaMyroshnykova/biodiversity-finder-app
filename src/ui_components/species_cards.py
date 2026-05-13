"""Tarjetas de especies."""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from src.image_loader import find_species_image_url
from src.map_components.species_map import render_species_occurrence_map
from src.sighting_narratives import build_sighting_narrative
from src.utils.formatting import format_coordinate, format_integer, format_score


def render_species_cards(
    df: pd.DataFrame,
    query_text: str,
    occurrence_points_df: pd.DataFrame | None = None,
) -> None:
    """Renderiza tarjetas de enciclopedia con imágenes, avisos y mapa por especie."""
    if df.empty:
        st.warning("No hay especies para mostrar.")
        return
    if query_text.strip():
        st.caption(f"Resultados para: **{query_text}**")
    else:
        st.caption("Mostrando especies con más observaciones.")

    used_image_urls: set[str] = set()
    for position, (_, row) in enumerate(df.head(15).iterrows(), start=1):
        if bool(row.get("is_threatened", False)):
            st.markdown(
                """
                <div style="border-left: 5px solid #d33; padding-left: 0.75rem;">
                Esta especie aparece como amenazada según la capa de conservación disponible.
                </div>
                """,
                unsafe_allow_html=True,
            )
        with st.container(border=True):
            image_column, content_column = st.columns([1, 2.4], vertical_alignment="top")
            with image_column:
                candidate_url = find_species_image_url(str(row.get("scientific_name", "")))
                image_url = candidate_url if candidate_url not in used_image_urls else None
                if image_url:
                    used_image_urls.add(image_url)
                    render_fixed_species_image(image_url=image_url, caption=str(row.get("scientific_name", "")))
                else:
                    render_species_image_placeholder()
            with content_column:
                render_species_card_content(position, row)
                render_card_map_section(row, occurrence_points_df)


def render_card_map_section(row: pd.Series, occurrence_points_df: pd.DataFrame | None) -> None:
    """Añade mapa desplegable para una especie concreta."""
    if occurrence_points_df is None:
        return
    scientific_name = str(row.get("scientific_name", "")).strip()
    if not scientific_name:
        return
    with st.expander("Ver mapa de avistamientos para esta especie", expanded=False):
        render_species_occurrence_map(
            occurrence_points_df=occurrence_points_df,
            selected_species_name=scientific_name,
            height=360,
            max_points=200,
        )


def render_fixed_species_image(image_url: str, caption: str) -> None:
    """Renderiza imagen con tamaño responsive."""
    safe_url = html.escape(image_url, quote=True)
    safe_caption = html.escape(caption)
    st.markdown(
        f"""
        <div class="species-image-wrap">
          <img src="{safe_url}" class="species-image" alt="{safe_caption}" />
          <div class="species-image-caption">{safe_caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_species_image_placeholder() -> None:
    """Muestra placeholder cuando no hay imagen fiable."""
    st.markdown(
        """
        <div class="species-image-placeholder">Imagen no disponible</div>
        """,
        unsafe_allow_html=True,
    )


def render_species_card_content(position: int, row: pd.Series) -> None:
    """Renderiza el contenido textual de una tarjeta."""
    title_column, metric_column = st.columns([3, 1])
    with title_column:
        st.subheader(f"{position}. {row.get('scientific_name', 'Unknown species')}")
        common_names = format_common_names(row.get("vernacular_names", ""))
        if common_names:
            st.caption(f"**Nombres comunes:** {common_names}")
        taxonomy_line = (
            f"{row.get('kingdom', 'Unknown')} · "
            f"{row.get('taxon_class', 'Unknown')} · "
            f"Orden: {row.get('taxon_order', 'Unknown')} · "
            f"Familia: {row.get('family', 'Unknown')}"
        )
        st.caption(taxonomy_line)
    with metric_column:
        st.metric("Score", format_score(row.get("search_score", 0.0)))
        st.metric("Obs.", format_integer(row.get("observations", 0)))

    render_conservation_badge(row)
    st.markdown(build_sighting_narrative(row))
    st.caption(
        "⚠️ Las etiquetas de hábitat, tamaño y color son inferencias educativas "
        "basadas en taxonomía y datos agregados, no mediciones biológicas oficiales."
    )

    info_column_1, info_column_2, info_column_3 = st.columns(3)
    with info_column_1:
        st.markdown(f"**Países:** {row.get('countries', 'Unknown')}")
        st.markdown(f"**Periodo:** {row.get('first_year', 'N/A')}–{row.get('last_year', 'N/A')}")
    with info_column_2:
        st.markdown(f"**Registro:** {row.get('most_common_basis', 'Unknown')}")
        st.markdown(f"**Estación:** {row.get('most_common_season', 'Unknown')}")
        if "habitat_tag" in row:
            st.markdown(f"**Hábitat tag:** {row.get('habitat_tag', 'Unknown')}")
    with info_column_3:
        latitude = format_coordinate(row.get("avg_latitude"))
        longitude = format_coordinate(row.get("avg_longitude"))
        st.markdown(f"**Centro geográfico:** {latitude}, {longitude}")
        if "size_tag" in row:
            st.markdown(f"**Tamaño tag:** {row.get('size_tag', 'Unknown')}")

    if "conservation_note" in row and str(row.get("conservation_note", "")).strip():
        st.caption(f"{row.get('conservation_note')}")


def render_conservation_badge(row: pd.Series) -> None:
    """Muestra badge visual de conservación con fuente honesta."""
    status = str(row.get("iucn_category", row.get("conservation_status", "NO_DATA")) or "NO_DATA").upper()
    category = str(row.get("iucn_status_label", row.get("conservation_category", "Sin datos IUCN")) or "Sin datos IUCN")
    source = str(row.get("iucn_source", row.get("conservation_source", "No IUCN data")) or "No IUCN data")
    is_official = bool(row.get("iucn_is_official", source.lower().startswith("iucn")))
    is_threatened = bool(row.get("is_threatened", False))

    source_text = "Fuente: IUCN Red List" if is_official else "Fuente: sin datos IUCN oficiales"
    message = f"Estado de conservación: {status} — {category}. {source_text}."
    if is_threatened:
        st.error(message)
    elif status in {"NT", "DD"}:
        st.warning(message)
    else:
        st.success(message)


def format_common_names(value: object, max_names: int = 6) -> str:
    """Formatea nombres comunes separados por pipe."""
    names_text = str(value or "").strip()
    if not names_text:
        return ""
    names = [name.strip() for name in names_text.split("|") if name.strip()]
    if not names:
        return ""
    unique_names = []
    seen = set()
    for name in names:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            unique_names.append(name)
    return " / ".join(unique_names[:max_names])
