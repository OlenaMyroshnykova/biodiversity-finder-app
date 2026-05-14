"""Species cards for the visual encyclopedia."""

from __future__ import annotations

import html
import os

import pandas as pd
import streamlit as st

from src.image_loader import find_species_image_url, is_valid_image_url
from src.map_components.species_map import render_species_occurrence_map
from src.sighting_narratives import build_sighting_narrative
from src.utils.formatting import format_coordinate, format_integer, format_score

THREATENED_CATEGORIES = {"VU", "EN", "CR", "EW", "EX"}
NEAR_THREATENED_CATEGORIES = {"NT"}
DATA_DEFICIENT_CATEGORIES = {"DD"}
NO_DATA_CATEGORIES = {"NO_DATA", "NE", "N/A", "", "NONE", "NAN"}

ARTIFACT_IMAGE_COLUMNS = [
    # Prefer curated encyclopedia URLs when the artifact has them.
    "wikidata_image_url",
    "wikipedia_image_url",
    "image_url",
    "thumbnail_url",
    "media_url",
    # GBIF images are useful but often show habitat/traps; keep them last.
    "gbif_image_url",
]

_TECHNICAL_EMPTY_VALUES = {"", "unknown", "none", "nan", "n/a", "no_data"}


def _allow_remote_image_lookup() -> bool:
    """Remote lookup is enabled by default for the deadline demo."""
    return os.getenv("ENABLE_REMOTE_IMAGE_LOOKUP", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def _remote_image_lookup_limit() -> int:
    """Maximum number of visible cards allowed to make remote image lookups."""
    raw_value = os.getenv("REMOTE_IMAGE_LOOKUP_LIMIT", "6").strip()
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 6


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def _cached_find_species_image_url(
    primary_name: str,
    common_names: str = "",
) -> str | None:
    """Find a representative image with cache.

    The UI uses the canonical scientific name and common names when available.
    Wikipedia/Wikimedia is preferred over GBIF occurrence photos because GBIF can
    return habitat shots where the animal is barely visible.
    """
    clean_name = str(primary_name or "").strip()
    if not clean_name:
        return None

    return find_species_image_url(
        clean_name,
        common_names=str(common_names or ""),
        prefer_wikimedia=True,
    )


def render_species_cards(
    df: pd.DataFrame,
    query_text: str,
    occurrence_points_df: pd.DataFrame | None = None,
) -> None:
    """Render visual species cards with image, conservation and map."""
    if df.empty:
        st.warning("No hay especies para mostrar.")
        return

    if query_text.strip():
        st.caption(f"Resultados para: **{query_text}**")
    else:
        st.caption("Mostrando especies con más observaciones.")

    used_image_urls: set[str] = set()

    for position, (_, row) in enumerate(df.head(15).iterrows(), start=1):
        if is_row_threatened(row):
            st.markdown("> ⚠️ Esta especie aparece como amenazada según IUCN Red List.")

        with st.container(border=True):
            image_column, content_column = st.columns([1, 2.4], vertical_alignment="top")

            with image_column:
                image_url = get_card_image_url(row, used_image_urls, position)
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


def get_card_image_url(
    row: pd.Series,
    used_image_urls: set[str],
    position: int = 1,
) -> str | None:
    """Return image from artifact first, then limited remote lookup."""
    for column in ARTIFACT_IMAGE_COLUMNS:
        value = str(row.get(column, "") or "").strip()
        if is_valid_image_url(value) and value not in used_image_urls:
            return value

    if not _allow_remote_image_lookup():
        return None
    if position > _remote_image_lookup_limit():
        return None

    primary_name = (
        str(row.get("canonical_scientific_name", "") or "").strip()
        or str(row.get("scientific_name", "") or "").strip()
    )
    common_names = str(row.get("vernacular_names", "") or "")
    candidate_url = _cached_find_species_image_url(primary_name, common_names)

    if candidate_url and candidate_url not in used_image_urls and is_valid_image_url(candidate_url):
        return candidate_url
    return None


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
            max_points=120,
        )


def render_fixed_species_image(image_url: str, caption: str) -> None:
    """Render image with a stable responsive frame."""
    safe_url = html.escape(image_url, quote=True)
    safe_caption = html.escape(caption)
    st.markdown(
        f"""
        <div class="species-image-card">
            <div class="species-image-frame">
                <img src="{safe_url}" alt="{safe_caption}" loading="lazy" />
            </div>
            <div class="species-image-caption">{safe_caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_species_image_placeholder() -> None:
    """Render placeholder when no reliable image exists."""
    st.markdown(
        """
        <div class="species-image-card species-image-placeholder">
            <div class="species-image-frame species-image-frame-empty">
                <span>Imagen no disponible</span>
            </div>
            <div class="species-image-caption">Se mostrará cuando exista una URL fiable.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_species_card_content(position: int, row: pd.Series) -> None:
    """Render textual content for one card.

    The public card intentionally avoids raw internal columns like
    ``habitat_tag``, ``size_tag`` and ``most_common_season``. Those columns are
    useful for search, but they are not official biological facts and looked
    confusing in the demo UI.
    """
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
        st.metric("Score", format_score(get_display_score(row)))
        st.metric("Obs.", format_integer(row.get("observations", 0)))

    render_conservation_badge(row)
    st.markdown(build_sighting_narrative(row))
    render_data_quality_note(row)

    info_column_1, info_column_2, info_column_3 = st.columns(3)
    with info_column_1:
        st.markdown(f"**Países:** {row.get('countries', 'Unknown')}")
        st.markdown(f"**Periodo:** {row.get('first_year', 'N/A')}–{row.get('last_year', 'N/A')}")
    with info_column_2:
        st.markdown(f"**Registro:** {row.get('most_common_basis', 'Unknown')}")
        st.markdown(f"**Clase:** {row.get('taxon_class', 'Unknown')}")
    with info_column_3:
        latitude = format_coordinate(row.get("avg_latitude"))
        longitude = format_coordinate(row.get("avg_longitude"))
        st.markdown(f"**Centro geográfico:** {latitude}, {longitude}")
        st.markdown(f"**Familia:** {row.get('family', 'Unknown')}")

    search_signal_summary = build_search_signal_summary(row)
    if search_signal_summary:
        with st.expander("Detalles técnicos del artifact", expanded=False):
            st.caption(
                "Estas señales se usan para la búsqueda educativa. No son una ficha "
                "taxonómica oficial ni sustituyen fuentes científicas."
            )
            st.write(search_signal_summary)

    conservation_note = str(row.get("conservation_note", "") or "").strip()
    if conservation_note:
        st.caption(conservation_note)


def get_display_score(row: pd.Series) -> float:
    """Return the best score available for a card.

    Structured searches create ``structured_match_score`` while text searches
    create ``search_score``. Showing only ``search_score`` made good structured
    results appear as ``0.000``.
    """
    for column in ("search_score", "structured_match_score", "score"):
        value = row.get(column, None)
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        if numeric_value > 0:
            return numeric_value
    return 0.0


def build_search_signal_summary(row: pd.Series) -> str:
    """Build a compact technical summary for the collapsed diagnostics expander."""
    parts: list[str] = []
    size_label = humanize_tag_value(row.get("size_tag", ""), kind="size")
    habitat_label = humanize_tag_value(row.get("habitat_tag", ""), kind="habitat")
    color_label = humanize_tag_value(row.get("color_tag", ""), kind="color")

    if size_label:
        parts.append(f"tamaño: {size_label}")
    if habitat_label:
        parts.append(f"hábitat: {habitat_label}")
    if color_label:
        parts.append(f"color: {color_label}")

    return " · ".join(parts)


def humanize_tag_value(value: object, kind: str = "generic") -> str:
    """Convert raw search tags into short Spanish labels.

    We intentionally avoid returning long raw strings like
    ``forest mountain terrestrial bosque montana`` in the public card.
    """
    raw_value = str(value or "").strip().lower()
    if raw_value in _TECHNICAL_EMPTY_VALUES:
        return ""

    token_text = raw_value.replace("|", " ").replace(",", " ").replace(";", " ")
    tokens = {token.strip() for token in token_text.split() if token.strip()}

    if kind == "size":
        ordered = [
            ("large", "grande"),
            ("grande", "grande"),
            ("medium", "mediano"),
            ("mediano", "mediano"),
            ("small", "pequeño"),
            ("pequeno", "pequeño"),
            ("pequeño", "pequeño"),
            ("tiny", "muy pequeño"),
        ]
    elif kind == "habitat":
        ordered = [
            ("savanna", "sabana"),
            ("sabana", "sabana"),
            ("grassland", "pradera"),
            ("forest", "bosque"),
            ("bosque", "bosque"),
            ("wetland", "humedal"),
            ("humedal", "humedal"),
            ("desert", "desierto"),
            ("desierto", "desierto"),
            ("marine", "marino"),
            ("ocean", "océano"),
            ("mountain", "montaña"),
            ("montana", "montaña"),
            ("montaña", "montaña"),
            ("terrestrial", "terrestre"),
        ]
    elif kind == "color":
        ordered = [
            ("brown", "marrón"),
            ("marron", "marrón"),
            ("white", "blanco"),
            ("black", "negro"),
            ("red", "rojo"),
            ("pink", "rosa"),
            ("rosa", "rosa"),
            ("blue", "azul"),
            ("green", "verde"),
            ("yellow", "amarillo"),
            ("colorful", "colorido"),
        ]
    else:
        ordered = []

    labels: list[str] = []
    seen: set[str] = set()
    for token, label in ordered:
        if token in tokens and label not in seen:
            seen.add(label)
            labels.append(label)
        if len(labels) >= 3:
            break

    return ", ".join(labels)


def is_row_threatened(row: pd.Series) -> bool:
    """Calculate threatened status from IUCN category when available."""
    status = get_iucn_category(row)
    if status in THREATENED_CATEGORIES:
        return True
    return bool(row.get("is_threatened", False))


def get_iucn_category(row: pd.Series) -> str:
    """Return normalized IUCN category."""
    value = row.get("iucn_category", None)
    if value is None or str(value).strip() == "":
        value = row.get("conservation_status", "NO_DATA")
    return str(value or "NO_DATA").strip().upper()


def get_iucn_label(row: pd.Series) -> str:
    """Return human-readable IUCN label."""
    value = row.get("iucn_status_label", None)
    if value is None or str(value).strip() == "":
        value = row.get("conservation_category", "Sin datos IUCN")
    return str(value or "Sin datos IUCN").strip()


def get_conservation_source(row: pd.Series) -> str:
    """Return conservation source."""
    source = str(row.get("conservation_source", "") or "").strip()
    if not source:
        source = str(row.get("iucn_source", "") or "").strip()
    return source or "No IUCN data"


def render_conservation_badge(row: pd.Series) -> None:
    """Show conservation badge with clear source."""
    status = get_iucn_category(row)
    label = get_iucn_label(row)
    source = get_conservation_source(row)
    source_text = "Fuente: IUCN Red List" if source == "IUCN Red List" else "Fuente: sin datos IUCN oficiales"

    if status in THREATENED_CATEGORIES:
        st.error(f"Estado de conservación: {status} — {label}. {source_text}.")
    elif status in NEAR_THREATENED_CATEGORIES:
        st.warning(f"Estado de conservación: {status} — {label}. {source_text}.")
    elif status in DATA_DEFICIENT_CATEGORIES:
        st.info(f"Estado de conservación: {status} — {label}. {source_text}.")
    elif status in NO_DATA_CATEGORIES:
        st.info("Estado de conservación: Sin datos IUCN. Fuente: no disponible en este artifact.")
    else:
        st.success(f"Estado de conservación: {status} — {label}. {source_text}.")


def render_data_quality_note(row: pd.Series) -> None:
    """Show honest data quality note."""
    source = get_conservation_source(row)
    if source == "IUCN Red List":
        conservation_text = "El estado de conservación procede de IUCN Red List."
    else:
        conservation_text = "Si no hay coincidencia IUCN, se muestra Sin datos IUCN; no inventamos LC."
    st.caption(
        "Las señales de hábitat, tamaño y color son ayudas educativas para búsqueda, "
        "no descripciones biológicas oficiales. "
        f"{conservation_text}"
    )


def format_common_names(value: object, max_names: int = 6) -> str:
    """Format pipe-separated common names."""
    names_text = str(value or "").strip()
    if not names_text:
        return ""

    names = [name.strip() for name in names_text.split("|") if name.strip()]
    if not names:
        return ""

    unique_names: list[str] = []
    seen: set[str] = set()
    for name in names:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            unique_names.append(name)

    return " / ".join(unique_names[:max_names])
