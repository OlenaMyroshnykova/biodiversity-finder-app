# 🐾 Biodiversity Finder App

Aplicación online de **Biodiversity Finder**.

Este repositorio contiene solo la parte de interfaz Streamlit. No descarga datos desde GBIF y no entrena la modelo.

Los artefactos ya entrenados se cargan desde Hugging Face Datasets:

```text
selenamir/biodiversity-finder-artifacts
```

## Qué hace la app

- Descarga `species_encyclopedia.parquet` desde Hugging Face.
- Descarga `metrics.json` desde Hugging Face.
- Permite buscar especies con lenguaje natural.
- Usa búsqueda semántica con TF-IDF y similitud coseno.
- Muestra tarjetas de enciclopedia y gráficos.
- Incluye búsqueda como `pajaro rosa`, `ave rapaz montaña`, `rana verde rio`.

## Estructura

```text
biodiversity-finder-app/
├── app.py
├── README.md
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── src/
│   ├── __init__.py
│   ├── artifact_loader.py
│   ├── charts.py
│   ├── search.py
│   └── ui.py
└── tests/
    └── test_search.py
```

## Ejecución local

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
streamlit run app.py
```

En PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
pytest
```

## Convención

- Variables, funciones y nombres de archivos: inglés.
- Textos visibles, comentarios y docstrings: español.
- El repositorio no contiene datos pesados.
