"""Componentes visuales de Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.image_loader import find_species_image_url


LANGUAGE_FLAGS = [
    {"code": "es", "label": "Español", "image_url": "https://flagcdn.com/w80/es.png"},
    {"code": "gb", "label": "English", "image_url": "https://flagcdn.com/w80/gb.png"},
    {"code": "ua", "label": "Українська", "image_url": "https://flagcdn.com/w80/ua.png"},
    {"code": "pt", "label": "Português", "image_url": "https://flagcdn.com/w80/pt.png"},
    {"code": "it", "label": "Italiano", "image_url": "https://flagcdn.com/w80/it.png"},
    {"code": "ru", "label": "Русский", "image_url": "https://flagcdn.com/w80/ru.png"},
]

SEARCH_MODEL_DESCRIPTION = (
    "Búsqueda híbrida: TF-IDF por palabras + TF-IDF por caracteres + "
    "sinónimos multilingües + detección de intención + ajustes taxonómicos."
)

MODEL_DASHBOARD_URL = "https://biodiversity-finder-training.streamlit.app/"
MODEL_ADEQUACY_URL = MODEL_DASHBOARD_URL
ARTIFACTS_URL = "https://huggingface.co/datasets/selenamir/biodiversity-finder-artifacts"


def format_coordinate(value: object) -> str:
    """Formatea coordenadas de forma segura."""
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "N/A"


def format_integer(value: object) -> str:
    """Formatea enteros de forma segura para métricas."""
    try:
        if pd.isna(value):
            return "0"
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def format_score(value: object) -> str:
    """Formatea score de búsqueda de forma segura."""
    try:
        if pd.isna(value):
            return "0.000"
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "0.000"


def get_supported_languages_accessible_text() -> str:
    """Devuelve texto accesible con nombres de idiomas."""
    return ", ".join(language["label"] for language in LANGUAGE_FLAGS)


def get_language_flags_html(compact: bool = False) -> str:
    """
    Devuelve HTML con iconos reales de banderas.

    No usamos emoji de banderas porque algunos sistemas los muestran como letras.
    """
    image_size = 30 if compact else 42
    gap = 8 if compact else 12

    flag_items = []

    for language in LANGUAGE_FLAGS:
        label = language["label"]
        image_url = language["image_url"]
        flag_items.append(
            f"""
            <span title="{label}" style="
                display: inline-flex;
                align-items: center;
                margin-right: {gap}px;
                margin-bottom: 0.35rem;
            ">
                <img
                    src="{image_url}"
                    alt="{label}"
                    width="{image_size}"
                    style="
                        border-radius: 5px;
                        border: 1px solid rgba(0,0,0,0.14);
                        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                        vertical-align: middle;
                    "
                />
            </span>
            """
        )

    return f"""
    <div aria-label="{get_supported_languages_accessible_text()}" style="
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: {gap}px;
        margin: 0.25rem 0 0.5rem 0;
    ">
        {"".join(flag_items)}
    </div>
    """


def render_language_flags(compact: bool = False) -> None:
    """Renderiza banderas reales como imágenes."""
    st.markdown(get_language_flags_html(compact=compact), unsafe_allow_html=True)


def apply_styles() -> None:
    """Aplica estilos CSS personalizados sin depender de HTML complejo."""
    css = """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(46, 125, 50, 0.12), transparent 32%),
            radial-gradient(circle at bottom right, rgba(33, 150, 243, 0.10), transparent 36%),
            linear-gradient(135deg, #f5fbf6 0%, #ffffff 50%, #eef6ff 100%);
    }

    h1, h2, h3 {
        color: #1b5e20;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(46, 125, 50, 0.16);
        padding: 0.85rem;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.88);
        border-radius: 18px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header() -> None:
    """Renderiza cabecera principal."""
    st.title("🐾 Biodiversity Finder")

    st.info(
        "Enciclopedia inteligente de biodiversidad basada en datos reales de GBIF. "
        "Puedes buscar con lenguaje natural, por ejemplo: `pajaro rosa`, "
        "`animal polar hielo`, `bicho con alas`, `rana verde rio`, `planta con flor`."
    )

    render_language_and_metrics_bar()
    render_search_system_info()


def render_language_and_metrics_bar() -> None:
    """Muestra idiomas y enlace a métricas de forma visible."""
    language_column, metrics_column = st.columns([1.4, 1], vertical_alignment="center")

    with language_column:
        st.markdown("### 🌍 Idiomas de búsqueda")
        render_language_flags(compact=False)
        st.caption(get_supported_languages_accessible_text())

    with metrics_column:
        st.markdown("### 🤖 Evaluación")
        st.link_button(
            "📊 Ver métricas de adecuación de la modelo",
            MODEL_DASHBOARD_URL,
            width="stretch",
        )


def render_search_system_info() -> None:
    """Muestra información visible sobre idiomas, búsqueda y modelo."""
    with st.expander("ℹ️ Cómo funciona el buscador", expanded=False):
        st.markdown("#### 🌍 Idiomas")
        render_language_flags(compact=False)
        st.caption(get_supported_languages_accessible_text())

        st.markdown(
            """
            **Ejemplos multilingües:**

            - `mariposa`, `butterfly`, `метелик`, `borboleta`, `farfalla`, `бабочка`
            - `oso polar`, `polar bear`, `білий ведмідь`, `urso polar`, `orso polare`
            - `rana`, `frog`, `жаба`, `sapo`, `rã`, `rospo`
            - `planta con flor`, `flowering plant`, `квіткова рослина`, `planta com flor`, `pianta con fiore`
            """
        )

        st.markdown("#### 🔎 Buscador")
        st.write(SEARCH_MODEL_DESCRIPTION)
        st.caption(
            "Importante: el buscador no usa una LLM en tiempo real. "
            "Usa una estrategia híbrida de recuperación de información sobre la enciclopedia."
        )

        st.markdown("#### 🤖 Modelo y adecuación")
        st.write(
            "La app consulta una enciclopedia generada por el repositorio de training. "
            "Ese pipeline descarga datos desde GBIF, limpia registros, crea features, "
            "entrena una modelo taxonómica y publica artefactos."
        )

        st.link_button(
            "📊 Abrir dashboard de métricas de adecuación",
            MODEL_DASHBOARD_URL,
        )
        st.link_button(
            "📦 Ver dataset y artefactos publicados",
            ARTIFACTS_URL,
        )


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int, int]:
    """Renderiza controles laterales de búsqueda y filtros."""
    st.sidebar.header("🔎 Búsqueda")

    query_text = st.sidebar.text_input(
        "Busca con lenguaje natural",
        placeholder="bicho con alas",
    )

    selected_classes = st.sidebar.multiselect(
        "Clase taxonómica",
        options=sorted(df["taxon_class"].dropna().unique()),
        default=[],
    )

    min_observations = st.sidebar.slider(
        "Mínimo de observaciones",
        min_value=1,
        max_value=int(max(1, df["observations"].max())),
        value=1,
    )

    max_results = st.sidebar.slider(
        "Número de resultados",
        min_value=5,
        max_value=50,
        value=15,
        step=5,
    )

    st.sidebar.divider()
    st.sidebar.markdown("### 🌍 Idiomas")
    st.sidebar.markdown(get_language_flags_html(compact=True), unsafe_allow_html=True)
    st.sidebar.caption(get_supported_languages_accessible_text())

    st.sidebar.markdown("### 🧠 Buscador")
    st.sidebar.caption(SEARCH_MODEL_DESCRIPTION)

    st.sidebar.link_button(
        "📊 Métricas de adecuación",
        MODEL_DASHBOARD_URL,
        width="stretch",
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        """
        **Ejemplos útiles**

        - `pajaro rosa`
        - `animal polar hielo`
        - `oso polar`
        - `білий ведмідь`
        - `insecto mariposa`
        - `borboleta`
        - `farfalla`
        - `bicho con alas`
        - `rana verde rio`
        - `жаба`
        - `ave rapaz montaña`
        - `planta con flor`
        - `pianta con fiore`
        - `mamifero`
        """
    )

    return query_text, selected_classes, min_observations, max_results


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: list[str],
    min_observations: int,
) -> pd.DataFrame:
    """Aplica filtros básicos antes de la búsqueda semántica."""
    filtered_df = df[df["observations"] >= min_observations].copy()

    if selected_classes:
        filtered_df = filtered_df[filtered_df["taxon_class"].isin(selected_classes)]

    return filtered_df


def render_metrics(result_df: pd.DataFrame, full_df: pd.DataFrame, metrics: dict) -> None:
    """Muestra métricas principales."""
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        st.metric("Resultados", f"{len(result_df):,}")

    with column_2:
        observations = int(result_df["observations"].sum()) if not result_df.empty else 0
        st.metric("Observaciones filtradas", f"{observations:,}")

    with column_3:
        st.metric("Especies en dataset", f"{len(full_df):,}")

    with column_4:
        accuracy = metrics.get("accuracy")
        accuracy_text = f"{accuracy * 100:.1f}%" if isinstance(accuracy, (int, float)) else "N/A"
        st.metric("Accuracy ML", accuracy_text)


def render_species_cards(df: pd.DataFrame, query_text: str) -> None:
    """Renderiza tarjetas limpias de enciclopedia con imágenes."""
    if df.empty:
        st.warning("No hay especies para mostrar.")
        return

    if query_text.strip():
        st.caption(f"Resultados para: **{query_text}**")
    else:
        st.caption("Mostrando especies con más observaciones.")

    for position, (_, row) in enumerate(df.head(15).iterrows(), start=1):
        with st.container(border=True):
            image_column, content_column = st.columns([1, 2.4], vertical_alignment="top")

            with image_column:
                image_url = find_species_image_url(str(row.get("scientific_name", "")))

                if image_url:
                    st.image(
                        image_url,
                        caption=str(row.get("scientific_name", "")),
                        width="stretch",
                    )
                else:
                    st.info("Sin foto disponible")

            with content_column:
                score = row.get("search_score", 0.0)

                title_column, metric_column = st.columns([3, 1])

                with title_column:
                    st.subheader(f"{position}. {row.get('scientific_name', 'Unknown species')}")
                    taxonomy_line = (
                        f"{row.get('kingdom', 'Unknown')} · "
                        f"{row.get('taxon_class', 'Unknown')} · "
                        f"Orden: {row.get('taxon_order', 'Unknown')} · "
                        f"Familia: {row.get('family', 'Unknown')}"
                    )
                    st.caption(taxonomy_line)

                with metric_column:
                    st.metric("Score", format_score(score))
                    st.metric("Obs.", format_integer(row.get("observations", 0)))

                st.write(row.get("profile_text", "Sin descripción disponible."))

                info_column_1, info_column_2, info_column_3 = st.columns(3)

                with info_column_1:
                    st.markdown(f"**Países:** {row.get('countries', 'Unknown')}")
                    st.markdown(
                        f"**Periodo:** "
                        f"{row.get('first_year', 'N/A')}–{row.get('last_year', 'N/A')}"
                    )

                with info_column_2:
                    st.markdown(f"**Registro:** {row.get('most_common_basis', 'Unknown')}")
                    st.markdown(f"**Estación:** {row.get('most_common_season', 'Unknown')}")

                with info_column_3:
                    latitude = format_coordinate(row.get("avg_latitude"))
                    longitude = format_coordinate(row.get("avg_longitude"))

                    st.markdown(f"**Centro geográfico:** {latitude}, {longitude}")

                    if "source_queries" in row:
                        st.markdown(f"**Fuente:** {row.get('source_queries', 'Unknown')}")


def render_data_table(df: pd.DataFrame) -> None:
    """Renderiza tabla compacta final."""
    if df.empty:
        st.info("La tabla está vacía.")
        return

    columns = [
        "scientific_name",
        "kingdom",
        "taxon_class",
        "taxon_order",
        "family",
        "observations",
        "countries",
        "first_year",
        "last_year",
        "source_queries",
        "avg_latitude",
        "avg_longitude",
    ]

    if "search_score" in df.columns:
        columns = ["search_score"] + columns

    existing_columns = [column for column in columns if column in df.columns]

    st.dataframe(
        df[existing_columns],
        width="stretch",
        hide_index=True,
    )
