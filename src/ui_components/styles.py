"""Estilos visuales de la app."""

from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """Aplica CSS básico."""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 32%),
                radial-gradient(circle at bottom right, rgba(22, 163, 74, 0.12), transparent 35%),
                linear-gradient(135deg, #f8fafc 0%, #eef7f0 100%);
        }

        .block-container {
            padding-top: 2rem;
        }

        .threatened-card-label {
            border: 2px solid #dc2626;
            background: #fef2f2;
            color: #7f1d1d;
            border-radius: 14px;
            padding: 0.65rem 0.9rem;
            margin: 1rem 0 0.4rem 0;
            font-weight: 700;
        }

        .species-image-frame {
            width: 100%;
            margin: 0;
        }

        .species-image-frame img {
            width: 100%;
            height: 280px;
            max-height: 280px;
            object-fit: cover;
            object-position: center;
            display: block;
            border-radius: 16px;
            border: 1px solid rgba(15, 23, 42, 0.12);
            background: #f1f5f9;
        }

        .species-image-frame figcaption {
            margin-top: 0.45rem;
            color: #64748b;
            font-size: 0.82rem;
            text-align: center;
            line-height: 1.25;
        }

        .species-image-placeholder {
            width: 100%;
            height: 280px;
            border-radius: 16px;
            border: 1px dashed rgba(15, 23, 42, 0.25);
            background:
                radial-gradient(circle at top left, rgba(22, 163, 74, 0.12), transparent 45%),
                #f8fafc;
            color: #64748b;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            text-align: center;
        }

        .species-image-placeholder-icon {
            font-size: 2rem;
        }

        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.75);
            border-radius: 14px;
            padding: 0.5rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
        }

        div[data-testid="stAlert"] {
            border-radius: 14px;
        }

        @media (max-width: 768px) {
            .species-image-frame img,
            .species-image-placeholder {
                height: 220px;
                max-height: 220px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
