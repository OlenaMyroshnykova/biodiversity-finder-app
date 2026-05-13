"""Tests de rendimiento funcional y textos actuales de la app."""
from __future__ import annotations

import pandas as pd

from src.artifact_loader import _normalize_conservation_columns, _normalize_project_scope
from src.search_components.engine import build_search_document_series
from src.ui_components.sidebar import get_available_taxon_classes
from src.ui_components.species_cards import get_iucn_category, get_conservation_source


def test_project_scope_removes_fungi_from_app_dataset() -> None:
    df = pd.DataFrame(
        [
            {"kingdom": "Animalia", "taxon_class": "Mammalia"},
            {"kingdom": "Plantae", "taxon_class": "Magnoliopsida"},
            {"kingdom": "Fungi", "taxon_class": "Agaricomycetes"},
        ]
    )

    scoped_df = _normalize_project_scope(df)

    assert set(scoped_df["kingdom"]) == {"Animalia", "Plantae"}
    assert get_available_taxon_classes(scoped_df) == ["Magnoliopsida", "Mammalia"]


def test_search_document_does_not_add_vibe_tags_to_tfidf() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Panthera leo",
                "vernacular_names": "Lion | León",
                "tags_de_busqueda": "brown savanna large",
                "search_document": "Panthera leo Lion León",
            }
        ]
    )

    document = build_search_document_series(df).iloc[0].lower()

    assert "panthera leo" in document
    assert "lion" in document
    assert "brown savanna large" not in document


def test_conservation_columns_do_not_fake_lc() -> None:
    df = pd.DataFrame([{"scientific_name": "Unknown species"}])

    normalized_df = _normalize_conservation_columns(df)

    assert normalized_df.loc[0, "iucn_category"] == "NO_DATA"
    assert normalized_df.loc[0, "conservation_source"] == "No IUCN data"


def test_card_conservation_helpers_prefer_iucn_fields() -> None:
    row = pd.Series(
        {
            "iucn_category": "VU",
            "iucn_status_label": "Vulnerable",
            "conservation_source": "IUCN Red List",
        }
    )

    assert get_iucn_category(row) == "VU"
    assert get_conservation_source(row) == "IUCN Red List"
