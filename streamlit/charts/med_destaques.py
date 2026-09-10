"""Gráficos: medicamentos em destaque na dispensação."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from charts.texto import insight_top, vazio
from charts.theme import PALETTE, abrevia, apply_layout, bar_horizontal, dispersao, heatmap
from data.prepare_med import meses_completos

_CLASSES_SAZON = (
    "Antibióticos e antimicrobianos",
    "Analgésicos e antitérmicos",
    "Sistema respiratório",
    "Saúde mental e neurologia",
    "Doenças cardiovasculares",
)


def top_saidas(df: pd.DataFrame, periodo: str):
    """Top 20 medicamentos por número de saídas."""
    serie = df["material_nome_base"].value_counts().head(20)
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 40) for i in serie.index]
    fig = bar_horizontal(serie, f"Top 20 medicamentos por saídas — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie)


def top_quantidade(df: pd.DataFrame, periodo: str):
    """Top 20 medicamentos por quantidade total."""
    serie = (
        df.groupby("material_nome_base")["quantidade"].sum().sort_values(ascending=False).head(20)
    )
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 40) for i in serie.index]
    fig = bar_horizontal(
        serie, f"Top 20 medicamentos por quantidade — {periodo}", mostrar_pct=False
    )
    return fig, insight_top(serie, "Volume alto ≠ mais saídas (protocolos longos).")


def comparacao_rankings(df: pd.DataFrame, periodo: str):
    """Dispersão: ranking de saídas × ranking de quantidade (top 20 por saídas)."""
    saidas = df["material_nome_base"].value_counts().rename("saidas")
    qtd = df.groupby("material_nome_base")["quantidade"].sum().rename("quantidade")
    base = (
        pd.concat([saidas, qtd], axis=1)
        .dropna()
        .assign(
            rank_saidas=lambda d: d["saidas"].rank(ascending=False, method="min"),
            rank_quantidade=lambda d: d["quantidade"].rank(ascending=False, method="min"),
        )
        .sort_values("rank_saidas")
        .head(20)
    )
    if base.empty:
        return vazio()
    fig = dispersao(
        base["rank_saidas"],
        base["rank_quantidade"],
        f"Ranking saídas × quantidade (top 20 saídas) — {periodo}",
        "Posição em saídas (1 = mais)",
        "Posição em quantidade (1 = mais)",
    )
    return fig, "Pontos longe da diagonal: frequente em pouca quantidade ou o contrário."


def evolucao_top5(df: pd.DataFrame, periodo: str):
    """Linhas mensais dos 5 medicamentos com mais saídas."""
    base = meses_completos(df)
    top5 = base["material_nome_base"].value_counts().head(5).index
    evolucao = (
        base.loc[base["material_nome_base"].isin(top5)]
        .groupby(["ano_mes", "material_nome_base"])
        .size()
        .reset_index(name="saidas")
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


def tipos_apresentacao(df: pd.DataFrame, periodo: str):
    """Tipos de apresentação (comprimido, frasco etc.)."""
    if "material_tipo" not in df.columns:
        return vazio("Sem coluna de tipo de apresentação.")
    serie = df["material_tipo"].fillna("Não informado").value_counts().head(15)
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 40) for i in serie.index]
    fig = bar_horizontal(serie, f"Tipos de apresentação — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie)


def top_apresentacoes(df: pd.DataFrame, periodo: str):
    """Top 20 apresentações completas (nome + dose + tipo)."""
    serie = df["apresentacao_completa"].value_counts().head(20)
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 48) for i in serie.index]
    fig = bar_horizontal(serie, f"Top 20 apresentações completas — {periodo}", mostrar_pct=False)
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
    """Média de quantidade por saída — universo = top 20 por saídas."""
    top20 = df["material_nome_base"].value_counts().head(20).index
    media = (
        df.loc[df["material_nome_base"].isin(top20)]
        .groupby("material_nome_base")["quantidade"]
        .mean()
        .sort_values(ascending=False)
        .round(1)
    )
    if media.empty:
        return vazio()
    media.index = [abrevia(i, 40) for i in media.index]
    fig = bar_horizontal(
        media, f"Média de quantidade por saída — Top 20 por saídas · {periodo}", mostrar_pct=False
    )
    return fig, insight_top(media, "Protocolos longos elevam a média por atendimento.")


def top_meds_por_bairro(df: pd.DataFrame, periodo: str):
    """Heatmap: top 5 medicamentos nos 10 bairros com mais saídas."""
    base = df.loc[~df["bairro_malformado"]]
    bairros = base["bairro_padronizado"].value_counts().head(10).index
    recorte = base.loc[base["bairro_padronizado"].isin(bairros)]
    if recorte.empty:
        return vazio()
    ranking = (
        recorte.groupby(["bairro_padronizado", "material_nome_base"])
        .size()
        .reset_index(name="saidas")
        .sort_values(["bairro_padronizado", "saidas"], ascending=[True, False])
        .groupby("bairro_padronizado", group_keys=False)
        .head(5)
    )
    pivot = ranking.pivot_table(
        index="bairro_padronizado",
        columns="material_nome_base",
        values="saidas",
        fill_value=0,
    )
    pivot = pivot.loc[:, (pivot > 0).any()]
    pivot.columns = [abrevia(c, 18) for c in pivot.columns]
    pivot.index.name = "bairro"
    pivot.columns.name = "medicamento"
    fig = heatmap(
        pivot,
        f"Top medicamentos por bairro (saídas) — {periodo}",
        "YlGnBu",
        cor_legenda="Saídas",
    )
    return fig, "Cada bairro mostra só seus 5 líderes (células zeradas = fora do top)."


def sazonalidade_tipo(df: pd.DataFrame, periodo: str):
    """Evolução mensal por tipo de tratamento (lista preferida do notebook)."""
    base = meses_completos(df).dropna(subset=["tipo_tratamento"])
    if base.empty:
        return vazio("Sem tipo de tratamento preenchido.")
    existentes = [c for c in _CLASSES_SAZON if c in set(base["tipo_tratamento"])]
    if not existentes:
        existentes = base["tipo_tratamento"].value_counts().head(5).index.tolist()
    pivot = (
        base.loc[base["tipo_tratamento"].isin(existentes)]
        .groupby(["ano_mes", "tipo_tratamento"])
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
