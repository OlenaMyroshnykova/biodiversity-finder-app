"""Estilos globales."""

from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """Aplica estilos CSS personalizados."""
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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
