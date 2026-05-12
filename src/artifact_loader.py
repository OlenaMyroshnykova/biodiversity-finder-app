"""Carga artefactos desde Hugging Face o desde modo offline local."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from huggingface_hub import hf_hub_download


REPO_ID = "selenamir/biodiversity-finder-artifacts"
REPO_TYPE = "dataset"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DATA_DIR = PROJECT_ROOT / "data" / "offline"


def is_offline_mode() -> bool:
    """Indica si la app debe intentar usar archivos locales ligeros."""
    return os.getenv("OFFLINE_MODE", "false").strip().lower() == "true"


@st.cache_data(show_spinner="Cargando enciclopedia...")
def load_encyclopedia() -> pd.DataFrame:
    """Carga enciclopedia completa o ligera según modo."""
    if is_offline_mode():
        offline_path = OFFLINE_DATA_DIR / "species_encyclopedia_light.parquet"

        if offline_path.exists():
            return pd.read_parquet(offline_path)

        st.warning(
            "OFFLINE_MODE está activo, pero no se encontró "
            "data/offline/species_encyclopedia_light.parquet. "
            "Se usará Hugging Face."
        )

    file_path = hf_hub_download(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        filename="processed/species_encyclopedia.parquet",
    )

    return pd.read_parquet(file_path)


@st.cache_data(show_spinner="Cargando puntos de avistamiento...")
def load_occurrence_points() -> pd.DataFrame:
    """Carga puntos de avistamiento para mapas Folium."""
    if is_offline_mode():
        offline_path = OFFLINE_DATA_DIR / "species_occurrence_points_light.parquet"

        if offline_path.exists():
            return pd.read_parquet(offline_path)

    try:
        file_path = hf_hub_download(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            filename="processed/species_occurrence_points.parquet",
        )

        return pd.read_parquet(file_path)
    except Exception:
        return pd.DataFrame(
            columns=[
                "scientific_name",
                "canonical_scientific_name",
                "decimalLatitude",
                "decimalLongitude",
                "countryCode",
                "eventDate",
            ]
        )


@st.cache_data(show_spinner="Cargando métricas del modelo...")
def load_metrics() -> dict:
    """Carga métricas de entrenamiento desde Hugging Face."""
    try:
        file_path = hf_hub_download(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            filename="reports/metrics.json",
        )

        with open(file_path, "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except Exception:
        return {
            "accuracy": None,
            "note": "Métricas no disponibles en modo offline o sin conexión.",
        }
