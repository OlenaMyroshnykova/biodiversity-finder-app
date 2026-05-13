"""App code should not depend on legacy curated download labels."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_app_narratives_do_not_use_source_query_demo_markers() -> None:
    checked_files = [
        PROJECT_ROOT / "src" / "sighting_narratives.py",
    ]
    combined_text = "\n".join(path.read_text(encoding="utf-8").lower() for path in checked_files)

    forbidden_markers = [
        "flamingo_pink_bird",
        "polar_bear",
        "jaguar_panthera_onca",
        "big_cats_felidae",
        "source_queries",
    ]

    for marker in forbidden_markers:
        assert marker not in combined_text
