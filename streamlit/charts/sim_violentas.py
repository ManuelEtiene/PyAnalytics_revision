"""Gráficos de mortes violentas — ordem do notebook Sprint 1."""

from __future__ import annotations

import pandas as pd

from charts.texto import insight_top, vazio
from charts.theme import PRIMARY, TERTIARY, bar_horizontal, bar_vertical, barras_empilhadas, boxplot
from data.constants import MAPA_LOCAL_CURTO, ORDEM_ASSIST, POP_ARARANGUA_VIOLENTAS
from data.prepare_sim_violentas import ranking_taxa_sc


def volume_por_local(df: pd.DataFrame, periodo: str):
    """Volume de mortes violentas por local de ocorrência."""
    serie = df["LOCOCOR"].value_counts().rename(index=_curto)
    fig = bar_vertical(serie, f"Mortes violentas por local — Araranguá, {periodo}")
    return fig, insight_top(serie)


def idade_por_local(df: pd.DataFrame, periodo: str):
    """Boxplot de idade por local."""
    grupos = {}
    for local, bloco in df.groupby("LOCOCOR"):
        idades = bloco["IDADE_ANOS"].dropna()
        if len(idades):
            grupos[_curto(local)] = idades
    if not grupos:
        return vazio()
    fig = boxplot(grupos, f"Idade por local de óbito — Araranguá, {periodo}")
    return fig, "Ambientes públicos costumam concentrar vítimas mais jovens."


def assistmed_por_local(df: pd.DataFrame, periodo: str):
    """Proporção de assistência médica por local."""
    tabela = pd.crosstab(df["LOCOCOR"], df["ASSISTMED"], normalize="index") * 100
    cols = [c for c in ORDEM_ASSIST if c in tabela.columns]
    tabela = tabela[cols]
    tabela.index = [_curto(i) for i in tabela.index]
    fig = barras_empilhadas(tabela, f"Assistência médica por local — Araranguá, {periodo}", True)
    return fig, "Via pública e domicílio concentram ausência de amparo médico."


def taxa_sc(periodo: str):
    """Taxa por 100 mil hab. em SC, com Araranguá destacada."""
    taxas = ranking_taxa_sc()
    if taxas.empty:
        return vazio("Sem população de referência para a taxa estadual.")
    nome = "Araranguá"
    vizinhos = _janela(taxas, nome)
    cores = [TERTIARY if m == nome else PRIMARY for m in vizinhos.index]
    fig = bar_horizontal(vizinhos.round(1), f"Taxa de mortes violentas/100 mil hab. — SC, {periodo}", False, cores)
    return fig, _insight_taxa(taxas, nome)


def top_causas_por_local(df: pd.DataFrame, periodo: str) -> list:
    """Um gráfico de top 10 causas para cada local (ordem do notebook)."""
    pares = []
    for local in df["LOCOCOR"].dropna().unique():
        serie = df.loc[df["LOCOCOR"] == local, "CAUSA_DESC"].value_counts().head(10)
        if serie.empty:
            continue
        fig = bar_horizontal(serie, f"Top 10 causas — {_curto(local)} (Araranguá, {periodo})")
        pares.append((fig, insight_top(serie, f"Ambiente: {_curto(local)}.")))
    return pares or [vazio()]


def volume_por_tipo(df: pd.DataFrame, periodo: str):
    """Acidentes, homicídios, suicídios e outros."""
    serie = df["TIPO_VIOLENCIA"].value_counts()
    fig = bar_vertical(serie, f"Mortes violentas por tipo — Araranguá, {periodo}")
    return fig, insight_top(serie, "Acidentes costumam superar a violência interpessoal.")


def acidentes_por_local(df: pd.DataFrame, periodo: str):
    """Acidentes fatais por local."""
    return _tipo_por_local(df, "Acidente", periodo)


def homicidios_por_local(df: pd.DataFrame, periodo: str):
    """Homicídios por local."""
    return _tipo_por_local(df, "Homicídio", periodo)


def top_acidentes(df: pd.DataFrame, periodo: str):
    """Top 10 causas de acidentes fatais."""
    return _top_tipo(df, "Acidente", periodo)


def top_homicidios(df: pd.DataFrame, periodo: str):
    """Top 10 causas de homicídios."""
    return _top_tipo(df, "Homicídio", periodo)


def _tipo_por_local(df: pd.DataFrame, tipo: str, periodo: str):
    """Barras de um tipo de violência por local."""
    bloco = df[df["TIPO_VIOLENCIA"] == tipo]
    if bloco.empty:
        return vazio(f"Nenhum registro de {tipo.lower()} no recorte.")
    serie = bloco["LOCOCOR"].value_counts().rename(index=_curto)
    fig = bar_vertical(serie, f"{tipo}s por local — Araranguá, {periodo}")
    return fig, insight_top(serie)


def _top_tipo(df: pd.DataFrame, tipo: str, periodo: str):
    """Top 10 causas de um tipo."""
    bloco = df[df["TIPO_VIOLENCIA"] == tipo]
    if bloco.empty:
        return vazio(f"Nenhum registro de {tipo.lower()} no recorte.")
    serie = bloco["CAUSA_DESC"].value_counts().head(10)
    fig = bar_horizontal(serie, f"Top 10 causas de {tipo.lower()}s — Araranguá, {periodo}")
    return fig, insight_top(serie)


def _janela(taxas: pd.Series, nome: str, raio: int = 10) -> pd.Series:
    """Fatia do ranking em torno do município."""
    if nome not in taxas.index:
        return taxas.head(21)
    idx = list(taxas.index).index(nome)
    return taxas.iloc[max(0, idx - raio): idx + raio + 1]


def _insight_taxa(taxas: pd.Series, nome: str) -> str:
    """Posição de Araranguá no ranking estadual."""
    if nome not in taxas.index:
        return "Araranguá não entrou no ranking (faltou população de referência)."
    lugar = list(taxas.index).index(nome) + 1
    return (
        f"Araranguá está na {lugar}ª posição de {len(taxas)} municípios "
        f"({taxas.loc[nome]:.1f} por 100 mil hab.)."
    )


def _curto(nome) -> str:
    """Rótulo curto de local."""
    return MAPA_LOCAL_CURTO.get(nome, str(nome))
