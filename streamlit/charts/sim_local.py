"""Gráficos de óbitos por local — ordem do notebook Sprint 1."""

from __future__ import annotations

import pandas as pd

from charts.texto import insight_top, vazio
from charts.theme import (
    MUTED,
    PRIMARY,
    SECONDARY,
    TERTIARY,
    bar_horizontal,
    bar_vertical,
    barras_agrupadas,
    barras_empilhadas,
    bolhas_geo,
    boxplot,
)
from data.constants import (
    MAPA_LOCAL_CURTO,
    ORDEM_ASSIST,
    ORDEM_LOCAIS_BOX,
    POP_CENSO_2022,
)


def proporcao_sc(sc: pd.DataFrame, periodo: str):
    """1. Proporção de óbitos por local em Santa Catarina."""
    contagem = sc["LOCOCOR"].value_counts().rename(index=_curto)
    fig = bar_horizontal(_pct(contagem), f"Proporção de óbitos por local — SC, {periodo}", False)
    return fig, insight_top(contagem, "Inclui registros com local ignorado.")


def idade_por_local_sc(sc: pd.DataFrame, periodo: str):
    """2. Boxplot de idade por local (SC)."""
    grupos = _idades_por_local(sc, ORDEM_LOCAIS_BOX)
    if not grupos:
        return vazio()
    fig = boxplot(grupos, f"Distribuição de idade por local — SC, {periodo}")
    return fig, "Via pública tende a idades mais jovens; hospital, a faixas mais altas."


def assistmed_sc(sc: pd.DataFrame, periodo: str):
    """3. Assistência médica empilhada por local (SC)."""
    tabela = _assist_por_local(sc)
    if tabela.empty:
        return vazio()
    fig = barras_empilhadas(
        tabela, f"Assistência médica prévia por local — SC, {periodo}",
        horizontal=True, cores=_cores_assist(tabela),
    )
    return fig, "Hospital concentra assistência confirmada; via pública, o contrário."


def mapa_ocorrencia(sc: pd.DataFrame, periodo: str):
    """4. Bolhas por município de ocorrência."""
    geo = (
        sc.dropna(subset=["lat", "lon"])
        .groupby(["nome", "lat", "lon"], as_index=False)
        .size()
        .rename(columns={"size": "obitos"})
        .sort_values("obitos", ascending=False)
    )
    if geo.empty:
        return vazio("Sem coordenadas para o mapa de ocorrência.")
    fig = bolhas_geo(geo, f"Óbitos por município de ocorrência — SC, {periodo}")
    top = geo.iloc[0]
    return fig, f"{top['nome']} lidera o volume ({int(top['obitos'])} óbitos)."


def causas_por_ambiente(sc: pd.DataFrame, periodo: str):
    """5. Capítulos CID-10 nos principais ambientes."""
    base = sc[(sc["ANO_OBITO"] >= 1996) & sc["CAUSA_GRUPO"].notna()]
    base = base[base["CAUSA_GRUPO"] != "Pré-CID10 (até 1995)"]
    top = base["CAUSA_GRUPO"].value_counts().head(7).index
    locais = ["Hospital", "Domicilio", "Via publica"]
    tabela = pd.crosstab(base["LOCOCOR"], base["CAUSA_GRUPO"], normalize="index") * 100
    tabela = tabela.reindex(locais)[list(top)].fillna(0)
    tabela["Outras"] = 100 - tabela.sum(axis=1)
    tabela.index = [_curto(i) for i in tabela.index]
    fig = barras_empilhadas(tabela, f"Principais causas por ambiente — SC, {periodo}", True)
    return fig, "Circulatório pesa no hospital; causas externas, na via pública."


def comparativo_local(ara, tub, sc, periodo: str):
    """6. Proporção por local: Araranguá × Tubarão × SC."""
    tabela = pd.concat(
        [_pct_local(ara).rename("Araranguá"),
         _pct_local(tub).rename("Tubarão"),
         _pct_local(sc).rename("SC (total)")],
        axis=1,
    ).fillna(0)
    tabela.index = [_curto(i) for i in tabela.index]
    fig = barras_agrupadas(tabela, f"Local de ocorrência — Araranguá × Tubarão × SC, {periodo}", True)
    return fig, insight_top(ara["LOCOCOR"].value_counts().rename(index=_curto), "Compare com Tubarão e com o estado.")


def idade_ara_vs_sc(ara, sc, periodo: str):
    """7. Idade em hospital, domicílio e via pública (Ara vs SC)."""
    pares = []
    for local in ("Hospital", "Domicilio", "Via publica"):
        grupos = {
            f"Araranguá · {_curto(local)}": _idades(ara, local),
            f"SC · {_curto(local)}": _idades(sc, local),
        }
        grupos = {k: v for k, v in grupos.items() if len(v)}
        if grupos:
            fig = boxplot(grupos, f"Idade no óbito — {_curto(local)} · {periodo}")
            pares.append((fig, f"Medianas de Araranguá e SC neste ambiente ({_curto(local)})."))
    return pares or [vazio()]


def assistmed_comparativo(ara, tub, sc, periodo: str):
    """8. Assistência médica: Araranguá × Tubarão × SC."""
    tabela = pd.concat(
        [_pct_assist(ara).rename("Araranguá"),
         _pct_assist(tub).rename("Tubarão"),
         _pct_assist(sc).rename("SC (total)")],
        axis=1,
    ).reindex(ORDEM_ASSIST).fillna(0)
    fig = barras_empilhadas(tabela.T, f"Assistência médica — Araranguá × Tubarão × SC, {periodo}", cores=_cores_assist(tabela.T))
    return fig, insight_top(ara["ASSISTMED"].value_counts(), "Valores do gráfico estão em % de cada recorte.")


def taxa_populacao(ara, tub, sc, periodo: str):
    """9. Média anual de óbitos por 100 mil hab. (Censo 2022)."""
    anos = max(int(sc["ANO_OBITO"].max() - sc["ANO_OBITO"].min()) + 1, 1)
    obitos = pd.Series({"Araranguá": len(ara), "Tubarão": len(tub), "SC (total)": len(sc)})
    pop = pd.Series(POP_CENSO_2022)
    taxa = (obitos / anos / pop * 100_000).round(1)
    fig = bar_vertical(taxa, f"Óbitos/100 mil hab./ano — Araranguá × Tubarão × SC, {periodo}", False)
    return fig, "Normalização pelo Censo 2022; número bruto favorece cidades maiores."


def _pct_local(df: pd.DataFrame) -> pd.Series:
    """Percentual por LOCOCOR, rótulo curto."""
    return _pct(df["LOCOCOR"].value_counts(dropna=True).rename(index=_curto))


def _pct(serie: pd.Series) -> pd.Series:
    """Converte contagem em percentual com 1 casa."""
    return (serie / serie.sum() * 100).round(1)


def _pct_assist(df: pd.DataFrame) -> pd.Series:
    """Percentual de ASSISTMED no recorte."""
    return (df["ASSISTMED"].value_counts(normalize=True) * 100).round(1)


def _assist_por_local(df: pd.DataFrame) -> pd.DataFrame:
    """Proporção de assistência dentro de cada local."""
    locais = ["Hospital", "Outros estabelecimentos de saude", "Domicilio", "Outros", "Via publica"]
    tabela = pd.crosstab(df["LOCOCOR"], df["ASSISTMED"], normalize="index") * 100
    cols = [c for c in ORDEM_ASSIST if c in tabela.columns]
    tabela = tabela.reindex(locais)[cols].fillna(0)
    tabela.index = [_curto(i) for i in tabela.index]
    return tabela


def _idades_por_local(df: pd.DataFrame, locais) -> dict:
    """Idades válidas (0–120) por local, com n no rótulo."""
    grupos = {}
    for local in locais:
        vals = _idades(df, local)
        if len(vals):
            grupos[f"{_curto(local)} (n={len(vals)})"] = vals
    return grupos


def _idades(df: pd.DataFrame, local: str):
    """Idades de um local, sem outliers absurdos."""
    vals = df.loc[df["LOCOCOR"] == local, "IDADE_ANOS"].dropna()
    return vals[(vals >= 0) & (vals <= 120)]


def _curto(nome) -> str:
    """Rótulo curto de local."""
    return MAPA_LOCAL_CURTO.get(nome, str(nome))


def _cores_assist(tabela) -> list:
    """Cores do notebook para Sim / Não / Ignorado / Não informado."""
    mapa = {"Sim": PRIMARY, "Não": TERTIARY, "Ignorado": SECONDARY, "Não informado": MUTED}
    return [mapa.get(col, PRIMARY) for col in tabela.columns]
