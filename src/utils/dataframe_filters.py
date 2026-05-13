"""Filtros básicos de DataFrame para la app.

La app debe reflejar el dataset real generado por el repositorio de training.
Por eso las clases taxonómicas disponibles se calculan desde el DataFrame
cargado y se limita el alcance del prototipo a Animalia y Plantae, tal como
indica el enunciado del proyecto.
"""

from __future__ import annotations

import pandas as pd

PROJECT_KINGDOMS = {"Animalia", "Plantae"}


def filter_project_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve solo registros dentro del alcance del proyecto.

    El entregable habla de especies animales o plantas. Si un artefacto antiguo
    o completo contiene hongos u otros reinos, no deben aparecer en los filtros
    principales de la app ni en los resultados por defecto.
    """

    if df.empty or "kingdom" not in df.columns:
        return df.copy()

    normalized_kingdom = df["kingdom"].fillna("").astype(str).str.strip()
    return df[normalized_kingdom.isin(PROJECT_KINGDOMS)].copy()


def get_available_taxon_classes(df: pd.DataFrame) -> list[str]:
    """Obtiene las clases taxonómicas disponibles en el dataset actual.

    No usa listas hardcodeadas. Si el parquet cambia, el selector cambia con él.
    """

    scoped_df = filter_project_scope(df)

    if scoped_df.empty or "taxon_class" not in scoped_df.columns:
        return []

    classes = (
        scoped_df["taxon_class"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    classes = classes[classes.ne("")]

    return sorted(classes.unique().tolist())


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: list[str],
    min_observations: int,
) -> pd.DataFrame:
    """Aplica filtros básicos con df.loc y mantiene el alcance Animalia/Plantae."""

    filtered_df = filter_project_scope(df)

    if "observations" in filtered_df.columns:
        observations = pd.to_numeric(filtered_df["observations"], errors="coerce").fillna(0)
        filtered_df = filtered_df.loc[observations >= min_observations].copy()

    if selected_classes and "taxon_class" in filtered_df.columns:
        filtered_df = filtered_df.loc[
            filtered_df["taxon_class"].isin(selected_classes)
        ].copy()

    return filtered_df
