from src import offline_loader


def test_delete_offline_artifacts_removes_only_expected_files(tmp_path, monkeypatch):
    monkeypatch.setattr(offline_loader, "OFFLINE_DATA_DIR", tmp_path)

    expected = offline_loader.expected_offline_files()
    for path in expected:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("demo", encoding="utf-8")

    extra_file = tmp_path / "keep_me.txt"
    extra_file.write_text("do not delete", encoding="utf-8")

    removed = offline_loader.delete_offline_artifacts()

    assert sorted(path.name for path in removed) == sorted(path.name for path in expected)
    assert all(not path.exists() for path in expected)
    assert extra_file.exists()


def test_missing_offline_files_reports_absent_expected_files(tmp_path, monkeypatch):
    monkeypatch.setattr(offline_loader, "OFFLINE_DATA_DIR", tmp_path)

    missing_names = {path.name for path in offline_loader.missing_offline_files()}

    assert missing_names == {
        "species_encyclopedia_light.parquet",
        "species_occurrence_points_light.parquet",
        "metrics.json",
    }
