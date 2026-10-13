"""Gráficos: lotes e prazos de validade."""

from __future__ import annotations

import pandas as pd

from charts.theme import PRIMARY, apply_layout, bar_horizontal, histograma
from charts.texto import insight_top, vazio
from charts.vac_common import com_data


def diversidade_lotes_vacina(df: pd.DataFrame, periodo: str, n: int = 12):
    """Quantidade de lotes distintos por vacina."""
    base = com_data(df).dropna(subset=["lote"])
    serie = base.groupby("nome_da_vacina")["lote"].nunique().sort_values(ascending=False).head(n)
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, f"Diversidade de lotes por vacina — {periodo}", mostrar_pct=False)
    fig.update_xaxes(title="Lotes distintos")
    return fig, insight_top(serie)


def diversidade_lotes_bairro(df: pd.DataFrame, periodo: str, n: int = 12):
    """Quantidade de lotes distintos por bairro da pessoa vacinada."""
    base = com_data(df).dropna(subset=["lote"])
    serie = base.groupby("bairro")["lote"].nunique().sort_values(ascending=False).head(n)
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, f"Diversidade de lotes por bairro — {periodo}", mostrar_pct=False)
    fig.update_xaxes(title="Lotes distintos")
    return fig, insight_top(serie)


def prazo_restante(df: pd.DataFrame, periodo: str):
    """Distribuição do prazo restante (dias) na data da aplicação."""
    base = com_data(df).dropna(subset=["prazo_restante_dias"])
    # remove negativos extremos / absurdos
    vals = base.loc[base["prazo_restante_dias"].between(0, 2000), "prazo_restante_dias"]
    if vals.empty:
        return vazio()
    fig = histograma(vals, f"Prazo restante do lote na aplicação (dias) — {periodo}", nbins=30)
    fig.update_xaxes(title="Dias até a validade")
    fig.update_yaxes(title="Número de aplicações")
    med = float(vals.median())
    return apply_layout(fig, fig.layout.title.text), f"Mediana do prazo restante: {med:.0f} dias."


def lotes_mais_usados(df: pd.DataFrame, periodo: str, n: int = 10):
    """Lotes com mais aplicações (código do lote)."""
    base = com_data(df).dropna(subset=["lote"])
    serie = base["lote"].value_counts().head(n)
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, f"Lotes com mais aplicações — {periodo}")
    fig.update_xaxes(title="Número de aplicações")
    return fig, insight_top(serie)
