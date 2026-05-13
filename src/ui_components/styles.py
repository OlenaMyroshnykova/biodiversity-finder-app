"""Visual styles for the app."""
from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    """Apply lightweight responsive CSS."""
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f8fbf6 0%, #eef7ee 100%);
        }

        .species-image-frame {
            width: 100%;
            max-width: 360px;
            margin: 0 auto 0.75rem auto;
            border: 1px solid rgba(49, 94, 59, 0.18);
            border-radius: 16px;
            overflow: hidden;
            background: #f7faf7;
            box-shadow: 0 8px 24px rgba(31, 61, 40, 0.08);
        }

        .species-image-frame img {
            display: block;
            width: 100%;
            height: clamp(220px, 24vw, 420px);
            aspect-ratio: 4 / 3;
            object-fit: contain;
            background: #f7faf7;
        }

        .species-image-frame figcaption {
            padding: 0.6rem 0.8rem;
            text-align: center;
            color: #56705a;
            font-size: 0.88rem;
            background: rgba(238, 247, 238, 0.92);
        }

        .species-image-placeholder {
            width: 100%;
            max-width: 360px;
            height: clamp(220px, 24vw, 420px);
            aspect-ratio: 4 / 3;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 0.35rem;
            margin: 0 auto 0.75rem auto;
            border: 1px dashed rgba(49, 94, 59, 0.25);
            border-radius: 16px;
            background: #f7faf7;
            color: #56705a;
            text-align: center;
        }

        .species-image-placeholder span {
            font-weight: 700;
        }

        .species-image-placeholder small {
            padding: 0 1rem;
            opacity: 0.8;
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
