"""Rodapé institucional."""

import streamlit as st


def render_footer() -> None:
    """Crédito do projeto de extensão, sempre no fim da página."""
    with st.container(key="pya_footer"):
        st.markdown("---")
        st.caption("© PyAnalytics — UFSC Campus Araranguá · Dados públicos de saúde")
