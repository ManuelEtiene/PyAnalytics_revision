"""Gráficos: origem do registro da aplicação."""

from __future__ import annotations

import pandas as pd

from charts.theme import heatmap
from charts.texto import insight_top, vazio
from charts.vac_common import (
    com_data,
    linhas_por_grupo,
    ranking_barras,
    serie_mensal_grupo,
)


def ranking_origem(df: pd.DataFrame, periodo: str):
    """Volume por origem do registro."""
    return ranking_barras(df, "origem", f"Origem do registro — {periodo}", n=8)


def evolucao_origem(df: pd.DataFrame, periodo: str):
    """Origens ao longo do tempo."""
    tab = serie_mensal_grupo(df, "origem", top=5)
    return linhas_por_grupo(
        tab, "origem", f"Origem do registro no tempo — {periodo}", "Origem"
    )


def origem_por_bairro(df: pd.DataFrame, periodo: str, n_bairros: int = 8):
    """Heatmap bairro × origem (top bairros da pessoa vacinada)."""
    base = com_data(df)
    tops = base["bairro"].value_counts().head(n_bairros).index
    tab = (
        base.loc[base["bairro"].isin(tops)]
        .pivot_table(
            index="bairro",
            columns="origem",
            values="data_aplicacao",
            aggfunc="count",
            fill_value=0,
        )
    )
    if tab.empty:
        return vazio()
    tab = tab.loc[tab.sum(axis=1).sort_values(ascending=False).index]
    tab.index.name = "Bairro"
    tab.columns.name = "Origem"
    fig = heatmap(tab, f"Bairro × origem do registro — {periodo}", cor_legenda="Aplicações")
    return fig, insight_top(base["origem"].value_counts())
