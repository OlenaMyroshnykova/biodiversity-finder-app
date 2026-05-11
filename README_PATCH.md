# UI Patch para Biodiversity Finder App

Este parche mejora la versión visual de la aplicación:

- Elimina HTML visible en las tarjetas.
- Sustituye las tarjetas largas por bloques nativos de Streamlit.
- Organiza la página en pestañas.
- Muestra menos resultados por defecto.
- Mejora la búsqueda `pajaro rosa` priorizando aves frente a plantas.
- Sustituye `use_container_width=True` por `width="stretch"`.
- Añade una tabla compacta de resultados.
- Añade una sección de resumen del dataset.

## Archivos que reemplaza

```text
app.py
src/search.py
src/charts.py
src/ui.py
tests/test_search.py
```

Copia estos archivos encima de los existentes, ejecuta tests y haz commit.
