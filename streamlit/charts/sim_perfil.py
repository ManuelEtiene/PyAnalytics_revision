"""Gráficos de perfil (ano, mês, idade, sexo, raça, escolaridade, local, causas)."""

from __future__ import annotations

import pandas as pd

from charts.theme import TERTIARY, abrevia, bar_horizontal, bar_vertical
from data.constants import MAPA_ESC_CURTO, MAPA_LOCAL_CURTO, NOMES_MESES, ROTULOS_FAIXAS


def obitos_por_ano(df: pd.DataFrame, periodo: str):
    """A1: Série histórica anual com linha de média e destaque pós-2020."""
    serie = df["ANO_OBITO"].value_counts().sort_index()
    fig = bar_vertical(serie, f"Óbitos por ano — Araranguá, {periodo}", False)
    media = float(serie.mean()) if len(serie) else 0
    fig.add_hline(y=media, line_dash="dash", line_color=TERTIARY,
                  annotation_text=f"Média ({media:.0f})")
    pico, n = (serie.idxmax(), int(serie.max())) if len(serie) else ("—", 0)
    
    insight = (
        f"Entre 1992 e 2025, Araranguá registrou de {int(serie.min())} a {n} mortes de moradores por ano. "
        f"Até 2019 ficou entre 267 e 424; desde 2020 subiu, com pico em 2021 ({n}), "
        "e de 2022 a 2025 ficou acima de 500 (com o crescimento e envelhecimento da população)."
    )
    return fig, insight


def media_por_mes(df: pd.DataFrame, periodo: str):
    """A2: Média de óbitos em cada mês do calendário (destacando inverno)."""
    validos = df.dropna(subset=["ANO_OBITO", "MES_OBITO"])
    tabela = validos.groupby(["ANO_OBITO", "MES_OBITO"]).size().unstack("MES_OBITO")
    media = tabela.mean(axis=0, skipna=True).reindex(range(1, 13))
    media.index = list(NOMES_MESES)
    fig = bar_vertical(media.fillna(0), f"Em média, quantas pessoas morrem em cada mês — Araranguá, {periodo}", False)
    insight = (
        "Morrem mais pessoas no inverno: julho tem em média 35,7 mortes, junho e agosto 33,5. "
        "Fevereiro tem o menor valor (27,2), mas é o mês mais curto."
    )
    return fig, insight


def obitos_por_faixa(df: pd.DataFrame, periodo: str):
    """A3: Distribuição por faixa etária com notas baseadas em factos."""
    serie = df["FAIXA_ETARIA"].value_counts().reindex(ROTULOS_FAIXAS).fillna(0)
    fig = bar_vertical(serie, f"Óbitos por faixa etária — Araranguá, {periodo}")
    insight = (
        "Seis em cada dez mortes (60,5%) ocorreram a partir dos 60 anos; a faixa de 70 a 79 concentra 21,0% (3.269). "
        "Bebês com menos de 1 ano somam 930 mortes (6,0%)."
    )
    return fig, insight


def obitos_por_sexo(df: pd.DataFrame, periodo: str):
    """A4: Óbitos por sexo."""
    serie = _sem_ignorado(df, "SEXO").value_counts()
    fig = bar_vertical(serie, f"Óbitos por sexo — Araranguá, {periodo}")
    insight = (
        "58,2% das mortes foram de homens (9.077) e 41,8% de mulheres (6.529): "
        "cerca de 14 homens para cada 10 mulheres."
    )
    return fig, insight


def obitos_por_raca(df: pd.DataFrame, periodo: str):
    """A5: Óbitos por raça/cor com nota explicativa sobre os informados."""
    serie = _sem_ignorado(df, "RACACOR").value_counts()
    fig = bar_vertical(serie, f"Óbitos por raça/cor — Araranguá, {periodo}")
    insight = (
        "Em 1 de cada 3 mortes (33,0%) a raça/cor não foi informada. Entre as com informação, "
        "a esmagadora maioria foi registada como branca, parda ou preta; "
        "note que esta distribuição reflete os registos e não a composição total da população."
    )
    return fig, insight


def obitos_por_escolaridade(df: pd.DataFrame, periodo: str):
    """A6: Óbitos por escolaridade ordenados corretamente e com nomes por extenso."""
    serie = _sem_ignorado(df, "ESC2010").value_counts()
    curtos = serie.rename(index=lambda c: MAPA_ESC_CURTO.get(c, c))
    
    # Ordem lógica de escolaridade (de menor para maior grau)
    ordem_desejada = [
        "Sem escolaridade",
        "Fundamental I (1ª a 4ª)",
        "Fundamental II (5ª a 8ª)",
        "Médio",
        "Superior"
    ]
    curtos = curtos.reindex([k for k in ordem_desejada if k in curtos.index]).fillna(0)
    
    fig = bar_vertical(curtos, f"Óbitos por escolaridade — Araranguá, {periodo}")
    insight = (
        "A escolaridade foi informada em só 1 de cada 3 mortes (33,8%). "
        "Entre elas, a maioria concentrou-se no ensino fundamental I, o que reflete em parte a menor escolaridade das gerações mais velhas."
    )
    return fig, insight


def obitos_por_local(df: pd.DataFrame, periodo: str):
    """A7: Local de ocorrência com clarificação de termos."""
    serie = _sem_ignorado(df, "LOCOCOR").value_counts()
    curtos = serie.rename(index=lambda c: MAPA_LOCAL_CURTO.get(c, c))
    fig = bar_horizontal(curtos, f"Local de ocorrência dos óbitos — Araranguá, {periodo}")
    insight = (
        "Sete em cada dez mortes (72,3%) ocorreram em hospital e duas em cada dez (20,7%) em casa; "
        "a via pública soma 3,7% e os outros estabelecimentos de saúde complementam o panorama."
    )
    return fig, insight


def top_causas(df: pd.DataFrame, periodo: str):
    """A8: Principais causas de óbito simplificadas."""
    serie = df["CAUSABAS_DESC"].value_counts().head(10)
    rotulos = serie.rename(index=lambda c: abrevia(c))
    fig = bar_horizontal(rotulos, f"Principais causas de óbito (top 10) — Araranguá, {periodo}")
    insight = (
        "A causa mais frequente foi o infarto (1.121 mortes, 7,2%), seguido do AVC (631; 4,0%) "
        "e da doença pulmonar obstrutiva crónica (442; 2,8%). Cerca de 6% das mortes têm causa desconhecida ou mal definida."
    )
    return fig, insight


def _sem_ignorado(df: pd.DataFrame, col: str) -> pd.Series:
    """Série sem Ignorado, como no notebook."""
    return df.loc[~df[col].isin({"Ignorado"}), col]