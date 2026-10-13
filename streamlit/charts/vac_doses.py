"""Gráficos: tipos de dose e andamento."""

from __future__ import annotations

import pandas as pd

from charts.vac_common import (
    com_data,
    linhas_por_grupo,
    ranking_barras,
    serie_mensal_grupo,
)


def ranking_dose_texto(df: pd.DataFrame, periodo: str, n: int = 12):
    """Textos de dose exatamente como na base."""
    return ranking_barras(
        df, "dose", f"Textos de dose mais frequentes — {periodo}", n=n
    )


def ranking_dose_grupo(df: pd.DataFrame, periodo: str):
    """Categorias agrupadas (única, 1ª, 2ª, reforço…)."""
    return ranking_barras(
        df, "dose_grupo", f"Categorias de dose (agrupadas) — {periodo}", n=10
    )


def evolucao_dose_grupo(df: pd.DataFrame, periodo: str, n: int = 5):
    """Evolução mensal das principais categorias de dose."""
    tab = serie_mensal_grupo(df, "dose_grupo", top=n)
    return linhas_por_grupo(
        tab,
        "dose_grupo",
        f"Categorias de dose no tempo — {periodo}",
        "Dose",
    )


def dose_por_vacina_lider(df: pd.DataFrame, periodo: str):
    """Distribuição de dose na vacina mais aplicada."""
    base = com_data(df)
    lider = base["nome_da_vacina"].value_counts().idxmax()
    parte = base.loc[base["nome_da_vacina"] == lider]
    return ranking_barras(
        parte,
        "dose_grupo",
        f"Doses da vacina líder (“{lider}”) — {periodo}",
        n=8,
    )
