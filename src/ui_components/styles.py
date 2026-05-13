"""Estilos visuales de la app."""
from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """Aplica CSS ligero y responsive."""
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: #f7fbf7;
        }

        .species-image-frame {
            margin: 0;
            border: 1px solid rgba(49, 92, 54, 0.15);
            border-radius: 14px;
            overflow: hidden;
            background: #f8fbf8;
        }

        .species-image-frame img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            display: block;
        }

        .species-image-frame figcaption {
            padding: 0.35rem 0.6rem;
            color: #5d6b60;
            font-size: 0.82rem;
        }

        .species-image-placeholder {
            min-height: 220px;
            border: 1px dashed rgba(49, 92, 54, 0.25);
            border-radius: 14px;
            background: #f8fbf8;
            color: #6d786f;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 1rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(49, 92, 54, 0.12);
            border-radius: 14px;
            padding: 0.7rem 0.9rem;
        }

        @media (max-width: 768px) {
            .species-image-frame img,
            .species-image-placeholder {
                height: 170px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
