import pandas as pd

from src.artifact_contract import normalize_artifact_dataframe
from src.search import semantic_search_encyclopedia


def test_search_uses_artifact_common_names_without_species_hack():
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Ursus arctos",
                "canonical_scientific_name": "Ursus arctos",
                "vernacular_names": "oso pardo | brown bear",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "family": "Ursidae",
                "tags_de_busqueda": "brown forest large marron bosque grande",
                "observations": 10,
                "search_document": "Ursus arctos oso pardo brown bear Ursidae",
                "has_image": True,
            },
            {
                "scientific_name": "Rattus norvegicus",
                "canonical_scientific_name": "Rattus norvegicus",
                "vernacular_names": "rata parda | brown rat",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "family": "Muridae",
                "tags_de_busqueda": "brown city small marron pequeno",
                "observations": 100,
                "search_document": "Rattus norvegicus rata parda brown rat Muridae",
                "has_image": True,
            },
        ]
    )

    normalized_df = normalize_artifact_dataframe(df)
    result = semantic_search_encyclopedia(normalized_df, "oso", top_n=5)

    assert not result.empty
    assert result.iloc[0]["canonical_scientific_name"] == "Ursus arctos"


def test_search_uses_tags_de_busqueda_for_vibe_queries():
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Desertus example",
                "canonical_scientific_name": "Desertus example",
                "vernacular_names": "",
                "kingdom": "Animalia",
                "taxon_class": "Insecta",
                "tags_de_busqueda": "small desert brown pequeno desierto marron",
                "observations": 3,
                "search_document": "Desertus example small desert brown pequeno desierto marron",
            }
        ]
    )

    result = semantic_search_encyclopedia(normalize_artifact_dataframe(df), "bicho pequeño desierto", top_n=5)
    assert len(result) == 1
