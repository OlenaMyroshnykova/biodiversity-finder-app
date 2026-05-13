"""Species cards for the visual encyclopedia."""
from __future__ import annotations

import html
import os
from typing import Iterable

import pandas as pd
import streamlit as st

try:
    from src.image_loader import find_species_image_url
except Exception:  # pragma: no cover - defensive fallback for optional image lookup
    find_species_image_url = None  # type: ignore[assignment]

from src.map_components.species_map import render_species_occurrence_map
from src.sighting_narratives import build_sighting_narrative
from src.utils.formatting import format_coordinate, format_integer, format_score

THREATENED_CATEGORIES = {"VU", "EN", "CR", "EW", "EX"}
WARNING_CATEGORIES = {"NT", "DD"}
ARTIFACT_IMAGE_COLUMNS = (
    "image_url",
    "thumbnail_url",
    "media_url",
    "gbif_image_url",
    "wikidata_image_url",
)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _allow_remote_image_lookup() -> bool:
    """Whether the app may look up missing card images remotely."""
    return _env_bool("ENABLE_REMOTE_IMAGE_LOOKUP", True)


def _remote_image_lookup_limit() -> int:
    """Maximum number of visible cards that may trigger remote image lookup."""
    try:
        return max(0, int(os.getenv("REMOTE_IMAGE_LOOKUP_LIMIT", "6")))
    except ValueError:
        return 6


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def _cached_find_species_image_url(scientific_name: str) -> str | None:
    """Cached remote lookup wrapper."""
    if not scientific_name or find_species_image_url is None:
        return None
    try:
        return find_species_image_url(scientific_name)
    except Exception:
        return None


def _clean_url(value: object) -> str | None:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return None


def _artifact_image_url(row: pd.Series) -> str | None:
    """Return the first image URL already stored in the artifact."""
    for column in ARTIFACT_IMAGE_COLUMNS:
        if column not in row.index:
            continue
        url = _clean_url(row.get(column))
        if url:
            return url
    return None


def get_card_image_url(
    row: pd.Series,
    used_image_urls: set[str] | None = None,
    position: int = 1,
) -> str | None:
    """Choose card image URL.

    Priority:
    1. URLs stored in the artifact.
    2. Cached remote lookup for the first N visible cards.
    3. No image.
    """
    used = used_image_urls if used_image_urls is not None else set()

    artifact_url = _artifact_image_url(row)
    if artifact_url and artifact_url not in used:
        return artifact_url

    if not _allow_remote_image_lookup() or position > _remote_image_lookup_limit():
        return None

    scientific_name = str(row.get("scientific_name", "")).strip()
    remote_url = _cached_find_species_image_url(scientific_name)
    if remote_url and remote_url not in used:
        return remote_url
    return None


def get_iucn_category(row: pd.Series) -> str:
    """Return normalized IUCN category for a row."""
    status = row.get("iucn_category", row.get("conservation_status", "NO_DATA"))
    text = str(status or "NO_DATA").strip().upper()
    return text or "NO_DATA"


def get_conservation_source(row: pd.Series) -> str:
    """Return conservation source text."""
    source = row.get("conservation_source", row.get("iucn_source", "No IUCN data"))
    text = str(source or "No IUCN data").strip()
    return text or "No IUCN data"


def render_species_cards(
    df: pd.DataFrame,
    query_text: str,
    occurrence_points_df: pd.DataFrame | None = None,
) -> None:
    """Render encyclopedia species cards with images, IUCN badges and maps."""
    if df.empty:
        st.warning("No hay especies para mostrar.")
        return

    if query_text.strip():
        st.caption(f"Resultados para: **{query_text}**")
    else:
        st.caption("Mostrando especies con más observaciones.")

    used_image_urls: set[str] = set()
    for position, (_, row) in enumerate(df.head(15).iterrows(), start=1):
        is_threatened = get_iucn_category(row) in THREATENED_CATEGORIES or bool(row.get("is_threatened", False))
        if is_threatened:
            st.markdown("Esta especie figura como amenazada según la capa de conservación disponible.")

        with st.container(border=True):
            image_column, content_column = st.columns([1, 2.4], vertical_alignment="top")
            with image_column:
                image_url = get_card_image_url(row, used_image_urls=used_image_urls, position=position)
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


def render_card_map_section(
    row: pd.Series,
    occurrence_points_df: pd.DataFrame | None,
) -> None:
    """Add expandable occurrence map for one species."""
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
    """Render a responsive species image."""
    safe_url = html.escape(image_url, quote=True)
    safe_caption = html.escape(caption)
    st.markdown(
        f"""
        <div class="species-image-frame">
            <img src="{safe_url}" alt="{safe_caption}" loading="lazy" />
            <div class="species-image-caption">{safe_caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_species_image_placeholder() -> None:
    """Show placeholder when image is not available."""
    st.markdown(
        """
        <div class="species-image-placeholder">
            Imagen no disponible en el dataset
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_species_card_content(position: int, row: pd.Series) -> None:
    """Render textual card content."""
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
    render_data_quality_caption(row)

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


def render_conservation_badge(row: pd.Series) -> None:
    """Show visual conservation badge with honest source text."""
    status = get_iucn_category(row)
    category = str(row.get("iucn_status_label", row.get("conservation_category", "Sin datos IUCN")) or "Sin datos IUCN")
    source = get_conservation_source(row)
    is_official = bool(row.get("iucn_is_official", False)) or source == "IUCN Red List"

    if status in THREATENED_CATEGORIES:
        st.error(f"Estado de conservación: {status} — {category}\n\nFuente: {source}")
    elif status in WARNING_CATEGORIES:
        st.warning(f"Estado de conservación: {status} — {category}\n\nFuente: {source}")
    elif status == "LC" and is_official:
        st.success(f"Estado de conservación: LC — Least Concern\n\nFuente: {source}")
    elif status == "NO_DATA":
        st.info("Estado de conservación: Sin datos IUCN\n\nFuente: no disponible en esta ejecución")
    elif is_official:
        st.success(f"Estado de conservación: {status} — {category}\n\nFuente: {source}")
    else:
        st.info(f"Estado de conservación: {status} — {category}\n\nFuente: {source}")


def render_data_quality_caption(row: pd.Series) -> None:
    """Show concise data-quality note for tags and conservation."""
    source = get_conservation_source(row)
    if source == "IUCN Red List":
        conservation_text = "El estado de conservación procede de IUCN Red List."
    else:
        conservation_text = "Si no hay datos IUCN, la app muestra 'Sin datos IUCN' y no inventa una categoría LC."

    st.caption(
        "Las etiquetas de hábitat, tamaño y color son inferencias educativas "
        "para búsqueda con Pandas, no mediciones biológicas oficiales. "
        + conservation_text
    )


def format_common_names(value: object, max_names: int = 6) -> str:
    """Format pipe-separated common names and remove duplicates."""
    names_text = str(value or "").strip()
    if not names_text:
        return ""
    names = [name.strip() for name in names_text.split("|") if name.strip()]
    unique_names: list[str] = []
    seen: set[str] = set()
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_names.append(name)
    return " / ".join(unique_names[:max_names])
