"""Gráficos territoriais: ranking SC e município de ocorrência."""

from __future__ import annotations

import pandas as pd

from charts.theme import PRIMARY, TERTIARY, bar_horizontal
from data.ranking import nome_ararangua, posicao, serie_absoluta, serie_taxa


def ranking_absoluto(ano_min: int, ano_max: int, periodo: str):
    """Top 15 municípios de SC por número de óbitos."""
    ranking = serie_absoluta(ano_min, ano_max)
    top = ranking.head(15)
    if top.empty:
        return None, "Sem dados para o ranking estadual.", ranking
    nome = nome_ararangua()
    cores = [TERTIARY if m == nome else PRIMARY for m in top.index]
    fig = bar_horizontal(
        top, f"Top 15 municípios de SC por óbitos — {periodo}", False, cores
    )
    lugar = posicao(ranking, nome)
    insight = _insight_ranking(lugar, len(ranking))
    return fig, insight, ranking


def _insight_ranking(lugar: int | None, total: int) -> str:
    """Texto do ranking absoluto."""
    if lugar is None:
        return "Araranguá não foi localizada no ranking absoluto de SC."
    return (
        f"Araranguá está na {lugar}ª posição de {total} municípios "
        "em número absoluto. Cidades maiores sobem no ranking só por população."
    )


def ranking_taxa(ano_min: int, ano_max: int, periodo: str):
    """Top 15 por taxa de óbitos / 10 mil hab. / ano."""
    taxas = serie_taxa(ano_min, ano_max)
    top = taxas.head(15)
    if top.empty:
        return None, "Sem população de referência para calcular a taxa."
    nome = nome_ararangua()
    cores = [TERTIARY if m == nome else PRIMARY for m in top.index]
    fig = bar_horizontal(
        top.round(1),
        f"Top 15 SC — óbitos/10 mil hab./ano — {periodo}",
        False,
        cores,
    )
    lugar = posicao(taxas, nome)
    valor = float(taxas.loc[nome]) if nome in taxas.index else 0.0
    return fig, _insight_taxa(lugar, valor)


def _insight_taxa(lugar: int | None, valor: float) -> str:
    """Texto do ranking por 10 mil habitantes."""
    if lugar is None:
        return "Araranguá não foi localizada no ranking normalizado por população."
    return (
        f"Normalizado pela população (IBGE 2021), Araranguá vai para a "
        f"{lugar}ª posição ({valor:.1f} óbitos/10 mil hab./ano)."
    )


def ocorrencia_por_municipio(df: pd.DataFrame, periodo: str):
    """Onde morreram os residentes de Araranguá."""
    serie = df["CODMUNOCOR_NOME"].value_counts().head(10)
    fig = bar_horizontal(
        serie, f"Óbitos de residentes de Araranguá por município de ocorrência — {periodo}"
    )
    n_fora = int(df["OCORREU_FORA_RESIDENCIA"].sum())
    pct = 100 * n_fora / len(df) if len(df) else 0
    insight = (
        f"{n_fora} de {len(df)} óbitos ({pct:.1f}%) ocorreram em outro município, "
        "em geral por deslocamento para hospital de maior complexidade."
    )
    return fig, insight
