# Offline local artifacts

Esta carpeta está pensada para los artifacts ligeros del modo offline local.

No subas los `.parquet` al repositorio. Descárgalos cuando los necesites:

```bash
python scripts/download_offline_artifacts.py
```

También puedes elegir **Offline local** en la sidebar de Streamlit y pulsar
**Descargar artifacts offline ahora**. La app guardará aquí:

- `species_encyclopedia_light.parquet`
- `species_occurrence_points_light.parquet`
- `metrics.json`
