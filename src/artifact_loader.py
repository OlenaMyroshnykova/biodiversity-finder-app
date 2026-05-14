"""Carga artifacts desde Hugging Face o desde modo offline local.

Arquitectura correcta:
- Online/demo: usar artifact completo por defecto.
- Offline/campo: usar artifact ligero local o remoto solo cuando se pide.
- La app valida y normaliza el contrato, pero no repara datos con hacks por especie.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from huggingface_hub import hf_hub_download

from src.artifact_contract import ARTIFACT_COLUMNS, normalize_artifact_dataframe, validate_artifact_contract

REPO_ID = "selenamir/biodiversity-finder-artifacts"
REPO_TYPE = "dataset"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DATA_DIR = PROJECT_ROOT / "data" / "offline"

ENCYCLOPEDIA_LIGHT_FILE = "processed/species_encyclopedia_light.parquet"
ENCYCLOPEDIA_FULL_FILE = "processed/species_encyclopedia.parquet"
OCCURRENCE_POINTS_LIGHT_FILE = "processed/species_occurrence_points_light.parquet"
OCCURRENCE_POINTS_FULL_FILE = "processed/species_occurrence_points.parquet"

OCCURRENCE_POINT_COLUMNS = [
    "scientific_name",
    "canonical_scientific_name",
    "decimalLatitude",
    "decimalLongitude",
    "countryCode",
    "eventDate",
]


def _truthy_env(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def is_offline_mode() -> bool:
    """Modo offline real: no depende de llamadas remotas para los datos base."""
    return _truthy_env("OFFLINE_MODE", "false")


def use_light_artifacts() -> bool:
    """Permite forzar artifact ligero para demo lenta, pero no es el valor normal."""
    return _truthy_env("USE_LIGHT_ARTIFACTS", "false")


def _download_artifact(filename: str) -> str:
    token = os.getenv("HF_TOKEN") or None
    return hf_hub_download(repo_id=REPO_ID, repo_type=REPO_TYPE, filename=filename, token=token)


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


@st.cache_data(show_spinner="Cargando enciclopedia de especies...")
def load_encyclopedia() -> pd.DataFrame:
    """Carga la enciclopedia bajo contrato estable."""
    if is_offline_mode():
        offline_path = OFFLINE_DATA_DIR / "species_encyclopedia_light.parquet"
        if offline_path.exists():
            return normalize_artifact_dataframe(_read_parquet_selected_columns(offline_path, ARTIFACT_COLUMNS))
        st.warning(
            "OFFLINE_MODE está activo, pero no se encontró "
            "data/offline/species_encyclopedia_light.parquet. Se usará Hugging Face."
        )

    filename = ENCYCLOPEDIA_LIGHT_FILE if use_light_artifacts() else ENCYCLOPEDIA_FULL_FILE
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
def load_occurrence_points() -> pd.DataFrame:
    """Carga puntos de avistamiento para mapas Folium."""
    if is_offline_mode():
        offline_path = OFFLINE_DATA_DIR / "species_occurrence_points_light.parquet"
        if offline_path.exists():
            return _read_parquet_selected_columns(offline_path, OCCURRENCE_POINT_COLUMNS)

    filename = OCCURRENCE_POINTS_LIGHT_FILE if use_light_artifacts() else OCCURRENCE_POINTS_FULL_FILE
    try:
        file_path = _download_artifact(filename)
        return _read_parquet_selected_columns(file_path, OCCURRENCE_POINT_COLUMNS)
    except Exception:
        return pd.DataFrame(columns=OCCURRENCE_POINT_COLUMNS)


@st.cache_data(show_spinner="Cargando métricas del modelo...")
def load_metrics() -> dict:
    """Carga métricas del entrenamiento desde Hugging Face."""
    try:
        file_path = _download_artifact("reports/metrics.json")
        with open(file_path, "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except Exception:
        return {"accuracy": None, "note": "Métricas no disponibles."}
