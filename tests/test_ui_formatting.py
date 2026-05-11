"""Tests para formateo seguro en la interfaz."""

import math

from src.ui import format_coordinate, format_integer, format_score


def test_format_coordinate_with_number() -> None:
    """Debe formatear números con tres decimales."""
    assert format_coordinate(38.123456) == "38.123"


def test_format_coordinate_with_none() -> None:
    """Debe soportar None."""
    assert format_coordinate(None) == "N/A"


def test_format_coordinate_with_nan() -> None:
    """Debe soportar NaN."""
    assert format_coordinate(math.nan) == "N/A"


def test_format_coordinate_with_text() -> None:
    """Debe soportar texto inválido."""
    assert format_coordinate("not-a-number") == "N/A"


def test_format_integer_with_none() -> None:
    """Debe soportar enteros vacíos."""
    assert format_integer(None) == "0"


def test_format_score_with_text() -> None:
    """Debe soportar score inválido."""
    assert format_score("bad-score") == "0.000"
