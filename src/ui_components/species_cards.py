"""Tarjetas de especies."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.image_loader import find_species_image_url
from src.utils.formatting import format_coordinate, format_integer, format_score


def render_species_cards(df: pd.DataFrame, query_text: str) -> None:
    """Renderiza tarjetas limpias de enciclopedia con imágenes."""
    if df.empty:
        st.warning("No hay especies para mostrar.")
        return

    if query_text.strip():
        st.caption(f"Resultados para: **{query_text}**")
    else:
        st.caption("Mostrando especies con más observaciones.")

    for position, (_, row) in enumerate(df.head(15).iterrows(), start=1):
        with st.container(border=True):
            image_column, content_column = st.columns([1, 2.4], vertical_alignment="top")

            with image_column:
                image_url = find_species_image_url(str(row.get("scientific_name", "")))

                if image_url:
                    st.image(
                        image_url,
                        caption=str(row.get("scientific_name", "")),
                        width="stretch",
                    )
                else:
                    st.info("Sin foto disponible")

            with content_column:
                render_species_card_content(position, row)


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

    st.write(row.get("profile_text", "Sin descripción disponible."))

    info_column_1, info_column_2, info_column_3 = st.columns(3)

    with info_column_1:
        st.markdown(f"**Países:** {row.get('countries', 'Unknown')}")
        st.markdown(
            f"**Periodo:** {row.get('first_year', 'N/A')}–{row.get('last_year', 'N/A')}"
        )

    with info_column_2:
        st.markdown(f"**Registro:** {row.get('most_common_basis', 'Unknown')}")
        st.markdown(f"**Estación:** {row.get('most_common_season', 'Unknown')}")

    with info_column_3:
        latitude = format_coordinate(row.get("avg_latitude"))
        longitude = format_coordinate(row.get("avg_longitude"))
        st.markdown(f"**Centro geográfico:** {latitude}, {longitude}")

        if "source_queries" in row:
            st.markdown(f"**Fuente:** {row.get('source_queries', 'Unknown')}")


def format_common_names(value: object, max_names: int = 6) -> str:
    """Formatea nombres comunes separados por pipe."""
    names_text = str(value or "").strip()

    if not names_text:
        return ""

    names = [
        name.strip()
        for name in names_text.split("|")
        if name.strip()
    ]

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
