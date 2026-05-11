"""Componentes visuales de Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def apply_styles() -> None:
    """
    Aplica estilos CSS personalizados.
    """
    css = """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(46, 125, 50, 0.16), transparent 31%),
            radial-gradient(circle at bottom right, rgba(33, 150, 243, 0.12), transparent 36%),
            linear-gradient(135deg, #f4fbf5 0%, #ffffff 48%, #eef6ff 100%);
    }

    h1, h2, h3 {
        color: #1b5e20;
    }

    .hero-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(46, 125, 50, 0.18);
        border-radius: 24px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.08);
    }

    .species-card {
        background: rgba(255, 255, 255, 0.94);
        border-left: 8px solid #2e7d32;
        border-radius: 20px;
        padding: 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.08);
    }

    .tag {
        display: inline-block;
        padding: 0.22rem 0.62rem;
        margin: 0.12rem;
        border-radius: 999px;
        background: #e8f5e9;
        border: 1px solid #c8e6c9;
        color: #1b5e20;
        font-weight: 600;
        font-size: 0.86rem;
    }

    .small-note {
        color: #4d5d4d;
        font-size: 0.94rem;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header() -> None:
    """
    Renderiza cabecera principal.
    """
    st.title("🐾 Biodiversity Finder")
    st.markdown(
        """
        <div class="hero-card">
        <b>Enciclopedia inteligente de biodiversidad</b><br>
        Explora especies a partir de datos reales procesados desde GBIF.
        Busca con lenguaje natural: <b>pajaro rosa</b>, <b>ave rapaz montaña</b>,
        <b>rana verde rio</b>, <b>animal polar hielo</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls(df: pd.DataFrame) -> tuple[str, list[str], int]:
    """
    Renderiza controles laterales de búsqueda y filtros.
    """
    st.sidebar.header("🔎 Búsqueda")

    query_text = st.sidebar.text_input(
        "Busca con lenguaje natural",
        placeholder="pajaro rosa",
    )

    selected_classes = st.sidebar.multiselect(
        "Filtrar por clase taxonómica",
        options=sorted(df["taxon_class"].dropna().unique()),
        default=[],
    )

    min_observations = st.sidebar.slider(
        "Mínimo de observaciones",
        min_value=1,
        max_value=int(max(1, df["observations"].max())),
        value=1,
    )

    st.sidebar.markdown(
        """
        **Ejemplos:**
        - pajaro rosa
        - ave rapaz montaña
        - rana verde rio
        - animal polar hielo
        - planta flor
        """
    )

    return query_text, selected_classes, min_observations


def apply_basic_filters(
    df: pd.DataFrame,
    selected_classes: list[str],
    min_observations: int,
) -> pd.DataFrame:
    """
    Aplica filtros básicos antes de la búsqueda semántica.
    """
    filtered_df = df[df["observations"] >= min_observations].copy()

    if selected_classes:
        filtered_df = filtered_df[filtered_df["taxon_class"].isin(selected_classes)]

    return filtered_df


def render_metrics(df: pd.DataFrame, metrics: dict) -> None:
    """
    Muestra métricas principales.
    """
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        st.metric("Especies mostradas", f"{len(df):,}")

    with column_2:
        observations = int(df["observations"].sum()) if not df.empty else 0
        st.metric("Observaciones", f"{observations:,}")

    with column_3:
        classes = df["taxon_class"].nunique() if not df.empty else 0
        st.metric("Clases", classes)

    with column_4:
        accuracy = metrics.get("accuracy")
        accuracy_text = f"{accuracy * 100:.1f}%" if isinstance(accuracy, (int, float)) else "N/A"
        st.metric("Accuracy ML", accuracy_text)


def render_species_cards(df: pd.DataFrame) -> None:
    """
    Renderiza tarjetas de enciclopedia.
    """
    st.header("📚 Enciclopedia de especies")

    if df.empty:
        st.info("No hay especies para mostrar.")
        return

    for _, row in df.head(30).iterrows():
        search_score = row.get("search_score", 0.0)

        html = f"""
        <div class="species-card">
            <h3><i>{row["scientific_name"]}</i></h3>

            <span class="tag">{row["kingdom"]}</span>
            <span class="tag">{row["taxon_class"]}</span>
            <span class="tag">Familia: {row["family"]}</span>
            <span class="tag">Observaciones: {row["observations"]:,}</span>
            <span class="tag">Score: {search_score:.3f}</span>

            <p>{row["profile_text"]}</p>

            <p>
            <b>Países:</b> {row["countries"]}<br>
            <b>Periodo:</b> {row["first_year"]}–{row["last_year"]}<br>
            <b>Registro más común:</b> {row["most_common_basis"]}<br>
            <b>Estación más frecuente:</b> {row["most_common_season"]}<br>
            <b>Centro geográfico aproximado:</b>
            {row["avg_latitude"]:.3f}, {row["avg_longitude"]:.3f}
            </p>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_data_table(df: pd.DataFrame) -> None:
    """
    Renderiza tabla final.
    """
    st.header("🧾 Tabla de especies")

    if df.empty:
        st.info("La tabla está vacía.")
        return

    columns = [
        "scientific_name",
        "taxon_class",
        "family",
        "observations",
        "countries",
        "first_year",
        "last_year",
        "avg_latitude",
        "avg_longitude",
    ]

    if "search_score" in df.columns:
        columns = ["search_score"] + columns

    existing_columns = [column for column in columns if column in df.columns]

    st.dataframe(
        df[existing_columns],
        use_container_width=True,
        hide_index=True,
    )
