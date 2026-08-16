"""Tema Plotly alinhado à paleta de Araranguá."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

PRIMARY = "#0059bb"
SECONDARY = "#fdc003"
TERTIARY = "#b6152e"
MUTED = "#717786"
PALETTE = [PRIMARY, TERTIARY, SECONDARY, "#004493", "#d93343", "#fabd00"]

_TEXTO_CLARO = "#191c1d"
_TEXTO_ESCURO = "#e8eaed"
_GRADE_CLARA = "#e1e3e4"
_GRADE_ESCURA = "#2c333d"


def _escuro() -> bool:
    """Indica se o portal está no tema escuro."""
    return bool(st.session_state.get("tema_escuro"))


def apply_layout(fig: go.Figure, title: str) -> go.Figure:
    """Aplica fundo limpo, fonte Inter e título."""
    texto = _TEXTO_ESCURO if _escuro() else _TEXTO_CLARO
    grade = _GRADE_ESCURA if _escuro() else _GRADE_CLARA
    fig.update_layout(
        title=title,
        font=dict(family="Inter, sans-serif", color=texto, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=56, b=8),
        title_font=dict(family="Hanken Grotesk, sans-serif", size=18, color=texto),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=texto)),
        coloraxis_colorbar=dict(tickfont=dict(color=texto), title_font=dict(color=texto)),
    )
    fig.update_xaxes(showgrid=False, color=texto, tickfont=dict(color=texto))
    fig.update_yaxes(gridcolor=grade, zeroline=False, color=texto, tickfont=dict(color=texto))
    return fig


def adaptar_tema(fig: go.Figure) -> go.Figure:
    """Ajusta cores do gráfico ao tema atual (claro/escuro)."""
    if not _escuro():
        return fig
    texto = _TEXTO_ESCURO
    grade = _GRADE_ESCURA
    fig.update_layout(
        font=dict(color=texto),
        title_font=dict(color=texto),
        legend=dict(font=dict(color=texto)),
        coloraxis_colorbar=dict(tickfont=dict(color=texto), title_font=dict(color=texto)),
    )
    fig.update_xaxes(color=texto, tickfont=dict(color=texto), title_font=dict(color=texto))
    fig.update_yaxes(color=texto, tickfont=dict(color=texto), gridcolor=grade, title_font=dict(color=texto))
    fig.update_annotations(font=dict(color=texto))
    fig.update_traces(textfont=dict(color=texto), selector=dict(type="bar"))
    fig.update_traces(textfont=dict(color=texto), selector=dict(type="heatmap"))
    return fig


def rotulo(valor: float, total: float, mostrar_pct: bool) -> str:
    """Texto da barra: n ou n (pct%)."""
    if mostrar_pct and total:
        return f"{int(valor)} ({100 * valor / total:.1f}%)"
    return f"{int(valor)}" if valor == int(valor) else f"{valor:.1f}"


def bar_vertical(serie, title: str, mostrar_pct: bool = True, color: str = PRIMARY):
    """Gráfico de barras verticais com rótulo."""
    total = float(serie.sum()) if len(serie) else 0
    textos = [rotulo(v, total, mostrar_pct) for v in serie.values]
    fig = go.Figure(
        go.Bar(
            x=[str(i) for i in serie.index],
            y=list(serie.values),
            text=textos,
            textposition="outside",
            marker_color=color,
            cliponaxis=False,
        )
    )
    return apply_layout(fig, title)


def bar_horizontal(serie, title: str, mostrar_pct: bool = True, cores=None):
    """Gráfico de barras horizontais (maior no topo)."""
    total = float(serie.sum()) if len(serie) else 0
    textos = [rotulo(v, total, mostrar_pct) for v in serie.values]
    fig = go.Figure(
        go.Bar(
            y=[str(i) for i in serie.index],
            x=list(serie.values),
            orientation="h",
            text=textos,
            textposition="outside",
            marker_color=cores or PRIMARY,
            cliponaxis=False,
        )
    )
    fig.update_yaxes(autorange="reversed")
    return apply_layout(fig, title)


def heatmap(tabela, title: str, escala: str = "Blues") -> go.Figure:
    """Heatmap com valores nas células."""
    fig = px.imshow(
        tabela,
        color_continuous_scale=escala,
        aspect="auto",
        text_auto=True,
    )
    fig.update_traces(texttemplate="%{z:.0f}")
    return apply_layout(fig, title)


def abrevia(texto: str, tamanho: int = 35) -> str:
    """Corta rótulos longos para caber no eixo."""
    texto = str(texto)
    if len(texto) <= tamanho:
        return texto
    return texto[: tamanho - 1].rstrip() + "…"
