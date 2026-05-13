"""Visual styles for the app."""
from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """Apply CSS used by cards and responsive species images."""
    st.markdown(
        """
        <style>
        .species-image-frame {
            width: 100%;
            max-width: 360px;
            margin: 0 auto 0.75rem auto;
            border-radius: 18px;
            overflow: hidden;
            background: rgba(15, 23, 42, 0.06);
            border: 1px solid rgba(148, 163, 184, 0.35);
        }

        .species-image-frame img {
            width: 100%;
            height: clamp(220px, 24vw, 420px);
            aspect-ratio: 4 / 3;
            object-fit: contain;
            display: block;
        }

        .species-image-caption {
            font-size: 0.82rem;
            color: #64748b;
            padding: 0.35rem 0.55rem 0.5rem 0.55rem;
            text-align: center;
        }

        .species-image-placeholder {
            width: 100%;
            max-width: 360px;
            height: clamp(220px, 24vw, 420px);
            border-radius: 18px;
            border: 1px dashed rgba(148, 163, 184, 0.55);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #64748b;
            background: rgba(241, 245, 249, 0.55);
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
