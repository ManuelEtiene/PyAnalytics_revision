"""Gráficos: medicamentos em destaque na dispensação."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from charts.texto import insight_top, vazio
from charts.theme import PALETTE, abrevia, apply_layout, bar_horizontal


def top_saidas(df: pd.DataFrame, periodo: str):
    """Top 15 medicamentos por número de saídas."""
    serie = df["material_nome_base"].value_counts().head(15)
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 40) for i in serie.index]
    fig = bar_horizontal(serie, f"Top 15 medicamentos por saídas — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie)


def evolucao_top5(df: pd.DataFrame, periodo: str):
    """Linhas mensais dos 5 medicamentos com mais saídas."""
    top5 = df["material_nome_base"].value_counts().head(5).index
    base = df.loc[df["material_nome_base"].isin(top5)]
    evolucao = (
        base.groupby(["ano_mes", "material_nome_base"]).size().reset_index(name="saidas")
    )
    if evolucao.empty:
        return vazio()
    fig = go.Figure()
    for i, med in enumerate(top5):
        dados = evolucao.loc[evolucao["material_nome_base"] == med].sort_values("ano_mes")
        fig.add_scatter(
            x=dados["ano_mes"],
            y=dados["saidas"],
            mode="lines+markers",
            name=abrevia(str(med), 28),
            line=dict(color=PALETTE[i % len(PALETTE)]),
        )
    fig = apply_layout(fig, f"Evolução mensal — Top 5 medicamentos · {periodo}")
    return fig, "Compare a estabilidade dos itens crônicos ao longo do ano."


def tipos_tratamento(df: pd.DataFrame, periodo: str):
    """Volume por tipo de tratamento."""
    serie = df["tipo_tratamento"].fillna("Não informado").value_counts().head(12)
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 40) for i in serie.index]
    fig = bar_horizontal(serie, f"Tipos de tratamento — {periodo}")
    return fig, insight_top(serie)


def top_bairros_saidas(df: pd.DataFrame, periodo: str):
    """Top 15 bairros por número de saídas."""
    base = df.loc[~df["bairro_malformado"]]
    serie = base["bairro_padronizado"].value_counts().head(15)
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, f"Top 15 bairros por saídas — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie)


def media_quantidade(df: pd.DataFrame, periodo: str):
    """Média de quantidade por saída — Top 20 medicamentos."""
    media = (
        df.groupby("material_nome_base")["quantidade"]
        .mean()
        .sort_values(ascending=False)
        .head(20)
    )
    if media.empty:
        return vazio()
    media.index = [abrevia(i, 40) for i in media.index]
    fig = bar_horizontal(media, f"Média de quantidade por saída — Top 20 · {periodo}", mostrar_pct=False)
    return fig, insight_top(media, "Protocolos longos elevam a média por atendimento.")


def sazonalidade_tipo(df: pd.DataFrame, periodo: str):
    """Evolução mensal por tipo de tratamento."""
    base = df.dropna(subset=["tipo_tratamento"]).copy()
    if base.empty:
        return vazio("Sem tipo de tratamento preenchido.")
    pivot = (
        base.groupby(["ano_mes", "tipo_tratamento"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    fig = go.Figure()
    for i, col in enumerate(pivot.columns):
        fig.add_scatter(
            x=pivot.index.astype(str),
            y=pivot[col],
            mode="lines+markers",
            name=abrevia(str(col), 28),
            line=dict(color=PALETTE[i % len(PALETTE)], width=1.8),
            marker=dict(size=5),
        )
    fig = apply_layout(fig, f"Sazonalidade por tipo de tratamento — {periodo}")
    return fig, "Condições crônicas tendem a curvas mais estáveis."
