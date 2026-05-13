"""Carga artefactos desde Hugging Face o desde modo offline local.

Optimización para la demo:
- Usa artefactos *_light.parquet por defecto.
- El parquet completo solo se usa si USE_FULL_ARTIFACTS=true.
- El scope se limita a Animalia + Plantae.
- Normaliza columnas de conservación para IUCN Red List v4.
"""
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
PROJECT_SCOPE_KINGDOMS = {"Animalia", "Plantae"}

ENCYCLOPEDIA_LIGHT_FILE = "processed/species_encyclopedia_light.parquet"
ENCYCLOPEDIA_FULL_FILE = "processed/species_encyclopedia.parquet"
OCCURRENCE_POINTS_LIGHT_FILE = "processed/species_occurrence_points_light.parquet"
OCCURRENCE_POINTS_FULL_FILE = "processed/species_occurrence_points.parquet"

ENCYCLOPEDIA_COLUMNS = [
    "scientific_name",
    "canonical_scientific_name",
    "vernacular_names",
    "common_name_es",
    "common_name_en",
    "kingdom",
    "phylum",
    "taxon_class",
    "taxon_order",
    "family",
    "genus",
    "species",
    "observations",
    "countries",
    "first_year",
    "last_year",
    "most_common_basis",
    "most_common_season",
    "avg_latitude",
    "avg_longitude",
    "habitat_tag",
    "size_tag",
    "color_tag",
    "tags_de_busqueda",
    "search_document",
    "profile_text",
    "image_url",
    "thumbnail_url",
    "media_url",
    "gbif_image_url",
    "wikidata_image_url",
    "image_source",
    "has_image",
    "iucn_category",
    "iucn_status_label",
    "iucn_source",
    "iucn_is_official",
    "conservation_status",
    "conservation_category",
    "conservation_source",
    "conservation_note",
    "is_threatened",
]

OCCURRENCE_POINT_COLUMNS = [
    "scientific_name",
    "canonical_scientific_name",
    "decimalLatitude",
    "decimalLongitude",
    "countryCode",
    "eventDate",
]


def is_offline_mode() -> bool:
    """Indica si la app debe intentar usar archivos locales ligeros."""
    return os.getenv("OFFLINE_MODE", "false").strip().lower() == "true"


def _use_full_artifacts() -> bool:
    """Permite usar artefactos completos solo si se pide explícitamente."""
    return os.getenv("USE_FULL_ARTIFACTS", "false").strip().lower() == "true"


def _read_parquet_selected_columns(file_path: str | Path, expected_columns: list[str]) -> pd.DataFrame:
    """Lee solo columnas esperadas cuando el parquet lo permite."""
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


def _download_artifact(filename: str) -> str:
    """Descarga un archivo de Hugging Face usando la caché local del Hub."""
    token = os.getenv("HF_TOKEN") or None
    return hf_hub_download(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        filename=filename,
        token=token,
    )


def _normalize_project_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra la app al scope del proyecto: animales y plantas."""
    if df.empty or "kingdom" not in df.columns:
        return df.copy()

    scoped_df = df[df["kingdom"].fillna("").astype(str).isin(PROJECT_SCOPE_KINGDOMS)].copy()
    return scoped_df if not scoped_df.empty else df.copy()


def _normalize_conservation_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura columnas de conservación coherentes con IUCN Red List v4."""
    result_df = df.copy()

    if "iucn_category" not in result_df.columns:
        if "conservation_status" in result_df.columns:
            result_df["iucn_category"] = result_df["conservation_status"]
        else:
            result_df["iucn_category"] = "NO_DATA"

    result_df["iucn_category"] = (
        result_df["iucn_category"].fillna("NO_DATA").astype(str).str.strip().replace({"": "NO_DATA"})
    )

    if "iucn_status_label" not in result_df.columns:
        if "conservation_category" in result_df.columns:
            result_df["iucn_status_label"] = result_df["conservation_category"]
        else:
            result_df["iucn_status_label"] = "Sin datos IUCN"

    result_df["iucn_status_label"] = (
        result_df["iucn_status_label"].fillna("Sin datos IUCN").astype(str).str.strip().replace({"": "Sin datos IUCN"})
    )

    if "conservation_status" not in result_df.columns:
        result_df["conservation_status"] = result_df["iucn_category"]

    if "conservation_category" not in result_df.columns:
        result_df["conservation_category"] = result_df["iucn_status_label"]

    if "conservation_source" not in result_df.columns:
        if "iucn_source" in result_df.columns:
            result_df["conservation_source"] = result_df["iucn_source"]
        else:
            result_df["conservation_source"] = "No IUCN data"

    result_df["conservation_source"] = (
        result_df["conservation_source"].fillna("No IUCN data").astype(str).str.strip().replace({"": "No IUCN data"})
    )

    if "iucn_is_official" not in result_df.columns:
        result_df["iucn_is_official"] = result_df["conservation_source"].eq("IUCN Red List")

    if "is_threatened" not in result_df.columns:
        result_df["is_threatened"] = result_df["iucn_category"].isin(["VU", "EN", "CR", "EW", "EX"])

    return result_df


@st.cache_data(show_spinner="Cargando enciclopedia ligera...")
def load_encyclopedia() -> pd.DataFrame:
    """Carga la enciclopedia ligera por defecto para mejorar el tiempo de carga."""
    if is_offline_mode():
        offline_path = OFFLINE_DATA_DIR / "species_encyclopedia_light.parquet"
        if offline_path.exists():
            df = _read_parquet_selected_columns(offline_path, ENCYCLOPEDIA_COLUMNS)
            return _normalize_conservation_columns(_normalize_project_scope(df))
        st.warning(
            "OFFLINE_MODE está activo, pero no se encontró "
            "data/offline/species_encyclopedia_light.parquet. Se usará Hugging Face."
        )

    filename = ENCYCLOPEDIA_FULL_FILE if _use_full_artifacts() else ENCYCLOPEDIA_LIGHT_FILE
    try:
        file_path = _download_artifact(filename)
    except Exception:
        file_path = _download_artifact(ENCYCLOPEDIA_FULL_FILE)

    df = _read_parquet_selected_columns(file_path, ENCYCLOPEDIA_COLUMNS)
    return _normalize_conservation_columns(_normalize_project_scope(df))


@st.cache_data(show_spinner="Cargando puntos de avistamiento ligeros...")
def load_occurrence_points() -> pd.DataFrame:
    """Carga puntos de avistamiento para mapas Folium."""
    if is_offline_mode():
        offline_path = OFFLINE_DATA_DIR / "species_occurrence_points_light.parquet"
        if offline_path.exists():
            return _read_parquet_selected_columns(offline_path, OCCURRENCE_POINT_COLUMNS)

    filename = OCCURRENCE_POINTS_FULL_FILE if _use_full_artifacts() else OCCURRENCE_POINTS_LIGHT_FILE
    try:
        file_path = _download_artifact(filename)
        return _read_parquet_selected_columns(file_path, OCCURRENCE_POINT_COLUMNS)
    except Exception:
        return pd.DataFrame(columns=OCCURRENCE_POINT_COLUMNS)


@st.cache_data(show_spinner="Cargando métricas del modelo...")
def load_metrics() -> dict:
    """Carga métricas de entrenamiento desde Hugging Face."""
    try:
        file_path = _download_artifact("reports/metrics.json")
        with open(file_path, "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except Exception:
        return {
            "accuracy": None,
            "note": "Métricas no disponibles en modo offline o sin conexión.",
        }
