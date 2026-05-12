"""Tests para image_loader."""

from src.image_loader import (
    build_binomial_name,
    build_image_search_names,
    canonicalize_scientific_name,
    deduplicate_preserving_order,
)


def test_canonicalize_scientific_name_removes_parentheses_authority() -> None:
    """Debe quitar autoría entre paréntesis."""
    assert canonicalize_scientific_name("Panthera leo (Linnaeus, 1758)") == "Panthera leo"


def test_build_binomial_name_keeps_first_two_words() -> None:
    """Debe crear nombre binomial."""
    assert build_binomial_name("Panthera leo melanochaita") == "Panthera leo"


def test_build_image_search_names_keeps_specific_before_general() -> None:
    """Debe buscar primero nombre completo y luego fallback."""
    names = build_image_search_names("Panthera leo melanochaita (C.E.H.Smith, 1858)")

    assert names[0] == "Panthera leo melanochaita (C.E.H.Smith, 1858)"
    assert "Panthera leo melanochaita" in names
    assert "Panthera leo" in names


def test_deduplicate_preserving_order() -> None:
    """Debe quitar duplicados sin cambiar orden."""
    assert deduplicate_preserving_order(["a", "b", "a", "", "c"]) == ["a", "b", "c"]
