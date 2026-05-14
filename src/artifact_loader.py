"""Load artifacts from Hugging Face or from local offline files.

Architecture:
- Online complete: use the full Hugging Face artifact for maximum search coverage.
- Online light: use the compressed/light Hugging Face artifact for quick demos.
- Offline local: use data/offline light artifacts previously downloaded by the app.

The app chooses the mode from the Streamlit sidebar and passes it to these loaders.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from huggingface_hub import hf_hub_download

from src.artifact_contract import (
    ARTIFACT_COLUMNS,
    normalize_artifact_dataframe,
    validate_artifact_contract,
)
from src.offline_loader import ArtifactMode, OFFLINE_DATA_DIR, get_default_artifact_mode

REPO_ID = "selenamir/biodiversity-finder-artifacts"
REPO_TYPE = "dataset"

ENCYCLOPEDIA_LIGHT_FILE = "processed/species_encyclopedia_light.parquet"
ENCYCLOPEDIA_FULL_FILE = "processed/species_encyclopedia.parquet"
OCCURRENCE_POINTS_LIGHT_FILE = "processed/species_occurrence_points_light.parquet"
OCCURRENCE_POINTS_FULL_FILE = "processed/species_occurrence_points.parquet"
METRICS_FILE = "reports/metrics.json"

OCCURRENCE_POINT_COLUMNS = [
    "scientific_name",
    "canonical_scientific_name",
    "decimalLatitude",
    "decimalLongitude",
    "countryCode",
    "eventDate",
]


def _resolve_mode(artifact_mode: ArtifactMode | str | None) -> ArtifactMode:
    if artifact_mode in {"online_full", "online_light", "offline_light"}:
        return artifact_mode  # type: ignore[return-value]
    return get_default_artifact_mode()


def _download_artifact(filename: str) -> str:
    token = os.getenv("HF_TOKEN") or None
    return hf_hub_download(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        filename=filename,
        token=token,
    )


def _read_parquet_selected_columns(file_path: str | Path, expected_columns: list[str]) -> pd.DataFrame:
    try:
        import pyarrow.parquet as pq

        schema = pq.read_schema(file_path)
        available_columns = [column for column in expected_columns if column in schema.names]
        if available_columns:
            return pd.read_parquet(file_path, columns=available_columns)
    except Exception:
        pass

    df = pd.read_parquet(file_path)
    available_columns = [column for column in expected_columns if column in df.columns]
    return df[available_columns].copy() if available_columns else df


def _online_filename(mode: ArtifactMode, full_file: str, light_file: str) -> str:
    return light_file if mode == "online_light" else full_file


@st.cache_data(show_spinner="Cargando enciclopedia de especies...")
def load_encyclopedia(artifact_mode: ArtifactMode | str | None = None) -> pd.DataFrame:
    """Load the encyclopedia according to the selected frontend mode."""
    mode = _resolve_mode(artifact_mode)

    if mode == "offline_light":
        offline_path = OFFLINE_DATA_DIR / "species_encyclopedia_light.parquet"
        if offline_path.exists():
            df = _read_parquet_selected_columns(offline_path, ARTIFACT_COLUMNS)
            return normalize_artifact_dataframe(df)
        st.warning(
            "Modo offline seleccionado, pero falta "
            "data/offline/species_encyclopedia_light.parquet. "
            "Cambia a modo online o ejecuta scripts/download_offline_artifacts.py."
        )
        return pd.DataFrame(columns=ARTIFACT_COLUMNS)

    filename = _online_filename(mode, ENCYCLOPEDIA_FULL_FILE, ENCYCLOPEDIA_LIGHT_FILE)
    try:
        file_path = _download_artifact(filename)
    except Exception:
        fallback = ENCYCLOPEDIA_LIGHT_FILE if filename == ENCYCLOPEDIA_FULL_FILE else ENCYCLOPEDIA_FULL_FILE
        file_path = _download_artifact(fallback)

    df = _read_parquet_selected_columns(file_path, ARTIFACT_COLUMNS)
    validation = validate_artifact_contract(df)
    if not validation.is_valid:
        st.warning(
            "El artifact no cumple completamente el contrato de búsqueda. "
            f"Columnas ausentes: {', '.join(validation.missing_columns)}"
        )
    return normalize_artifact_dataframe(df)


@st.cache_data(show_spinner="Cargando puntos de avistamiento...")
def load_occurrence_points(artifact_mode: ArtifactMode | str | None = None) -> pd.DataFrame:
    """Load occurrence points for Folium maps according to the selected mode."""
    mode = _resolve_mode(artifact_mode)

    if mode == "offline_light":
        offline_path = OFFLINE_DATA_DIR / "species_occurrence_points_light.parquet"
        if offline_path.exists():
            return _read_parquet_selected_columns(offline_path, OCCURRENCE_POINT_COLUMNS)
        return pd.DataFrame(columns=OCCURRENCE_POINT_COLUMNS)

    filename = _online_filename(mode, OCCURRENCE_POINTS_FULL_FILE, OCCURRENCE_POINTS_LIGHT_FILE)
    try:
        file_path = _download_artifact(filename)
        return _read_parquet_selected_columns(file_path, OCCURRENCE_POINT_COLUMNS)
    except Exception:
        return pd.DataFrame(columns=OCCURRENCE_POINT_COLUMNS)


@st.cache_data(show_spinner="Cargando métricas del modelo...")
def load_metrics(artifact_mode: ArtifactMode | str | None = None) -> dict:
    """Load model metrics from local offline artifacts or Hugging Face."""
    mode = _resolve_mode(artifact_mode)

    if mode == "offline_light":
        offline_path = OFFLINE_DATA_DIR / "metrics.json"
        if offline_path.exists():
            with open(offline_path, "r", encoding="utf-8") as metrics_file:
                return json.load(metrics_file)
        return {"accuracy": None, "note": "Métricas offline no disponibles."}

    try:
        file_path = _download_artifact(METRICS_FILE)
        with open(file_path, "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except Exception:
        return {"accuracy": None, "note": "Métricas no disponibles."}
