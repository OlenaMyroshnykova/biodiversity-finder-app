from __future__ import annotations

import pandas as pd

from src.natural_language_query import apply_natural_language_filters, parse_natural_language_query
from src.search_components.query_expansion import expand_query
from src.ui_components.config import get_supported_languages_text


def test_frontend_supported_languages_are_es_en_without_flags():
    supported = get_supported_languages_text()

    assert supported == "Español, English"
    assert "Українська" not in supported
    assert "Русский" not in supported
    assert "Português" not in supported
    assert "Italiano" not in supported
    assert "🇪🇸" not in supported
    assert "🇬🇧" not in supported


def test_query_expansion_does_not_expand_removed_languages():
    expanded = expand_query("крокодил тварина passaro uccello")

    assert "reptilia" not in expanded
    assert "animalia" not in expanded
    assert "aves" not in expanded


def test_spanish_vibe_query_becomes_structured_filters():
    parsed = parse_natural_language_query("animal grande de la sabana")

    assert parsed.group_tags == ["animal"]
    assert parsed.size_tags == ["large"]
    assert parsed.habitat_tags == ["savanna"]


def test_common_names_do_not_override_structured_filters():
    df = pd.DataFrame(
        [
            {
                "scientific_name": "Panthera leo",
                "vernacular_names": "lion|león|лев",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "taxon_order": "Carnivora",
                "family": "Felidae",
                "size_tag": "large grande",
                "habitat_tag": "savanna sabana",
                "color_tag": "brown marron",
            },
            {
                "scientific_name": "Felis chaus",
                "vernacular_names": "jungle cat|gato de la jungla|камышовый кот",
                "kingdom": "Animalia",
                "taxon_class": "Mammalia",
                "taxon_order": "Carnivora",
                "family": "Felidae",
                "size_tag": "medium mediano",
                "habitat_tag": "wetland humedal",
                "color_tag": "brown marron",
            },
        ]
    )

    result, parsed, used_fallback = apply_natural_language_filters(df, "animal grande de la sabana")

    assert not used_fallback
    assert parsed.has_structured_filters
    assert list(result["scientific_name"]) == ["Panthera leo"]
    assert all(result["size_tag"].str.contains("large"))
    assert all(result["habitat_tag"].str.contains("savanna"))
