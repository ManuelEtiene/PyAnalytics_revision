"""Título da página com botão Voltar à direita."""

import streamlit as st

from navigation import href


def faixa_titulo(titulo: str, voltar_id: str, label: str = "Voltar") -> None:
    """H2 à esquerda e Voltar à direita, na mesma linha."""
    with st.container(key="pya_titulo_faixa"):
        st.html(_html_faixa(titulo, voltar_id, label))


def _html_faixa(titulo: str, voltar_id: str, label: str) -> str:
    """Markup da faixa título + voltar."""
    return (
        '<div class="pya-titulo-faixa">'
        f"<h2>{titulo}</h2>"
        f'<a class="pya-voltar" href="{href(voltar_id)}" target="_self">'
        f"← {label}</a>"
        "</div>"
    )
