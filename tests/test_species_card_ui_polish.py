import pandas as pd

from src.sighting_narratives import build_sighting_narrative
from src.ui_components.species_cards import (
    build_search_signal_summary,
    get_display_score,
    humanize_tag_value,
)


def test_narrative_does_not_present_search_habitat_tags_as_official_habitat():
    row = pd.Series(
        {
            "scientific_name": "Loxodonta africana",
            "vernacular_names": "African Savanna Elephant",
            "taxon_class": "Mammalia",
            "family": "Elephantidae",
            "habitat_tag": "forest mountain terrestrial bosque montana montaña terrestre",
            "size_tag": "medium large mediano grande",
            "color_tag": "brown",
            "observations": 21,
            "countries": "KE, TZ",
            "iucn_category": "EN",
            "conservation_source": "IUCN Red List",
        }
    )

    narrative = build_sighting_narrative(row)

    assert "asociado a bosques" not in narrative
    assert "forest mountain" not in narrative
    assert "señales de hábitat" in narrative
    assert "de tamaño grande" in narrative


def test_score_uses_structured_score_when_text_score_is_zero():
    row = pd.Series({"search_score": 0.0, "structured_match_score": 0.82})

    assert get_display_score(row) == 0.82


def test_raw_tag_noise_is_humanized_for_collapsed_diagnostics():
    assert humanize_tag_value("medium large mediano grande", kind="size") == "grande, mediano"
    assert humanize_tag_value(
        "forest mountain terrestrial bosque montana montaña terrestre",
        kind="habitat",
    ) == "bosque, montaña, terrestre"

    summary = build_search_signal_summary(
        pd.Series(
            {
                "size_tag": "medium large mediano grande",
                "habitat_tag": "forest mountain terrestrial bosque montana montaña terrestre",
                "color_tag": "brown",
            }
        )
    )

    assert "medium large" not in summary
    assert "forest mountain" not in summary
    assert "tamaño: grande, mediano" in summary
