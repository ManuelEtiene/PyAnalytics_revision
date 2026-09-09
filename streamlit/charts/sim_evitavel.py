"""Gráficos de mortalidade evitável e desigualdades sociais."""

from __future__ import annotations

import pandas as pd

from charts.texto import insight_top, vazio
from charts.theme import (
    abrevia,
    bar_horizontal,
    bar_vertical,
    barras_agrupadas,
    barras_empilhadas,
    heatmap,
    histograma,
)
from data.constants import MAPA_ESC_CURTO, ORDEM_ESC, ORDEM_GRUPO_CAUSA, ROTULOS_FAIXAS_INFARTO


def raca_por_sexo(df: pd.DataFrame, periodo: str):
    """Óbitos por raça/cor e sexo."""
    base = df[~df["SEXO"].isin({"Ignorado"}) & ~df["RACACOR"].isin({"Ignorado"})]
    if base.empty:
        return vazio()
    tabela = pd.crosstab(base["RACACOR"], base["SEXO"])
    fig = barras_empilhadas(tabela, f"Óbitos por raça/cor e sexo — Araranguá, {periodo}")
    return fig, "Composição demográfica dos óbitos no município."


def distribuicao_idade(df: pd.DataFrame, periodo: str):
    """Histograma de idade ao óbito."""
    vals = df["IDADE_ANOS"].dropna()
    if vals.empty:
        return vazio("Sem idade preenchida.")
    fig = histograma(vals, f"Distribuição de óbitos por idade — Araranguá, {periodo}", nbins=20)
    return fig, f"{len(vals)} óbitos com idade válida. Concentração em idades avançadas é esperada."


def grupos_causa(df: pd.DataFrame, periodo: str):
    """Volume de óbitos por grupo CID-10."""
    serie = df["GRUPO_CAUSA"].value_counts()
    if serie.empty:
        return vazio()
    fig = bar_horizontal(serie, f"Óbitos por grupo de causas — Araranguá, {periodo}")
    return fig, insight_top(serie, "Circulatório e neoplasias costumam liderar.")


def top_causas(df: pd.DataFrame, periodo: str):
    """Top 5 causas específicas (descrição CID)."""
    serie = df["CAUSABAS_DESC"].value_counts().head(5)
    if serie.empty:
        return vazio()
    serie.index = [abrevia(i, 45) for i in serie.index]
    fig = bar_horizontal(serie, f"Principais causas específicas — Araranguá, {periodo}")
    return fig, insight_top(serie)


def heatmap_raca_esc(df: pd.DataFrame, periodo: str):
    """% do total: raça/cor × escolaridade."""
    base = df[(df["ESC2010"] != "Ignorado") & (df["RACACOR"] != "Ignorado")]
    if base.empty:
        return vazio("Sem raça e escolaridade preenchidas.")
    tabela = pd.crosstab(base["RACACOR"], base["ESC2010"], normalize="all") * 100
    tabela = tabela.reindex(columns=[c for c in ORDEM_ESC if c in tabela.columns])
    tabela.columns = [MAPA_ESC_CURTO.get(c, c) for c in tabela.columns]
    tabela.index.name = "RACACOR"
    tabela.columns.name = "ESC2010"
    fig = heatmap(
        tabela.round(1),
        f"Raça/cor × escolaridade (% do total) — Araranguá, {periodo}",
    )
    return fig, "Células escuras mostram onde se concentra o volume de óbitos."


def heatmap_causa_esc(df: pd.DataFrame, periodo: str):
    """% dentro do grupo de causa × escolaridade."""
    base = df[df["ESC2010"] != "Ignorado"]
    if base.empty:
        return vazio("Sem escolaridade preenchida.")
    tabela = pd.crosstab(base["GRUPO_CAUSA"], base["ESC2010"], normalize="index") * 100
    tabela = tabela.reindex(columns=[c for c in ORDEM_ESC if c in tabela.columns])
    ordem = [g for g in ORDEM_GRUPO_CAUSA if g in tabela.index]
    tabela = tabela.reindex(ordem)
    tabela.columns = [MAPA_ESC_CURTO.get(c, c) for c in tabela.columns]
    tabela.index.name = "GRUPO_CAUSA"
    tabela.columns.name = "ESC2010"
    fig = heatmap(
        tabela.round(1),
        f"Grupo de causa × escolaridade (% na causa) — Araranguá, {periodo}",
        "YlGnBu",
    )
    return fig, "Cada linha soma ~100%: perfil educacional dentro daquela causa."


def infarto_sexo(df: pd.DataFrame, periodo: str):
    """Óbitos por infarto segundo o sexo."""
    base = _infarto(df)
    if base.empty:
        return vazio("Sem óbitos por infarto no recorte.")
    serie = base["SEXO"].value_counts()
    fig = bar_vertical(serie, f"Infarto por sexo — Araranguá, {periodo}")
    return fig, insight_top(serie)


def infarto_faixa(df: pd.DataFrame, periodo: str):
    """Óbitos por infarto segundo a faixa etária."""
    base = _infarto(df).dropna(subset=["FAIXA_INFARTO"])
    if base.empty:
        return vazio("Sem óbitos por infarto com idade.")
    serie = base["FAIXA_INFARTO"].value_counts().reindex(ROTULOS_FAIXAS_INFARTO, fill_value=0)
    fig = bar_vertical(serie, f"Infarto por faixa etária — Araranguá, {periodo}", mostrar_pct=False)
    return fig, insight_top(serie)


def taxas_territorio(taxas: pd.DataFrame, periodo: str):
    """Taxas anuais por 100 mil: Araranguá × Criciúma × SC."""
    if taxas.empty:
        return vazio()
    ordem = [g for g in ORDEM_GRUPO_CAUSA if g in taxas.index]
    tabela = taxas.reindex(ordem).fillna(0)
    fig = barras_agrupadas(
        tabela,
        f"Média anual por 100 mil hab. — Ara × Criciúma × SC, {periodo}",
        horizontal=True,
    )
    return fig, "Normalização pela população do Censo 2022 (IBGE)."


def _infarto(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra óbitos cuja causa básica é infarto (I21…)."""
    cid = df["CAUSABAS"].astype(str).str.upper()
    return df.loc[cid.str.startswith("I21", na=False)].copy()
