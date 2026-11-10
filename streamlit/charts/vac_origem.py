"""Gráficos: origem do registro da aplicação."""

from __future__ import annotations

import pandas as pd
import plotly.express as px

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
    """Gráfico de barras horizontais 100% empilhadas: Bairro × origem."""
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
    
    # Conversão para percentual (100% empilhado) por bairro
    tab_perc = tab.div(tab.sum(axis=1), axis=0) * 100
    df_plot = tab_perc.reset_index().melt(
        id_vars="bairro", var_name="Origem", value_name="Percentual"
    )
    
    fig = px.bar(
        df_plot,
        x="Percentual",
        y="bairro",
        color="Origem",
        orientation="h",
        title=f"Bairro × origem do registro (100% empilhado) — {periodo}",
        labels={"Percentual": "Participação (%)", "bairro": "Bairro", "Origem": "Origem"},
    )
    fig.update_layout(
        barmode="stack",
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Participação (%)",
        yaxis_title="Bairro",
    )
    
    return fig, insight_top(base["origem"].value_counts())