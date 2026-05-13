"""Estilos visuales de la app."""
from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """Aplica CSS ligero y responsive."""
    st.markdown(
        """
        <style>
        .species-image-frame {
            width: 100%;
            max-width: 360px;
            margin: 0 auto 0.75rem auto;
            border-radius: 18px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.10);
            display: flex;
            align-items: center;
            justify-content: center;
            aspect-ratio: 4 / 3;
        }

        .species-image-frame img {
            width: 100%;
            height: clamp(220px, 24vw, 420px);
            aspect-ratio: 4 / 3;
            object-fit: contain;
            display: block;
            background: rgba(0, 0, 0, 0.08);
        }

        .species-image-caption {
            text-align: center;
            font-size: 0.78rem;
            opacity: 0.78;
            margin-top: 0.2rem;
        }

        .species-image-placeholder {
            width: 100%;
            max-width: 360px;
            height: clamp(220px, 24vw, 420px);
            aspect-ratio: 4 / 3;
            border-radius: 18px;
            border: 1px dashed rgba(255, 255, 255, 0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            opacity: 0.75;
            padding: 1rem;
            margin: 0 auto 0.75rem auto;
        }

        @media (max-width: 768px) {
            .species-image-frame,
            .species-image-placeholder {
                max-width: 100%;
            }

            .species-image-frame img,
            .species-image-placeholder {
                height: 220px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
