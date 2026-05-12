"""API pública del buscador."""

from src.search_components.engine import semantic_search_encyclopedia
from src.search_components.normalizer import normalize_text
from src.search_components.query_expansion import expand_query

__all__ = [
    "semantic_search_encyclopedia",
    "normalize_text",
    "expand_query",
]
