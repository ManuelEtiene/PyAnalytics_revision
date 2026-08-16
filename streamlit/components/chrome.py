"""Injeta o CSS do design no app (claro / escuro)."""

from pathlib import Path

import streamlit as st

_STYLES = Path(__file__).resolve().parents[1] / "styles"


def inject_theme() -> None:
    """Carrega o tema base e, se ativo, o modo escuro."""
    css = (_STYLES / "theme.css").read_text()
    if st.session_state.get("tema_escuro"):
        css += "\n" + (_STYLES / "dark.css").read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
