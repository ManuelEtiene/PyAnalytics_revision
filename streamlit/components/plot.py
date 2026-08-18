"""Exibe gráfico Plotly + insight curto."""

import streamlit as st

from charts.theme import adaptar_tema, tema_plotly


def plot(fig, insight: str | None = None) -> None:
    """Renderiza o gráfico em largura total, sem barra de ferramentas."""
    fig = adaptar_tema(fig)
    st.plotly_chart(
        fig,
        width="stretch",
        theme=tema_plotly(fig),
        config={"displayModeBar": False},
    )
    if insight:
        st.caption(insight)


def plot_or_caption(fig, insight: str | None = None) -> None:
    """Mostra o gráfico ou só o recado, se não houver figura."""
    if fig is None:
        st.caption(insight or "Sem dados para este gráfico.")
        return
    plot(fig, insight)
