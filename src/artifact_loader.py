"""Carga artefactos desde Hugging Face Datasets."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st
from huggingface_hub import hf_hub_download


REPO_ID = "selenamir/biodiversity-finder-artifacts"
REPO_TYPE = "dataset"


@st.cache_data(show_spinner="Cargando enciclopedia desde Hugging Face...")
def load_encyclopedia() -> pd.DataFrame:
    """
    Carga la enciclopedia de especies desde Hugging Face.

    Returns:
        Dataframe con perfiles agregados de especies.
    """
    file_path = hf_hub_download(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        filename="processed/species_encyclopedia.parquet",
    )

    return pd.read_parquet(file_path)


@st.cache_data(show_spinner="Cargando métricas del modelo...")
def load_metrics() -> dict:
    """
    Carga métricas de entrenamiento desde Hugging Face.

    Returns:
        Diccionario con métricas principales.
    """
    file_path = hf_hub_download(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        filename="reports/metrics.json",
    )

    with open(file_path, "r", encoding="utf-8") as metrics_file:
        return json.load(metrics_file)
