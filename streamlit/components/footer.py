"""Rodapé institucional."""

import streamlit as st


def render_footer() -> None:
    """Crédito do projeto de extensão."""
    st.markdown("---")
    st.caption("© PyAnalytics — UFSC Campus Araranguá · Dados públicos de saúde")
