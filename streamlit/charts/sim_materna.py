"""Gráficos de saúde materna e infantil — ordem do notebook Sprint 1."""

from __future__ import annotations

import pandas as pd

from charts.texto import insight_top, vazio
from charts.theme import (
    bar_vertical,
    barras_agrupadas,
    dispersao,
    heatmap,
    histograma,
    histograma_hue,
    linha,
)


def idade_infantil(df: pd.DataFrame):
    """Distribuição da idade em anos (exclui 0)."""
    vals = df.loc[df["IDADE_ANOS"] != 0, "IDADE_ANOS"].dropna()
    return histograma(vals, "Distribuição da idade (anos)"), _n(vals, "óbitos infantis com idade > 0.")


def primeiros_meses(df: pd.DataFrame):
    """Óbitos no primeiro ano de vida."""
    serie = df.loc[df["IDADE_ANOS"] < 1, "IDADE_ANOS"].value_counts().sort_index()
    if serie.empty:
        return vazio("Sem óbitos com menos de 1 ano para o recorte.")
    return linha(serie, "Primeiro ano de vida"), "Concentração no início da vida indica risco neonatal."


def peso_vs_gestacao_inf(df: pd.DataFrame):
    """Peso ao nascer × semanas (menores de 1 ano)."""
    return _dispersao_menor_um(df, "PESO", "Peso (g)", "Semanas × peso ao nascer")


def idade_vs_gestacao_inf(df: pd.DataFrame):
    """Idade × semanas (menores de 1 ano)."""
    return _dispersao_menor_um(df, "IDADE_ANOS", "Idade (anos)", "Semanas × idade")


def idade_infantil_completa(df: pd.DataFrame):
    """Histograma de idade incluindo o ano 0."""
    vals = df["IDADE_ANOS"].dropna()
    return histograma(vals, "Distribuição da idade (anos)"), _n(vals, "óbitos infantis.")


def idade_mae(df: pd.DataFrame):
    """Contagem por idade da mãe."""
    serie = df["IDADEMAE"].value_counts().sort_index()
    if serie.empty:
        return vazio("Sem idade da mãe preenchida.")
    return linha(serie, "Contagem por idade da mãe"), insight_top(serie)


def semanas_gestacao(df: pd.DataFrame):
    """Histograma de semanas gestacionais."""
    vals = df["SEMAGESTAC"].dropna()
    return histograma(vals, "Semanas de gestação"), _n(vals, "registros com semana preenchida.")


def idade_por_sexo(df: pd.DataFrame):
    """Idade da criança por sexo."""
    base = df.dropna(subset=["IDADE_ANOS", "SEXO"])
    if base.empty:
        return vazio()
    fig = histograma_hue(base, "IDADE_ANOS", "SEXO", "Distribuição de idade por sexo")
    return fig, "Compare o volume entre sexos em cada faixa de idade."


def semanas_por_parto(df: pd.DataFrame):
    """Semanas de gestação por tipo de parto."""
    base = df.dropna(subset=["SEMAGESTAC", "PARTO"])
    if base.empty:
        return vazio()
    fig = histograma_hue(base, "SEMAGESTAC", "PARTO", "Semanas de gestação por tipo de parto")
    return fig, "Prematuridade aparece à esquerda do gráfico."


def parto_vs_momento(df: pd.DataFrame):
    """Tipo de parto × momento do óbito."""
    return _cruzado(df, "PARTO", "OBITOPARTO", "Tipo de parto × momento do óbito")


def heatmap_parto_peso(df: pd.DataFrame):
    """Parto × faixa de peso."""
    return _heatmap(df, "PARTO", "FAIXA_PESO", "Parto × faixa de peso")


def heatmap_parto_gravidez(df: pd.DataFrame):
    """Parto × tipo de gravidez."""
    return _heatmap(df, "PARTO", "GRAVIDEZ", "Parto × tipo de gravidez")


def momento_vs_parto(df: pd.DataFrame):
    """Momento do óbito × tipo de parto."""
    return _cruzado(df, "OBITOPARTO", "PARTO", "Óbito em relação ao parto vs. tipo de parto")


def gravidez_vs_parto(df: pd.DataFrame):
    """Tipo de gravidez × parto."""
    return _cruzado(df, "GRAVIDEZ", "PARTO", "Tipo de gravidez vs. tipo de parto")


def peso_por_momento(df: pd.DataFrame):
    """Peso ao nascer por momento do óbito."""
    return _hist_hue(df, "PESO", "OBITOPARTO", "Peso ao nascer por momento do óbito")


def peso_por_parto(df: pd.DataFrame):
    """Peso ao nascer por tipo de parto."""
    return _hist_hue(df, "PESO", "PARTO", "Peso ao nascer por tipo de parto")


def media_peso_gravidez(df: pd.DataFrame):
    """Média de peso por gravidez e momento do óbito."""
    tabela = df.groupby(["GRAVIDEZ", "OBITOPARTO"], observed=False)["PESO"].mean().unstack()
    if tabela is None or tabela.empty:
        return vazio()
    fig = barras_agrupadas(tabela.fillna(0), "Média de peso (g) por gravidez e momento do óbito")
    return fig, "Peso médio menor sugere prematuridade ou restrição de crescimento."


def momento_obito(df: pd.DataFrame):
    """Distribuição do momento do óbito."""
    return _contagem(df, "OBITOPARTO", "Distribuição do momento do óbito")


def gravidez_vs_gestacao(df: pd.DataFrame):
    """Tipo de gravidez × tempo de gestação (notebook)."""
    return _cruzado(df, "GRAVIDEZ", "GESTACAO", "Tipo de gravidez vs. tempo de gestação")


def tempo_gestacao(df: pd.DataFrame):
    """Tempo de gestação (faixas SIM)."""
    return _contagem(df, "GESTACAO", "Tempo de gestação")


def mae_vs_peso(df: pd.DataFrame):
    """Faixa de idade da mãe × faixa de peso."""
    return _cruzado(df, "FAIXA_IDADEMAE", "FAIXA_PESO", "Idade da mãe × faixa de peso")


def mae_vs_semanas(df: pd.DataFrame):
    """Faixa de idade da mãe × semanas."""
    return _cruzado(df, "FAIXA_IDADEMAE", "FAIXA_SEMAGESTAC", "Idade da mãe × semanas de gestação")


def escolaridade_mae(df: pd.DataFrame):
    """Escolaridade da mãe × faixa de peso."""
    return _cruzado(df, "ESCMAE2010", "FAIXA_PESO", "Escolaridade da mãe × faixa de peso")


def heatmap_tipo_assist(df: pd.DataFrame):
    """Tipo de óbito × assistência médica."""
    return _heatmap(df, "TIPOBITO", "ASSISTMED", "Tipo de óbito × assistência médica")


def assist_por_tipo(df: pd.DataFrame):
    """Assistência por tipo de óbito."""
    return _cruzado(df, "TIPOBITO", "ASSISTMED", "Assistência médica por tipo de óbito")


def assist_por_local(df: pd.DataFrame):
    """Assistência por local de ocorrência."""
    return _cruzado(df, "LOCOCOR", "ASSISTMED", "Assistência médica por local", True)


def idade_materna(df: pd.DataFrame):
    """Idade das mulheres no recorte materno."""
    vals = df["IDADE_ANOS"].dropna()
    return histograma(vals, "Distribuição da idade (óbitos maternos)"), _n(vals, "óbitos maternos.")


def idade_materna_linha(df: pd.DataFrame):
    """Série de idade materna."""
    serie = df["IDADE_ANOS"].value_counts().sort_index()
    if serie.empty:
        return vazio()
    return linha(serie, "Idade (óbitos maternos)"), insight_top(serie)


def _dispersao_menor_um(df, y: str, ylabel: str, title: str):
    """Dispersão só com menores de 1 ano."""
    return _dispersao(df[df["IDADE_ANOS"] < 1], "SEMAGESTAC", y, title, "Semana de gestação", ylabel)


def _dispersao(df, x: str, y: str, title: str, xlabel: str, ylabel: str):
    """Nuvem de pontos com duas colunas numéricas."""
    base = df.dropna(subset=[x, y])
    if base.empty:
        return vazio()
    fig = dispersao(base[x], base[y], title, xlabel, ylabel)
    return fig, f"{len(base)} registros com {xlabel.lower()} e {ylabel.lower()} preenchidos."


def _contagem(df, col: str, title: str):
    """Barras da frequência de uma coluna."""
    if col not in df.columns:
        return vazio()
    serie = df[col].value_counts()
    if serie.empty:
        return vazio()
    return bar_vertical(serie, title), insight_top(serie)


def _cruzado(df, x: str, hue: str, title: str, horizontal: bool = False):
    """Barras agrupadas a partir de duas colunas categóricas."""
    tabela = pd.crosstab(df[x], df[hue])
    if tabela.empty:
        return vazio()
    fig = barras_agrupadas(tabela, title, horizontal)
    return fig, insight_top(tabela.sum(axis=1))


def _heatmap(df, linhas: str, colunas: str, title: str):
    """Heatmap de contingência."""
    tabela = pd.crosstab(df[linhas], df[colunas])
    if tabela.empty:
        return vazio()
    return heatmap(tabela, title), "Células escuras indicam combinações mais frequentes."


def _hist_hue(df, x: str, hue: str, title: str):
    """Histograma colorido por categoria."""
    base = df.dropna(subset=[x, hue])
    if base.empty:
        return vazio()
    return histograma_hue(base, x, hue, title, 7), f"{len(base)} registros neste cruzamento."


def _n(vals, sufixo: str) -> str:
    """Insight com o tamanho da série."""
    if vals is None or len(vals) == 0:
        return "Sem dados para este gráfico."
    return f"{int(len(vals))} {sufixo}"
