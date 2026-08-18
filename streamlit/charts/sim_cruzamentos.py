"""Cruzamentos: heatmaps, sexo × local e ocupação."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from charts.theme import PALETTE, abrevia, apply_layout, bar_horizontal, heatmap
from data.constants import MAPA_ESC_CURTO, MAPA_LOCAL_CURTO, ORDEM_ESC, ROTULOS_FAIXAS


def sexo_por_local(df: pd.DataFrame, periodo: str):
    """Barras empilhadas de local de ocorrência por sexo (exclui Ignorado)."""
    base = df[~df["SEXO"].isin({"Ignorado"}) & ~df["LOCOCOR"].isin({"Ignorado"})]
    tabela = pd.crosstab(base["SEXO"], base["LOCOCOR"])
    fig = go.Figure()
    for i, col in enumerate(tabela.columns):
        fig.add_bar(
            x=tabela.index.astype(str),
            y=tabela[col],
            name=MAPA_LOCAL_CURTO.get(col, col),
            marker_color=PALETTE[i % len(PALETTE)],
        )
    fig.update_layout(barmode="stack", yaxis_title="Número de óbitos")
    fig = apply_layout(fig, f"Óbitos por sexo e local de ocorrência — Araranguá, {periodo}")
    insight = (
        "Compare a composição das barras: peso hospitalar semelhante entre sexos "
        "sugere acesso parecido; diferenças grandes podem indicar causas distintas "
        "(ex.: causas externas fora do hospital entre homens)."
    )
    return fig, insight


def causas_por_faixa(df: pd.DataFrame, periodo: str):
    """Heatmap das 5 principais causas × faixa etária (sem 'Outras')."""
    top5 = df["CAUSABAS_DESC"].value_counts().head(5).index
    base = df[df["CAUSABAS_DESC"].isin(top5)]
    tabela = pd.crosstab(base["CAUSABAS_DESC"], base["FAIXA_ETARIA"])
    tabela = tabela.reindex(index=list(top5), columns=list(ROTULOS_FAIXAS), fill_value=0)
    if tabela.empty:
        return None, "Sem causas para o cruzamento com faixa etária."
    tabela.index = [abrevia(i, 40) for i in tabela.index]
    fig = heatmap(tabela, f"Causas de óbito × faixa etária — Araranguá, {periodo}", "Reds")
    insight = (
        "Causas cardiovasculares tendem a idades avançadas; causas externas, "
        "a faixas jovens/adultas. Células escuras mostram onde cada causa pesa mais."
    )
    return fig, insight


def escolaridade_por_faixa(df: pd.DataFrame, periodo: str):
    """Heatmap escolaridade × idade (exclui ignorados)."""
    validos = df[df["ESC2010"] != "Ignorado"]
    tabela = pd.crosstab(validos["ESC2010"], validos["FAIXA_ETARIA"])
    tabela = tabela.reindex(columns=list(ROTULOS_FAIXAS), fill_value=0)
    tabela = tabela.reindex([o for o in ORDEM_ESC if o in tabela.index])
    if tabela.empty:
        return None, "Sem escolaridade preenchida para o cruzamento."
    tabela.index = [MAPA_ESC_CURTO.get(i, i) for i in tabela.index]
    fig = heatmap(tabela, f"Escolaridade × faixa etária — Araranguá, {periodo}")
    insight = _insight_esc_faixa(tabela)
    return fig, insight


def _insight_esc_faixa(tabela: pd.DataFrame) -> str:
    """Lê a célula mais frequente do heatmap de escolaridade."""
    if tabela.empty or tabela.values.size == 0:
        return "Sem dados de escolaridade para o cruzamento."
    empilhado = tabela.stack()
    celula = empilhado.idxmax()
    return (
        f"A combinação mais frequente é \"{celula[0]}\" na faixa \"{celula[1]}\" "
        f"({int(empilhado.max())} óbitos). Células escuras em 70+ e baixa "
        "escolaridade costumam ser efeito de coorte, não causalidade direta."
    )


def top_ocupacoes(df: pd.DataFrame, periodo: str):
    """Top 10 ocupações declaradas, se a coluna existir."""
    if "OCUPACAO_DESC" not in df.columns:
        return None, "A coluna de ocupação não está disponível nesta base."
    serie = df["OCUPACAO_DESC"].value_counts()
    validos = serie[~serie.index.isin({"Ignorado/Não se aplica"})]
    validos = validos[~validos.index.astype(str).str.startswith("Desconhecido")]
    top = validos.head(10)
    if top.empty:
        return None, "Não há ocupações válidas para exibir."
    rotulos = top.rename(index=lambda c: abrevia(c, 40))
    fig = bar_horizontal(rotulos, f"Principais ocupações nos óbitos — Araranguá, {periodo}")
    pct_ign = 100 * serie.get("Ignorado/Não se aplica", 0) / serie.sum()
    insight = (
        f"A ocupação mais frequente foi \"{top.index[0]}\" ({int(top.iloc[0])} óbitos). "
        f"{pct_ign:.1f}% dos registros não têm ocupação informada (excluídos do gráfico)."
    )
    return fig, insight
