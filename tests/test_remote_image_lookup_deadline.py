import os
from unittest.mock import patch

import pandas as pd

from src.ui_components.species_cards import (
    _allow_remote_image_lookup,
    _remote_image_lookup_limit,
    get_card_image_url,
)


def test_remote_image_lookup_is_enabled_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_REMOTE_IMAGE_LOOKUP", raising=False)
    assert _allow_remote_image_lookup() is True


def test_remote_image_lookup_limit_defaults_to_six(monkeypatch):
    monkeypatch.delenv("REMOTE_IMAGE_LOOKUP_LIMIT", raising=False)
    assert _remote_image_lookup_limit() == 6


def test_remote_lookup_is_not_called_after_limit(monkeypatch):
    monkeypatch.setenv("ENABLE_REMOTE_IMAGE_LOOKUP", "true")
    monkeypatch.setenv("REMOTE_IMAGE_LOOKUP_LIMIT", "1")

    row = pd.Series({"scientific_name": "Panthera leo"})

    with patch("src.ui_components.species_cards._cached_find_species_image_url") as mocked_lookup:
        image_url = get_card_image_url(row, used_image_urls=set(), position=2)

    assert image_url is None
    mocked_lookup.assert_not_called()


def test_existing_artifact_image_url_wins_without_remote_lookup(monkeypatch):
    monkeypatch.setenv("ENABLE_REMOTE_IMAGE_LOOKUP", "false")
    row = pd.Series({"scientific_name": "Panthera leo", "image_url": "https://example.com/lion.jpg"})

    assert get_card_image_url(row, used_image_urls=set(), position=10) == "https://example.com/lion.jpg"
