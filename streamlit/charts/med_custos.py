"""Gráficos: custos sobre as dispensações."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from charts.texto import insight_top, vazio
from charts.theme import (
    PRIMARY,
    TERTIARY,
    abrevia,
    apply_layout,
    bar_horizontal,
    dispersao,
)


def evolucao_mensal(df: pd.DataFrame, periodo: str):
    """Barras de custo + linha de quantidade por mês."""
    mensal = (
        df.groupby("ano_mes")
        .agg(custo_total=("custo_total", "sum"), quantidade_total=("quantidade", "sum"))
        .reset_index()
        .sort_values("ano_mes")
    )
    if mensal.empty:
        return vazio()
    fig = go.Figure()
    fig.add_bar(
        x=mensal["ano_mes"],
        y=mensal["custo_total"] / 1e3,
        name="Custo (R$ mil)",
        marker_color=PRIMARY,
        opacity=0.75,
    )
    fig.add_scatter(
        x=mensal["ano_mes"],
        y=mensal["quantidade_total"] / 1e3,
        name="Qtd (mil un.)",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color=TERTIARY, width=2),
    )
    fig.update_layout(
        yaxis=dict(title="Custo (R$ mil)"),
        yaxis2=dict(title="Quantidade (mil)", overlaying="y", side="right"),
    )
    fig = apply_layout(fig, f"Evolução mensal — custo e quantidade · {periodo}")
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5),
        margin=dict(l=8, r=56, t=56, b=72),
        yaxis2=dict(title="Quantidade (mil)", overlaying="y", side="right"),
    )
    return fig, "Custo e volume tendem a caminhar juntos ao longo dos meses."


def top_custo(df: pd.DataFrame, periodo: str):
    """Top 10 medicamentos por custo total."""
    serie = _agg_med(df).sort_values("custo_total", ascending=False).head(10)
    if serie.empty:
        return vazio()
    plot = serie.set_index("material_nome_base")["custo_total"]
    plot.index = [abrevia(i, 40) for i in plot.index]
    fig = bar_horizontal(plot, f"Top 10 medicamentos por custo — {periodo}", mostrar_pct=False)
    return fig, insight_top(plot, "Concentração do orçamento em poucos itens.")


def quantidade_vs_custo(df: pd.DataFrame, periodo: str):
    """Dispersão quantidade × custo por medicamento."""
    base = _agg_med(df)
    if base.empty:
        return vazio()
    fig = dispersao(
        base["quantidade_total"] / 1e3,
        base["custo_total"] / 1e3,
        f"Quantidade × custo por medicamento — {periodo}",
        "Quantidade (mil un.)",
        "Custo (R$ mil)",
    )
    r = base["quantidade_total"].corr(base["custo_total"])
    return fig, f"Correlação linear volume×custo: r = {r:.2f} (valores próximos de 0 = pouco ligados)."


def top_fabricantes(df: pd.DataFrame, periodo: str):
    """Top 5 fabricantes por custo."""
    serie = (
        df.groupby("fabricante_nome")["custo_total"].sum().sort_values(ascending=False).head(5)
    )
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, f"Top 5 fabricantes por custo — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie)


def top_classes(df: pd.DataFrame, periodo: str):
    """Top 5 classes terapêuticas por custo."""
    serie = (
        df.groupby("classe_terapeutica")["custo_total"].sum().sort_values(ascending=False).head(5)
    )
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 40) for i in serie.index]
    fig = bar_horizontal(serie, f"Top 5 classes terapêuticas por custo — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie, "Terapias contínuas puxam o orçamento.")


def _agg_med(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega custo e quantidade por medicamento base."""
    return (
        df.groupby("material_nome_base", as_index=False)
        .agg(custo_total=("custo_total", "sum"), quantidade_total=("quantidade", "sum"))
    )
