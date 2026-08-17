"""Cabeçalho e seções iguais às do Retrato."""

import streamlit as st

from components.plot import plot_or_caption


def cabecalho(titulo: str, detalhe: str) -> None:
    """Título H2 + linha de recorte/período."""
    st.markdown(f"## {titulo}")
    st.caption(detalhe)


def secao(nome: str, *pares) -> None:
    """Subtítulo H3 e gráficos em sequência (um por vez, largura total)."""
    st.markdown(f"### {nome}")
    for par in pares:
        _mostra(par)


def _mostra(par) -> None:
    """Aceita (fig, insight) ou uma lista desses pares."""
    if par is None:
        return
    if isinstance(par, list):
        for item in par:
            plot_or_caption(*item)
        return
    plot_or_caption(*par)
