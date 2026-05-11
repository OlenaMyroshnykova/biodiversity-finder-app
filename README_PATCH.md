# Images Patch para Biodiversity Finder App

Este parche añade fotos a las tarjetas de especies.

## Qué cambia

- Añade `src/image_loader.py`.
- Busca imágenes en GBIF en vivo usando el nombre científico.
- Usa `st.cache_data` para no repetir llamadas constantemente.
- Muestra una imagen por tarjeta cuando GBIF devuelve una foto.
- Si GBIF no tiene foto para una especie, la tarjeta sigue funcionando sin imagen.
- Añade `requests` explícitamente a `requirements.txt`.
- Añade test básico para validar la extracción de URL de imagen.

## Archivos que reemplaza o añade

```text
requirements.txt
src/image_loader.py
src/ui.py
tests/test_image_loader.py
```

## Después de copiar

```bash
pip install -r requirements.txt
pytest
streamlit run app.py
```
