"""Gráficos: estratégias de vacinação."""

from __future__ import annotations

import pandas as pd

from charts.theme import heatmap
from charts.texto import insight_top, vazio
from charts.vac_common import com_data, ranking_barras, serie_mensal_grupo, linhas_por_grupo


def ranking_estrategias(df: pd.DataFrame, periodo: str):
    """Frequência das estratégias na base."""
    return ranking_barras(df, "estrategia", f"Estratégias de vacinação — {periodo}", n=12)


def evolucao_estrategias(df: pd.DataFrame, periodo: str, n: int = 4):
    """Estratégias principais no tempo."""
    tab = serie_mensal_grupo(df, "estrategia", top=n)
    return linhas_por_grupo(
        tab,
        "estrategia",
        f"Estratégias ao longo do tempo — {periodo}",
        "Estratégia",
    )


def cruzamento_vacina_estrategia(df: pd.DataFrame, periodo: str, n_vac: int = 8):
    """Heatmap vacina × estratégia (top vacinas)."""
    base = com_data(df)
    tops = base["nome_da_vacina"].value_counts().head(n_vac).index
    tab = (
        base.loc[base["nome_da_vacina"].isin(tops)]
        .pivot_table(
            index="nome_da_vacina",
            columns="estrategia",
            values="data_aplicacao",
            aggfunc="count",
            fill_value=0,
        )
    )
    if tab.empty:
        return vazio()
    tab.index.name = "Vacina"
    tab.columns.name = "Estratégia"
    # ordena por volume
    tab = tab.loc[tab.sum(axis=1).sort_values(ascending=False).index]
    fig = heatmap(tab, f"Vacina × estratégia (top {n_vac}) — {periodo}", cor_legenda="Aplicações")
    return fig, insight_top(base["estrategia"].value_counts())


def estrategias_raras(df: pd.DataFrame, periodo: str, limiar: int = 50):
    """Estratégias com pouco volume (barras)."""
    serie = com_data(df)["estrategia"].value_counts()
    rara = serie[serie < limiar].sort_values(ascending=True)
    if rara.empty:
        return vazio("Não há estratégias abaixo do limiar.")
    from charts.theme import bar_horizontal

    fig = bar_horizontal(rara, f"Estratégias menos frequentes (< {limiar}) — {periodo}")
    fig.update_xaxes(title="Número de aplicações")
    return fig, f"{len(rara)} estratégia(s) com menos de {limiar} aplicações."
