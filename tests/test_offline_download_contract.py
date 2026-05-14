from pathlib import Path

import src.offline_loader as offline_loader


def test_offline_artifacts_have_stable_local_names() -> None:
    assert set(offline_loader.OFFLINE_ARTIFACTS) == {
        "species_encyclopedia_light.parquet",
        "species_occurrence_points_light.parquet",
        "metrics.json",
    }


def test_download_offline_artifacts_copies_hf_files(monkeypatch, tmp_path: Path) -> None:
    fake_cache = tmp_path / "hf-cache"
    fake_cache.mkdir()

    def fake_hf_hub_download(**kwargs):
        source = fake_cache / Path(kwargs["filename"]).name
        source.write_text("fake artifact", encoding="utf-8")
        return str(source)

    monkeypatch.setattr(offline_loader, "hf_hub_download", fake_hf_hub_download)

    target_dir = tmp_path / "offline"
    downloaded = offline_loader.download_offline_artifacts(target_dir)

    assert [path.name for path in downloaded] == list(offline_loader.OFFLINE_ARTIFACTS)
    assert all(path.exists() for path in downloaded)
    assert all(path.parent == target_dir for path in downloaded)
