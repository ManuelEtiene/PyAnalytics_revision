"""Ranking de municípios de SC (absoluto e por 10 mil hab.)."""

from __future__ import annotations

import pandas as pd

from data.constants import COD_ARARANGUA
from data.decode import decodifica_municipio
from data.load_sim import load_contagem_municipios
from data.lookups import mapa_municipios, mapa_populacao


def serie_absoluta(ano_min: int, ano_max: int) -> pd.Series:
    """Óbitos por nome de município, ordem decrescente."""
    brutos = load_contagem_municipios(ano_min, ano_max)
    mun = mapa_municipios()
    nomes = {cod: decodifica_municipio(cod, mun) for cod in brutos}
    return pd.Series(brutos).rename(index=nomes).sort_values(ascending=False)


def serie_taxa(ano_min: int, ano_max: int) -> pd.Series:
    """Taxa média anual de óbitos por 10 mil habitantes (IBGE 2021)."""
    brutos = load_contagem_municipios(ano_min, ano_max)
    pop = mapa_populacao()
    anos = max(ano_max - ano_min + 1, 1)
    taxas = {}
    for cod, obitos in brutos.items():
        habitantes = pop.get(str(cod).zfill(6))
        if habitantes and habitantes > 0:
            taxas[cod] = (obitos / anos) / habitantes * 10000
    mun = mapa_municipios()
    nomes = {cod: decodifica_municipio(cod, mun) for cod in taxas}
    return pd.Series(taxas).rename(index=nomes).sort_values(ascending=False)


def nome_ararangua() -> str:
    """Nome de Araranguá segundo a tabela IBGE."""
    return decodifica_municipio(COD_ARARANGUA, mapa_municipios())


def posicao(serie: pd.Series, nome: str) -> int | None:
    """Posição 1-based do município na série ordenada."""
    if nome not in serie.index:
        return None
    return list(serie.index).index(nome) + 1
