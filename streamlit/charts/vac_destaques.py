"""Gráficos: vacinas em destaque nas aplicações."""

from __future__ import annotations

import pandas as pd

from charts.theme import pizza
from charts.texto import insight_top
from charts.vac_common import com_data, ranking_barras, serie_mensal_grupo, linhas_por_grupo


def ranking_vacinas(df: pd.DataFrame, periodo: str, n: int = 12):
    """Ranking das vacinas mais aplicadas."""
    col = _col_vacina(df)
    return ranking_barras(df, col, f"Vacinas com mais aplicações — {periodo}", n=n)


def concentracao(df: pd.DataFrame, periodo: str):
    """Participação das principais vacinas no total."""
    col = _col_vacina(df)
    serie = com_data(df)[col].value_counts()
    fig = pizza(serie, f"Concentração das aplicações por vacina — {periodo}", top=6)
    return fig, insight_top(serie)


def ranking_por_estrategia(df: pd.DataFrame, periodo: str):
    """Top vacinas dentro da estratégia mais frequente."""
    base = com_data(df)
    col = _col_vacina(base)
    lider = base["estrategia"].value_counts().idxmax()
    parte = base.loc[base["estrategia"] == lider]
    return ranking_barras(
        parte,
        col,
        f"Top vacinas na estratégia “{lider}” — {periodo}",
        n=8,
    )


def evolucao_lideres(df: pd.DataFrame, periodo: str, n: int = 5):
    """Evolução mensal das vacinas líderes."""
    col = _col_vacina(df)
    tab = serie_mensal_grupo(df, col, top=n)
    return linhas_por_grupo(
        tab,
        col,
        f"Evolução dos imunizantes líderes — {periodo}",
        "Vacina",
    )


def _col_vacina(df: pd.DataFrame) -> str:
    """Prefere o nome curto quando existir."""
    return "vacina_curta" if "vacina_curta" in df.columns else "nome_da_vacina"
