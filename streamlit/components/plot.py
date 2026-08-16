"""Exibe gráfico Plotly + insight curto."""

import streamlit as st

from charts.theme import adaptar_tema


def plot(fig, insight: str | None = None) -> None:
    """Renderiza o gráfico em largura total, sem barra de ferramentas."""
    st.plotly_chart(
        adaptar_tema(fig),
        width="stretch",
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
