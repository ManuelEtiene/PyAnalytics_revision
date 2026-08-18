"""Mortalidade evitável — página-reserva até a análise existir."""

import streamlit as st

from catalog import get_item
from components.voltar import faixa_titulo


def render() -> None:
    """Só o título do tema e o aviso de que ainda não há conteúdo."""
    item = get_item("evitavel")
    faixa_titulo(item.title, "sim")
    st.markdown("EM BREVE")
