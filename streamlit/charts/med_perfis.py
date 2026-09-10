"""Gráficos: perfis de cuidado na farmácia básica."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from charts.texto import insight_top, vazio
from charts.theme import PALETTE, abrevia, apply_layout, bar_horizontal, pizza
from data.med_perfis_map import PERFIL_OUTROS
from data.prepare_med import meses_completos


def volume_por_perfil(df: pd.DataFrame, periodo: str):
    """Barras horizontais — volume por perfil de cuidado."""
    serie = df["perfil_cuidado"].value_counts().sort_values(ascending=True)
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, f"Medicamentos por perfil de cuidado — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie.sort_values(ascending=False))


def perfis_menos_frequentes(df: pd.DataFrame, periodo: str):
    """Mesmos perfis sem a categoria residual."""
    serie = (
        df.loc[df["perfil_cuidado"] != PERFIL_OUTROS, "perfil_cuidado"]
        .value_counts()
        .sort_values(ascending=True)
    )
    if serie.empty:
        return vazio()
    fig = bar_horizontal(
        serie, f"Perfis (sem “Outros”) — {periodo}", mostrar_pct=False
    )
    return fig, "Linhas menores respondem a demandas sazonais ou pontuais."


def participacao_pizza(df: pd.DataFrame, periodo: str):
    """Participação percentual dos perfis (top 8 + residual)."""
    serie = df["perfil_cuidado"].value_counts()
    if serie.empty:
        return vazio()
    fig = pizza(serie, f"Participação por perfil de cuidado — {periodo}", top=8)
    lider = serie.index[0]
    pct = 100 * serie.iloc[0] / serie.sum()
    return fig, f'"{lider}" responde por {pct:.1f}% das dispensações.'


def top10_medicamentos(df: pd.DataFrame, periodo: str):
    """Top 10 medicamentos (rótulo até o hífen)."""
    serie = df["material_nome"].fillna("").value_counts().head(10)
    if serie.empty:
        return vazio()
    serie.index = [abrevia(str(i).split("-")[0].strip(), 40) for i in serie.index]
    fig = bar_horizontal(serie, f"Top 10 medicamentos — {periodo}", mostrar_pct=False)
    return fig, insight_top(serie)


def evolucao_mensal_perfis(df: pd.DataFrame, periodo: str):
    """Linhas mensais por perfil (meses completos)."""
    base = meses_completos(df)
    if base.empty:
        return vazio()
    pivot = (
        base.groupby(["ano_mes", "perfil_cuidado"]).size().unstack(fill_value=0).sort_index()
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
    fig = apply_layout(fig, f"Evolução mensal por perfil — {periodo}")
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="center", x=0.5),
        margin=dict(l=8, r=8, t=56, b=100),
    )
    return fig, "Crônicos tendem a curvas estáveis; respiratório oscila mais."


def top5_por_perfil(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela: top 5 medicamentos em cada perfil."""
    base = df.copy()
    base["med"] = base["material_nome"].fillna("").astype(str)
    tabela = (
        base.groupby(["perfil_cuidado", "med"])
        .size()
        .reset_index(name="saidas")
        .sort_values(["perfil_cuidado", "saidas"], ascending=[True, False])
        .groupby("perfil_cuidado", group_keys=False)
        .head(5)
    )
    tabela["med"] = tabela["med"].str.split("-").str[0].str.strip()
    return tabela.rename(
        columns={"perfil_cuidado": "Perfil", "med": "Medicamento", "saidas": "Saídas"}
    )
