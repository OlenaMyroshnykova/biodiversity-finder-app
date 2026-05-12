Write-Host "Cleaning obsolete app files..."

$filesToRemove = @(
  "README_PATCH.md",

  "src/search_components/taxonomy_intents.py",
  "src/search_components/synonyms.py",

  "tests/test_butterfly_search.py",
  "tests/test_multilingual_search.py",
  "tests/test_general_search_precision.py",
  "tests/test_jaguar_search.py",
  "tests/test_felidae_general_search.py",
  "tests/test_search_engine_refactor.py",
  "tests/test_vernacular_search_app.py",
  "tests/test_clean_code_structure.py",

  "tests/test_ui_sidebar_flags_only.py",
  "tests/test_ui_formatting.py"
)

foreach ($filePath in $filesToRemove) {
  if (Test-Path $filePath) {
    git rm -f $filePath 2>$null
    if (Test-Path $filePath) {
      Remove-Item -Force $filePath
    }
    Write-Host "Removed: $filePath"
  }
}

Write-Host "Cleanup finished."
