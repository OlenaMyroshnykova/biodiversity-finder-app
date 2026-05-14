import pandas as pd

from src.artifact_contract import normalize_artifact_dataframe, validate_artifact_contract


def test_common_name_language_columns_are_optional_display_fields() -> None:
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Ursus arctos",
                "vernacular_names": "oso pardo | brown bear",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "family": "Ursidae",
                "tags_de_busqueda": "brown forest large",
                "search_document": "Ursus arctos oso pardo brown bear Ursidae",
            }
        ]
    )

    validation = validate_artifact_contract(df)
    normalized = normalize_artifact_dataframe(df)

    assert validation.is_valid
    assert validation.missing_columns == []
    assert "common_name_es" in normalized.columns
    assert "common_name_en" in normalized.columns
    assert normalized.loc[0, "common_name_es"] == ""
    assert "oso pardo" in normalized.loc[0, "search_document"]
