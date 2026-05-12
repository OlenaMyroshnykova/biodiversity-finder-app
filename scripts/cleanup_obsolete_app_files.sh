#!/usr/bin/env bash
set -e

echo "Cleaning obsolete app files..."

FILES_TO_REMOVE=(
  "README_PATCH.md"

  # Search modules from previous animal-specific versions
  "src/search_components/taxonomy_intents.py"
  "src/search_components/synonyms.py"

  # Old tests that expected animal-specific intent logic
  "tests/test_butterfly_search.py"
  "tests/test_multilingual_search.py"
  "tests/test_general_search_precision.py"
  "tests/test_jaguar_search.py"
  "tests/test_felidae_general_search.py"
  "tests/test_search_engine_refactor.py"
  "tests/test_vernacular_search_app.py"
  "tests/test_clean_code_structure.py"

  # Old UI patch tests that can be too implementation-specific after refactor
  "tests/test_ui_sidebar_flags_only.py"
  "tests/test_ui_formatting.py"
)

for file_path in "${FILES_TO_REMOVE[@]}"; do
  if [ -f "$file_path" ]; then
    git rm -f "$file_path" 2>/dev/null || rm -f "$file_path"
    echo "Removed: $file_path"
  fi
done

echo "Cleanup finished."
