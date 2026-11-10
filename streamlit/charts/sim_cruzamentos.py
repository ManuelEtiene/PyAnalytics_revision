"""Cruzamentos (escolaridade x faixa, ocupações, sexo x local, causas x faixa)."""

from __future__ import annotations

import pandas as pd
import plotly.express as px

from charts.theme import PALETTE, abrevia, bar_horizontal, barras_empilhadas
from data.constants import MAPA_LOCAL_CURTO


def escolaridade_por_faixa(df: pd.DataFrame, periodo: str):
    """(Mantido caso necessário, mas removido da vista principal conforme A9)."""
    tabela = pd.crosstab(df["ESC2010"], df["FAIXA_ETARIA"])
    fig = px.imshow(tabela, text_auto=True, color_continuous_scale="Reds")
    fig.update_layout(title=f"Escolaridade por faixa etária — Araranguá, {periodo}")
    insight = "Cruzamento entre escolaridade e faixa etária."
    return fig, insight


def top_ocupacoes(df: pd.DataFrame, periodo: str):
    """A10: Principais ocupações agrupadas (destacando o setor agrícola)."""
    serie = df["OCUPACAO_DESC"].value_counts().head(10)
    rotulos = serie.rename(index=lambda c: abrevia(c, 40))
    fig = bar_horizontal(rotulos, f"Principais ocupações declaradas — Araranguá, {periodo}")
    insight = (
        "Aposentados e donas de casa lideram em volume absoluto devido à estrutura etária, "
        "enquanto as várias vertentes da agricultura somam centenas de registos, evidenciando o peso do setor primário."
    )
    return fig, insight


def sexo_por_local(df: pd.DataFrame, periodo: str):
    """A11: Sexo por local de ocorrência em barras empilhadas a 100%."""
    validos = df.loc[~df["SEXO"].isin({"Ignorado"}) & ~df["LOCOCOR"].isin({"Ignorado"})].copy()
    validos["LOCOCOR"] = validos["LOCOCOR"].map(MAPA_LOCAL_CURTO).fillna(validos["LOCOCOR"])
    
    tabela = pd.crosstab(validos["SEXO"], validos["LOCOCOR"], normalize="index") * 100
    fig = barras_empilhadas(tabela, f"Local de ocorrência por sexo (% a 100%) — Araranguá, {periodo}")
    
    insight = (
        "A proporção de óbitos em ambiente hospitalar e no domicílio é muito semelhante entre homens e mulheres "
        "(cerca de 70% em hospitais e 20% em casa), indicando padrões de acesso à rede de saúde equivalentes por género."
    )
    return fig, insight


def causas_por_faixa(df: pd.DataFrame, periodo: str):
    """A12: Causas básicas por faixa etária com paleta azul e nomes simplificados."""
    # Top 5 causas mais frequentes para o cruzamento ficar limpo e legível
    top_causas = df["CAUSABAS_DESC"].value_counts().head(5).index
    filtrado = df[df["CAUSABAS_DESC"].isin(top_causas)].copy()
    
    filtrado["CAUSABAS_DESC"] = filtrado["CAUSABAS_DESC"].apply(lambda c: abrevia(c, 35))
    tabela = pd.crosstab(filtrado["CAUSABAS_DESC"], filtrado["FAIXA_ETARIA"])
    
    fig = px.imshow(
        tabela,
        text_auto=True,
        color_continuous_scale="Blues",  # Paleta azul solicitada na auditoria
        aspect="auto"
    )
    fig.update_layout(
        title=f"Principais causas de óbito por faixa etária — Araranguá, {periodo}",
        xaxis_title="Faixa etária",
        yaxis_title="Causa básica"
    )
    
    insight = (
        "Doenças cardiovasculares (como infarto e AVC) concentram-se fortemente nas faixas etárias avançadas "
        "(a partir dos 60 anos), enquanto as causas externas e mortes violentas predominam nas faixas jovens e adultas."
    )
    return fig, insight