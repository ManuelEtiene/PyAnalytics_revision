"""Gráficos de perfil (ano, mês, idade, sexo, raça, escolaridade, local, causas)."""

from __future__ import annotations

import pandas as pd

from charts.theme import TERTIARY, abrevia, bar_horizontal, bar_vertical
from data.constants import MAPA_ESC_CURTO, MAPA_LOCAL_CURTO, NOMES_MESES, ROTULOS_FAIXAS


def obitos_por_ano(df: pd.DataFrame, periodo: str):
    """Série histórica anual com linha de média."""
    serie = df["ANO_OBITO"].value_counts().sort_index()
    fig = bar_vertical(serie, f"Óbitos por ano — Araranguá, {periodo}", False)
    media = float(serie.mean()) if len(serie) else 0
    fig.add_hline(y=media, line_dash="dash", line_color=TERTIARY,
                  annotation_text=f"Média ({media:.0f})")
    pico, n = (serie.idxmax(), int(serie.max())) if len(serie) else ("—", 0)
    pct = 100 * n / serie.sum() if len(serie) else 0
    insight = (
        f"O ano com mais óbitos foi {int(pico)} ({n} óbitos, {pct:.1f}% do período). "
        f"A média é de {media:.0f} óbitos/ano."
    )
    return fig, insight


def media_por_mes(df: pd.DataFrame, periodo: str):
    """Média de óbitos em cada mês do calendário."""
    validos = df.dropna(subset=["ANO_OBITO", "MES_OBITO"])
    tabela = validos.groupby(["ANO_OBITO", "MES_OBITO"]).size().unstack("MES_OBITO")
    media = tabela.mean(axis=0, skipna=True).reindex(range(1, 13))
    media.index = list(NOMES_MESES)
    fig = bar_vertical(media.fillna(0), f"Média de óbitos por mês do ano — Araranguá, {periodo}", False)
    pico, baixo = media.idxmax(), media.idxmin()
    insight = (
        f"Em média, {pico} concentra o maior número ({media.max():.1f}/ano) e "
        f"{baixo} o menor ({media.min():.1f}). Inverno no topo é compatível com "
        "maior mortalidade cardiovascular e respiratória."
    )
    return fig, insight


def obitos_por_faixa(df: pd.DataFrame, periodo: str):
    """Distribuição por faixa etária."""
    serie = df["FAIXA_ETARIA"].value_counts().reindex(ROTULOS_FAIXAS).fillna(0)
    fig = bar_vertical(serie, f"Óbitos por faixa etária — Araranguá, {periodo}")
    top = serie.idxmax()
    insight = (
        f"A faixa \"{top}\" concentra {int(serie.max())} óbitos "
        f"({100 * serie.max() / serie.sum():.1f}%). "
        "Faixas jovens podem indicar causas evitáveis."
    )
    return fig, insight


def obitos_por_sexo(df: pd.DataFrame, periodo: str):
    """Óbitos por sexo (exclui Ignorado, como no notebook)."""
    serie = _sem_ignorado(df, "SEXO").value_counts()
    fig = bar_vertical(serie, f"Óbitos por sexo — Araranguá, {periodo}")
    top = serie.idxmax()
    insight = (
        f"{top} concentra {100 * serie.max() / serie.sum():.1f}% dos óbitos "
        f"({int(serie.max())} de {int(serie.sum())}). Predomínio masculino é comum "
        "por causas externas e cardiovasculares mais cedo."
    )
    return fig, insight


def obitos_por_raca(df: pd.DataFrame, periodo: str):
    """Óbitos por raça/cor (exclui Ignorado)."""
    serie = _sem_ignorado(df, "RACACOR").value_counts()
    fig = bar_vertical(serie, f"Óbitos por raça/cor — Araranguá, {periodo}")
    top = serie.idxmax()
    insight = (
        f"\"{top}\" concentra {100 * serie.max() / serie.sum():.1f}% dos óbitos. "
        "O preenchimento na Declaração de Óbito pode subestimar Parda ou Indígena."
    )
    return fig, insight


def obitos_por_escolaridade(df: pd.DataFrame, periodo: str):
    """Óbitos por escolaridade, com rótulos curtos (exclui Ignorado)."""
    serie = _sem_ignorado(df, "ESC2010").value_counts()
    curtos = serie.rename(index=lambda c: MAPA_ESC_CURTO.get(c, c))
    fig = bar_vertical(curtos, f"Óbitos por escolaridade — Araranguá, {periodo}")
    top = serie.idxmax()
    insight = (
        f"A categoria mais frequente foi \"{top}\" ({int(serie.max())} óbitos, "
        f"{100 * serie.max() / serie.sum():.1f}%). Reflete em parte gerações "
        "mais velhas, com menos acesso à escola."
    )
    return fig, insight


def obitos_por_local(df: pd.DataFrame, periodo: str):
    """Óbitos por local de ocorrência (exclui Ignorado)."""
    serie = _sem_ignorado(df, "LOCOCOR").value_counts()
    curtos = serie.rename(index=lambda c: MAPA_LOCAL_CURTO.get(c, c))
    fig = bar_horizontal(curtos, f"Óbitos por local de ocorrência — Araranguá, {periodo}")
    top = serie.idxmax()
    insight = (
        f"\"{top}\" concentra {100 * serie.max() / serie.sum():.1f}% "
        f"({int(serie.max())}). Muitos óbitos hospitalares sugerem acesso à rede; "
        "domicílio ou via pública pedem atenção."
    )
    return fig, insight


def top_causas(df: pd.DataFrame, periodo: str):
    """Top 10 causas básicas de óbito."""
    serie = df["CAUSABAS_DESC"].value_counts().head(10)
    rotulos = serie.rename(index=lambda c: abrevia(c))
    fig = bar_horizontal(rotulos, f"Principais causas de óbito (top 10) — Araranguá, {periodo}")
    insight = (
        f"\"{serie.index[0]}\" é a causa mais frequente "
        f"({100 * serie.iloc[0] / df['CAUSABAS_DESC'].value_counts().sum():.1f}%, "
        f"{int(serie.iloc[0])} casos). Causas cardiovasculares no topo são típicas "
        "da transição epidemiológica brasileira."
    )
    return fig, insight


def _sem_ignorado(df: pd.DataFrame, col: str) -> pd.Series:
    """Série sem Ignorado, como no notebook."""
    return df.loc[~df[col].isin({"Ignorado"}), col]
