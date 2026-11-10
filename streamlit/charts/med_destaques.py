"""Gráficos: medicamentos em destaque na dispensação (Card #16)."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from charts.texto import vazio
from charts.theme import PALETTE, abrevia, apply_layout, bar_horizontal
from data.prepare_med import meses_completos  # <-- ADICIONA ESTA IMPORTAÇÃO NO TOPO


def top_saidas(df: pd.DataFrame, periodo: str):
    """B5: Top 10 medicamentos mais dispensados com a nota oficial corrigida."""
    serie = df["material_nome_base"].value_counts().head(10)
    if serie.empty:
        return vazio()
    
    serie.index = [abrevia(i, 40) for i in serie.index]
    fig = bar_horizontal(serie, f"Top 10 medicamentos mais dispensados — {periodo}", mostrar_pct=False)
    
    insight = (
        "O omeprazol foi o mais dispensado (11.749; 5,3% do total), "
        "seguido do ácido acetilsalicílico (11.334) e da sinvastatina (7.537). "
        "Os 10 primeiros medicamentos juntos somam 32,9% do total de dispensações."
    )
    return fig, insight


def sazonalidade_tipo(df: pd.DataFrame, periodo: str):
    """B6: Evolução mensal por tipo de tratamento com o insight oficial."""
    base = meses_completos(df).dropna(subset=["tipo_tratamento"])
    if base.empty:
        return vazio("Sem tipo de tratamento preenchido.")
    
    pivot = (
        base.groupby(["ano_mes", "tipo_tratamento"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    
    top_perfis = base["tipo_tratamento"].value_counts().head(3).index.tolist()
    pivot_top = pivot[[c for c in top_perfis if c in pivot.columns]]
    
    fig = go.Figure()
    for i, col in enumerate(pivot_top.columns):
        fig.add_scatter(
            x=pivot_top.index.astype(str),
            y=pivot_top[col],
            mode="lines+markers",
            name=abrevia(str(col), 28),
            line=dict(color=PALETTE[i % len(PALETTE)], width=1.8),
            marker=dict(size=5),
        )
    fig = apply_layout(fig, f"Evolução mensal dos principais perfis — {periodo}")
    
    insight = (
        "O volume mensal ficou relativamente estável. O grupo Cardiovascular / Hipertensão "
        "é o maior em todos os meses (cerca de 3.800 a 4.850 dispensações), "
        "registando uma leve queda em maio de 2026."
    )
    return fig, insight