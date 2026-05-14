"""Contrato de datos entre training y app.

La app no debe adivinar qué columnas existen ni compensar errores del pipeline
con reglas por especie. Este módulo define qué columnas son obligatorias para
buscar y cuáles son solo de presentación.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

import pandas as pd

PROJECT_SCOPE_KINGDOMS = {"Animalia", "Plantae"}
THREATENED_IUCN_CATEGORIES = {"VU", "EN", "CR", "EW", "EX"}

# Campos mínimos para que la búsqueda funcione de forma estable.
# Importante: common_name_es/common_name_en NO son obligatorios. Son columnas
# bonitas para mostrar nombres por idioma si el pipeline conoce el idioma real
# desde GBIF/Wikidata, pero el buscador debe funcionar con vernacular_names y
# search_document aunque esas columnas no existan.
REQUIRED_SEARCH_CONTRACT_COLUMNS = [
    "scientific_name",
    "vernacular_names",
    "kingdom",
    "taxon_class",
    "family",
    "tags_de_busqueda",
    "search_document",
]

# Campos de presentación opcionales. Si faltan, la app los crea vacíos y usa
# vernacular_names/scientific_name como fallback visual.
OPTIONAL_DISPLAY_COLUMNS = [
    "common_name_es",
    "common_name_en",
    "preferred_common_name",
]

# Campos útiles para búsqueda/ranking si existen, pero no deben bloquear el demo
# porque algunos artifacts antiguos no los tienen separados.
OPTIONAL_SEARCH_COLUMNS = [
    "canonical_scientific_name",
    "phylum",
    "taxon_order",
    "genus",
    "species",
    "countries",
    "source_queries",
    "profile_text",
    "color_tag",
    "habitat_tag",
    "size_tag",
    "iucn_category",
    "iucn_status_label",
    "conservation_status",
    "conservation_category",
]

SEARCH_CONTRACT_COLUMNS = (
    REQUIRED_SEARCH_CONTRACT_COLUMNS + OPTIONAL_DISPLAY_COLUMNS + OPTIONAL_SEARCH_COLUMNS
)

ARTIFACT_COLUMNS = SEARCH_CONTRACT_COLUMNS + [
    "observations",
    "first_year",
    "last_year",
    "avg_latitude",
    "avg_longitude",
    "most_common_basis",
    "most_common_season",
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


@dataclass(frozen=True)
class ArtifactContractDiagnostics:
    """Diagnóstico técnico sin alarmar por columnas opcionales."""

    missing_required_columns: list[str]
    missing_optional_display_columns: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.missing_required_columns


def normalize_text(value: object) -> str:
    """Normaliza texto para búsqueda ES/EN sin depender de mayúsculas o acentos."""
    text = str(value or "").lower().strip()
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(ascii_text.split())


def validate_artifact_contract(df: pd.DataFrame) -> ArtifactValidationResult:
    """Comprueba solo las columnas mínimas para que la búsqueda funcione.

    Las columnas ``common_name_es`` y ``common_name_en`` son opcionales porque el
    idioma solo debe separarse cuando la fuente trae un language code fiable.
    Si faltan, ``normalize_artifact_dataframe`` las crea vacías.
    """
    missing = [column for column in REQUIRED_SEARCH_CONTRACT_COLUMNS if column not in df.columns]
    return ArtifactValidationResult(is_valid=not missing, missing_columns=missing)


def get_artifact_contract_diagnostics(df: pd.DataFrame) -> ArtifactContractDiagnostics:
    """Devuelve diagnóstico completo para un expander técnico, no para warning."""
    return ArtifactContractDiagnostics(
        missing_required_columns=[
            column for column in REQUIRED_SEARCH_CONTRACT_COLUMNS if column not in df.columns
        ],
        missing_optional_display_columns=[
            column for column in OPTIONAL_DISPLAY_COLUMNS if column not in df.columns
        ],
    )


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


VIBE_TAG_COLUMNS = {"tags_de_busqueda", "color_tag", "habitat_tag", "size_tag"}


def build_runtime_search_document(df: pd.DataFrame) -> pd.Series:
    """Build the free-text search document from names, taxonomy and profile text.

    ``tags_de_busqueda`` and the structured vibe columns are intentionally
    excluded from the TF-IDF text document. They are used by the
    natural-language-to-filter layer as structured signals, not as generic text.

    The function keeps the original casing from the artifact. The search engine
    normalizes text only at scoring time, so tests/debug output can still show
    names like "Leopardo" or "Phoenicopterus roseus" exactly as they came from
    the data pipeline.
    """
    document = pd.Series([""] * len(df), index=df.index, dtype=str)

    runtime_columns = [
        column
        for column in SEARCH_CONTRACT_COLUMNS + ["search_document"]
        if column not in VIBE_TAG_COLUMNS
    ]

    for column in runtime_columns:
        if column in df.columns:
            values = (
                df[column]
                .fillna("")
                .astype(str)
                .str.replace("|", " ", regex=False)
                .str.replace(";", " ", regex=False)
                .str.replace(",", " ", regex=False)
            )
            document = document + " " + values

    return document.str.replace(r"\s+", " ", regex=True).str.strip()
