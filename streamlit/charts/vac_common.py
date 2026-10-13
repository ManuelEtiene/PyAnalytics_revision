"""Helpers compartilhados dos gráficos de vacinas."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from charts.texto import insight_top, vazio
from charts.theme import PALETTE, PRIMARY, abrevia, apply_layout, bar_horizontal


def com_data(df: pd.DataFrame) -> pd.DataFrame:
    """Só registros com data de aplicação válida."""
    return df.dropna(subset=["data_aplicacao"]).copy()


def mensal_contagem(df: pd.DataFrame) -> pd.DataFrame:
    """Aplicações por mês (rótulo MM/AAAA), com variação %."""
    base = com_data(df)
    if base.empty:
        return pd.DataFrame(columns=["mes_label", "aplicacoes", "variacao_pct"])
    mensal = (
        base.groupby(["mes_periodo", "mes_label"], as_index=False)
        .size()
        .rename(columns={"size": "aplicacoes"})
        .sort_values("mes_periodo")
    )
    mensal["variacao_pct"] = mensal["aplicacoes"].pct_change() * 100
    return mensal


def serie_mensal_grupo(df: pd.DataFrame, coluna: str, top: int = 5) -> pd.DataFrame:
    """Tabela mês × categoria (top-N) com contagens."""
    base = com_data(df)
    tops = base[coluna].value_counts().head(top).index
    tab = (
        base.loc[base[coluna].isin(tops)]
        .groupby(["mes_label", "mes_periodo", coluna])
        .size()
        .reset_index(name="aplicacoes")
        .sort_values("mes_periodo")
    )
    return tab


def linha_mensal_geral(mensal: pd.DataFrame, titulo: str):
    """Linha única do volume mensal com anotações de %."""
    if mensal.empty:
        return vazio()
    fig = go.Figure(
        go.Scatter(
            x=mensal["mes_label"],
            y=mensal["aplicacoes"],
            mode="lines+markers+text",
            text=_textos_variacao(mensal["variacao_pct"]),
            textposition="top center",
            line=dict(color=PRIMARY, width=3),
            marker=dict(size=9),
            name="Aplicações",
        )
    )
    fig.update_yaxes(title="Número de aplicações", rangemode="tozero")
    fig.update_xaxes(title="Mês")
    pico = mensal.loc[mensal["aplicacoes"].idxmax()]
    insight = (
        f"Pico em {pico['mes_label']} ({int(pico['aplicacoes']):,} aplicações)."
        .replace(",", ".")
    )
    return apply_layout(fig, titulo), insight


def linhas_por_grupo(tab: pd.DataFrame, coluna: str, titulo: str, legenda: str):
    """Várias linhas mensais (uma por categoria)."""
    if tab.empty:
        return vazio()
    fig = go.Figure()
    grupos = tab.groupby(coluna)["aplicacoes"].sum().sort_values(ascending=False).index
    for i, nome in enumerate(grupos):
        parte = tab.loc[tab[coluna] == nome].sort_values("mes_periodo")
        fig.add_scatter(
            x=parte["mes_label"],
            y=parte["aplicacoes"],
            mode="lines+markers",
            name=abrevia(str(nome), 28),
            line=dict(color=PALETTE[i % len(PALETTE)], width=2),
        )
    meses = (
        tab[["mes_periodo", "mes_label"]]
        .drop_duplicates()
        .sort_values("mes_periodo")["mes_label"]
        .tolist()
    )
    fig.update_yaxes(title="Número de aplicações", rangemode="tozero")
    fig.update_xaxes(title="Mês", categoryorder="array", categoryarray=meses)
    fig.update_layout(legend_title_text=legenda)
    totais = tab.groupby(coluna)["aplicacoes"].sum().sort_values(ascending=False)
    return apply_layout(fig, titulo), insight_top(totais)


def ranking_barras(df: pd.DataFrame, coluna: str, titulo: str, n: int = 10):
    """Barras horizontais do ranking de aplicações."""
    serie = com_data(df)[coluna].value_counts().head(n)
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, titulo)
    fig.update_xaxes(title="Número de aplicações")
    return fig, insight_top(serie)


def _textos_variacao(serie: pd.Series) -> list[str]:
    """Rótulos +X% / -X% (ignora inf e NaN)."""
    textos = []
    for v in serie:
        if pd.isna(v) or not np.isfinite(v):
            textos.append("")
        else:
            textos.append(f"{v:+.0f}%")
    return textos
