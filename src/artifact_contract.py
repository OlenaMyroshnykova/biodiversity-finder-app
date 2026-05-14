"""Contrato de datos entre training y app.

La app no debe adivinar qué columnas existen ni compensar errores del pipeline
con reglas por especie. Este módulo define las columnas que el artifact debe
exponer y normaliza valores básicos para que la búsqueda sea estable.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

import pandas as pd

PROJECT_SCOPE_KINGDOMS = {"Animalia", "Plantae"}
THREATENED_IUCN_CATEGORIES = {"VU", "EN", "CR", "EW", "EX"}

SEARCH_CONTRACT_COLUMNS = [
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
    "countries",
    "source_queries",
    "profile_text",
    "color_tag",
    "habitat_tag",
    "size_tag",
    "tags_de_busqueda",
    "iucn_category",
    "iucn_status_label",
    "conservation_status",
    "conservation_category",
]

ARTIFACT_COLUMNS = SEARCH_CONTRACT_COLUMNS + [
    "observations",
    "first_year",
    "last_year",
    "avg_latitude",
    "avg_longitude",
    "most_common_basis",
    "most_common_season",
    "search_document",
    "image_url",
    "thumbnail_url",
    "media_url",
    "gbif_image_url",
    "wikidata_image_url",
    "image_source",
    "has_image",
    "iucn_source",
    "iucn_is_official",
    "conservation_source",
    "conservation_note",
    "is_threatened",
]


@dataclass(frozen=True)
class ArtifactValidationResult:
    """Resultado legible de la validación del artifact."""

    is_valid: bool
    missing_columns: list[str]


def normalize_text(value: object) -> str:
    """Normaliza texto para búsqueda ES/EN sin depender de mayúsculas o acentos."""
    text = str(value or "").lower().strip()
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(ascii_text.split())


def validate_artifact_contract(df: pd.DataFrame) -> ArtifactValidationResult:
    """Comprueba que el parquet tenga las columnas mínimas del contrato."""
    missing = [column for column in SEARCH_CONTRACT_COLUMNS if column not in df.columns]
    return ArtifactValidationResult(is_valid=not missing, missing_columns=missing)


def normalize_artifact_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica normalización defensiva al artifact cargado por Streamlit."""
    result = df.copy()

    for column in ARTIFACT_COLUMNS:
        if column not in result.columns:
            result[column] = ""

    if "kingdom" in result.columns:
        scoped = result[result["kingdom"].fillna("").astype(str).isin(PROJECT_SCOPE_KINGDOMS)].copy()
        if not scoped.empty:
            result = scoped

    for column in SEARCH_CONTRACT_COLUMNS + ["search_document"]:
        result[column] = result[column].fillna("").astype(str)

    result["iucn_category"] = (
        result["iucn_category"].fillna("NO_DATA").astype(str).str.strip().replace({"": "NO_DATA"})
    )
    result["conservation_status"] = result["conservation_status"].where(
        result["conservation_status"].astype(str).str.strip() != "",
        result["iucn_category"],
    )

    if "is_threatened" not in result.columns:
        result["is_threatened"] = False
    result["is_threatened"] = (
        result["is_threatened"].fillna(False).astype(bool)
        | result["iucn_category"].str.upper().isin(THREATENED_IUCN_CATEGORIES)
    )

    result["search_document"] = build_runtime_search_document(result)
    return result


def build_runtime_search_document(df: pd.DataFrame) -> pd.Series:
    """Crea un documento de búsqueda homogéneo desde el contrato del artifact."""
    document = pd.Series([""] * len(df), index=df.index, dtype=str)
    for column in SEARCH_CONTRACT_COLUMNS + ["search_document"]:
        if column in df.columns:
            document = document + " " + df[column].fillna("").astype(str)
    return document.apply(normalize_text)
