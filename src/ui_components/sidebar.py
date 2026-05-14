"""Sidebar de búsqueda, filtros y selección de modo de datos."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.offline_loader import (
    ArtifactMode,
    MODE_LABELS,
    delete_offline_artifacts,
    describe_artifact_mode,
    download_offline_artifacts,
    expected_offline_files,
    get_default_artifact_mode,
    missing_offline_files,
)
from src.ui_components.config import MODEL_DASHBOARD_URL, SEARCH_MODEL_DESCRIPTION

PROJECT_SCOPE_KINGDOMS = {"Animalia", "Plantae"}
MODE_OPTIONS: list[ArtifactMode] = ["online_full", "online_light", "offline_light"]


def get_available_taxon_classes(df: pd.DataFrame) -> list[str]:
    """Return real taxonomic classes available in the loaded dataset."""
    if df.empty or "taxon_class" not in df.columns:
        return []
    scoped_df = df.copy()
    if "kingdom" in scoped_df.columns:
        scoped_df = scoped_df[scoped_df["kingdom"].fillna("").astype(str).isin(PROJECT_SCOPE_KINGDOMS)]
    classes = scoped_df["taxon_class"].dropna().astype(str).str.strip()
    classes = classes[classes.ne("")]
    return sorted(classes.unique().tolist())


def _safe_rerun() -> None:
    try:
        st.rerun()
    except Exception:  # pragma: no cover
        return


def _render_offline_artifact_actions() -> None:
    """Render buttons to download or delete local offline artifacts."""
    missing = missing_offline_files()

    if missing:
        st.sidebar.warning(
            "Faltan artifacts offline:\n" + "\n".join(f"- {path.name}" for path in missing)
        )
        if st.sidebar.button("Descargar artifacts offline ahora", type="primary"):
            with st.sidebar.status("Descargando artifacts light...", expanded=True) as status:
                try:
                    downloaded = download_offline_artifacts()
                except Exception as exc:  # pragma: no cover - network/HF dependent
                    status.update(label="No se pudieron descargar los artifacts.", state="error")
                    st.sidebar.error(str(exc))
                    return
                status.update(label="Artifacts offline descargados.", state="complete")
                st.sidebar.success("Guardado en data/offline: " + ", ".join(path.name for path in downloaded))
            _safe_rerun()
        return

    st.sidebar.success("Artifacts offline disponibles en data/offline.")
    with st.sidebar.expander("Gestionar artifacts offline", expanded=False):
        st.caption("Archivos locales que usa el modo offline:")
        for path in expected_offline_files():
            size_kb = path.stat().st_size / 1024 if path.exists() else 0
            st.caption(f"- {path.name} ({size_kb:,.0f} KB)")
        st.warning(
            "Eliminar solo borra la copia local en data/offline. "
            "No toca Hugging Face ni los artifacts del repo training."
        )
        if st.button("Eliminar artifacts offline locales", type="secondary"):
            removed = delete_offline_artifacts()
            if removed:
                st.success("Eliminados: " + ", ".join(path.name for path in removed))
            else:
                st.info("No había artifacts offline para eliminar.")
            _safe_rerun()


def render_data_mode_selector() -> ArtifactMode:
    """Render frontend selector for online/full/light/offline data modes."""
    default_mode = get_default_artifact_mode()
    default_index = MODE_OPTIONS.index(default_mode) if default_mode in MODE_OPTIONS else 0

    st.sidebar.markdown("### Modo de datos")
    selected_mode = st.sidebar.radio(
        "Selecciona la fuente de datos",
        options=MODE_OPTIONS,
        index=default_index,
        format_func=lambda mode: MODE_LABELS[mode],
        help=(
            "Online completo usa el artifact completo de Hugging Face. "
            "Online ligero usa el parquet comprimido. Offline local usa data/offline."
        ),
    )
    st.sidebar.caption(describe_artifact_mode(selected_mode))

    if selected_mode == "offline_light":
        _render_offline_artifact_actions()

    st.sidebar.divider()
    return selected_mode


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int, int]:
    """Render search and filter controls after the data mode has been selected."""
    st.sidebar.markdown("### Idiomas")
    st.sidebar.caption("Búsqueda principal disponible en Español e English.")
    st.sidebar.caption("Los nombres comunes se usan como apoyo visual y búsqueda secundaria por nombre.")
    st.sidebar.divider()

    st.sidebar.header("Búsqueda")
    query_text = st.sidebar.text_input(
        "Busca en lenguaje natural o por nombre científico",
        placeholder="animal grande de la sabana",
    )
    selected_classes = st.sidebar.multiselect(
        "Filtrar por clase taxonómica disponible en el dataset",
        options=get_available_taxon_classes(df),
        default=[],
    )

    max_observations = int(max(1, df["observations"].max())) if "observations" in df.columns and not df.empty else 1
    if max_observations <= 1:
        st.sidebar.caption("Filtro de observaciones no disponible para el artifact actual.")
        min_observations = 1
    else:
        min_observations = st.sidebar.slider(
            "Mínimo de observaciones en el dataset",
            min_value=1,
            max_value=max_observations,
            value=1,
        )

    max_results = st.sidebar.slider(
        "Número máximo de resultados",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
    )

    st.sidebar.divider()
    st.sidebar.markdown("### Motor de búsqueda")
    st.sidebar.caption(SEARCH_MODEL_DESCRIPTION)
    st.sidebar.caption(
        "La búsqueda vibe convierte la frase en etiquetas estructuradas y filtra con df.loc. "
        "Los nombres comunes quedan como fallback por nombre."
    )
    st.sidebar.caption(
        "Los estados de conservación proceden de IUCN Red List cuando conservation_source = 'IUCN Red List'."
    )
    st.sidebar.caption("Los mapas están dentro de cada tarjeta de especie.")
    st.sidebar.link_button("Métricas del clasificador taxonómico", MODEL_DASHBOARD_URL, width="stretch")

    st.sidebar.divider()
    st.sidebar.markdown("**Ejemplos de búsqueda**")
    st.sidebar.markdown(
        """
- `animal grande de la sabana`
- `small animal in the desert`
- `ave de humedal`
- `wetland bird`
- `planta verde de bosque`
- `large mammal forest`
- `cocodrilo` / `crocodile`
- `tiburón` / `shark`
- `Panthera leo` / `Equus quagga`
"""
    )

    return query_text, selected_classes, min_observations, max_results
