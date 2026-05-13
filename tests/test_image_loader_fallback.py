"""Tests para fallback de imágenes GBIF + Wikimedia."""

from src import image_loader


class FakeResponse:
    """Respuesta falsa para requests.get."""

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        """No hace nada."""
        return None

    def json(self):
        """Devuelve payload falso."""
        return self.payload


def test_is_valid_image_url_accepts_jpg() -> None:
    """Debe aceptar jpg."""
    assert image_loader.is_valid_image_url("https://example.com/image.jpg")


def test_is_valid_image_url_rejects_svg() -> None:
    """Debe rechazar svg."""
    assert not image_loader.is_valid_image_url("https://example.com/map.svg")


def test_extract_image_url_from_gbif_record() -> None:
    """Debe extraer imagen desde media.identifier."""
    record = {
        "media": [
            {
                "identifier": "https://example.com/species.jpg",
            }
        ]
    }

    assert image_loader.extract_image_url_from_gbif_record(record) == "https://example.com/species.jpg"


def test_find_species_image_uses_gbif_first(monkeypatch) -> None:
    """Debe usar GBIF si GBIF devuelve imagen."""
    def fake_get(url, params=None, headers=None, timeout=None):
        return FakeResponse(
            {
                "results": [
                    {
                        "media": [
                            {
                                "identifier": "https://example.com/gbif-image.jpg",
                            }
                        ]
                    }
                ]
            }
        )

    image_loader.find_species_image_url.cache_clear()
    image_loader.find_species_image_candidates.cache_clear()
    monkeypatch.setattr(image_loader.requests, "get", fake_get)

    assert image_loader.find_species_image_url("Vanessa atalanta") == "https://example.com/gbif-image.jpg"


def test_find_species_image_falls_back_to_wikimedia(monkeypatch) -> None:
    """Debe buscar en Wikimedia si GBIF no tiene imagen."""
    calls = []

    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append(url)

        if url == image_loader.GBIF_OCCURRENCE_URL:
            return FakeResponse({"results": []})

        return FakeResponse(
            {
                "query": {
                    "pages": [
                        {
                            "title": "File:Vanessa atalanta.jpg",
                            "imageinfo": [
                                {
                                    "thumburl": "https://upload.wikimedia.org/example/Vanessa_atalanta.jpg",
                                    "url": "https://upload.wikimedia.org/example/Vanessa_atalanta_original.jpg",
                                    "mime": "image/jpeg",
                                    "width": 700,
                                    "height": 500,
                                }
                            ],
                        }
                    ]
                }
            }
        )

    image_loader.find_species_image_url.cache_clear()
    image_loader.find_species_image_candidates.cache_clear()
    monkeypatch.setattr(image_loader.requests, "get", fake_get)

    result = image_loader.find_species_image_url("Vanessa atalanta")

    assert result == "https://upload.wikimedia.org/example/Vanessa_atalanta.jpg"
    assert any(image_loader.GBIF_OCCURRENCE_URL in call for call in calls)
    assert any(image_loader.WIKIMEDIA_API_URL in call for call in calls)


def test_wikimedia_ignores_bad_placeholder(monkeypatch) -> None:
    """Debe ignorar placeholders."""
    def fake_get(url, params=None, headers=None, timeout=None):
        return FakeResponse(
            {
                "query": {
                    "pages": [
                        {
                            "title": "File:placeholder.svg",
                            "imageinfo": [
                                {
                                    "thumburl": "https://upload.wikimedia.org/example/placeholder.svg",
                                    "mime": "image/svg+xml",
                                    "width": 700,
                                    "height": 500,
                                }
                            ],
                        }
                    ]
                }
            }
        )

    monkeypatch.setattr(image_loader.requests, "get", fake_get)

    assert image_loader.search_wikimedia_file("Vanessa atalanta") is None
