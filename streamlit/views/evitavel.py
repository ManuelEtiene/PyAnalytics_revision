"""Mortalidade evitável — página-reserva até a análise existir."""

import streamlit as st

from catalog import get_item


def render() -> None:
    """Só o título do tema e o aviso de que ainda não há conteúdo."""
    item = get_item("evitavel")
    st.markdown(f"## {item.title}")
    st.markdown("EM BREVE")
