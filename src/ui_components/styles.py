"""Visual styles for the Streamlit app."""
from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """Apply stable, responsive CSS."""
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
            border: 1px solid rgba(255, 255, 255, 0.14);
            aspect-ratio: 4 / 3;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .species-image-frame img {
            width: 100%;
            height: clamp(220px, 24vw, 420px);
            aspect-ratio: 4 / 3;
            object-fit: contain;
            display: block;
            background: rgba(0, 0, 0, 0.10);
        }

        .species-image-caption {
            text-align: center;
            font-size: 0.85rem;
            opacity: 0.78;
            margin-top: 0.25rem;
        }

        .species-image-placeholder {
            width: 100%;
            height: clamp(220px, 24vw, 420px);
            border-radius: 18px;
            border: 1px dashed rgba(255, 255, 255, 0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            opacity: 0.72;
            padding: 1rem;
        }

        .threatened-card-note {
            border-left: 4px solid #ff4b4b;
            padding: 0.5rem 0.75rem;
            margin-bottom: 0.75rem;
            background: rgba(255, 75, 75, 0.08);
            border-radius: 0.5rem;
        }

        @media (max-width: 768px) {
            .species-image-frame {
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
