"""Species cards for the visual encyclopedia."""
from __future__ import annotations

import html
import os

import pandas as pd
import streamlit as st

from src.image_loader import find_species_image_url, is_probably_valid_image_url
from src.map_components.species_map import render_species_occurrence_map
from src.sighting_narratives import build_sighting_narrative
from src.utils.formatting import format_coordinate, format_integer, format_score

ARTIFACT_IMAGE_COLUMNS = [
    "image_url",
    "thumbnail_url",
    "media_url",
    "gbif_image_url",
    "wikidata_image_url",
    "image",
]


def remote_image_lookup_enabled() -> bool:
    """Allow deadline remote fallback unless explicitly disabled."""
    return os.getenv("ENABLE_REMOTE_IMAGE_LOOKUP", "true").strip().lower() == "true"


def remote_image_lookup_limit() -> int:
    """Maximum cards that may perform remote image lookup."""
    try:
        return max(0, int(os.getenv("REMOTE_IMAGE_LOOKUP_LIMIT", "3")))
    except ValueError:
        return 3


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def find_species_image_url_cached(scientific_name: str) -> str | None:
    """Cache remote image lookup for 24 hours to keep reruns fast."""
    return find_species_image_url(scientific_name)


def render_species_cards(
    df: pd.DataFrame,
    query_text: str,
    occurrence_points_df: pd.DataFrame | None = None,
) -> None:
    """Render encyclopedia cards with artifact images first and remote fallback."""
    if df.empty:
        st.warning("No hay especies para mostrar.")
        return

    if query_text.strip():
        st.caption(f"Resultados para: **{query_text}**")
    else:
        st.caption("Mostrando especies con más observaciones.")

    used_image_urls: set[str] = set()
    lookup_limit = remote_image_lookup_limit()

    for position, (_, row) in enumerate(df.head(15).iterrows(), start=1):
        if bool(row.get("is_threatened", False)):
            st.markdown(
                """
                <div class="threatened-card-note">
                Esta especie aparece como amenazada según IUCN Red List.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.container(border=True):
            image_column, content_column = st.columns([1, 2.4], vertical_alignment="top")

            with image_column:
                image_url = choose_card_image_url(
                    row=row,
                    position=position,
                    used_image_urls=used_image_urls,
                    remote_lookup_limit=lookup_limit,
                )
                if image_url:
                    used_image_urls.add(image_url)
                    render_fixed_species_image(
                        image_url=image_url,
                        caption=str(row.get("scientific_name", "")),
                    )
                else:
                    render_species_image_placeholder()

            with content_column:
                render_species_card_content(position, row)

            render_card_map_section(row, occurrence_points_df)


def choose_card_image_url(
    *,
    row: pd.Series,
    position: int,
    used_image_urls: set[str],
    remote_lookup_limit: int,
) -> str | None:
    """Prefer image URLs stored in the artifact, then remote lookup fallback."""
    artifact_url = get_artifact_image_url(row)
    if artifact_url and artifact_url not in used_image_urls:
        return artifact_url

    if not remote_image_lookup_enabled() or position > remote_lookup_limit:
        return None

    scientific_name = str(row.get("scientific_name", "") or "").strip()
    if not scientific_name:
        return None

    candidate_url = find_species_image_url_cached(scientific_name)
    if candidate_url and candidate_url not in used_image_urls:
        return candidate_url
    return None


def get_artifact_image_url(row: pd.Series) -> str | None:
    """Read a valid image URL already stored in the artifact."""
    for column in ARTIFACT_IMAGE_COLUMNS:
        if column not in row:
            continue
        value = str(row.get(column, "") or "").strip()
        if value and is_probably_valid_image_url(value):
            return value
    return None


def render_card_map_section(row: pd.Series, occurrence_points_df: pd.DataFrame | None) -> None:
    """Add an expandable Folium map per species."""
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
    """Render responsive image without distorted aspect ratio."""
    safe_url = html.escape(image_url, quote=True)
    safe_caption = html.escape(caption)
    st.markdown(
        f"""
        <div class="species-image-frame">
            <img src="{safe_url}" alt="{safe_caption}" loading="lazy" />
        </div>
        <div class="species-image-caption">{safe_caption}</div>
        """,
        unsafe_allow_html=True,
    )


def render_species_image_placeholder() -> None:
    """Show placeholder when no reliable image URL is available."""
    st.markdown(
        """
        <div class="species-image-placeholder">
            Imagen no disponible en el dataset ni en la búsqueda rápida.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_species_card_content(position: int, row: pd.Series) -> None:
    """Render textual content for a species card."""
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
        "Las etiquetas de hábitat, tamaño y color son inferencias educativas "
        "para búsqueda rápida; el estado de conservación viene de IUCN cuando "
        "la fuente aparece como IUCN Red List."
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
    """Show honest conservation badge and source."""
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
    elif status == "NO_DATA":
        st.info(message)
    else:
        st.success(message)


def format_common_names(value: object, max_names: int = 6) -> str:
    """Format pipe-separated common names without duplicates."""
    names_text = str(value or "").strip()
    if not names_text:
        return ""
    names = [name.strip() for name in names_text.split("|") if name.strip()]
    unique_names: list[str] = []
    seen: set[str] = set()
    for name in names:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            unique_names.append(name)
    return " / ".join(unique_names[:max_names])
